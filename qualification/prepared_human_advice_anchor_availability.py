"""Strict old-pin privacy diagnostic; storage-valid append-only negative fixtures.

This is not evidence of public case creation or an operated privacy-removal flow.
No old row changes, FK bypass, trigger disabling, or invented second person.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest

from human_advice_anchor_fixtures import case_pointer_visibility, unavailable_anchor_case
from test_human_advice_live import ROUTE
from test_live_application import expect


@pytest.mark.parametrize("restriction", ["RESTRICTED", "REMOVED"])
def test_unavailable_exact_plan_pin_hides_case_history_list_replay_and_all_pointers(live, restriction):
    fixture = unavailable_anchor_case(live, restriction)
    case, request = fixture["case"], fixture["request"]
    plan_path = live.path("ai-enablement/plans", fixture["original"]["object_id"])
    current = expect(live.request(plan_path, actor="admin"), 200)
    assert current["revision_id"] == fixture["newer"]
    expect(live.request(plan_path + "/revisions/" + fixture["older"] + "/guidance", actor="admin"), 404)
    # A readable older AVAILABLE selector remains noncurrent; the public create
    # command must reject it independently of the unavailable-pin boundary.
    older_available_request = {
        **request,
        "operation_id": str(uuid4()),
        "data": {**request["data"], "context_plan_revision": fixture["original"]["revision_id"]},
    }
    expect(live.request(live.path(ROUTE), actor="admin", method="POST", body=older_available_request), 409)
    path = live.path(ROUTE, case["object_id"])
    calls = {
        "requester_current": live.request(path, actor="admin"),
        "adviser_current": live.request(path, actor="reviewer"),
        "history": live.request(path + "/revisions", actor="admin"),
        "exact_revision": live.request(path + "/revisions/" + case["revision_id"], actor="admin"),
        "receipt_replay": live.request(live.path(ROUTE), actor="admin", method="POST", body=request),
    }
    listing = expect(live.request(live.path(ROUTE), actor="admin"), 200)
    pointers = case_pointer_visibility(live, fixture)
    observation = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Storage-valid synthetic negative fixture with appended unavailable old pin and readable new head. No public API creation/retention/erasure workflow claim; immutable guards/FKs stay enabled.",
        "old_pin_state": restriction,
        "current_plan_status": 200,
        "older_guidance_status": 404,
        "fresh_noncurrent_available_anchor_status": 409,
        "case_statuses": {key: response.status_code for key, response in calls.items()},
        "case_listed": case["object_id"] in [item["object_id"] for item in listing["items"]],
        "pointer_rows_visible": pointers,
    }
    if report := os.environ.get("TOLA_ADVICE_ANCHOR_DIAGNOSTIC_REPORT"):
        target = Path(report)
        existing = json.loads(target.read_text()) if target.exists() else {}
        existing[restriction] = observation
        target.write_text(json.dumps(existing, indent=2) + "\n")
    assert all(response.status_code == 404 for response in calls.values()), observation
    assert observation["case_listed"] is False, observation
    assert not any(pointers.values()), observation
