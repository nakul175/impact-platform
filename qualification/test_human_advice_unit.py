"""Pure advice contracts and consent/state regressions; no database evidence."""

from copy import deepcopy
from datetime import datetime, timezone
from datetime import timedelta
from types import SimpleNamespace
from uuid import UUID, uuid4

from jsonschema import Draft202012Validator, FormatChecker
import pytest

from impact_api.domain import DomainError
from impact_api.human_advice import (
    HumanAdviceCases,
    brief_digest,
    fingerprint_value,
    initial_payload,
    public_payload,
    role,
    selector,
    transition,
)
from impact_api.human_advice_contracts import (
    ACTION_DATA,
    MATERIAL_POLICY,
    PRIVATE_PROOF_FIELDS,
    augment,
    public_schema,
    stored_schema,
    validate_body,
)
from impact_api.store import hash_data

STAMP = "2026-10-05T09:30:00+00:00"


def parties():
    return {
        who + "_" + field: str(uuid4())
        for who in ("requester", "adviser")
        for field in ("principal_id", "membership_id", "natural_id")
    }


def creation():
    return {
        "operation_id": str(uuid4()),
        "data": {
            "title": "Synthetic public communications pilot advice",
            "context_plan_id": str(uuid4()),
            "context_plan_revision": str(uuid4()),
            "adviser_membership_id": str(uuid4()),
            "problem": "Private synthetic example question; never a programme record reference.",
            "scope": "Help choose a bounded human-reviewed public drafting trial",
            "data_boundary": "Synthetic or public text only; no personal or programme records",
            "desired_outcome": "An accountable recommendation and small next steps",
            "material_policy": MATERIAL_POLICY,
            "invitation_consent": True,
        },
    }


def action_body(data, revision=None):
    return {"operation_id": str(uuid4()), "expected_revision": revision or str(uuid4()), "data": data}


def advance(payload, state, action, data, who, revision=None):
    revision = revision or str(uuid4())
    validate_body(action_body(data, revision), action)
    return transition(payload, state, action, data, payload[who + "_principal_id"], revision, STAMP)


def assigned():
    request = creation()
    payload = initial_payload(request["data"], parties(), STAMP)
    declared, _ = advance(
        payload,
        "Open",
        "declare-scope",
        {"conflict": "NONE", "details": "No supplier or other relevant relationship", "scope_accepted": True},
        "adviser",
    )
    rev = str(uuid4())
    payload, state = advance(
        declared,
        "Open",
        "assign",
        {"declaration_revision_id": rev, "sharing_confirmed": True},
        "requester",
        rev,
    )
    return payload, state


def advised():
    payload, state = assigned()
    return advance(
        payload,
        state,
        "advise",
        {
            "advice": "Try the synthetic task and have a colleague check every factual claim.",
            "actions": [
                {"description": "Write acceptance examples", "responsibility": "REQUESTER"},
                {"description": "Review the synthetic examples", "responsibility": "ADVISER"},
            ],
        },
        "adviser",
    )


def assert_stored(payload):
    Draft202012Validator(stored_schema(), format_checker=FormatChecker()).validate(payload)


def test_server_uuid_selectors_are_normalized_without_widening_closed_request_types():
    value = uuid4()
    assert selector(value) == str(value)
    assert selector(str(value)) == str(value)
    request = creation()
    request["data"]["adviser_membership_id"] = value
    with pytest.raises(DomainError) as error:
        validate_body(request)
    assert error.value.code == "VALIDATION_FAILED"


@pytest.mark.parametrize("found", [False, True])
def test_exact_anchor_guard_qualifies_tenant_object_revision_type_and_availability(found):
    ctx = SimpleNamespace(tenant_id=str(uuid4()))
    plan, revision = uuid4(), uuid4()
    captured = []

    def execute(query, arguments):
        captured.append((query, arguments))
        return SimpleNamespace(fetchone=lambda: {"revision_id": revision} if found else None)

    module = HumanAdviceCases(None)
    if found:
        module.require_available_anchor(SimpleNamespace(execute=execute), ctx, plan, revision)
    else:
        with pytest.raises(DomainError) as error:
            module.require_available_anchor(SimpleNamespace(execute=execute), ctx, plan, revision)
        assert error.value.code == "RESOURCE_UNAVAILABLE" and error.value.status == 404
    query, arguments = captured[0]
    assert arguments == (ctx.tenant_id, str(plan), str(revision))
    for predicate in (
        "tenant_id=%s",
        "object_id=%s",
        "revision_id=%s",
        "object_type='AIAdoptionPlan'",
        "restriction_state='AVAILABLE'",
    ):
        assert predicate in query


