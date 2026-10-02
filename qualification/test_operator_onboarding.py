"""v0.26a governed operator onboarding and sign-in accounts (gap A3), through live HTTP, the platform
role and the development account backend (the development users file; the Keycloak backend runs the
same operations in test_live_idp.py and in the CI container stack).

An operator nominates a person by e-mail; the operator creates that person's sign-in account and sees
the one-time password once; the person signs in and accepts with fresh MFA. Nobody accepts for
someone else, nobody nominates themselves, and a new operator counts at activation only because they
are a different natural person from the requester and the owner.
"""

import json
import time
from uuid import uuid4
import httpx
import pytest
from jsonschema import Draft202012Validator, FormatChecker
from test_administration import command, expect, expiry, signed
from test_tenant_lifecycle import action as tenant_action, recovery_contact, request_tenant
from test_usable_staging import onboarded
from impact_api.operator_contracts import ACCOUNT_RECEIPT, DIRECTORY, NOMINATION_RECEIPT

NOMINATIONS = "/v1/platform/operator-nominations"
ACCOUNTS = "/v1/platform/accounts"


def valid(schema, value):
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    return value


def as_person(live, subject, email, path, method="GET", body=None, **claims):
    """A request as a provisioned account: the development stand-in for the provider's token, with
    the verified e-mail claim the provider would carry."""
    token = signed(live, subject, email=email, email_verified=True, name="New Colleague", **claims)
    return live.request(
        path, actor=None, method=method, body=body, headers={"Authorization": "Bearer " + token}
    )


def nominate(live, email, actor="admin", status=200, days=30, operation=None):
    body = command(
        {"email": email, "operator_expires_at": expiry(days), "reason": "Second platform operator"},
        operation=operation,
    )
    result = expect(live.request(NOMINATIONS, actor=actor, method="POST", body=body), status)
    if status == 200:
        valid(NOMINATION_RECEIPT, result)
    return result, body


def create_account(live, email, actor="admin", status=200, **data):
    body = command(
        {
            "email": email,
            "first_name": "New",
            "last_name": "Colleague",
            "nomination_id": None,
            "tenant_id": None,
            "reason": "Sign-in for a nominated colleague",
            **data,
        }
    )
    result = expect(live.request(ACCOUNTS, actor=actor, method="POST", body=body), status)
    if status == 200:
        valid(ACCOUNT_RECEIPT, result)
    return result, body


def subject_of(live, identity_id):
    with live.db() as c:
        return c.execute(
            "SELECT provider_subject FROM impact.auth_identity WHERE identity_id=%s", (identity_id,)
        ).fetchone()["provider_subject"]


def nomination_action(live, nomination, name, subject=None, email=None, actor=None, status=200, body=None):
    path = NOMINATIONS + "/" + nomination["nomination_id"] + "/actions/" + name
    body = body or command({"reason": "Decision"}, nomination["revision_id"])
    if subject:
        return expect(as_person(live, subject, email, path, "POST", body), status)
    return expect(live.request(path, actor=actor, method="POST", body=body), status)


def onboard_operator(live):
    """A second operator onboarded entirely through the control plane; returns (identity, subject, email)."""
    email = "operator-" + str(uuid4())[:8] + "@example.test"
    nomination, _ = nominate(live, email)
    account, _ = create_account(live, email, nomination_id=nomination["nomination_id"])
    subject = subject_of(live, account["identity_id"])
    accepted = nomination_action(live, nomination, "accept", subject, email)
    assert accepted["state"] == "Accepted"
    return account["identity_id"], subject, email


