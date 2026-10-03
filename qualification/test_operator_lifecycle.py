"""v0.27 operator lifecycle: renewal before expiry and deactivation of a platform operator, through
live HTTP on the platform role.

Each change is made by a different active operator (a different natural person) with fresh
assurance and a reason, names the exact operator revision, and is written only by the SECURITY
DEFINER `impact.apply_operator_change` (migration 0029) into `platform_operator` and the insert-only
register `platform_operator_change`, with a tenant-less `platform_event` and a `platform_receipt`.
Nobody renews or deactivates themselves, a second identity of the subject's natural person counts
as the subject, a non-operator never learns whether the subject exists, and the last active operator
cannot be deactivated (the actor must be another one).
"""

import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import psycopg
import pytest
from jsonschema import Draft202012Validator, FormatChecker
from test_administration import command, expect, expiry, signed
from test_operator_onboarding import NOMINATIONS, as_person, onboard_operator
from impact_api.operator_contracts import DIRECTORY, OPERATOR_RECEIPT

OPERATORS = "/v1/platform/operators"


def valid(schema, value):
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    return value


def listed(live, identity_id, actor="admin"):
    directory = valid(DIRECTORY, expect(live.request(OPERATORS, actor=actor), 200))
    return next(o for o in directory["operators"] if o["identity_id"] == identity_id), directory


def change(live, identity_id, action, revision, actor="admin", status=200, body=None, **data):
    body = body or command({"reason": "Operator lifecycle check", **data}, revision)
    path = OPERATORS + "/" + identity_id + "/actions/" + action
    result = expect(live.request(path, actor=actor, method="POST", body=body), status)
    if status == 200:
        valid(OPERATOR_RECEIPT, result)
    return result, body


def test_renewal_by_another_operator_with_receipt_event_and_register(live):
    identity, subject, email = onboard_operator(live)
    before, _ = listed(live, identity)
    assert before["state"] == "Active" and before["active"]
    # Bounds: not earlier than the current expiry, not beyond 365 days; a stale revision; no reason.
    assert (
        change(live, identity, "renew", before["revision_id"], status=422, expires_at=expiry(10))[0][
            "reason_code"
        ]
        == "OPERATOR_EXPIRY_BOUNDS"
    )
    assert (
        change(live, identity, "renew", before["revision_id"], status=422, expires_at=expiry(400))[0][
            "reason_code"
        ]
        == "OPERATOR_EXPIRY_BOUNDS"
    )
    change(live, identity, "renew", str(uuid4()), status=409, expires_at=expiry(60))
    expect(
        live.request(
            OPERATORS + "/" + identity + "/actions/renew",
            actor="admin",
            method="POST",
            body=command({"expires_at": expiry(60)}, before["revision_id"]),
        ),
        422,
    )
    # A non-operator never learns whether the subject exists; an unknown subject is unavailable.
    change(live, identity, "renew", before["revision_id"], actor="author", status=404, expires_at=expiry(60))
    change(live, str(uuid4()), "renew", before["revision_id"], status=404, expires_at=expiry(60))
    # Fresh assurance is required.
    stale = signed(live, live.fixture["actors"]["admin"]["identity_id"], auth_time=time.time() - 400)
    refused = live.request(
        OPERATORS + "/" + identity + "/actions/renew",
        actor=None,
        method="POST",
        headers={"Authorization": "Bearer " + stale},
        body=command({"expires_at": expiry(60), "reason": "x"}, before["revision_id"]),
    )
    assert expect(refused, 403)["code"] == "ASSURANCE_REQUIRED"
    # The subject cannot renew themself.
    own = as_person(
        live,
        subject,
        email,
        OPERATORS + "/" + identity + "/actions/renew",
        "POST",
        command({"expires_at": expiry(60), "reason": "Self renewal"}, before["revision_id"]),
    )
    assert expect(own, 403)["reason_code"] == "INDEPENDENCE_REQUIRED"

    later = expiry(60)
    renewed, body = change(live, identity, "renew", before["revision_id"], expires_at=later)
    assert renewed["state"] == "Active" and renewed["revision_id"] != before["revision_id"]
    assert datetime.fromisoformat(renewed["expires_at"]) == datetime.fromisoformat(later)
    # Exact retry returns the receipt; the same operation with another payload is a conflict; the
    # old revision is stale now.
    assert change(live, identity, "renew", before["revision_id"], body=body)[0] == renewed
    changed = {**body, "data": {**body["data"], "reason": "Changed"}}
    change(live, identity, "renew", before["revision_id"], status=409, body=changed)
    change(live, identity, "renew", before["revision_id"], status=409, expires_at=expiry(90))
    after, directory = listed(live, identity)
    assert after["revision_id"] == renewed["revision_id"] and after["expires_at"] == renewed["expires_at"]
    entry = next(g for g in directory["changes"] if g["change_id"] == renewed["change_id"])
    assert entry["action"] == "renew" and entry["operator_identity_id"] == identity
    assert entry["actor_identity_id"] == live.fixture["actors"]["admin"]["identity_id"]
    assert datetime.fromisoformat(entry["previous_expires_at"]) == datetime.fromisoformat(
        before["expires_at"]
    )
    with live.db() as c:
        row = c.execute(
            "SELECT * FROM impact.platform_operator_change WHERE change_id=%s", (renewed["change_id"],)
        ).fetchone()
        assert row["previous_active"] and row["active"] and str(row["revision_id"]) == renewed["revision_id"]
        assert str(row["previous_revision_id"]) == before["revision_id"]
        assert row["reason"] == "Operator lifecycle check"
        event = c.execute(
            "SELECT tenant_id,revision_id,reason FROM impact.platform_event WHERE action='operator-renew' AND payload->>'change_id'=%s",
            (renewed["change_id"],),
        ).fetchone()
        assert event["tenant_id"] is None and str(event["revision_id"]) == renewed["revision_id"]
        receipt = c.execute(
            "SELECT 1 FROM impact.platform_receipt WHERE identity_id=%s AND operation_id=%s",
            (live.fixture["actors"]["admin"]["identity_id"], body["operation_id"]),
        ).fetchone()
        assert receipt
        # The origin of the authority is kept; only the expiry moved.
        operator = c.execute(
            "SELECT * FROM impact.platform_operator WHERE identity_id=%s", (identity,)
        ).fetchone()
        assert operator["active"] and "Accepted nomination" in operator["authority_reference"]
    # The renewed operator still acts as one.
    assert expect(as_person(live, subject, email, "/v1/platform/tenants"), 200)["operator"] is True


