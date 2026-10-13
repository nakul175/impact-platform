"""Explicit native experiment for an unapplied draft; not discovered by normal test_ glob."""

import os
from pathlib import Path
from uuid import uuid4

import pytest

from test_ai_diagnosis_live import action, action_body, get, save
from test_ai_diagnosis_native import login
from test_native_roles import denied
import test_report_exports as exports
import test_worker as worker_tests


@pytest.fixture(scope="module", autouse=True)
def draft_policy(live):
    assert os.environ.get("IMPACT_NATIVE_TEST") == "1", "Real native login harness required"
    row = save(live)
    with login("WORKER") as c, c.transaction():
        c.execute("SET LOCAL ROLE impact_worker")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        assert c.execute(
            "SELECT object_id FROM impact.object_revision WHERE revision_id=%s", (row["revision_id"],)
        ).fetchone(), "Current inherited access must be observed before the draft"
    draft = (
        Path(__file__).resolve().parents[1]
        / "docs/engineering/delivery-system-20261011/diagnosis-worker-fence.DRAFT.sql"
    )
    with live.db() as c:
        c.execute(draft.read_text())
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SET LOCAL ROLE impact_owner")
            for table, policy in (
                ("object_registry", "worker_diagnosis_registry_fence"),
                ("object_revision", "worker_diagnosis_revision_fence"),
            ):
                c.execute("DROP POLICY " + policy + " ON impact." + table)


@pytest.mark.parametrize("set_role", [False, True])
def test_real_worker_login_hides_exact_diagnosis_history_and_refuses_inserts(live, set_role):
    row = save(live)
    completed = action(live, row, "complete")
    corrected = action(live, completed, "revise", body=action_body(completed, reason="Synthetic correction"))
    original = get(live, corrected)
    tenant = live.fixture["tenant_a"]
    with login("WORKER") as c:
        assert c.execute(
            "SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user"
        ).fetchone() == (False, False)
        if not set_role:
            for table in ("object_registry", "object_revision"):
                refusal = denied(c, "SELECT object_id FROM impact." + table, tenant=tenant)
                assert "permission denied for schema impact" in refusal
            assert get(live, corrected) == original
            return
        for scope in (tenant, live.fixture["tenant_b"], None):
            with c.transaction():
                if set_role:
                    c.execute("SET LOCAL ROLE impact_worker")
                if scope:
                    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (scope,))
                for table in ("object_registry", "object_revision"):
                    assert (
                        c.execute(
                            "SELECT object_id FROM impact." + table + " WHERE object_id=%s",
                            (row["object_id"],),
                        ).fetchall()
                        == []
                    )
                    assert (
                        c.execute(
                            "SELECT object_id FROM impact." + table + " WHERE object_type='AIDiagnosis'"
                        ).fetchall()
                        == []
                    )
        with live.db() as owner:
            source = owner.execute(
                "SELECT * FROM impact.object_registry WHERE object_id=%s", (row["object_id"],)
            ).fetchone()
            revision = owner.execute(
                "SELECT * FROM impact.object_revision WHERE revision_id=%s", (row["revision_id"],)
            ).fetchone()
        reason = denied(
            c,
            "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,lifecycle_state,classification,owner_id,created_by) VALUES(%s,%s,'AIDiagnosis','Draft','INTERNAL',%s,%s)",
            (tenant, str(uuid4()), source["owner_id"], source["created_by"]),
            role="impact_worker" if set_role else None,
            tenant=tenant,
        )
        assert "row-level security" in reason
        reason = denied(
            c,
            "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,schema_version,payload,payload_sha256,author_id,revision_number) VALUES(%s,%s,%s,'AIDiagnosis',%s,%s,%s,%s,4)",
            (
                tenant,
                row["object_id"],
                str(uuid4()),
                revision["schema_version"],
                __import__("psycopg").types.json.Jsonb(revision["payload"]),
                revision["payload_sha256"],
                revision["author_id"],
            ),
            role="impact_worker" if set_role else None,
            tenant=tenant,
        )
        assert "row-level security" in reason
    assert get(live, corrected) == original


def test_existing_reminders_and_worker_grants_with_draft(live):
    worker_tests.test_worker_role_holds_no_privilege_migration_0025_revoked(live)
    worker_tests.test_worker_job_and_report_privileges_after_migration_0026(live)
    worker_tests.test_authority_expiry_reminders_are_idempotent_per_threshold(live)


def test_existing_pinned_export_rendering_with_draft(live):
    exports.test_worker_renders_immutable_artifacts_whose_numbers_match_the_snapshot_and_html(live)
