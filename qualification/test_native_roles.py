"""Native-only login-role boundaries. Every expected denial below is derived from the GRANT,
REVOKE and row-level-security statements of the migrations named in each test, not from the
application code: 0001 (privilege roles), 0003 (tenant-table grants to impact_app/impact_worker
and forced tenant fences), 0004/0005/0012 (identity-only tables), 0013/0014 (impact_platform's
grants and its RESTRICTIVE object-type policies), 0015 and 0016 (control-plane tables readable by
impact_platform only). A denial is asserted as PostgreSQL insufficient_privilege (sqlstate 42501)
or, for a fence, as an empty result; nothing here is a status code of the API.
"""

import json
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx
import psycopg
import pytest
from psycopg import sql
from psycopg.errors import InsufficientPrivilege

ROOT = Path(__file__).resolve().parents[1]
LOGIN_NAMES = ["impact_app_login", "impact_identity_login", "impact_platform_login", "impact_migrator"]
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="native PostgreSQL only: PGlite serves one superuser session and has no login-role "
    "topology to test (run scripts/run.py test --native)",
)
PRIVILEGE_ROLES = [
    "impact_owner",
    "impact_app",
    "impact_worker",
    "impact_identity",
    "impact_sensitive",
    "impact_privacy",
    "impact_observer",
    "impact_platform",
]


def dsn(name):
    value = os.environ.get("IMPACT_LOGIN_DSN_" + name)
    if not value:
        pytest.skip("IMPACT_LOGIN_DSN_" + name + " is exported only by scripts/run.py test --native")
    return value


@pytest.fixture
def connect():
    opened = []

    def _connect(name):
        c = psycopg.connect(dsn(name), autocommit=True, prepare_threshold=None)
        opened.append(c)
        return c

    yield _connect
    for c in opened:
        c.close()


class Rollback(Exception):
    pass


def denied(c, statement, params=None, role=None, tenant=None):
    """The statement fails with exactly insufficient_privilege inside a rolled-back transaction."""
    with pytest.raises(InsufficientPrivilege) as info:
        with c.transaction():
            if role:
                c.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
            if tenant:
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(statement, params)
    assert info.value.sqlstate == "42501", info.value
    return str(info.value)


def query(c, statement, params=None, role=None, tenant=None):
    """Run one read as the given role inside a transaction and return all rows."""
    with c.transaction():
        if role:
            c.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
        if tenant:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return c.execute(statement, params).fetchall()


def assumable(c, role):
    try:
        with c.transaction():
            c.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
            return c.execute("SELECT current_user").fetchone()[0] == role
    except InsufficientPrivilege as exc:
        assert exc.sqlstate == "42501"
        return False


@pytest.mark.parametrize(
    "login,own",
    [("APP", "impact_app"), ("IDENTITY", "impact_identity"), ("PLATFORM", "impact_platform")],
)
def test_each_login_is_unprivileged_and_assumes_exactly_its_own_role(connect, login, own):
    c = connect(login)
    user, superuser, bypass, inherit, owner_member = c.execute(
        "SELECT current_user,rolsuper,rolbypassrls,rolinherit,pg_has_role(current_user,'impact_owner','MEMBER') FROM pg_roles WHERE rolname=current_user"
    ).fetchone()
    assert user == own + "_login" and not superuser and not bypass and not inherit and not owner_member
    assert assumable(c, own)
    for other in PRIVILEGE_ROLES:
        if other != own:
            assert not assumable(c, other), user + " may assume " + other
    # Without SET ROLE the login itself holds nothing: no schema usage was granted to it (0001, 0013).
    denied(c, "SELECT count(*) FROM impact.schema_migration")


