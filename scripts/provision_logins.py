"""Environment provisioning of the runtime login identities. Cluster-level, never a migration.

Migrations 0001 and 0013 define the NOLOGIN privilege roles; nothing in the migration set may
carry a credential or a cluster-wide login. This script is what the deployment administrator runs
instead: it creates four LOGIN roles, each a member of exactly one privilege role, with CONNECT on
one database and nothing else. Passwords arrive through the environment and are never printed.

    IMPACT_ADMIN_DSN                 superuser (or CREATEROLE) connection to the target database
    IMPACT_LOGIN_PASSWORD_APP        impact_app_login       -> impact_app       (domain requests)
    IMPACT_LOGIN_PASSWORD_IDENTITY   impact_identity_login  -> impact_identity  (identity tables)
    IMPACT_LOGIN_PASSWORD_PLATFORM   impact_platform_login  -> impact_platform  (control plane)
    IMPACT_LOGIN_PASSWORD_MIGRATOR   impact_migrator        -> impact_owner     (scripts/migrate.py)

The privilege roles are created here only when absent, with exactly the attributes migration
0001/0013 give them, so that a fresh cluster can be provisioned before the first migration runs.
`impact_owner` additionally receives CREATE on the database: migration 0001 creates the `impact`
schema with that role as its owner, and a non-superuser migration session needs the database
privilege to do so. The API never receives the administrator or migrator credential.
"""

import argparse
import json
import os
import sys

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

# Login role -> (privilege role it may SET ROLE to, password environment suffix).
LOGINS = {
    "impact_app_login": ("impact_app", "APP"),
    "impact_identity_login": ("impact_identity", "IDENTITY"),
    "impact_platform_login": ("impact_platform", "PLATFORM"),
    "impact_migrator": ("impact_owner", "MIGRATOR"),
}
# NOLOGIN privilege roles exactly as migrations 0001 (first seven) and 0013 (impact_platform) create them.
PRIVILEGE_ROLES = (
    "impact_owner",
    "impact_app",
    "impact_worker",
    "impact_identity",
    "impact_sensitive",
    "impact_privacy",
    "impact_observer",
    "impact_platform",
)
LOGIN_ATTRIBUTES = sql.SQL("LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS NOREPLICATION")


def passwords_from_env(env=os.environ):
    missing = [s for _, (_, s) in LOGINS.items() if not env.get("IMPACT_LOGIN_PASSWORD_" + s)]
    if missing:
        raise RuntimeError("Missing IMPACT_LOGIN_PASSWORD_" + "/".join(missing))
    return {login: env["IMPACT_LOGIN_PASSWORD_" + suffix] for login, (_, suffix) in LOGINS.items()}


def login_dsn(admin_dsn, login, password):
    """Same host, port and database as the administrator connection, different identity."""
    params = conninfo_to_dict(admin_dsn)
    params.update(user=login, password=password)
    return make_conninfo(**params)


def grant_database_access(c, database):
    """The database-level privileges provisioning gives, and nothing about roles or passwords:
    CONNECT on the database for the four logins and CREATE for impact_owner. The drill tools call
    this on the disposable copies they create, since a dump of one database carries no database
    ACL and the cluster-level logins already exist with their passwords."""
    for login in LOGINS:
        c.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(database), sql.Identifier(login)
            )
        )
    c.execute(sql.SQL("GRANT CREATE ON DATABASE {} TO impact_owner").format(sql.Identifier(database)))


def provision(admin_dsn, passwords, database=None, verify=True):
    with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None) as c:
        me = c.execute(
            "SELECT rolsuper OR rolcreaterole AS may_provision, current_database() AS db FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        if not me[0]:
            raise RuntimeError("IMPACT_ADMIN_DSN must identify a superuser or CREATEROLE administrator")
        database = database or me[1]
        created = []
        for role in PRIVILEGE_ROLES:
            if not c.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role,)).fetchone():
                c.execute(
                    sql.SQL(
                        "CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS"
                    ).format(sql.Identifier(role))
                )
                created.append(role)
        for login, (group, _) in LOGINS.items():
            exists = c.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (login,)).fetchone()
            c.execute(
                sql.SQL("{} ROLE {} WITH {} PASSWORD {}").format(
                    sql.SQL("ALTER" if exists else "CREATE"),
                    sql.Identifier(login),
                    LOGIN_ATTRIBUTES,
                    sql.Literal(passwords[login]),
                )
            )
            c.execute(sql.SQL("GRANT {} TO {}").format(sql.Identifier(group), sql.Identifier(login)))
            # Exactly one membership: anything else that accumulated is removed.
            for (other,) in c.execute(
                "SELECT r.rolname FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.roleid JOIN pg_roles l ON l.oid=m.member WHERE l.rolname=%s AND r.rolname<>%s",
                (login, group),
            ).fetchall():
                c.execute(sql.SQL("REVOKE {} FROM {}").format(sql.Identifier(other), sql.Identifier(login)))
        grant_database_access(c, database)
        topology = {
            row[0]: {
                "login": row[1],
                "superuser": row[2],
                "bypass_rls": row[3],
                "inherit": row[4],
                "memberships": row[5],
            }
            for row in c.execute(
                "SELECT l.rolname,l.rolcanlogin,l.rolsuper,l.rolbypassrls,l.rolinherit,"
                "COALESCE((SELECT array_agg(r.rolname ORDER BY r.rolname) FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.roleid WHERE m.member=l.oid),'{}') "
                "FROM pg_roles l WHERE l.rolname=ANY(%s) ORDER BY l.rolname",
                (list(LOGINS),),
            ).fetchall()
        }
    for login, (group, _) in LOGINS.items():
        row = topology[login]
        if row["superuser"] or row["bypass_rls"] or row["inherit"] or row["memberships"] != [group]:
            raise RuntimeError("Login topology is not as provisioned: " + login)
    verified = {}
    if verify:
        for login, (group, _) in LOGINS.items():
            verified[login] = verify_login(login_dsn(admin_dsn, login, passwords[login]), group)
    return {
        "database": database,
        "privilege_roles_created": created,
        "logins": topology,
        "verified": verified,
    }


def verify_login(dsn, group):
    """Each login can assume its own privilege role and no other; the check itself is read-only."""
    denied = []
    with psycopg.connect(dsn, autocommit=True, prepare_threshold=None) as c:
        user, superuser, bypass = c.execute(
            "SELECT current_user,rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        if superuser or bypass:
            raise RuntimeError("Privileged login: " + user)
        with c.transaction():
            c.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(group)))
            assumed = c.execute("SELECT current_user").fetchone()[0]
        if assumed != group:
            raise RuntimeError(user + " could not assume " + group)
        for other in PRIVILEGE_ROLES:
            if other == group:
                continue
            try:
                with c.transaction():
                    c.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(other)))
            except psycopg.errors.InsufficientPrivilege:
                denied.append(other)
            else:
                raise RuntimeError(user + " may assume " + other)
    return {"current_user": user, "assumes": group, "denied": denied}


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--database", help="Database granted CONNECT; defaults to the administrator's")
    parser.add_argument("--no-verify", action="store_true", help="Skip the login round-trip checks")
    args = parser.parse_args()
    admin = os.environ.get("IMPACT_ADMIN_DSN")
    if not admin:
        raise RuntimeError("IMPACT_ADMIN_DSN is required")
    result = provision(admin, passwords_from_env(), args.database, verify=not args.no_verify)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
