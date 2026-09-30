"""Prepare the deployment database cluster; the one-shot `migrate` job of deploy/compose.yaml.

Idempotent, and run on every deployment before the API and worker start:

1. provision the five runtime and migration logins on the application database with
   scripts/provision_logins.py (passwords from IMPACT_LOGIN_PASSWORD_*), revoking PUBLIC's
   CONNECT on it (`--revoke-public-connect`);
2. create or re-password the identity provider's own login role and database (`keycloak`), which
   holds nothing of the application and is reachable by that role only;
3. apply the checksum-ledgered migrations with scripts/migrate.py as `impact_migrator`.

It never loads the acceptance fixture, never creates tenants, identities or grants, and never
prints a password. Environment:

    IMPACT_ADMIN_DSN              superuser connection to the application database
    IMPACT_LOGIN_PASSWORD_APP/IDENTITY/PLATFORM/WORKER/MIGRATOR
    IMPACT_KEYCLOAK_DB_PASSWORD   password of the provider's `keycloak` login
    IMPACT_KEYCLOAK_DB            provider database name (default keycloak)
"""

import json
import os
import sys
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from provision_logins import login_dsn, passwords_from_env, provision  # noqa: E402
import migrate  # noqa: E402

PROVIDER_ROLE = "keycloak"
PROVIDER_ATTRIBUTES = sql.SQL("LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS NOREPLICATION")


def prepare_provider_database(admin_dsn, password, database="keycloak"):
    """The provider's login and database: created when absent, re-passworded every run so the
    stored secret stays authoritative, owned by that login, closed to PUBLIC."""
    if len(password) < 32:
        raise RuntimeError("IMPACT_KEYCLOAK_DB_PASSWORD must be at least 32 characters")
    with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None) as c:
        if not c.execute("SELECT rolsuper FROM pg_roles WHERE rolname=current_user").fetchone()[0]:
            raise RuntimeError("IMPACT_ADMIN_DSN must identify a superuser")
        exists = c.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (PROVIDER_ROLE,)).fetchone()
        c.execute(
            sql.SQL("{} ROLE {} WITH {} PASSWORD {}").format(
                sql.SQL("ALTER" if exists else "CREATE"),
                sql.Identifier(PROVIDER_ROLE),
                PROVIDER_ATTRIBUTES,
                sql.Literal(password),
            )
        )
        created = False
        if not c.execute("SELECT 1 FROM pg_database WHERE datname=%s", (database,)).fetchone():
            c.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(database), sql.Identifier(PROVIDER_ROLE)
                )
            )
            created = True
        c.execute(sql.SQL("REVOKE CONNECT ON DATABASE {} FROM PUBLIC").format(sql.Identifier(database)))
        c.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(database), sql.Identifier(PROVIDER_ROLE)
            )
        )
        # The maintenance database holds nothing, but no runtime login needs to open it either.
        c.execute("REVOKE CONNECT ON DATABASE postgres FROM PUBLIC")
    return {"database": database, "role": PROVIDER_ROLE, "created": created}


def main(env=os.environ):
    admin = env.get("IMPACT_ADMIN_DSN")
    if not admin:
        raise RuntimeError("IMPACT_ADMIN_DSN is required")
    if env.get("IMPACT_ALLOW_FIXTURE_LOAD"):
        raise RuntimeError("A deployment database never loads the acceptance fixture")
    passwords = passwords_from_env(env)
    logins = provision(admin, passwords, verify=True, revoke_public=True)
    provider = prepare_provider_database(
        admin, env.get("IMPACT_KEYCLOAK_DB_PASSWORD", ""), env.get("IMPACT_KEYCLOAK_DB", "keycloak")
    )
    migrated = migrate.run(login_dsn(admin, "impact_migrator", passwords["impact_migrator"]))
    if migrated["schema_version"] != migrate.LATEST:
        raise RuntimeError("Schema version " + str(migrated["schema_version"]) + " after migration")
    summary = {
        "database": logins["database"],
        "host": conninfo_to_dict(admin).get("host"),
        "public_connect": logins["public_connect"],
        "logins": sorted(logins["logins"]),
        "provider_database": provider,
        "migration_role": migrated["migration_role"],
        "applied": migrated["applied"],
        "schema_version": migrated["schema_version"],
        "fixture_loaded": migrated["fixture_loaded"],
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
