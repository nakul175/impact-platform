"""v0.26a usable staging, through live HTTP and the actual database roles: reference data for a new
tenant (gap A1), the initial-access-v2 profile (A2) and reviewed purpose-bound grants (A4).

The tenant is onboarded exactly as on staging: an operator requests it, the owner accepts, a recovery
contact is approved, an independent operator activates it, and initial access (profile v2) is
proposed by the owner, accepted by the second administrator and approved by an independent operator.
Nothing here relaxes an independence rule; the tests assert that each one still holds.
"""

import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pytest
from test_administration import command, expect, expiry, signed
from test_access_bootstrap import propose, action as bootstrap_action
from impact_api.contracts import validate
from impact_api.reference_contracts import DEFAULTS


def onboarded(live, roles=("MEL_ADMIN", "PRIVACY")):
    """An Active tenant with reviewed initial access v2: owner `author`, second administrator
    `reviewer`, approved by the operator `admin`."""
    row, tenant, _, _ = propose(live, role_names=list(roles))
    row = bootstrap_action(live, row, "accept")
    applied = bootstrap_action(live, row, "approve", "admin")
    return tenant["tenant_id"], applied


def path(live, tenant, route):
    return live.path(route, tenant=tenant)


def objects(live, tenant, kind):
    with live.db() as c:
        return c.execute(
            "SELECT r.object_id,r.lifecycle_state,r.head_revision,v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type=%s ORDER BY v.payload->>'starts_at',r.object_id",
            (tenant, kind),
        ).fetchall()


def membership_of(live, tenant, actor):
    members = expect(
        live.request(path(live, tenant, "membership-directory") + "?limit=100", actor="author"), 200
    )["items"]
    return next(m for m in members if m["identity_id"] == live.fixture["actors"][actor]["identity_id"])


# ---- A1: reference data ---------------------------------------------------------------------------


