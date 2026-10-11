"""Post-erasure backup recovery with actual independent privacy HTTP execution.

Objects are synthetic preparation, not HTTP creation or approval evidence.
Backup is taken AFTER erasure. This never claims pre-erasure backup replay closure.
"""

import json
import os
from pathlib import Path
import socket
import sys

import httpx
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
import pytest
import test_privacy_requests as privacy

from test_ai_diagnosis_linkage_candidate_native import linkage, registered_linkage  # noqa: F401
from test_ai_diagnosis_privacy_candidate_native import diagnosis_privacy_scope, owned, stored  # noqa: F401
from test_live_application import cmd, expect

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Actual post-erasure native backup and replacement restricted API required",
)


def evidence(live, diagnosis_id, source_id, case_id):
    """Scoped durable rows only; do not copy session cookies or private configuration."""
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        result = {}
        for table, predicate, params, order in [
            (
                "object_registry",
                "object_id=ANY(%s::uuid[])",
                ([diagnosis_id, source_id, case_id],),
                "object_id",
            ),
            (
                "object_revision",
                "object_id=ANY(%s::uuid[])",
                ([diagnosis_id, source_id, case_id],),
                "object_id,revision_number",
            ),
            (
                "diagnosis_evidence_binding",
                "object_id=%s",
                (diagnosis_id,),
                "revision_id,problem_id,reference_position",
            ),
            ("deletion_ledger", "case_id=%s", (case_id,), "object_id"),
            ("privacy_store_action", "case_id=%s", (case_id,), "object_id,store"),
            ("audit_event_current", "object_reference=%s", (case_id,), "object_id"),
            ("operation_receipt", "outcome->>'object_id'=%s", (case_id,), "command_type,operation_id"),
        ]:
            result[table] = [
                row["v"]
                for row in c.execute(
                    "SELECT to_jsonb(t) AS v FROM impact."
                    + table
                    + " t WHERE tenant_id=%s AND "
                    + predicate
                    + " ORDER BY "
                    + order,
                    (tenant, *params),
                ).fetchall()
            ]
        return result


@pytest.mark.usefixtures("diagnosis_privacy_scope")
def test_post_erasure_backup_restored_api_keeps_removed_payloads_and_exact_privacy_retry(live, monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts"))
    import restore_drill
    import run as runner

    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"]) as c:
        assert registered_linkage(c), "This recovery test qualifies registered47 storage"
    subject = privacy.member(live)
    source, versions = owned(live, subject)
    obj = versions[-1]["object_id"]
    before, source_before = stored(live, obj), stored(live, source["object_id"])
    privacy.revoke(live, subject)
    created = privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[obj])
    case_id = created["object_id"]
    privacy.approve(live, case_id)
    approved = privacy.case(live, case_id)
    body = cmd(
        {"purpose": privacy.PURPOSE, "approved_plan_hash": approved["data"]["plan_sha256"]},
        approved["revision_id"],
    )
    path = live.path("privacy-cases", case_id) + "/actions/execute"
    receipt = expect(live.request(path, actor="privacy", method="POST", body=body), 200)
    after = stored(live, obj)
    assert len(before) == len(after) == 3
    for old, new in zip(before, after, strict=True):
        assert new["row"]["payload"] is None and new["row"]["restriction_state"] == "REMOVED"
        assert {k: v for k, v in old["row"].items() if k not in {"payload", "restriction_state"}} == {
            k: v for k, v in new["row"].items() if k not in {"payload", "restriction_state"}
        }
    assert stored(live, source["object_id"]) == source_before
    original = evidence(live, obj, source["object_id"], case_id)
    assert original["diagnosis_evidence_binding"] == []
    assert any(row["object_id"] == obj for row in original["deletion_ledger"])
    assert original["privacy_store_action"] and all(
        row["state"] == "COMPLETED" for row in original["privacy_store_action"]
    )
    assert original["audit_event_current"] and original["operation_receipt"]

    fixture = os.environ["IMPACT_FIXTURE_DSN"]
    target = restore_drill.conninfo_to_dict(fixture)["dbname"] + "_restored"
    restored = make_conninfo(fixture, dbname=target)
    local = live.local / "erasure-restored-api"
    local.mkdir(mode=0o700)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    base = "http://127.0.0.1:" + str(port)
    result = {
        "backup_phase": "AFTER_ACTUAL_ERASURE",
        "schema_registered": 47,
        "pre_erasure_replay_claim": False,
    }
    api = client = None
    try:
        drill = restore_drill.run(
            fixture,
            fixture,
            restore_drill.passwords_from_env(os.environ),
            os.environ["IMPACT_PG_BIN"],
            keep=True,
        )
        assert drill["outcome"] == "PASS" and all(drill["checks"].values())
        assert drill["migration"]["schema_version"] == 47 and drill["migration"]["applied"] == []
        with psycopg.connect(make_conninfo(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], dbname=target)) as c:
            assert registered_linkage(c)
        result["restore"] = drill
        config = dict(live.config)
        for key, role in [("app_dsn", "APP"), ("identity_dsn", "IDENTITY"), ("platform_dsn", "PLATFORM")]:
            config[key] = make_conninfo(os.environ["IMPACT_LOGIN_DSN_" + role], dbname=target)
        config["public_origin"] = base
        private = local / "config.json"
        private.write_text(json.dumps(config))
        private.chmod(0o600)
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(ROOT / "apps/api"),
            "IMPACT_CONFIG_FILE": str(private),
            "IMPACT_REQUIRE_UNPRIVILEGED_DB": "1",
        }
        monkeypatch.setenv("IMPACT_PORT", str(port))
        client = httpx.Client(base_url=base, trust_env=False, timeout=20)

        class Restored:
            fixture = live.fixture
            path = live.path

            def request(self, path, actor="admin", method="GET", body=None, params=None):
                return client.request(
                    method,
                    path,
                    json=body,
                    params=params,
                    headers={"Authorization": "Bearer " + live.token(actor)},
                )

            def db(self):
                return psycopg.connect(restored, row_factory=dict_row, prepare_threshold=None)

        copied = Restored()
        api, seconds = runner.start_api(local, env, base)
        result["ready_seconds"] = seconds
        assert evidence(copied, obj, source["object_id"], case_id) == original
        assert stored(copied, obj) == after and stored(copied, source["object_id"]) == source_before
        for suffix in ["", "/revisions", *["/revisions/" + row["revision_id"] for row in versions]]:
            refusal = expect(copied.request(live.path("ai-enablement/diagnoses", obj) + suffix), 404)
            assert refusal["code"] == "RESOURCE_UNAVAILABLE"
        assert expect(copied.request(path, actor="privacy", method="POST", body=body), 200) == receipt
        assert evidence(copied, obj, source["object_id"], case_id) == original
        assert privacy.case(copied, case_id)["lifecycle_state"] == "Completed"
        assert evidence(live, obj, source["object_id"], case_id) == original
        result["exact_privacy_retry_no_new_effects"] = True
        result["removed_diagnosis_reads"] = "current/history/three_named_revisions404"
    finally:
        if api is not None:
            code, clean, _ = runner.stop_api(local, api)
            result["api_stop"] = {"code": code, "clean": clean}
        if client is not None:
            client.close()
        with psycopg.connect(fixture, autocommit=True) as c:
            c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(target)))
            assert c.execute("SELECT 1 FROM pg_database WHERE datname=%s", (target,)).fetchone() is None
        result["restored_database_dropped"] = True
        (live.local / "diagnosis-erasure-restore.json").write_text(json.dumps(result, indent=2) + "\n")
    assert result["api_stop"]["clean"]
