"""Native-only upgrade check: a populated database at the previous schema is upgraded to the latest.

LATEST is the number of migration files (20 since build 0.19.0) and BASELINE is LATEST - 1. On a
fresh disposable database next to the one named by IMPACT_FIXTURE_DSN this script applies
migrations 0001-BASELINE as the provisioned `impact_migrator` login, loads the acceptance fixture as
the superuser (the fixture touches only migration 0002/0003 tables), adds one browser session row
and one outbox event with its delivery row, and (since 0.18.0) one draft framework and one blank
draft target with their registry and revision rows so that the ALTER TABLE of
`impact.framework_current` and `impact.target_current` in 0019 runs on populated tables, applies the
remaining migration as the migrator (since 0.19.0 migration 0020 alters `impact.indicator_definition_current`
and `impact.calculated_result_current`, which the acceptance fixture populates), and then verifies with direct queries, starting no service,
that `impact.schema_migration` holds LATEST rows with exactly the SHA-256 values ledgered in
docs/current/CURRENT-DATA-DICTIONARY.md, that `max(version)` is LATEST, that the columns and tables
0017, 0018 and 0019 add exist, and that the tenant, revision, session and outbox counts loaded at
the baseline are unchanged, with the pre-existing session's new columns NULL, the pre-existing
delivery row left undispatchable (no channel, PENDING, lease generation 0) and the pre-existing
framework and target projections present with their new columns NULL (`data_preserved`); any of
these failing fails the check. The result is merged into the JSON report named by --report under
`upgrade_check`.

    IMPACT_ADMIN_DSN (or IMPACT_FIXTURE_DSN)   superuser connection; creates and drops the database
    IMPACT_LOGIN_PASSWORD_*                     the provisioned login passwords (see provision_logins.py)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb
from psycopg.conninfo import conninfo_to_dict, make_conninfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import migrate  # noqa: E402
from fixture_support import fixture_database_allowed  # noqa: E402
from provision_logins import login_dsn, passwords_from_env, provision  # noqa: E402

DICTIONARY = ROOT / "docs/current/CURRENT-DATA-DICTIONARY.md"
LATEST = len(list((ROOT / "infrastructure/migrations").glob("*.sql")))
BASELINE = LATEST - 1
# The session row inserted at the baseline; its identity is the fixture author.
SESSION_IDENTITY = "69407b72-0f5f-5126-8d04-a1355db5a9c5"
# The outbox row inserted at the baseline, in fixture tenant A.
OUTBOX_TENANT = "ce56220a-32a5-5ca5-a45f-860dc3d9c958"
OUTBOX_EVENT = "7b0c6a39-4f0f-4bb5-9c38-9f2d4f7e0a18"
# The planning rows inserted at the baseline (fixture tenant A, author, programme WATER-A and the
# 2026-Q3 period); synthetic identifiers.
AUTHOR_PRINCIPAL = "ed661ad8-b93f-5f9f-acb8-4d8a56774a9c"
PROGRAMME = "67bdb368-3aa8-5924-8275-52460bd936f2"
PERIOD = "13f1e2c4-1faa-55d3-b904-ed90e67406f5"
FRAMEWORK = ("0b9f3f5e-6f0e-4d1c-9c52-1a0f5d7c1a01", "0b9f3f5e-6f0e-4d1c-9c52-1a0f5d7c1a02")
TARGET = ("0b9f3f5e-6f0e-4d1c-9c52-1a0f5d7c1a03", "0b9f3f5e-6f0e-4d1c-9c52-1a0f5d7c1a04")


def insert_planning_rows(c):
    """A draft framework and a blank draft target in the projections 0019 alters."""
    for kind, (obj, rev), payload in [
        ("Framework", FRAMEWORK, {"programme_id": PROGRAMME, "version_label": "Legacy draft", "nodes": []}),
        ("Target", TARGET, {"period_id": PERIOD, "value_state": "MISSING", "value": None}),
    ]:
        c.execute(
            "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,lifecycle_state,classification,owner_id,created_at,created_by,updated_at) VALUES(%s,%s,%s,%s,'Draft','INTERNAL',%s,now(),%s,now())",
            (OUTBOX_TENANT, obj, kind, rev, AUTHOR_PRINCIPAL, AUTHOR_PRINCIPAL),
        )
        c.execute(
            "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,schema_version,payload,payload_sha256,author_id,created_at) VALUES(%s,%s,%s,%s,'1.2',%s,%s,%s,now())",
            (
                OUTBOX_TENANT,
                obj,
                rev,
                kind,
                Jsonb(payload),
                hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).digest(),
                AUTHOR_PRINCIPAL,
            ),
        )
    c.execute(
        "INSERT INTO impact.framework_current(tenant_id,object_id,revision_id,programme_id,version_label,nodes) VALUES(%s,%s,%s,%s,'Legacy draft','[]'::jsonb)",
        (OUTBOX_TENANT, *FRAMEWORK, PROGRAMME),
    )
    c.execute(
        "INSERT INTO impact.target_current(tenant_id,object_id,revision_id,period_id,value_state) VALUES(%s,%s,%s,%s,'MISSING')",
        (OUTBOX_TENANT, *TARGET, PERIOD),
    )


def ledgered_checksums():
    """The migration register table of the data dictionary: file name -> SHA-256."""
    register = {}
    for line in DICTIONARY.read_text().splitlines():
        match = re.fullmatch(r"\|\s*(\d{4}_[a-z_]+\.sql)\s*\|\s*([0-9a-f]{64})\s*\|", line.strip())
        if match:
            register[match.group(1)] = match.group(2)
    if len(register) != LATEST:
        raise RuntimeError(
            "Expected "
            + str(LATEST)
            + " ledgered migrations in the data dictionary, found "
            + str(len(register))
        )
    return register


def with_database(dsn, dbname):
    params = conninfo_to_dict(dsn)
    params["dbname"] = dbname
    return make_conninfo(**params)


def run(admin_dsn, fixture_dsn, passwords):
    base = conninfo_to_dict(fixture_dsn).get("dbname") or "impact_test"
    target = (base if fixture_database_allowed(base) and base != "impact_dev" else "impact_test") + "_upgrade"
    if not fixture_database_allowed(target):
        raise RuntimeError("Upgrade database name refused: " + target)
    started = time.monotonic()
    result = {"database": target, "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None) as c:
        c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(target)))
        c.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target)))
    provision(admin_dsn, passwords, target, verify=False)
    migrator = login_dsn(with_database(fixture_dsn, target), "impact_migrator", passwords["impact_migrator"])
    superuser = with_database(fixture_dsn, target)
    os.environ["IMPACT_ALLOW_FIXTURE_LOAD"] = "1"
    first = migrate.run(migrator, superuser, until=BASELINE, fixture=True)
    result["baseline"] = {
        "applied": first["applied"],
        "schema_version": first["schema_version"],
        "session_user": first["session_user"],
        "migration_role": first["migration_role"],
        "fixture_loaded": first["fixture_loaded"],
        "fixture_user": first.get("fixture_user"),
        "fixture_loaded_at_schema": BASELINE,
    }
    if first["schema_version"] != BASELINE or not first["fixture_loaded"]:
        raise RuntimeError("Schema-" + str(BASELINE) + " baseline was not established")
    with psycopg.connect(superuser, prepare_threshold=None) as c:
        c.execute(
            "INSERT INTO impact.web_session(session_hash,identity_id,created_at,last_seen_at,expires_at,auth_time) VALUES(%s,%s,now(),now(),now()+interval '8 hours',now())",
            (hashlib.sha256(b"upgrade-check-session").digest(), SESSION_IDENTITY),
        )
        result["baseline"]["tenants"] = c.execute("SELECT count(*) FROM impact.tenant_root").fetchone()[0]
        result["baseline"]["revisions"] = c.execute("SELECT count(*) FROM impact.object_revision").fetchone()[
            0
        ]
        result["baseline"]["sessions"] = c.execute("SELECT count(*) FROM impact.web_session").fetchone()[0]
        c.execute(
            "INSERT INTO impact.outbox_event VALUES(%s,%s,'object.changed',now(),'{}'::jsonb)",
            (OUTBOX_TENANT, OUTBOX_EVENT),
        )
        c.execute(
            "INSERT INTO impact.outbox_delivery(tenant_id,event_id) VALUES(%s,%s)",
            (OUTBOX_TENANT, OUTBOX_EVENT),
        )
        insert_planning_rows(c)
        result["baseline"]["revisions"] += 2
        result["baseline"]["calculation_rows"] = c.execute(
            "SELECT (SELECT count(*) FROM impact.indicator_definition_current)+(SELECT count(*) FROM impact.calculated_result_current)"
        ).fetchone()[0]
        result["baseline"]["outbox_deliveries"] = c.execute(
            "SELECT count(*) FROM impact.outbox_delivery"
        ).fetchone()[0]
    second = migrate.run(migrator, superuser)
    result["upgrade"] = {
        "applied": second["applied"],
        "session_user": second["session_user"],
        "migration_role": second["migration_role"],
    }
    register = ledgered_checksums()
    files = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT / "infrastructure/migrations").glob("*.sql")
    }
    if files != register:
        raise RuntimeError("Migration files differ from the ledgered checksums")
    with psycopg.connect(superuser, prepare_threshold=None) as c:
        rows = c.execute("SELECT version,sha256 FROM impact.schema_migration ORDER BY version").fetchall()
        max_version = c.execute("SELECT max(version) FROM impact.schema_migration").fetchone()[0]
        tenants = c.execute("SELECT count(*) FROM impact.tenant_root").fetchone()[0]
        revisions = c.execute("SELECT count(*) FROM impact.object_revision").fetchone()[0]
        sessions = c.execute("SELECT count(*) FROM impact.web_session").fetchone()[0]
        added = c.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema='impact' AND table_name='web_session' AND column_name IN ('provider_sid','provider_logout_hint')"
        ).fetchone()[0]
        replay_table = c.execute("SELECT to_regclass('impact.oidc_logout_token')").fetchone()[0]
        untouched = c.execute(
            "SELECT count(*) FROM impact.web_session WHERE session_hash=%s AND provider_sid IS NULL AND provider_logout_hint IS NULL",
            (hashlib.sha256(b"upgrade-check-session").digest(),),
        ).fetchone()[0]
        deliveries = c.execute("SELECT count(*) FROM impact.outbox_delivery").fetchone()[0]
        dispatch_columns = c.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema='impact' AND table_name='outbox_delivery' AND column_name IN ('channel','template','state','lease_owner','lease_generation','lease_expires_at','next_attempt_at','recipient_sealed')"
        ).fetchone()[0]
        worker_tables = [
            c.execute("SELECT to_regclass(%s)", ("impact." + name,)).fetchone()[0]
            for name in ["notification_delivery", "recovery_channel_challenge", "worker_heartbeat"]
        ]
        planning_columns = c.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema='impact' AND ((table_name='framework_current' AND column_name IN ('effective_from','supersedes_revision','supersedes_revision_kind','exceptions')) OR (table_name='target_current' AND column_name IN ('indicator_id','indicator_id_kind','milestone_label','due_at','supersedes_revision','supersedes_revision_kind','reason')))"
        ).fetchone()[0]
        planning_tables = [
            c.execute("SELECT to_regclass(%s)", ("impact." + name,)).fetchone()[0]
            for name in ["framework_baseline", "target_binding"]
        ]
        legacy_planning = c.execute(
            "SELECT (SELECT count(*) FROM impact.framework_current WHERE tenant_id=%s AND object_id=%s AND effective_from IS NULL AND supersedes_revision IS NULL AND exceptions IS NULL)+(SELECT count(*) FROM impact.target_current WHERE tenant_id=%s AND object_id=%s AND indicator_id IS NULL AND value IS NULL AND value_state='MISSING')",
            (OUTBOX_TENANT, FRAMEWORK[0], OUTBOX_TENANT, TARGET[0]),
        ).fetchone()[0]
        calculation_columns = c.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema='impact' AND table_name IN ('indicator_definition_current','calculated_result_current') AND column_name='disaggregation'"
        ).fetchone()[0]
        legacy_calculation = c.execute(
            "SELECT (SELECT count(*) FROM impact.indicator_definition_current WHERE disaggregation IS NULL)+(SELECT count(*) FROM impact.calculated_result_current WHERE disaggregation IS NULL)"
        ).fetchone()[0]
        legacy_delivery = c.execute(
            "SELECT count(*) FROM impact.outbox_delivery WHERE tenant_id=%s AND event_id=%s AND channel IS NULL AND state='PENDING' AND lease_generation=0 AND lease_owner IS NULL",
            (OUTBOX_TENANT, OUTBOX_EVENT),
        ).fetchone()[0]
    ledger = {int(name[:4]): sha for name, sha in register.items()}
    recorded = {int(v): s for v, s in rows}
    mismatches = [v for v in sorted(set(ledger) | set(recorded)) if ledger.get(v) != recorded.get(v)]
    result["verification"] = {
        "rows": len(rows),
        "max_version": max_version,
        "checksum_mismatches": mismatches,
        "tenants_after_upgrade": tenants,
        "revisions_after_upgrade": revisions,
        "sessions_after_upgrade": sessions,
        "provider_logout_columns_present": added == 2,
        "logout_token_table_present": replay_table is not None,
        "outbox_deliveries_after_upgrade": deliveries,
        "dispatch_columns_present": dispatch_columns == 8,
        "worker_tables_present": all(worker_tables),
        "planning_columns_present": planning_columns == 11,
        "planning_tables_present": all(planning_tables),
        "calculation_columns_present": calculation_columns == 2,
        "calculation_rows_preserved": legacy_calculation,
        "data_preserved": tenants == result["baseline"]["tenants"]
        and revisions == result["baseline"]["revisions"]
        and sessions == result["baseline"]["sessions"]
        and deliveries == result["baseline"]["outbox_deliveries"]
        and untouched == 1
        and legacy_delivery == 1
        and legacy_planning == 2
        and result["baseline"]["calculation_rows"] > 0
        and legacy_calculation == result["baseline"]["calculation_rows"],
    }
    if (
        mismatches
        or len(rows) != LATEST
        or max_version != LATEST
        or added != 2
        or replay_table is None
        or dispatch_columns != 8
        or not all(worker_tables)
        or planning_columns != 11
        or not all(planning_tables)
        or calculation_columns != 2
        or not result["verification"]["data_preserved"]
    ):
        raise RuntimeError("Upgrade verification failed: " + json.dumps(result["verification"]))
    with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None) as c:
        c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(target)))
    result["duration_seconds"] = round(time.monotonic() - started, 2)
    result["outcome"] = "PASS"
    return result


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--report", help="JSON file to merge the result into under the key upgrade_check")
    args = parser.parse_args()
    fixture_dsn = os.environ.get("IMPACT_FIXTURE_DSN")
    admin_dsn = os.environ.get("IMPACT_ADMIN_DSN") or fixture_dsn
    if not fixture_dsn or not admin_dsn:
        raise RuntimeError("IMPACT_FIXTURE_DSN (and optionally IMPACT_ADMIN_DSN) are required")
    try:
        result = run(admin_dsn, fixture_dsn, passwords_from_env())
        code = 0
    except Exception as exc:  # recorded, then re-raised for the exit code
        result = {"outcome": "FAIL", "error": type(exc).__name__ + ": " + str(exc)}
        code = 1
    print(json.dumps(result, indent=2, default=str))
    if args.report:
        path = Path(args.report)
        report = json.loads(path.read_text()) if path.exists() else {}
        report["upgrade_check"] = result
        path.write_text(json.dumps(report, indent=2, default=str) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
