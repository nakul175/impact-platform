"""API/security cases for the integrated internal advice candidate.

Evidence is named separately and does not establish hosted acceptance.
Synthetic fixture metadata adaptations never weaken the application participant rule.
"""

from contextlib import contextmanager
import base64
import json
import os
import time
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from jsonschema import Draft202012Validator, FormatChecker

from impact_api.service import Service
from impact_api.config import Settings
from impact_api.human_advice_contracts import PRIVATE_PROOF_FIELDS, public_schema
from test_ai_adoption_plans import plan
from test_ai_adoption_plans_live import save as save_plan
from test_human_advice_unit import creation
from test_live_application import cmd, expect

ROUTE = "ai-enablement/human-advice"


def assert_public_case(case):
    Draft202012Validator(public_schema(), format_checker=FormatChecker()).validate(case["data"])
    assert not PRIVATE_PROOF_FIELDS.intersection(case["data"])
    for decision in ("declaration", "assignment"):
        assert case["data"][decision] is None or "authenticated_at" not in case["data"][decision]


def assert_public_receipt(receipt):
    assert set(receipt) == {
        "object_id",
        "revision_id",
        "business_state",
        "operation_id",
        "correlation_id",
        "saved_at",
    }


def open_case(live, data=None, status=201):
    anchor = save_plan(live)
    request = creation()
    request["data"].update(
        context_plan_id=anchor["object_id"],
        context_plan_revision=anchor["revision_id"],
        adviser_membership_id=live.fixture["actors"]["reviewer"]["membership_id"],
    )
    request["data"].update(data or {})
    receipt = expect(live.request(live.path(ROUTE), actor="admin", method="POST", body=request), status)
    if status == 201:
        assert_public_receipt(receipt)
    return receipt, request, anchor


def act(live, case, action, data, actor="admin", status=200, request=None):
    body = request or cmd(data, case["revision_id"])
    receipt = expect(
        live.request(
            live.path(ROUTE, case["object_id"]) + "/actions/" + action, actor=actor, method="POST", body=body
        ),
        status,
    )
    if status == 200:
        assert_public_receipt(receipt)
    return receipt, body


def declare(live, case, conflict="NONE", accepted=True):
    return act(
        live,
        case,
        "declare-scope",
        {
            "conflict": conflict,
            "details": "Synthetic accountable conflict declaration",
            "scope_accepted": accepted,
        },
        "reviewer",
    )


def assign(live, case):
    declared, _ = declare(live, case)
    assigned, _ = act(
        live,
        declared,
        "assign",
        {"declaration_revision_id": declared["revision_id"], "sharing_confirmed": True},
    )
    return assigned


def advise(live, case):
    return act(
        live,
        case,
        "advise",
        {
            "advice": "Use synthetic text, verify sources and have a person review the output.",
            "actions": [{"description": "Prepare acceptance examples", "responsibility": "REQUESTER"}],
        },
        "reviewer",
    )


