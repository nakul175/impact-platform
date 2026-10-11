"""US-DX-01a bounded manual input and the published closed command contracts."""

from copy import deepcopy
from uuid import uuid4

import pytest

from impact_api.ai_diagnoses import validate_diagnosis
from impact_api.contracts import validate
from impact_api.domain import DomainError


def diagnosis():
    first, second = str(uuid4()), str(uuid4())
    return {
        "title": "Synthetic programme priorities",
        "problems": [
            {
                "problem_id": first,
                "description": "Duplicated synthetic reporting",
                "affected_area": "Reporting",
                "supporting_evidence": "Synthetic sample: three duplicate forms.",
            },
            {
                "problem_id": second,
                "description": "Slow synthetic training preparation",
                "affected_area": "Training",
                "supporting_evidence": "Synthetic rehearsal: two preparation sessions.",
            },
        ],
        "priority_order": [second, first],
    }


def test_completed_validation_preserves_input_identity_evidence_and_explicit_order():
    # AC-US-DX-01a-001 — order is independent of collection order, no inferred evidence.
    data = diagnosis()
    original = deepcopy(data)
    validate_diagnosis(data, complete=True)
    assert data == original


def test_draft_allows_missing_evidence_and_priority_but_complete_names_each_problem():
    # AC-US-DX-01a-002 — report every unfinished visible problem, not only the first.
    data = diagnosis()
    data["problems"][0]["supporting_evidence"] = "  "
    data["priority_order"] = []
    original = deepcopy(data)
    validate_diagnosis(data)
    with pytest.raises(DomainError) as result:
        validate_diagnosis(data, complete=True)
    error = result.value
    assert error.code == "VALIDATION_FAILED" and error.reason == "DIAGNOSIS_INCOMPLETE"
    assert len(error.fields) == 3
    for problem in data["problems"]:
        matching = [field for field in error.fields if problem["problem_id"] in field["path"]]
        assert matching and all(problem["description"] in field["message"] for field in matching)
        assert all(set(field) == {"path", "message"} for field in matching)
    assert data == original


@pytest.mark.parametrize(
    "field,limit", [("description", 1000), ("affected_area", 150), ("supporting_evidence", 4000)]
)
def test_each_problem_text_accepts_limit_and_refuses_overflow(field, limit):
    data = diagnosis()
    data["problems"][0][field] = "x" * limit
    validate_diagnosis(data, complete=True)
    data["problems"][0][field] += "x"
    with pytest.raises(DomainError):
        validate_diagnosis(data)


@pytest.mark.parametrize(
    "fault",
    [
        "duplicate_problem",
        "duplicate_priority",
        "unknown_priority",
        "uppercase_id",
        "braced_id",
        "nonstring_id",
        "server_field",
        "unknown_problem_field",
        "overlong_title",
        "blank_title",
        "too_many",
        "boolean_problems",
    ],
)
def test_ambiguous_identity_untrusted_server_fields_and_invalid_bounds_are_refused(fault):
    data = diagnosis()
    if fault == "duplicate_problem":
        data["problems"][1]["problem_id"] = data["problems"][0]["problem_id"]
    elif fault == "duplicate_priority":
        data["priority_order"].append(data["priority_order"][0])
    elif fault == "unknown_priority":
        data["priority_order"].append(str(uuid4()))
    elif fault in ("uppercase_id", "braced_id", "nonstring_id"):
        value = data["problems"][0]["problem_id"]
        data["problems"][0]["problem_id"] = (
            value.upper() if fault == "uppercase_id" else "{" + value + "}" if fault == "braced_id" else True
        )
    elif fault == "server_field":
        data["completed_by"] = str(uuid4())
    elif fault == "unknown_problem_field":
        data["problems"][0]["evidence_revision_id"] = str(uuid4())
    elif fault == "overlong_title":
        data["title"] = "x" * 151
    elif fault == "blank_title":
        data["title"] = "   "
    elif fault == "too_many":
        data["problems"] = [{**data["problems"][0], "problem_id": str(uuid4())} for _ in range(21)]
        data["priority_order"] = []
    else:
        data["problems"] = True
    with pytest.raises(DomainError) as result:
        validate_diagnosis(data)
    assert result.value.status == 422


def test_empty_draft_is_valid_and_empty_completion_is_refused():
    data = {"title": "Synthetic draft", "problems": [], "priority_order": []}
    validate_diagnosis(data)
    with pytest.raises(DomainError) as result:
        validate_diagnosis(data, complete=True)
    assert result.value.fields == [{"path": "problems", "message": "Add at least one problem."}]


def test_twenty_problems_and_an_exact_twenty_item_order_can_complete():
    data = diagnosis()
    data["problems"] = [{**data["problems"][0], "problem_id": str(uuid4())} for _ in range(20)]
    data["priority_order"] = [problem["problem_id"] for problem in reversed(data["problems"])]
    validate_diagnosis(data, complete=True)


@pytest.mark.parametrize(
    "schema", ["AIDiagnosisCreate", "AIDiagnosisUpdate", "AIDiagnosisComplete", "AIDiagnosisRevise"]
)
def test_commands_are_closed_and_refuse_client_completion_metadata(schema):
    body = {"operation_id": str(uuid4())}
    if schema in ("AIDiagnosisCreate", "AIDiagnosisUpdate"):
        body["data"] = diagnosis()
    if schema != "AIDiagnosisCreate":
        body["expected_revision"] = str(uuid4())
    if schema == "AIDiagnosisRevise":
        body["reason"] = "Synthetic correction"
    validate(schema, body)
    for field in ("completed_by", "completed_at", "diagnosis_state", "approved"):
        with pytest.raises(DomainError):
            validate(schema, {**body, field: "forged"})


@pytest.mark.parametrize("code", ["INVALID_CURSOR", "IDEMPOTENCY_EXPIRED"])
def test_diagnosis_error_reader_admits_actual_cursor_expiry_refusals_but_stays_closed(code):
    body = {
        "code": code,
        "message": "The request could not be completed.",
        "retryable": False,
        "correlation_id": str(uuid4()),
        "permitted_actions": [],
    }
    validate("AIDiagnosisError", body)
    with pytest.raises(DomainError):
        validate("AIDiagnosisError", {**body, "private_payload": diagnosis()})
    with pytest.raises(DomainError):
        validate("AIDiagnosisError", {**body, "code": "UNREVIEWED_CODE"})
