"""Positive user journey for FR-DQ-007 / APL-623 anomaly assistance."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from impact_api.contracts import validate
from test_calculation_methods import observation_data
from test_dashboards import measure
from test_forms import temporary_grants
from test_live_application import expect
from test_measurement import approve, create, get, submit


def test_analyst_runs_anomaly_assistance_and_confirms_a_reviewable_finding(live):
    _, indicator, _, keys = measure(live, keys=6)
    revoke = temporary_grants(
        live, "author", ["dashboards.draft.create", "dashboards.draft.edit", "dashboards.read"]
    )
    start = datetime(2026, 8, 1, tzinfo=timezone.utc)
    revisions = []
    for index, (key, value) in enumerate(zip(keys, ["9", "10", "10", "11", "9", "100"])):
        event = start + timedelta(days=index)
        row = create(
            live,
            "observations",
            observation_data(
                indicator,
                key,
                str(int(value) / 100),
                {},
                numerator=value,
                denominator="100",
                event_at=event.isoformat().replace("+00:00", "Z"),
                captured_at=(event + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
            ),
        )
        approve(live, submit(live, "observations", row))
        revisions.append(get(live, "observations", row["object_id"]))

    path = live.path("anomaly-runs")
    body = {
        "operation_id": str(uuid4()),
        "data": {
            "method_version": "ROBUST_MAD_1",
            "eligible_observations": [
                {"object_id": row["object_id"], "revision_id": row["revision_id"]} for row in revisions
            ],
            "comparison_window": {
                "starts_at": "2026-08-01T00:00:00Z",
                "ends_at": "2026-09-01T00:00:00Z",
            },
            "owner_id": live.fixture["actors"]["author"]["principal_id"],
        },
    }
    run = expect(live.request(path, actor="author", method="POST", body=body), 201)
    validate("AnomalyRunOutcome", run)
    assert run["eligible_revision_count"] == 6
    assert run["source_mutation"] is False and run["person_fraud_label"] is False
    assert len(run["findings"]) == 1
    finding = run["findings"][0]
    assert finding["observation_revision"] == revisions[-1]["revision_id"]

    current = expect(live.request(live.path("anomaly-findings", finding["finding_id"]), actor="author"), 200)
    validate("AnomalyResource", current)
    assert current["data"]["state"] == "SUGGESTED"

    hidden = expect(
        live.request(
            live.path(
                "anomaly-findings",
                finding["finding_id"],
                tenant=live.fixture["tenant_b"],
            ),
            actor="other_tenant",
        ),
        404,
    )
    assert hidden["code"] == "RESOURCE_UNAVAILABLE"
    denied = expect(
        live.request(
            live.path("anomaly-findings", finding["finding_id"]) + "/actions/review",
            actor="enumerator",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {"decision": "CONFIRMED", "reason_code": None},
            },
        ),
        404,
    )
    assert denied["code"] == "RESOURCE_UNAVAILABLE"

    reviewed = expect(
        live.request(
            live.path("anomaly-findings", finding["finding_id"]) + "/actions/review",
            actor="author",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {"decision": "CONFIRMED", "reason_code": None},
            },
        ),
        200,
    )
    validate("AnomalyReviewOutcome", reviewed)
    assert reviewed["confirmed_quality_defect"] is True
    assert reviewed["source_mutation"] is False
    source = get(live, "observations", revisions[-1]["object_id"])
    assert source["revision_id"] == revisions[-1]["revision_id"]
    assert source["data"]["value"] == "1.0"
    revoke()
