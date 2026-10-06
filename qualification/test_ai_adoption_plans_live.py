"""Real API/registry qualification for tenant-shared nonprofit adoption drafts."""

from contextlib import contextmanager
import os
from uuid import uuid4

import psycopg
import pytest

from test_ai_adoption_plans import plan
from test_live_application import cmd, expect


def save(live, data=None, actor="admin"):
    return expect(
        live.request(live.path("ai-enablement/plans"), actor=actor, method="POST", body=cmd(data or plan())),
        201,
    )


@contextmanager
def management_disabled(live, actor):
    """Narrow the synthetic actor's management permission, restoring it afterwards."""
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grants = c.execute(
            "SELECT object_id,purpose FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability='ai.enablement.manage' AND purpose IS NULL",
            (tenant, live.fixture["actors"][actor]["principal_id"]),
        ).fetchall()
        assert grants
        c.execute(
            "UPDATE impact.grant_current SET purpose='QUALIFICATION' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
            (tenant, [str(g["object_id"]) for g in grants]),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            for grant in grants:
                c.execute(
                    "UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s",
                    (grant["purpose"], tenant, grant["object_id"]),
                )


def test_durable_adoption_plan_save_replay_revision_and_atomic_audit(live):
    path = live.path("ai-enablement/plans")
    body = cmd(plan())
    first = expect(live.request(path, actor="admin", method="POST", body=body), 201)
    assert first == expect(live.request(path, actor="admin", method="POST", body=body), 201)
    current = expect(live.request(path + "/" + first["object_id"], actor="reviewer"), 200)
    assert current["business_state"] == "Draft"
    assert current["data"]["profile"] == plan()["profile"]
    assert set(current["data"]["content_versions"]) == {"catalog", "solutions"}
    expect(
        live.request(
            path, actor="admin", method="POST", body={**body, "data": {**plan(), "title": "Changed intent"}}
        ),
        409,
    )
    updated_data = {**plan(), "title": "Synthetic reviewed pilot requirements"}
    update = cmd(updated_data, first["revision_id"])
    second = expect(
        live.request(path + "/" + first["object_id"], actor="admin", method="PUT", body=update), 200
    )
    assert second == expect(
        live.request(path + "/" + first["object_id"], actor="admin", method="PUT", body=update), 200
    )
    stale = expect(
        live.request(
            path + "/" + first["object_id"],
            actor="admin",
            method="PUT",
            body=cmd(plan(), first["revision_id"]),
        ),
        409,
    )
    assert stale["code"] == "CONFLICT_VERSION"
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        rows = c.execute(
            "SELECT revision_id,payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s ORDER BY revision_number",
            (live.fixture["tenant_a"], first["object_id"]),
        ).fetchall()
        assert len(rows) == 2 and rows[0]["payload"]["title"] == plan()["title"]
        assert rows[1]["payload"]["title"] == updated_data["title"]
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s AND action_type IN ('create_ai_adoption_plan','update_ai_adoption_plan')",
                (live.fixture["tenant_a"], first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_id'=%s",
                (live.fixture["tenant_a"], first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=ANY(%s::uuid[])",
                (live.fixture["tenant_a"], [body["operation_id"], update["operation_id"]]),
            ).fetchone()["n"]
            == 2
        )


def test_adoption_plan_readonly_tenant_revoked_wrong_kind_and_closed_data(live):
    created = save(live)
    path = live.path("ai-enablement/plans")
    # The fixture reviewer also holds MEL_ADMIN; narrow that existing write grant.
    with management_disabled(live, "reviewer"):
        expect(live.request(path, actor="reviewer"), 200)
        expect(live.request(path, actor="reviewer", method="POST", body=cmd(plan())), 404)
        expect(
            live.request(
                path + "/" + created["object_id"],
                actor="reviewer",
                method="PUT",
                body=cmd(plan(), created["revision_id"]),
            ),
            404,
        )
    for actor in ["other_tenant", "revoked"]:
        expect(live.request(path, actor=actor), 404)
        expect(live.request(path + "/" + created["object_id"], actor=actor), 404)
        expect(live.request(path, actor=actor, method="POST", body=cmd(plan())), 404)
    wrong = live.fixture["programme_a"]
    expect(live.request(path + "/" + wrong, actor="admin"), 404)
    expect(live.request(path + "/" + wrong, actor="admin", method="PUT", body=cmd(plan(), str(uuid4()))), 404)
    for malformed in [
        {**plan(), "approved": True},
        {**plan(), "content_versions": {"catalog": "forged"}},
        {**plan(), "solution_ids": ["invented-provider"]},
        {**plan(), "learning_completed": ["foundations:999"]},
        {**plan(), "pilot": {**plan()["pilot"], "completed_actions": ["AUTO_AWARD"]}},
    ]:
        expect(live.request(path, actor="admin", method="POST", body=cmd(malformed)), 422)


def test_adoption_list_pagination_and_cursor_tenant_principal_binding(live):
    for title in ["Synthetic page A", "Synthetic page B", "Synthetic page C"]:
        save(live, {**plan(), "title": title})
    path = live.path("ai-enablement/plans")
    one = expect(live.request(path + "?limit=2", actor="admin"), 200)
    assert len(one["items"]) == 2 and one["next_cursor"] and "total_rows" not in one
    seen = [r["object_id"] for r in one["items"]]
    cursor = one["next_cursor"]
    while cursor:
        page = expect(live.request(path, actor="admin", params={"limit": 2, "cursor": cursor}), 200)
        seen.extend(r["object_id"] for r in page["items"])
        cursor = page["next_cursor"]
    assert len(seen) == len(set(seen)) and len(seen) >= 3
    expect(live.request(path, actor="reviewer", params={"cursor": one["next_cursor"]}), 400)
    other_path = live.path("ai-enablement/plans", tenant=live.fixture["tenant_b"])
    expect(live.request(other_path, actor="other_tenant", params={"cursor": one["next_cursor"]}), 400)
    expect(live.request(path, actor="admin", params={"cursor": one["next_cursor"] + "forged"}), 400)
    expect(live.request(path + "?limit=101", actor="admin"), 422)


def test_scoped_adoption_reads_filter_list_and_cursors_follow_current_visibility(live):
    first, second = save(live), save(live)
    tenant, scope = live.fixture["tenant_a"], str(uuid4())
    reader = live.fixture["actors"]["reviewer"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grant = c.execute(
            "SELECT g.* FROM impact.grant_current g WHERE tenant_id=%s AND subject_id=%s AND capability='ai.enablement.read' AND purpose IS NULL LIMIT 1",
            (tenant, reader["principal_id"]),
        ).fetchone()
        template = c.execute(
            "SELECT * FROM impact.scope_definition WHERE tenant_id=%s AND scope_id=%s",
            (tenant, grant["scope_id"]),
        ).fetchone()
        c.execute(
            "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) VALUES(%s,%s,'OBJECT_SET',%s)",
            (tenant, scope, template["predicate_version"]),
        )
        c.execute("INSERT INTO impact.scope_member VALUES(%s,%s,%s)", (tenant, scope, first["object_id"]))
        c.execute(
            "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
            (scope, tenant, grant["object_id"]),
        )
    try:
        path = live.path("ai-enablement/plans")
        page = expect(live.request(path, actor="reviewer"), 200)
        assert [r["object_id"] for r in page["items"]] == [first["object_id"]]
        expect(live.request(path + "/" + first["object_id"], actor="reviewer"), 200)
        expect(live.request(path + "/" + second["object_id"], actor="reviewer"), 404)
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(
                "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
                (grant["scope_id"], tenant, grant["object_id"]),
            )


def test_adoption_exact_replay_requires_current_management_authority(live):
    path, body = live.path("ai-enablement/plans"), cmd(plan())
    first = expect(live.request(path, actor="admin", method="POST", body=body), 201)
    with management_disabled(live, "admin"):
        expect(live.request(path + "/" + first["object_id"], actor="admin"), 200)
        expect(live.request(path, actor="admin", method="POST", body=body), 404)


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1", reason="Real login-role boundaries require native PostgreSQL"
)
def test_native_adoption_revisions_are_fenced_immutable_and_hidden_from_platform(live):
    created = save(live)
    tenant = live.fixture["tenant_a"]
    dsn = os.environ.get("IMPACT_LOGIN_DSN_APP")
    assert dsn, "Native qualification must provision the application login"
    with psycopg.connect(dsn, autocommit=True) as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
            assert (
                c.execute(
                    "SELECT object_id FROM impact.object_registry WHERE object_id=%s", (created["object_id"],)
                ).fetchall()
                == []
            )
            for table in ["object_registry", "object_revision", "operation_receipt"]:
                assert c.execute(
                    "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=%s::regclass",
                    ("impact." + table,),
                ).fetchone() == (True, True)
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                c.execute(
                    "UPDATE impact.object_revision SET payload=payload WHERE tenant_id=%s AND revision_id=%s",
                    (tenant, created["revision_id"]),
                )
    platform_dsn = os.environ.get("IMPACT_LOGIN_DSN_PLATFORM")
    assert platform_dsn, "Native qualification must provision the platform login"
    with psycopg.connect(platform_dsn, autocommit=True) as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_platform")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            assert (
                c.execute(
                    "SELECT object_id FROM impact.object_registry WHERE object_id=%s", (created["object_id"],)
                ).fetchall()
                == []
            )