def test_nomination_account_and_acceptance_by_the_nominee_only(live):
    email = "nominee-" + str(uuid4())[:8] + "@example.test"
    nomination, body = nominate(live, email)
    assert nomination["state"] == "Nominated" and nomination["email_mask"].startswith("no***@")
    assert not nomination["account_created_by_nominator"]
    # Exact retry returns the receipt; the same operation with another payload is a conflict.
    assert expect(live.request(NOMINATIONS, actor="admin", method="POST", body=body), 200) == nomination
    changed = {**body, "data": {**body["data"], "reason": "Changed"}}
    expect(live.request(NOMINATIONS, actor="admin", method="POST", body=changed), 409)
    # A second open nomination for the same address is refused.
    assert nominate(live, email, status=409)[0]["reason_code"] == "NOMINATION_PENDING"

    account, account_body = create_account(live, email, nomination_id=nomination["nomination_id"])
    password = account["temporary_password"]
    assert account["password_shown"] and len(password) >= 12 and account["provider_created"]
    assert account["sign_in_url"] == live.config["public_origin"] + "/"
    replay = expect(live.request(ACCOUNTS, actor="admin", method="POST", body=account_body), 200)
    assert replay["temporary_password"] is None and not replay["password_shown"]
    assert {k: v for k, v in replay.items() if k not in {"temporary_password", "password_shown"}} == {
        k: v for k, v in account.items() if k not in {"temporary_password", "password_shown"}
    }
    assert subject_of(live, account["identity_id"])

    # The person signs in with the one-time password on the development login page.
    with live.db() as c:
        c.execute("DELETE FROM impact.login_attempt")
    with httpx.Client(base_url=live.config["public_origin"], trust_env=False, timeout=20) as browser:
        signed_in = browser.post(
            "/auth/development-login",
            headers={"Origin": live.config["public_origin"]},
            json={"username": email, "password": password},
        )
        assert signed_in.status_code == 200, signed_in.text
        me = expect(browser.get("/auth/me"), 200)
        assert me["identity_id"] == account["identity_id"] and me["tenants"] == []
        mine = valid(DIRECTORY, expect(browser.get("/v1/platform/operators"), 200))
        assert not mine["operator"] and mine["operators"] == [] and mine["identities"] == []
        (seen,) = mine["nominations"]
        assert seen["nomination_id"] == nomination["nomination_id"] and seen["account_created_by_nominator"]
        current = seen["revision_id"]
        # The nominating operator cannot accept for the nominee; another operator neither.
        nomination_action(
            live, nomination, "accept", actor="admin", status=404, body=command({"reason": "x"}, current)
        )
        nomination_action(
            live, nomination, "accept", actor="owner", status=404, body=command({"reason": "x"}, current)
        )
        stale = command({"reason": "Accept"}, nomination["nomination_id"])
        expect(
            browser.post(
                NOMINATIONS + "/" + nomination["nomination_id"] + "/actions/accept",
                headers={"Origin": live.config["public_origin"], "X-CSRF-Token": me["csrf_token"]},
                json=stale,
            ),
            409,
        )
        accept = command({"reason": "I accept the operator role"}, current)
        accepted = expect(
            browser.post(
                NOMINATIONS + "/" + nomination["nomination_id"] + "/actions/accept",
                headers={"Origin": live.config["public_origin"], "X-CSRF-Token": me["csrf_token"]},
                json=accept,
            ),
            200,
        )
        assert accepted["state"] == "Accepted" and accepted["nominee_identity_id"] == account["identity_id"]
        assert expect(browser.get("/v1/platform/tenants"), 200)["operator"] is True
    # The first sign-in consumed the one-time password: it can no longer be reissued.
    reissue = command({"email": email, "reason": "Lost it"}, account["revision_id"])
    refused = live.request(
        ACCOUNTS + "/" + account["account_id"] + "/actions/reissue",
        actor="admin",
        method="POST",
        body=reissue,
    )
    assert expect(refused, 409)["reason_code"] == "ACCOUNT_IN_USE"
    operators = valid(DIRECTORY, expect(live.request("/v1/platform/operators", actor="admin"), 200))
    entry = next(o for o in operators["operators"] if o["identity_id"] == account["identity_id"])
    assert entry["active"] and nomination["nomination_id"] in entry["authority_reference"]
    with live.db() as c:
        events = c.execute(
            "SELECT action,tenant_id,payload::text AS payload FROM impact.platform_event WHERE identity_id IN (%s,%s) AND action IN ('operator-nominate','account-create','operator-accept') AND (payload->>'nomination_id'=%s OR payload->>'account_id'=%s)",
            (
                live.fixture["actors"]["admin"]["identity_id"],
                account["identity_id"],
                nomination["nomination_id"],
                account["account_id"],
            ),
        ).fetchall()
        assert sorted(e["action"] for e in events) == [
            "account-create",
            "operator-accept",
            "operator-nominate",
        ]
        assert all(e["tenant_id"] is None for e in events)
        # The one-time password exists nowhere in the platform's records.
        for table in ["platform_event", "platform_receipt", "provider_account"]:
            assert not c.execute(
                "SELECT 1 FROM impact." + table + " t WHERE t::text LIKE %s", ("%" + password + "%",)
            ).fetchone(), table
        row = c.execute(
            "SELECT * FROM impact.platform_operator WHERE identity_id=%s", (account["identity_id"],)
        ).fetchone()
        assert row["active"]
    assert password not in (live.local / "api.log").read_text()
    assert password not in (live.local / "users.json").read_text()


