"""Reviewed renewal of delegated authority through live HTTP and actual database roles."""

import time
from datetime import datetime
from uuid import uuid4
import psycopg
import pytest
from jsonschema import Draft202012Validator, FormatChecker
from test_access_bootstrap import applied as bootstrapped
from test_administration import command, expect, expiry, provision_identity, request_as, signed
from test_recovery_contacts import action as recovery_action, fresh_tenant
from test_tenant_lifecycle import action as tenant_action, recovery_contact as enrol_recovery_contact
from impact_api.renewal_contracts import AUTHORITY, DIRECTORY, RECEIPT

BASE = "/v1/platform/authority-renewals"


def valid(schema, value):
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    return value


def bootstrapped_tenant(live):
    """Active managed tenant with applied initial access: owner=author, second=reviewer, operator=admin."""
    access, tenant = bootstrapped(live)
    return tenant, access


def authority(live, tenant, actor="author", status=200):
    result = expect(
        live.request("/v1/platform/tenants/" + tenant["tenant_id"] + "/authority", actor=actor), status
    )
    return valid(AUTHORITY, result) if status == 200 else result


def directory(live, actor="author"):
    return valid(DIRECTORY, expect(live.request(BASE, actor=actor), 200))


def propose(live, tenant=None, status=200, revision=None, **changes):
    tenant = tenant or bootstrapped_tenant(live)[0]
    current = authority(live, tenant)
    body = command(
        {
            "second_identity_id": current["second_identity_id"]
            or live.fixture["actors"]["reviewer"]["identity_id"],
            "authority_hash": current["authority_hash"] or "0" * 64,
            "expires_at": expiry(60),
            "reason": "Renew bounded delegation before expiry",
            **changes,
        },
        revision or current["tenant_revision"],
    )
    path = "/v1/platform/tenants/" + tenant["tenant_id"] + "/authority-renewal"
    row = expect(live.request(path, method="POST", body=body), status)
    return (valid(RECEIPT, row) if status == 200 else row), tenant, path, body


def action(live, row, name, actor="reviewer", status=200, body=None):
    return expect(
        live.request(
            BASE + "/" + row["request_id"] + "/actions/" + name,
            actor=actor,
            method="POST",
            body=body or command({"reason": "Reviewed authority renewal"}, row["revision_id"]),
        ),
        status,
    )


def snapshot(live, tenant_id):
    """Every expiry, revision and marker a renewal may touch."""
    with live.db() as c:
        return {
            "authority": {
                str(r["authority_id"]): r["expires_at"]
                for r in c.execute(
                    "SELECT authority_id,expires_at FROM impact.grant_authority WHERE tenant_id=%s",
                    (tenant_id,),
                )
            },
            "grants": {
                str(r["object_id"]): (r["expires_at"], r["lifecycle_state"], r["revision_number"])
                for r in c.execute(
                    "SELECT g.object_id,g.expires_at,r.lifecycle_state,v.revision_number FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE g.tenant_id=%s",
                    (tenant_id,),
                )
            },
            "assignments": {
                str(r["assignment_id"]): r["expires_at"]
                for r in c.execute(
                    "SELECT assignment_id,expires_at FROM impact.member_role_assignment WHERE tenant_id=%s",
                    (tenant_id,),
                )
            },
            "memberships": {
                str(r["object_id"]): r["expires_at"]
                for r in c.execute(
                    "SELECT object_id,expires_at FROM impact.membership_current WHERE tenant_id=%s",
                    (tenant_id,),
                )
            },
            "epochs": {
                str(r["principal_id"]): r["subject_epoch"]
                for r in c.execute(
                    "SELECT principal_id,subject_epoch FROM impact.tenant_principal WHERE tenant_id=%s",
                    (tenant_id,),
                )
            },
            "policy_epoch": c.execute(
                "SELECT policy_epoch FROM impact.tenant_root WHERE tenant_id=%s", (tenant_id,)
            ).fetchone()["policy_epoch"],
            "marker": [
                str(r["request_id"])
                for r in c.execute(
                    "SELECT request_id FROM impact.tenant_access_bootstrap_applied WHERE tenant_id=%s",
                    (tenant_id,),
                )
            ],
        }