def test_problem_is_not_in_any_shared_immutable_case_payload():
    request = creation()
    validate_body(request)
    nonce = str(uuid4())
    payload = initial_payload(request["data"], parties(), STAMP, nonce)
    assert "problem" not in payload
    assert payload["problem_sha256"] == brief_digest(request["data"]["problem"], nonce).hex()
    assert payload["problem_sha256"] != hash_data({"problem": request["data"]["problem"]}).hex()
    assert payload["problem_sha256"] != brief_digest(request["data"]["problem"], uuid4()).hex()
    assert "brief_nonce" not in payload
    assert payload["assignment"] is None and payload["state"] == "Open"
    assert_stored(payload)


def test_public_payload_allowlist_omits_private_proofs_without_mutating_stored_consent():
    payload, _ = assigned()
    original = deepcopy(payload)
    payload["future_private_proof"] = "server-only"
    payload["declaration"]["future_private_proof"] = "server-only"
    public = public_payload(payload)
    Draft202012Validator(public_schema(), format_checker=FormatChecker()).validate(public)
    assert not PRIVATE_PROOF_FIELDS.intersection(public)
    assert "future_private_proof" not in public
    for decision in ("declaration", "assignment"):
        assert "authenticated_at" not in public[decision]
        assert "future_private_proof" not in public[decision]
        assert payload[decision]["authenticated_at"] == original[decision]["authenticated_at"]
    for field in PRIVATE_PROOF_FIELDS:
        assert payload[field] == original[field]
    for field in (
        "requester_principal_id",
        "adviser_principal_id",
        "requester_membership_id",
        "adviser_membership_id",
    ):
        assert public[field] == original[field]
    public["declaration"]["details"] = "Edited public copy"
    assert payload["declaration"]["details"] == original["declaration"]["details"]
    spec, policy = {"components": {"schemas": {}}, "paths": {}}, {"operations": []}
    augment(spec, policy)
    assert spec["components"]["schemas"]["HumanAdviceCase"]["properties"]["data"] == {
        "$ref": "#/components/schemas/HumanAdvicePublicData"
    }
    assert PRIVATE_PROOF_FIELDS <= set(spec["components"]["schemas"]["HumanAdviceStoredData"]["properties"])


@pytest.mark.parametrize(
    "who,state",
    [
        ("requester", "Open"),
        ("adviser", "Open"),
        ("requester", "Assigned"),
        ("adviser", "Assigned"),
        ("requester", "Closed"),
    ],
)
def test_case_result_protects_server_proofs_and_preserves_private_brief_visibility(who, state):
    request = creation()
    nonce = uuid4()
    payload = initial_payload(request["data"], parties(), STAMP, nonce)
    if state != "Open":
        payload, _ = assigned()
        payload["problem_sha256"] = brief_digest(request["data"]["problem"], nonce).hex()
    payload["state"] = state
    brief = {
        "problem": request["data"]["problem"],
        "problem_sha256": bytes.fromhex(payload["problem_sha256"]),
        "brief_nonce": nonce,
    }
    connection = SimpleNamespace(execute=lambda *args: SimpleNamespace(fetchone=lambda: brief))
    case = {"payload": payload, "object_id": uuid4(), "head_revision": uuid4(), "lifecycle_state": state}
    ctx = SimpleNamespace(principal_id=payload[who + "_principal_id"], tenant_id=uuid4())
    result = HumanAdviceCases(None).result(
        connection, ctx, case, {"head_revision": payload["context_plan_revision"]}
    )
    Draft202012Validator(public_schema(), format_checker=FormatChecker()).validate(result["data"])
    assert not PRIVATE_PROOF_FIELDS.intersection(result["data"])
    for decision in ("declaration", "assignment"):
        assert result["data"][decision] is None or "authenticated_at" not in result["data"][decision]
    assert result["problem"] == (None if (who, state) == ("adviser", "Open") else request["data"]["problem"])
    assert_stored(payload)


def test_public_projection_keeps_private_brief_integrity_validation_before_disclosure():
    request = creation()
    nonce = uuid4()
    payload = initial_payload(request["data"], parties(), STAMP, nonce)
    brief = {
        "problem": "Tampered synthetic brief",
        "problem_sha256": bytes.fromhex(payload["problem_sha256"]),
        "brief_nonce": nonce,
    }
    connection = SimpleNamespace(execute=lambda *args: SimpleNamespace(fetchone=lambda: brief))
    case = {"payload": payload, "object_id": uuid4(), "head_revision": uuid4(), "lifecycle_state": "Open"}
    ctx = SimpleNamespace(principal_id=payload["requester_principal_id"], tenant_id=uuid4())
    with pytest.raises(DomainError) as error:
        HumanAdviceCases(None).result(
            connection, ctx, case, {"head_revision": payload["context_plan_revision"]}
        )
    assert error.value.status == 404


