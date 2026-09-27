"""Governed eligibility exceptions, personal notices and recalculation recovery."""
# ruff: noqa: F811

from datetime import datetime, timezone

from test_live_application import cmd, expect
from test_measurement import setup, get, action, submit, approve, observation, result  # noqa: F401
from test_changes import propose
from test_period_governance import request_close


def test_reviewed_exclusion_preserves_denominator_history_and_allows_close(live, setup):
    programme, indicator, plan, period = setup()
    obligations = [dict(item) for item in plan["data"]["obligations"]]
    obligations[-1].update(
        eligibility="EXCEPTED",
        exclusion_reason="Partner ceased eligible operations before the reporting deadline.",
        exclusion_effective_at=datetime.now(timezone.utc).isoformat(),
    )
    change = propose(live, plan, "CollectionPlan", {"obligations": obligations})
    approve(live, submit(live, "measurement-changes", change))
    amended = get(live, "collection-plans", plan["object_id"])
    assert amended["data"]["obligations"][-1]["eligibility"] == "EXCEPTED"

    for obligation in amended["data"]["obligations"][:-1]:
        row = observation(live, indicator, obligation["source_key"])
        approve(live, submit(live, "observations", row))
    calculated = result(live, indicator, period)
    coverage = calculated["data"]["coverage"]
    assert coverage["expected_count"] == 5
    assert coverage["required_count"] == 4
    assert coverage["excepted_count"] == 1
    assert coverage["approved_count"] == 4
    assert coverage["approval_percent"] == "100.00"
    assert coverage["complete"]
    assert coverage["obligations"][-1]["status"] == "EXCEPTED"
    assert coverage["obligations"][-1]["exclusion_reason"].startswith("Partner ceased")

    workflow = request_close(live, programme, period)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    assert candidate["record"]["data"]["blockers"] == []
    approve(live, workflow)
    snapshot = next(
        item
        for item in get(live, "snapshots")["items"]
        if item["data"].get("programme_id") == programme["object_id"]
        and item["data"]["period_id"] == period["object_id"]
    )
    assert snapshot["lifecycle_state"] == "Locked"


def test_exclusion_requires_justification_and_cannot_remove_every_requirement(live, setup):
    _, _, plan, _ = setup()
    missing_reason = [dict(item) for item in plan["data"]["obligations"]]
    missing_reason[-1]["eligibility"] = "EXCEPTED"
    denied = expect(
        live.request(
            live.path("measurement-changes"),
            method="POST",
            body=cmd(
                {
                    "target_kind": "CollectionPlan",
                    "target_id": plan["object_id"],
                    "target_revision": plan["revision_id"],
                    "reason": "Unsupported exception",
                    "proposed_data": {"obligations": missing_reason},
                }
            ),
        ),
        422,
    )
    assert denied["field_errors"]

    all_excepted = [
        {
            **item,
            "eligibility": "EXCEPTED",
            "exclusion_reason": "Reviewed eligibility exception.",
            "exclusion_effective_at": datetime.now(timezone.utc).isoformat(),
        }
        for item in plan["data"]["obligations"]
    ]
    denied = expect(
        live.request(
            live.path("measurement-changes"),
            method="POST",
            body=cmd(
                {
                    "target_kind": "CollectionPlan",
                    "target_id": plan["object_id"],
                    "target_revision": plan["revision_id"],
                    "reason": "Attempt to erase denominator",
                    "proposed_data": {"obligations": all_excepted},
                }
            ),
        ),
        422,
    )
    assert denied["reason_code"] == "AT_LEAST_ONE_REQUIRED_OBLIGATION"


def test_correction_creates_personal_work_notice_and_recalculation_resolves_it(live, setup):
    _, indicator, plan, period = setup()
    source = observation(live, indicator, plan["data"]["obligations"][0]["source_key"])
    approve(live, submit(live, "observations", source))
    source = get(live, "observations", source["object_id"])
    old_result = result(live, indicator, period)

    change = propose(live, source, "Observation", {"value": "25", "source_version": "2"})
    approve(live, submit(live, "measurement-changes", change))
    assert get(live, "calculated-results", old_result["object_id"])["data"]["freshness"]["stale"]

    tasks = get(live, "work-items")["items"]
    task = next(
        item
        for item in tasks
        if item["data"].get("calculation", {}).get("indicator_id") == indicator["object_id"]
        and item["data"]["calculation"]["period_id"] == period["object_id"]
    )
    assert task["lifecycle_state"] == "Open"
    assert task["data"]["calculation"]["state"] == "PENDING"
    assert task["data"]["calculation"]["affected_result_count"] >= 1
    expect(live.request(live.path("work-items", task["object_id"]), actor="reviewer"), 404)

    notices = get(live, "notifications")["items"]
    notice = next(
        item
        for item in notices
        if item["data"]["safe_reference"] == task["object_id"]
        and item["data"]["notice_class"] == "CALCULATION_STALE"
    )
    assert notice["data"]["acknowledged_at"] is None
    action(live, "notifications", notice, "acknowledge")
    assert get(live, "notifications", notice["object_id"])["data"]["acknowledged_at"]
    assert get(live, "work-items", task["object_id"])["lifecycle_state"] == "Open"

    body = cmd({}, task["revision_id"])
    completed = action(live, "work-items", task, "recalculate", body=body)
    assert action(live, "work-items", task, "recalculate", body=body) == completed
    assert completed["business_state"] == "Completed"
    current = get(live, "work-items", task["object_id"])
    assert current["lifecycle_state"] == "Completed"
    assert current["data"]["calculation"]["state"] == "RECALCULATED"
    replacement = get(live, "calculated-results", completed["result_id"])
    assert replacement["data"]["displayed_value"] == "25"
    assert replacement["data"]["freshness"]["stale"] is False
    assert get(live, "calculated-results", old_result["object_id"])["data"]["freshness"]["stale"]

    with live.db() as connection:
        states = connection.execute(
            "SELECT DISTINCT state FROM impact.calculation_invalidation WHERE work_item_id=%s",
            (task["object_id"],),
        ).fetchall()
        assert {row["state"] for row in states} == {"RECALCULATED"}
        connection.execute("SET LOCAL ROLE impact_app")
        connection.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
        assert (
            connection.execute(
                "SELECT count(*) AS n FROM impact.calculation_invalidation WHERE tenant_id=%s",
                (live.fixture["tenant_a"],),
            ).fetchone()["n"]
            == 0
        )