def test_app_role_cannot_read_control_plane_tables(connect, live):
    """0013 grants platform_operator/deployment_qualification SELECT to impact_platform only; 0014,
    0015 and 0016 grant tenant_access_bootstrap, tenant_recovery_contact and tenant_authority_renewal
    to impact_platform only. impact_app has no grant on any of them."""
    c = connect("APP")
    tenant = live.fixture["tenant_a"]
    for table in [
        "tenant_authority_renewal",
        "tenant_recovery_contact",
        "platform_operator",
        "deployment_qualification",
        "tenant_access_bootstrap",
        "tenant_access_bootstrap_applied",
        "tenant_onboarding",
        "platform_event",
        # 0028 (v0.26a): operator nominations and provisioned accounts, platform only.
        "platform_operator_nomination",
        "provider_account",
        # 0029 (v0.27): the operator change register, platform only.
        "platform_operator_change",
    ]:
        message = denied(c, "SELECT count(*) FROM impact." + table, role="impact_app", tenant=tenant)
        assert "permission denied" in message
    # Positive control: the same role reads the fenced tenant tables 0003 grants it.
    assert query(c, "SELECT count(*) FROM impact.tenant_root", role="impact_app", tenant=tenant) == [(1,)]
    assert query(c, "SELECT count(*) FROM impact.grant_current", role="impact_app", tenant=tenant)[0][0] > 0


def test_app_role_tenant_fence_needs_transaction_local_tenant(connect, live):
    """0003 forces the tenant_fence policy on every tenant table: no tenant setting means no rows,
    and a tenant setting exposes exactly that tenant."""
    c = connect("APP")
    a, b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    for table in ["object_registry", "object_revision", "tenant_root", "grant_current", "membership_current"]:
        assert query(c, "SELECT count(*) FROM impact." + table, role="impact_app") == [(0,)], table
    seen_a = query(
        c, "SELECT DISTINCT tenant_id::text FROM impact.object_registry", role="impact_app", tenant=a
    )
    seen_b = query(
        c, "SELECT DISTINCT tenant_id::text FROM impact.object_registry", role="impact_app", tenant=b
    )
    assert seen_a == [(a,)] and seen_b == [(b,)]
    assert query(
        c, "SELECT count(*) FROM impact.object_registry WHERE tenant_id=%s", (b,), role="impact_app", tenant=a
    ) == [(0,)]
    # Writing another tenant's row is refused by the policy's WITH CHECK, not by a constraint.
    message = denied(
        c,
        "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) VALUES(%s,%s,'TENANT',%s)",
        (b, str(uuid.uuid4()), str(uuid.uuid4())),
        role="impact_app",
        tenant=a,
    )
    assert "row-level security" in message


def test_identity_role_reads_identity_tables_only(connect, live):
    """0003/0004/0005/0012 grant auth_identity, sessions, invitations, profiles, security state and
    preferences to impact_identity; no tenant table is granted to it and the identity_tenants
    function (0004) is its only view of memberships."""
    c = connect("IDENTITY")
    identity = live.fixture["actors"]["author"]["identity_id"]
    tenant = live.fixture["tenant_a"]
    assert query(c, "SELECT count(*) FROM impact.auth_identity", role="impact_identity")[0][0] >= 10
    # Earlier tests may have made this identity a principal of tenants they created; the fixture
    # tenant is always among them and the function is the identity role's only membership view.
    assert (tenant,) in query(
        c, "SELECT tenant_id::text FROM impact.identity_tenants(%s)", (identity,), role="impact_identity"
    )
    for table in [
        "object_registry",
        "object_revision",
        "tenant_principal",
        "tenant_root",
        "grant_current",
        "membership_current",
        "grant_authority",
        "tenant_authority_renewal",
        "tenant_recovery_contact",
        "platform_operator",
    ]:
        assert "permission denied" in denied(
            c, "SELECT count(*) FROM impact." + table, role="impact_identity", tenant=tenant
        ), table


