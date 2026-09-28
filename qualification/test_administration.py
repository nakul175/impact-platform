"""Running-API security and lifecycle tests, with isolated provisioned identity fixtures."""

import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, unquote
import jwt
import pytest
import psycopg
import httpx
from impact_api.contracts import validate
from impact_api.identity_profile import email_hash, masked_email


def command(data, revision=None, operation=None):
    return {
        "operation_id": operation or str(uuid.uuid4()),
        **({"expected_revision": revision} if revision else {}),
        "data": data,
    }


def expect(response, status):
    assert response.status_code == status, response.text
    return response.json()


def expiry(days=20):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def signed(live, identity, **overrides):
    return live.signed(identity, **overrides)


def request_as(live, identity, path, method="GET", body=None, token=None):
    return live.request(
        path,
        actor=None,
        method=method,
        body=body,
        headers={"Authorization": "Bearer " + (token or signed(live, identity))},
    )


def provision_identity(live, natural=None):
    identity = str(uuid.uuid4())
    email = "person-" + identity[:8] + "@example.test"
    with live.db() as c:
        c.execute(
            "INSERT INTO impact.auth_identity VALUES(%s,%s,%s,%s)",
            (identity, live.config["issuer"], identity, natural or str(uuid.uuid4())),
        )
        c.execute(
            "INSERT INTO impact.identity_profile VALUES(%s,%s,%s,%s,now())",
            (identity, "Test colleague", email_hash(email), masked_email(email)),
        )
    return identity, email


def listing(live, route, actor="admin"):
    return expect(live.request(live.path(route) + "?limit=100", actor=actor), 200)["items"]


def role(live, name="AUTHOR"):
    return next(r for r in listing(live, "role-templates") if r["name"] == name)


def tenant_scope(live):
    return next(s["object_id"] for s in listing(live, "access-scopes") if s["scope_type"] == "TENANT")


def invitation_token(receipt):
    return json.loads(unquote(urlparse(receipt["invitation_url"]).fragment[7:]))["token"]


def invite(live, email, role_name="AUTHOR", scope=None, actor="admin"):
    body = command(
        {
            "email": email,
            "role_template_id": role(live, role_name)["object_id"],
            "scope_ids": [scope or tenant_scope(live)],
            "expires_at": expiry(5),
            "membership_expires_at": expiry(20),
            "external": True,
            "reason": "Isolated acceptance qualification",
        }
    )
    return body, expect(
        live.request(live.path("member-invitations"), actor=actor, method="POST", body=body), 200
    )


def join(live, natural=None, scope=None):
    identity, email = provision_identity(live, natural)
    _, receipt = invite(live, email, scope=scope)
    accepted = expect(
        request_as(
            live,
            identity,
            live.path("invitation-acceptances"),
            method="POST",
            body=command({"invitation_token": invitation_token(receipt)}),
        ),
        200,
    )
    return identity, accepted


def member(live, obj):
    return next(m for m in listing(live, "membership-directory") if m["object_id"] == obj)


def action(live, route, obj, verb, revision, actor="admin"):
    return live.request(
        live.path(route, obj) + "/actions/" + verb,
        actor=actor,
        method="POST",
        body=command({"reason": "Qualification " + verb}, revision),
    )


@pytest.mark.parametrize(
    "route,schema",
    [
        ("membership-directory", "MemberDirectoryList"),
        ("member-invitations", "MemberInvitationList"),
        ("role-templates", "RoleTemplateList"),
        ("access-scopes", "AccessScopeList"),
        ("access-requests", "AccessRequestList"),
    ],
)
def test_administration_closed_list_contracts(live, route, schema):
    data = expect(live.request(live.path(route) + "?limit=3", actor="admin"), 200)
    validate(schema, data)
    assert len(data["items"]) <= 3


