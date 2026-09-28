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
import subprocess
import sys
import uuid
from pathlib import Path

import psycopg
import pytest
from psycopg import sql
from psycopg.errors import InsufficientPrivilege

ROOT = Path(__file__).resolve().parents[1]
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
    assert summary["applied"] == [] and summary["schema_version"] == 16
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
    connection or one login for all three purposes, refuses."""
    from impact_api.config import Settings
    from impact_api.domain import DomainError
    from impact_api.store import Database

    superuser = os.environ.get("IMPACT_FIXTURE_DSN")
    assert superuser and live.config["require_unprivileged_db"] is True
    assert live.request("/health/ready", actor=None).status_code == 200
    topology = Database(Settings(**live.config)).verify_topology()
    assert {name: row["login"] for name, row in topology.items()} == {
        "app": "impact_app_login",
        "identity": "impact_identity_login",
        "platform": "impact_platform_login",
    }
    privileged = Database(Settings(**{**live.config, "app_dsn": superuser}))
    with pytest.raises(DomainError) as refused:
        privileged.verify_topology()
    assert refused.value.reason == "PRIVILEGED_RUNTIME_CONNECTION"
    with pytest.raises(RuntimeError, match="Privileged runtime connection refused"):
        with privileged.transaction():
            pass
    shared = Database(
        Settings(
            **{**live.config, "identity_dsn": live.config["app_dsn"], "platform_dsn": live.config["app_dsn"]}
        )
    )
    with pytest.raises(DomainError) as same:
        shared.verify_topology()
    assert same.value.reason == "SHARED_RUNTIME_LOGIN"
    unconfigured = Database(Settings(**{**live.config, "platform_dsn": ""}))
    with pytest.raises(DomainError) as missing:
        unconfigured.verify_topology()
    assert missing.value.reason == "PLATFORM_NOT_CONFIGURED"
