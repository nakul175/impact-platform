"""Native-only upgrade check: a populated database at the previous schema is upgraded to the latest.

LATEST is the number of migration files (17 since build 0.15.0) and BASELINE is LATEST - 1. On a
fresh disposable database next to the one named by IMPACT_FIXTURE_DSN this script applies
migrations 0001-BASELINE as the provisioned `impact_migrator` login, loads the acceptance fixture as
the superuser (the fixture touches only migration 0002/0003 tables), adds one browser session row
so that the ALTER TABLE of `impact.web_session` in 0017 runs on a populated table, applies the
remaining migration as the migrator, and then verifies with direct queries, starting no service,
that `impact.schema_migration` holds LATEST rows with exactly the SHA-256 values ledgered in
docs/current/CURRENT-DATA-DICTIONARY.md, that `max(version)` is LATEST, that the two columns and the
replay table 0017 adds exist, and that the tenant, revision and session counts loaded at the baseline are unchanged
with the pre-existing session's new columns NULL (`data_preserved`); any of these failing fails the
check. The result is merged into the JSON report named by --report under `upgrade_check`.

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
        "data_preserved": tenants == result["baseline"]["tenants"]
        and revisions == result["baseline"]["revisions"]
        and sessions == result["baseline"]["sessions"]
        and untouched == 1,
    }
    if (
        mismatches
        or len(rows) != LATEST
        or max_version != LATEST
        or added != 2
        or replay_table is None
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