def test_platform_role_writes_only_its_restrictive_object_types(connect, live):
    """0013 grants impact_platform SELECT/INSERT on object_revision and RESTRICTIVE policies bound
    to a fixed object-type list, widened once by 0014 to Tenant, Membership, HostingPolicy,
    PrivacyPolicy, RetentionPolicy, Grant, RoleTemplate and Predicate. A Programme revision is
    outside that list; grant_authority is SELECT-only and member_role_assignment SELECT/INSERT
    (0014), so both expiries can be re-dated only by the SECURITY DEFINER applicator (0016)."""
    c = connect("PLATFORM")
    tenant = live.fixture["tenant_a"]
    membership = live.records["member_author"]
    programme = live.fixture["programme_a"]
    principal = live.fixture["actors"]["author"]["principal_id"]

    def revision_insert(object_id, object_type):
        return (
            "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,revision_number) VALUES(%s,%s,%s,%s,NULL,'1.2','{}'::jsonb,%s,%s,now(),99)",
            (tenant, object_id, str(uuid.uuid4()), object_type, b"\x00" * 32, principal),
        )

    # Positive control, rolled back: a Membership revision passes both policies.
    with pytest.raises(Rollback):
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_platform")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(*revision_insert(membership["object_id"], "Membership"))
            assert (
                c.execute(
                    "SELECT count(*) FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_number=99",
                    (tenant, membership["object_id"]),
                ).fetchone()[0]
                == 1
            )
            raise Rollback
    message = denied(c, *revision_insert(programme, "Programme"), role="impact_platform", tenant=tenant)
    assert "row-level security" in message
    # The restrictive policy also hides business revisions from the platform role's reads.
    assert query(
        c,
        "SELECT count(*) FROM impact.object_revision WHERE object_type='Programme'",
        role="impact_platform",
        tenant=tenant,
    ) == [(0,)]
    for statement in [
        "SELECT count(*) FROM impact.programme_current",
        "SELECT count(*) FROM impact.observation_current",
        "UPDATE impact.grant_authority SET expires_at=expires_at",
        "UPDATE impact.member_role_assignment SET expires_at=expires_at",
        "DELETE FROM impact.object_revision",
        "UPDATE impact.object_revision SET payload=payload",
        "INSERT INTO impact.grant_authority(tenant_id,authority_id,principal_id,capability,scope_id,expires_at) VALUES(%s,gen_random_uuid(),%s,'programmes.read',gen_random_uuid(),now())",
    ]:
        params = (tenant, principal) if statement.startswith("INSERT INTO impact.grant_authority") else None
        assert "permission denied" in denied(c, statement, params, role="impact_platform", tenant=tenant), (
            statement
        )


def test_platform_role_cannot_make_operators_or_rewrite_nominations(connect, live):
    """0028 (v0.26a): impact_platform holds SELECT/INSERT on platform_operator_nomination and
    provider_account, UPDATE on a few decision columns only, and no write on platform_operator
    (0013); an acceptance is recorded only by the definer accept_operator_nomination, which refuses
    an actor of the nominating operator's natural person; identities of provisioned accounts only
    through register_provider_account_identity. app, identity and worker logins reach none of it."""
    c = connect("PLATFORM")
    admin = live.fixture["actors"]["admin"]
    for statement, params in [
        (
            "INSERT INTO impact.platform_operator(identity_id,active,expires_at,authority_reference) VALUES(%s,true,now()+interval '1 day','direct')",
            (live.fixture["actors"]["author"]["identity_id"],),
        ),
        ("UPDATE impact.platform_operator SET expires_at=expires_at+interval '1 year'", None),
        ("UPDATE impact.platform_operator_nomination SET email_hash=email_hash", None),
        ("UPDATE impact.platform_operator_nomination SET operator_expires_at=now()", None),
        ("UPDATE impact.provider_account SET provider_subject='other'", None),
        ("DELETE FROM impact.platform_operator_nomination", None),
        ("DELETE FROM impact.provider_account", None),
        ("INSERT INTO impact.auth_identity VALUES(gen_random_uuid(),'x','y',gen_random_uuid())", None),
    ]:
        assert "permission denied" in denied(c, statement, params, role="impact_platform"), statement
    nomination = str(uuid.uuid4())
    with pytest.raises(Rollback):
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_platform")
            c.execute(
                "INSERT INTO impact.platform_operator_nomination(nomination_id,revision_id,state,nominated_by,email_hash,email_mask,reason,operator_expires_at,expires_at,nominator_auth_time) VALUES(%s,gen_random_uuid(),'Nominated',%s,%s,'ad***@example.test','native check',now()+interval '10 days',now()+interval '1 day',now())",
                (nomination, admin["identity_id"], b"\x01" * 32),
            )
            with pytest.raises(psycopg.Error) as refused:
                with c.transaction():
                    c.execute(
                        "UPDATE impact.platform_operator_nomination SET state='Accepted' WHERE nomination_id=%s",
                        (nomination,),
                    )
            assert "acceptance only through" in str(refused.value)
            # The nominating operator cannot accept through the definer either.
            with pytest.raises(InsufficientPrivilege):
                with c.transaction():
                    c.execute(
                        "SELECT impact.accept_operator_nomination(%s,%s)", (nomination, admin["identity_id"])
                    )
            raise Rollback
    for login, role in [("APP", "impact_app"), ("IDENTITY", "impact_identity")]:
        other = connect(login)
        for statement in [
            "SELECT count(*) FROM impact.platform_operator_nomination",
            "SELECT count(*) FROM impact.provider_account",
            "SELECT impact.register_provider_account_identity(gen_random_uuid())",
            "SELECT impact.accept_operator_nomination(gen_random_uuid(),gen_random_uuid())",
        ]:
            assert "permission denied" in denied(other, statement, role=role), (login, statement)


