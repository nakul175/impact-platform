"""Unit checks of framework structure rules and target progress arithmetic (no database)."""

import uuid
from decimal import Decimal

import pytest
from impact_api.planning import (
    performance_band,
    progress,
    safe_progress,
    slot,
    structure_issues,
    threshold_issue,
)


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
    assert result["change_from_baseline_reason"] == "NON_POSITIVE_BASELINE"


def test_negative_baseline_has_no_percentage_change():
    # M3: a percentage change from a negative baseline needs an approved interpretation.
    result = progress(actual("5"), goal("10"), goal("-4", target_basis="BASELINE"), 0)
    assert result["change_from_baseline"] == "9"
    assert result["change_from_baseline_percent"] == "Undefined"
    assert result["change_from_baseline_reason"] == "NON_POSITIVE_BASELINE"
    positive = progress(actual("15"), goal("10"), goal("10", target_basis="BASELINE"), 0)
    assert (
        positive["change_from_baseline_percent"] == "50.00"
        and positive["change_from_baseline_reason"] is None
    )


def test_overflow_empties_one_row_not_the_read():
    # L1: the reviewer's values, a deviation beyond NUMERIC(38,12).
    big = "99999999999999999999999999.999999999999"
    result = safe_progress(actual(big), goal("-" + big), None, 2)
    assert result["status"] == "NOT_COMPUTABLE" and result["reason_code"] == "ARITHMETIC_OVERFLOW"
    assert result["deviation"] is None and result["attainment_percent"] is None
    assert safe_progress(actual("120"), goal("100"), None, 0)["attainment_percent"] == "120.00"


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


# Theory of change, assumptions and status thresholds (v0.27 planning) --------------------------


def link(a, b, kind="CONTRIBUTES_TO", strength="MODERATE", assumptions=(), rid=None):
    return {
        "relationship_id": rid or str(uuid.uuid4()),
        "from_node_id": a["node_id"],
        "to_node_id": b["node_id"],
        "relationship_type": kind,
        "rationale": "Stated pathway.",
        "evidence_strength": strength,
        "assumption_ids": list(assumptions),
    }


def assumption(nodes=(), status="HOLDS", kind="ASSUMPTION", owner="o", review="2027-01-01", aid=None):
    return {
        "assumption_id": aid or str(uuid.uuid4()),
        "kind": kind,
        "node_ids": [n["node_id"] for n in nodes],
        "statement": "Funding continues.",
        "owner_id": owner,
        "review_date": review,
        "status": status,
    }


def toc(nodes, relationships=(), assumptions=(), today="2026-10-02"):
    return {(s, r, o) for s, r, o, _ in structure_issues(nodes, relationships, assumptions, today)}


def only_rules(found):
    return {(s, r) for s, r, _ in found}


def test_relationship_rules():
    impact = node("IMPACT", indicators=["a"])
    outcome = node("OUTCOME", impact["node_id"], indicators=["b"])
    other = node("OUTCOME", impact["node_id"], indicators=["c"])
    output = node("OUTPUT", outcome["node_id"], indicators=["d"])
    nodes = [impact, outcome, other, output]
    # FT-PLN-002: two outcomes contribute to one impact; alternative pathways are allowed.
    assert toc(nodes, [link(outcome, impact), link(other, impact), link(output, other)]) == set()
    # DEPENDS_ON states the same contribution from the dependent side.
    assert toc(nodes, [link(impact, outcome, "DEPENDS_ON")]) == set()
    assert only_rules(toc(nodes, [link(impact, outcome)])) == {("ERROR", "RELATIONSHIP_LEVEL_ORDER")}
    assert only_rules(toc(nodes, [link(outcome, impact, "DEPENDS_ON")])) == {
        ("ERROR", "RELATIONSHIP_LEVEL_ORDER")
    }
    assert only_rules(toc(nodes, [link(outcome, outcome)])) == {("ERROR", "RELATIONSHIP_SELF")}
    stranger = node("OUTPUT")
    assert only_rules(toc(nodes, [link(outcome, stranger)])) == {("ERROR", "RELATIONSHIP_ENDPOINT_MISSING")}
    same = link(outcome, impact)
    assert ("ERROR", "DUPLICATE_RELATIONSHIP_ID") in only_rules(toc(nodes, [same, dict(same)]))
    assert ("ERROR", "DUPLICATE_RELATIONSHIP") in only_rules(
        toc(nodes, [link(outcome, impact), link(outcome, impact)])
    )
    # A causal cycle between nodes of one level is refused, naming every node on the cycle.
    found = toc(nodes, [link(outcome, other), link(other, outcome)])
    assert {o for s, r, o in found if r == "RELATIONSHIP_CYCLE"} == {outcome["node_id"], other["node_id"]}
    assert only_rules(toc(nodes, [link(outcome, impact, assumptions=[str(uuid.uuid4())])])) == {
        ("ERROR", "RELATIONSHIP_ASSUMPTION_MISSING")
    }
    funding = assumption([outcome])
    assert toc(nodes, [link(outcome, impact, assumptions=[funding["assumption_id"]])], [funding]) == set()
    assert only_rules(toc(nodes, [link(outcome, impact, strength="UNTESTED")])) == {
        ("WARNING", "UNTESTED_RELATIONSHIP")
    }


