"""Unregistered typed linkage candidate; actual restricted logins, no release claim."""

from copy import deepcopy
from contextlib import ExitStack
import os
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import psycopg
from psycopg.errors import ForeignKeyViolation, InsufficientPrivilege
import pytest
import test_privacy_requests as privacy
import test_report_exports as exports
import test_worker as worker_tests

from impact_api.store import Context, write
from test_ai_diagnosis_evidence_live import external, linked, source_access
from test_ai_diagnosis_live import action, action_body, get, save
from test_ai_diagnosis_native import login
from test_ai_diagnosis_payload_native import insert_copy, payload

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Native typed linkage requires restricted PostgreSQL logins",
)


def rows(live, row):
    with login("APP") as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            return c.execute(
                "SELECT problem_id,reference_position,evidence_id,evidence_revision FROM impact.diagnosis_evidence_binding "
                "WHERE tenant_id=%s AND object_id=%s AND revision_id=%s ORDER BY problem_id,reference_position",
                (live.fixture["tenant_a"], row["object_id"], row["revision_id"]),
            ).fetchall()


@pytest.fixture(scope="module")
def linkage(live):
    # Historical fixture preparation before candidate installation, including a
    # second tenant without depending on onboarding-directory completeness.
    legacy = []
    for actor_name in ["admin", "other_tenant"]:
        actor = live.fixture["actors"][actor_name]
        tenant = actor["tenant_id"]
        ctx = Context(
            tenant,
            actor["principal_id"],
            actor["membership_id"],
            SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
            0,
            0,
            [],
        )
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            source = write(
                c, ctx, "Evidence", {"external_reference": "https://example.test/legacy-source"}, "Draft"
            )
            data = linked(source)
            data["diagnosis_state"] = "Draft"
            row = write(c, ctx, "AIDiagnosis", data, "Draft")
            before = c.execute(
                "SELECT to_jsonb(v) AS v FROM impact.object_revision v WHERE tenant_id=%s AND object_id=%s",
                (tenant, row["object_id"]),
            ).fetchall()
            legacy.append((tenant, row, before))
    script = (
        ROOT / "docs/engineering/delivery-system-20261011/diagnosis-evidence-linkage.CANDIDATE.sql"
    ).read_text()
    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
        c.execute(script)
    try:
        yield legacy
    finally:
        with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_owner")
                c.execute("DROP TRIGGER populate_diagnosis_bindings ON impact.object_revision")
                c.execute("DROP TRIGGER cleanup_diagnosis_bindings ON impact.object_revision")
                c.execute("DROP TABLE impact.diagnosis_evidence_binding")
                c.execute(
                    "DROP FUNCTION impact.guard_diagnosis_binding(),impact.populate_diagnosis_bindings(),impact.cleanup_diagnosis_bindings()"
                )
                c.execute(
                    "ALTER TABLE impact.object_revision DROP CONSTRAINT diagnosis_reference_shape_valid"
                )
                c.execute("DROP FUNCTION impact.diagnosis_reference_shape_valid(jsonb)")
                assert c.execute("SELECT to_regclass('impact.diagnosis_evidence_binding')").fetchone() == (
                    None,
                )


def test_all_tenant_candidate_backfill_preserves_exact_history(linkage, live):
    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"]) as c:
        c.execute("SET LOCAL ROLE impact_owner")
        for tenant, row, before in linkage:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            assert c.execute(
                "SELECT count(*) FROM impact.diagnosis_evidence_binding WHERE tenant_id=%s AND object_id=%s",
                (tenant, row["object_id"]),
            ).fetchone() == (1,)
            after = c.execute(
                "SELECT to_jsonb(v) FROM impact.object_revision v WHERE tenant_id=%s AND object_id=%s",
                (tenant, row["object_id"]),
            ).fetchall()
            assert [x[0] for x in after] == [x["v"] for x in before]
        assert c.execute("SELECT max(version) FROM impact.schema_migration").fetchone() == (46,)


def test_new_links_completion_correction_and_exact_history_are_atomic(linkage, live):
    source = external(live)
    with source_access(live, source):
        data = linked(source)
        row = save(live, data=data)
        expected = [(data["problems"][0]["problem_id"], 1, source["object_id"], source["revision_id"])]
        assert [
            tuple(str(x) if i != 1 else x for i, x in enumerate(item)) for item in rows(live, row)
        ] == expected
        completed = action(live, row, "complete")
        corrected = action(
            live, completed, "revise", body=action_body(completed, reason="Synthetic linked correction")
        )
        assert rows(live, corrected) == rows(live, completed) == rows(live, row)
        assert get(live, corrected)["data"]["problems"] == data["problems"]