def principal_of(live, tenant_id, actor):
    with live.db() as c:
        return str(
            c.execute(
                "SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
                (tenant_id, live.fixture["actors"][actor]["identity_id"]),
            ).fetchone()["principal_id"]
        )


def test_reviewed_renewal_extends_every_pinned_ceiling_and_keeps_readiness(live):
    tenant, access = bootstrapped_tenant(live)
    tenant_id = tenant["tenant_id"]
    current = authority(live, tenant)
    assert current["renewable"] and current["reason_unavailable"] is None
    assert current["bootstrap_request_id"] == access["request_id"]
    assert current["second_identity_id"] == live.fixture["actors"]["reviewer"]["identity_id"]
    assert [p["identity_id"] for p in current["principals"]] == [
        live.fixture["actors"]["author"]["identity_id"],
        current["second_identity_id"],
    ]
    row, _, _, _ = propose(live, tenant)
    assert row["state"] == "Requested" and row["manifest"]["principals"] == current["principals"]
    assert row["authority_hash"] == current["authority_hash"]
    assert row["previous_expires_at"] == current["earliest_expires_at"]
    assert authority(live, tenant)["reason_unavailable"] == "RENEWAL_PENDING"
    before = snapshot(live, tenant_id)
    action(live, row, "approve", "admin", status=409)
    accepted = action(live, row, "accept")
    assert accepted["state"] == "Accepted" and accepted["accepted_at"] and not accepted["applied_at"]
    assert snapshot(live, tenant_id) == before
    approved = valid(RECEIPT, action(live, accepted, "approve", "admin"))
    assert approved["state"] == "Applied" and approved["applied_at"]
    assert approved["approved_by"] == live.fixture["actors"]["admin"]["identity_id"]
    renewed = datetime.fromisoformat(approved["expires_at"])
    after = snapshot(live, tenant_id)
    assert set(after["authority"]) == set(before["authority"]) == set(row["manifest"]["authority_ids"])
    assert all(value < renewed for value in before["authority"].values())
    assert all(value == renewed for value in after["authority"].values())
    pinned = {g for p in row["manifest"]["principals"] for g in p["grant_ids"]}
    assert len(pinned) == 2 * len(access["manifest"]["roles"]["TENANT_ADMIN"])
    assert set(after["grants"]) == set(before["grants"])
    for grant_id, (expires_at, state, revision_number) in after["grants"].items():
        old = before["grants"][grant_id]
        assert grant_id in pinned and state == "Active" and old[1] == "Active"
        assert expires_at == renewed and old[0] < renewed and revision_number == old[2] + 1
    assignments = {a for p in row["manifest"]["principals"] for a in p["assignment_ids"]}
    assert assignments and set(after["assignments"]) == set(before["assignments"]) == assignments
    assert all(value == renewed for value in after["assignments"].values())
    owner_member, second_member = (p["membership_id"] for p in row["manifest"]["principals"])
    assert after["memberships"][owner_member] is None is before["memberships"][owner_member]
    assert before["memberships"][second_member] < renewed == after["memberships"][second_member]
    assert after["marker"] == before["marker"] == [access["request_id"]]
    assert after["policy_epoch"] == before["policy_epoch"] + 1
    for actor in ["author", "reviewer"]:
        principal = principal_of(live, tenant_id, actor)
        assert after["epochs"][principal] == before["epochs"][principal] + 1
    fresh = fresh_tenant(live, tenant)
    assert all(fresh["readiness"].values()) and fresh["revision_id"] == tenant["revision_id"]
    access_view = expect(live.request(live.path("me/access", tenant=tenant_id), actor="reviewer"), 200)
    assert "roles.manage" in access_view["capabilities"]
    later = authority(live, tenant)
    assert later["renewable"] and later["earliest_expires_at"] == approved["expires_at"]
    assert later["authority_hash"] != current["authority_hash"]
    listed = next(r for r in directory(live)["items"] if r["request_id"] == row["request_id"])
    assert listed["state"] == "Applied" and listed["approved_by"] == approved["approved_by"]
    with live.db() as c:
        events = c.execute(
            "SELECT action FROM impact.platform_event WHERE tenant_id=%s AND action LIKE 'authority-renewal-%%' ORDER BY created_at",
            (tenant_id,),
        ).fetchall()
        assert [e["action"] for e in events] == [
            "authority-renewal-request",
            "authority-renewal-accept",
            "authority-renewal-approve",
        ]


