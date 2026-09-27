"""Qualification of period preview, immutable lock and scoped restatement."""
# ruff: noqa: F811

from datetime import datetime, timedelta, timezone
import uuid

from test_live_application import cmd, expect
from test_measurement import setup, get, action, submit, approve, observation, result  # noqa: F401


def complete_period(live, setup):
    programme, indicator, plan, period = setup()
    rows = []
    for obligation in plan["data"]["obligations"]:
        row = observation(live, indicator, obligation["source_key"])
        approve(live, submit(live, "observations", row))
        rows.append(get(live, "observations", row["object_id"]))
    provisional = result(live, indicator, period)
    return programme, indicator, plan, period, rows, provisional


def request_close(live, programme, period):
    template = get(live, "workflow-templates")["items"][0]
    receipt = action(
        live,
        "periods",
        period,
        "close",
        {
            "workflow_version": template["revision_id"],
            "programme_id": programme["object_id"],
            "reason": "Quarterly source and quality review complete.",
        },
    )
    return get(live, "workflows", receipt["object_id"])


def test_close_creates_immutable_snapshot_and_official_results(live, setup):
    programme, indicator, _, period, rows, provisional = complete_period(live, setup)
    workflow = request_close(live, programme, period)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    assert candidate["kind"] == "PeriodClose"
    assert candidate["record"]["data"]["blockers"] == []
    assert candidate["record"]["data"]["entries"][0]["coverage"]["complete"]
    action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Independent close review."},
        actor="reviewer",
    )
    assert get(live, "periods", period["object_id"])["lifecycle_state"] == "Open"
    snapshots = get(live, "snapshots")["items"]
    snapshot = next(
        s
        for s in snapshots
        if s["data"]["period_id"] == period["object_id"]
        and s["data"].get("programme_id") == programme["object_id"]
    )
    assert snapshot["lifecycle_state"] == "Locked" and len(snapshot["data"]["result_versions"]) == 1
    official = next(
        r
        for r in get(live, "calculated-results")["items"]
        if r["revision_id"] in snapshot["data"]["result_versions"]
    )
    assert official["data"]["mode"] == "OFFICIAL"
    assert official["data"]["input_snapshot_id"] == snapshot["object_id"]
    assert provisional["data"]["mode"] == "PROVISIONAL"
    assert get(live, "calculated-results", provisional["object_id"])["data"]["mode"] == "PROVISIONAL"
    action(
        live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]}, status=409
    )
    late = observation(live, indicator, "late-" + str(uuid.uuid4()))
    denied = action(
        live,
        "observations",
        late,
        "submit",
        {"workflow_version": get(live, "workflow-templates")["items"][0]["revision_id"]},
        status=409,
    )
    assert denied["reason_code"] == "PERIOD_RESTATEMENT_REQUIRED"
    assert get(live, "snapshots", snapshot["object_id"]) == snapshot
    with live.db() as c:
        binding = c.execute(
            "SELECT * FROM impact.period_snapshot_binding WHERE programme_id=%s AND period_id=%s",
            (programme["object_id"], period["object_id"]),
        ).fetchone()
        assert binding["snapshot_version"] == 1 and binding["supersedes_snapshot_id"] is None
        for row in rows:
            assert c.execute(
                "SELECT 1 FROM impact.lineage_edge WHERE result_revision=%s AND contribution_identity=%s AND disposition='INCLUDED'",
                (official["revision_id"], row["object_id"]),
            ).fetchone()


def test_blocked_close_is_reviewable_but_cannot_lock(live, setup):
    programme, indicator, plan, period = setup()
    row = observation(live, indicator, plan["data"]["obligations"][0]["source_key"])
    approve(live, submit(live, "observations", row))
    result(live, indicator, period)
    workflow = request_close(live, programme, period)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    codes = {b["code"] for b in candidate["record"]["data"]["blockers"]}
    assert {"MISSING_VALUES"} <= codes
    denied = action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Cannot close."},
        actor="reviewer",
        status=422,
    )
    assert denied["reason_code"] == "PERIOD_CLOSE_BLOCKED"
    assert get(live, "periods", period["object_id"])["lifecycle_state"] == "Open"
    assert get(live, "workflows", workflow["object_id"])["lifecycle_state"] == "InReview"


