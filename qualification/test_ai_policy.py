"""FR-AI-001 explicit AI enablement and policy on the real API and database (PGlite or native).

Every acceptance scenario of docs/sprints/SPRINT-01.md is exercised here; the provider is always a
synthetic spy. The server AI switch is off in qualification runs, so the advisory gate is driven
in-process with the switch on (as test_ai_enablement_live.py does) and the run's own database.
These tests never reserve an advisory request: tenant A's daily budget stays untouched.
"""
# ruff: noqa: F811

import json
import time
from uuid import uuid4

import psycopg
import pytest
from starlette.requests import Request

from impact_api.ai_enablement import AIEnablement
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database
from test_live_application import expect
from test_measurement import setup, get, action, create, submit, approve  # noqa: F401
from test_period_governance import all_items, complete_period, request_close
from test_reporting import package_data

POLICY = "ai-enablement/policy"


def advisory_rule(**changes):
    """The scenario's rule: INTERNAL data, destination openai-us, purpose "planning advice", English,
    human review, a budget of 100 units and no tools."""
    return {
        "use_case": "ADVISORY_DRAFT",
        "enabled": True,
        "data_classes": ["INTERNAL"],
        "destinations": ["openai-us"],
        "purposes": ["planning advice"],
        "languages": ["en"],
        "review_mode": "HUMAN_REVIEW",
        "budget_units": 100,
        "tools": [],
        **changes,
    }


def current(live, actor="admin"):
    return expect(live.request(live.path(POLICY), actor=actor), 200)


def command(live, rules, expected=None, operation=None):
    return {
        "operation_id": operation or str(uuid4()),
        "expected_version": current(live)["policy_version"] if expected is None else expected,
        "data": {"use_cases": rules},
    }


def put(live, body, actor="admin", token=None):
    if token:
        return live.request(
            live.path(POLICY),
            actor=None,
            method="PUT",
            body=body,
            headers={"Authorization": "Bearer " + token},
        )
    return live.request(live.path(POLICY), actor=actor, method="PUT", body=body)


def enact(live, rules):
    return expect(put(live, command(live, rules)), 200)


def counts(live):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))

        def n(sql):
            return c.execute(sql, (tenant,)).fetchone()["n"]

        return {
            "versions": n("SELECT count(*) AS n FROM impact.ai_policy_version WHERE tenant_id=%s"),
            "rules": n("SELECT count(*) AS n FROM impact.ai_use_case_policy WHERE tenant_id=%s"),
            "reservations": n("SELECT count(*) AS n FROM impact.ai_advisory_request WHERE tenant_id=%s"),
            "results": n("SELECT count(*) AS n FROM impact.ai_advisory_result WHERE tenant_id=%s"),
            "advisory_objects": n(
                "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s "
                "AND object_type='AIAdvisoryRequest'"
            ),
        }


class SpyProvider:
    configured = True
    destination = "openai-us"

    def __init__(self):
        self.calls = 0

    def generate(self, profile, assessment):
        self.calls += 1
        raise AssertionError("A refused request must never reach the provider")


def gate(live, actor="author"):
    """The real AIEnablement on the run's database with the server switch on and a spy provider.
    The fixture author is a Programme Manager holding ai.advisory.request."""
    settings = Settings(**live.config)
    db = Database(settings)
    identity = Auth(settings, db).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token(actor)).encode())],
            }
        )
    )
    provider = SpyProvider()
    return AIEnablement(Service(settings, db), provider, enabled=True), identity, provider


def advisory_body(version, sensitive=False, **extra):
    return {
        "operation_id": str(uuid4()),
        "consent": True,
        "policy_version": version,
        "profile": {
            "sector": "GENERAL",
            "team_size": 8,
            "goal": "Draft a public donor newsletter",
            "data_readiness": "BASIC",
            "ai_experience": "EXPERIMENTING",
            "sensitive_data": sensitive,
        },
        **extra,
    }


def refused(api, identity, live, body):
    with pytest.raises(DomainError) as caught:
        api.advisory(identity, live.fixture["tenant_a"], body, str(uuid4()))
    return caught.value


# Scenario: Enable one use case with its policy


