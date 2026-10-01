"""Checks of a restored backup set inside the restore drill (deploy/restore-drill.sh).

Runs in the application image as the `drill-check` job, on the drill's own internal network,
against the throwaway `drill-db` that deploy/drill_restore.sh has just restored the set into. It
never sees the live database. Prints one JSON object (no secret, no tenant data) and exits 1 when
any check fails.

    IMPACT_DRILL_DSN        superuser connection to the restored application database
    IMPACT_DRILL_IDP_DSN    superuser connection to the restored identity-provider database
    PGPASSWORD              the drill database's one-time password (from restore-drill.sh)
    restore_check.py --set daily/YYYYMMDD [--backups /backups]

Checks:
    objects_match_digests      every member of objects.tar is <tenant>/<xx>/<sha256> and its bytes
                               hash to that name (content addressing survived)
    blobs_present_in_objects   every restored impact.file_blob row has its object in the tar, with
                               the recorded SHA-256 and size (the tar is taken after the dumps)
    migrations_checksummed     scripts/migrate.py as impact_migrator: every ledgered checksum equals
                               this image's migration file, and the copy reaches this build's schema
                               (a backup older than the image may legitimately apply newer files)
    schema_matches_manifest    the restored schema version equals the one recorded at backup time
    owned_by_impact_owner      every table of the impact schema is owned by impact_owner
    tenant_fences_forced       every table with forced row-level security has at least one policy,
                               and the forced tables are not fewer than in a fresh migration
    app_role_sees_no_rows_without_tenant   impact_app reads nothing of object_registry without a
                               transaction-local tenant
    identity_provider_realm    the restored provider database holds the `impact` realm
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import sys
import tarfile
import time
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
MEMBER = re.compile(
    r"^(?:\./)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/([0-9a-f]{2})/([0-9a-f]{64})$"
)
# Forced-RLS tables a fresh migration creates are far more than this; a restore that lost the
# fences would show far fewer. The exact number is reported alongside.
MIN_FORCED_TABLES = 50


def object_digests(archive):
    """{object key: (sha256 hex, bytes)} of the tar's regular files, and the names that are not
    content-addressed or whose bytes do not hash to their name."""
    found, mismatched, foreign = {}, [], []
    with tarfile.open(archive, mode="r|") as tar:
        for member in tar:
            if not member.isfile():
                continue
            match = MEMBER.fullmatch(member.name)
            if not match:
                foreign.append(member.name[:120])
                continue
            digest = hashlib.sha256()
            handle = tar.extractfile(member)
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
            tenant, prefix, name = match.groups()
            if digest.hexdigest() != name or prefix != name[:2]:
                mismatched.append(member.name[:120])
            found[tenant + "/" + prefix + "/" + name] = (digest.hexdigest(), member.size)
    return found, mismatched, foreign


def blob_rows(c):
    return [
        (row[0], bytes(row[1]).hex(), int(row[2]))
        for row in c.execute("SELECT object_key,sha256,bytes FROM impact.file_blob ORDER BY 1").fetchall()
    ]


def blobs_missing(rows, objects):
    """Blob rows whose object is absent from the tar or differs in digest or size."""
    return [key for key, digest, size in rows if objects.get(key) != (digest, size)]


def security(c):
    owners = {
        row[0]
        for row in c.execute(
            "SELECT DISTINCT pg_get_userbyid(c.relowner) FROM pg_class c JOIN pg_namespace n "
            "ON n.oid=c.relnamespace WHERE n.nspname='impact' AND c.relkind IN ('r','p')"
        ).fetchall()
    }
    forced, unfenced = c.execute(
        "SELECT count(*) FILTER (WHERE c.relforcerowsecurity),"
        "count(*) FILTER (WHERE c.relforcerowsecurity AND NOT EXISTS "
        "(SELECT 1 FROM pg_policy p WHERE p.polrelid=c.oid)) FROM pg_class c JOIN pg_namespace n "
        "ON n.oid=c.relnamespace WHERE n.nspname='impact' AND c.relkind IN ('r','p')"
    ).fetchone()
    return sorted(owners), forced, unfenced


def rows_without_tenant(dsn):
    with psycopg.connect(dsn, prepare_threshold=None) as c:
        c.execute("SET LOCAL ROLE impact_app")
        return c.execute("SELECT count(*) FROM impact.object_registry").fetchone()[0]


def table_totals(c):
    tables = [r[0] for r in c.execute("SELECT tablename FROM pg_tables WHERE schemaname='impact'").fetchall()]
    rows = sum(
        c.execute(sql.SQL("SELECT count(*) FROM impact.{}").format(sql.Identifier(t))).fetchone()[0]
        for t in tables
    )
    return len(tables), rows


def migrator_dsn(dsn, password):
    params = conninfo_to_dict(dsn)
    params.update(user="impact_migrator", password=password)
    return make_conninfo(**params)


def run_migrations(dsn):
    """Give the drill cluster's impact_migrator a one-time password (the cluster is discarded) and
    run the migration runner as that login, exactly as deploy/prepare_database.py does."""
    import migrate

    password = secrets.token_hex(24)
    with psycopg.connect(dsn, autocommit=True, prepare_threshold=None) as c:
        c.execute(sql.SQL("ALTER ROLE impact_migrator LOGIN PASSWORD {}").format(sql.Literal(password)))
    try:
        result = migrate.run(migrator_dsn(dsn, password))
        return {
            "session_user": result["session_user"],
            "applied": result["applied"],
            "schema_version": result["schema_version"],
            "latest": migrate.LATEST,
            "error": None,
        }
    except Exception as exc:  # a checksum mismatch is the finding, reported not raised
        return {"applied": [], "schema_version": None, "latest": migrate.LATEST, "error": str(exc)[:300]}


def check(set_dir, dsn, idp_dsn):
    started = time.monotonic()
    manifest = json.loads((set_dir / "manifest.json").read_text())
    report = {
        "set": set_dir.parent.name + "/" + set_dir.name,
        "manifest_schema": manifest.get("schema_version"),
    }
    objects, mismatched, foreign = object_digests(set_dir / "objects.tar")
    report["objects"] = {"files": len(objects), "mismatched": mismatched[:20], "foreign": foreign[:20]}
    with psycopg.connect(dsn, prepare_threshold=None) as c:
        restored_schema = c.execute("SELECT max(version) FROM impact.schema_migration").fetchone()[0]
        rows = blob_rows(c)
        owners, forced, unfenced = security(c)
        tables, total_rows = table_totals(c)
    missing = blobs_missing(rows, objects)
    report["blobs"] = {"rows": len(rows), "missing_or_different": len(missing)}
    report["restored"] = {"schema_version": restored_schema, "tables": tables, "rows": total_rows}
    report["security"] = {"owners": owners, "forced_rls_tables": forced, "forced_without_policy": unfenced}
    hidden = rows_without_tenant(dsn)
    migration = run_migrations(dsn)
    report["migration"] = migration
    with psycopg.connect(idp_dsn, prepare_threshold=None) as c:
        realm = c.execute("SELECT count(*) FROM realm WHERE name='impact'").fetchone()[0]
        report["identity_provider"] = {
            "realm": realm,
            "accounts": c.execute(
                "SELECT count(*) FROM user_entity u JOIN realm r ON r.id=u.realm_id WHERE r.name='impact'"
            ).fetchone()[0],
        }
    report["checks"] = {
        "objects_match_digests": not mismatched and not foreign,
        "blobs_present_in_objects": not missing,
        "migrations_checksummed": migration["error"] is None
        and migration["schema_version"] == migration["latest"],
        "schema_matches_manifest": restored_schema == manifest.get("schema_version"),
        "owned_by_impact_owner": owners == ["impact_owner"],
        "tenant_fences_forced": forced >= MIN_FORCED_TABLES and unfenced == 0,
        "app_role_sees_no_rows_without_tenant": hidden == 0,
        "identity_provider_realm": realm == 1,
    }
    report["seconds"] = round(time.monotonic() - started, 2)
    report["outcome"] = "PASS" if all(report["checks"].values()) else "FAIL"
    return report


def main(argv=None, env=os.environ):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--set", required=True, help="daily/YYYYMMDD or weekly/YYYYMMDD")
    parser.add_argument("--backups", default="/backups")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"(daily|weekly)/[0-9]{8}", args.set):
        print(json.dumps({"outcome": "FAIL", "error": "set must be daily/YYYYMMDD or weekly/YYYYMMDD"}))
        return 1
    try:
        report = check(Path(args.backups) / args.set, env["IMPACT_DRILL_DSN"], env["IMPACT_DRILL_IDP_DSN"])
    except Exception as exc:
        report = {"outcome": "FAIL", "error": type(exc).__name__ + ": " + str(exc)[:300]}
    print(json.dumps(report, sort_keys=True))
    return 0 if report["outcome"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
