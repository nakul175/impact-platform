"""Live control-plane acceptance and isolation; no provider qualification is inferred."""

import time
from types import SimpleNamespace
from uuid import uuid4
import psycopg
import pytest
from test_administration import command, expect, signed, expiry
from impact_api.store import Context, write
from impact_api.tenant_contracts import DIRECTORY, RECEIPT
from jsonschema import Draft202012Validator, FormatChecker

BASE = "/v1/platform/tenants"


def directory(live, actor="admin"):
    result = expect(live.request(BASE, actor=actor), 200)
    Draft202012Validator(DIRECTORY, format_checker=FormatChecker()).validate(result)
    return result


def request_tenant(live, **changes):
    qualification = directory(live)["qualifications"][0]
    data = {
        "owner_identity_id": live.fixture["actors"]["author"]["identity_id"],
        "qualification_id": qualification["qualification_id"],
        "operating_name": "Acceptance tenant " + str(uuid4())[:8],
        "reporting_zone": "Asia/Kolkata",
        "retention_days": 365,
        "privacy_reference": qualification["privacy_reference"],
        "reason": "Qualification request",
        **changes,
    }
    body = command(data)
    response = live.request(BASE, actor="admin", method="POST", body=body)
    return response, body


def action(live, row, name, actor="owner", status=200, body=None):
    return expect(
        live.request(
            BASE + "/" + row["tenant_id"] + "/actions/" + name,
            actor=actor,
            method="POST",
            body=body or command({"reason": "Lifecycle qualification"}, row["revision_id"]),
        ),
        status,
    )


def active(live):
    row = expect(request_tenant(live)[0], 200)
    accepted = action(live, row, "accept-owner", actor="author")
    recovery_contact(live, accepted)
    return action(live, accepted, "activate")


def recovery_contact(live, tenant):
    contact = expect(
        live.request(
            BASE + "/" + tenant["tenant_id"] + "/recovery-contacts",
            method="POST",
            body=command(
                {
                    "nominee_identity_id": live.fixture["actors"]["partner"]["identity_id"],
                    "expected_contact_revision": tenant.get("recovery_contact", {}).get("revision_id"),
                    "expires_at": expiry(60),
                    "reason": "Synthetic recovery contact",
                },
                tenant["revision_id"],
            ),
        ),
        200,
    )
    path = "/v1/platform/recovery-contacts/" + contact["contact_id"] + "/actions/"
    contact = expect(
        live.request(
            path + "verify",
            actor="partner",
            method="POST",
            body=command({"reason": "Confirm registered account"}, contact["revision_id"]),
        ),
        200,
    )
    return expect(
        live.request(
            path + "approve",
            actor="admin",
            method="POST",
            body=command({"reason": "Independent contact review"}, contact["revision_id"]),
        ),
        200,
    )


def test_request_requires_separate_operator_authority(live):
    row, body = request_tenant(live)
    row = expect(row, 200)
    Draft202012Validator(RECEIPT, format_checker=FormatChecker()).validate(row)
    assert row["state"] == "Requested"
    expect(live.request(BASE, actor="reviewer", method="POST", body=body), 403)
    assert directory(live, "author")["operator"] is False
    assert row["tenant_id"] not in {r["tenant_id"] for r in directory(live, "reviewer")["items"]}
    expect(live.request(BASE, actor="admin", method="POST", body=body), 200)
    changed = {**body, "data": {**body["data"], "operating_name": "Changed retry"}}
    expect(live.request(BASE, actor="admin", method="POST", body=changed), 409)
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.platform_event WHERE tenant_id=%s", (row["tenant_id"],)
            ).fetchone()["n"]
            == 1
        )