def test_administrator_enables_one_use_case_as_a_new_audited_policy_version(live):
    tenant = live.fixture["tenant_a"]
    before, totals = current(live), counts(live)
    with live.db() as c:
        audits = c.execute(
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND action_type='ai_policy.changed'",
            (tenant,),
        ).fetchone()["n"]
    body = command(live, [advisory_rule()])
    receipt = expect(put(live, body), 200)
    assert receipt["policy_version"] == before["policy_version"] + 1
    assert receipt["policy_version_id"] == receipt["revision_id"]
    assert receipt["business_state"] == "Active" and receipt["operation_id"] == body["operation_id"]
    # A Programme Manager (the fixture author) reads exactly what the "Policy in force" card shows.
    seen = current(live, actor="author")
    assert seen["policy_version"] == receipt["policy_version"]
    assert seen["policy_version_id"] == receipt["policy_version_id"]
    assert seen["use_cases"] == [advisory_rule()]
    assert [rule["use_case"] for rule in seen["use_cases"] if rule["enabled"]] == ["ADVISORY_DRAFT"]
    assert seen["created_by"] == live.fixture["actors"]["admin"]["principal_id"]
    assert seen["reserved_use_cases"] == ["EXTRACTION", "REPORT_DRAFT", "CHAT"]
    # The server switch is off in qualification runs: the policy alone never makes AI available.
    assert seen["server_enabled"] is False and seen["advisory_available"] is False
    catalog = expect(live.request(live.path("ai-enablement/catalog"), actor="author"), 200)
    assert catalog["advisory_available"] is False
    after = counts(live)
    assert after["versions"] == totals["versions"] + 1 and after["rules"] == totals["rules"] + 1
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        numbers = [
            r["version_no"]
            for r in c.execute(
                "SELECT version_no FROM impact.ai_policy_version WHERE tenant_id=%s ORDER BY version_no",
                (tenant,),
            ).fetchall()
        ]
        # Versions are numbered 1..n with no gap: the tenant's first policy was version 1.
        assert numbers == list(range(1, len(numbers) + 1)) and numbers[-1] == receipt["policy_version"]
        stored = c.execute(
            "SELECT * FROM impact.ai_use_case_policy WHERE tenant_id=%s AND policy_version_id=%s",
            (tenant, receipt["policy_version_id"]),
        ).fetchall()
        assert len(stored) == 1
        assert {k: stored[0][k] for k in advisory_rule()} == advisory_rule()
        version = c.execute(
            "SELECT * FROM impact.ai_policy_version WHERE tenant_id=%s AND policy_version_id=%s",
            (tenant, receipt["policy_version_id"]),
        ).fetchone()
        assert str(version["created_by"]) == live.fixture["actors"]["admin"]["principal_id"]
        assert str(version["object_id"]) == receipt["object_id"]
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s AND object_type='AIConfiguration'",
                (tenant,),
            ).fetchone()["n"]
            == 1
        )
        revision = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (tenant, receipt["revision_id"]),
        ).fetchone()
        assert revision["payload"] == {
            "policy_version": receipt["policy_version"],
            "use_cases": [advisory_rule()],
        }
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s "
                "AND action_type='ai_policy.changed'",
                (tenant,),
            ).fetchone()["n"]
            == audits + 1
        )
        assert c.execute(
            "SELECT 1 FROM impact.audit_event_current WHERE tenant_id=%s AND action_type='ai_policy.changed' "
            "AND object_reference=%s AND real_actor_id=%s",
            (tenant, receipt["object_id"], live.fixture["actors"]["admin"]["principal_id"]),
        ).fetchone()
        assert c.execute(
            "SELECT 1 FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_revision'=%s",
            (tenant, receipt["revision_id"]),
        ).fetchone()
        assert c.execute(
            "SELECT 1 FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='update_ai_policy' "
            "AND operation_id=%s",
            (tenant, body["operation_id"]),
        ).fetchone()


def test_policy_history_lists_every_version_newest_first_with_bound_cursors(live):
    first = enact(live, [advisory_rule(budget_units=10)])
    second = enact(live, [advisory_rule(enabled=False)])
    path = live.path(POLICY + "/revisions")
    page = expect(live.request(path + "?limit=1", actor="author"), 200)
    assert [item["policy_version"] for item in page["items"]] == [second["policy_version"]]
    assert page["items"][0]["use_cases"] == [advisory_rule(enabled=False)]
    following = expect(
        live.request(path + "?limit=1&cursor=" + page["next_cursor"], actor="author"),
        200,
    )
    assert [item["policy_version"] for item in following["items"]] == [first["policy_version"]]
    assert following["items"][0]["use_cases"] == [advisory_rule(budget_units=10)]
    # A cursor is bound to its principal and route.
    expect(live.request(path + "?limit=1&cursor=" + page["next_cursor"], actor="admin"), 400)
    expect(live.request(path, actor="other_tenant"), 404)
    expect(live.request(path, actor="revoked"), 404)
    expect(live.request(path + "?limit=0", actor="author"), 422)


