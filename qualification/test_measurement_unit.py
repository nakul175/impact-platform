from datetime import datetime, timezone
from uuid import uuid4
import pytest
from impact_api.domain import DomainError
from impact_api.measurement import coverage, definition_ready, valid_value
from impact_api.contracts import validate


def definition(**kw):
    return {
        "code": "H",
        "name": "Households",
        "measurement_type": "COUNT",
        "unit": "households",
        "population": "Resident households",
        "inclusion": "Registered",
        "exclusion": "Duplicates",
        "method": "Register count",
        "source_mode": "MANUAL",
        "time_semantic": "FLOW",
        "combination_rule": "SUM",
        "display_decimals": 0,
        **kw,
    }


def example(states):
    obligations = [
        {
            "label": f"Partner {i}",
            "source_namespace": "MANUAL",
            "source_key": str(i),
            "due_at": "2026-09-01T00:00:00Z",
        }
        for i in range(len(states))
    ]
    rows = [
        {
            "head_revision": str(uuid4()),
            "payload": {
                "source_namespace": "MANUAL",
                "source_key": str(i),
                "value": "0",
                "value_state": value,
                "approval_state": approval,
            },
        }
        for i, state in enumerate(states)
        if state
        for value, approval in [state]
    ]
    return {"head_revision": str(uuid4()), "payload": {"obligations": obligations}}, rows


def test_fsd_five_contributors_three_approved_one_pending_one_missing():
    plan, rows = example([("PRESENT", "APPROVED")] * 3 + [("PRESENT", "SUBMITTED"), None])
    result, included = coverage(plan, rows, definition(), datetime(2026, 9, 25, tzinfo=timezone.utc))
    assert [
        result[k]
        for k in [
            "expected_count",
            "received_count",
            "valid_count",
            "approved_count",
            "pending_count",
            "missing_count",
            "overdue_count",
        ]
    ] == [5, 4, 4, 3, 1, 1, 2]
    assert result["approval_percent"] == "60.00" and not result["complete"] and len(included) == 3


@pytest.mark.parametrize(
    "state,status",
    [
        ("MISSING", "MISSING"),
        ("NOT_COLLECTED", "MISSING"),
        ("NOT_APPLICABLE", "EXCLUDED"),
        ("INVALID", "EXCLUDED"),
    ],
)
def test_non_present_never_reduces_expected(state, status):
    plan, rows = example([(state, "APPROVED")])
    result, included = coverage(plan, rows, definition(), datetime(2026, 8, 1, tzinfo=timezone.utc))
    assert result["expected_count"] == 1 and result["approved_count"] == 0 and not result["complete"]
    assert result["obligations"][0]["status"] == status and not included and result["overdue_count"] == 0


def test_zero_is_valid_and_unplanned_does_not_fill_gap():
    plan, rows = example([("PRESENT", "APPROVED"), None])
    rows.append(
        {
            "head_revision": str(uuid4()),
            "payload": {
                "source_namespace": "EXTRA",
                "source_key": "1",
                "value": "999",
                "value_state": "PRESENT",
                "approval_state": "APPROVED",
            },
        }
    )
    result, included = coverage(plan, rows, definition(), datetime(2026, 9, 25, tzinfo=timezone.utc))
    assert (
        result["valid_count"] == 1
        and result["approved_count"] == 1
        and result["missing_count"] == 1
        and result["unplanned_count"] == 1
        and len(included) == 1
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"source_mode": "FORM"},
        {"time_semantic": "STOCK"},
        {"combination_rule": "WEIGHTED_INDEX"},
        {"combination_rule": "UNIQUE_COUNT"},
        {"time_semantic": "CUMULATIVE"},
        {"measurement_type": "CURRENCY"},
        {"measurement_type": "PERCENTAGE"},
        {"method": "  "},
    ],
)
def test_unsupported_or_incomplete_definitions_blocked(changes):
    with pytest.raises(DomainError):
        definition_ready(definition(**changes))


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"measurement_type": "DECIMAL"},
        {
            "measurement_type": "PERCENTAGE",
            "combination_rule": "POOLED_RATIO",
            "numerator_meaning": "Successful visits",
            "denominator_meaning": "All visits",
        },
        {
            "measurement_type": "RATIO",
            "combination_rule": "POOLED_RATIO",
            "numerator_meaning": "Cases",
            "denominator_meaning": "Visits",
        },
    ],
)
def test_supported_definition_contract(changes):
    value = definition(**changes)
    validate("IndicatorDefinitionData", value)
    definition_ready(value)


@pytest.mark.parametrize(
    "value,valid", [("0", True), ("10", True), ("-1", False), ("1.5", False), ("NaN", False), (None, False)]
)
def test_count_qualification(value, valid):
    assert valid_value(definition(), {"value_state": "PRESENT", "value": value}) is valid


@pytest.mark.parametrize(
    "bad",
    [{"obligations": []}, {"obligations": [{"label": ""}]}, {"title": "  "}, {"lifecycle_state": "Approved"}],
)
def test_plan_contract_rejects_invalid_or_authority_fields(bad):
    with pytest.raises(DomainError):
        validate("CollectionPlanDraftData", bad)


def test_completion_and_cutoff_are_snapshot_properties():
    plan, rows = example([("PRESENT", "APPROVED")])
    result, _ = coverage(plan, rows, definition(), datetime(2026, 9, 25, tzinfo=timezone.utc))
    assert result["complete"] and result["approval_percent"] == "100.00" and result["overdue_count"] == 0
    assert result["plan_revision"] == plan["head_revision"]


def test_reviewed_exception_retains_expected_count_but_changes_required_denominator():
    plan, rows = example([("PRESENT", "APPROVED"), None])
    plan["payload"]["obligations"][1].update(
        eligibility="EXCEPTED",
        exclusion_reason="Contributor was ineligible for this period.",
        exclusion_effective_at="2026-08-31T00:00:00Z",
    )
    result, included = coverage(plan, rows, definition(), datetime(2026, 9, 25, tzinfo=timezone.utc))
    assert result["expected_count"] == 2
    assert result["required_count"] == 1
    assert result["excepted_count"] == 1
    assert result["approved_count"] == 1
    assert result["approval_percent"] == "100.00"
    assert result["complete"] and len(included) == 1
    assert result["obligations"][1]["status"] == "EXCEPTED"