def test_deactivation_by_another_operator_ends_authority_at_once(live):
    identity, subject, email = onboard_operator(live)
    current, _ = listed(live, identity)
    # Nobody deactivates themself.
    own = as_person(
        live,
        subject,
        email,
        OPERATORS + "/" + identity + "/actions/deactivate",
        "POST",
        command({"reason": "Leaving"}, current["revision_id"]),
    )
    assert expect(own, 403)["reason_code"] == "INDEPENDENCE_REQUIRED"
    change(live, identity, "deactivate", current["revision_id"], actor="author", status=404)
    deactivated, body = change(live, identity, "deactivate", current["revision_id"], actor="owner")
    assert deactivated["state"] == "Deactivated" and not deactivated["active"]
    assert deactivated["expires_at"] == current["expires_at"]
    assert change(live, identity, "deactivate", current["revision_id"], actor="owner", body=body)[0] == (
        deactivated
    )
    # Authority ends at once: the person is no longer an operator anywhere in the control plane.
    mine = valid(DIRECTORY, expect(as_person(live, subject, email, OPERATORS), 200))
    assert not mine["operator"] and mine["operators"] == []
    assert expect(as_person(live, subject, email, "/v1/platform/tenants"), 200)["operator"] is False
    refused = as_person(
        live,
        subject,
        email,
        NOMINATIONS,
        "POST",
        command({"email": "x@example.test", "operator_expires_at": expiry(10), "reason": "x"}),
    )
    assert expect(refused, 403)["reason_code"] == "PLATFORM_OPERATOR_REQUIRED"
    # Deactivated authority is neither renewed nor deactivated again.
    assert (
        change(live, identity, "renew", deactivated["revision_id"], status=409, expires_at=expiry(60))[0][
            "reason_code"
        ]
        == "OPERATOR_DEACTIVATED"
    )
    assert change(live, identity, "deactivate", deactivated["revision_id"], status=409)[0]["reason_code"] == (
        "OPERATOR_DEACTIVATED"
    )
    with live.db() as c:
        row = c.execute(
            "SELECT * FROM impact.platform_operator_change WHERE change_id=%s", (deactivated["change_id"],)
        ).fetchone()
        assert row["action"] == "deactivate" and row["previous_active"] and not row["active"]
        assert str(row["actor_identity_id"]) == live.fixture["actors"]["owner"]["identity_id"]
        event = c.execute(
            "SELECT tenant_id FROM impact.platform_event WHERE action='operator-deactivate' AND payload->>'change_id'=%s",
            (deactivated["change_id"],),
        ).fetchone()
        assert event and event["tenant_id"] is None
        # At least one active operator always remains.
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.platform_operator WHERE active AND expires_at>now()"
            ).fetchone()["n"]
            >= 1
        )
    # Only the two fixture operators and the one onboarded here were involved: the changes list
    # shows the deactivation to operators.
    _, directory = listed(live, live.fixture["actors"]["owner"]["identity_id"])
    assert any(g["change_id"] == deactivated["change_id"] for g in directory["changes"])