def test_request_is_owner_only_reads_are_owner_or_operator_and_fields_are_closed(live):
    _, tenant, path, body = propose(live)
    for actor in ["admin", "reviewer", "owner", "other_tenant", "partner"]:
        expect(live.request(path, actor=actor, method="POST", body=body), 404)
    expect(live.request(path, method="POST", body={**body, "capabilities": ["*"]}), 422)
    expect(live.request(path, method="POST", body={**body, "data": {**body["data"], "roles": []}}), 422)
    authority(live, tenant, "admin")
    authority(live, tenant, "owner")
    for actor in ["reviewer", "other_tenant", "partner"]:
        authority(live, tenant, actor, 404)
    # Legacy fixture tenants are not managed tenants and expose no delegated authority.
    authority(live, {"tenant_id": live.fixture["tenant_a"]}, "admin", 404)


def test_second_administrator_must_hold_authority_and_be_a_distinct_person(live):
    tenant, _ = bootstrapped_tenant(live)
    row, _, _, _ = propose(
        live, tenant, status=403, second_identity_id=live.fixture["actors"]["partner"]["identity_id"]
    )
    assert row["reason_code"] == "SECOND_ADMIN_UNAVAILABLE"
    alias, _ = provision_identity(live, live.fixture["actors"]["author"]["natural_identity_id"])
    row, _, _, _ = propose(live, tenant, status=403, second_identity_id=alias)
    assert row["reason_code"] == "INDEPENDENCE_REQUIRED"
    propose(live, tenant, status=404, second_identity_id=str(uuid4()))
    row, _, _, _ = propose(live, tenant, status=409, authority_hash="0" * 64)
    assert row["reason_code"] == "AUTHORITY_CHANGED"
    propose(live, tenant, status=409, revision=str(uuid4()))
    assert propose(live, tenant)[0]["state"] == "Requested"


@pytest.mark.parametrize(
    "value",
    [expiry(29), expiry(30), expiry(-1), expiry(100), "not-a-date", "2026-12-31T00:00:00"],
)
def test_expiry_must_exceed_current_ceiling_within_ninety_days(live, value):
    row, _, _, _ = propose(live, status=422, expires_at=value)
    assert row.get("reason_code") in {"GRANT_EXPIRY_BOUNDS", None}