def test_reference_defaults_make_a_new_tenant_ready_for_measurement(live):
    tenant, applied = onboarded(live)
    defaults = path(live, tenant, "reference-defaults")
    body = command({"reason": "Standard reference set for the first programme"})
    # The second administrator holds the same TENANT_ADMIN bundle; the owner applies it here.
    receipt = expect(live.request(defaults, method="POST", body=body), 200)
    validate("AdministrationReceipt", receipt)
    assert expect(live.request(defaults, method="POST", body=body), 200) == receipt
    changed = {**body, "data": {"reason": "Another reason"}}
    assert expect(live.request(defaults, method="POST", body=changed), 409)["code"] == "CONFLICT_OPERATION"
    again = expect(live.request(defaults, method="POST", body=command({"reason": "Twice"})), 409)
    assert again["reason_code"] == "REFERENCE_DEFAULTS_APPLIED"

    zone = ZoneInfo("Asia/Kolkata")
    year = datetime.now(zone).year
    calendars = objects(live, tenant, "ReportingCalendar")
    assert len(calendars) == 1 and calendars[0]["lifecycle_state"] == "Active"
    assert calendars[0]["payload"] == {
        "title": DEFAULTS["calendar"]["title"],
        "zone": "Asia/Kolkata",
        "frequency": "QUARTERLY",
        "first_year": year,
        "last_year": year + 1,
    }
    periods = objects(live, tenant, "Period")
    assert [p["payload"]["code"] for p in periods] == [
        str(y) + "-Q" + str(q) for y in (year, year + 1) for q in (1, 2, 3, 4)
    ]
    assert all(p["lifecycle_state"] == "Open" for p in periods)
    assert all(p["payload"]["calendar_version"] == str(calendars[0]["head_revision"]) for p in periods)
    for earlier, later in zip(periods, periods[1:]):
        assert earlier["payload"]["ends_at"] == later["payload"]["starts_at"]
    # Local midnight of 1 January in the tenant's reporting zone, held as a UTC instant.
    assert (
        periods[0]["payload"]["starts_at"]
        == datetime(year, 1, 1, tzinfo=zone).astimezone(timezone.utc).isoformat()
    )
    (workflow,) = objects(live, tenant, "WorkflowTemplate")
    assert workflow["payload"]["independent"] is True and workflow["payload"]["required_approvals"] == 1
    (template,) = objects(live, tenant, "ReportTemplate")
    assert template["lifecycle_state"] == "Active"
    assert [s["section_code"] for s in template["payload"]["sections"]] == ["summary", "results", "caveats"]
    (geography,) = objects(live, tenant, "Geography")
    assert geography["payload"] == {"title": "Organisation-wide", "code": "ORG"}
    with live.db() as c:
        # One audit event and one outbox event per record written (calendar, 8 periods, workflow
        # template, report template, geography), one stated reason, one receipt.
        audits = c.execute(
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND action_type='apply_reference_defaults'",
            (tenant,),
        ).fetchone()["n"]
        assert audits == 12
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='apply_reference_defaults'",
                (tenant,),
            ).fetchone()["n"]
            == 1
        )
        assert c.execute(
            "SELECT 1 FROM impact.admin_reason WHERE tenant_id=%s AND revision_id=%s",
            (tenant, receipt["revision_id"]),
        ).fetchone()

    # A programme manager (MEL_ADMIN, granted through an independently reviewed access request) can
    # now give a programme a calendar and a geography that satisfy readiness.
    member = membership_of(live, tenant, "reviewer")
    roles = expect(live.request(path(live, tenant, "role-templates"), actor="reviewer"), 200)["items"]
    role = next(r for r in roles if r["name"] == "MEL_ADMIN")
    request = expect(
        live.request(
            path(live, tenant, "access-requests"),
            actor="reviewer",
            method="POST",
            body=command(
                {
                    "membership_id": member["object_id"],
                    "expected_membership_revision": member["revision_id"],
                    "role_template_id": role["object_id"],
                    "scope_ids": [applied["scope_id"]],
                    "expires_at": expiry(20),
                    "reason": "Programme set-up",
                }
            ),
        ),
        200,
    )
    review = path(live, tenant, "access-requests") + "/" + request["object_id"] + "/actions/approve"
    approval = command({"reason": "Reviewed"}, request["revision_id"])
    expect(live.request(review, actor="reviewer", method="POST", body=approval), 403)
    expect(live.request(review, actor="author", method="POST", body=approval), 200)
    calendar_id = str(calendars[0]["object_id"])
    programme = expect(
        live.request(
            path(live, tenant, "programmes"),
            actor="reviewer",
            method="POST",
            body=command(
                {
                    "code": "FIRST",
                    "title": "First staged programme",
                    "programme_type": "SERVICE_DELIVERY",
                    "starts_at": periods[0]["payload"]["starts_at"],
                    "ends_at": periods[-1]["payload"]["ends_at"],
                    "reporting_calendar_id": calendar_id,
                    "geography_id": str(geography["object_id"]),
                }
            ),
        ),
        201,
    )
    readiness = expect(
        live.request(
            path(live, tenant, "programmes") + "/" + programme["object_id"] + "/readiness", actor="reviewer"
        ),
        200,
    )
    checks = {c["code"]: c["passed"] for c in readiness["checks"]}
    assert checks["PROGRAMME_DETAILS"] and checks["REPORTING_CALENDAR_ID"] and checks["GEOGRAPHY_ID"]
    listed = expect(live.request(path(live, tenant, "periods") + "?limit=100", actor="reviewer"), 200)
    assert len(listed["items"]) == 8