def test_invitation_identity_single_use_exact_retry_and_no_token_storage(live):
    identity, email = provision_identity(live)
    body, receipt = invite(live, email)
    validate("AdministrationReceipt", receipt)
    assert (
        expect(live.request(live.path("member-invitations"), actor="admin", method="POST", body=body), 200)
        == receipt
    )
    token = invitation_token(receipt)
    with live.db() as c:
        row = c.execute(
            "SELECT * FROM impact.member_invitation WHERE invitation_id=%s", (receipt["object_id"],)
        ).fetchone()
        assert bytes(row["token_hash"]) == hashlib.sha256(token.encode()).digest()
        raw = c.execute(
            "SELECT outcome::text AS text FROM impact.operation_receipt WHERE operation_id=%s",
            (body["operation_id"],),
        ).fetchone()["text"]
        assert token not in raw and email not in raw
    denied = expect(
        live.request(
            live.path("invitation-acceptances"),
            actor="partner",
            method="POST",
            body=command({"invitation_token": token}),
        ),
        410,
    )
    assert denied["code"] == "INVITATION_UNAVAILABLE"
    acceptance = command({"invitation_token": token})
    first = expect(
        request_as(live, identity, live.path("invitation-acceptances"), method="POST", body=acceptance), 200
    )
    assert (
        expect(
            request_as(live, identity, live.path("invitation-acceptances"), method="POST", body=acceptance),
            200,
        )
        == first
    )
    expect(
        request_as(
            live,
            identity,
            live.path("invitation-acceptances"),
            method="POST",
            body=command({"invitation_token": token}),
        ),
        410,
    )
    caps = expect(request_as(live, identity, live.path("me/access")), 200)["capabilities"]
    assert "observations.draft.create" in caps and "membership.revoke" not in caps
    expect(
        request_as(
            live,
            identity,
            live.path("programmes", live.fixture["programme_b"], tenant=live.fixture["tenant_b"]),
        ),
        404,
    )


def test_reissue_invalidates_old_link_and_revoke_disables_new_link(live):
    identity, email = provision_identity(live)
    _, receipt = invite(live, email)
    second = expect(
        action(live, "member-invitations", receipt["object_id"], "resend", receipt["revision_id"]), 200
    )
    assert invitation_token(receipt) != invitation_token(second)
    expect(
        request_as(
            live,
            identity,
            live.path("invitation-acceptances"),
            method="POST",
            body=command({"invitation_token": invitation_token(receipt)}),
        ),
        410,
    )
    expect(action(live, "member-invitations", second["object_id"], "revoke", second["revision_id"]), 200)
    expect(
        request_as(
            live,
            identity,
            live.path("invitation-acceptances"),
            method="POST",
            body=command({"invitation_token": invitation_token(second)}),
        ),
        410,
    )


def test_expired_invitation_and_wrong_tenant_are_denied(live):
    identity, email = provision_identity(live)
    _, receipt = invite(live, email)
    token = invitation_token(receipt)
    expect(
        request_as(
            live,
            identity,
            live.path("invitation-acceptances", tenant=live.fixture["tenant_b"]),
            method="POST",
            body=command({"invitation_token": token}),
        ),
        410,
    )
    with live.db() as c:
        c.execute(
            "UPDATE impact.member_invitation SET expires_at=now()-interval '1 second' WHERE invitation_id=%s",
            (receipt["object_id"],),
        )
    expect(
        request_as(
            live,
            identity,
            live.path("invitation-acceptances"),
            method="POST",
            body=command({"invitation_token": token}),
        ),
        410,
    )


def test_invitation_checks_current_inviter_authority(live):
    identity, email = provision_identity(live)
    _, receipt = invite(live, email)
    tenant = live.fixture["tenant_a"]
    admin = live.fixture["actors"]["admin"]
    with live.db() as c:
        rows = c.execute(
            "SELECT g.object_id FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND g.capability='member.invite' AND r.lifecycle_state='Active'",
            (tenant, admin["principal_id"]),
        ).fetchall()
        ids = [str(r["object_id"]) for r in rows]
        c.execute(
            "UPDATE impact.object_registry SET lifecycle_state='Revoked' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
            (tenant, ids),
        )
    try:
        expect(
            request_as(
                live,
                identity,
                live.path("invitation-acceptances"),
                method="POST",
                body=command({"invitation_token": invitation_token(receipt)}),
            ),
            403,
        )
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.object_registry SET lifecycle_state='Active' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
                (tenant, ids),
            )


