from datetime import datetime, timezone

from impact_api.dashboard_alerts import advance, evaluate


NOW = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
RULE = {
    "operator": "LT",
    "threshold": "10",
    "minimum_coverage": 75,
    "max_freshness_seconds": 3600,
}


def result(**updates):
    payload = {
        "value_state": "PRESENT",
        "value": "9",
        "mode": "OFFICIAL",
        "freshness": {"calculated_at": "2026-10-15T11:30:00+00:00", "stale": False},
        "coverage": {"approval_percent": 100},
    }
    payload.update(updates)
    return {"payload": payload}


def test_missing_and_absent_values_never_become_threshold_zero():
    assert evaluate(RULE, None, NOW) == ("MISSINGNESS", "RESULT_ABSENT")
    assert evaluate(RULE, result(value_state="MISSING", value=None), NOW) == (
        "MISSINGNESS",
        "VALUE_NOT_PRESENT",
    )


def test_stale_coverage_provisional_and_threshold_outcomes_are_distinct():
    assert evaluate(RULE, result(freshness={"calculated_at": "2026-10-15T09:00:00+00:00"}), NOW) == (
        "STALE_INPUT",
        "RESULT_STALE",
    )
    assert evaluate(RULE, result(coverage={"approval_percent": 50}), NOW) == (
        "MISSINGNESS",
        "COVERAGE_BELOW_MINIMUM",
    )
    assert evaluate(RULE, result(mode="PROVISIONAL"), NOW) == (
        "NO_TRIGGER",
        "OFFICIAL_RESULT_REQUIRED",
    )
    assert evaluate(RULE, result(), NOW) == ("THRESHOLD", "CONDITION_MET")
    assert evaluate(RULE, result(value="10"), NOW) == ("NO_TRIGGER", "CONDITION_NOT_MET")
    assert evaluate({**RULE, "operator": "GT"}, result(value="11"), NOW) == (
        "THRESHOLD",
        "CONDITION_MET",
    )


def test_calendar_month_cadence_preserves_month_end_safely():
    assert advance(datetime(2026, 1, 31, tzinfo=timezone.utc), "MONTHLY") == datetime(
        2026, 2, 28, tzinfo=timezone.utc
    )
    assert advance(datetime(2026, 2, 28, tzinfo=timezone.utc), "MONTHLY") == datetime(
        2026, 3, 28, tzinfo=timezone.utc
    )
