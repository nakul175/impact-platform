"""Positive user journey for FR-CAL-003 / APL-402 pooled ratios."""

from test_calculation_methods import build, calculate_result, observation_data
from test_live_application import expect
from test_measurement import approve, create, submit


def test_analyst_calculates_denominator_weighted_ratio_from_approved_components(live):
    """Pool 50/100 and 1/10 as 51/110, then reproduce the exact governed result."""

    _, indicator, period, keys = build(
        live,
        scheme=None,
        measurement_type="PERCENTAGE",
        combination_rule="POOLED_RATIO",
        numerator_meaning="Households with safe water",
        denominator_meaning="Households visited",
        display_decimals=2,
    )
    sources = []
    for key, numerator, denominator in zip(keys, ["50", "1"], ["100", "10"]):
        row = create(
            live,
            "observations",
            observation_data(indicator, key, "0", {}) | {"numerator": numerator, "denominator": denominator},
        )
        approve(live, submit(live, "observations", row))
        sources.append(row["object_id"])

    result = calculate_result(live, indicator, period)
    data = result["data"]
    assert data["value_state"] == "PRESENT"
    assert (data["numerator"], data["denominator"]) == ("51", "110")
    assert (data["value"], data["displayed_value"]) == ("46.363636363636", "46.36")
    assert data["displayed_value"] != "30.00"
    assert data["formula"]["statistic_label"] == "POOLED_RATIO"
    assert data["formula"]["weighting_basis"] == "DENOMINATOR_WEIGHTED"
    assert data["formula"]["component_requirement"] == "NUMERATOR_AND_DENOMINATOR_REQUIRED"
    assert data["formula"]["multiplier_stage"] == "AFTER_POOLING"

    reproduced = expect(
        live.request(live.path("calculated-results", result["object_id"]) + "/reproduction"),
        200,
    )
    assert reproduced["exact_match"] is True
    assert reproduced["stored"] == reproduced["recomputed"]
    assert (reproduced["stored"]["numerator"], reproduced["stored"]["denominator"]) == ("51", "110")
    assert {source["object_id"] for source in reproduced["sources"]} == set(sources)
    assert all(source["disposition"] == "INCLUDED" for source in reproduced["sources"])
    expect(
        live.request(
            live.path("calculated-results", result["object_id"], tenant=live.fixture["tenant_b"])
            + "/reproduction",
            actor="other_tenant",
        ),
        404,
    )