@contextmanager
def changed_grant(live, actor, capability):
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"][actor]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        rows = c.execute(
            "SELECT object_id,purpose FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability=%s AND purpose IS NULL",
            (tenant, principal, capability),
        ).fetchall()
        assert rows
        c.execute(
            "UPDATE impact.grant_current SET purpose='SYNTHETIC_ADVICE_DISABLED' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
            (tenant, [row["object_id"] for row in rows]),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            for row in rows:
                c.execute(
                    "UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s",
                    (row["purpose"], tenant, row["object_id"]),
                )


@contextmanager
def expired_member(live, actor="reviewer"):
    tenant = live.fixture["tenant_a"]
    membership = live.fixture["actors"][actor]["membership_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        original = c.execute(
            "SELECT expires_at FROM impact.membership_current WHERE tenant_id=%s AND object_id=%s",
            (tenant, membership),
        ).fetchone()["expires_at"]
        c.execute(
            "UPDATE impact.membership_current SET expires_at=now()-interval '1 second' WHERE tenant_id=%s AND object_id=%s",
            (tenant, membership),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(
                "UPDATE impact.membership_current SET expires_at=%s WHERE tenant_id=%s AND object_id=%s",
                (original, tenant, membership),
            )


def test_real_case_requires_exact_assignment_and_requester_closure_then_ends_adviser_access(live):
    opened, request, _ = open_case(live)
    path = live.path(ROUTE, opened["object_id"])
    assert opened == expect(live.request(live.path(ROUTE), actor="admin", method="POST", body=request), 201)
    invitation = expect(live.request(path, actor="reviewer"), 200)
    assert_public_case(invitation)
    assert invitation["problem"] is None and "problem" not in invitation["data"]
    assert request["data"]["problem"] not in json.dumps(invitation)
    own = expect(live.request(path, actor="admin"), 200)
    assert_public_case(own)
    assert own["problem"] == request["data"]["problem"]
    active = assign(live, opened)
    assert expect(live.request(path, actor="reviewer"), 200)["problem"] == own["problem"]
    draft, advise_body = advise(live, active)
    assert draft == act(live, active, "advise", {}, "reviewer", request=advise_body)[0]
    current = expect(live.request(path, actor="admin"), 200)
    assert_public_case(current)
    close = {
        "advice_revision_id": draft["revision_id"],
        "acknowledged_action_ids": [item["action_id"] for item in current["data"]["advice"]["actions"]],
        "closure_reason": "Advice acknowledged; organisation retains every decision.",
    }
    closed, close_body = act(live, draft, "close", close)
    assert closed["business_state"] == "Closed"
    assert closed == act(live, draft, "close", {}, request=close_body)[0]
    frozen = expect(live.request(path, actor="admin"), 200)
    assert_public_case(frozen)
    assert frozen["data"]["closure"]["advice_revision_id"] == draft["revision_id"]
    assert frozen["data"]["advice"] == current["data"]["advice"]
    for suffix in ("", "/revisions", "/revisions/" + draft["revision_id"]):
        expect(live.request(path + suffix, actor="reviewer"), 404)
    act(live, active, "advise", {}, "reviewer", status=404, request=advise_body)
    act(live, closed, "cancel", {"reason": "Cannot mutate terminal advice"}, status=409)
    assert not any(
        item["object_id"] == opened["object_id"]
        for item in expect(live.request(live.path(ROUTE), actor="reviewer"), 200)["items"]
    )


def test_current_historical_and_list_responses_omit_identity_proofs_but_store_exact_consent(live):
    opened, request, _ = open_case(live)
    active = assign(live, opened)
    path = live.path(ROUTE, opened["object_id"])
    for actor in ("admin", "reviewer"):
        current = expect(live.request(path, actor=actor), 200)
        assert_public_case(current)
        assert current["problem"] == request["data"]["problem"]
        historical = expect(live.request(path + "/revisions/" + opened["revision_id"], actor=actor), 200)
        assert_public_case(historical)
        assert historical["problem"] == (None if actor == "reviewer" else request["data"]["problem"])
        page = expect(live.request(live.path(ROUTE), actor=actor), 200)
        for item in page["items"]:
            assert_public_case(item)
        assert opened["object_id"] in [item["object_id"] for item in page["items"]]
        history = expect(live.request(path + "/revisions", actor=actor), 200)
        assert active["revision_id"] in [item["revision_id"] for item in history["items"]]
        for item in history["items"]:
            frozen = expect(live.request(path + "/revisions/" + item["revision_id"], actor=actor), 200)
            assert_public_case(frozen)
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        payload = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
            (live.fixture["tenant_a"], active["object_id"], active["revision_id"]),
        ).fetchone()["payload"]
        assert PRIVATE_PROOF_FIELDS <= set(payload)
        for decision in ("declaration", "assignment"):
            assert payload[decision]["authenticated_at"]
        assert payload["requester_natural_id"] == live.fixture["actors"]["admin"]["natural_identity_id"]
        assert payload["adviser_natural_id"] == live.fixture["actors"]["reviewer"]["natural_identity_id"]
        assert payload["problem_sha256"]


@pytest.mark.parametrize("actor", ["author", "partner"])
def test_nonparticipants_cannot_read_cases_history_receipts_or_list_entries(live, actor):
    case, _, _ = open_case(live)
    path = live.path(ROUTE, case["object_id"])
    for suffix in ("", "/revisions", "/revisions/" + case["revision_id"]):
        expect(live.request(path + suffix, actor=actor), 404)
    act(live, case, "cancel", {"reason": "Nonparticipant cannot close"}, actor, 404)
    result = live.request(live.path(ROUTE), actor=actor)
    if result.status_code == 200:
        assert case["object_id"] not in [item["object_id"] for item in result.json()["items"]]
    else:
        expect(result, 404)
    expect(
        live.request(
            path,
            actor=actor,
            method="GET",
            params={"principal_id": live.fixture["actors"]["admin"]["principal_id"]},
        ),
        404,
    )


def test_an_adviser_declared_conflict_is_preserved_without_sharing_the_private_brief(live):
    case, request, _ = open_case(live)
    declared, _ = declare(live, case, "DECLARED", False)
    own = expect(live.request(live.path(ROUTE, case["object_id"]), actor="admin"), 200)
    assert own["data"]["declaration"]["conflict"] == "DECLARED"
    act(
        live,
        declared,
        "assign",
        {"declaration_revision_id": declared["revision_id"], "sharing_confirmed": True},
        status=403,
    )
    invitation = expect(live.request(live.path(ROUTE, case["object_id"]), actor="reviewer"), 200)
    assert invitation["problem"] is None and request["data"]["problem"] not in json.dumps(invitation)


@pytest.mark.parametrize(
    "mutation", ["unknown_recipient", "record_reference", "server_actor", "false_consent", "duplicate_json"]
)
def test_closed_bodies_never_disclose_records_or_create_financial_external_actions(live, mutation):
    _, original, anchor = open_case(live)
    body = {**original, "operation_id": str(uuid4()), "data": dict(original["data"])}
    if mutation == "duplicate_json":
        raw = json.dumps(body)
        raw = raw.replace(
            '"invitation_consent": true', '"invitation_consent": true, "invitation_consent": true'
        )
        response = live.client.post(
            live.path(ROUTE),
            content=raw,
            headers={"Authorization": "Bearer " + live.token("admin"), "Content-Type": "application/json"},
        )
        expect(response, 400)
        return
    if mutation == "false_consent":
        body["data"]["invitation_consent"] = False
    else:
        body["data"][
            {
                "unknown_recipient": "recipient_ids",
                "record_reference": "programme_id",
                "server_actor": "requester_principal_id",
            }[mutation]
        ] = str(uuid4())
    expect(live.request(live.path(ROUTE), actor="admin", method="POST", body=body), 422)
    assert anchor["object_id"]


def test_same_natural_person_or_missing_named_member_cannot_be_the_adviser(live):
    open_case(live, {"adviser_membership_id": live.fixture["actors"]["admin"]["membership_id"]}, 403)
    open_case(live, {"adviser_membership_id": str(uuid4())}, 404)
    open_case(live, {"adviser_membership_id": live.fixture["actors"]["other_tenant"]["membership_id"]}, 404)


def test_distinct_accounts_for_the_same_natural_person_still_fail_independence(live):
    adviser = live.fixture["actors"]["reviewer"]
    with live.db() as c:
        original = c.execute(
            "SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s",
            (adviser["identity_id"],),
        ).fetchone()["natural_identity_id"]
        c.execute(
            "UPDATE impact.auth_identity SET natural_identity_id=%s WHERE identity_id=%s",
            (live.fixture["actors"]["admin"]["natural_identity_id"], adviser["identity_id"]),
        )
    try:
        open_case(live, status=403)
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.auth_identity SET natural_identity_id=%s WHERE identity_id=%s",
                (original, adviser["identity_id"]),
            )