def test_assumption_rules():
    impact = node("IMPACT", indicators=["a"])
    outcome = node("OUTCOME", impact["node_id"], indicators=["b"])
    nodes = [impact, outcome]
    assert toc(nodes, [], [assumption([outcome])]) == set()
    one = assumption([outcome])
    assert ("ERROR", "DUPLICATE_ASSUMPTION_ID") in only_rules(toc(nodes, [], [one, dict(one)]))
    assert only_rules(toc(nodes, [], [assumption([node("OUTPUT")])])) == {
        ("ERROR", "ASSUMPTION_NODE_MISSING")
    }
    assert only_rules(toc(nodes, [], [assumption([outcome], owner=None)])) == {
        ("ERROR", "ASSUMPTION_INCOMPLETE")
    }
    assert only_rules(toc(nodes, [], [assumption()])) == {("WARNING", "UNLINKED_ASSUMPTION")}
    assert toc(nodes, [], [assumption(kind="CONTEXT")]) == set()
    # FT-PLN-007: an invalid assumption flags the linked outcome, not the impact; the flag is a
    # warning the planner documents, so recorded actuals are untouched.
    invalid = assumption([outcome], status="INVALID")
    assert toc(nodes, [], [invalid]) == {("WARNING", "ASSUMPTION_INVALID", outcome["node_id"])}
    assert only_rules(toc(nodes, [], [assumption([outcome], review="2026-01-01")])) == {
        ("WARNING", "ASSUMPTION_REVIEW_DUE")
    }


def thresholds(scheme, on_track, at_risk):
    return {"scheme": scheme, "on_track": on_track, "at_risk": at_risk}


def banded(value, direction="HIGHER", kind="VALUE", scheme="ATTAINMENT_PERCENT", on="100", at="80", **extra):
    return goal(value, direction, kind, status_thresholds=thresholds(scheme, on, at), **extra)


def test_threshold_rules():
    assert threshold_issue(banded("100")) is None
    assert threshold_issue(goal("100")) is None
    assert threshold_issue(banded("100", on="80", at="100")) == "THRESHOLD_ORDER"
    assert threshold_issue(banded("10", "LOWER")) == "THRESHOLD_SCHEME_MISMATCH"
    assert threshold_issue(banded("10", "LOWER", scheme="DEVIATION", on="0", at="2")) is None
    assert threshold_issue(banded("10", "LOWER", scheme="DEVIATION", on="2", at="0")) == "THRESHOLD_ORDER"
    assert threshold_issue(banded("10", scheme="DEVIATION", on="-1", at="0")) == "THRESHOLD_NEGATIVE"
    assert threshold_issue(banded(None, "MILESTONE", "MILESTONE", "DEVIATION", "0", "1")) == (
        "THRESHOLDS_NOT_ALLOWED"
    )


def test_bands_follow_the_declared_thresholds_and_direction():
    # FSD 32.2 standard higher-target template: achieved at 100 percent, at risk from 80, below 80.
    higher = banded("100")
    assert progress(actual("120"), higher, None, 0)["band"] == "ON_TRACK"
    assert progress(actual("100"), higher, None, 0)["band"] == "ON_TRACK"
    assert progress(actual("80"), higher, None, 0)["band"] == "AT_RISK"
    assert progress(actual("79.999999999999"), higher, None, 0)["band"] == "OFF_TRACK"
    # Lower is better: the adverse deviation is above the target, a shortfall is on track.
    lower = banded("10", "LOWER", scheme="DEVIATION", on="0", at="2")
    assert progress(actual("8"), lower, None, 0)["band"] == "ON_TRACK"
    assert progress(actual("12"), lower, None, 0)["band"] == "AT_RISK"
    assert progress(actual("12.000000000001"), lower, None, 0)["band"] == "OFF_TRACK"
    # Range: the adverse distance is outside the bounds only.
    within = banded(None, "RANGE", "RANGE", "DEVIATION", "0", "5", low="10", high="20")
    assert progress(actual("20"), within, None, 0)["band"] == "ON_TRACK"
    assert progress(actual("25"), within, None, 0)["band"] == "AT_RISK"
    assert progress(actual("4"), within, None, 0)["band"] == "OFF_TRACK"
    # A higher target banded by deviation in the indicator's unit.
    by_unit = banded("100", scheme="DEVIATION", on="5", at="10")
    assert progress(actual("97"), by_unit, None, 0)["band"] == "ON_TRACK"
    assert progress(actual("90"), by_unit, None, 0)["band"] == "AT_RISK"


def test_bands_never_conceal_a_separately_visible_state():
    higher = banded("100")
    assert progress(actual("120"), goal("100"), None, 0)["band_reason"] == "NO_THRESHOLDS"
    blank = progress(actual(None, "MISSING"), higher, None, 0)
    assert (blank["band"], blank["band_reason"]) == (None, "NO_PRESENT_ACTUAL")
    none = progress(actual("120"), None, None, 0)
    assert (none["band"], none["band_reason"]) == (None, "NO_TARGET")
    stale = progress({**actual("120"), "stale": True}, higher, None, 0)
    assert (stale["band"], stale["band_reason"], stale["status"]) == (None, "STALE_ACTUAL", "ACHIEVED")
    zero = progress(actual("5"), banded("0"), None, 0)
    assert (zero["band"], zero["band_reason"], zero["reason_code"]) == (
        None,
        "ATTAINMENT_UNDEFINED",
        "ZERO_TARGET",
    )
    milestone = progress(
        actual("5"),
        goal(None, "MILESTONE", "MILESTONE", milestone_label="L", due_at="2026-06-01T00:00:00Z"),
        None,
        0,
    )
    assert (milestone["band"], milestone["band_reason"]) == (None, "MILESTONE_ASSESSMENT")
    assert performance_band(Decimal("5"), None) == (None, "NO_THRESHOLDS")
    big = "99999999999999999999999999.999999999999"
    overflow = safe_progress(actual(big), goal("-" + big), None, 2)
    assert (overflow["band"], overflow["band_reason"]) == (None, "ARITHMETIC_OVERFLOW")
