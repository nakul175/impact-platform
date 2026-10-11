"""Typed linkage qualification on registered storage or the retained schema46 candidate."""

from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import os
import hashlib
from pathlib import Path
import time
from types import SimpleNamespace
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
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
from test_live_application import cmd
from test_native_concurrency import sender

ROOT = Path(__file__).resolve().parents[1]
REGISTERED = ROOT / "infrastructure/migrations/0047_diagnosis_evidence_privacy.sql"
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


def registered_linkage(c):
    """Fail closed on a partly installed or mismatched registered schema."""
    with c.transaction():
        c.execute("SET LOCAL ROLE impact_owner")
        return _registered_linkage(c)


def _registered_linkage(c):
    registered = c.execute("SELECT sha256 FROM impact.schema_migration WHERE version=47").fetchone()
    present = c.execute("SELECT to_regclass('impact.diagnosis_evidence_binding')").fetchone()[0]
    if registered is None:
        return False
    assert c.execute("SELECT max(version) FROM impact.schema_migration").fetchone() == (47,)
    assert registered == (hashlib.sha256(REGISTERED.read_bytes()).hexdigest(),)
    assert present is not None
    columns = {
        row[0]
        for row in c.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_schema='impact' "
            "AND table_name='diagnosis_evidence_binding'"
        ).fetchall()
    }
    assert columns == {
        "tenant_id",
        "object_id",
        "revision_id",
        "diagnosis_kind",
        "problem_id",
        "reference_position",
        "evidence_id",
        "evidence_revision",
        "evidence_kind",
    }
    assert c.execute(
        "SELECT count(*) FROM information_schema.columns WHERE table_schema='impact' "
        "AND table_name='privacy_case_current' AND column_name='diagnosis_ids'"
    ).fetchone() == (1,)
    return True


@pytest.fixture(scope="module")
def linkage(live):
    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
        registered = registered_linkage(c)
    # On schema46 this precedes candidate installation. Registered storage
    # already populates these fresh rows; the separate legacy-upgrade tests
    # retain actual backfill proof. Both include a second tenant.
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
    if not registered:
        with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
            c.execute(script)
    try:
        yield legacy
    finally:
        with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
            if registered:
                assert registered_linkage(c)
                return
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
        if REGISTERED.exists() and registered_linkage(c):
            assert c.execute("SELECT max(version) FROM impact.schema_migration").fetchone() == (47,)
        else:
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


