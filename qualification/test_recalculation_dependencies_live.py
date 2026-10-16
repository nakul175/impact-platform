"""APL-421 / FR-CAL-011 live correction and recalculation dependency journey."""
# ruff: noqa: F811

from test_changes import propose
from test_live_application import cmd, expect
from test_measurement import action, approve, get, observation, result, setup, submit  # noqa: F401


def test_approved_correction_records_dependencies_and_recalculates_exactly_once(live, setup):
    _, indicator, plan, period = setup()
    source = observation(live, indicator, plan["data"]["obligations"][0]["source_key"])
    approve(live, submit(live, "observations", source))
    source = get(live, "observations", source["object_id"])
    original = result(live, indicator, period)

    correction = propose(
        live,
        source,
        "Observation",
        {"value": "25", "source_version": "2"},
    )
    approve(live, submit(live, "measurement-changes", correction))
    assert get(live, "calculated-results", original["object_id"])["data"]["freshness"]["stale"]

    task = next(
        item
        for item in get(live, "work-items")["items"]
        if item["data"].get("calculation", {}).get("indicator_id") == indicator["object_id"]
        and item["data"]["calculation"]["period_id"] == period["object_id"]
    )
    calculation = task["data"]["calculation"]
    assert calculation["state"] == "PENDING"
    assert calculation["affected_result_count"] == 1
    assert calculation["dependency_counts"] == {"LIVE_DASHBOARD": 1, "RESULT": 1}

    body = cmd({}, task["revision_id"])
    completed = action(live, "work-items", task, "recalculate", body=body)
    repeated = action(live, "work-items", task, "recalculate", body=body)
    assert repeated == completed
    assert completed["business_state"] == "Completed"

    current = get(live, "work-items", task["object_id"])
    assert current["data"]["calculation"]["state"] == "RECALCULATED"
    assert current["data"]["calculation"]["dependency_counts"] == {
        "LIVE_DASHBOARD": 1,
        "RESULT": 1,
    }
    replacement = get(live, "calculated-results", completed["result_id"])
    assert replacement["data"]["displayed_value"] == "25"
    assert replacement["data"]["freshness"]["stale"] is False
    assert get(live, "calculated-results", original["object_id"])["data"]["freshness"]["stale"]

    with live.db() as connection:
        rows = connection.execute(
            "SELECT state,replacement_result_id FROM impact.calculation_invalidation "
            "WHERE tenant_id=%s AND work_item_id=%s",
            (live.fixture["tenant_a"], task["object_id"]),
        ).fetchall()
    assert len(rows) == 1
    assert rows[0]["state"] == "RECALCULATED"
    assert str(rows[0]["replacement_result_id"]) == completed["result_id"]
    expect(
        live.request(
            live.path("calculated-results", completed["result_id"], tenant=live.fixture["tenant_b"]),
            actor="other_tenant",
        ),
        404,
    )