def test_platform_role_changes_operators_only_through_the_definer(connect, live):
    """0029 (v0.27): impact_platform reads platform_operator_change and still writes nothing on
    platform_operator; renewal and deactivation go through the definer apply_operator_change, which
    refuses the subject as actor, another identity of the subject's natural person, a non-operator
    actor, a stale revision and a renewal that does not move the expiry later. app, identity and
    worker logins reach neither the register nor the definer."""
    c = connect("PLATFORM")
    admin, owner, author = (live.fixture["actors"][k] for k in ["admin", "owner", "author"])
    for statement, params in [
        ("UPDATE impact.platform_operator SET active=false", None),
        ("UPDATE impact.platform_operator SET expires_at=expires_at+interval '1 day'", None),
        (
            "INSERT INTO impact.platform_operator_change(change_id,operator_identity_id,action,actor_identity_id,actor_auth_time,reason,previous_revision_id,revision_id,previous_expires_at,expires_at,previous_active,active) VALUES(gen_random_uuid(),%s,'deactivate',%s,now(),'x',gen_random_uuid(),gen_random_uuid(),now(),now(),true,false)",
            (owner["identity_id"], admin["identity_id"]),
        ),
        ("DELETE FROM impact.platform_operator_change", None),
        ("UPDATE impact.platform_operator_change SET reason='x'", None),
    ]:
        assert "permission denied" in denied(c, statement, params, role="impact_platform"), statement
    revision = query(
        c,
        "SELECT revision_id FROM impact.platform_operator WHERE identity_id=%s",
        (owner["identity_id"],),
        role="impact_platform",
    )[0][0]
    for actor, expected, action, expiry in [
        (owner["identity_id"], revision, "deactivate", None),  # the subject as actor
        (author["identity_id"], revision, "deactivate", None),  # not an operator
        (admin["identity_id"], uuid.uuid4(), "deactivate", None),  # stale revision
        (admin["identity_id"], revision, "renew", "now()"),  # not later than the current expiry
    ]:
        with pytest.raises(psycopg.Error, match="operator change denied") as refused:
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_platform")
                c.execute(
                    "SELECT impact.apply_operator_change(gen_random_uuid(),%s,%s,%s,%s,"
                    + (expiry or "NULL")
                    + ",now(),'native check')",
                    (owner["identity_id"], actor, action, expected),
                )
        assert refused.value.sqlstate == "42501"
    # Another identity of the subject's natural person is the subject: with admin linked to the
    # owner's natural person (inside a transaction that is rolled back), admin cannot act on owner.
    with live.db() as superuser:
        with pytest.raises(Rollback):
            with superuser.transaction():
                superuser.execute(
                    "UPDATE impact.auth_identity SET natural_identity_id=(SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s) WHERE identity_id=%s",
                    (owner["identity_id"], admin["identity_id"]),
                )
                with pytest.raises(psycopg.Error, match="operator change denied"):
                    with superuser.transaction():
                        superuser.execute("SET LOCAL ROLE impact_platform")
                        superuser.execute(
                            "SELECT impact.apply_operator_change(gen_random_uuid(),%s,%s,'deactivate',%s,NULL,now(),'x')",
                            (owner["identity_id"], admin["identity_id"], revision),
                        )
                raise Rollback
    assert query(c, "SELECT count(*) FROM impact.platform_operator_change", role="impact_platform")[0][0] >= 0
    for login, role in [("APP", "impact_app"), ("IDENTITY", "impact_identity"), ("WORKER", "impact_worker")]:
        other = connect(login)
        for statement in [
            "SELECT count(*) FROM impact.platform_operator_change",
            "SELECT impact.apply_operator_change(gen_random_uuid(),gen_random_uuid(),gen_random_uuid(),'renew',gen_random_uuid(),now(),now(),'x')",
        ]:
            assert "permission denied" in denied(other, statement, role=role), (login, statement)


