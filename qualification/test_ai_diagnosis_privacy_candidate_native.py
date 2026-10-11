"""Actual independent privacy flow for an unregistered diagnosis selector candidate.

Owned diagnosis/source versions are synthetic preparation, not HTTP creation
evidence. No grants, approvals, plan actions or deletion-ledger rows are fabricated.
Actual run evidence is separate; this file claims neither schema 47 nor acceptance.
"""

from copy import deepcopy
import os
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
import test_privacy_requests as privacy

from impact_api.store import Context, load, write
from test_ai_diagnosis_evidence_live import linked
from test_ai_diagnosis_linkage_candidate_native import linkage  # noqa: F401
from test_ai_diagnosis_payload_native import insert_copy
from test_live_application import cmd, expect

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Diagnosis privacy candidate requires actual restricted native PostgreSQL logins",
)


@pytest.fixture(scope="module")
def diagnosis_privacy_scope(request, live):
    request.getfixturevalue("linkage")
    script = (
        ROOT / "docs/engineering/delivery-system-20261011/diagnosis-privacy-scope.CANDIDATE.sql"
    ).read_text()
    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
        c.execute(script)
    try:
        yield
    finally:
        with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_owner")
                c.execute("ALTER TABLE impact.privacy_case_current DROP COLUMN diagnosis_ids")
                assert c.execute(
                    "SELECT count(*) FROM information_schema.columns WHERE table_schema='impact' "
                    "AND table_name='privacy_case_current' AND column_name='diagnosis_ids'"
                ).fetchone() == (0,)
                assert c.execute("SELECT max(version) FROM impact.schema_migration").fetchone() == (46,)


def owned(live, subject, versions=3):
    """Prepare fresh own objects without giving the subject new runtime authority."""
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        natural = c.execute(
            "SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s",
            (subject.identity,),
        ).fetchone()["natural_identity_id"]
        ctx = Context(
            tenant,
            subject.principal,
            subject.membership,
            SimpleNamespace(natural_identity_id=str(natural)),
            0,
            0,
            [],
        )
        source = write(c, ctx, "Evidence", {"external_reference": "https://example.test/privacy-source"})
        data = linked(source)
        rows = []
        for n in range(versions):
            data = deepcopy(data)
            data["title"] = "Synthetic owned diagnosis version " + str(n + 1)
            data["diagnosis_state"] = "Completed" if n == 1 else "Draft"
            previous = load(c, ctx, rows[-1]["object_id"], "AIDiagnosis") if rows else None
            rows.append(write(c, ctx, "AIDiagnosis", data, data["diagnosis_state"], previous))
    return source, rows


def stored(live, object_id):
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        return c.execute(
            "SELECT to_jsonb(v) AS row FROM impact.object_revision v WHERE tenant_id=%s "
            "AND object_id=%s ORDER BY revision_number",
            (live.fixture["tenant_a"], object_id),
        ).fetchall()


