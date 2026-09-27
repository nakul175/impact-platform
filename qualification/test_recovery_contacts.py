"""Recovery enrolment is independently reviewed evidence, not tenant access."""

import time
from uuid import uuid4
import pytest
import psycopg
from jsonschema import Draft202012Validator, FormatChecker
from test_administration import command, expect, expiry, signed, provision_identity, request_as
from test_tenant_lifecycle import request_tenant, action as tenant_action, directory as tenants
from impact_api.recovery_contracts import DIRECTORY, RECEIPT

BASE = "/v1/platform/recovery-contacts"


def preparing(live):
    tenant = expect(request_tenant(live)[0], 200)
    return tenant_action(live, tenant, "accept-owner", "author")


def listing(live, actor="author"):
    result = expect(live.request(BASE, actor=actor), 200)
    Draft202012Validator(DIRECTORY, format_checker=FormatChecker()).validate(result)
    cursor = result["next_cursor"]
    while cursor:
        page = expect(live.request(BASE + "?cursor=" + cursor, actor=actor), 200)
        Draft202012Validator(DIRECTORY, format_checker=FormatChecker()).validate(page)
        result["items"].extend(page["items"])
        cursor = page["next_cursor"]
    return result


def nominate(live, tenant=None, status=200, **changes):
    tenant = tenant or preparing(live)
    path = "/v1/platform/tenants/" + tenant["tenant_id"] + "/recovery-contacts"
    body = command(
        {
            "nominee_identity_id": live.fixture["actors"]["partner"]["identity_id"],
            "expected_contact_revision": tenant["recovery_contact"]["revision_id"],
            "expires_at": expiry(60),
            "reason": "Recovery contact test",
            **changes,
        },
        tenant["revision_id"],
    )
    result = expect(live.request(path, method="POST", body=body), status)
    if status == 200:
        Draft202012Validator(RECEIPT, format_checker=FormatChecker()).validate(result)
    return result, tenant, path, body


def action(live, row, name, actor="partner", status=200, body=None):
    return expect(
        live.request(
            BASE + "/" + row["contact_id"] + "/actions/" + name,
            actor=actor,
            method="POST",
            body=body or command({"reason": "Recovery qualification"}, row["revision_id"]),
        ),
        status,
    )


def approved(live):
    row, tenant, _, _ = nominate(live)
    verified = action(live, row, "verify")
    return action(live, verified, "approve", "admin"), tenant


def fresh_tenant(live, tenant):
    page = tenants(live)
    while True:
        for row in page["items"]:
            if row["tenant_id"] == tenant["tenant_id"]:
                return row
        assert page["next_cursor"], "Managed tenant missing"
        page = expect(live.request("/v1/platform/tenants?cursor=" + page["next_cursor"], actor="admin"), 200)


def test_verified_contact_is_required_before_activation_and_grants_no_access(live):
    row, tenant, _, _ = nominate(live)
    tenant_action(live, tenant, "activate", status=403)
    action(live, row, "approve", "admin", status=409)
    verified = action(live, row, "verify")
    assert not verified["verification"]["eligible"]
    tenant_action(live, tenant, "activate", status=403)
    result = action(live, verified, "approve", "admin")
    assert result["verification"]["eligible"]
    Draft202012Validator(RECEIPT, format_checker=FormatChecker()).validate(result)
    activated = tenant_action(live, tenant, "activate")
    assert activated["readiness"]["recovery_contact_verified"]
    expect(live.request(live.path("me/access", tenant=tenant["tenant_id"]), actor="partner"), 404)
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
            (tenant["tenant_id"], row["nominee_identity_id"]),
        ).fetchone()
        assert not c.execute(
            "SELECT 1 FROM impact.grant_current WHERE tenant_id=%s", (tenant["tenant_id"],)
        ).fetchone()


def test_owner_only_nomination_and_private_identity_bound_inbox(live):
    row, _, path, body = nominate(live)
    for actor in ["admin", "owner", "reviewer", "other_tenant"]:
        expect(live.request(path, actor=actor, method="POST", body=body), 404)
        action(live, row, "verify", actor, status=404)
    assert row["contact_id"] in {r["contact_id"] for r in listing(live, "partner")["items"]}
    assert row["contact_id"] not in {r["contact_id"] for r in listing(live, "other_tenant")["items"]}