def test_migrator_assumes_owner_only_and_runs_the_migration_runner(connect, live):
    """impact_migrator is a member of impact_owner alone; scripts/migrate.py runs as impact_owner
    on that login and verifies every ledgered checksum. A domain login cannot run it."""
    c = connect("MIGRATOR")
    assert assumable(c, "impact_owner")
    for other in PRIVILEGE_ROLES:
        if other != "impact_owner":
            assert not assumable(c, other), other
    env = {**os.environ, "IMPACT_MIGRATION_DSN": dsn("MIGRATOR"), "PYTHONPATH": str(ROOT / "apps/api")}
    env.pop("IMPACT_FIXTURE_DSN", None)
    completed = subprocess.run(
        [sys.executable, "scripts/migrate.py", "--json"], cwd=ROOT, env=env, capture_output=True, text=True
    )
    assert completed.returncode == 0, completed.stderr
    summary = json.loads(completed.stdout.strip().splitlines()[-1])
    assert summary["session_user"] == "impact_migrator"
    assert summary["migration_role"] == "impact_owner"
    assert summary["applied"] == [] and summary["schema_version"] == len(
        list((ROOT / "infrastructure/migrations").glob("*.sql"))
    )
    refused = subprocess.run(
        [sys.executable, "scripts/migrate.py"],
        cwd=ROOT,
        env={**env, "IMPACT_MIGRATION_DSN": dsn("APP")},
        capture_output=True,
        text=True,
    )
    assert refused.returncode != 0 and "member of impact_owner" in refused.stderr