def test_renewed_adviser_authority_invalidates_an_old_scope_consent(live):
    opened, _, _ = open_case(live)
    declared, _ = declare(live, opened)
    tenant = live.fixture["tenant_a"]
    adviser = live.fixture["actors"]["reviewer"]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        original = c.execute(
            "SELECT auth_not_before FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s",
            (tenant, adviser),
        ).fetchone()["auth_not_before"]
        c.execute(
            "UPDATE impact.tenant_principal SET auth_not_before=now() WHERE tenant_id=%s AND principal_id=%s",
            (tenant, adviser),
        )
    try:
        error, _ = act(
            live,
            declared,
            "assign",
            {"declaration_revision_id": declared["revision_id"], "sharing_confirmed": True},
            status=409,
        )
        assert error["reason_code"] == "CASE_CONSENT_CHANGED"
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(
                "UPDATE impact.tenant_principal SET auth_not_before=%s WHERE tenant_id=%s AND principal_id=%s",
                (original, tenant, adviser),
            )


def test_tenant_selectors_never_make_a_case_or_anchor_visible_elsewhere(live):
    case, _, anchor = open_case(live)
    other = live.fixture["tenant_b"]
    for suffix in ("", "/revisions", "/revisions/" + case["revision_id"]):
        expect(live.request(live.path(ROUTE, case["object_id"], other) + suffix, actor="other_tenant"), 404)
    # This principal is authorised to its own tenant's empty advice directory;
    # an invalid cursor is a 400 after that independent current-authority gate.
    own_directory = expect(live.request(live.path(ROUTE, tenant=other), actor="other_tenant"), 200)
    assert case["object_id"] not in [item["object_id"] for item in own_directory["items"]]
    expect(
        live.request(live.path(ROUTE, tenant=other), actor="other_tenant", params={"cursor": str(uuid4())}),
        400,
    )
    expect(
        live.request(
            live.path(ROUTE, tenant=other) + "/eligible-peers",
            actor="other_tenant",
            params={"context_plan_id": anchor["object_id"]},
        ),
        404,
    )