@pytest.mark.parametrize("fault", ["missing", "wrong_object", "wrong_kind", "foreign_tenant"])
def test_actual_app_insert_cannot_store_structurally_invalid_source_links(linkage, live, fault):
    source = external(live)
    row = save(live)
    data = deepcopy(payload(live, row))
    ref = {"object_id": source["object_id"], "revision_id": source["revision_id"]}
    if fault == "missing":
        ref["revision_id"] = str(uuid4())
    elif fault == "wrong_object":
        ref["object_id"] = str(uuid4())
    elif fault == "foreign_tenant":
        ref = linkage[1][2][0]["v"]["payload"]["problems"][0]["evidence_references"][0]
    else:
        ref = {"object_id": row["object_id"], "revision_id": row["revision_id"]}
    data["problems"][0]["evidence_references"] = [ref]
    with login("APP") as c:
        with pytest.raises(ForeignKeyViolation):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                insert_copy(c, row, data)
    assert rows(live, row) == []


def test_new_table_forces_tenant_fence_and_no_worker_platform_identity_grants(linkage, live):
    tenant, row, _ = linkage[0]
    with login("APP") as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            assert c.execute(
                "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid='impact.diagnosis_evidence_binding'::regclass"
            ).fetchone() == (True, True)
            assert c.execute("SELECT count(*) FROM impact.diagnosis_evidence_binding").fetchone() == (0,)
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
            assert c.execute(
                "SELECT count(*) FROM impact.diagnosis_evidence_binding WHERE object_id=%s",
                (row["object_id"],),
            ).fetchone() == (0,)
            for role in ["impact_worker", "impact_platform", "impact_identity"]:
                assert c.execute(
                    "SELECT has_table_privilege(%s,'impact.diagnosis_evidence_binding','SELECT')", (role,)
                ).fetchone() == (False,)
            assert c.execute(
                "SELECT has_table_privilege('impact_app','impact.diagnosis_evidence_binding','UPDATE')"
            ).fetchone() == (False,)
            assert c.execute(
                "SELECT has_table_privilege('impact_app','impact.diagnosis_evidence_binding','DELETE')"
            ).fetchone() == (False,)


def test_ordinary_owner_delete_cannot_bypass_binding_immutability(linkage, live):
    tenant, row, _ = linkage[0]
    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
        with pytest.raises(InsufficientPrivilege):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_owner")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                c.execute(
                    "DELETE FROM impact.diagnosis_evidence_binding WHERE tenant_id=%s AND object_id=%s",
                    (tenant, row["object_id"]),
                )


def test_existing_independent_source_erasure_preserves_links_but_refuses_disclosure(
    linkage, live, monkeypatch
):
    captured = []
    original = privacy.member_evidence
    with ExitStack() as grants:

        def linked_member_evidence(*args, **kwargs):
            evidence_id, upload_id, digest = original(*args, **kwargs)
            with live.db() as c:
                source_revision = str(
                    c.execute(
                        "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                        (live.fixture["tenant_a"], evidence_id),
                    ).fetchone()["head_revision"]
                )
            source = {"object_id": evidence_id, "revision_id": source_revision}
            grants.enter_context(source_access(live, source))
            row = save(live, data=linked(source))
            captured.append((row, get(live, row), rows(live, row)))
            return evidence_id, upload_id, digest

        monkeypatch.setattr(privacy, "member_evidence", linked_member_evidence)
        # Existing natural-person independence, plan/hash, erasure, audit and
        # official-number assertions stay intact; synthetic execution only.
        privacy.test_erasure_reaches_every_store_keeps_audit_and_never_alters_official_numbers(live)
        assert captured
        for row, before, bindings in captured:
            assert (
                live.request(
                    live.path("ai-enablement/diagnoses", row["object_id"]), actor="admin"
                ).status_code
                == 404
            )
            assert rows(live, row) == bindings
            assert payload(live, row)["problems"] == before["data"]["problems"]


def test_existing_worker_duties_run_with_linkage_trigger_installed(linkage, live):
    worker_tests.test_authority_expiry_reminders_are_idempotent_per_threshold(live)
    exports.test_worker_renders_immutable_artifacts_whose_numbers_match_the_snapshot_and_html(live)