def test_removed_ceilings_invalidate_the_proposal_and_are_never_resurrected(live):
    tenant, _ = bootstrapped_tenant(live)
    tenant_id = tenant["tenant_id"]
    second = principal_of(live, tenant_id, "reviewer")
    with live.db() as c:
        removed = str(
            c.execute(
                "DELETE FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s AND capability='roles.manage' RETURNING authority_id",
                (tenant_id, second),
            ).fetchone()["authority_id"]
        )
        revoked = str(
            c.execute(
                "SELECT object_id FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability='roles.manage'",
                (tenant_id, second),
            ).fetchone()["object_id"]
        )
        c.execute(
            "UPDATE impact.object_registry SET lifecycle_state='Revoked' WHERE tenant_id=%s AND object_id=%s",
            (tenant_id, revoked),
        )
    row, _, _, _ = propose(live, tenant)
    owner_entry, second_entry = row["manifest"]["principals"]
    assert removed not in row["manifest"]["authority_ids"]
    assert (
        "roles.manage" in owner_entry["capabilities"] and "roles.manage" not in second_entry["capabilities"]
    )
    assert revoked not in owner_entry["grant_ids"] + second_entry["grant_ids"]
    assert len(second_entry["grant_ids"]) == len(owner_entry["grant_ids"]) - 1
    row = action(live, row, "accept")
    before = snapshot(live, tenant_id)
    with live.db() as c:
        c.execute(
            "DELETE FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s AND capability='groups.manage'",
            (tenant_id, second),
        )
    body = command({"reason": "Approve stale package"}, row["revision_id"])
    assert action(live, row, "approve", "admin", status=409, body=body)["reason_code"] == "AUTHORITY_CHANGED"
    after = snapshot(live, tenant_id)
    before["authority"].pop(next(k for k in before["authority"] if k not in after["authority"]))
    assert after == before
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.platform_receipt WHERE operation_id=%s", (body["operation_id"],)
        ).fetchone()
        assert (
            c.execute(
                "SELECT state,approved_by FROM impact.tenant_authority_renewal WHERE request_id=%s",
                (row["request_id"],),
            ).fetchone()["state"]
            == "Accepted"
        )
    action(live, row, "cancel", "author")
    fresh, _, _, _ = propose(live, tenant)
    assert set(fresh["manifest"]["authority_ids"]) == set(after["authority"])
    approved = action(live, action(live, fresh, "accept"), "approve", "admin")
    renewed = datetime.fromisoformat(approved["expires_at"])
    final = snapshot(live, tenant_id)
    assert set(final["authority"]) == set(after["authority"]) and len(final["authority"]) == len(
        before["authority"]
    )
    assert all(value == renewed for value in final["authority"].values())
    assert final["grants"][revoked] == before["grants"][revoked] and final["grants"][revoked][1] == "Revoked"
    assert all(v[0] == renewed for k, v in final["grants"].items() if k != revoked)


@pytest.mark.parametrize(
    "drift,status,reason",
    [
        ("tenant", 409, "RENEWAL_CONTEXT_CHANGED"),
        ("owner", 409, "RENEWAL_CONTEXT_CHANGED"),
        ("expired", 403, "RENEWAL_EXPIRED"),
        ("hash", 409, "AUTHORITY_CHANGED"),
        ("qualification", 403, "TENANT_NOT_READY"),
        ("owner_cutoff", 403, "REAUTHENTICATION_REQUIRED"),
        ("second_cutoff", 403, "REAUTHENTICATION_REQUIRED"),
    ],
)
def test_approval_rechecks_pinned_context_and_consent(live, drift, status, reason):
    row, tenant, _, _ = propose(live)
    row = action(live, row, "accept")
    before = snapshot(live, tenant["tenant_id"])
    with live.db() as c:
        if drift == "tenant":
            c.execute(
                "UPDATE impact.tenant_onboarding SET revision_id=%s WHERE tenant_id=%s",
                (str(uuid4()), tenant["tenant_id"]),
            )
        elif drift == "owner":
            c.execute(
                "UPDATE impact.tenant_authority_renewal SET owner_revision=%s WHERE request_id=%s",
                (str(uuid4()), row["request_id"]),
            )
        elif drift == "expired":
            c.execute(
                "UPDATE impact.tenant_authority_renewal SET review_expires_at=now()-interval '1 second' WHERE request_id=%s",
                (row["request_id"],),
            )
        elif drift == "hash":
            c.execute(
                "UPDATE impact.tenant_authority_renewal SET authority_hash=%s WHERE request_id=%s",
                ("0" * 64, row["request_id"]),
            )
        elif drift == "qualification":
            c.execute(
                "UPDATE impact.tenant_onboarding SET qualification_revision=%s WHERE tenant_id=%s",
                (str(uuid4()), tenant["tenant_id"]),
            )
        else:
            key = "owner_auth_time" if drift == "owner_cutoff" else "second_auth_time"
            person = row["owner_identity_id"] if drift == "owner_cutoff" else row["second_identity_id"]
            c.execute(
                "INSERT INTO impact.identity_security_state VALUES(%s,now()-interval '1 day') ON CONFLICT(identity_id) DO NOTHING",
                (person,),
            )
            c.execute(
                "UPDATE impact.tenant_authority_renewal SET "
                + key
                + "=now()-interval '2 days' WHERE request_id=%s",
                (row["request_id"],),
            )
    assert action(live, row, "approve", "admin", status=status)["reason_code"] == reason
    assert snapshot(live, tenant["tenant_id"]) == before


