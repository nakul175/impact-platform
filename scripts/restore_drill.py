"""Native-only backup and restore drill of the database the qualification suite just used.

Given IMPACT_FIXTURE_DSN (a superuser connection to a disposable impact_test[_suffix] database)
the drill dumps that database with `pg_dump -Fc` to a temporary file, creates `<database>_restored`
beside it, restores the archive with `pg_restore`, grants the provisioned login roles CONNECT on the
copy, runs scripts/migrate.py against it as `impact_migrator` (which must apply nothing and find
all ledgered checksums in place, one per migration file), and verifies by direct query that the seeded OFFICIAL result
46.36 is present, that every table of the `impact` schema holds exactly as many rows as the
source, and that ownership and row-level security survived: every table is owned by
`impact_owner`, the forced tenant fences are in place, `impact_app` reads nothing without a
transaction-local tenant and exactly that tenant with one, and it still cannot read the
control-plane tables. The copy is dropped afterwards. The result is written to
docs/evidence/native-restore-drill.json and, with --report, merged under `restore_drill`.

    IMPACT_FIXTURE_DSN                 superuser connection to the source database (required)
    IMPACT_ADMIN_DSN                   superuser connection used to create and drop the copy (default: fixture)
    IMPACT_LOGIN_PASSWORD_APP          the passwords the four provisioned logins already have
    IMPACT_LOGIN_PASSWORD_IDENTITY     (all four required; the drill never generates, sets or
    IMPACT_LOGIN_PASSWORD_PLATFORM     rotates a credential and never alters a role: the copy
    IMPACT_LOGIN_PASSWORD_MIGRATOR     only receives the database-level CONNECT/CREATE grants)
    IMPACT_PG_BIN                      directory holding pg_dump and pg_restore (default: PATH)

pg_dump must be at least as new as the server: an older client refuses a newer server. Both
binaries are recorded with their versions so the evidence shows which client did the work. The
superuser password never appears on a command line: pg_dump and pg_restore receive host, port,
user and database as arguments and the password through PGPASSWORD in their environment.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.errors import InsufficientPrivilege

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import migrate  # noqa: E402
from fixture_support import fixture_database_allowed  # noqa: E402
from native_upgrade_check import ledgered_checksums, with_database  # noqa: E402
from provision_logins import LOGINS, grant_database_access, login_dsn, passwords_from_env  # noqa: E402

EVIDENCE = ROOT / "docs/evidence/native-restore-drill.json"
FIXTURE = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text())
RECORDS = {r["key"]: r for r in json.loads((ROOT / "specification/fixtures/records.json").read_text())}
# The seeded OFFICIAL pooled result (51/110) inside the seeded locked snapshot: fixture data, not a
# calculation by this build, and exactly what a restore must bring back byte for byte.
GOLDEN = {"displayed_value": "46.36", "value": "46.363636363636", "mode": "OFFICIAL"}
CONTROL_PLANE_TABLES = ["tenant_authority_renewal", "tenant_recovery_contact", "platform_operator"]


def binary(name, pg_bin):
    path = shutil.which(name, path=pg_bin) if pg_bin else shutil.which(name)
    if not path:
        raise RuntimeError(name + " is not available" + (" in " + pg_bin if pg_bin else " on PATH"))
    version = subprocess.run([path, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    match = re.search(r"\(PostgreSQL\) (\d+)", version)
    return {"path": path, "version": version, "major": int(match.group(1)) if match else None}


def timed(command, env=None):
    started = time.monotonic()
    completed = subprocess.run(command, capture_output=True, text=True, env=env)
    seconds = round(time.monotonic() - started, 2)
    if completed.returncode != 0:
        raise RuntimeError(
            command[0] + " failed (" + str(completed.returncode) + "): " + completed.stderr.strip()[-2000:]
        )
    return seconds, completed.stderr.strip()


def client_connection(dsn):
    """Split a DSN for the client tools: a conninfo string of everything but the password (host,
    port, user, dbname and any connection option) for the command line, and the password, if the
    DSN carries one, for PGPASSWORD in the tool's environment."""
    params = conninfo_to_dict(dsn)
    password = params.pop("password", None)
    return make_conninfo(**params), password