@pytest.mark.parametrize(
    "field",
    [
        "recipient_ids",
        "programme_id",
        "participant_id",
        "attachment_revision",
        "provider",
        "fee",
        "booking",
        "approval",
        "requester_principal_id",
        "authenticated_at",
        "waive_conflict",
    ],
)
@pytest.mark.parametrize("nested", [False, True])
def test_external_references_server_fields_and_commitments_are_rejected(field, nested):
    request = creation()
    (request["data"] if nested else request)[field] = str(uuid4())
    with pytest.raises(DomainError) as error:
        validate_body(request)
    assert error.value.code == "VALIDATION_FAILED"


@pytest.mark.parametrize(
    "edit",
    [
        lambda d: d.update(invitation_consent=False),
        lambda d: d.update(material_policy="ANY_RECORD"),
        lambda d: d.update(problem=" "),
        lambda d: d.update(problem="x" * 4001),
        lambda d: d.update(scope="x" * 2001),
        lambda d: d.update(adviser_membership_id="missing"),
        lambda d: d.update(context_plan_revision="old"),
    ],
)
def test_invitation_consent_material_limit_and_scope_selectors_fail_closed(edit):
    request = creation()
    edit(request["data"])
    with pytest.raises(DomainError):
        validate_body(request)


def test_same_natural_person_under_another_principal_cannot_be_the_adviser():
    members = parties()
    members["adviser_natural_id"] = members["requester_natural_id"]
    with pytest.raises(DomainError) as error:
        initial_payload(creation()["data"], members, STAMP)
    assert error.value.reason == "INDEPENDENCE_REQUIRED"


def test_full_accountable_case_closes_only_with_exact_advice_and_all_actions_acknowledged():
    payload, state = assigned()
    assert payload["assignment"]["sharing_confirmed"] and state == "Assigned"
    questioned, state = advance(
        payload,
        state,
        "request-input",
        {"question": "Which synthetic success examples should we use?"},
        "adviser",
    )
    responded, state = advance(
        questioned,
        state,
        "respond",
        {"response": "Verify every claim against the public source."},
        "requester",
    )
    advice, state = advance(
        responded,
        state,
        "advise",
        {
            "advice": "Use the synthetic trial, with human review.",
            "actions": [{"description": "Prepare the test examples", "responsibility": "REQUESTER"}],
        },
        "adviser",
    )
    advice_revision = str(uuid4())
    closed, state = advance(
        advice,
        state,
        "close",
        {
            "advice_revision_id": advice_revision,
            "acknowledged_action_ids": [item["action_id"] for item in advice["advice"]["actions"]],
            "closure_reason": "Advice acknowledged; our organisation will decide whether to act.",
        },
        "requester",
        advice_revision,
    )
    assert state == "Closed" and closed["advice"] == advice["advice"]
    assert closed["closure"]["advice_revision_id"] == advice_revision
    assert [note["kind"] for note in closed["notes"]] == ["QUESTION", "RESPONSE"]
    assert closed["notes"][0]["author_id"] == closed["adviser_principal_id"]
    assert closed["notes"][1]["author_id"] == closed["requester_principal_id"]
    assert payload["notes"] == []  # Every predecessor remains unchanged.
    assert_stored(closed)


@pytest.mark.parametrize("conflict,accepted", [("DECLARED", False), ("NONE", False)])
def test_declared_conflict_or_unaccepted_scope_is_recorded_but_cannot_be_assigned(conflict, accepted):
    payload = initial_payload(creation()["data"], parties(), STAMP)
    payload, state = advance(
        payload,
        "Open",
        "declare-scope",
        {"conflict": conflict, "details": "Accountable declaration", "scope_accepted": accepted},
        "adviser",
    )
    assert payload["declaration"]["conflict"] == conflict and state == "Open"
    revision = str(uuid4())
    with pytest.raises(DomainError):
        advance(
            payload,
            state,
            "assign",
            {"declaration_revision_id": revision, "sharing_confirmed": True},
            "requester",
            revision,
        )


def test_conflict_cannot_be_recorded_as_accepted_scope():
    with pytest.raises(DomainError):
        validate_body(
            action_body({"conflict": "DECLARED", "details": "Supplier relationship", "scope_accepted": True}),
            "declare-scope",
        )