def test_operator_independence_and_operator_only_review(live):
    row, tenant, _, _ = propose(live)
    for actor, name in [
        ("author", "approve"),
        ("reviewer", "approve"),
        ("reviewer", "reject"),
        ("author", "reject"),
    ]:
        assert action(live, row, name, actor, status=403)["reason_code"] == "PLATFORM_OPERATOR_REQUIRED"
    row = action(live, row, "accept")
    body = command({"reason": "Alias must not approve"}, row["revision_id"])
    for actor in ["author", "reviewer"]:
        alias, _ = provision_identity(live, live.fixture["actors"][actor]["natural_identity_id"])
        with live.db() as c:
            c.execute(
                "INSERT INTO impact.platform_operator VALUES(%s,true,now()+interval '1 day','Synthetic alias test')",
                (alias,),
            )
        response = expect(
            request_as(live, alias, BASE + "/" + row["request_id"] + "/actions/approve", "POST", body), 403
        )
        assert response["reason_code"] == "INDEPENDENCE_REQUIRED"
    assert snapshot(live, tenant["tenant_id"])["marker"]
    assert action(live, row, "approve", "owner")["state"] == "Applied"


def test_exact_retry_operation_reuse_and_fresh_assurance(live):
    row, tenant, path, body = propose(live)
    assert expect(live.request(path, method="POST", body=body), 200) == row
    changed = expect(
        live.request(path, method="POST", body={**body, "data": {**body["data"], "reason": "Different"}}), 409
    )
    assert changed["reason_code"] == "OPERATION_REUSE"
    token = signed(live, row["second_identity_id"], auth_time=time.time() - 600)
    stale = expect(
        request_as(
            live,
            row["second_identity_id"],
            BASE + "/" + row["request_id"] + "/actions/accept",
            "POST",
            command({"reason": "Stale assurance"}, row["revision_id"]),
            token=token,
        ),
        403,
    )
    assert stale["reason_code"] == "FRESH_MFA_REQUIRED"
    accept = command({"reason": "Exact consent"}, row["revision_id"])
    accepted = action(live, row, "accept", body=accept)
    assert action(live, row, "accept", body=accept) == accepted
    action(live, row, "accept", status=409)
    assert action(live, accepted, "accept", status=409)["reason_code"] == "INVALID_RENEWAL_TRANSITION"
    approve = command({"reason": "Final review"}, accepted["revision_id"])
    approved = action(live, accepted, "approve", "admin", body=approve)
    with live.db() as c:
        c.execute(
            "UPDATE impact.object_registry SET lifecycle_state='Revoked' WHERE tenant_id=%s AND object_type='Grant'",
            (tenant["tenant_id"],),
        )
    assert action(live, accepted, "approve", "admin", body=approve) == approved
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_type='Grant' AND lifecycle_state='Active'",
            (tenant["tenant_id"],),
        ).fetchone()
    # A replay never re-extends: the renewed ceiling stays exactly as approved once.
    assert all(
        v == datetime.fromisoformat(approved["expires_at"])
        for v in snapshot(live, tenant["tenant_id"])["authority"].values()
    )


