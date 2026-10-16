"""Positive user journey for FR-ANA-009 / APL-618 dashboard alerts."""

from uuid import uuid4

from impact_api.contracts import validate
from test_dashboards import measure
from test_forms import temporary_grants
from test_live_application import expect


def test_author_creates_due_rule_and_receives_a_durable_missingness_incident(live):
    _, indicator, period, _ = measure(live, keys=1)
    revoke = temporary_grants(
        live, "author", ["dashboards.draft.create", "dashboards.draft.edit", "dashboards.read"]
    )
    path = live.path("dashboard-alert-rules")
    body = {
        "operation_id": str(uuid4()),
        "data": {
            "measure_id": indicator["object_id"],
            "operator": "LT",
            "threshold": "50",
            "minimum_coverage": 100,
            "max_freshness_seconds": 86400,
            "evaluation_cadence": "DAILY",
            "recipient_ids": [live.fixture["actors"]["author"]["principal_id"]],
            "cooldown_seconds": 3600,
        },
    }

    created = expect(live.request(path, actor="author", method="POST", body=body), 201)
    current = expect(live.request(path + "/" + created["object_id"], actor="author"), 200)
    validate("DashboardAlertRule", current)
    assert current["data"]["measure_id"] == indicator["object_id"]

    evaluation = expect(
        live.request(
            path + "/" + created["object_id"] + "/actions/evaluate",
            actor="author",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {"period_id": period["object_id"], "result_id": None},
            },
        ),
        200,
    )
    validate("DashboardAlertOutcome", evaluation)
    assert evaluation["outcome"] == "MISSINGNESS"
    assert evaluation["reason_code"] == "RESULT_ABSENT"
    assert evaluation["occurrence_count"] == 1
    assert evaluation["coalesced"] is False

    incidents = expect(live.request(path + "/" + created["object_id"] + "/incidents", actor="author"), 200)
    validate("DashboardAlertIncidentList", incidents)
    assert len(incidents["items"]) == 1
    incident = incidents["items"][0]
    assert incident["object_id"] == evaluation["incident_id"]
    assert incident["data"]["rule_id"] == created["object_id"]
    assert incident["data"]["evaluation_period_id"] == period["object_id"]
    assert incident["data"]["recipient_ids"] == body["data"]["recipient_ids"]
    revoke()
