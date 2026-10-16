"""Whole positive forecast-scenario journey for FR-AI-017 / APL-718."""

from uuid import uuid4

from impact_api.contracts import validate
from test_dashboards import calculate, close, measure, ratio_source
from test_forms import temporary_grants
from test_live_application import expect
from test_measurement import get
from test_period_governance import all_items


def _official_result(live, numerator):
    programme, indicator, period, keys = measure(live, keys=1)
    ratio_source(live, indicator, keys[0], str(numerator), "100")
    calculate(live, indicator, period)
    close(live, programme, period)
    snapshot = next(
        item
        for item in get(live, "snapshots")["items"]
        if item["data"].get("programme_id") == programme["object_id"]
        and item["data"].get("period_id") == period["object_id"]
    )
    result = next(
        item
        for item in all_items(live, "calculated-results")
        if item["revision_id"] in snapshot["data"]["result_versions"]
    )
    assert result["data"]["mode"] == "OFFICIAL"
    assert result["data"]["value_state"] == "PRESENT"
    return result


def test_exact_official_revisions_create_bounded_and_versioned_planning_scenarios(live):
    results = [_official_result(live, value) for value in (10, 12, 15)]
    revoke = temporary_grants(live, "admin", ["calculated-results.read"])
    path = live.path("ai-enablement/forecasts")

    exploratory = expect(
        live.request(
            path,
            actor="admin",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "scenario_id": None,
                "label": "Sparse trend check",
                "horizon": 2,
                "method": "LINEAR_TREND_V1",
                "assumptions": ["No structural break during the two planning periods"],
                "input_result_revisions": [results[0]["revision_id"]],
            },
        ),
        200,
    )
    validate("AIForecast", exploratory)
    assert exploratory["status"] == "EXPLORATORY"
    assert exploratory["label"].startswith("Exploratory: ")
    assert exploratory["validation_history"]["evidence_sufficient"] is False
    assert exploratory["can_request_adoption"] is False
    refused = expect(
        live.request(
            path
            + f"/{exploratory['scenario_id']}/versions/{exploratory['version']}/actions/request-adoption",
            actor="admin",
            method="POST",
        ),
        409,
    )
    assert refused["reason_code"] == "EXPLORATORY_FORECAST_NOT_ADOPTABLE"

    scenario_id = str(uuid4())
    assumptions = ["Collection cadence remains stable", "No approved target is modified"]
    request = {
        "operation_id": str(uuid4()),
        "scenario_id": scenario_id,
        "label": "Three-period planning projection",
        "horizon": 3,
        "method": "LINEAR_TREND_V1",
        "assumptions": assumptions,
        "input_result_revisions": [item["revision_id"] for item in results],
    }
    # Closed operation validation must not consume the uncertain-operation identity.
    expect(live.request(path, actor="admin", method="POST", body={**request, "method": "EXECUTE_SQL"}), 422)
    first = expect(live.request(path, actor="admin", method="POST", body=request), 200)
    assert expect(live.request(path, actor="admin", method="POST", body=request), 200) == first
    validate("AIForecast", first)
    assert first["scenario_id"] == scenario_id and first["version"] == 1
    assert first["status"] == "PROJECTION" and first["label"].startswith("Scenario: ")
    assert first["assumptions"] == assumptions
    assert first["method"] == "LINEAR_TREND_V1"
    assert first["validation_history"] == {
        "method": "LINEAR_TREND_V1",
        "input_count": 3,
        "minimum_for_projection": 3,
        "evidence_sufficient": True,
        "uncertainty_method": "MAX_ABSOLUTE_DELTA_RESIDUAL_V1",
    }
    assert [item["revision_id"] for item in first["inputs"]] == request["input_result_revisions"]
    assert len(first["projections"]) == 3 and first["targets_changed"] is False

    exported = expect(
        live.request(path + f"/{scenario_id}/export", actor="admin", params={"version": 1}), 200
    )
    validate("AIForecastExport", exported)
    assert [series["kind"] for series in exported["series"]] == ["ACTUAL", "PROJECTION"]
    assert [item["revision_id"] for item in exported["series"][0]["values"]] == request[
        "input_result_revisions"
    ]
    assert exported["series"][1]["uncertainty"] == "MAX_ABSOLUTE_DELTA_RESIDUAL_V1"
    assert exported["approved_targets_changed"] is False

    adoption = expect(
        live.request(
            path + f"/{scenario_id}/versions/1/actions/request-adoption",
            actor="admin",
            method="POST",
        ),
        200,
    )
    validate("AIForecastAdoptionReview", adoption)
    assert adoption["state"] == "PENDING" and adoption["targets_changed"] is False

    second = expect(
        live.request(
            path,
            actor="admin",
            method="POST",
            body={**request, "operation_id": str(uuid4()), "assumptions": assumptions + ["Revised"]},
        ),
        200,
    )
    assert second["scenario_id"] == scenario_id and second["version"] == 2
    assert second["assumptions"][-1] == "Revised"
    historical = expect(live.request(path + f"/{scenario_id}", actor="admin", params={"version": 1}), 200)
    assert historical["assumptions"] == assumptions
    revoke()