def test_policy_reads_are_tenant_fenced_and_need_the_read_capability(live):
    for actor in ("other_tenant", "revoked", "partner", "enumerator"):
        expect(live.request(live.path(POLICY), actor=actor), 404)
    # A tenant A member never reads tenant B's policy: client-supplied tenant IDs are selectors only.
    expect(live.request(live.path(POLICY, tenant=live.fixture["tenant_b"]), actor="author"), 404)


# Scenario: Core workflows complete with AI off


def test_core_workflows_complete_with_every_ai_use_case_off(live, setup):
    enact(live, [advisory_rule(enabled=False), advisory_rule(use_case="CHAT", enabled=False)])
    policy = current(live, actor="author")
    assert not any(rule["enabled"] for rule in policy["use_cases"])
    before = counts(live)
    # A programme is set up and its period closed with an independent review.
    programme, indicator, plan, period, rows, provisional = complete_period(live, setup)
    assert programme["lifecycle_state"] == "Active"
    workflow = request_close(live, programme, period)
    action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Independent close review."},
        actor="reviewer",
    )
    snapshot = next(
        s
        for s in all_items(live, "snapshots")
        if s["data"]["period_id"] == period["object_id"]
        and s["data"].get("programme_id") == programme["object_id"]
    )
    assert snapshot["lifecycle_state"] == "Locked"
    # A report is generated from an approved package.
    report = create(live, "reports", package_data(live))
    approve(live, submit(live, "reports", report))
    assert get(live, "reports", report["object_id"])["lifecycle_state"] == "Approved"
    response = live.request(live.path("reports", report["object_id"]) + "/export")
    assert response.status_code == 200 and "46.36 PERCENT" in response.text
    # No AI reservation, result or provider call happened along the way.
    after = counts(live)
    assert {k: after[k] for k in ("reservations", "results", "advisory_objects")} == {
        k: before[k] for k in ("reservations", "results", "advisory_objects")
    }
    api, identity, provider = gate(live)
    error = refused(api, identity, live, advisory_body(policy["policy_version"]))
    assert (error.status, error.code, error.reason) == (503, "SERVICE_UNAVAILABLE", "AI_USE_CASE_DISABLED")
    assert provider.calls == 0 and counts(live)["reservations"] == before["reservations"]
    assert api.catalog(identity, live.fixture["tenant_a"])["advisory_available"] is False


# Scenario: Reject a request outside the policy


def test_sensitive_request_outside_the_policy_is_refused_before_reservation(live):
    receipt = enact(live, [advisory_rule()])
    before = counts(live)
    api, identity, provider = gate(live)
    error = refused(api, identity, live, advisory_body(receipt["policy_version"], sensitive=True))
    assert (error.status, error.code, error.reason) == (422, "VALIDATION_FAILED", "AI_POLICY_BLOCKED")
    assert "confidential data is above the highest allowed data class" in error.message
    assert provider.calls == 0
    assert counts(live) == before
    # With the switch on and ADVISORY_DRAFT enabled, the catalogue reports advisory as available.
    assert api.catalog(identity, live.fixture["tenant_a"])["advisory_available"] is True


def test_destination_language_and_budget_rules_refuse_before_reservation(live):
    for rule, fragment in [
        ({"destinations": ["openai-us"], "languages": ["hi"]}, "language (en) is not covered"),
        ({"budget_units": 0}, "no budget is approved"),
    ]:
        receipt = enact(live, [advisory_rule(**rule)])
        before = counts(live)
        api, identity, provider = gate(live)
        error = refused(api, identity, live, advisory_body(receipt["policy_version"]))
        assert (error.status, error.reason) == (422, "AI_POLICY_BLOCKED") and fragment in error.message
        assert provider.calls == 0 and counts(live) == before


def test_allowed_classes_are_a_ceiling_and_an_advisory_ceiling_below_internal_is_refused(live):
    before = counts(live)
    refusal = expect(put(live, command(live, [advisory_rule(data_classes=["PUBLIC"])])), 422)
    assert refusal["reason_code"] == "AI_DATA_CLASS_TOO_LOW"
    assert counts(live)["versions"] == before["versions"]
    # CONFIDENTIAL allows the sensitive (CONFIDENTIAL) and ordinary (INTERNAL) brief. An unmet
    # language rule keeps the request from being reserved, and the refusal names only that rule.
    receipt = enact(live, [advisory_rule(data_classes=["CONFIDENTIAL"], languages=["hi"])])
    assert current(live, actor="author")["use_cases"][0]["data_classes"] == ["CONFIDENTIAL"]
    before = counts(live)
    api, identity, provider = gate(live)
    for sensitive in (True, False):
        error = refused(api, identity, live, advisory_body(receipt["policy_version"], sensitive=sensitive))
        assert error.reason == "AI_POLICY_BLOCKED" and "language (en)" in error.message
        assert "data class" not in error.message
    assert provider.calls == 0 and counts(live) == before


