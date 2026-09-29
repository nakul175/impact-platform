"""Unit checks of framework structure rules and target progress arithmetic (no database)."""

import uuid

import pytest
from impact_api.planning import progress, slot, structure_issues


def actual(value, state="PRESENT"):
    return {"mode": "OFFICIAL", "value_state": state, "value": value}


def goal(value=None, direction="HIGHER", kind="VALUE", state="PRESENT", **extra):
    return {"target_kind": kind, "direction": direction, "value_state": state, "value": value, **extra}


def test_higher_target_attainment_is_uncapped():
    # FT-IND-003: actual 120 against a higher target of 100 is 120 percent attainment.
    result = progress(actual("120"), goal("100"), None, 0)
    assert (result["status"], result["attainment_percent"], result["deviation"]) == (
        "ACHIEVED",
        "120.00",
        "20",
    )


def test_lower_target_reports_signed_deviation_without_inverting_success():
    # FT-IND-003 / FT-ANA-003: lower-is-better target 10 with actual 8 is achieved, deviation -2.
    result = progress(actual("8"), goal("10", "LOWER"), None, 1)
    assert result["status"] == "ACHIEVED" and result["attainment_percent"] is None
    assert (result["deviation"], result["displayed_deviation"]) == ("-2", "-2.0")
    assert progress(actual("12"), goal("10", "LOWER"), None, 0)["status"] == "ABOVE_TARGET"


def test_zero_target_and_zero_baseline_are_undefined_not_divided():
    result = progress(actual("5"), goal("0"), goal("0", target_basis="BASELINE"), 0)
    assert result["attainment_percent"] == "Undefined" and result["reason_code"] == "ZERO_TARGET"
    assert result["change_from_baseline"] == "5" and result["change_from_baseline_percent"] == "Undefined"


def test_range_bounds_are_inclusive():
    bounds = {"low": "3", "high": "9"}
    for value, status, deviation in [
        ("3", "WITHIN_RANGE", "0"),
        ("9", "WITHIN_RANGE", "0"),
        ("2.5", "BELOW_RANGE", "-0.5"),
        ("10", "ABOVE_RANGE", "1"),
    ]:
        result = progress(actual(value), goal(None, "RANGE", "RANGE", **bounds), None, 1)
        assert (result["status"], result["deviation"]) == (status, deviation)


def test_blank_target_and_blank_actual_are_never_zero():
    assert progress(actual(None, "MISSING"), goal("10"), None, 0)["status"] == "NO_ACTUAL"
    blank = progress(actual("7"), goal(None, state="MISSING"), None, 0)
    assert blank["status"] == "NO_TARGET" and blank["reason_code"] == "TARGET_MISSING"
    assert blank["deviation"] is None
    assert progress(actual("7"), None, None, 0)["reason_code"] == "NO_APPROVED_TARGET"


def test_milestones_require_assessment_and_arithmetic_uses_stored_values():
    assert (
        progress(actual("1"), goal("1", "MILESTONE", "MILESTONE"), None, 0)["status"] == "ASSESSMENT_REQUIRED"
    )
    # 46.363636363636 against 50 uses the stored value, not the displayed 46.36.
    result = progress(actual("46.363636363636"), goal("50"), None, 2)
    assert result["attainment_percent"] == "92.73" and result["deviation"] == "-3.636363636364"
    assert result["displayed_deviation"] == "-3.64"


def test_target_slots():
    assert slot({"target_basis": "BASELINE", "target_kind": "VALUE"}) == "BASELINE"
    assert slot({"target_basis": "ORIGINAL", "target_kind": "RANGE"}) == "TARGET"
    assert slot({"target_kind": "MILESTONE", "milestone_label": "Launch"}) == "MILESTONE:Launch"


def node(level, parent=None, owner="o", indicators=()):
    return {
        "node_id": str(uuid.uuid4()),
        "node_type": level,
        "parent_node_id": parent,
        "owner_id": owner,
        "indicator_ids": list(indicators),
    }


def rules(nodes):
    return {(severity, rule) for severity, rule, _, _ in structure_issues(nodes)}


def test_structure_rules():
    impact = node("IMPACT", indicators=["a"])
    outcome = node("OUTCOME", impact["node_id"], indicators=["b"])
    assert rules([impact, outcome]) == set()
    assert ("ERROR", "LEVEL_ORDER") in rules(
        [impact, outcome, node("IMPACT", outcome["node_id"], indicators=["c"])]
    )
    assert ("ERROR", "ORPHAN_PARENT") in rules([node("OUTPUT", str(uuid.uuid4()), indicators=["c"])])
    looped = node("OUTCOME", indicators=["x"])
    other = node("OUTCOME", looped["node_id"], indicators=["y"])
    looped["parent_node_id"] = other["node_id"]
    assert ("ERROR", "CONTAINMENT_CYCLE") in rules([looped, other])
    itself = node("OUTPUT", indicators=["z"])
    itself["parent_node_id"] = itself["node_id"]
    assert ("ERROR", "CONTAINMENT_CYCLE") in rules([itself])
    assert ("ERROR", "DUPLICATE_NODE_ID") in rules([impact, dict(impact)])
    assert ("ERROR", "INDICATOR_LINKED_TWICE") in rules(
        [impact, node("OUTCOME", impact["node_id"], indicators=["a"])]
    )
    assert ("ERROR", "NODE_INCOMPLETE") in rules([node("ACTIVITY", owner=None)])
    assert ("WARNING", "ORPHAN_NODE") in rules([impact, node("OUTPUT", indicators=["d"])])
    assert ("WARNING", "UNMEASURED_RESULT") in rules([node("OUTPUT")])
    assert ("WARNING", "UNMEASURED_RESULT") not in rules([node("ACTIVITY")])


@pytest.mark.parametrize("value", ["1e3", "01", "1.0000000000001"])
def test_progress_rejects_non_contract_decimals(value):
    with pytest.raises(Exception):
        progress(actual(value), goal("1"), None, 0)