def test_old_declaration_revision_cannot_authorise_a_new_assignment():
    payload = initial_payload(creation()["data"], parties(), STAMP)
    payload, _ = advance(
        payload,
        "Open",
        "declare-scope",
        {"conflict": "NONE", "details": "No conflicts", "scope_accepted": True},
        "adviser",
    )
    with pytest.raises(DomainError) as error:
        advance(
            payload,
            "Open",
            "assign",
            {"declaration_revision_id": str(uuid4()), "sharing_confirmed": True},
            "requester",
            str(uuid4()),
        )
    assert error.value.code == "CONFLICT_VERSION"


@pytest.mark.parametrize("acknowledgement", ["missing", "unknown", "duplicate"])
def test_closure_cannot_invent_or_omit_action_acknowledgement(acknowledgement):
    payload, state = advised()
    ids = [item["action_id"] for item in payload["advice"]["actions"]]
    ids = (
        ids[:-1]
        if acknowledgement == "missing"
        else [str(uuid4())]
        if acknowledgement == "unknown"
        else [ids[0], ids[0]]
    )
    rev = str(uuid4())
    with pytest.raises(DomainError):
        advance(
            payload,
            state,
            "close",
            {
                "advice_revision_id": rev,
                "acknowledged_action_ids": ids,
                "closure_reason": "Acknowledgement attempted",
            },
            "requester",
            rev,
        )


def test_new_advice_or_request_for_input_invalidates_the_old_closure_target():
    payload, state = advised()
    previous = deepcopy(payload)
    with pytest.raises(DomainError) as error:
        advance(
            payload,
            state,
            "close",
            {
                "advice_revision_id": str(uuid4()),
                "acknowledged_action_ids": [item["action_id"] for item in payload["advice"]["actions"]],
                "closure_reason": "Old advice",
            },
            "requester",
            str(uuid4()),
        )
    assert error.value.reason == "ADVICE_CHANGED"
    queried, state = advance(
        payload, state, "request-input", {"question": "One more bounded question"}, "adviser"
    )
    assert state == "AwaitingInput" and queried["advice"] is None
    assert payload == previous


@pytest.mark.parametrize(
    "action,who,data",
    [
        (
            "declare-scope",
            "requester",
            {"conflict": "NONE", "details": "No conflict", "scope_accepted": True},
        ),
        ("request-input", "requester", {"question": "Wrong actor"}),
        ("advise", "requester", {"advice": "Self-advice", "actions": []}),
        ("cancel", "adviser", {"reason": "Wrong actor"}),
        ("respond", "adviser", {"response": "Wrong actor"}),
    ],
)
def test_requester_and_adviser_responsibilities_do_not_overlap(action, who, data):
    payload, state = assigned()
    with pytest.raises(DomainError) as error:
        advance(payload, state, action, data, who)
    assert error.value.status == 404


@pytest.mark.parametrize("state", ["Closed", "Cancelled"])
@pytest.mark.parametrize("action", list(ACTION_DATA))
def test_terminal_states_never_accept_another_material_transition(state, action):
    payload, _ = advised()
    who = "requester" if action in {"assign", "respond", "close", "cancel"} else "adviser"
    with pytest.raises(DomainError) as error:
        transition(payload, state, action, {}, payload[who + "_principal_id"], str(uuid4()), STAMP)
    assert error.value.reason == "HUMAN_ADVICE_TERMINAL"


def test_notes_are_bounded_without_losing_cancellation_recovery():
    payload, state = assigned()
    payload["notes"] = [{}] * 50
    with pytest.raises(DomainError) as error:
        advance(payload, state, "request-input", {"question": "Further question"}, "adviser")
    assert error.value.reason == "HUMAN_ADVICE_NOTE_LIMIT"
    _, state = advance(payload, state, "cancel", {"reason": "Stop this bounded case"}, "requester")
    assert state == "Cancelled"


def test_nonparticipant_and_database_metadata_canonicalisation_fail_closed():
    payload, _ = assigned()
    with pytest.raises(DomainError) as error:
        role(payload, str(uuid4()))
    assert error.value.status == 404
    metadata = {"id": UUID(payload["requester_principal_id"]), "at": datetime.now(timezone.utc)}
    assert len(hash_data(fingerprint_value(metadata))) == 32


