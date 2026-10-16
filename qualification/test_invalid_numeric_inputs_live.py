"""APL-415 / FR-CAL-010 live positive journey for governed numeric boundaries."""

from test_calculation_methods import build, observation_data
from test_live_application import cmd, expect
from test_measurement import action, approve, create, get, submit


def test_approved_negative_adjustment_calculates_while_invalid_counts_are_refused(live):
    basis = "Approved refund and correction adjustment."
    definition, indicator, period, keys = build(
        live,
        scheme=None,
        measurement_type="DECIMAL",
        combination_rule="SUM",
        allows_negative_adjustments=True,
        negative_adjustment_basis=basis,
    )
    for key, value in zip(keys[:2], ["8", "-3"]):
        row = create(live, "observations", observation_data(indicator, key, value, {}))
        approve(live, submit(live, "observations", row))

    receipt = action(
        live,
        "indicator-instances",
        indicator,
        "calculate",
        {"period_id": period["object_id"]},
    )
    calculated = get(live, "calculated-results", receipt["object_id"])["data"]
    assert calculated["value_state"] == "PRESENT"
    assert calculated["value"] == "5"
    assert calculated["displayed_value"] == "5"
    assert calculated["formula"]["allows_negative_adjustments"] is True
    assert calculated["formula"]["negative_adjustment_basis"] == basis
    assert definition["data"]["allows_negative_adjustments"] is True

    _, count_indicator, _, count_keys = build(
        live,
        scheme=None,
        measurement_type="COUNT",
        combination_rule="COUNT",
        time_semantic="EVENT",
    )
    invalid = create(
        live,
        "observations",
        observation_data(count_indicator, count_keys[0], "-2", {}),
    )
    template = get(live, "workflow-templates")["items"][0]
    refused = expect(
        live.request(
            live.path("observations", invalid["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": template["revision_id"]}, invalid["revision_id"]),
        ),
        422,
    )
    assert refused["reason_code"] == "NEGATIVE_COUNT"
    assert get(live, "observations", invalid["object_id"])["lifecycle_state"] == "Draft"


def test_zero_denominator_is_durable_undefined_result_not_successful_zero(live):
    _, indicator, period, keys = build(
        live,
        scheme=None,
        measurement_type="PERCENTAGE",
        combination_rule="POOLED_RATIO",
        numerator_meaning="Eligible reached",
        denominator_meaning="Eligible population",
    )
    for key in keys:
        row = create(
            live,
            "observations",
            observation_data(indicator, key, "0", {}, numerator="0", denominator="0"),
        )
        approve(live, submit(live, "observations", row))

    receipt = action(
        live,
        "indicator-instances",
        indicator,
        "calculate",
        {"period_id": period["object_id"]},
    )
    calculated = get(live, "calculated-results", receipt["object_id"])["data"]
    assert calculated["value_state"] == "UNDEFINED"
    assert calculated["reason_code"] == "ZERO_DENOMINATOR"
    assert calculated["value"] is None
    assert calculated["displayed_value"] == "Undefined"


def test_ratio_quantity_and_percentage_bound_refusals_remain_specific(live):
    _, indicator, _, keys = build(
        live,
        scheme=None,
        measurement_type="PERCENTAGE",
        combination_rule="POOLED_RATIO",
        numerator_meaning="Eligible reached",
        denominator_meaning="Eligible population",
    )
    template = get(live, "workflow-templates")["items"][0]
    negative = expect(
        live.request(
            live.path("observations"),
            method="POST",
            body=cmd(
                observation_data(
                    indicator,
                    keys[0],
                    "0",
                    {},
                    numerator="-1",
                    denominator="10",
                )
            ),
        ),
        422,
    )
    assert negative["reason_code"] == "NEGATIVE_RATIO_QUANTITY"

    overflow = create(
        live,
        "observations",
        observation_data(indicator, keys[1], "0", {}, numerator="11", denominator="10"),
    )
    refused = expect(
        live.request(
            live.path("observations", overflow["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": template["revision_id"]}, overflow["revision_id"]),
        ),
        422,
    )
    assert refused["reason_code"] == "PERCENTAGE_OUT_OF_RANGE"
    assert get(live, "observations", overflow["object_id"])["lifecycle_state"] == "Draft"