def test_waiting_diagnosis_routes_recheck_actual_independent_source_erasure(linkage, live, monkeypatch):
    """Pause actual erasure under its tenant lock, never replace its approved plan.

    The disposable trigger only delays removal of this one fresh Evidence row.
    It grants no privilege and does not supply a diagnosis-removal approval.
    """
    original_source, original_execute = privacy.member_evidence, privacy.execute
    captured = []
    tenant = live.fixture["tenant_a"]
    pause_key = str(uuid4())

    def diagnosis_effects():
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            return [
                c.execute(query, (tenant,)).fetchone()["n"]
                for query in [
                    "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s AND object_type='AIDiagnosis'",
                    "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_type='AIDiagnosis'",
                    "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s "
                    "AND command_type IN ('create_ai_diagnosis','update_ai_diagnosis','complete_ai_diagnosis','revise_ai_diagnosis')",
                ]
            ]

    pooled = os.environ.get("IMPACT_DB_POOLER") == "pgbouncer-transaction"

    def pool_waiters(c):
        """Count real queued clients, which have no PostgreSQL backend yet."""
        database = c.execute("SELECT current_database() AS name").fetchone()["name"]
        admin_dsn = os.environ.get("IMPACT_POOLER_ADMIN_DSN")
        assert admin_dsn, "Pooled qualification requires its actual admin console"
        with psycopg.connect(
            admin_dsn, autocommit=True, prepare_threshold=None, row_factory=dict_row
        ) as admin:
            pools = [
                r
                for r in admin.execute("SHOW POOLS").fetchall()
                if r["database"] == database and r["user"] == "impact_app_login"
            ]
            clients = [
                r
                for r in admin.execute("SHOW CLIENTS").fetchall()
                if r["database"] == database and r["user"] == "impact_app_login" and r["state"] == "waiting"
            ]
        assert len(pools) <= 1, "Expected one app pool for this synthetic database"
        return pools[0] if pools else None, len(clients)

    def advisory_waiters(c):
        c.execute("SELECT pg_stat_clear_snapshot()")
        return c.execute(
            "SELECT count(*) AS n FROM pg_stat_activity WHERE usename='impact_app_login' "
            "AND datname=current_database() AND wait_event_type='Lock' AND wait_event='advisory'"
        ).fetchone()["n"]

    def waiting(c, minimum, pooled_queue=False):
        deadline = time.monotonic() + 2
        if pooled_queue:
            size = int(os.environ["IMPACT_POOLER_POOL_SIZE"])
            assert size == 3, "This qualification pins the deliberately small three-backend pool"
            last = None
            while time.monotonic() < deadline:
                count = advisory_waiters(c)
                app_pool, client_waiting = pool_waiters(c)
                last = (count, app_pool, client_waiting)
                if (
                    app_pool is not None
                    and app_pool["pool_mode"] == "transaction"
                    and count == size
                    and int(app_pool["sv_active"]) == size
                    and int(app_pool["cl_active"]) == size
                    and int(app_pool["cl_waiting"]) == minimum - size
                    and client_waiting == minimum - size
                ):
                    return
                time.sleep(0.01)
            pytest.fail(
                f"Eight actual requests did not reach three advisory waits plus five pool queues: {last}"
            )
        while time.monotonic() < deadline:
            c.execute("SELECT pg_stat_clear_snapshot()")
            count = c.execute(
                "SELECT count(*) AS n FROM pg_stat_activity WHERE usename='impact_app_login' "
                "AND wait_event_type='Lock' AND wait_event='advisory'"
            ).fetchone()["n"]
            if count >= minimum:
                return
            time.sleep(0.01)
        pytest.fail(f"Actual PostgreSQL advisory wait count did not reach {minimum}")

    with ExitStack() as grants:

        def linked_source(*args, **kwargs):
            evidence_id, upload_id, digest = original_source(*args, **kwargs)
            with live.db() as c:
                revision = str(
                    c.execute(
                        "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                        (tenant, evidence_id),
                    ).fetchone()["head_revision"]
                )
            source = {"object_id": evidence_id, "revision_id": revision}
            grants.enter_context(source_access(live, source))
            creation = cmd(linked(source))
            row = save(live, body=creation)
            captured.append((source, row, creation, payload(live, row), rows(live, row)))
            return evidence_id, upload_id, digest

        def paused_execute(*args, **kwargs):
            source, row, creation, before, bindings = captured[-1]
            with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
                with c.transaction():
                    c.execute("SET LOCAL ROLE impact_owner")
                    c.execute(
                        "CREATE FUNCTION impact.test_pause_diagnosis_source_erasure() RETURNS trigger "
                        "LANGUAGE plpgsql AS $$ BEGIN PERFORM pg_advisory_xact_lock(hashtextextended('"
                        + pause_key
                        + "',7)); RETURN NEW; END $$"
                    )
                    c.execute(
                        "CREATE TRIGGER test_pause_diagnosis_source_erasure BEFORE UPDATE ON impact.object_revision "
                        "FOR EACH ROW WHEN (OLD.object_id='"
                        + source["object_id"]
                        + "'::uuid AND NEW.restriction_state='REMOVED') "
                        "EXECUTE FUNCTION impact.test_pause_diagnosis_source_erasure()"
                    )
            path = live.path("ai-enablement/diagnoses")
            item = path + "/" + row["object_id"]
            token = live.token("admin")
            effects_before = diagnosis_effects()
            calls = {
                "current": sender(live, token, "GET", item),
                "named": sender(live, token, "GET", item + "/revisions/" + row["revision_id"]),
                "history": sender(live, token, "GET", item + "/revisions"),
                "list": sender(live, token, "GET", path),
                "create": sender(live, token, "POST", path, cmd(linked(source))),
                "complete": sender(live, token, "POST", item + "/actions/complete", action_body(row)),
                "replay": sender(live, token, "POST", path, creation),
            }
            try:
                with ThreadPoolExecutor(max_workers=8) as pool:
                    with live.db() as holder:
                        holder.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,7))", (pause_key,))
                        if pooled:
                            app_pool, client_waiting = pool_waiters(holder)
                            assert advisory_waiters(holder) == 0
                            assert client_waiting == 0
                            assert app_pool is None or int(app_pool["cl_waiting"]) == 0
                        erasure = pool.submit(original_execute, *args, **kwargs)
                        waiting(holder, 1)
                        assert not erasure.done(), "Real erasure must still hold its tenant lock"
                        queued = {name: pool.submit(call) for name, call in calls.items()}
                        waiting(holder, 8, pooled_queue=pooled)
                        assert not erasure.done() and all(not f.done() for f in queued.values())
                        holder.commit()
                    receipt = erasure.result(timeout=10)
                    results = {name: future.result(timeout=10) for name, future in queued.items()}
                for name, result in results.items():
                    if name == "list":
                        assert result["status"] == 200, result
                        assert row["object_id"] not in {item["object_id"] for item in result["body"]["items"]}
                    else:
                        assert result["status"] == 404, (name, result)
                        assert result["body"]["code"] == "RESOURCE_UNAVAILABLE", (name, result)
                assert payload(live, row) == before and rows(live, row) == bindings
                assert diagnosis_effects() == effects_before
                return receipt
            finally:
                with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
                    with c.transaction():
                        c.execute("SET LOCAL ROLE impact_owner")
                        c.execute(
                            "DROP TRIGGER test_pause_diagnosis_source_erasure ON impact.object_revision"
                        )
                        c.execute("DROP FUNCTION impact.test_pause_diagnosis_source_erasure()")
                        assert c.execute(
                            "SELECT to_regproc('impact.test_pause_diagnosis_source_erasure')"
                        ).fetchone() == (None,)

        monkeypatch.setattr(privacy, "member_evidence", linked_source)
        monkeypatch.setattr(privacy, "execute", paused_execute)
        privacy.test_erasure_reaches_every_store_keeps_audit_and_never_alters_official_numbers(live)
        assert len(captured) == 1