def test_self_nomination_non_operators_and_existing_operators_are_refused(live):
    assert nominate(live, "admin@example.test", status=403)[0]["reason_code"] == "SELF_NOMINATION"
    assert nominate(live, "someone@example.test", actor="author", status=403)[0]["reason_code"] == (
        "PLATFORM_OPERATOR_REQUIRED"
    )
    assert nominate(live, "owner@example.test", status=409)[0]["reason_code"] == "ALREADY_OPERATOR"
    assert (
        nominate(live, "late-" + str(uuid4())[:8] + "@example.test", days=400, status=422)[0]["reason_code"]
        == "OPERATOR_EXPIRY_BOUNDS"
    )
    stale = signed(live, live.fixture["actors"]["admin"]["identity_id"], auth_time=time.time() - 400)
    response = live.request(
        NOMINATIONS,
        actor=None,
        method="POST",
        headers={"Authorization": "Bearer " + stale},
        body=command({"email": "x@example.test", "operator_expires_at": expiry(10), "reason": "x"}),
    )
    assert expect(response, 403)["code"] == "ASSURANCE_REQUIRED"
    expect(live.request(NOMINATIONS, actor="admin", method="POST", body=command({"email": "x"})), 422)
    # Accounts: an operator cannot create one for their own address; a non-operator for anyone.
    assert create_account(live, "admin@example.test", status=403)[0]["reason_code"] == "SELF_ACCOUNT"
    assert create_account(live, "someone@example.test", actor="author", status=403)[0]["reason_code"] == (
        "PLATFORM_OPERATOR_REQUIRED"
    )


def test_a_second_identity_of_the_nominating_operator_cannot_accept(live):
    email = "alias-" + str(uuid4())[:8] + "@example.test"
    nomination, _ = nominate(live, email)
    account, _ = create_account(live, email, nomination_id=nomination["nomination_id"])
    # Simulate one person holding two provider accounts: the new account is linked to the
    # nominating operator's natural person (what an identity merge would record).
    with live.db() as c:
        c.execute(
            "UPDATE impact.auth_identity SET natural_identity_id=%s WHERE identity_id=%s",
            (live.fixture["actors"]["admin"]["natural_identity_id"], account["identity_id"]),
        )
    subject = subject_of(live, account["identity_id"])
    refused = nomination_action(live, nomination, "accept", subject, email, status=403)
    assert refused["reason_code"] == "INDEPENDENCE_REQUIRED"
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.platform_operator WHERE identity_id=%s", (account["identity_id"],)
        ).fetchone()
    # The database refuses it too, whatever the application checked.
    with live.db() as c:
        c.execute("SET ROLE impact_platform")
        with pytest.raises(Exception, match="acceptance denied"):
            c.execute(
                "SELECT impact.accept_operator_nomination(%s,%s)",
                (nomination["nomination_id"], account["identity_id"]),
            )


def test_decline_cancel_and_closed_nominations(live):
    email = "decline-" + str(uuid4())[:8] + "@example.test"
    nomination, _ = nominate(live, email)
    account, _ = create_account(live, email, nomination_id=nomination["nomination_id"])
    subject = subject_of(live, account["identity_id"])
    # A person not addressed by the nomination does not see it.
    other = "other-" + str(uuid4())[:8] + "@example.test"
    assert (
        valid(DIRECTORY, expect(as_person(live, subject, other, "/v1/platform/operators"), 200))[
            "nominations"
        ]
        == []
    )
    declined = nomination_action(live, nomination, "decline", subject, email)
    assert declined["state"] == "Declined"
    nomination_action(live, declined, "accept", subject, email, status=409)
    nomination_action(live, declined, "cancel", actor="admin", status=409)
    second, _ = nominate(live, email)
    nomination_action(live, second, "cancel", subject, email, status=403)
    cancelled = nomination_action(live, second, "cancel", actor="owner")
    assert cancelled["state"] == "Cancelled"
    # The platform role cannot record an acceptance by itself (only the definer can).
    third, _ = nominate(live, email)
    with live.db() as c:
        c.execute("SET ROLE impact_platform")
        with pytest.raises(Exception, match="acceptance only through"):
            c.execute(
                "UPDATE impact.platform_operator_nomination SET state='Accepted' WHERE nomination_id=%s",
                (third["nomination_id"],),
            )
    with live.db() as c:
        c.execute("SET ROLE impact_platform")
        with pytest.raises(Exception, match="permission denied"):
            c.execute(
                "INSERT INTO impact.platform_operator(identity_id,active,expires_at,authority_reference) VALUES(%s,true,now()+interval '1 day','direct')",
                (account["identity_id"],),
            )