def tool_environment(dsn):
    env = {**os.environ, "PGCONNECT_TIMEOUT": "10"}
    env.pop("PGPASSWORD", None)
    password = client_connection(dsn)[1]
    if password:
        env["PGPASSWORD"] = password
    return env


def table_counts(dsn):
    """Row count of every table in the impact schema, partitions included, keyed by name."""
    with psycopg.connect(dsn, prepare_threshold=None) as c:
        tables = [
            row[0]
            for row in c.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname='impact' ORDER BY tablename"
            ).fetchall()
        ]
        return {
            table: c.execute(
                sql.SQL("SELECT count(*) FROM impact.{}").format(sql.Identifier(table))
            ).fetchone()[0]
            for table in tables
        }


def security_map(dsn):
    """Owner, row-level-security flags and policy count of every impact table, keyed by name."""
    with psycopg.connect(dsn, prepare_threshold=None) as c:
        rows = c.execute(
            "SELECT c.relname,pg_get_userbyid(c.relowner),c.relrowsecurity,c.relforcerowsecurity,"
            "(SELECT count(*) FROM pg_policy p WHERE p.polrelid=c.oid) "
            "FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='impact' AND c.relkind IN ('r','p') ORDER BY c.relname"
        ).fetchall()
        functions = c.execute(
            "SELECT p.proname,pg_get_userbyid(p.proowner),p.prosecdef FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='impact' ORDER BY p.proname"
        ).fetchall()
        grants = c.execute(
            "SELECT c.relname,g.rolname,a.privilege_type,a.is_grantable FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace, aclexplode(c.relacl) a JOIN pg_roles g ON g.oid=a.grantee WHERE n.nspname='impact' AND c.relkind IN ('r','p') ORDER BY 1,2,3,4"
        ).fetchall()
    return {
        "tables": {
            name: {"owner": owner, "rls": rls, "force_rls": force, "policies": policies}
            for name, owner, rls, force, policies in rows
        },
        "functions": {
            name: {"owner": owner, "security_definer": secdef} for name, owner, secdef in functions
        },
        "grants": [list(row) for row in grants],
    }


def golden(dsn):
    """The seeded OFFICIAL result revision and its membership of the seeded snapshot revision."""
    tenant = FIXTURE["tenant_a"]
    result, snapshot = RECORDS["pooled_result"], RECORDS["snapshot"]
    with psycopg.connect(dsn, prepare_threshold=None) as c:
        row = c.execute(
            "SELECT payload->>'displayed_value',payload->>'value',payload->>'mode',payload_sha256 FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
            (tenant, result["object_id"], result["revision_id"]),
        ).fetchone()
        versions = c.execute(
            "SELECT payload->'result_versions' FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
            (tenant, snapshot["object_id"], snapshot["revision_id"]),
        ).fetchone()
        projected = c.execute(
            "SELECT displayed_value,mode FROM impact.calculated_result_current WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
            (tenant, result["object_id"], result["revision_id"]),
        ).fetchone()
    found = dict(zip(["displayed_value", "value", "mode"], row[:3])) if row else None
    in_snapshot = bool(versions and result["revision_id"] in (versions[0] or []))
    return {
        "result_revision": result["revision_id"],
        "snapshot_revision": snapshot["revision_id"],
        "expected": GOLDEN,
        "found": found,
        "payload_sha256": bytes(row[3]).hex() if row else None,
        "result_in_seeded_snapshot": in_snapshot,
        "projection": list(projected) if projected else None,
        "ok": found == GOLDEN and in_snapshot and projected == (GOLDEN["displayed_value"], GOLDEN["mode"]),
    }