# Scenario: Reject a request made against an old policy


def test_request_made_against_an_old_policy_version_is_refused(live):
    old = enact(live, [advisory_rule()])
    new = enact(live, [advisory_rule(budget_units=50)])
    assert new["policy_version"] == old["policy_version"] + 1
    before = counts(live)
    api, identity, provider = gate(live)
    error = refused(api, identity, live, advisory_body(old["policy_version"]))
    assert (error.status, error.code, error.reason) == (409, "CONFLICT_VERSION", "AI_POLICY_CHANGED")
    assert provider.calls == 0 and counts(live) == before


# Scenario: Reject implicit tools


def test_tools_are_never_implicit_or_grantable(live):
    before = counts(live)
    tool = put(live, command(live, [advisory_rule(tools=["web_search"])]))
    assert expect(tool, 422)["code"] == "VALIDATION_FAILED"
    chat = expect(put(live, command(live, [advisory_rule(), advisory_rule(use_case="CHAT")])), 422)
    assert chat["reason_code"] == "AI_USE_CASE_RESERVED"
    assert counts(live)["versions"] == before["versions"]
    # CHAT may be recorded only as off and with an empty tools list.
    receipt = enact(live, [advisory_rule(), advisory_rule(use_case="CHAT", enabled=False)])
    seen = current(live, actor="author")
    assert [rule["tools"] for rule in seen["use_cases"]] == [[], []]
    before = counts(live)
    api, identity, provider = gate(live)
    error = refused(api, identity, live, advisory_body(receipt["policy_version"], tools=["web_search"]))
    assert (error.status, error.reason) == (422, "AI_POLICY_BLOCKED")
    assert "tools are not allowed" in error.message
    assert provider.calls == 0 and counts(live) == before
    # Over HTTP the closed request refuses a malformed tool list before anything else runs.
    malformed = advisory_body(receipt["policy_version"], tools="web_search")
    response = live.request(live.path("ai-enablement/advisory"), actor="admin", method="POST", body=malformed)
    assert expect(response, 422)["code"] == "VALIDATION_FAILED"
    assert counts(live) == before


# Scenario: Reject policy change by a non-administrator or without fresh sign-in


def test_policy_change_refused_without_administration_or_fresh_sign_in(live):
    before = counts(live)
    body = command(live, [advisory_rule()])
    for actor, status in [
        ("reviewer", 403),  # MEL Manager (MEL_ADMIN): reads the policy, cannot change it
        ("author", 403),  # Programme Manager
        ("partner", 404),
        ("enumerator", 404),
        ("revoked", 404),
        ("other_tenant", 404),
    ]:
        refusal = expect(put(live, {**body, "operation_id": str(uuid4())}, actor=actor), status)
        if status == 403:
            assert refusal["code"] == "POLICY_DENIED"
    admin = live.fixture["actors"]["admin"]["identity_id"]
    stale = expect(put(live, body, token=live.signed(admin, auth_time=time.time() - 400)), 403)
    assert (stale["code"], stale["reason_code"]) == ("ASSURANCE_REQUIRED", "FRESH_AUTHENTICATION_REQUIRED")
    edge = expect(put(live, body, token=live.signed(admin, auth_time=time.time() - 301)), 403)
    assert edge["reason_code"] == "FRESH_AUTHENTICATION_REQUIRED"
    assert counts(live) == before
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        # Every refusal inside authorisation is recorded (0.27.0 denial auditing).
        assert c.execute(
            "SELECT 1 FROM impact.access_denial WHERE tenant_id=%s AND principal_id=%s AND operation_id='update_ai_policy'",
            (live.fixture["tenant_a"], live.fixture["actors"]["reviewer"]["principal_id"]),
        ).fetchone()
    # The same command with a fresh sign-in succeeds once.
    assert expect(put(live, body), 200)["policy_version"] == body["expected_version"] + 1
    assert counts(live)["versions"] == before["versions"] + 1


