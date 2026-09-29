"""Tenant administration increment: permissions, lifecycle, immutable history, and accounts."""

import json
import time
from types import SimpleNamespace
from uuid import uuid4
import httpx
import pytest
from test_administration import (
    command,
    expect,
    expiry,
    join,
    listing,
    member,
    request_as,
    role,
    signed,
    tenant_scope,
)
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.contracts import DELEGABLE_CAPABILITIES, IMPLEMENTED_OPERATIONS, OPERATIONS, validate
from impact_api.store import Database


def create(live, route, data, actor="admin", status=200):
    return expect(
        live.request(
            live.path(route),
            actor=actor,
            method="POST",
            body=command({"reason": "Workspace qualification", **data}),
        ),
        status,
    )


def act(live, route, item, action, data=None, actor="admin", status=200):
    return expect(
        live.request(
            live.path(route, item["object_id"]) + "/actions/" + action,
            actor=actor,
            method="POST",
            body=command({"reason": "Workspace qualification", **(data or {})}, item.get("revision_id")),
        ),
        status,
    )


def custom_role(live, capabilities=None):
    return create(
        live,
        "role-templates",
        {"name": "Custom " + str(uuid4())[:8], "capabilities": capabilities or ["programmes.read"]},
    )


@pytest.mark.parametrize(
    "route,schema",
    [
        ("access-groups", "AccessGroupList"),
        ("group-change-requests", "GroupChangeList"),
        ("organisation-units", "UnitDirectoryList"),
        ("renewal-requests", "MembershipRenewalList"),
        ("ownership-transfers", "OwnershipTransferList"),
    ],
)
def test_closed_workspace_lists(live, route, schema):
    validate(schema, expect(live.request(live.path(route), actor="admin"), 200))
    expect(live.request(live.path(route), actor="author"), 200 if route == "organisation-units" else 403)


def test_custom_role_ceiling_system_protection_and_immutable_versions(live):
    before = role(live)
    act(live, "role-templates", before, "retire", status=403)
    create(live, "role-templates", {"name": "Not delegated", "capabilities": ["identity.unmask"]}, status=403)
    created = custom_role(live)
    revised = act(
        live,
        "role-templates",
        created,
        "revise",
        {"name": "Revised " + str(uuid4())[:8], "capabilities": ["programmes.read", "observations.read"]},
    )
    act(live, "role-templates", created, "retire", status=409)
    with live.db() as c:
        revisions = c.execute(
            "SELECT payload FROM impact.object_revision WHERE object_id=%s ORDER BY revision_number",
            (created["object_id"],),
        ).fetchall()
    assert revisions[0]["payload"]["capabilities"] == ["programmes.read"]
    assert len(revisions) == 2
    act(live, "role-templates", revised, "retire")
    assert created["object_id"] not in {r["object_id"] for r in listing(live, "role-templates")}


