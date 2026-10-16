"""Positive user journey for FR-CAL-016 / APL-611 governed statistical interpretation."""

from impact_api.contracts import validate
from test_calculation_methods import observation_data
from test_dashboards import calculate, measure
from test_live_application import expect
from test_measurement import approve, create, get, submit


def test_independently_approved_raw_values_produce_a_labelled_sample_median(live):
    _, indicator, period, keys = measure(
        live,
        keys=5,
        measurement_type="DECIMAL",
        combination_rule="MEDIAN",
        unit="score",
        display_decimals=0,
        statistical_interpretation={
            "sample_basis": "RAW_VALUES",
            "weighting": "NONE",
            "uncertainty_method": "NONE",
            "uncertainty_level": None,
            "population_interpretation": "SAMPLE",
            "expansion_method": None,
        },
    )
    observations = []
    for key, value in zip(keys, ["1", "2", "100", "3", "4"], strict=True):
        draft = create(live, "observations", observation_data(indicator, key, value, {}))
        approve(live, submit(live, "observations", draft))
        observations.append(get(live, "observations", draft["object_id"]))

    result = calculate(live, indicator, period)
    assert result["data"]["value"] == "3"
    assert result["data"]["displayed_value"] == "3"
    assert result["data"]["formula"]["statistic_label"] == "POOLED_MEDIAN"
    assert result["data"]["formula"]["sample_basis"] == "RAW_VALUES"
    assert result["data"]["formula"]["population_interpretation"] == "SAMPLE"
    assert {item["code"] for item in result["data"]["limitations"]} == {
        "POOLED_MEDIAN",
        "SAMPLE_NOT_POPULATION",
        "UNCERTAINTY_NOT_ESTIMATED",
        "PERIOD_CLOSE_REQUIRED",
    }

    reproduced = expect(
        live.request(live.path("calculated-results", result["object_id"]) + "/reproduction"),
        200,
    )
    validate("CalculationReproduction", reproduced)
    assert reproduced["exact_match"] is True
    assert reproduced["formula"]["statistic_label"] == "POOLED_MEDIAN"
    assert {source["revision_id"] for source in reproduced["sources"]} == {
        row["revision_id"] for row in observations
    }
    expect(
        live.request(
            live.path("calculated-results", result["object_id"], tenant=live.fixture["tenant_b"])
            + "/reproduction",
            actor="other_tenant",
        ),
        404,
    )
