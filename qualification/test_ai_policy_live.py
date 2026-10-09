"""FR-AI-001 policy registers on real login roles (native PostgreSQL only).

Row-level security, grants and the insert-only guards are only meaningful on the provisioned
non-superuser logins; PGlite connects as a superuser, which bypasses row security. Run with
`scripts/run.py test --native --pytest-path qualification/test_ai_policy_live.py`.
"""

import os
from uuid import uuid4

import psycopg
import pytest

from test_ai_policy import advisory_rule, enact

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Real login-role boundaries require native PostgreSQL",
)
TABLES = ("ai_policy_version", "ai_use_case_policy")


def login(role):
    dsn = os.environ.get("IMPACT_LOGIN_DSN_" + role)
    assert dsn, "Native qualification must provision the " + role.lower() + " login"
    return psycopg.connect(dsn, autocommit=True)


def test_native_policy_registers_are_fenced_forced_and_visible_only_to_their_tenant(live):
    receipt = enact(live, [advisory_rule()])
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    with login("APP") as c:
        for table in TABLES:
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                assert c.execute(
                    "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=%s::regclass",
                    ("impact." + table,),
                ).fetchone() == (True, True)
                # No tenant context: nothing is visible.
                assert c.execute(f"SELECT * FROM impact.{table}").fetchall() == []
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_b,))
                assert (
                    c.execute(
                        f"SELECT * FROM impact.{table} WHERE policy_version_id=%s",
                        (receipt["policy_version_id"],),
                    ).fetchall()
                    == []
                )
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_a,))
                rows = c.execute(
                    f"SELECT tenant_id FROM impact.{table} WHERE policy_version_id=%s",
                    (receipt["policy_version_id"],),
                ).fetchall()
                assert rows and {str(row[0]) for row in rows} == {tenant_a}


def test_native_application_role_cannot_rewrite_delete_or_cross_the_fence(live):
    receipt = enact(live, [advisory_rule()])
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    with login("APP") as c:
        for table in TABLES:
            for statement in (
                f"UPDATE impact.{table} SET tenant_id=tenant_id",
                f"DELETE FROM impact.{table}",
            ):
                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    with c.transaction():
                        c.execute("SET LOCAL ROLE impact_app")
                        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_a,))
                        c.execute(statement)
        # WITH CHECK: a row for another tenant cannot be inserted from tenant B's context.
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_b,))
                c.execute(
                    "INSERT INTO impact.ai_use_case_policy(tenant_id,policy_version_id,use_case,enabled,data_classes,"
                    "destinations,purposes,languages,review_mode,budget_units,tools) "
                    "VALUES(%s,%s,'CHAT',false,'{}','{}','{}','{}','HUMAN_REVIEW',0,'{}')",
                    (tenant_a, receipt["policy_version_id"]),
                )
        # The forged version insert under the right tenant still fails its typed revision keys.
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_a,))
                c.execute(
                    "INSERT INTO impact.ai_policy_version(tenant_id,policy_version_id,object_id,version_no,"
                    "created_by,created_at) VALUES(%s,%s,%s,999999,%s,now())",
                    (
                        tenant_a,
                        str(uuid4()),
                        receipt["object_id"],
                        live.fixture["actors"]["admin"]["principal_id"],
                    ),
                )


@pytest.mark.parametrize("role", ["PLATFORM", "IDENTITY", "WORKER"])
def test_native_other_runtime_roles_cannot_read_or_write_the_policy(live, role):
    enact(live, [advisory_rule()])
    with login(role) as c:
        for table in TABLES:
            for statement in (
                f"SELECT * FROM impact.{table}",
                f"DELETE FROM impact.{table}",
            ):
                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    with c.transaction():
                        c.execute(
                            "SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],)
                        )
                        c.execute(statement)
