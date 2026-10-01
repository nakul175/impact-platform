"""Checksum-verified migrations, the only migration runner. Fixture loading is explicit and bounded.

Connections: migrations run on IMPACT_MIGRATION_DSN (falling back to IMPACT_FIXTURE_DSN, which is
what a superuser development session supplies); the fixture loads on IMPACT_FIXTURE_DSN (falling
back to the migration connection). A non-superuser migration session must be `impact_owner` or a
member of it (the provisioned `impact_migrator` login) and runs as `impact_owner`, the role the
migrations themselves assume with SET LOCAL ROLE. The fixture is loaded by the superuser fixture
connection because every tenant table forces row-level security, including against its owner.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
import psycopg
from pglast import split

ROOT = Path(__file__).resolve().parents[1]
# The schema version this build expects (the highest migration number) and the number of migration
# files. They are equal on an integrated build; a branch carrying a later migration before the ones
# numbered between (parallel increments) differs, and every check compares like with like.
COUNT = len(list((ROOT / "infrastructure/migrations").glob("*.sql")))
LATEST = max(int(p.name[:4]) for p in (ROOT / "infrastructure/migrations").glob("*.sql"))
sys.path.insert(0, str(ROOT / "scripts"))
from fixture_support import fixture_database_allowed  # noqa: E402

MIGRATIONS = ROOT / "infrastructure/migrations"


def execute_script(c, source):
    for statement in split(source):
        if statement.strip().rstrip(";").upper() in {"BEGIN", "COMMIT"}:
            continue
        c.execute(statement)


def migration_files():
    return [(int(p.name[:4]), p) for p in sorted(MIGRATIONS.glob("*.sql"))]


def assume_owner(c):
    """Return (session_user, effective role). Migrations run as impact_owner unless a superuser runs them."""
    user, superuser = c.execute(
        "SELECT current_user,rolsuper FROM pg_roles WHERE rolname=current_user"
    ).fetchone()
    if superuser:
        # A superuser deployment administrator runs the files as written; migration 0001 creates
        # the privilege roles and the owned schema on a fresh cluster.
        return user, user
    if user != "impact_owner":
        member = c.execute(
            "SELECT CASE WHEN EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_owner') THEN pg_has_role(current_user,'impact_owner','MEMBER') ELSE false END"
        ).fetchone()[0]
        if not member:
            raise RuntimeError("Migration session must be a superuser or a member of impact_owner: " + user)
        c.execute("SET ROLE impact_owner")
    return user, "impact_owner"


def apply_migrations(c, until=None):
    present = c.execute("SELECT to_regclass('impact.schema_migration')").fetchone()[0]
    applied = (
        dict(c.execute("SELECT version,sha256 FROM impact.schema_migration").fetchall()) if present else {}
    )
    done = []
    for version, path in migration_files():
        content = path.read_bytes()
        checksum = hashlib.sha256(content).hexdigest()
        if version in applied:
            if applied[version] != checksum:
                raise RuntimeError("Migration checksum mismatch: " + path.name)
            continue
        if until is not None and version > until:
            continue
        with c.transaction():
            execute_script(c, content.decode())
            c.execute(
                "INSERT INTO impact.schema_migration(version,sha256) VALUES(%s,%s)", (version, checksum)
            )
        done.append(path.name)
        print("Applied " + path.name)
    return done


def load_fixture(c, if_empty=False):
    db = c.execute("SELECT current_database()").fetchone()[0]
    if os.environ.get("IMPACT_ALLOW_FIXTURE_LOAD") != "1" or not fixture_database_allowed(db):
        raise RuntimeError("Fixture target refused")
    if if_empty and c.execute("SELECT 1 FROM impact.tenant_root LIMIT 1").fetchone():
        print("Fixture already present; not reloaded")
        return False
    with c.transaction():
        c.execute("SELECT set_config('impact.allow_fixtures','true',true)")
        execute_script(c, (ROOT / "specification/fixtures/seed.sql").read_text())
    print("Loaded disposable acceptance fixture")
    return True


def run(migration_dsn, fixture_dsn=None, until=None, fixture=False, fixture_if_empty=False):
    with psycopg.connect(migration_dsn, autocommit=True, prepare_threshold=None) as c:
        session_user, role = assume_owner(c)
        applied = apply_migrations(c, until)
        version = c.execute("SELECT max(version) FROM impact.schema_migration").fetchone()[0]
        database = c.execute("SELECT current_database()").fetchone()[0]
    result = {
        "database": database,
        "session_user": session_user,
        "migration_role": role,
        "applied": applied,
        "schema_version": version,
        "fixture_loaded": False,
    }
    if fixture or fixture_if_empty:
        with psycopg.connect(fixture_dsn or migration_dsn, autocommit=True, prepare_threshold=None) as c:
            result["fixture_loaded"] = load_fixture(c, if_empty=fixture_if_empty)
            result["fixture_user"] = c.execute("SELECT current_user").fetchone()[0]
    return result


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--fixture", action="store_true", help="Load the acceptance fixture into an empty database"
    )
    parser.add_argument(
        "--fixture-if-empty", action="store_true", help="Load the fixture unless tenant rows already exist"
    )
    parser.add_argument("--until", type=int, help="Apply only migrations with a version up to this number")
    parser.add_argument("--json", action="store_true", help="Print a JSON summary")
    args = parser.parse_args()
    migration_dsn = os.environ.get("IMPACT_MIGRATION_DSN") or os.environ.get("IMPACT_FIXTURE_DSN")
    fixture_dsn = os.environ.get("IMPACT_FIXTURE_DSN") or migration_dsn
    if not migration_dsn:
        raise RuntimeError("An explicit migration connection is required")
    result = run(migration_dsn, fixture_dsn, args.until, args.fixture, args.fixture_if_empty)
    if args.json:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