def test_stale_version_exact_retry_changed_payload_and_closed_command(live):
    base = current(live)["policy_version"]
    for expected in sorted({base + 1, base + 2} | ({base - 1} if base else set())):
        stale = expect(put(live, command(live, [advisory_rule()], expected=expected)), 409)
        assert stale["reason_code"] == "AI_POLICY_CHANGED"
    before = counts(live)
    body = command(live, [advisory_rule(purposes=["planning advice", "board briefing"])])
    first = expect(put(live, body), 200)
    assert expect(put(live, body), 200) == first
    assert counts(live)["versions"] == before["versions"] + 1
    changed = json.loads(json.dumps(body))
    changed["data"]["use_cases"][0]["budget_units"] = 7
    assert expect(put(live, changed), 409)["code"] == "CONFLICT_OPERATION"
    for bad in [
        {**command(live, [advisory_rule()]), "created_by": live.fixture["actors"]["admin"]["principal_id"]},
        {**command(live, [advisory_rule()]), "expected_version": "1"},
        command(live, [{**advisory_rule(), "approved": True}]),
        command(live, [advisory_rule(destinations=["openai-eu"])]),
        command(live, [advisory_rule(data_classes=[])]),
        command(live, [advisory_rule(), advisory_rule()]),
    ]:
        expect(put(live, bad), 422)
    duplicate = live.request(
        live.path(POLICY),
        actor="admin",
        method="PUT",
        content=b'{"operation_id":"' + str(uuid4()).encode() + b'","operation_id":"x"}',
        headers={"Content-Type": "application/json"},
    )
    expect(duplicate, 400)
    assert counts(live)["versions"] == before["versions"] + 1


# Database guarantees visible on any database (row fences need real roles: test_ai_policy_live.py)


def refused_statement(live, error, statement, values):
    """Run one statement that the database must refuse, inside its own savepoint."""
    with live.db() as c:
        with pytest.raises(error):
            with c.transaction():
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                c.execute(statement, values)


def test_policy_rows_are_insert_only_and_checked_by_the_database(live):
    receipt = enact(live, [advisory_rule()])
    tenant = live.fixture["tenant_a"]
    for statement in [
        "UPDATE impact.ai_policy_version SET version_no=version_no WHERE tenant_id=%s",
        "DELETE FROM impact.ai_policy_version WHERE tenant_id=%s",
        "UPDATE impact.ai_use_case_policy SET budget_units=budget_units WHERE tenant_id=%s",
        "DELETE FROM impact.ai_use_case_policy WHERE tenant_id=%s",
    ]:
        refused_statement(live, psycopg.errors.InsufficientPrivilege, statement, (tenant,))
    insert = (
        "INSERT INTO impact.ai_use_case_policy(tenant_id,policy_version_id,use_case,enabled,data_classes,"
        "destinations,purposes,languages,review_mode,budget_units,tools) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    valid = [tenant, receipt["policy_version_id"], "CHAT", False, [], [], [], [], "HUMAN_REVIEW", 0, []]
    for change in [
        {3: True},  # a reserved use case enabled
        {10: ["web_search"]},  # any tool
        {5: ["openai-eu"]},  # an unreviewed destination
        {4: ["SECRET"]},  # an unknown data class
        {7: ["english"]},  # not a language tag
        {9: -1},  # a negative budget
        {2: "ADVISORY_DRAFT", 3: True},  # enabled without class, destination, purpose or language
    ]:
        values = list(valid)
        for index, value in change.items():
            values[index] = value
        refused_statement(live, psycopg.errors.CheckViolation, insert, values)
    # One AIConfiguration object per tenant.
    refused_statement(
        live,
        psycopg.errors.UniqueViolation,
        "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,lifecycle_state,"
        "classification,owner_id,created_at,created_by,updated_at) "
        "VALUES(%s,%s,'AIConfiguration',%s,'Active','INTERNAL',NULL,now(),%s,now())",
        (tenant, str(uuid4()), str(uuid4()), live.fixture["actors"]["admin"]["principal_id"]),
    )
    # A new advisory reservation must record its policy version (NOT VALID: earlier rows keep NULL).
    refused_statement(
        live,
        psycopg.errors.CheckViolation,
        "INSERT INTO impact.ai_advisory_request(tenant_id,request_id,object_id,principal_id,fingerprint,"
        "reserved_at) VALUES(%s,%s,%s,%s,%s,now())",
        (tenant, str(uuid4()), str(uuid4()), live.fixture["actors"]["admin"]["principal_id"], b"x" * 32),
    )