@pytest.mark.parametrize(
    "changes,status",
    [
        ({"expires_at": expiry(100)}, 422),
        ({"expires_at": expiry(-1)}, 422),
        ({"nominee_identity_id": str(uuid4())}, 404),
        ({"extra": "forbidden"}, 422),
        ({"expected_contact_revision": str(uuid4())}, 409),
    ],
)
def test_nomination_contract_and_expiry_limits(live, changes, status):
    nominate(live, status=status, **changes)


def test_owner_alias_cannot_be_recovery_contact(live):
    alias, _ = provision_identity(live, live.fixture["actors"]["author"]["natural_identity_id"])
    nominate(live, status=403, nominee_identity_id=alias)


def test_reviewer_must_be_a_different_natural_person(live):
    row, _, _, _ = nominate(live, nominee_identity_id=live.fixture["actors"]["admin"]["identity_id"])
    row = action(live, row, "verify", "admin")
    action(live, row, "approve", "admin", status=403)
    alias, _ = provision_identity(live, live.fixture["actors"]["admin"]["natural_identity_id"])
    with live.db() as c:
        c.execute(
            "INSERT INTO impact.platform_operator VALUES(%s,true,now()+interval '1 day','Synthetic alias test')",
            (alias,),
        )
    expect(
        request_as(
            live,
            alias,
            BASE + "/" + row["contact_id"] + "/actions/approve",
            method="POST",
            body=command({"reason": "Alias must not approve"}, row["revision_id"]),
        ),
        403,
    )
    action(live, row, "approve", "owner")


def test_fresh_assurance_and_exact_retry(live):
    row, _, path, body = nominate(live)
    assert expect(live.request(path, method="POST", body=body), 200) == row
    expect(
        live.request(path, method="POST", body={**body, "data": {**body["data"], "reason": "Changed"}}), 409
    )
    token = signed(live, row["nominee_identity_id"], auth_time=time.time() - 600)
    expect(
        request_as(
            live,
            row["nominee_identity_id"],
            BASE + "/" + row["contact_id"] + "/actions/verify",
            method="POST",
            body=command({"reason": "Stale"}, row["revision_id"]),
            token=token,
        ),
        403,
    )
    verify = command({"reason": "Exact consent"}, row["revision_id"])
    verified = action(live, row, "verify", body=verify)
    assert action(live, row, "verify", body=verify) == verified
    action(live, row, "verify", status=409)


def test_replacement_preserves_old_contact_until_atomic_approval(live):
    old, tenant = approved(live)
    tenant = fresh_tenant(live, tenant)
    new, _, _, _ = nominate(
        live, tenant, nominee_identity_id=live.fixture["actors"]["reviewer"]["identity_id"]
    )
    assert new["replaces_contact_id"] == old["contact_id"]
    assert fresh_tenant(live, tenant)["recovery_contact"]["contact_id"] == old["contact_id"]
    nominate(live, tenant, status=409)
    verified = action(live, new, "verify", "reviewer")
    result = action(live, verified, "approve", "admin")
    assert fresh_tenant(live, tenant)["recovery_contact"]["contact_id"] == result["contact_id"]
    old_record = next(r for r in listing(live, "partner")["items"] if r["contact_id"] == old["contact_id"])
    assert old_record["state"] == "Replaced" and not old_record["verification"]["eligible"]
    assert result["contact_id"] not in {r["contact_id"] for r in listing(live, "partner")["items"]}
    action(live, old, "revoke", status=409)


@pytest.mark.parametrize("name,actor", [("decline", "partner"), ("cancel", "author"), ("reject", "admin")])
def test_terminal_proposals_do_not_displace_existing_contact(live, name, actor):
    old, tenant = approved(live)
    tenant = fresh_tenant(live, tenant)
    row, _, _, _ = nominate(live, tenant)
    action(live, row, name, actor)
    assert fresh_tenant(live, tenant)["recovery_contact"]["contact_id"] == old["contact_id"]
    assert nominate(live, tenant)[0]["state"] == "Nominated"


def test_revocation_blocks_activation_without_resurrecting_on_retry(live):
    row, tenant, _, _ = nominate(live)
    row = action(live, row, "verify")
    body = command({"reason": "Approve exact record"}, row["revision_id"])
    contact = action(live, row, "approve", "admin", body=body)
    action(live, contact, "revoke")
    assert action(live, row, "approve", "admin", body=body) == contact
    assert not fresh_tenant(live, tenant)["recovery_contact"]["eligible"]
    tenant_action(live, tenant, "activate", status=403)