def test_one_live_renewal_per_tenant_until_withdrawn_or_rejected(live):
    row, tenant, _, _ = propose(live)
    assert propose(live, tenant, status=409)[0]["reason_code"] == "RENEWAL_PENDING"
    cancelled = action(live, row, "cancel", "author")
    assert cancelled["state"] == "Cancelled"
    action(live, row, "cancel", "author", status=409)
    assert (
        action(live, cancelled, "cancel", "author", status=409)["reason_code"] == "INVALID_RENEWAL_TRANSITION"
    )
    row, _, _, _ = propose(live, tenant)
    row = action(live, row, "accept")
    assert propose(live, tenant, status=409)[0]["reason_code"] == "RENEWAL_PENDING"
    assert action(live, row, "reject", "admin")["state"] == "Rejected"
    assert authority(live, tenant)["renewable"]
    assert propose(live, tenant)[0]["state"] == "Requested"
    assert snapshot(live, tenant["tenant_id"])["authority"]


def test_suspension_and_missing_recovery_contact_block_renewal(live):
    row, tenant, _, _ = propose(live)
    row = action(live, row, "accept")
    contact = fresh_tenant(live, tenant)["recovery_contact"]
    recovery_action(
        live, {"contact_id": contact["contact_id"], "revision_id": contact["revision_id"]}, "revoke"
    )
    assert action(live, row, "approve", "admin", status=403)["reason_code"] == "TENANT_NOT_READY"
    # Suspension sets every principal's auth_not_before to the suspension instant. The owner's
    # authentication is pinned before it: the suite's cached token is re-minted once it is 60 s
    # old, and an owner who authenticated after the suspension may withdraw (next test).
    authenticated_before = time.time() - 5
    suspended = tenant_action(live, fresh_tenant(live, tenant), "suspend", "admin")
    described = authority(live, suspended, "admin")
    assert not described["renewable"] and described["reason_unavailable"] == "TENANT_NOT_ACTIVE"
    assert propose(live, suspended, status=403)[0]["reason_code"] == "TENANT_NOT_ACTIVE"
    assert action(live, row, "approve", "admin", status=403)["reason_code"] == "TENANT_NOT_ACTIVE"
    stale = owner_request(live, row, "cancel", auth_time=authenticated_before)
    assert expect(stale, 403)["reason_code"] == "REAUTHENTICATION_REQUIRED"
    assert action(live, row, "reject", "admin")["state"] == "Rejected"


def owner_request(live, row, name, auth_time):
    """One renewal action by the owner (author) with an explicit authentication instant."""
    token = live.signed(live.fixture["actors"]["author"]["identity_id"], auth_time=auth_time)
    return live.request(
        BASE + "/" + row["request_id"] + "/actions/" + name,
        method="POST",
        body=command({"reason": "Withdraw the renewal proposal"}, row["revision_id"]),
        headers={"Authorization": "Bearer " + token},
    )


def test_owner_who_authenticated_after_suspension_may_withdraw_a_pending_renewal(live):
    """Withdrawal stays open while the tenant is not Active (RELEASE-0.13), after re-authentication."""
    row, tenant, _, _ = propose(live)
    row = action(live, row, "accept")
    tenant_action(live, fresh_tenant(live, tenant), "suspend", "admin")
    assert action(live, row, "approve", "admin", status=403)["reason_code"] == "TENANT_NOT_ACTIVE"
    withdrawn = expect(owner_request(live, row, "cancel", auth_time=time.time()), 200)
    assert withdrawn["state"] == "Cancelled"


def test_unready_tenant_is_not_renewable_until_recovery_evidence_is_restored(live):
    tenant, _ = bootstrapped_tenant(live)
    assert authority(live, tenant)["renewable"]
    contact = fresh_tenant(live, tenant)["recovery_contact"]
    recovery_action(
        live, {"contact_id": contact["contact_id"], "revision_id": contact["revision_id"]}, "revoke"
    )
    described = authority(live, tenant)
    assert not described["renewable"] and described["reason_unavailable"] == "TENANT_NOT_READY"
    assert described["authority_hash"] and len(described["principals"]) == 2
    assert propose(live, tenant, status=403)[0]["reason_code"] == "TENANT_NOT_READY"
    enrol_recovery_contact(live, fresh_tenant(live, tenant))
    assert authority(live, tenant)["renewable"]
    assert propose(live, tenant)[0]["state"] == "Requested"