def test_custom_roles_delegate_only_implemented_capabilities(live):
    """#19: a capability of a design-only operation is not delegable, even inside the creator's
    delegation ceiling; the orphan baseline policy row is gone from the generated policy."""
    assert "create_organisation_units" not in OPERATIONS
    assert "create_organisation_unit" in OPERATIONS
    design_only = {
        p["capability"]
        for p in OPERATIONS.values()
        if not p.get("purpose_required") and p["capability"] not in DELEGABLE_CAPABILITIES
    }
    assert design_only and all(
        p["operation_id"] not in IMPLEMENTED_OPERATIONS
        for p in OPERATIONS.values()
        if p["capability"] in design_only
    )
    admin = live.fixture["actors"]["admin"]
    with live.db() as c:
        ceilings = {
            r["capability"]
            for r in c.execute(
                "SELECT capability FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s AND expires_at>now()",
                (admin["tenant_id"], admin["principal_id"]),
            ).fetchall()
        }
    # The fixture administrator holds no ceiling for a design-only capability, so give it one for
    # the duration of the check: before #19 that alone made the capability delegable.
    target = sorted(design_only - ceilings)[0]
    ceiling, scope = str(uuid4()), tenant_scope(live)
    with live.db() as c:
        c.execute(
            "INSERT INTO impact.grant_authority VALUES(%s,%s,%s,%s,%s,now()+interval '1 day')",
            (admin["tenant_id"], ceiling, admin["principal_id"], target, scope),
        )
    try:
        refused = create(
            live,
            "role-templates",
            {"name": "Design only " + str(uuid4())[:8], "capabilities": ["programmes.read", target]},
            status=403,
        )
        assert refused["code"] == "POLICY_DENIED" and refused["reason_code"] == "CAPABILITY_NOT_DELEGABLE"
        implemented = sorted(DELEGABLE_CAPABILITIES & ceilings)
        assert "programmes.read" in implemented
        created = custom_role(live, implemented[:3])
        act(
            live,
            "role-templates",
            created,
            "revise",
            {"name": "Revised " + str(uuid4())[:8], "capabilities": [target]},
            status=403,
        )
    finally:
        with live.db() as c:
            c.execute(
                "DELETE FROM impact.grant_authority WHERE tenant_id=%s AND authority_id=%s",
                (admin["tenant_id"], ceiling),
            )


def unit(live, parent=None):
    return create(
        live,
        "organisation-units",
        {"code": "UNIT_" + str(uuid4())[:8].upper(), "name": "Test unit", "parent_id": parent},
    )


def test_organisation_cycle_cross_tenant_and_root_move_projection(live):
    root, other = unit(live), unit(live)
    child = unit(live, root["object_id"])
    act(live, "organisation-units", root, "reparent", {"parent_id": child["object_id"]}, status=422)
    moved = act(live, "organisation-units", child, "reparent", {"parent_id": other["object_id"]})
    result = act(live, "organisation-units", moved, "reparent", {"parent_id": None})
    act(live, "organisation-units", child, "rename", {"name": "Stale"}, status=409)
    with live.db() as c:
        assert (
            c.execute(
                "SELECT parent_id FROM impact.organisation_unit_current WHERE object_id=%s",
                (child["object_id"],),
            ).fetchone()["parent_id"]
            is None
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s", (child["object_id"],)
            ).fetchone()["n"]
            == 3
        )
    data = next(r for r in listing(live, "organisation-units") if r["object_id"] == result["object_id"])
    assert data["parent_id"] is None
    response = live.request(
        live.path("organisation-units", root["object_id"], tenant=live.fixture["tenant_b"])
        + "/actions/rename",
        actor="admin",
        method="POST",
        body=command({"name": "Bad", "reason": "Test"}, root["revision_id"]),
    )
    expect(response, 404)


def group_proposal(live, group, member_id, role_id):
    return create(
        live,
        "group-change-requests",
        {
            "group_id": group["object_id"],
            "expected_group_revision": group["revision_id"],
            "membership_ids": [member_id],
            "bindings": [
                {"role_template_id": role_id, "scope_ids": [tenant_scope(live)], "expires_at": expiry(5)}
            ],
        },
    )


def test_group_review_derived_access_removal_and_role_revision_pinning(live):
    identity, joined = join(live)
    custom = custom_role(live, ["groups.read"])
    group = create(live, "access-groups", {"name": "Group " + str(uuid4())[:8]})
    expect(request_as(live, identity, live.path("access-groups")), 403)
    proposal = group_proposal(live, group, joined["object_id"], custom["object_id"])
    act(live, "group-change-requests", proposal, "approve", status=403)
    act(live, "group-change-requests", proposal, "approve", actor="owner")
    expect(request_as(live, identity, live.path("access-groups")), 200)
    act(
        live,
        "role-templates",
        custom,
        "revise",
        {"name": "Changed " + str(uuid4())[:8], "capabilities": ["groups.read", "roles.manage"]},
    )
    access = expect(request_as(live, identity, live.path("me/access")), 200)
    assert "groups.read" in access["capabilities"] and "roles.manage" not in access["capabilities"]
    current = next(r for r in listing(live, "access-groups") if r["object_id"] == group["object_id"])
    act(live, "access-groups", current, "remove-member", {"membership_id": joined["object_id"]})
    expect(request_as(live, identity, live.path("access-groups")), 403)
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.group_entitlement WHERE group_id=%s", (group["object_id"],)
            ).fetchone()["n"]
            == 0
        )