def test_reference_commands_are_governed_tenant_administration(live):
    calendars = live.path("reporting-calendars")
    create = command(
        {
            "title": "Monthly test calendar",
            "frequency": "MONTHLY",
            "zone": "Europe/London",
            "first_year": 2026,
            "years": 1,
            "reason": "Monthly reporting",
        }
    )
    # Wrong role (no reference-data.manage), another tenant, a revoked membership.
    expect(live.request(calendars, actor="author", method="POST", body=create), 403)
    expect(live.request(calendars, actor="other_tenant", method="POST", body=create), 404)
    expect(live.request(calendars, actor="revoked", method="POST", body=create), 404)
    stale = signed(live, live.fixture["actors"]["admin"]["identity_id"], auth_time=time.time() - 400)
    response = live.request(
        calendars, actor=None, method="POST", body=create, headers={"Authorization": "Bearer " + stale}
    )
    assert expect(response, 403)["code"] == "ASSURANCE_REQUIRED"
    receipt = expect(live.request(calendars, actor="admin", method="POST", body=create), 200)
    assert expect(live.request(calendars, actor="admin", method="POST", body=create), 200) == receipt
    bad = command({**create["data"], "zone": "Mars/Olympus"})
    assert expect(live.request(calendars, actor="admin", method="POST", body=bad), 422)["reason_code"] == (
        "INVALID_TIME_ZONE"
    )
    unknown = command({**create["data"], "extra": True})
    expect(live.request(calendars, actor="admin", method="POST", body=unknown), 422)
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        periods = c.execute(
            "SELECT v.payload FROM impact.object_revision v JOIN impact.object_registry r ON r.tenant_id=v.tenant_id AND r.head_revision=v.revision_id WHERE r.tenant_id=%s AND r.object_type='Period' AND v.payload->>'calendar_version'=%s ORDER BY v.payload->>'starts_at'",
            (tenant, receipt["revision_id"]),
        ).fetchall()
    assert [p["payload"]["code"] for p in periods] == ["2026-" + str(m).zfill(2) for m in range(1, 13)]
    # Summer time: April starts at 23:00 UTC on 31 March in London.
    assert periods[3]["payload"]["starts_at"] == "2026-03-31T23:00:00+00:00"
    extend = calendars + "/" + receipt["object_id"] + "/actions/extend"
    expect(
        live.request(
            extend,
            actor="admin",
            method="POST",
            body=command({"years": 1, "reason": "x"}, receipt["object_id"]),
        ),
        409,
    )
    extended = expect(
        live.request(
            extend,
            actor="admin",
            method="POST",
            body=command({"years": 1, "reason": "Next year"}, receipt["revision_id"]),
        ),
        200,
    )
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_type='Period' AND payload->>'calendar_version'=%s",
                (tenant, extended["revision_id"]),
            ).fetchone()["n"]
            == 12
        )
        head = c.execute(
            "SELECT v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
            (tenant, receipt["object_id"]),
        ).fetchone()["payload"]
        assert head["last_year"] == 2027
    workflow = expect(
        live.request(
            live.path("workflow-templates"),
            actor="admin",
            method="POST",
            body=command({"title": "Programme review", "reason": "Second review template"}),
        ),
        200,
    )
    assert workflow["business_state"] == "Active"
    sections = [
        {"section_code": "summary", "heading": "Summary", "required": True, "narrative_limit": 2000},
        {"section_code": "summary", "heading": "Again", "required": False, "narrative_limit": 2000},
    ]
    duplicate = command({"title": "Bad", "language": "en", "sections": sections, "reason": "x"})
    assert (
        expect(
            live.request(live.path("report-templates"), actor="admin", method="POST", body=duplicate), 422
        )["reason_code"]
        == "DUPLICATE_SECTION_CODE"
    )
    geography = command({"title": "Northern district", "code": "NORTH-1", "reason": "Programme area"})
    expect(live.request(live.path("geographies"), actor="admin", method="POST", body=geography), 200)
    clash = command({"title": "Again", "code": "north-1", "reason": "Programme area"})
    assert (
        expect(live.request(live.path("geographies"), actor="admin", method="POST", body=clash), 409)[
            "reason_code"
        ]
        == "GEOGRAPHY_CODE_EXISTS"
    )
    # The fixture calendar (zone and frequency only) is never extended by guesswork.
    fixture_calendar = live.records["calendar"]
    with live.db() as c:
        head = c.execute(
            "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
            (tenant, fixture_calendar["object_id"]),
        ).fetchone()["head_revision"]
    refused = live.request(
        live.path("reporting-calendars") + "/" + fixture_calendar["object_id"] + "/actions/extend",
        actor="admin",
        method="POST",
        body=command({"years": 1, "reason": "Unknown coverage"}, str(head)),
    )
    assert expect(refused, 422)["reason_code"] == "CALENDAR_NOT_EXTENSIBLE"