def test_a_second_identity_of_the_subject_is_not_independent_and_the_database_refuses_too(live):
    identity, subject, email = onboard_operator(live)
    current, _ = listed(live, identity)
    admin = live.fixture["actors"]["admin"]
    # One person with two provider accounts: the new operator is linked to admin's natural person.
    with live.db() as c:
        c.execute(
            "UPDATE impact.auth_identity SET natural_identity_id=%s WHERE identity_id=%s",
            (admin["natural_identity_id"], identity),
        )
    assert (
        change(live, identity, "renew", current["revision_id"], status=403, expires_at=expiry(60))[0][
            "reason_code"
        ]
        == "INDEPENDENCE_REQUIRED"
    )
    assert change(live, identity, "deactivate", current["revision_id"], status=403)[0]["reason_code"] == (
        "INDEPENDENCE_REQUIRED"
    )
    with live.db() as c:
        for actor, expected in [
            (admin["identity_id"], current["revision_id"]),  # same natural person
            (identity, current["revision_id"]),  # self
            (live.fixture["actors"]["owner"]["identity_id"], str(uuid4())),  # stale revision
            (live.fixture["actors"]["author"]["identity_id"], current["revision_id"]),  # not an operator
        ]:
            with pytest.raises(psycopg.Error, match="operator change denied"):
                with c.transaction():
                    c.execute("SET LOCAL ROLE impact_platform")
                    c.execute(
                        "SELECT impact.apply_operator_change(%s,%s,%s,'deactivate',%s,NULL,now(),'x')",
                        (str(uuid4()), identity, actor, expected),
                    )
        # A renewal that does not move the expiry later is refused by the definer as well.
        with pytest.raises(psycopg.Error, match="operator change denied"):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_platform")
                c.execute(
                    "SELECT impact.apply_operator_change(%s,%s,%s,'renew',%s,now()+interval '1 day',now(),'x')",
                    (
                        str(uuid4()),
                        identity,
                        live.fixture["actors"]["owner"]["identity_id"],
                        current["revision_id"],
                    ),
                )
    # Another operator (the fixture owner, a different natural person) still can.
    renewed, _ = change(live, identity, "renew", current["revision_id"], actor="owner", expires_at=expiry(45))
    assert renewed["state"] == "Active"
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.platform_operator_change WHERE operator_identity_id=%s",
                (identity,),
            ).fetchone()["n"]
            == 1
        )


def test_platform_role_writes_operators_only_through_the_definer(live):
    identity, _, _ = onboard_operator(live)
    with live.db() as c:
        for statement in [
            "UPDATE impact.platform_operator SET active=false WHERE identity_id=%s",
            "UPDATE impact.platform_operator SET expires_at=now()+interval '2 years' WHERE identity_id=%s",
            "INSERT INTO impact.platform_operator_change(change_id,operator_identity_id,action,actor_identity_id,actor_auth_time,reason,previous_revision_id,revision_id,previous_expires_at,expires_at,previous_active,active) VALUES(gen_random_uuid(),%s,'deactivate',%s,now(),'x',gen_random_uuid(),gen_random_uuid(),now(),now(),true,false)",
            "DELETE FROM impact.platform_operator_change WHERE operator_identity_id=%s",
            "UPDATE impact.platform_operator_change SET reason='edited' WHERE operator_identity_id=%s",
        ]:
            params = (identity, live.fixture["actors"]["admin"]["identity_id"])
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with c.transaction():
                    c.execute("SET LOCAL ROLE impact_platform")
                    c.execute(statement, params[: statement.count("%s")])
    # Even the owner cannot re-point an operator row at another identity.
    with live.db() as c:
        with pytest.raises(psycopg.Error, match="operator identity is immutable"):
            with c.transaction():
                c.execute(
                    "UPDATE impact.platform_operator SET identity_id=%s WHERE identity_id=%s",
                    (str(uuid4()), identity),
                )
    # A direct update by a privileged maintainer still moves the revision, so a change that pinned
    # the earlier revision is refused.
    current, _ = listed(live, identity)
    with live.db() as c:
        c.execute(
            "UPDATE impact.platform_operator SET expires_at=expires_at+interval '1 hour' WHERE identity_id=%s",
            (identity,),
        )
    moved, _ = listed(live, identity)
    assert moved["revision_id"] != current["revision_id"]
    assert datetime.fromisoformat(moved["expires_at"]) - datetime.fromisoformat(current["expires_at"]) == (
        timedelta(hours=1)
    )
    change(live, identity, "deactivate", current["revision_id"], actor="owner", status=409)
    assert datetime.fromisoformat(moved["updated_at"]) > datetime.now(timezone.utc) - timedelta(minutes=5)