def test_generated_routes_reuse_scoped_ai_read_and_manage_without_provider_permission():
    spec = {"components": {"schemas": {}}, "paths": {}}
    policy = {"operations": []}
    augment(spec, policy)
    assert len(policy["operations"]) == 13
    assert {item["capability"] for item in policy["operations"]} == {
        "ai.enablement.read",
        "ai.enablement.manage",
    }
    assert all(
        item["fresh_assurance_seconds"] == 300 for item in policy["operations"] if item["method"] == "POST"
    )
    assert all(schema["additionalProperties"] is False for schema in spec["components"]["schemas"].values())
    peer = next(
        item for item in policy["operations"] if item["operation_id"] == "list_human_advice_eligible_peers"
    )
    assert peer["role_templates"] == ["OWNER", "TENANT_ADMIN"]
    assert peer["capability"] == "ai.enablement.manage" and peer["fresh_assurance_seconds"] is None
    assert set(
        spec["components"]["schemas"]["HumanAdviceEligiblePeers"]["properties"]["items"]["items"][
            "properties"
        ]
    ) == {"membership_id", "display_name"}


@pytest.mark.parametrize("who", ["requester", "adviser"])
@pytest.mark.parametrize(
    "change", ["read_revoked", "manage_revoked", "natural_person_changed", "consent_cutoff_changed"]
)
def test_material_decisions_recheck_both_participants_current_authority_and_consent(monkeypatch, who, change):
    payload, _ = assigned()
    module = HumanAdviceCases(None)
    rows = {
        payload[person + "_membership_id"]: {
            "principal_id": payload[person + "_principal_id"],
            "natural_id": payload[person + "_natural_id"],
            "auth_not_before": None,
        }
        for person in ("requester", "adviser")
    }
    row = rows[payload[who + "_membership_id"]]
    if change == "natural_person_changed":
        row["natural_id"] = str(uuid4())
    if change == "consent_cutoff_changed":
        row["auth_not_before"] = datetime.fromisoformat(STAMP) + timedelta(seconds=1)
    monkeypatch.setattr(module, "member", lambda c, ctx, identifier: rows[identifier])
    revoked = "ai.enablement.read" if change == "read_revoked" else "ai.enablement.manage"
    monkeypatch.setattr(
        module,
        "member_scope",
        lambda c, ctx, member, cap, anchor: (
            not (change in {"read_revoked", "manage_revoked"} and member is row and cap == revoked)
        ),
    )
    with pytest.raises(DomainError) as error:
        module.current_participants(None, None, payload)
    assert error.value.status == (404 if change in {"read_revoked", "manage_revoked"} else 409)


@pytest.mark.parametrize("missing", ["directory", "tenant_scope", "ai_manage", "ai_read", "current_role"])
def test_peer_lookup_rechecks_every_directory_and_plan_gate_without_roster_disclosure(monkeypatch, missing):
    module = HumanAdviceCases(None)
    calls = []
    ctx = SimpleNamespace(
        tenant_id=str(uuid4()),
        principal_id=str(uuid4()),
        membership_id=str(uuid4()),
        grants=[{"capability": "memberships.read", "scope_type": "TENANT", "purpose": None}],
    )
    if missing == "tenant_scope":
        ctx.grants[0]["scope_type"] = "OBJECT_SET"

    def check(c, current, operation, object_id=None, hidden=False):
        calls.append(operation)
        if operation == {
            "directory": "list_membership_directory",
            "ai_manage": "list_human_advice_eligible_peers",
            "ai_read": "get_ai_adoption_plan",
        }.get(missing):
            raise DomainError("POLICY_DENIED", 403)

    class Connection:
        def execute(self, sql, args):
            assert "owner_membership_id" in sql and "TENANT_ADMIN" in sql
            return self

        def fetchone(self):
            return {"allowed": missing != "current_role"}

    monkeypatch.setattr("impact_api.human_advice.authorize", check)
    with pytest.raises(DomainError) as error:
        module.directory_authority(Connection(), ctx, str(uuid4()))
    assert error.value.code == "RESOURCE_UNAVAILABLE" and error.value.status == 404
    assert calls[0] == "list_membership_directory"


@pytest.mark.parametrize("cursor_key", [[str(uuid4()), str(uuid4())], "uuid", [False], [0], [-1]])
def test_bounded_cursor_keys_refuse_wrong_shapes_and_nonpositive_revision_numbers(cursor_key):
    module = HumanAdviceCases(SimpleNamespace(cursor_key=lambda binding, cursor: cursor_key))
    with pytest.raises(DomainError) as error:
        module.key("current-binding", "signed-but-invalid-key", number=True)
    assert error.value.code == "INVALID_CURSOR" and error.value.status == 400
