"""Actual source-authority lock waits; synthetic narrowing is not governed revocation."""

from concurrent.futures import ThreadPoolExecutor
import os
import time

import pytest

from test_ai_diagnosis_evidence_live import external, linked, source_access
from test_ai_diagnosis_live import action_body, domain_counts, get, save
from test_live_application import cmd
from test_native_concurrency import sender

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Actual PostgreSQL advisory waits require the native provisioned login harness",
)


@pytest.mark.parametrize("operation", ["get", "named", "history", "list", "create", "complete", "replay"])
def test_waiting_diagnosis_operation_rechecks_source_grant_before_disclosure_or_effect(live, operation):
    source = external(live)
    with source_access(live, source) as grant:
        creation = cmd(linked(source))
        row = save(live, body=creation)
        original = get(live, row)
        tenant = live.fixture["tenant_a"]
        path = live.path("ai-enablement/diagnoses")
        method, body, success = "GET", None, 200
        if operation in {"get", "named", "history", "complete"}:
            path += "/" + row["object_id"]
        if operation == "named":
            path += "/revisions/" + row["revision_id"]
        elif operation == "history":
            path += "/revisions"
        elif operation == "complete":
            path += "/actions/complete"
            method, body = "POST", action_body(row)
        elif operation in {"create", "replay"}:
            method, body, success = "POST", creation if operation == "replay" else cmd(linked(source)), 201
        token, before = live.token("admin"), domain_counts(live)
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                with live.db() as holder:
                    holder.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                    holder.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
                    queued = pool.submit(sender(live, token, method, path, body))
                    deadline, waiting = time.monotonic() + 2, False
                    while time.monotonic() < deadline and not queued.done():
                        holder.execute("SELECT pg_stat_clear_snapshot()")
                        waiting = holder.execute(
                            "SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE usename='impact_app_login' "
                            "AND wait_event_type='Lock' AND wait_event='advisory') AS waiting"
                        ).fetchone()["waiting"]
                        if waiting:
                            break
                        time.sleep(0.01)
                    assert waiting and not queued.done(), (
                        "Observe a real wait before source authority narrows"
                    )
                    holder.execute(
                        "UPDATE impact.grant_current SET purpose='synthetic-source-withdrawn' "
                        "WHERE tenant_id=%s AND object_id=%s AND capability='evidence.read' AND purpose IS NULL",
                        (tenant, grant["object_id"]),
                    )
                    holder.commit()
                result = queued.result(timeout=10)
            if operation == "list":
                assert result["status"] == 200, result
                assert row["object_id"] not in {item["object_id"] for item in result["body"]["items"]}
            else:
                assert result["status"] == 404 and result["body"]["code"] == "RESOURCE_UNAVAILABLE", result
            assert domain_counts(live) == before
        finally:
            with live.db() as c:
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
                c.execute(
                    "UPDATE impact.grant_current SET purpose=NULL WHERE tenant_id=%s AND object_id=%s",
                    (tenant, grant["object_id"]),
                )
        assert get(live, row) == original
        restored = live.request(path, actor="admin", method=method, body=body)
        assert restored.status_code == success, restored.text
        if operation == "replay":
            assert restored.json() == row and domain_counts(live) == before