@pytest.mark.parametrize("verb", ["suspend", "revoke"])
def test_owner_custody_cannot_be_removed(live, verb):
    owner = member(live, live.fixture["actors"]["owner"]["membership_id"])
    denied = expect(action(live, "memberships", owner["object_id"], verb, owner["revision_id"]), 403)
    assert denied["reason_code"] == "LAST_OWNER_PROTECTED"


def test_owner_grants_cannot_be_removed(live):
    owner = member(live, live.fixture["actors"]["owner"]["membership_id"])
    grant = owner["grants"][0]
    assert (
        expect(action(live, "grants", grant["object_id"], "revoke", grant["revision_id"]), 403)["reason_code"]
        == "LAST_OWNER_PROTECTED"
    )


def test_suspension_reactivation_requires_new_authentication(live):
    identity, receipt = join(live)
    old_token = signed(live, identity)
    expect(request_as(live, identity, live.path("programmes"), token=old_token), 200)
    suspended = expect(
        action(live, "memberships", receipt["object_id"], "suspend", receipt["revision_id"]), 200
    )
    expect(request_as(live, identity, live.path("programmes"), token=old_token), 404)
    expect(action(live, "memberships", receipt["object_id"], "reactivate", suspended["revision_id"]), 200)
    denied = expect(request_as(live, identity, live.path("programmes"), token=old_token), 401)
    assert denied["reason_code"] == "REAUTHENTICATION_REQUIRED"
    expect(request_as(live, identity, live.path("programmes")), 200)


def test_offboarding_revokes_grants_and_preserves_attribution(live):
    identity, receipt = join(live)
    before = member(live, receipt["object_id"])
    assert before["grants"]
    revoked = expect(action(live, "memberships", receipt["object_id"], "revoke", receipt["revision_id"]), 200)
    after = member(live, receipt["object_id"])
    assert after["state"] == "Revoked" and not after["grants"]
    expect(request_as(live, identity, live.path("programmes")), 404)
    expect(action(live, "memberships", receipt["object_id"], "reactivate", revoked["revision_id"]), 409)
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s", (receipt["object_id"],)
            ).fetchone()["n"]
            >= 2
        )


def role_request(live, recipient, actor="admin", role_name="REVIEWER", scope=None):
    data = {
        "membership_id": recipient["object_id"],
        "expected_membership_revision": recipient["revision_id"],
        "role_template_id": role(live, role_name)["object_id"],
        "scope_ids": [scope or tenant_scope(live)],
        "expires_at": expiry(10),
        "reason": "Independent entitlement review",
    }
    return expect(
        live.request(live.path("access-requests"), actor=actor, method="POST", body=command(data)), 200
    )


def test_role_change_requires_independent_approval_and_rechecks_revision(live):
    identity, receipt = join(live)
    proposal = role_request(live, receipt)
    assert (
        expect(
            action(live, "access-requests", proposal["object_id"], "approve", proposal["revision_id"]), 403
        )["reason_code"]
        == "INDEPENDENCE_REQUIRED"
    )
    decision = command({"reason": "Independently verified"}, proposal["revision_id"])
    path = live.path("access-requests", proposal["object_id"]) + "/actions/approve"
    approved = expect(live.request(path, actor="owner", method="POST", body=decision), 200)
    assert expect(live.request(path, actor="owner", method="POST", body=decision), 200) == approved
    assert (
        "workflow.approve" in expect(request_as(live, identity, live.path("me/access")), 200)["capabilities"]
    )
    assert member(live, receipt["object_id"])["revision_id"] != receipt["revision_id"]


def test_target_cannot_approve_own_access(live):
    recipient = member(live, live.fixture["actors"]["admin"]["membership_id"])
    proposal = role_request(live, recipient, actor="owner", role_name="AUTHOR")
    denied = expect(
        action(
            live, "access-requests", proposal["object_id"], "approve", proposal["revision_id"], actor="admin"
        ),
        403,
    )
    assert denied["reason_code"] == "INDEPENDENCE_REQUIRED"
    expect(
        action(
            live, "access-requests", proposal["object_id"], "reject", proposal["revision_id"], actor="owner"
        ),
        403,
    )