@pytest.mark.parametrize("capability", ["ai.enablement.read", "ai.enablement.manage"])
def test_lost_current_authority_prevents_receipt_replay_and_assignment(live, capability):
    case, _, _ = open_case(live)
    declared, body = declare(live, case)
    with changed_grant(live, "reviewer", capability):
        act(live, case, "declare-scope", {}, "reviewer", 404, request=body)
        act(
            live,
            declared,
            "assign",
            {"declaration_revision_id": declared["revision_id"], "sharing_confirmed": True},
            status=404,
        )
        if capability == "ai.enablement.read":
            expect(live.request(live.path(ROUTE, case["object_id"]), actor="reviewer"), 404)
    act(live, declared, "cancel", {"reason": "Requester can end the case"})


def test_expired_adviser_is_hidden_and_cannot_authorise_assignment_but_requester_can_cancel(live):
    case, _, _ = open_case(live)
    declared, body = declare(live, case)
    with expired_member(live):
        expect(live.request(live.path(ROUTE, case["object_id"]), actor="reviewer"), 404)
        act(live, case, "declare-scope", {}, "reviewer", 404, request=body)
        act(
            live,
            declared,
            "assign",
            {"declaration_revision_id": declared["revision_id"], "sharing_confirmed": True},
            status=404,
        )
        cancelled, _ = act(live, declared, "cancel", {"reason": "Named member's authority expired"})
        assert cancelled["business_state"] == "Cancelled"


def test_plan_edit_makes_the_old_case_read_only_until_requester_cancels(live):
    opened, _, anchor = open_case(live)
    active = assign(live, opened)
    data = plan()
    data["title"] = "Changed scope requires a new advice case"
    expect(
        live.request(
            live.path("ai-enablement/plans", anchor["object_id"]),
            actor="admin",
            method="PUT",
            body=cmd(data, anchor["revision_id"]),
        ),
        200,
    )
    assert not expect(live.request(live.path(ROUTE, opened["object_id"]), actor="admin"), 200)[
        "context_current"
    ]
    act(
        live,
        active,
        "advise",
        {"advice": "Cannot apply old consent to new plan scope", "actions": []},
        "reviewer",
        409,
    )
    act(live, active, "cancel", {"reason": "Open a new case for the changed plan"})


def test_exact_declaration_advice_and_complete_action_ids_are_required(live):
    opened, _, _ = open_case(live)
    declared, _ = declare(live, opened)
    act(
        live,
        declared,
        "assign",
        {"declaration_revision_id": opened["revision_id"], "sharing_confirmed": True},
        status=409,
    )
    active, _ = act(
        live,
        declared,
        "assign",
        {"declaration_revision_id": declared["revision_id"], "sharing_confirmed": True},
    )
    draft, _ = advise(live, active)
    current = expect(live.request(live.path(ROUTE, draft["object_id"]), actor="admin"), 200)
    action_ids = [item["action_id"] for item in current["data"]["advice"]["actions"]]
    act(
        live,
        draft,
        "close",
        {
            "advice_revision_id": active["revision_id"],
            "acknowledged_action_ids": action_ids,
            "closure_reason": "Stale draft",
        },
        status=409,
    )
    act(
        live,
        draft,
        "close",
        {
            "advice_revision_id": draft["revision_id"],
            "acknowledged_action_ids": [],
            "closure_reason": "Incomplete acknowledgement",
        },
        status=403,
    )