def test_pending_group_approval_rejects_changed_role_and_group(live):
    _, joined = join(live)
    custom = custom_role(live)
    group = create(live, "access-groups", {"name": "Stale group " + str(uuid4())[:8]})
    proposal = group_proposal(live, group, joined["object_id"], custom["object_id"])
    act(
        live,
        "role-templates",
        custom,
        "revise",
        {"name": "Revised " + str(uuid4())[:8], "capabilities": ["programmes.read"]},
    )
    act(live, "group-change-requests", proposal, "approve", actor="owner", status=409)
    act(live, "group-change-requests", proposal, "reject", actor="owner")
    proposal = group_proposal(live, group, joined["object_id"], custom["object_id"])
    act(live, "access-groups", group, "retire")
    act(live, "group-change-requests", proposal, "approve", actor="owner", status=409)


def test_renewal_requires_independence_and_never_restores_old_permissions(live):
    identity, joined = join(live)
    token = signed(live, identity)
    current = member(live, joined["object_id"])
    renewal = create(
        live,
        "renewal-requests",
        {
            "membership_id": current["object_id"],
            "expected_membership_revision": current["revision_id"],
            "expires_at": expiry(40),
        },
    )
    act(live, "renewal-requests", renewal, "approve", status=403)
    act(live, "renewal-requests", renewal, "approve", actor="owner")
    expect(request_as(live, identity, live.path("me/access"), token=token), 401)
    assert expect(request_as(live, identity, live.path("me/access")), 200)["capabilities"] == []
    assert member(live, joined["object_id"])["grants"] == []


def test_owner_transfer_requires_nominee_and_transfers_no_grants(live):
    owner = member(live, live.fixture["actors"]["owner"]["membership_id"])
    successor = member(live, live.fixture["actors"]["admin"]["membership_id"])
    data = {"membership_id": successor["object_id"], "expected_membership_revision": successor["revision_id"]}
    create(live, "ownership-transfers", data, status=403)
    transfer = create(live, "ownership-transfers", data, actor="owner")
    act(live, "ownership-transfers", transfer, "accept", actor="owner", status=403)
    before = expect(live.request(live.path("me/access"), actor="admin"), 200)["capabilities"]
    act(live, "ownership-transfers", transfer, "accept")
    assert member(live, successor["object_id"])["owner"] is True
    assert member(live, owner["object_id"])["owner"] is False
    assert expect(live.request(live.path("me/access"), actor="admin"), 200)["capabilities"] == before
    # Return custody through the same governed mechanism so unrelated fixture tests remain independent.
    back = create(
        live,
        "ownership-transfers",
        {"membership_id": owner["object_id"], "expected_membership_revision": owner["revision_id"]},
    )
    act(live, "ownership-transfers", back, "accept", actor="owner")


def test_preferences_closed_identity_preserving_and_stale_write(live):
    identity, _ = join(live)
    old = expect(request_as(live, identity, "/auth/preferences"), 200)
    data = {
        "expected_revision": old["revision_id"],
        "display_name": "Preferred name",
        "language": "en",
        "timezone": "Asia/Kolkata",
        "reduced_motion": True,
    }
    expect(request_as(live, identity, "/auth/preferences", "PUT", {**data, "identity_id": str(uuid4())}), 422)
    expect(request_as(live, identity, "/auth/preferences", "PUT", {**data, "timezone": "No/SuchZone"}), 422)
    saved = expect(request_as(live, identity, "/auth/preferences", "PUT", data), 200)
    assert saved["display_name"] == "Preferred name" and saved["revision_id"]
    expect(request_as(live, identity, "/auth/preferences", "PUT", data), 409)
    assert expect(request_as(live, identity, "/auth/me"), 200)["identity_id"] == identity