# ---- A4: reviewed purpose-bound grants ------------------------------------------------------------


def purpose_request(live, tenant, scope, member, actor="reviewer", status=200, **changes):
    body = command(
        {
            "membership_id": member["object_id"],
            "expected_membership_revision": member["revision_id"],
            "capability": "privacy-cases.read",
            "purpose": "DATA_SUBJECT_REQUEST",
            "scope_id": scope,
            "expires_at": expiry(20),
            "reason": "Handle a data-subject request",
            **changes,
        }
    )
    return expect(
        live.request(path(live, tenant, "purpose-grants"), actor=actor, method="POST", body=body), status
    ), body


def test_purpose_bound_grant_needs_an_independent_second_person(live):
    tenant, applied = onboarded(live)
    member = membership_of(live, tenant, "reviewer")
    privacy = path(live, tenant, "privacy-cases") + "?purpose=DATA_SUBJECT_REQUEST"
    expect(live.request(privacy, actor="reviewer"), 403)
    request, body = purpose_request(live, tenant, applied["scope_id"], member)
    validate("AdministrationReceipt", request)
    assert (
        expect(
            live.request(path(live, tenant, "purpose-grants"), actor="reviewer", method="POST", body=body),
            200,
        )
        == request
    )
    changed = {**body, "data": {**body["data"], "reason": "Changed"}}
    expect(
        live.request(path(live, tenant, "purpose-grants"), actor="reviewer", method="POST", body=changed), 409
    )
    listed = expect(live.request(path(live, tenant, "purpose-grants"), actor="author"), 200)["items"]
    assert [i["capability"] for i in listed] == ["privacy-cases.read"] and listed[0]["state"] == "Requested"
    approve = path(live, tenant, "purpose-grants") + "/" + request["object_id"] + "/actions/approve"
    decision = command({"reason": "Independent review"}, request["revision_id"])
    # The requester (who is also the member receiving it) cannot approve; another tenant cannot see it.
    assert (
        expect(live.request(approve, actor="reviewer", method="POST", body=decision), 403)["reason_code"]
        == "INDEPENDENCE_REQUIRED"
    )
    expect(live.request(approve, actor="other_tenant", method="POST", body=decision), 404)
    expect(
        live.request(
            approve, actor="author", method="POST", body=command({"reason": "x"}, request["object_id"])
        ),
        409,
    )
    applied_grant = expect(live.request(approve, actor="author", method="POST", body=decision), 200)
    assert expect(live.request(approve, actor="author", method="POST", body=decision), 200) == applied_grant
    access = expect(live.request(path(live, tenant, "me/access"), actor="reviewer"), 200)
    assert ["privacy-cases.read", "DATA_SUBJECT_REQUEST"] in access["purpose_capabilities"]
    assert "privacy-cases.read" not in access["capabilities"]
    expect(live.request(privacy, actor="reviewer"), 200)
    expect(live.request(path(live, tenant, "privacy-cases") + "?purpose=OTHER", actor="reviewer"), 403)
    with live.db() as c:
        grants = c.execute(
            "SELECT g.capability,g.purpose,g.issuer_id,s.scope_type FROM impact.grant_current g JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id WHERE g.tenant_id=%s AND g.purpose IS NOT NULL",
            (tenant,),
        ).fetchall()
        assert len(grants) == 1 and grants[0]["purpose"] == "DATA_SUBJECT_REQUEST"
        assert grants[0]["scope_type"] == "TENANT"
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND action_type IN ('request_purpose_grant','approve_purpose_grant')",
                (tenant,),
            ).fetchone()["n"]
            == 2
        )
    # A second request for the same capability and purpose while the grant is active is refused.
    member = membership_of(live, tenant, "reviewer")
    again, _ = purpose_request(live, tenant, applied["scope_id"], member, status=409)
    assert again["reason_code"] == "PURPOSE_GRANT_EXISTS"