@pytest.mark.parametrize("native", [False, True])
def test_participant_context_clears_on_transaction_end_and_missing_reused_context_hides_rows(live, native):
    dsn = os.environ.get("IMPACT_LOGIN_DSN_APP") if native else None
    if native and not dsn:
        pytest.skip("Provisioned native app login required; PGlite evidence is separately scoped")
    case, _, _ = open_case(live)
    tenant = live.fixture["tenant_a"]
    connection = psycopg.connect(dsn, prepare_threshold=None) if native else live.db()
    try:
        with connection.transaction():
            connection.execute("SET LOCAL ROLE impact_app")
            connection.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            assert (
                connection.execute(
                    "SELECT object_id FROM impact.human_advice_case_current WHERE object_id=%s",
                    (case["object_id"],),
                ).fetchone()
                is None
            )
            connection.execute(
                "SELECT set_config('impact.human_advice_principal',%s,true)",
                (live.fixture["actors"]["admin"]["principal_id"],),
            )
            assert connection.execute(
                "SELECT object_id FROM impact.human_advice_case_current WHERE object_id=%s",
                (case["object_id"],),
            ).fetchone()
        with connection.transaction():
            connection.execute("SET LOCAL ROLE impact_app")
            connection.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            assert (
                connection.execute(
                    "SELECT object_id FROM impact.human_advice_case_current WHERE object_id=%s",
                    (case["object_id"],),
                ).fetchone()
                is None
            )
            assert (
                connection.execute(
                    "SELECT payload FROM impact.object_revision WHERE object_id=%s", (case["object_id"],)
                ).fetchone()
                is None
            )
    finally:
        connection.close()


@pytest.mark.parametrize("who", ["admin", "reviewer", "author"])
def test_direct_runtime_rows_and_private_brief_follow_the_case_participant_boundary(live, who):
    case, _, _ = open_case(live)
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        c.execute(
            "SELECT set_config('impact.human_advice_principal',%s,true)",
            (live.fixture["actors"][who]["principal_id"],),
        )
        rows = c.execute(
            "SELECT payload FROM impact.object_revision WHERE object_id=%s", (case["object_id"],)
        ).fetchall()
        assert bool(rows) == (who in {"admin", "reviewer"})
        assert all("problem" not in row["payload"] for row in rows)
        authors = c.execute(
            "SELECT natural_identity_id FROM impact.object_natural_author WHERE object_id=%s",
            (case["object_id"],),
        ).fetchall()
        assert bool(authors) == (who in {"admin", "reviewer"})
        brief = c.execute(
            "SELECT problem FROM impact.human_advice_private_brief WHERE object_id=%s", (case["object_id"],)
        ).fetchone()
        assert bool(brief) == (who == "admin")
        audits = c.execute(
            "SELECT object_id FROM impact.audit_event_current WHERE object_reference=%s", (case["object_id"],)
        ).fetchall()
        assert bool(audits) == (who in {"admin", "reviewer"})
        audit_revisions = c.execute(
            "SELECT payload FROM impact.object_revision WHERE object_type='AuditEvent' AND payload->>'object_reference'=%s",
            (case["object_id"],),
        ).fetchall()
        assert bool(audit_revisions) == (who in {"admin", "reviewer"})
        receipts = c.execute(
            "SELECT operation_id FROM impact.operation_receipt WHERE command_type='create_human_advice_case' AND outcome->>'object_id'=%s",
            (case["object_id"],),
        ).fetchall()
        assert bool(receipts) == (who in {"admin", "reviewer"})
        events = c.execute(
            "SELECT event_id FROM impact.outbox_event WHERE payload->>'aggregate_type'='HumanAdviceCase' AND payload->>'aggregate_id'=%s",
            (case["object_id"],),
        ).fetchall()
        assert bool(events) == (who in {"admin", "reviewer"})
        assert all(
            c.execute(
                "SELECT channel FROM impact.outbox_delivery WHERE event_id=%s", (event["event_id"],)
            ).fetchone()["channel"]
            is None
            for event in events
        )