@pytest.mark.parametrize(
    "drift,status",
    [
        ("tenant", 409),
        ("owner", 409),
        ("expiry", 403),
        ("verification", 403),
        ("identity", 403),
        ("cutoff", 403),
    ],
)
def test_approval_rechecks_every_evidence_pin(live, drift, status):
    row, tenant, _, _ = nominate(live)
    row = action(live, row, "verify")
    with live.db() as c:
        if drift == "tenant":
            c.execute(
                "UPDATE impact.tenant_onboarding SET revision_id=%s WHERE tenant_id=%s",
                (str(uuid4()), tenant["tenant_id"]),
            )
        elif drift == "owner":
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET owner_revision=%s WHERE contact_id=%s",
                (str(uuid4()), row["contact_id"]),
            )
        elif drift == "expiry":
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET review_expires_at=now()-interval '1 second' WHERE contact_id=%s",
                (row["contact_id"],),
            )
        elif drift == "verification":
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET verified_at=now()-interval '2 days' WHERE contact_id=%s",
                (row["contact_id"],),
            )
        elif drift == "identity":
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET email_hash=%s WHERE contact_id=%s",
                (b"x" * 32, row["contact_id"]),
            )
        else:
            c.execute(
                "INSERT INTO impact.identity_security_state VALUES(%s,now()-interval '1 day') ON CONFLICT DO NOTHING",
                (row["nominee_identity_id"],),
            )
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET verified_auth_time=now()-interval '2 days' WHERE contact_id=%s",
                (row["contact_id"],),
            )
    action(live, row, "approve", "admin", status=status)
    assert not fresh_tenant(live, tenant)["recovery_contact"]["eligible"]


def test_expired_contact_blocks_reactivation_without_suspending_active_business(live):
    row, tenant = approved(live)
    tenant = tenant_action(live, tenant, "activate")
    with live.db() as c:
        c.execute(
            "UPDATE impact.tenant_recovery_contact SET expires_at=now()-interval '1 second' WHERE contact_id=%s",
            (row["contact_id"],),
        )
    assert fresh_tenant(live, tenant)["recovery_contact"]["reason"] == "EXPIRED"
    expect(live.request(live.path("me/access", tenant=tenant["tenant_id"])), 200)
    suspended = tenant_action(live, tenant, "suspend", "admin")
    tenant_action(live, suspended, "reactivate", status=403)
    # Fresh owner authentication can repair recovery readiness while suspended.
    current = fresh_tenant(live, suspended)
    nomination = expect(
        request_as(
            live,
            live.fixture["actors"]["author"]["identity_id"],
            "/v1/platform/tenants/" + tenant["tenant_id"] + "/recovery-contacts",
            method="POST",
            body=command(
                {
                    "nominee_identity_id": row["nominee_identity_id"],
                    "expected_contact_revision": current["recovery_contact"]["revision_id"],
                    "expires_at": expiry(30),
                    "reason": "Renew expired contact during suspension",
                },
                current["revision_id"],
            ),
        ),
        200,
    )
    nomination = action(live, nomination, "verify")
    action(live, nomination, "approve", "admin")
    assert tenant_action(live, suspended, "reactivate")["state"] == "Active"


def test_changed_current_contact_invalidates_pending_replacement(live):
    old, tenant = approved(live)
    row, _, _, _ = nominate(live, fresh_tenant(live, tenant))
    row = action(live, row, "verify")
    action(live, old, "revoke")
    action(live, row, "approve", "admin", status=409)


def test_runtime_roles_cannot_read_contact_evidence_or_rewrite_audit(live):
    for role, sql in [
        ("impact_app", "SELECT * FROM impact.tenant_recovery_contact"),
        ("impact_identity", "SELECT * FROM impact.tenant_recovery_contact"),
        ("impact_app", "SELECT impact.lock_recovery_identities('{}'::uuid[])"),
        ("impact_platform", "DELETE FROM impact.tenant_recovery_contact"),
        ("impact_platform", "UPDATE impact.platform_event SET reason='rewrite'"),
    ]:
        with live.db() as c:
            c.execute("SET LOCAL ROLE " + role)
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(sql)