def test_second_login_same_natural_person_is_not_independent(live):
    identity, receipt = join(live, natural=live.fixture["actors"]["owner"]["natural_identity_id"])
    proposal = role_request(live, receipt)
    assert (
        expect(
            action(
                live,
                "access-requests",
                proposal["object_id"],
                "approve",
                proposal["revision_id"],
                actor="owner",
            ),
            403,
        )["reason_code"]
        == "INDEPENDENCE_REQUIRED"
    )


def test_changed_membership_invalidates_pending_role_request(live):
    _, receipt = join(live)
    proposal = role_request(live, receipt)
    expect(action(live, "memberships", receipt["object_id"], "suspend", receipt["revision_id"]), 200)
    expect(
        action(
            live, "access-requests", proposal["object_id"], "approve", proposal["revision_id"], actor="owner"
        ),
        409,
    )


def test_object_scoped_invitation_cannot_read_other_objects(live):
    scope = expect(
        live.request(
            live.path("access-scopes"),
            actor="admin",
            method="POST",
            body=command(
                {
                    "title": "One programme",
                    "object_ids": [live.fixture["programme_a"]],
                    "reason": "Scope qualification",
                }
            ),
        ),
        200,
    )
    identity, _ = join(live, scope=scope["object_id"])
    expect(request_as(live, identity, live.path("programmes", live.fixture["programme_a"])), 200)
    expect(request_as(live, identity, live.path("programmes", live.fixture["mutable_programme"])), 404)
    rows = expect(request_as(live, identity, live.path("programmes")), 200)["items"]
    assert [r["object_id"] for r in rows] == [live.fixture["programme_a"]]


def test_cross_tenant_scope_creation_is_atomic(live):
    body = command(
        {"title": "Denied", "object_ids": [live.fixture["programme_b"]], "reason": "Cross tenant negative"}
    )
    expect(live.request(live.path("access-scopes"), actor="admin", method="POST", body=body), 404)
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.operation_receipt WHERE operation_id=%s", (body["operation_id"],)
        ).fetchone()


def test_delegation_expiry_cannot_be_exceeded(live):
    identity, email = provision_identity(live)
    body = command(
        {
            "email": email,
            "role_template_id": role(live)["object_id"],
            "scope_ids": [tenant_scope(live)],
            "expires_at": expiry(5),
            "membership_expires_at": expiry(89),
            "external": True,
            "reason": "Bounded authority",
        }
    )
    assert (
        expect(live.request(live.path("member-invitations"), actor="admin", method="POST", body=body), 403)[
            "reason_code"
        ]
        == "DELEGATION_NOT_PERMITTED"
    )


def test_privileged_action_requires_recent_authentication(live):
    _, receipt = join(live)
    actor = live.fixture["actors"]["admin"]
    token = signed(live, actor["identity_id"], auth_time=time.time() - 301)
    response = request_as(
        live,
        actor["identity_id"],
        live.path("memberships", receipt["object_id"]) + "/actions/suspend",
        method="POST",
        body=command({"reason": "Old assurance"}, receipt["revision_id"]),
        token=token,
    )
    assert expect(response, 403)["reason_code"] == "FRESH_AUTHENTICATION_REQUIRED"


def test_recent_token_without_authentication_time_cannot_authorize_admin_changes(live):
    identity = live.fixture["actors"]["admin"]["identity_id"]
    claims = jwt.decode(signed(live, identity), options={"verify_signature": False})
    claims.pop("auth_time")
    token = jwt.encode(claims, (live.local / "private.pem").read_bytes(), algorithm="RS256")
    expect(request_as(live, identity, live.path("me/access"), token=token), 200)
    response = request_as(
        live,
        identity,
        live.path("access-scopes"),
        method="POST",
        token=token,
        body=command(
            {
                "title": "No human authentication evidence",
                "object_ids": [live.fixture["programme_a"]],
                "reason": "Negative assurance test",
            }
        ),
    )
    assert expect(response, 403)["reason_code"] == "FRESH_AUTHENTICATION_REQUIRED"