def test_session_inventory_revoke_one_all_and_identity_isolation(live):
    auth = Auth(Settings(**live.config), Database(Settings(**live.config)))
    identity_id, _ = join(live)
    identity = auth.identity({"sub": identity_id, "auth_time": time.time()})
    cookies = [auth.session(identity).headers["set-cookie"].split(";", 1)[0] for _ in range(2)]
    sessions = expect(request_as(live, identity_id, "/auth/sessions"), 200)["items"]
    assert len(sessions) == 2 and "session_hash" not in sessions[0]
    target = sessions[0]["session_id"]
    expect(live.request("/auth/sessions/" + target + "/revoke", actor="author", method="POST"), 404)
    expect(request_as(live, identity_id, "/auth/sessions/" + target + "/revoke", "POST"), 200)
    assert len(expect(request_as(live, identity_id, "/auth/sessions"), 200)["items"]) == 1
    old_token = signed(live, identity_id)
    expect(request_as(live, identity_id, "/auth/sessions/revoke-all", "POST"), 200)
    expect(request_as(live, identity_id, "/auth/me", token=old_token), 401)
    for cookie in cookies:
        expect(live.request("/auth/me", actor=None, headers={"Cookie": cookie}), 401)
    expect(request_as(live, identity_id, "/auth/me"), 200)


def test_fifteen_minute_idle_and_csrf_revocation(live):
    passwords = json.loads((live.local / "passwords.json").read_text())
    with httpx.Client(base_url=str(live.client.base_url), trust_env=False) as client:
        expect(
            client.post(
                "/auth/development-login",
                headers={"Origin": live.config["public_origin"]},
                json={"username": "partner", "password": passwords["partner"]},
            ),
            200,
        )
        expect(
            client.post("/auth/sessions/revoke-all", headers={"Origin": live.config["public_origin"]}), 403
        )
        with live.db() as c:
            c.execute(
                "UPDATE impact.web_session SET last_seen_at=now()-interval '16 minutes' WHERE identity_id=%s",
                (live.fixture["actors"]["partner"]["identity_id"],),
            )
        expect(client.get("/auth/me"), 401)


def test_assurance_is_claimed_by_trusted_provider_not_token_issuance(live):
    settings = Settings(**{**live.config, "required_acr": "urn:impact:test:mfa"})
    auth = Auth(settings, Database(settings))
    actor = live.fixture["actors"]["admin"]["identity_id"]
    assert not auth.identity({"sub": actor, "auth_time": time.time()}).assurance_verified
    assert auth.identity(
        {"sub": actor, "auth_time": time.time(), "acr": "urn:impact:test:mfa", "amr": ["pwd", "otp"]}
    ).assurance_verified
    assert not auth.identity(
        {"sub": actor, "auth_time": time.time(), "acr": "wrong", "amr": ["mfa"]}
    ).assurance_verified
    # Authority is enforced centrally for every operation that demands freshness.
    from impact_api.store import authorize
    from impact_api.domain import DomainError

    with pytest.raises(DomainError, match="request") as exc:
        authorize(
            None,
            SimpleNamespace(
                identity=SimpleNamespace(
                    assurance_verified=False,
                    auth_time=auth.identity({"sub": actor, "auth_time": time.time()}).auth_time,
                ),
                grants=[{"capability": "roles.manage", "purpose": None, "scope_type": "TENANT"}],
            ),
            "create_role_template",
        )
    assert exc.value.reason == "MFA_ASSURANCE_REQUIRED"
