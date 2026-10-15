"""US-DX-03 / APL-364: locked baseline metrics for an exact priority problem."""

from copy import deepcopy
from datetime import datetime
from uuid import uuid4

import pytest

from impact_api.contracts import validate
from test_ai_diagnosis_live import action as diagnosis_action
from test_ai_diagnosis_live import get as get_diagnosis, save as save_diagnosis
from test_live_application import expect

ROUTE = "ai-enablement/problem-baselines"
METRICS = ("time", "cost", "quality", "reach")


def completed_diagnosis(live):
    draft = save_diagnosis(live)
    completed = diagnosis_action(live, draft, "complete")
    return completed, get_diagnosis(live, completed)


def measure(value, unit, basis):
    return {
        "value": value,
        "unit": unit,
        "basis": basis,
        "observed_from": "2026-01-01",
        "observed_to": "2026-03-31",
    }


def baseline_data(completed, diagnosis_row, metrics=None):
    problem = diagnosis_row["data"]["problems"][0]
    return {
        "diagnosis_id": completed["object_id"],
        "diagnosis_revision": completed["revision_id"],
        "problem_id": problem["problem_id"],
        "title": "Synthetic baseline for " + problem["affected_area"],
        "metrics": metrics
        if metrics is not None
        else {
            "time": measure("120.00", "staff-minutes/week", "Synthetic staff exercise"),
            "cost": measure("3500.50", "INR/month", "Synthetic operating estimate"),
            "quality": measure("72.5", "percent", "Synthetic checklist score"),
            "reach": measure("18", "people/month", "Synthetic service register"),
        },
        "supporting_evidence": "Synthetic baseline interview and operating log.",
        "evidence_references": [],
    }


def create(live, data):
    result = expect(
        live.request(
            live.path(ROUTE),
            actor="admin",
            method="POST",
            body={"operation_id": str(uuid4()), "data": data},
        ),
        201,
    )
    validate("AIProblemBaselineReceipt", result)
    return result


def get(live, row, **kwargs):
    result = expect(live.request(live.path(ROUTE, row["object_id"]), actor="admin", **kwargs), 200)
    validate("AIProblemBaseline", result)
    return result


def baseline_counts(live, object_id):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return {
            "revisions": c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
                (tenant, object_id),
            ).fetchone()["n"],
            "locks": c.execute(
                "SELECT count(*) AS n FROM impact.problem_baseline_lock WHERE tenant_id=%s AND object_id=%s",
                (tenant, object_id),
            ).fetchone()["n"],
        }


def test_problem_baseline_kind_and_worker_fences_are_installed(live):
    with live.db() as c:
        constraint = c.execute(
            "SELECT pg_get_constraintdef(oid) AS definition FROM pg_constraint "
            "WHERE conrelid='impact.object_registry'::regclass "
            "AND conname='object_registry_object_type_check'"
        ).fetchone()["definition"]
        assert "AIProblemBaseline" in constraint
        policies = c.execute(
            "SELECT polname,polpermissive FROM pg_policy "
            "WHERE polrelid IN ('impact.object_registry'::regclass,'impact.object_revision'::regclass) "
            "AND polname IN ('worker_problem_baseline_registry_fence',"
            "'worker_problem_baseline_revision_fence') ORDER BY polname"
        ).fetchall()
        assert [row["polname"] for row in policies] == [
            "worker_problem_baseline_registry_fence",
            "worker_problem_baseline_revision_fence",
        ]
        assert all(not row["polpermissive"] for row in policies)


def test_problem_baseline_draft_preserves_partial_exact_metrics(live):
    completed, diagnosis_row = completed_diagnosis(live)
    partial = {"time": measure("0", "staff-minutes/week", "Measured synthetic zero")}
    row = create(live, baseline_data(completed, diagnosis_row, partial))
    current = get(live, row)
    assert current["business_state"] == "Draft"
    assert current["data"]["metrics"] == partial
    assert current["data"]["diagnosis_revision"] == completed["revision_id"]
    assert "locked_at" not in current["data"] and "locked_by" not in current["data"]


@pytest.mark.parametrize("missing", METRICS)
def test_problem_baseline_refuses_incomplete_lock_without_writing(live, missing):
    completed, diagnosis_row = completed_diagnosis(live)
    data = baseline_data(completed, diagnosis_row)
    del data["metrics"][missing]
    row = create(live, data)
    before = baseline_counts(live, row["object_id"])
    refusal = expect(
        live.request(
            live.path(ROUTE, row["object_id"]) + "/actions/lock",
            actor="admin",
            method="POST",
            body={"operation_id": str(uuid4()), "expected_revision": row["revision_id"]},
        ),
        422,
    )
    assert refusal["code"] == "VALIDATION_FAILED"
    assert refusal["reason_code"] == "PROBLEM_BASELINE_INCOMPLETE"
    assert any(item["path"] == "metrics." + missing for item in refusal["field_errors"])
    assert baseline_counts(live, row["object_id"]) == before
    assert get(live, row)["business_state"] == "Draft"


def test_problem_baseline_lock_is_server_dated_immutable_and_exactly_replayable(live):
    completed, diagnosis_row = completed_diagnosis(live)
    data = baseline_data(completed, diagnosis_row)
    row = create(live, data)
    lock_body = {"operation_id": str(uuid4()), "expected_revision": row["revision_id"]}
    locked = expect(
        live.request(
            live.path(ROUTE, row["object_id"]) + "/actions/lock",
            actor="admin",
            method="POST",
            body=lock_body,
        ),
        200,
    )
    validate("AIProblemBaselineReceipt", locked)
    current = get(live, locked)
    assert current["business_state"] == "Locked"
    assert current["data"]["metrics"] == data["metrics"]
    assert current["data"]["locked_by"] == live.fixture["actors"]["admin"]["principal_id"]
    assert datetime.fromisoformat(current["data"]["locked_at"].replace("Z", "+00:00")).tzinfo
    assert baseline_counts(live, row["object_id"]) == {"revisions": 2, "locks": 1}

    replay = expect(
        live.request(
            live.path(ROUTE, row["object_id"]) + "/actions/lock",
            actor="admin",
            method="POST",
            body=lock_body,
        ),
        200,
    )
    assert replay == locked
    assert baseline_counts(live, row["object_id"]) == {"revisions": 2, "locks": 1}

    changed = deepcopy(data)
    changed["metrics"]["cost"]["value"] = "3501.00"
    refusal = expect(
        live.request(
            live.path(ROUTE, row["object_id"]),
            actor="admin",
            method="PUT",
            body={
                "operation_id": str(uuid4()),
                "expected_revision": locked["revision_id"],
                "data": changed,
            },
        ),
        409,
    )
    assert refusal["reason_code"] == "PROBLEM_BASELINE_LOCKED"
    assert get(live, locked) == current
    assert baseline_counts(live, row["object_id"]) == {"revisions": 2, "locks": 1}


def test_problem_baseline_is_hidden_from_another_tenant_and_unqualified_actor(live):
    completed, diagnosis_row = completed_diagnosis(live)
    row = create(live, baseline_data(completed, diagnosis_row))
    expect(live.request(live.path(ROUTE, row["object_id"]), actor="author"), 404)
    expect(
        live.request(
            live.path(ROUTE, row["object_id"], tenant=live.fixture["tenant_b"]),
            actor="other_tenant",
        ),
        404,
    )