def test_non_admin_cannot_issue_invites_or_mutate_memberships(live):
    target = member(live, live.fixture["actors"]["partner"]["membership_id"])
    expect(
        action(live, "memberships", target["object_id"], "suspend", target["revision_id"], actor="author"),
        403,
    )
    expect(live.request(live.path("member-invitations"), actor="partner"), 403)


def test_generic_membership_patch_cannot_bypass_governance(live):
    target = member(live, live.fixture["actors"]["partner"]["membership_id"])
    expect(
        live.request(
            live.path("memberships", target["object_id"]),
            actor="admin",
            method="PATCH",
            body=command({"status": "Active"}, target["revision_id"]),
        ),
        404,
    )


def test_administration_create_cannot_be_called_through_patch(live):
    body = command(
        {
            "title": "Wrong method",
            "object_ids": [live.fixture["programme_a"]],
            "reason": "Negative method test",
        }
    )
    expect(
        live.request(live.path("access-scopes", str(uuid.uuid4())), actor="admin", method="PATCH", body=body),
        404,
    )
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.operation_receipt WHERE operation_id=%s", (body["operation_id"],)
        ).fetchone()


def test_invitation_cannot_grant_administrative_role(live):
    identity, email = provision_identity(live)
    body = command(
        {
            "email": email,
            "role_template_id": role(live, "TENANT_ADMIN")["object_id"],
            "scope_ids": [tenant_scope(live)],
            "expires_at": expiry(5),
            "membership_expires_at": expiry(20),
            "external": True,
            "reason": "Elevated negative",
        }
    )
    assert (
        expect(live.request(live.path("member-invitations"), actor="admin", method="POST", body=body), 403)[
            "reason_code"
        ]
        == "ADMIN_ROLE_REQUIRES_INDEPENDENT_APPROVAL"
    )


def test_unprovisioned_identity_is_not_silently_created(live):
    expect(request_as(live, str(uuid.uuid4()), "/auth/me"), 401)


def test_app_role_cannot_manufacture_delegation_or_owner_custody(live):
    for table in ["grant_authority", "tenant_custody"]:
        with live.db() as c:
            c.execute("SET LOCAL ROLE impact_app")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute("DELETE FROM impact." + table)


def test_admin_cursor_bound_to_policy_epoch_and_tenant(live):
    page = expect(live.request(live.path("membership-directory") + "?limit=1", actor="admin"), 200)
    assert page["next_cursor"]
    _, receipt = join(live)
    expect(
        live.request(live.path("membership-directory") + "?cursor=" + page["next_cursor"], actor="admin"), 400
    )
    expect(
        live.request(live.path("membership-directory", tenant=live.fixture["tenant_b"]), actor="admin"), 404
    )


def test_missing_reason_and_read_only_injection_are_rejected(live):
    target = member(live, live.fixture["actors"]["partner"]["membership_id"])
    for data in [{"reason": " "}, {"reason": "x", "status": "Active"}]:
        expect(
            live.request(
                live.path("memberships", target["object_id"]) + "/actions/suspend",
                actor="admin",
                method="POST",
                body=command(data, target["revision_id"]),
            ),
            422,
        )


def test_invitation_acceptance_immediately_updates_cookie_workspace_directory(live):
    base = str(live.client.base_url).rstrip("/")
    passwords = json.loads((live.local / "passwords.json").read_text())
    with httpx.Client(base_url=base, trust_env=False) as browser:
        expect(
            browser.post(
                "/auth/development-login",
                json={"username": "invitee", "password": passwords["invitee"]},
                headers={"Origin": base},
            ),
            200,
        )
        session = expect(browser.get("/auth/me"), 200)
        assert session["tenants"] == []
        _, invitation = invite(live, "invitee@example.test")
        expect(
            browser.post(
                live.path("invitation-acceptances"),
                json=command({"invitation_token": invitation_token(invitation)}),
                headers={"Origin": base, "X-CSRF-Token": session["csrf_token"]},
            ),
            200,
        )
        for _ in range(3):
            workspaces = expect(browser.get("/auth/me"), 200)["tenants"]
            assert [w["tenant_id"] for w in workspaces] == [live.fixture["tenant_a"]]