def test_owner_acceptance_activation_independence_and_no_implied_access(live):
    row = expect(request_tenant(live)[0], 200)
    action(live, row, "activate", status=409)
    action(live, row, "accept-owner", actor="reviewer", status=404)
    body = command({"reason": "Accept exact nominated configuration"}, row["revision_id"])
    accepted = action(live, row, "accept-owner", actor="author", body=body)
    assert not accepted["readiness"]["recovery_contact_verified"]
    assert action(live, row, "accept-owner", actor="author", body=body) == accepted
    action(live, row, "accept-owner", actor="author", status=409)
    action(live, accepted, "activate", actor="admin", status=403)
    action(live, accepted, "activate", status=403)
    recovery_contact(live, accepted)
    activated = action(live, accepted, "activate")
    access = expect(live.request(live.path("me/access", tenant=row["tenant_id"])), 200)
    assert access["capabilities"] == []
    expect(live.request(live.path("programmes", tenant=row["tenant_id"])), 403)
    expect(live.request(live.path("me/access", tenant=row["tenant_id"]), actor="owner"), 404)
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.grant_current WHERE tenant_id=%s", (row["tenant_id"],)
            ).fetchone()["n"]
            == 0
        )
    assert activated["state"] == "Active"


@pytest.mark.parametrize(
    "changes",
    [
        {"reporting_zone": "No/Such_Zone"},
        {"retention_days": 4000},
        {"privacy_reference": "Wrong policy"},
        {"retention_days": True},
        {"unknown": "rejected"},
    ],
)
def test_closed_profile_and_qualified_policy(live, changes):
    expect(request_tenant(live, **changes)[0], 422)


def test_qualification_revision_drift_and_expired_acceptance(live):
    row = expect(request_tenant(live)[0], 200)
    with live.db() as c:
        c.execute(
            "UPDATE impact.tenant_onboarding SET owner_expires_at=now()-interval '1 second' WHERE tenant_id=%s",
            (row["tenant_id"],),
        )
    action(live, row, "accept-owner", actor="author", status=403)
    row = expect(request_tenant(live)[0], 200)
    accepted = action(live, row, "accept-owner", actor="author")
    # Drift the tenant's pin, leaving shared qualification fixtures unchanged.
    with live.db() as c:
        c.execute(
            "UPDATE impact.tenant_onboarding SET qualification_revision=%s WHERE tenant_id=%s",
            (str(uuid4()), row["tenant_id"]),
        )
    action(live, accepted, "activate", status=403)


def test_operator_revocation_prevents_receipt_replay(live):
    response, body = request_tenant(live)
    expect(response, 200)
    identity = live.fixture["actors"]["admin"]["identity_id"]
    try:
        with live.db() as c:
            c.execute("UPDATE impact.platform_operator SET active=false WHERE identity_id=%s", (identity,))
        expect(live.request(BASE, actor="admin", method="POST", body=body), 403)
    finally:
        with live.db() as c:
            c.execute("UPDATE impact.platform_operator SET active=true WHERE identity_id=%s", (identity,))


def test_suspension_reactivation_and_closing_fence(live):
    row = active(live)
    suspended = action(live, row, "suspend", actor="admin")
    expect(live.request(live.path("me/access", tenant=row["tenant_id"])), 404)
    action(live, row, "suspend", actor="admin", status=409)
    resumed = action(live, suspended, "reactivate")
    expect(live.request(live.path("me/access", tenant=row["tenant_id"])), 401)
    token = signed(live, live.fixture["actors"]["author"]["identity_id"], auth_time=time.time())
    expect(
        live.request(
            live.path("me/access", tenant=row["tenant_id"]),
            actor=None,
            headers={"Authorization": "Bearer " + token},
        ),
        200,
    )
    closed = action(live, resumed, "begin-closure", actor="admin")
    assert closed["state"] == "Closing"
    action(live, closed, "reactivate", status=409)
    expect(live.request(live.path("me/access", tenant=row["tenant_id"])), 404)
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s", (row["tenant_id"],)
            ).fetchone()["n"]
            > 0
        )