def test_grant_revoked_through_administration_after_proposal_invalidates_it(live):
    row, tenant, _, _ = propose(live)
    row = action(live, row, "accept")
    second = row["manifest"]["principals"][1]
    with live.db() as c:
        head = str(
            c.execute(
                "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                (tenant["tenant_id"], second["grant_ids"][0]),
            ).fetchone()["head_revision"]
        )
    revoked = expect(
        request_as(
            live,
            live.fixture["actors"]["author"]["identity_id"],
            live.path("grants", second["grant_ids"][0], tenant=tenant["tenant_id"]) + "/actions/revoke",
            "POST",
            command({"reason": "Revoke one administrative grant before approval"}, head),
        ),
        200,
    )
    assert revoked["business_state"] == "Revoked"
    before = snapshot(live, tenant["tenant_id"])
    assert action(live, row, "approve", "admin", status=409)["reason_code"] == "AUTHORITY_CHANGED"
    assert snapshot(live, tenant["tenant_id"]) == before
    action(live, row, "cancel", "author")
    fresh, _, _, _ = propose(live, tenant)
    assert second["grant_ids"][0] not in fresh["manifest"]["principals"][1]["grant_ids"]
    approved = action(live, action(live, fresh, "accept"), "approve", "admin")
    after = snapshot(live, tenant["tenant_id"])
    assert after["grants"][second["grant_ids"][0]] == before["grants"][second["grant_ids"][0]]
    assert after["grants"][second["grant_ids"][0]][1] == "Revoked"
    assert all(
        v[0] == datetime.fromisoformat(approved["expires_at"])
        for k, v in after["grants"].items()
        if k != second["grant_ids"][0]
    )


@pytest.mark.parametrize("name,actor", [("cancel", "author"), ("reject", "admin")])
def test_expired_pending_proposal_is_closed_before_a_fresh_one(live, name, actor):
    row, tenant, _, _ = propose(live)
    with live.db() as c:
        c.execute(
            "UPDATE impact.tenant_authority_renewal SET review_expires_at=now()-interval '1 second' WHERE request_id=%s",
            (row["request_id"],),
        )
    assert action(live, row, "accept", status=403)["reason_code"] == "RENEWAL_EXPIRED"
    assert propose(live, tenant, status=409)[0]["reason_code"] == "RENEWAL_PENDING"
    assert authority(live, tenant)["reason_unavailable"] == "RENEWAL_PENDING"
    closed = action(live, row, name, actor)
    assert closed["state"] == ("Cancelled" if name == "cancel" else "Rejected")
    assert authority(live, tenant)["renewable"]
    assert propose(live, tenant)[0]["state"] == "Requested"


def test_private_inbox_and_cross_tenant_isolation(live):
    row, tenant, _, _ = propose(live)
    for actor in ["reviewer", "admin", "author"]:
        assert row["request_id"] in {r["request_id"] for r in directory(live, actor)["items"]}
    for actor in ["other_tenant", "partner", "enumerator"]:
        assert row["request_id"] not in {r["request_id"] for r in directory(live, actor)["items"]}
    for actor in ["author", "admin", "other_tenant", "partner"]:
        action(live, row, "accept", actor, status=404)
    # Withdrawal belongs to the current owner alone; the second administrator cannot see it as theirs.
    for actor in ["reviewer", "other_tenant", "partner"]:
        action(live, row, "cancel", actor, status=404)
        action(live, row, "reject", actor, status=404 if actor != "reviewer" else 403)
    action(live, {**row, "request_id": str(uuid4())}, "accept", status=404)
    action(live, {**row, "request_id": str(uuid4())}, "approve", "admin", status=404)