def test_case_cursor_cannot_be_forged_or_reused_by_another_actor_or_route(live):
    first, _, _ = open_case(live)
    open_case(live)
    page = expect(live.request(live.path(ROUTE), actor="admin", params={"limit": 1}), 200)
    cursor = page["next_cursor"]
    assert cursor
    expect(
        live.request(
            live.path(ROUTE),
            actor="admin",
            params={"limit": 1, "cursor": cursor[:-1] + ("1" if cursor[-1] != "1" else "2")},
        ),
        400,
    )
    expect(live.request(live.path(ROUTE), actor="author"), 200)
    expect(live.request(live.path(ROUTE), actor="author", params={"cursor": cursor}), 400)
    other_path = live.path(ROUTE, tenant=live.fixture["tenant_b"])
    expect(live.request(other_path, actor="other_tenant"), 200)
    expect(live.request(other_path, actor="other_tenant", params={"cursor": cursor}), 400)
    expect(
        live.request(
            live.path(ROUTE, first["object_id"]) + "/revisions", actor="admin", params={"cursor": cursor}
        ),
        400,
    )
    act(live, first, "cancel", {"reason": "Visibility changed"})
    expect(live.request(live.path(ROUTE), actor="admin", params={"cursor": cursor}), 400)


def test_eligible_peers_are_minimal_current_colleagues_with_separate_directory_authority(live):
    anchor = save_plan(live)
    path = live.path(ROUTE) + "/eligible-peers"
    query = {"context_plan_id": anchor["object_id"]}
    peers = expect(live.request(path, actor="admin", params=query), 200)
    assert all(set(item) == {"membership_id", "display_name"} for item in peers["items"])
    memberships = {item["membership_id"] for item in peers["items"]}
    assert live.fixture["actors"]["reviewer"]["membership_id"] in memberships
    assert live.fixture["actors"]["admin"]["membership_id"] not in memberships
    assert live.fixture["actors"]["partner"]["membership_id"] not in memberships
    # An ordinary manager with current AI read/manage still cannot browse members.
    expect(live.request(path, actor="reviewer", params=query), 404)
    expect(live.request(path, actor="reviewer", params={"context_plan_id": str(uuid4())}), 404)
    for cap in ("memberships.read", "ai.enablement.read", "ai.enablement.manage"):
        with changed_grant(live, "admin", cap):
            expect(live.request(path, actor="admin", params=query), 404)


@pytest.mark.parametrize("change", ["read", "manage", "expired"])
def test_colleague_selector_rechecks_candidate_scope_and_current_membership_each_page(live, change):
    anchor = save_plan(live)
    path = live.path(ROUTE) + "/eligible-peers"
    query = {"context_plan_id": anchor["object_id"]}
    adaptation = (
        expired_member(live, "reviewer")
        if change == "expired"
        else changed_grant(live, "reviewer", "ai.enablement." + change)
    )
    with adaptation:
        peers = expect(live.request(path, actor="admin", params=query), 200)
        assert live.fixture["actors"]["reviewer"]["membership_id"] not in {
            item["membership_id"] for item in peers["items"]
        }


def test_peer_cursors_are_signed_principal_route_anchor_expiry_and_visibility_bound(live):
    anchor = save_plan(live)
    other = save_plan(live)
    path = live.path(ROUTE) + "/eligible-peers"
    query = {"context_plan_id": anchor["object_id"], "limit": 1}
    page = expect(live.request(path, actor="admin", params=query), 200)
    cursor = page["next_cursor"]
    assert cursor
    # Custody alone does not give this OWNER the saved-plan management gate;
    # authority is rechecked before returning cursor-validation information.
    expect(live.request(path, actor="owner", params=query), 404)
    expect(live.request(path, actor="owner", params={**query, "cursor": cursor}), 404)
    for actor, params in [
        ("admin", {**query, "cursor": cursor[:-1] + ("1" if cursor[-1] != "1" else "2")}),
        ("admin", {**query, "context_plan_id": other["object_id"], "cursor": cursor}),
    ]:
        expect(live.request(path, actor=actor, params=params), 400)
    expect(live.request(live.path(ROUTE), actor="admin", params={"cursor": cursor}), 400)
    encoded = cursor.split(".")[0]
    payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * ((-len(encoded)) % 4)))
    payload["expires"] = int(time.time()) - 1
    expired = Service.cursor(SimpleNamespace(s=Settings(**live.config)), payload)
    expect(live.request(path, actor="admin", params={**query, "cursor": expired}), 400)
    with expired_member(live, "reviewer"):
        expect(live.request(path, actor="admin", params={**query, "cursor": cursor}), 400)


