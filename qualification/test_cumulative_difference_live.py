"""Positive user journey for FR-CAL-005 / APL-405 cumulative differences."""

from test_calculation_methods import build, calculate_result, observation_data
from test_live_application import expect
from test_measurement import approve, create, submit


def test_analyst_calculates_and_reproduces_cumulative_increment(live):
    """Positions 10, 15, 20 produce 20 from baseline zero, never their sum."""

    _, indicator, period, keys = build(
        live,
        scheme=None,
        measurement_type="COUNT",
        time_semantic="CUMULATIVE",
        combination_rule="CUMULATIVE_DIFFERENCE",
        cumulative_baseline="0",
        cumulative_baseline_basis="Programme register starts at zero before this reporting period.",
        display_decimals=0,
    )
    source_ids = []
    times = ["2026-07-15T12:00:00Z", "2026-08-15T12:00:00Z", "2026-09-15T12:00:00Z"]
    for key, value, event_at in zip(keys, ["10", "15", "20"], times):
        row = create(
            live,
            "observations",
            observation_data(indicator, key, value, {})
            | {"event_at": event_at, "captured_at": "2026-09-16T13:00:00Z"},
        )
        approve(live, submit(live, "observations", row))
        source_ids.append(row["object_id"])

    result = calculate_result(live, indicator, period)
    data = result["data"]
    assert data["value_state"] == "PRESENT"
    assert (data["value"], data["displayed_value"]) == ("20", "20")
    assert data["value"] != "45"
    assert data["formula"]["statistic_label"] == "CUMULATIVE_DIFFERENCE"
    assert data["formula"]["cumulative_baseline"] == "0"
    assert data["formula"]["cumulative_baseline_basis"].startswith("Programme register")
    assert data["cumulative_increments"] == [
        {"event_at": times[0], "position": "10", "increment": "10"},
        {"event_at": times[1], "position": "15", "increment": "5"},
        {"event_at": times[2], "position": "20", "increment": "5"},
    ]
    assert "CUMULATIVE_INCREMENT" in {item["code"] for item in data["limitations"]}

    reproduced = expect(
        live.request(live.path("calculated-results", result["object_id"]) + "/reproduction"), 200
    )
    assert reproduced["exact_match"] is True
    assert reproduced["stored"] == reproduced["recomputed"]
    assert reproduced["stored"]["cumulative_increments"] == data["cumulative_increments"]
    assert {source["object_id"] for source in reproduced["sources"]} == set(source_ids)
    assert all(source["disposition"] == "INCLUDED" for source in reproduced["sources"])