@pytest.mark.usefixtures("diagnosis_privacy_scope")
def test_actual_independent_diagnosis_erasure_cleans_bindings_preserves_history_and_source(live):
    subject = privacy.member(live)
    source, versions = owned(live, subject)
    obj = versions[-1]["object_id"]
    before, source_before = stored(live, obj), stored(live, source["object_id"])
    official_before = privacy.official_fingerprint(live)
    active = privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[obj])
    assert privacy.approve(live, active["object_id"], status=409)["reason_code"] == "SUBJECT_STILL_ACTIVE"
    privacy.revoke(live, subject)
    created = privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[obj])
    case_id = created["object_id"]
    preview = privacy.plan(live, case_id)
    selected = [e for e in preview["entries"] if e["object_id"] == obj]
    assert len(selected) == 1
    assert (
        selected[0]["store"],
        selected[0]["action"],
        selected[0]["object_type"],
        selected[0]["state"],
    ) == ("DATABASE", "DELETE", "AIDiagnosis", "APPROVED")
    assert not any(e["object_id"] == source["object_id"] for e in preview["entries"])
    privacy.approve(live, case_id)
    approved = privacy.case(live, case_id)
    body = cmd(
        {"purpose": privacy.PURPOSE, "approved_plan_hash": approved["data"]["plan_sha256"]},
        approved["revision_id"],
    )
    path = live.path("privacy-cases", case_id) + "/actions/execute"
    first = expect(live.request(path, actor="privacy", method="POST", body=body), 200)
    after = stored(live, obj)
    assert len(after) == len(before) == 3
    for old, new in zip(before, after, strict=True):
        assert new["row"]["payload"] is None and new["row"]["restriction_state"] == "REMOVED"
        assert {k: v for k, v in old["row"].items() if k not in {"payload", "restriction_state"}} == {
            k: v for k, v in new["row"].items() if k not in {"payload", "restriction_state"}
        }
    assert stored(live, source["object_id"]) == source_before
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.diagnosis_evidence_binding WHERE object_id=%s", (obj,)
            ).fetchone()["n"]
            == 0
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_registry WHERE object_id=%s", (obj,)
            ).fetchone()["n"]
            == 1
        )
        ledger = c.execute(
            "SELECT disposition FROM impact.deletion_ledger WHERE case_id=%s AND object_id=%s", (case_id, obj)
        ).fetchall()
        assert len(ledger) == 1
        actions = c.execute(
            "SELECT store,state FROM impact.privacy_store_action WHERE case_id=%s AND object_id=%s",
            (case_id, obj),
        ).fetchall()
        assert actions == [{"store": "DATABASE", "state": "COMPLETED"}]
        counts = c.execute(
            "SELECT (SELECT count(*) FROM impact.operation_receipt WHERE outcome->>'object_id'=%s) AS receipts, (SELECT count(*) FROM impact.audit_event_current WHERE object_reference=%s) AS audits",
            (case_id, case_id),
        ).fetchone()
    assert expect(live.request(path, actor="privacy", method="POST", body=body), 200) == first
    with live.db() as c:
        assert (
            c.execute(
                "SELECT (SELECT count(*) FROM impact.operation_receipt WHERE outcome->>'object_id'=%s) AS receipts, (SELECT count(*) FROM impact.audit_event_current WHERE object_reference=%s) AS audits",
                (case_id, case_id),
            ).fetchone()
            == counts
        )
    assert privacy.case(live, case_id)["lifecycle_state"] == "Completed"
    assert privacy.official_fingerprint(live) == official_before
    for suffix in ["", "/revisions", *["/revisions/" + v["revision_id"] for v in versions]]:
        expect(live.request(live.path("ai-enablement/diagnoses", obj) + suffix, actor="admin"), 404)


@pytest.mark.usefixtures("diagnosis_privacy_scope")
def test_diagnosis_privacy_selector_refusals_and_closed_scope(live):
    subject = privacy.member(live)
    source, versions = owned(live, subject, versions=1)
    obj = versions[0]["object_id"]
    assert (
        privacy.create_case(live, subject, "ACCESS", diagnosis_ids=[obj], status=422)["reason_code"]
        == "ERASURE_SCOPE_ONLY"
    )
    stranger = privacy.member(live)
    _, other = owned(live, stranger, versions=1)
    for selected in [str(uuid4()), source["object_id"], other[0]["object_id"]]:
        assert (
            privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[selected], status=422)["reason_code"]
            == "NOT_SUBJECT_DATA"
        )
    for ids in [[obj, obj], [str(uuid4()) for _ in range(51)], ["invalid"], "invalid"]:
        privacy.create_case(live, subject, "ERASURE", diagnosis_ids=ids, status=422)


@pytest.mark.usefixtures("diagnosis_privacy_scope")
def test_new_diagnosis_revision_invalidates_actual_approved_erasure_plan(live):
    subject = privacy.member(live)
    _, versions = owned(live, subject, versions=1)
    obj = versions[0]["object_id"]
    privacy.revoke(live, subject)
    created = privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[obj])
    privacy.approve(live, created["object_id"])
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        natural = c.execute(
            "SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s", (subject.identity,)
        ).fetchone()["natural_identity_id"]
        ctx = Context(
            tenant,
            subject.principal,
            subject.membership,
            SimpleNamespace(natural_identity_id=str(natural)),
            0,
            0,
            [],
        )
        previous = load(c, ctx, obj, "AIDiagnosis")
        data = deepcopy(previous["payload"])
        data["title"] = "Synthetic appended revision after plan approval"
        write(c, ctx, "AIDiagnosis", data, "Draft", previous)
    before = stored(live, obj)
    assert privacy.execute(live, created["object_id"], status=409)["reason_code"] == "PLAN_CHANGED"
    assert stored(live, obj) == before
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.deletion_ledger WHERE case_id=%s AND object_id=%s",
                (created["object_id"], obj),
            ).fetchone()["n"]
            == 0
        )


