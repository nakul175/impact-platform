"""Actual replacement restored API with checked linkage registration; synthetic identity only."""

import json
import os
import socket
import sys

import httpx
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
import pytest
import test_ai_diagnosis_recovery as recovery

from clone_connections import clone_login_dsn

from test_ai_diagnosis_evidence_live import external, linked, source_access
from test_ai_diagnosis_linkage_candidate_native import (  # noqa: F401
    LATEST_SCHEMA_VERSION,
    ROOT,
    linkage,
    registered_linkage,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Actual native backup/restore and replacement restricted API process required",
)


@pytest.mark.usefixtures("linkage")
def test_restored_linked_api_replays_exact_history_restarts_and_refuses_lost_source_access(live, monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts"))
    import restore_drill
    import run as runner

    fixture = os.environ["IMPACT_FIXTURE_DSN"]
    target = restore_drill.conninfo_to_dict(fixture)["dbname"] + "_restored"
    restored = make_conninfo(fixture, dbname=target)
    local = live.local / "linked-restored-api"
    local.mkdir(mode=0o700)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    base = "http://127.0.0.1:" + str(port)
    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"]) as c:
        registered = registered_linkage(c)
    result = {
        "schema_registered": 47 if registered else 46,
        "candidate_registered": registered,
        "api_phases": [],
    }
    api = None
    client = None
    source = external(live)
    with source_access(live, source) as grant:
        monkeypatch.setattr(recovery, "diagnosis", lambda: linked(source))
        checkpoint = recovery.capture_diagnosis(live)
        try:
            drill = restore_drill.run(
                fixture,
                fixture,
                restore_drill.passwords_from_env(os.environ),
                os.environ["IMPACT_PG_BIN"],
                keep=True,
            )
            assert drill["outcome"] == "PASS" and all(drill["checks"].values())
            assert drill["migration"]["schema_version"] == LATEST_SCHEMA_VERSION
            assert drill["migration"]["applied"] == []
            with psycopg.connect(make_conninfo(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], dbname=target)) as c:
                assert registered_linkage(c) is registered
            result["restore"] = drill
            config = dict(live.config)
            for key, name in [("app_dsn", "APP"), ("identity_dsn", "IDENTITY"), ("platform_dsn", "PLATFORM")]:
                config[key] = clone_login_dsn(name, target)
            config["public_origin"] = base
            private_config = local / "config.json"
            private_config.write_text(json.dumps(config))
            private_config.chmod(0o600)
            # No fixture/migrator/worker DSN, login passwords, PG* override or
            # provider key is inherited by the replacement API process.
            env = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": str(ROOT / "apps/api"),
                "IMPACT_CONFIG_FILE": str(private_config),
                "IMPACT_REQUIRE_UNPRIVILEGED_DB": "1",
            }
            monkeypatch.setenv("IMPACT_PORT", str(port))
            client = httpx.Client(base_url=base, trust_env=False, timeout=20)

            class Restored:
                fixture = live.fixture
                path = live.path

                def request(self, path, actor="admin", method="GET", body=None):
                    return client.request(
                        method, path, json=body, headers={"Authorization": "Bearer " + live.token(actor)}
                    )

                def db(self):
                    return psycopg.connect(restored, row_factory=dict_row, prepare_threshold=None)

            restored_live = Restored()
            for phase in [1, 2]:
                api, seconds = runner.start_api(local, env, base)
                recovery.verify_diagnosis(restored_live, checkpoint)
                result["api_phases"].append({"phase": phase, "ready_seconds": seconds, "exact_replay": True})
                if phase == 1:
                    code, clean, _ = runner.stop_api(local, api)
                    result["api_phases"][-1].update(stop_code=code, clean_stop=clean)
                    assert clean
                    api = None
            before = recovery.owned_counts(restored_live, checkpoint)
            with restored_live.db() as c:
                tenant = live.fixture["tenant_a"]
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
                changed = c.execute(
                    "UPDATE impact.grant_current SET purpose='synthetic-restored-source-ended' "
                    "WHERE tenant_id=%s AND object_id=%s AND capability='evidence.read' AND purpose IS NULL",
                    (tenant, grant["object_id"]),
                ).rowcount
                assert changed == 1
            path = live.path("ai-enablement/diagnoses", checkpoint["object_id"])
            for suffix in ["", "/revisions", "/revisions/" + checkpoint["versions"][0]["revision_id"]]:
                refused = restored_live.request(path + suffix)
                assert refused.status_code == 404 and refused.json()["code"] == "RESOURCE_UNAVAILABLE"
            for command in checkpoint["commands"]:
                refused = restored_live.request(command["path"], method="POST", body=command["body"])
                assert refused.status_code == 404 and refused.json()["code"] == "RESOURCE_UNAVAILABLE"
            assert recovery.owned_counts(restored_live, checkpoint) == before
            # The original API remains authorised: the refusal is from the
            # changed disposable restored database, not the original process.
            recovery.verify_diagnosis(live, checkpoint)
            result["original_api_unchanged"] = True
            result["source_access_loss"] = (
                "Three reads and all three original exact receipts refuse404; no revision/receipt/audit effects"
            )
        finally:
            if api is not None:
                code, clean, _ = runner.stop_api(local, api)
                result["final_api_stop"] = {"code": code, "clean": clean}
            if client is not None:
                client.close()
            with psycopg.connect(fixture, autocommit=True) as c:
                c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(target)))
                assert c.execute("SELECT 1 FROM pg_database WHERE datname=%s", (target,)).fetchone() is None
            result["restored_database_dropped"] = True
            (live.local / "diagnosis-linkage-api-restore.json").write_text(
                json.dumps(result, indent=2) + "\n"
            )
        assert result["final_api_stop"]["clean"]