def test_source_change_after_preview_requires_new_preview(live, setup):
    programme, indicator, _, period, _, _ = complete_period(live, setup)
    workflow = request_close(live, programme, period)
    late = observation(live, indicator, "late-" + str(uuid.uuid4()))
    approve(live, submit(live, "observations", late))
    denied = action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Independent review."},
        actor="reviewer",
        status=409,
    )
    assert denied["reason_code"] == "PERIOD_CLOSE_PREVIEW_STALE"
    assert get(live, "periods", period["object_id"])["lifecycle_state"] == "Open"


def test_restatement_limits_correction_and_supersedes_without_overwrite(live, setup):
    programme, indicator, _, period, rows, _ = complete_period(live, setup)
    first_close = request_close(live, programme, period)
    approve(live, first_close)
    locked = get(live, "periods", period["object_id"])
    first_snapshot = next(
        s
        for s in get(live, "snapshots")["items"]
        if s["data"].get("programme_id") == programme["object_id"]
        and s["data"]["period_id"] == period["object_id"]
    )
    denied = expect(
        live.request(
            live.path("measurement-changes"),
            method="POST",
            body=cmd(
                {
                    "target_kind": "Observation",
                    "target_id": rows[0]["object_id"],
                    "target_revision": rows[0]["revision_id"],
                    "reason": "Locked correction",
                    "proposed_data": {"value": "20"},
                }
            ),
        ),
        409,
    )
    assert denied["reason_code"] == "PERIOD_RESTATEMENT_REQUIRED"
    template = get(live, "workflow-templates")["items"][0]
    restate_receipt = action(
        live,
        "periods",
        locked,
        "restate",
        {
            "workflow_version": template["revision_id"],
            "programme_id": programme["object_id"],
            "reason": "Correct a verified transcription error.",
            "source_ids": [rows[0]["object_id"]],
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        },
    )
    restate_workflow = get(live, "workflows", restate_receipt["object_id"])
    approve(live, restate_workflow)
    assert get(live, "periods", period["object_id"])["lifecycle_state"] == "Open"
    proposal = expect(
        live.request(
            live.path("measurement-changes"),
            method="POST",
            body=cmd(
                {
                    "target_kind": "Observation",
                    "target_id": rows[0]["object_id"],
                    "target_revision": rows[0]["revision_id"],
                    "reason": "Verified transcription correction.",
                    "proposed_data": {"value": "20", "source_version": "2"},
                }
            ),
        ),
        201,
    )
    proposal = get(live, "measurement-changes", proposal["object_id"])
    approve(live, submit(live, "measurement-changes", proposal))
    result(live, indicator, period)
    second_close = request_close(live, programme, get(live, "periods", period["object_id"]))
    approve(live, second_close)
    snapshots = [
        s
        for s in get(live, "snapshots")["items"]
        if s["data"]["period_id"] == period["object_id"]
        and s["data"].get("programme_id") == programme["object_id"]
    ]
    assert len(snapshots) == 2
    assert get(live, "snapshots", first_snapshot["object_id"]) == first_snapshot
    with live.db() as c:
        versions = c.execute(
            "SELECT * FROM impact.period_snapshot_binding WHERE programme_id=%s AND period_id=%s ORDER BY snapshot_version",
            (programme["object_id"], period["object_id"]),
        ).fetchall()
        assert [v["snapshot_version"] for v in versions] == [1, 2]
        assert versions[1]["supersedes_snapshot_id"] == versions[0]["snapshot_id"]


def test_restatement_rejects_source_not_in_snapshot_and_rls_hides_bindings(live, setup):
    programme, _, _, period, _, _ = complete_period(live, setup)
    approve(live, request_close(live, programme, period))
    locked = get(live, "periods", period["object_id"])
    unrelated = live.records["observation_1"]["object_id"]
    template = get(live, "workflow-templates")["items"][0]
    denied = action(
        live,
        "periods",
        locked,
        "restate",
        {
            "workflow_version": template["revision_id"],
            "programme_id": programme["object_id"],
            "reason": "Attempt unrelated correction.",
            "source_ids": [unrelated],
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        },
        status=422,
    )
    assert denied["reason_code"] == "SOURCE_NOT_IN_LOCKED_SNAPSHOT"
    expect(live.request(live.path("snapshots"), actor="other_tenant"), 404)
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.period_snapshot_binding WHERE tenant_id=%s",
                (live.fixture["tenant_a"],),
            ).fetchone()["n"]
            == 0
        )