def test_restarting_fixture_provisioning_does_not_restore_revoked_original_grant(live, monkeypatch):
    from pathlib import Path
    from types import SimpleNamespace
    from impact_api.store import Context, write

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    from bootstrap_administration import provision

    actor = live.fixture["actors"]["admin"]
    ctx = Context(
        actor["tenant_id"],
        actor["principal_id"],
        actor["membership_id"],
        SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
        0,
        0,
        [],
    )
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (actor["tenant_id"],))
        grants = c.execute(
            "SELECT r.*,v.payload,v.revision_number FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision JOIN impact.grant_current g ON g.tenant_id=r.tenant_id AND g.object_id=r.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND g.capability='member.invite' AND g.purpose IS NULL",
            (actor["tenant_id"], actor["principal_id"]),
        ).fetchall()
        assert grants
        for grant in grants:
            write(c, ctx, "Grant", grant["payload"], "Revoked", grant, track_author=False)
        provision(c, live.fixture)
        remaining = c.execute(
            "SELECT count(*) AS n FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND g.capability='member.invite' AND g.purpose IS NULL AND r.lifecycle_state='Active'",
            (actor["tenant_id"], actor["principal_id"]),
        ).fetchone()["n"]
        assert remaining == 0
        c.rollback()  # Isolated fixture experiment: preserve the live administrator for later tests.


def test_offboarding_cancels_pending_work_and_never_automatically_resumes_it(live):
    from types import SimpleNamespace
    from impact_api.store import Context, write

    identity, receipt = join(live)
    _, email = provision_identity(live)
    _, invitation = invite(live, email)
    scope = tenant_scope(live)
    queued, running = str(uuid.uuid4()), str(uuid.uuid4())
    with live.db() as c:
        tenant = live.fixture["tenant_a"]
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        principal = c.execute(
            "SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
            (tenant, identity),
        ).fetchone()["principal_id"]
        natural = c.execute(
            "SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s", (identity,)
        ).fetchone()["natural_identity_id"]
        # Seed pending/running work; no worker execution capability is claimed by this test.
        c.execute(
            "UPDATE impact.member_invitation SET inviter_id=%s WHERE tenant_id=%s AND invitation_id=%s",
            (principal, tenant, invitation["object_id"]),
        )
        for job, state in [(queued, "Queued"), (running, "Running")]:
            c.execute(
                "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest) VALUES(%s,%s,'qualification',%s,%s,%s,'{}')",
                (tenant, job, principal, scope, state),
            )
        ctx = Context(
            tenant,
            str(principal),
            receipt["object_id"],
            SimpleNamespace(natural_identity_id=str(natural)),
            0,
            0,
            [],
        )
        schedule = write(
            c,
            ctx,
            "Schedule",
            {
                "command_type": "qualification",
                "scope_id": scope,
                "timezone": "UTC",
                "expression": "0 0 * * *",
                "missed_run_policy": "SKIP",
            },
            "Active",
        )
    suspended = expect(
        action(live, "memberships", receipt["object_id"], "suspend", receipt["revision_id"]), 200
    )
    expect(action(live, "memberships", receipt["object_id"], "reactivate", suspended["revision_id"]), 200)
    with live.db() as c:
        jobs = c.execute(
            "SELECT job_id,state,cancellation_requested_at FROM impact.job WHERE job_id=ANY(%s::uuid[])",
            ([queued, running],),
        ).fetchall()
        assert {str(j["job_id"]): j["state"] for j in jobs} == {queued: "Cancelled", running: "Running"}
        assert all(j["cancellation_requested_at"] for j in jobs)
        assert c.execute(
            "SELECT revoked_at FROM impact.member_invitation WHERE invitation_id=%s",
            (invitation["object_id"],),
        ).fetchone()["revoked_at"]
        assert (
            c.execute(
                "SELECT lifecycle_state FROM impact.object_registry WHERE object_id=%s",
                (schedule["object_id"],),
            ).fetchone()["lifecycle_state"]
            == "Paused"
        )