def test_runtime_roles_cannot_read_renewals_or_extend_authority(live):
    # Privilege boundaries: no HTTP role can read or reset review rows, re-date delegation
    # ceilings or role assignments directly, or run the applicator without EXECUTE.
    for role, query in [
        ("impact_app", "SELECT * FROM impact.tenant_authority_renewal"),
        ("impact_app", "INSERT INTO impact.tenant_authority_renewal DEFAULT VALUES"),
        ("impact_app", "UPDATE impact.grant_authority SET expires_at=now()"),
        ("impact_app", "UPDATE impact.member_role_assignment SET expires_at=now()"),
        ("impact_app", "SELECT * FROM impact.apply_authority_renewal(gen_random_uuid())"),
        ("impact_identity", "SELECT * FROM impact.tenant_authority_renewal"),
        ("impact_identity", "SELECT * FROM impact.apply_authority_renewal(gen_random_uuid())"),
        ("impact_platform", "DELETE FROM impact.tenant_authority_renewal"),
        ("impact_platform", "UPDATE impact.grant_authority SET expires_at=now()"),
        ("impact_platform", "INSERT INTO impact.grant_authority VALUES(NULL,NULL,NULL,NULL,NULL,NULL)"),
        ("impact_platform", "UPDATE impact.member_role_assignment SET expires_at=now()"),
        ("impact_platform", "UPDATE impact.member_role_assignment SET grant_ids='{}'"),
        ("impact_platform", "DELETE FROM impact.tenant_access_bootstrap_applied"),
    ]:
        with live.db() as c:
            c.execute("SET LOCAL ROLE " + role)
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(query)
    # Not a privilege boundary: the control-plane role may execute the applicator, which
    # itself denies (42501) any request that is unknown, not Applied or not reviewed.
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_platform")
        with pytest.raises(psycopg.errors.InsufficientPrivilege, match="authority renewal denied"):
            c.execute("SELECT * FROM impact.apply_authority_renewal(gen_random_uuid())")


def test_failure_after_extension_rolls_back_everything_and_exact_retry_succeeds(live):
    row, tenant, _, _ = propose(live)
    row = action(live, row, "accept")
    body = command({"reason": "Atomic renewal"}, row["revision_id"])
    before = snapshot(live, tenant["tenant_id"])
    with live.db() as c:
        c.execute(
            "CREATE FUNCTION impact.test_reject_renewal_event() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.action='authority-renewal-approve' THEN RAISE EXCEPTION 'qualification injected failure'; END IF; RETURN NEW; END $$"
        )
        c.execute(
            "CREATE TRIGGER test_reject_renewal_event BEFORE INSERT ON impact.platform_event FOR EACH ROW EXECUTE FUNCTION impact.test_reject_renewal_event()"
        )
    try:
        action(live, row, "approve", "admin", status=503, body=body)
        assert snapshot(live, tenant["tenant_id"]) == before
        with live.db() as c:
            assert not c.execute(
                "SELECT 1 FROM impact.platform_receipt WHERE operation_id=%s", (body["operation_id"],)
            ).fetchone()
            pending = c.execute(
                "SELECT state,approved_by,applied_at,revision_id FROM impact.tenant_authority_renewal WHERE request_id=%s",
                (row["request_id"],),
            ).fetchone()
            assert pending["state"] == "Accepted" and not pending["approved_by"] and not pending["applied_at"]
            assert str(pending["revision_id"]) == row["revision_id"]
    finally:
        with live.db() as c:
            c.execute("DROP TRIGGER test_reject_renewal_event ON impact.platform_event")
            c.execute("DROP FUNCTION impact.test_reject_renewal_event()")
    approved = action(live, row, "approve", "admin", body=body)
    assert approved["state"] == "Applied"
    after = snapshot(live, tenant["tenant_id"])
    assert after != before and all(
        v == datetime.fromisoformat(approved["expires_at"]) for v in after["authority"].values()
    )