def test_a_new_operator_counts_at_activation_only_as_a_different_person(live):
    identity, subject, email = onboard_operator(live)
    # Requested by `admin` for owner `author`: the new operator is independent of both.
    row = expect(request_tenant(live)[0], 200)
    accepted = tenant_action(live, row, "accept-owner", actor="author")
    recovery_contact(live, accepted)
    # A recovery contact does not change the tenant's revision (the listing is paged, so it is
    # not searched here: in a full run the tenant may be beyond its first page).
    current = accepted
    activated = expect(
        as_person(
            live,
            subject,
            email,
            "/v1/platform/tenants/" + row["tenant_id"] + "/actions/activate",
            "POST",
            command({"reason": "Independent activation by the second operator"}, current["revision_id"]),
        ),
        200,
    )
    assert activated["state"] == "Active"
    # When the new operator requested the tenant, the same person cannot activate it.
    qualification = expect(live.request("/v1/platform/tenants", actor="admin"), 200)["qualifications"][0]
    requested = expect(
        as_person(
            live,
            subject,
            email,
            "/v1/platform/tenants",
            "POST",
            command(
                {
                    "owner_identity_id": live.fixture["actors"]["author"]["identity_id"],
                    "qualification_id": qualification["qualification_id"],
                    "operating_name": "Requested by the new operator",
                    "reporting_zone": "UTC",
                    "retention_days": 365,
                    "privacy_reference": qualification["privacy_reference"],
                    "reason": "Second tenant",
                }
            ),
        ),
        200,
    )
    accepted = tenant_action(live, requested, "accept-owner", actor="author")
    recovery_contact(live, accepted)
    current = accepted
    refused = as_person(
        live,
        subject,
        email,
        "/v1/platform/tenants/" + requested["tenant_id"] + "/actions/activate",
        "POST",
        command({"reason": "Self activation"}, current["revision_id"]),
    )
    assert expect(refused, 403)["reason_code"] == "INDEPENDENCE_REQUIRED"
    # An operator independent of both (the fixture `owner` operator) still can.
    assert tenant_action(live, current, "activate", actor="owner")["state"] == "Active"


def test_a_tenant_owner_creates_sign_ins_only_for_invited_addresses(live):
    tenant, applied = onboarded(live)
    email = "invitee-" + str(uuid4())[:8] + "@example.test"
    data = {"tenant_id": tenant}
    assert create_account(live, email, actor="author", status=403, **data)[0]["reason_code"] == (
        "INVITATION_REQUIRED"
    )
    roles = expect(live.request(live.path("role-templates", tenant=tenant), actor="author"), 200)["items"]
    role = next(r for r in roles if r["name"] == "MEL_ADMIN")
    expect(
        live.request(
            live.path("member-invitations", tenant=tenant),
            actor="author",
            method="POST",
            body=command(
                {
                    "email": email,
                    "role_template_id": role["object_id"],
                    "scope_ids": [applied["scope_id"]],
                    "expires_at": expiry(5),
                    "membership_expires_at": expiry(20),
                    "external": True,
                    "reason": "New programme officer",
                }
            ),
        ),
        200,
    )
    # Only the tenant's current owner: not its second administrator, not an operator, not elsewhere.
    create_account(live, email, actor="reviewer", status=404, **data)
    create_account(live, email, actor="admin", status=404, **data)
    create_account(live, email, actor="other_tenant", status=404, **data)
    account, _ = create_account(live, email, actor="author", **data)
    assert account["tenant_id"] == tenant and account["temporary_password"]
    with live.db() as c:
        event = c.execute(
            "SELECT tenant_id FROM impact.platform_event WHERE action='account-create' AND payload->>'account_id'=%s",
            (account["account_id"],),
        ).fetchone()
        assert str(event["tenant_id"]) == tenant
    path = ACCOUNTS + "/" + account["account_id"] + "/actions/reissue"
    body = command({"email": email, "reason": "Handed over the wrong note"}, account["revision_id"])
    expect(live.request(path, actor="reviewer", method="POST", body=body), 404)
    wrong = command({"email": "x" + email, "reason": "Wrong address"}, account["revision_id"])
    assert expect(live.request(path, actor="author", method="POST", body=wrong), 422)["reason_code"] == (
        "EMAIL_MISMATCH"
    )
    reissued = expect(live.request(path, actor="author", method="POST", body=body), 200)
    assert reissued["temporary_password"] and reissued["temporary_password"] != account["temporary_password"]
    assert reissued["credentials_issued"] == 2
    expect(live.request(path, actor="author", method="POST", body=body), 200)["temporary_password"] is None
    stale = command({"email": email, "reason": "Again"}, account["revision_id"])
    expect(live.request(path, actor="author", method="POST", body=stale), 409)
    users = json.loads((live.local / "users.json").read_text())
    assert users[email]["temporary"] is True
    assert reissued["temporary_password"] not in json.dumps(users)
