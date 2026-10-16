"""Positive user journey for FR-CAL-008 / APL-408 calculation coverage status."""

from story_read_recovery import assert_read_recovery

from test_calculation_methods import observation_data
from test_dashboards import calculate, measure, ratio_source
from test_live_application import expect
from test_measurement import create, get, submit


def test_calculation_keeps_approved_pending_and_missing_coverage_explicit(live):
    _, indicator, period, keys = measure(live, keys=5)
    for key, numerator in zip(keys[:3], ["10", "20", "30"]):
        ratio_source(live, indicator, key, numerator, "100")

    pending = create(
        live,
        "observations",
        observation_data(
            indicator,
            keys[3],
            "0.4",
            {},
            numerator="40",
            denominator="100",
        ),
    )
    submit(live, "observations", pending)

    result = calculate(live, indicator, period)
    current = get(live, "calculated-results", result["object_id"])
    coverage = current["data"]["coverage"]
    assert current["revision_id"] == result["revision_id"]
    assert current["data"]["value"] == "20"
    assert coverage["coverage_state"] == "PARTIAL"
    assert coverage["approval_percent"] == "60.00"
    assert coverage["approved_count"] == 3
    assert coverage["pending_count"] == 1
    assert coverage["missing_count"] == 1
    assert coverage["plan_revision"]
    assert "pending, missing or excluded" in coverage["coverage_reason"]
    assert "PARTIAL_COVERAGE" in {limitation["code"] for limitation in current["data"]["limitations"]}
    expect(
        live.request(
            live.path("calculated-results", result["object_id"], tenant=live.fixture["tenant_b"]),
            actor="other_tenant",
        ),
        404,
    )
    assert_read_recovery(live, "calculated-results", result["object_id"], expected=current)