def test_runtime_roles_cannot_manufacture_platform_authority_or_lifecycle(live):
    for role, statement in [
        ("impact_app", "SELECT * FROM impact.platform_operator"),
        ("impact_identity", "SELECT * FROM impact.tenant_onboarding"),
        ("impact_platform", "UPDATE impact.platform_operator SET active=true"),
        ("impact_app", "UPDATE impact.tenant_root SET lifecycle_state='Active'"),
        ("impact_platform", "SELECT * FROM impact.observation_current"),
        ("impact_platform", "DELETE FROM impact.platform_event"),
    ]:
        with live.db() as c:
            c.execute("SET LOCAL ROLE " + role)
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(statement)


def test_recent_authentication_required(live):
    row = active(live)
    token = signed(live, live.fixture["actors"]["admin"]["identity_id"], auth_time=time.time() - 600)
    expect(
        live.request(
            BASE + "/" + row["tenant_id"] + "/actions/suspend",
            actor=None,
            method="POST",
            headers={"Authorization": "Bearer " + token},
            body=command({"reason": "Too old"}, row["revision_id"]),
        ),
        403,
    )


def test_suspension_holds_work_without_resurrection_or_cross_tenant_effect(live):
    row = active(live)
    tenant = row["tenant_id"]
    actor = live.fixture["actors"]["author"]
    event, scope, queued, running, schedule = [str(uuid4()) for _ in range(5)]
    with live.db() as c:
        principal = str(
            c.execute(
                "SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
                (tenant, actor["identity_id"]),
            ).fetchone()["principal_id"]
        )
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        ctx = Context(
            tenant, principal, "", SimpleNamespace(natural_identity_id=actor["natural_identity_id"]), 0, 0, []
        )
        write(c, ctx, "Schedule", {"command_type": "TEST"}, "Active", object_id=schedule, track_author=False)
        predicate = write(c, ctx, "Predicate", {"scope_type": "TENANT"}, "Active", track_author=False)
        c.execute(
            "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) VALUES(%s,%s,'TENANT',%s)",
            (tenant, scope, predicate["revision_id"]),
        )
        for job, state in [(queued, "Queued"), (running, "Running")]:
            c.execute(
                "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest) VALUES(%s,%s,'Test',%s,%s,%s,'{}')",
                (tenant, job, principal, scope, state),
            )
        c.execute("INSERT INTO impact.outbox_event VALUES(%s,%s,'test',now(),'{}')", (tenant, event))
        c.execute("INSERT INTO impact.outbox_delivery(tenant_id,event_id) VALUES(%s,%s)", (tenant, event))
    suspended = action(live, row, "suspend", actor="admin")
    action(live, suspended, "reactivate")
    # An unrelated existing tenant remains usable throughout.
    expect(live.request(live.path("programmes")), 200)
    with live.db() as c:
        jobs = {
            str(j["job_id"]): j
            for j in c.execute(
                "SELECT job_id,state,cancellation_requested_at,lease_generation FROM impact.job WHERE tenant_id=%s",
                (tenant,),
            ).fetchall()
        }
        assert jobs[queued]["state"] == "Cancelled"
        assert jobs[running]["state"] == "Cancelling"
        assert all(j["lease_generation"] == 1 and j["cancellation_requested_at"] for j in jobs.values())
        assert c.execute(
            "SELECT held_at FROM impact.outbox_delivery WHERE tenant_id=%s AND event_id=%s", (tenant, event)
        ).fetchone()["held_at"]
        assert c.execute(
            "SELECT 1 FROM impact.tenant_schedule_hold WHERE tenant_id=%s AND schedule_id=%s",
            (tenant, schedule),
        ).fetchone()


def test_platform_record_projection_does_not_reveal_business_payloads(live):
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_platform")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        assert not c.execute(
            "SELECT payload FROM impact.object_revision WHERE object_type='Observation'"
        ).fetchall()
        assert not c.execute(
            "SELECT object_id FROM impact.object_registry WHERE object_type='Programme'"
        ).fetchall()