def test_runtime_guard_refuses_privileged_and_shared_connections(live):
    """The API runs with IMPACT_REQUIRE_UNPRIVILEGED_DB=1 and passed readiness, so its three
    connections are distinct unprivileged logins. The same guard, given the superuser fixture
    connection or one login for all three purposes, refuses: readiness and, on the request path,
    every transaction before a connection is yielded. A refusal is never cached."""
    from impact_api.config import Settings
    from impact_api.domain import DomainError
    from impact_api.store import Database

    superuser = os.environ.get("IMPACT_FIXTURE_DSN")
    assert superuser and live.config["require_unprivileged_db"] is True
    assert live.request("/health/ready", actor=None).status_code == 200
    verified = Database(Settings(**live.config))
    topology = verified.verify_topology()
    assert {name: row["login"] for name, row in topology.items()} == {
        "app": "impact_app_login",
        "identity": "impact_identity_login",
        "platform": "impact_platform_login",
    }
    assert verified.topology_verified is topology and verified.topology_verified_at
    with verified.transaction() as c:
        assert c.execute("SELECT current_user").fetchone()["current_user"] == "impact_app"
    privileged = Database(Settings(**{**live.config, "app_dsn": superuser}))
    with pytest.raises(DomainError) as refused:
        privileged.verify_topology()
    assert refused.value.reason == "PRIVILEGED_RUNTIME_CONNECTION"
    assert privileged.topology_verified is None and privileged.topology_verified_at is None
    with pytest.raises(DomainError) as refused_transaction:
        with privileged.transaction():
            raise AssertionError("a connection was yielded on a privileged login")
    assert refused_transaction.value.reason == "PRIVILEGED_RUNTIME_CONNECTION"
    shared = Database(
        Settings(
            **{**live.config, "identity_dsn": live.config["app_dsn"], "platform_dsn": live.config["app_dsn"]}
        )
    )
    with pytest.raises(DomainError) as same:
        shared.verify_topology()
    assert same.value.reason == "SHARED_RUNTIME_LOGIN"
    assert shared.topology_verified is None
    for kwargs in [{}, {"identity": True}, {"platform": True}, {"tenant": live.fixture["tenant_a"]}]:
        with pytest.raises(DomainError) as same_transaction:
            with shared.transaction(**kwargs):
                raise AssertionError("a connection was yielded on a shared login")
        assert same_transaction.value.reason == "SHARED_RUNTIME_LOGIN", kwargs
    unconfigured = Database(Settings(**{**live.config, "platform_dsn": ""}))
    with pytest.raises(DomainError) as missing:
        unconfigured.verify_topology()
    assert missing.value.reason == "PLATFORM_NOT_CONFIGURED"
    with pytest.raises(DomainError) as missing_transaction:
        with unconfigured.transaction():
            raise AssertionError("a connection was yielded without a platform login")
    assert missing_transaction.value.reason == "PLATFORM_NOT_CONFIGURED"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_revoke_public_connect_refuses_a_login_without_a_grant(live):
    """On a scratch database of the suite's cluster, a throwaway login with no grant at all opens
    the database (PUBLIC keeps PostgreSQL's default CONNECT), scripts/provision_logins.py
    --revoke-public-connect then makes the same connection fail with 'permission denied for
    database' while the four provisioned logins, granted CONNECT explicitly, still open it; a
    CREATEROLE-only administrator is refused by the script before it changes anything. The scratch
    database and both throwaway roles are dropped afterwards."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from provision_logins import LOGINS, login_dsn, passwords_from_env
    from native_upgrade_check import with_database

    superuser = os.environ["IMPACT_FIXTURE_DSN"]
    suffix = uuid.uuid4().hex[:8]
    scratch, bystander, weak_admin = (
        "impact_test_public_" + suffix,
        "bystander_" + suffix,
        "weak_admin_" + suffix,
    )
    secret = uuid.uuid4().hex
    scratch_dsn = with_database(superuser, scratch)
    passwords = passwords_from_env()

    def opens(login, password):
        try:
            with psycopg.connect(login_dsn(scratch_dsn, login, password), connect_timeout=5) as c:
                return c.execute("SELECT current_user").fetchone()[0] == login
        except psycopg.OperationalError as exc:
            assert "permission denied for database" in str(exc), exc
            return False

    def provision_cli(admin_dsn, *flags):
        return subprocess.run(
            [sys.executable, "scripts/provision_logins.py", "--database", scratch, "--no-verify", *flags],
            cwd=ROOT,
            env={**os.environ, "IMPACT_ADMIN_DSN": admin_dsn},
            capture_output=True,
            text=True,
        )

    with psycopg.connect(superuser, autocommit=True, prepare_threshold=None) as c:
        c.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(scratch)))
        for role in [bystander, weak_admin]:
            c.execute(
                sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOBYPASSRLS NOINHERIT {} PASSWORD {}").format(
                    sql.Identifier(role),
                    sql.SQL("CREATEROLE" if role == weak_admin else "NOCREATEROLE"),
                    sql.Literal(secret),
                )
            )
    try:
        assert opens(bystander, secret), "PUBLIC's default CONNECT admits a login with no grant"
        # CREATEROLE alone cannot provision: no ADMIN OPTION on the privilege roles, no ownership.
        refused = provision_cli(login_dsn(scratch_dsn, weak_admin, secret))
        assert refused.returncode != 0 and "ADMIN OPTION" in refused.stderr, refused.stderr
        assert opens(bystander, secret)
        # Default off: provisioning alone leaves PUBLIC's CONNECT in place.
        kept = provision_cli(superuser)
        assert kept.returncode == 0, kept.stderr
        assert json.loads(kept.stdout)["public_connect"] is True
        assert opens(bystander, secret)
        revoked = provision_cli(superuser, "--revoke-public-connect")
        assert revoked.returncode == 0, revoked.stderr
        assert json.loads(revoked.stdout)["public_connect"] is False
        assert not opens(bystander, secret), "a login without a grant must be refused after the revocation"
        for login in LOGINS:
            assert opens(login, passwords[login]), login
    finally:
        with psycopg.connect(superuser, autocommit=True, prepare_threshold=None) as c:
            c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(scratch)))
            for role in [bystander, weak_admin]:
                c.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role)))


def test_api_on_a_shared_login_refuses_requests_not_only_readiness(live):
    """A second API process started on the suite's configuration with the app login for all three
    connections: readiness reports SHARED_RUNTIME_LOGIN, and so does a domain read with a valid
    token, since the guard runs before any transaction yields a connection. No login name reaches
    a response. The process is stopped before the test returns."""
    config_path = live.local / "shared-login-config.json"
    config_path.write_text(
        json.dumps(
            {**live.config, "identity_dsn": live.config["app_dsn"], "platform_dsn": live.config["app_dsn"]}
        )
    )
    config_path.chmod(0o600)
    port = free_port()
    base = "http://127.0.0.1:" + str(port)
    log = (live.local / "shared-login-api.log").open("w")
    api = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "impact_api.main:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-access-log",
        ],
        cwd=ROOT,
        # Only the configuration file: no IMPACT_* override, fixture or migration connection.
        env={
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", str(live.local)),
            "PYTHONPATH": str(ROOT / "apps/api"),
            "IMPACT_CONFIG_FILE": str(config_path),
            "NO_PROXY": "127.0.0.1,localhost",
            "no_proxy": "127.0.0.1,localhost",
        },
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        with httpx.Client(base_url=base, trust_env=False, timeout=5) as client:
            for _ in range(240):
                assert api.poll() is None, "the shared-login API process exited; see shared-login-api.log"
                try:
                    if client.get("/health/live").status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.25)
            else:
                raise AssertionError("the shared-login API process did not start")
            ready = client.get("/health/ready")
            programmes = client.get(
                live.path("programmes"), headers={"Authorization": "Bearer " + live.token("author")}
            )
            # The cookie path opens the identity transaction before looking the session up.
            me = client.get("/auth/me", headers={"Cookie": "impact_dev_session=" + str(uuid.uuid4())})
        for response in [ready, programmes, me]:
            assert response.status_code == 503, response.text
            body = response.json()
            assert body["code"] == "SERVICE_UNAVAILABLE" and body["reason_code"] == "SHARED_RUNTIME_LOGIN"
            assert body["retryable"] is True and body["message"] == "The request could not be completed."
            assert not any(name in response.text for name in LOGIN_NAMES), response.text
        assert live.request("/health/ready", actor=None).status_code == 200
    finally:
        if api.poll() is None:
            api.terminate()
            try:
                api.wait(timeout=10)
            except subprocess.TimeoutExpired:
                api.kill()
                api.wait()
        log.close()
    assert api.poll() is not None
    assert "SHARED_RUNTIME_LOGIN" in (live.local / "shared-login-api.log").read_text()
