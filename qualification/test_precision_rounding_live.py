"""Positive user journey for FR-CAL-009 / APL-411 precision and output-only rounding."""

from test_calculation_methods import build, observation_data
from test_measurement import action, approve, create, get, submit


def test_three_exact_inputs_round_only_after_the_unrounded_sum_is_stored(live):
    _, indicator, period, keys = build(
        live,
        scheme=None,
        measurement_type="DECIMAL",
        combination_rule="SUM",
        display_decimals=2,
    )
    for key in keys:
        observation = create(
            live,
            "observations",
            observation_data(indicator, key, "0.335", {}),
        )
        approve(live, submit(live, "observations", observation))

    receipt = action(
        live,
        "indicator-instances",
        indicator,
        "calculate",
        {"period_id": period["object_id"]},
    )
    result = get(live, "calculated-results", receipt["object_id"])
    data = result["data"]
    assert data["value"] == "1.005"
    assert data["displayed_value"] == "1.01"
    assert data["calculation_precision_digits"] == 100
    assert data["formula"]["input_scale_digits"] == 12
    assert data["formula"]["stored_scale_digits"] == 12
    assert data["formula"]["rounding_rule"] == "HALF_UP"
    assert data["formula"]["rounding_boundary"] == "OUTPUT_ONLY"
    assert data["lineage_manifest_id"]
