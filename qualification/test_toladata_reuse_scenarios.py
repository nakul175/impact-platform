"""New synthetic regressions inspired by Mercy Corps TolaData reporting scenarios.

Source: 7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d, indicators/tests/iptt_tests/scenarios.py,
indicators/queries/targets_queries.py and indicators/tests/test_generate_periodic_target.py.
These exercise Impact semantics; no upstream Django code or fixtures are imported.
"""

from datetime import datetime, timedelta

import pytest

from impact_api.domain import DomainError, calculate, disaggregate
from impact_api.planning import progress
from impact_api.reference_data import periods


def definition(rule="SUM", semantic="FLOW", kind="DECIMAL", **extra):
    return {
        "combination_rule": rule,
        "time_semantic": semantic,
        "measurement_type": kind,
        "unit": "synthetic units",
        "display_decimals": 2,
        **extra,
    }


def observation(value, at="2024-02-01T00:00:00Z", **extra):
    return {
        "value": value,
        "event_at": at,
        "approval_state": "APPROVED",
        "value_state": "PRESENT",
        **extra,
    }


def target(value):
    return {"value_state": "PRESENT", "target_kind": "POINT", "direction": "HIGHER", "value": value}


def test_empty_result_and_explicit_zero_have_different_report_meaning():
    empty = calculate(definition(), [])
    zero = calculate(definition(), [observation("0")])
    assert (empty["value_state"], empty["value"]) == ("UNDEFINED", None)
    assert (zero["value_state"], zero["value"]) == ("PRESENT", "0")
    assert progress(empty, target("100"), None, 2)["status"] == "NO_ACTUAL"
    assert progress(zero, target("100"), None, 2)["attainment_percent"] == "0.00"


def test_missing_and_unapproved_results_never_inflate_period_actual():
    rows = [
        observation("12"),
        observation(None, value_state="MISSING"),
        observation("500", approval_state="SUBMITTED"),
        observation("900", approval_state="RETURNED"),
    ]
    assert calculate(definition(), rows)["value"] == "12"


def test_period_flow_and_cumulative_position_cannot_share_a_summation_rule():
    rows = [observation("10"), observation("25", "2024-02-02T00:00:00Z")]
    assert calculate(definition(), rows)["value"] == "35"
    assert calculate(definition("LAST_VALID", "CUMULATIVE"), rows)["value"] == "25"
    with pytest.raises(DomainError) as caught:
        calculate(definition("SUM", "CUMULATIVE"), rows)
    assert caught.value.reason == "CONFIGURATION_NOT_IMPLEMENTED"


def test_percentage_actual_requires_components_and_is_not_latest_or_average():
    rows = [
        observation("50", numerator="50", denominator="100"),
        observation("10", "2024-02-02T00:00:00Z", numerator="1", denominator="10"),
    ]
    result = calculate(definition("POOLED_RATIO", "FLOW", "PERCENTAGE"), rows)
    assert (result["numerator"], result["denominator"], result["displayed_value"]) == ("51", "110", "46.36")
    with pytest.raises(DomainError):
        calculate(definition("POOLED_RATIO", "FLOW", "PERCENTAGE"), [observation("50")])


def test_zero_denominator_stays_undefined_through_target_comparison():
    result = calculate(
        definition("POOLED_RATIO", "FLOW", "PERCENTAGE"),
        [observation("0", numerator="0", denominator="0")],
    )
    assert result["reason_code"] == "ZERO_DENOMINATOR"
    compared = progress(result, target("80"), None, 2)
    assert compared["status"] == "NO_ACTUAL"
    assert compared["attainment_percent"] is None


def test_zero_target_and_missing_target_are_distinct_from_zero_actual():
    actual = calculate(definition(), [observation("12")])
    zero = progress(actual, target("0"), None, 2)
    missing = progress(actual, None, None, 2)
    assert (zero["attainment_percent"], zero["reason_code"]) == ("Undefined", "ZERO_TARGET")
    assert (missing["status"], missing["reason_code"]) == ("NO_TARGET", "NO_APPROVED_TARGET")


def test_attainment_uses_raw_decimal_and_is_not_capped_at_one_hundred():
    actual = calculate(definition(), [observation("3.005")])
    assert actual["displayed_value"] == "3.01"
    assert progress(actual, target("2"), None, 2)["attainment_percent"] == "150.25"


def test_cumulative_latest_uses_equivalent_instants_and_rejects_conflicts():
    rows = [observation("10"), observation("20", "2024-02-02T05:30:00+05:30")]
    assert calculate(definition("LAST_VALID", "CUMULATIVE"), list(reversed(rows)))["value"] == "20"
    rows.append(observation("21", "2024-02-02T00:00:00Z"))
    assert calculate(definition("LAST_VALID", "CUMULATIVE"), rows)["reason_code"] == "TIED_LATEST_VALUES"


def test_multiselect_disaggregations_are_not_a_second_total():
    dim = {
        "code": "SERVICE",
        "version": "1",
        "multiselect": True,
        "exhaustive": True,
        "categories": [{"code": "A"}, {"code": "B"}],
    }
    spec = definition(disaggregation={"dimensions": [dim]})
    rows = [observation("10", dimension_values={"SERVICE": "A|B"})]
    entries = disaggregate(spec, rows)
    assert [entry["value"] for entry in entries] == ["10", "10"]
    assert all(entry["additivity"] == "NONADDITIVE" for entry in entries)
    assert calculate(spec, rows)["value"] == "10"


def test_monthly_leap_day_and_year_rollover_have_exclusive_contiguous_ends():
    generated = list(periods("MONTHLY", "UTC", 2024, 2))
    feb = generated[1]
    assert feb == ("2024-02", "2024-02-01T00:00:00+00:00", "2024-03-01T00:00:00+00:00")
    assert datetime.fromisoformat(feb[2]) - datetime.fromisoformat(feb[1]) == timedelta(days=29)
    assert generated[11][2] == generated[12][1] == "2025-01-01T00:00:00+00:00"
    assert all(left[2] == right[1] for left, right in zip(generated, generated[1:]))


def test_quarterly_and_annual_boundaries_use_reporting_zone_not_utc_midnight():
    quarters = list(periods("QUARTERLY", "Asia/Kolkata", 2024, 1))
    annual = list(periods("ANNUAL", "Asia/Kolkata", 2024, 1))
    assert quarters[0] == ("2024-Q1", "2023-12-31T18:30:00+00:00", "2024-03-31T18:30:00+00:00")
    assert annual[0] == ("2024", quarters[0][1], quarters[-1][2])


def test_monthly_dst_boundary_preserves_local_midnight_and_contiguity():
    generated = list(periods("MONTHLY", "America/New_York", 2024, 1))
    march = generated[2]
    assert march == ("2024-03", "2024-03-01T05:00:00+00:00", "2024-04-01T04:00:00+00:00")
    assert march[2] == generated[3][1]