def test_account_revocation_invalidates_contact_and_fresh_renewal_restores_readiness(live):
    person, _ = provision_identity(live)
    row, tenant, _, _ = nominate(live, nominee_identity_id=person)

    def person_action(record, name):
        return expect(
            request_as(
                live,
                person,
                BASE + "/" + record["contact_id"] + "/actions/" + name,
                method="POST",
                body=command({"reason": "Fresh contact consent"}, record["revision_id"]),
            ),
            200,
        )

    row = person_action(row, "verify")
    old = action(live, row, "approve", "admin")
    expect(request_as(live, person, "/auth/sessions/revoke-all", method="POST"), 200)
    current = fresh_tenant(live, tenant)
    assert current["recovery_contact"]["reason"] == "AUTHENTICATION_REVOKED"
    tenant_action(live, tenant, "activate", status=403)
    renewal, _, _, _ = nominate(live, current, nominee_identity_id=person)
    renewed = action(live, person_action(renewal, "verify"), "approve", "admin")
    assert renewed["verification"]["eligible"] and renewed["replaces_contact_id"] == old["contact_id"]
    tenant_action(live, tenant, "activate")


@pytest.mark.parametrize("drift,reason", [("email", "IDENTITY_CHANGED"), ("owner", "OWNER_CHANGED")])
def test_active_contact_eligibility_rechecks_identity_and_custody(live, drift, reason):
    row, tenant = approved(live)
    with live.db() as c:
        if drift == "email":
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET email_hash=%s WHERE contact_id=%s",
                (b"z" * 32, row["contact_id"]),
            )
        else:
            c.execute(
                "UPDATE impact.tenant_onboarding SET owner_identity_id=%s WHERE tenant_id=%s",
                (live.fixture["actors"]["reviewer"]["identity_id"], tenant["tenant_id"]),
            )
    assert fresh_tenant(live, tenant)["recovery_contact"]["reason"] == reason
    tenant_action(live, tenant, "activate", status=403)


def test_replacement_failure_restores_old_contact_and_all_evidence(live):
    old, tenant = approved(live)
    row, _, _, _ = nominate(live, fresh_tenant(live, tenant))
    row = action(live, row, "verify")
    body = command({"reason": "Atomic replacement"}, row["revision_id"])
    with live.db() as c:
        c.execute(
            "CREATE FUNCTION impact.test_recovery_rollback() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.action='recovery-approve' THEN RAISE EXCEPTION 'qualification injected failure'; END IF; RETURN NEW; END $$"
        )
        c.execute(
            "CREATE TRIGGER test_recovery_rollback BEFORE INSERT ON impact.platform_event FOR EACH ROW EXECUTE FUNCTION impact.test_recovery_rollback()"
        )
    try:
        action(live, row, "approve", "admin", status=503, body=body)
        current = fresh_tenant(live, tenant)["recovery_contact"]
        assert current["eligible"] and current["revision_id"] == old["revision_id"]
        with live.db() as c:
            assert not c.execute(
                "SELECT 1 FROM impact.platform_receipt WHERE operation_id=%s", (body["operation_id"],)
            ).fetchone()
            assert not c.execute(
                "SELECT 1 FROM impact.platform_event WHERE tenant_id=%s AND action='recovery-replaced'",
                (tenant["tenant_id"],),
            ).fetchone()
    finally:
        with live.db() as c:
            c.execute("DROP TRIGGER test_recovery_rollback ON impact.platform_event")
            c.execute("DROP FUNCTION impact.test_recovery_rollback()")
    assert action(live, row, "approve", "admin", body=body)["state"] == "Active"


def test_revoked_operator_loses_access_to_approval_receipt(live):
    row, _, _, _ = nominate(live)
    row = action(live, row, "verify")
    body = command({"reason": "Approved"}, row["revision_id"])
    action(live, row, "approve", "admin", body=body)
    identity = live.fixture["actors"]["admin"]["identity_id"]
    try:
        with live.db() as c:
            c.execute("UPDATE impact.platform_operator SET active=false WHERE identity_id=%s", (identity,))
        action(live, row, "approve", "admin", status=404, body=body)
    finally:
        with live.db() as c:
            c.execute("UPDATE impact.platform_operator SET active=true WHERE identity_id=%s", (identity,))
