"""Checksum-verified migrations on native PostgreSQL. Fixture loading is explicit and bounded."""

import argparse
import hashlib
import os
from pathlib import Path
import psycopg
from pglast import split

ROOT = Path(__file__).resolve().parents[1]


def execute_script(c, source):
    for statement in split(source):
        if statement.strip().rstrip(";").upper() in {"BEGIN", "COMMIT"}:
            continue
        c.execute(statement)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    args = parser.parse_args()
    dsn = os.environ.get("IMPACT_MIGRATION_DSN") or os.environ.get("IMPACT_FIXTURE_DSN")
    if not dsn:
        raise RuntimeError("An explicit migration connection is required")
    with psycopg.connect(dsn, autocommit=True, prepare_threshold=None) as c:
        db = c.execute("SELECT current_database()").fetchone()[0]
        if args.fixture and (
            os.environ.get("IMPACT_ALLOW_FIXTURE_LOAD") != "1" or db not in {"impact_dev", "impact_test"}
        ):
            raise RuntimeError("Fixture target refused")
        present = c.execute("SELECT to_regclass('impact.schema_migration')").fetchone()[0]
        applied = (
            dict(c.execute("SELECT version,sha256 FROM impact.schema_migration").fetchall())
            if present
            else {}
        )
        for path in sorted((ROOT / "infrastructure/migrations").glob("*.sql")):
            version = int(path.name[:4])
            content = path.read_bytes()
            checksum = hashlib.sha256(content).hexdigest()
            if version in applied:
                if applied[version] != checksum:
                    raise RuntimeError("Migration checksum mismatch: " + path.name)
                continue
            with c.transaction():
                execute_script(c, content.decode())
                c.execute(
                    "INSERT INTO impact.schema_migration(version,sha256) VALUES(%s,%s)", (version, checksum)
                )
            print("Applied " + path.name)
        if args.fixture:
            with c.transaction():
                c.execute("SELECT set_config('impact.allow_fixtures','true',true)")
                execute_script(c, (ROOT / "specification/fixtures/seed.sql").read_text())
            print("Loaded disposable acceptance fixture")


if __name__ == "__main__":
    main()