@pytest.mark.parametrize(
    "changes,status,reason",
    [
        ({"capability": "programmes.read"}, 403, "NON_DELEGABLE_CAPABILITY"),
        ({"capability": "support.access"}, 403, "NON_DELEGABLE_CAPABILITY"),
        ({"purpose": "QUALIFICATION"}, 403, "PURPOSE_NOT_PERMITTED"),
        ({"expires_at": expiry(120)}, 422, "GRANT_EXPIRY_BOUNDS"),
    ],
)
def test_purpose_grant_requests_are_bounded(live, changes, status, reason):
    tenant, applied = onboarded(live)
    member = membership_of(live, tenant, "reviewer")
    result, _ = purpose_request(live, tenant, applied["scope_id"], member, status=status, **changes)
    assert result["reason_code"] == reason


def test_purpose_grants_never_exceed_the_ceiling_or_touch_the_owner(live):
    tenant, applied = onboarded(live)
    owner = membership_of(live, tenant, "author")
    result, _ = purpose_request(live, tenant, applied["scope_id"], owner, status=403)
    assert result["reason_code"] == "LAST_OWNER_PROTECTED"
    # Fixture tenant A: its administrators' ceilings were never reviewed for purpose-bound
    # capabilities, so the request is beyond the issuer's delegation ceiling.
    members = expect(live.request(live.path("membership-directory") + "?limit=100", actor="admin"), 200)[
        "items"
    ]
    reviewer = next(
        m for m in members if m["identity_id"] == live.fixture["actors"]["reviewer"]["identity_id"]
    )
    scope = next(
        s["object_id"]
        for s in expect(live.request(live.path("access-scopes"), actor="admin"), 200)["items"]
        if s["scope_type"] == "TENANT"
    )
    body = command(
        {
            "membership_id": reviewer["object_id"],
            "expected_membership_revision": reviewer["revision_id"],
            "capability": "privacy.approve",
            "purpose": "DATA_SUBJECT_REQUEST",
            "scope_id": scope,
            "expires_at": expiry(10),
            "reason": "Beyond the ceiling",
        }
    )
    refused = live.request(live.path("purpose-grants"), actor="admin", method="POST", body=body)
    assert expect(refused, 403)["reason_code"] == "DELEGATION_NOT_PERMITTED"
    # Wrong role (the author holds no grant.request); a non-member of the onboarded tenant.
    expect(live.request(live.path("purpose-grants"), actor="author", method="POST", body=body), 403)
    expect(live.request(path(live, tenant, "purpose-grants"), actor="partner", method="POST", body=body), 404)


def test_initial_access_v2_ceiling_covers_purpose_bound_capabilities_without_role_templates(live):
    tenant, applied = onboarded(live, roles=("AUTHOR",))
    roles = expect(live.request(path(live, tenant, "role-templates"), actor="author"), 200)["items"]
    assert {r["name"] for r in roles} == {"TENANT_ADMIN", "AUTHOR"}
    assert not any(c.startswith("privacy") or c == "audit.export" for r in roles for c in r["capabilities"])
    assert "reference-data.manage" in next(r for r in roles if r["name"] == "TENANT_ADMIN")["capabilities"]
    with live.db() as c:
        ceiling = {
            r["capability"]
            for r in c.execute(
                "SELECT capability FROM impact.grant_authority WHERE tenant_id=%s", (tenant,)
            ).fetchall()
        }
    assert {"privacy.approve", "privacy.execute", "audit.export", "forms.draft.create"} <= ceiling
    assert applied["manifest"]["version"] == "initial-access-v2"