@pytest.mark.usefixtures("diagnosis_privacy_scope")
def test_actual_diagnosis_erasure_honours_retention_hold(live):
    subject = privacy.member(live)
    source, versions = owned(live, subject)
    obj = versions[-1]["object_id"]
    before = stored(live, obj)
    source_before = stored(live, source["object_id"])
    privacy.revoke(live, subject)
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        c.execute(
            "INSERT INTO impact.retention_hold(tenant_id,hold_id,object_id,authority_reference,review_at) "
            "VALUES(%s,%s,%s,'Synthetic diagnosis legal hold',now()+interval '30 days')",
            (live.fixture["tenant_a"], str(uuid4()), obj),
        )
    created = privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[obj])
    selected = [e for e in privacy.plan(live, created["object_id"])["entries"] if e["object_id"] == obj]
    assert len(selected) == 1
    assert selected[0]["state"] == "HELD" and selected[0]["reason"] == "RETENTION_HOLD"
    assert selected[0]["hold_review_at"]
    privacy.approve(live, created["object_id"])
    privacy.execute(live, created["object_id"])
    assert privacy.case(live, created["object_id"])["lifecycle_state"] == "PartiallyCompleted"
    assert stored(live, obj) == before
    assert stored(live, source["object_id"]) == source_before
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.diagnosis_evidence_binding WHERE object_id=%s", (obj,)
            ).fetchone()["n"]
            == 3
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.deletion_ledger WHERE case_id=%s AND object_id=%s",
                (created["object_id"], obj),
            ).fetchone()["n"]
            == 0
        )


@pytest.mark.usefixtures("diagnosis_privacy_scope")
def test_foreign_tenant_diagnosis_is_not_subject_data(live):
    subject = privacy.member(live)
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
        foreign = c.execute(
            "SELECT object_id FROM impact.object_registry WHERE tenant_id=%s "
            "AND object_type='AIDiagnosis' ORDER BY object_id LIMIT 1",
            (live.fixture["tenant_b"],),
        ).fetchone()
    assert foreign, "Unchanged linkage fixture prepares an actual other-tenant diagnosis"
    assert (
        privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[str(foreign["object_id"])], status=422)[
            "reason_code"
        ]
        == "NOT_SUBJECT_DATA"
    )


@pytest.mark.usefixtures("diagnosis_privacy_scope")
def test_actual_erasure_removes_insert_only_restricted_diagnosis_revision(live):
    subject = privacy.member(live)
    _, versions = owned(live, subject, versions=2)
    obj = versions[-1]["object_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (live.fixture["tenant_a"],))
        original = c.execute(
            "SELECT payload FROM impact.object_revision WHERE revision_id=%s", (versions[-1]["revision_id"],)
        ).fetchone()["payload"]
        # NEW restricted revision preparation, never an update or guard bypass.
        insert_copy(c, versions[-1], original, restriction="RESTRICTED")
    before = stored(live, obj)
    assert len(before) == 3
    assert [r["row"]["restriction_state"] for r in before].count("RESTRICTED") == 1
    privacy.revoke(live, subject)
    created = privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[obj])
    privacy.approve(live, created["object_id"])
    privacy.execute(live, created["object_id"])
    after = stored(live, obj)
    for old, new in zip(before, after, strict=True):
        assert new["row"]["payload"] is None and new["row"]["restriction_state"] == "REMOVED"
        assert {k: v for k, v in old["row"].items() if k not in {"payload", "restriction_state"}} == {
            k: v for k, v in new["row"].items() if k not in {"payload", "restriction_state"}
        }
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.diagnosis_evidence_binding WHERE object_id=%s", (obj,)
            ).fetchone()["n"]
            == 0
        )
