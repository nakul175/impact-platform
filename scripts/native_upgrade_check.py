"""Native-only upgrade check: a populated schema-15 database is upgraded to schema 16.

On a fresh disposable database next to the one named by IMPACT_FIXTURE_DSN this script applies
migrations 0001-0015 as the provisioned `impact_migrator` login, loads the acceptance fixture as the
superuser (the fixture touches only migration 0002/0003 tables, so it is loaded before 0016 as a
genuinely populated pre-upgrade database), applies the remaining migration as the migrator, and
then verifies with direct queries, starting no service, that `impact.schema_migration` holds all 16
rows with exactly the SHA-256 values ledgered in docs/current/CURRENT-DATA-DICTIONARY.md, that
`max(version)` is 16, that the table 0016 adds exists, and that the tenant and revision counts
loaded at schema 15 are unchanged (`data_preserved`); any of these failing fails the check. The
result is merged into the JSON report named by --report.

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


def ledgered_checksums():
    """The migration register table of the data dictionary: file name -> SHA-256."""
    register = {}
    for line in DICTIONARY.read_text().splitlines():
        match = re.fullmatch(r"\|\s*(\d{4}_[a-z_]+\.sql)\s*\|\s*([0-9a-f]{64})\s*\|", line.strip())
        if match:
            register[match.group(1)] = match.group(2)
    if len(register) != 16:
        raise RuntimeError(
            "Expected 16 ledgered migrations in the data dictionary, found " + str(len(register))
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
    first = migrate.run(migrator, superuser, until=15, fixture=True)
    result["schema_15"] = {
        "applied": first["applied"],
        "schema_version": first["schema_version"],
        "session_user": first["session_user"],
        "migration_role": first["migration_role"],
        "fixture_loaded": first["fixture_loaded"],
        "fixture_user": first.get("fixture_user"),
        "fixture_loaded_at_schema": 15,
    }
    if first["schema_version"] != 15 or not first["fixture_loaded"]:
        raise RuntimeError("Schema-15 baseline was not established")
    with psycopg.connect(superuser, prepare_threshold=None) as c:
        result["schema_15"]["tenants"] = c.execute("SELECT count(*) FROM impact.tenant_root").fetchone()[0]
        result["schema_15"]["revisions"] = c.execute(
            "SELECT count(*) FROM impact.object_revision"
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
        renewal_table = c.execute("SELECT to_regclass('impact.tenant_authority_renewal')").fetchone()[0]
    ledger = {int(name[:4]): sha for name, sha in register.items()}
    recorded = {int(v): s for v, s in rows}
    mismatches = [v for v in sorted(set(ledger) | set(recorded)) if ledger.get(v) != recorded.get(v)]
    result["verification"] = {
        "rows": len(rows),
        "max_version": max_version,
        "checksum_mismatches": mismatches,
        "tenants_after_upgrade": tenants,
        "revisions_after_upgrade": revisions,
        "authority_renewal_table_present": renewal_table is not None,
        "data_preserved": tenants == result["schema_15"]["tenants"]
        and revisions == result["schema_15"]["revisions"],
    }
    if (
        mismatches
        or len(rows) != 16
        or max_version != 16
        or renewal_table is None
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