def fenced_reads(app_dsn):
    """impact_app on the restored copy: nothing without a tenant, one tenant with one, and no
    control-plane table at all (sqlstate 42501)."""
    checks = {}
    with psycopg.connect(app_dsn, autocommit=True, prepare_threshold=None) as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            checks["rows_without_tenant"] = c.execute(
                "SELECT count(*) FROM impact.object_registry"
            ).fetchone()[0]
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (FIXTURE["tenant_a"],))
            checks["rows_with_tenant_a"] = c.execute(
                "SELECT count(*) FROM impact.object_registry"
            ).fetchone()[0]
            checks["tenants_visible_with_tenant_a"] = [
                str(row[0])
                for row in c.execute("SELECT DISTINCT tenant_id FROM impact.object_registry").fetchall()
            ]
        denied = []
        for table in CONTROL_PLANE_TABLES:
            try:
                with c.transaction():
                    c.execute("SET LOCAL ROLE impact_app")
                    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (FIXTURE["tenant_a"],))
                    c.execute(sql.SQL("SELECT count(*) FROM impact.{}").format(sql.Identifier(table)))
            except InsufficientPrivilege as exc:
                if exc.sqlstate == "42501":
                    denied.append(table)
        checks["control_plane_tables_denied"] = denied
    checks["ok"] = (
        checks["rows_without_tenant"] == 0
        and checks["rows_with_tenant_a"] > 0
        and checks["tenants_visible_with_tenant_a"] == [FIXTURE["tenant_a"]]
        and denied == CONTROL_PLANE_TABLES
    )
    return checks


