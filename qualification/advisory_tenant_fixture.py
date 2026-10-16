"""A fresh synthetic workspace for tests that exercise committed daily AI budgets.

Existing request history is never deleted, backdated, or excluded from the budget query.
The fixture uses only the existing admin identity and its current explicit AI grants.
"""

from types import SimpleNamespace
from uuid import uuid4

from impact_api.store import Context, write


def isolated_advisory_tenant(live):
    tenant = str(uuid4())
    admin = live.fixture["actors"]["admin"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        grants = c.execute(
            "SELECT g.capability,g.purpose FROM impact.grant_current g "
            "JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id "
            "WHERE g.tenant_id=%s AND g.subject_id=%s AND r.lifecycle_state='Active' "
            "AND g.capability LIKE 'ai.%%'",
            (live.fixture["tenant_a"], admin["principal_id"]),
        ).fetchall()
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("INSERT INTO impact.tenant_root VALUES(%s,'TEST_LOCAL','Active',0)", (tenant,))
        c.execute(
            "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind) "
            "VALUES(%s,%s,%s,'HUMAN')",
            (tenant, admin["principal_id"], admin["identity_id"]),
        )
        ctx = Context(
            tenant,
            admin["principal_id"],
            str(uuid4()),
            SimpleNamespace(natural_identity_id=admin["natural_identity_id"]),
            0,
            0,
            [],
        )
        write(
            c,
            ctx,
            "Membership",
            {
                "identity_id": admin["identity_id"],
                "authority_source": "LOCAL_TEST",
                "external": False,
            },
            "Active",
            object_id=ctx.membership_id,
            track_author=False,
        )
        predicate = write(c, ctx, "Predicate", {"scope_type": "TENANT"}, track_author=False)
        scope = str(uuid4())
        c.execute(
            "INSERT INTO impact.scope_definition VALUES(%s,%s,'TENANT',%s)",
            (tenant, scope, predicate["revision_id"]),
        )
        for grant in grants:
            data = {
                "subject_id": admin["principal_id"],
                "capability": grant["capability"],
                "scope_id": scope,
                "starts_at": "2026-01-01T00:00:00Z",
                "expires_at": "2027-01-01T00:00:00Z",
                "issuer_id": admin["principal_id"],
            }
            if grant["purpose"]:
                data["purpose"] = grant["purpose"]
            write(c, ctx, "Grant", data, "Active", track_author=False)
    return tenant
