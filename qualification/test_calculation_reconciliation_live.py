"""Positive user journey for FR-CAL-015 / APL-424 calculation reconciliation."""

from story_read_recovery import assert_read_recovery

from impact_api.contracts import validate
from test_dashboards import calculate, measure, ratio_source
from test_live_application import expect


def test_analyst_explains_and_reconciles_a_newly_included_approved_source(live):
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "2", "4")
    earlier = calculate(live, indicator, period)

    explanation = expect(
        live.request(live.path("calculated-results", earlier["object_id"]) + "/explanation"),
        200,
    )
    validate("CalculationExplanation", explanation)
    assert explanation["result_revision"] == earlier["revision_id"]
    assert explanation["source_set"]["included_count"] == 1
    assert explanation["source_set"]["excluded_count"] == 0
    assert explanation["formula"]["method"] == "POOLED_RATIO"
    assert explanation["coverage"]["complete"] is False

    ratio_source(live, indicator, keys[1], "3", "4")
    later = calculate(live, indicator, period)
    compared = expect(
        live.request(
            live.path("calculated-results", earlier["object_id"]) + "/comparison/" + later["object_id"]
        ),
        200,
    )
    validate("CalculationComparison", compared)
    assert compared["earlier_result_revision"] == earlier["revision_id"]
    assert compared["later_result_revision"] == later["revision_id"]
    assert compared["difference"] == "12.5"
    assert compared["reconciled"] is True
    assert compared["approval_blocked"] is False
    assert [(item["category"], item["effect"], item["reference_state"]) for item in compared["causes"]] == [
        ("SOURCE", "12.5", "PERMITTED"),
        ("FILTER", "0", "PERMITTED"),
    ]
    expect(
        live.request(
            live.path("calculated-results", earlier["object_id"], tenant=live.fixture["tenant_b"])
            + "/explanation",
            actor="other_tenant",
        ),
        404,
    )
    assert_read_recovery(
        live,
        "calculated-results",
        earlier["object_id"],
        "/comparison/" + later["object_id"],
        expected=compared,
    )