def run(admin_dsn, fixture_dsn, passwords, pg_bin=None, keep=False):
    source = conninfo_to_dict(fixture_dsn).get("dbname")
    if not fixture_database_allowed(source) or source == "impact_dev":
        raise RuntimeError(
            "The drill runs only against a disposable impact_test[_suffix] database: " + str(source)
        )
    target = source + "_restored"
    if not fixture_database_allowed(target):
        raise RuntimeError("Restored database name refused: " + target)
    started = time.monotonic()
    result = {
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_database": source,
        "restored_database": target,
    }
    pg_dump, pg_restore = binary("pg_dump", pg_bin), binary("pg_restore", pg_bin)
    with psycopg.connect(fixture_dsn, prepare_threshold=None) as c:
        server = c.execute("SHOW server_version").fetchone()[0]
    result["server_version"] = server
    result["client"] = {"pg_dump": pg_dump, "pg_restore": pg_restore}
    if pg_dump["major"] is None or pg_dump["major"] < int(server.split(".")[0]):
        raise RuntimeError(
            "pg_dump " + pg_dump["version"] + " is older than the server " + server + "; set IMPACT_PG_BIN"
        )
    result["source"] = {
        "tables": table_counts(fixture_dsn),
        "golden": golden(fixture_dsn),
        "security": security_map(fixture_dsn),
    }
    tool_env = tool_environment(fixture_dsn)
    with tempfile.TemporaryDirectory(prefix="impact-restore-drill-") as workdir:
        archive = Path(workdir) / (source + ".dump")
        seconds, notes = timed(
            [
                pg_dump["path"],
                "--format=custom",
                "--no-password",
                "--dbname=" + client_connection(fixture_dsn)[0],
                "--file=" + str(archive),
            ],
            tool_env,
        )
        result["dump"] = {
            "format": "custom",
            "seconds": seconds,
            "bytes": archive.stat().st_size,
            "warnings": notes or None,
        }
        with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None) as c:
            c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(target)))
            c.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target)))
        target_dsn = with_database(fixture_dsn, target)
        seconds, notes = timed(
            [
                pg_restore["path"],
                "--no-password",
                "--exit-on-error",
                "--dbname=" + client_connection(target_dsn)[0],
                str(archive),
            ],
            tool_env,
        )
        result["restore"] = {"seconds": seconds, "warnings": notes or None}
    # The login roles are cluster-level and survive with their passwords; a dump of one database
    # carries no database ACL, so the copy receives only the CONNECT/CREATE grants. No role is
    # created or altered and no password is set here.
    with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None) as c:
        grant_database_access(c, target)
    migrator = login_dsn(target_dsn, "impact_migrator", passwords["impact_migrator"])
    migration = migrate.run(migrator)
    register = ledgered_checksums()
    with psycopg.connect(target_dsn, prepare_threshold=None) as c:
        recorded = {
            int(v): s for v, s in c.execute("SELECT version,sha256 FROM impact.schema_migration").fetchall()
        }
    ledger = {int(name[:4]): sha for name, sha in register.items()}
    result["migration"] = {
        "session_user": migration["session_user"],
        "migration_role": migration["migration_role"],
        "applied": migration["applied"],
        "schema_version": migration["schema_version"],
        "checksums_verified": len(recorded),
        "checksum_mismatches": [
            v for v in sorted(set(ledger) | set(recorded)) if ledger.get(v) != recorded.get(v)
        ],
    }
    restored = {
        "tables": table_counts(target_dsn),
        "golden": golden(target_dsn),
        "security": security_map(target_dsn),
    }
    result["restored"] = {"golden": restored["golden"]}
    differing = {
        table: {"source": result["source"]["tables"].get(table), "restored": restored["tables"].get(table)}
        for table in sorted(set(result["source"]["tables"]) | set(restored["tables"]))
        if result["source"]["tables"].get(table) != restored["tables"].get(table)
    }
    result["row_counts"] = {
        "tables_compared": len(restored["tables"]),
        "rows_compared": sum(restored["tables"].values()),
        "named": {
            table: restored["tables"].get(table)
            for table in [
                "object_revision",
                "operation_receipt",
                "outbox_event",
                "outbox_delivery",
                "platform_event",
            ]
        },
        "differing": differing,
    }
    owners = {row["owner"] for row in restored["security"]["tables"].values()}
    result["security"] = {
        "tables": len(restored["security"]["tables"]),
        "owners": sorted(owners),
        "rls_and_policies_identical": restored["security"]["tables"]
        == result["source"]["security"]["tables"],
        "functions_identical": restored["security"]["functions"] == result["source"]["security"]["functions"],
        "grants_identical": restored["security"]["grants"] == result["source"]["security"]["grants"],
        "fenced_reads": fenced_reads(
            login_dsn(target_dsn, "impact_app_login", passwords["impact_app_login"])
        ),
    }
    del result["source"]["security"], result["source"]["tables"]
    checks = {
        "migration_applied_nothing": migration["applied"] == []
        and migration["schema_version"] == migrate.LATEST,
        "checksums_ok": len(recorded) == migrate.COUNT and not result["migration"]["checksum_mismatches"],
        "golden_official_result": restored["golden"]["ok"] and result["source"]["golden"]["ok"],
        "row_counts_equal": not differing,
        "owned_by_impact_owner": owners == {"impact_owner"},
        "rls_survived": result["security"]["rls_and_policies_identical"]
        and result["security"]["functions_identical"]
        and result["security"]["grants_identical"]
        and result["security"]["fenced_reads"]["ok"],
    }
    result["checks"] = checks
    if not keep:
        with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None) as c:
            c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(target)))
    result["restored_database_dropped"] = not keep
    result["duration_seconds"] = round(time.monotonic() - started, 2)
    result["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result["outcome"] = "PASS" if all(checks.values()) else "FAIL"
    if result["outcome"] != "PASS":
        raise RuntimeError("Restore drill checks failed: " + json.dumps(checks))
    return result


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--report", help="JSON file to merge the result into under the key restore_drill")
    parser.add_argument("--keep", action="store_true", help="Keep the restored database for inspection")
    args = parser.parse_args()
    fixture_dsn = os.environ.get("IMPACT_FIXTURE_DSN")
    admin_dsn = os.environ.get("IMPACT_ADMIN_DSN") or fixture_dsn
    if not fixture_dsn:
        raise RuntimeError("IMPACT_FIXTURE_DSN (and optionally IMPACT_ADMIN_DSN) are required")
    try:
        try:
            passwords = passwords_from_env()
        except RuntimeError:
            # The drill only connects as the provisioned logins; it never generates or sets a
            # password, so the operator must supply the ones the roles already have.
            raise RuntimeError(
                "The restore drill needs the passwords of the four provisioned logins in "
                + ", ".join("IMPACT_LOGIN_PASSWORD_" + suffix for _, suffix in LOGINS.values())
                + "; it does not generate or rotate credentials (scripts/run.py test --native exports "
                + "them, and scripts/provision_logins.py sets them)"
            ) from None
        result = run(admin_dsn, fixture_dsn, passwords, os.environ.get("IMPACT_PG_BIN") or None, args.keep)
        result["credentials_altered"] = False
        code = 0
    except Exception as exc:  # recorded, then reported through the exit code
        result = {"outcome": "FAIL", "error": type(exc).__name__ + ": " + str(exc)}
        code = 1
    print(json.dumps(result, indent=2, default=str))
    EVIDENCE.write_text(json.dumps(result, indent=2, default=str) + "\n")
    if args.report:
        path = Path(args.report)
        report = json.loads(path.read_text()) if path.exists() else {}
        report["restore_drill"] = result
        path.write_text(json.dumps(report, indent=2, default=str) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
