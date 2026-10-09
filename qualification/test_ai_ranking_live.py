"""US-MP-03 ranking weights on the real application role (native PostgreSQL only).

Row-level security is meaningful only on the provisioned non-superuser logins; PGlite connects as a
superuser, which bypasses it. Run with
`scripts/run.py test --native --pytest-path qualification/test_ai_ranking_live.py`.

Both tenants' weights objects are written in one transaction on the application login with
`SET LOCAL ROLE impact_app`, through the same `store.write` the API uses, and the transaction is
rolled back, so tenant B keeps the defaults for every other test.
"""

import os
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest

from impact_api.ai_ranking import DEFAULT_WEIGHTS, KIND
from impact_api.store import Context, write
from test_ai_ranking import read_weights, save

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Real login-role boundaries require native PostgreSQL",
)


def login(role):
    dsn = os.environ.get("IMPACT_LOGIN_DSN_" + role)
    assert dsn, "Native qualification must provision the " + role.lower() + " login"
    return psycopg.connect(dsn)


def context(live, actor):
    person = live.fixture["actors"][actor]
    return Context(
        person["tenant_id"],
        person["principal_id"],
        person["membership_id"],
        SimpleNamespace(natural_identity_id=person["natural_identity_id"]),
        0,
        0,
        [],
    )


def visible(c, tenant):
    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
    return {
        (str(row[0]), str(row[1]))
        for row in c.execute(
            "SELECT tenant_id,object_id FROM impact.object_registry WHERE object_type=%s", (KIND,)
        ).fetchall()
    }


def test_native_weights_singletons_are_per_tenant_and_fenced_under_the_application_role(live):
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    save(live, DEFAULT_WEIGHTS)  # tenant A's committed weights object
    a_revision = read_weights(live)["revision_id"]
    with login("APP") as c:
        c.execute("SET LOCAL ROLE impact_app")
        assert c.execute("SELECT current_user").fetchone()[0] == "impact_app"
        a_rows = visible(c, tenant_a)
        assert len(a_rows) == 1 and next(iter(a_rows))[0] == tenant_a
        a_id = next(iter(a_rows))[1]
        # Tenant B's own weights object, written as the API writes it.
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_b,))
        b = write(c, context(live, "other_tenant"), KIND, dict(DEFAULT_WEIGHTS), "Active")
        # Both singletons exist side by side (the index is per tenant, not global), and each tenant
        # sees only its own registry row and revisions.
        assert visible(c, tenant_b) == {(tenant_b, b["object_id"])}
        assert not c.execute(
            "SELECT 1 FROM impact.object_revision WHERE revision_id=%s", (a_revision,)
        ).fetchone()
        assert visible(c, tenant_a) == {(tenant_a, a_id)}
        assert not c.execute(
            "SELECT 1 FROM impact.object_revision WHERE revision_id=%s", (b["revision_id"],)
        ).fetchone()
        # Without a tenant, nothing is visible.
        c.execute("SELECT set_config('impact.tenant_id','',true)")
        assert (
            c.execute("SELECT count(*) FROM impact.object_registry WHERE object_type=%s", (KIND,)).fetchone()[
                0
            ]
            == 0
        )
        # A second weights object for the same tenant is refused by the per-tenant unique index.
        for tenant, actor in ((tenant_a, "admin"), (tenant_b, "other_tenant")):
            with pytest.raises(psycopg.errors.UniqueViolation):
                with c.transaction():
                    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                    write(c, context(live, actor), KIND, dict(DEFAULT_WEIGHTS), "Active")
        # WITH CHECK: from tenant A's context no row can be written for tenant B.
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with c.transaction():
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_a,))
                c.execute(
                    "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,"
                    "lifecycle_state,classification,owner_id,created_at,created_by,updated_at) "
                    "VALUES(%s,%s,%s,%s,'Active','INTERNAL',NULL,now(),%s,now())",
                    (
                        tenant_b,
                        str(uuid4()),
                        KIND,
                        str(uuid4()),
                        live.fixture["actors"]["other_tenant"]["principal_id"],
                    ),
                )
        index = c.execute(
            "SELECT indexdef FROM pg_indexes WHERE schemaname='impact' AND indexname='ai_ranking_weights_one_per_tenant'"
        ).fetchone()[0]
        assert "(tenant_id)" in index and "WHERE (object_type = 'AIRankingWeights'::text)" in index
        c.rollback()
    # Rolled back: tenant B still has the defaults.
    assert read_weights(live, actor="other_tenant", tenant=tenant_b)["source"] == "DEFAULT"