@pytest.mark.parametrize("name", ["APP", "WORKER", "IDENTITY", "PLATFORM", "EXECUTOR"])
def test_native_runtime_logins_cannot_read_private_cases_or_audit_receipt_event_pointers_without_context(
    live, name
):
    dsn = os.environ.get("IMPACT_LOGIN_DSN_" + name)
    if not dsn:
        pytest.skip("Actual provisioned native login is required for runtime role evidence")
    case, _, _ = open_case(live)
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        event = c.execute(
            "SELECT event_id FROM impact.outbox_event WHERE payload->>'aggregate_type'='HumanAdviceCase' AND payload->>'aggregate_id'=%s",
            (case["object_id"],),
        ).fetchone()["event_id"]
        c.execute(
            "INSERT INTO impact.consumer_receipt(tenant_id,consumer,event_id,applied_at) VALUES(%s,'synthetic-human-advice-pointer-test',%s,now())",
            (live.fixture["tenant_a"], event),
        )
    queries = [
        ("SELECT object_id FROM impact.object_registry WHERE object_id=%s", case["object_id"]),
        ("SELECT revision_id FROM impact.object_revision WHERE object_id=%s", case["object_id"]),
        (
            "SELECT natural_identity_id FROM impact.object_natural_author WHERE object_id=%s",
            case["object_id"],
        ),
        ("SELECT object_id FROM impact.audit_event_current WHERE object_reference=%s", case["object_id"]),
        (
            "SELECT operation_id FROM impact.operation_receipt WHERE command_type='create_human_advice_case' AND outcome->>'object_id'=%s",
            case["object_id"],
        ),
        (
            "SELECT event_id FROM impact.outbox_event WHERE payload->>'aggregate_type'='HumanAdviceCase' AND payload->>'aggregate_id'=%s",
            case["object_id"],
        ),
        ("SELECT object_id FROM impact.human_advice_case_current WHERE object_id=%s", case["object_id"]),
        ("SELECT problem FROM impact.human_advice_private_brief WHERE object_id=%s", case["object_id"]),
        ("SELECT event_id FROM impact.outbox_delivery WHERE event_id=%s", event),
        ("SELECT event_id FROM impact.consumer_receipt WHERE event_id=%s", event),
    ]
    with psycopg.connect(dsn, prepare_threshold=None) as c:
        for query, identifier in queries:
            try:
                with c.transaction():
                    c.execute(
                        "SET LOCAL ROLE " + ("impact_app" if name == "EXECUTOR" else "impact_" + name.lower())
                    )
                    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                    assert not c.execute(query, (identifier,)).fetchall()
            except psycopg.errors.InsufficientPrivilege:
                # A runtime without table privileges is also denied; the
                # transaction savepoint rolls back the refused statement.
                pass


def test_event_failure_rolls_back_head_projection_private_brief_and_receipt(live):
    anchor = save_plan(live)
    body = creation()
    body["data"].update(
        context_plan_id=anchor["object_id"],
        context_plan_revision=anchor["revision_id"],
        adviser_membership_id=live.fixture["actors"]["reviewer"]["membership_id"],
    )
    with live.db() as c:
        c.execute(
            "CREATE FUNCTION impact.synthetic_advice_event_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.payload->>'aggregate_type'='HumanAdviceCase' THEN RAISE EXCEPTION 'synthetic advice event failure'; END IF; RETURN NEW; END $$"
        )
        c.execute(
            "CREATE TRIGGER synthetic_advice_event_failure BEFORE INSERT ON impact.outbox_event FOR EACH ROW EXECUTE FUNCTION impact.synthetic_advice_event_failure()"
        )
    try:
        response = live.request(live.path(ROUTE), actor="admin", method="POST", body=body)
        assert response.status_code >= 500
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            assert (
                c.execute(
                    "SELECT object_id FROM impact.human_advice_case_current WHERE context_plan_id=%s",
                    (anchor["object_id"],),
                ).fetchone()
                is None
            )
            assert (
                c.execute(
                    "SELECT operation_id FROM impact.operation_receipt WHERE operation_id=%s",
                    (body["operation_id"],),
                ).fetchone()
                is None
            )
            assert (
                c.execute(
                    "SELECT object_id FROM impact.object_revision WHERE object_type='HumanAdviceCase' AND payload->>'context_plan_id'=%s",
                    (anchor["object_id"],),
                ).fetchone()
                is None
            )
    finally:
        with live.db() as c:
            c.execute("DROP TRIGGER synthetic_advice_event_failure ON impact.outbox_event")
            c.execute("DROP FUNCTION impact.synthetic_advice_event_failure()")
    first = expect(live.request(live.path(ROUTE), actor="admin", method="POST", body=body), 201)
    assert first == expect(live.request(live.path(ROUTE), actor="admin", method="POST", body=body), 201)
