"""Story-bound error and recovery checks for analytics, evaluation and finance.

The read cases prove malformed selectors fail closed and do not prevent a later,
well-formed lookup.  The command cases prove closed request schemas reject an
unknown field before consuming the operation id or writing any durable domain,
audit, outbox or receipt row.  Reusing that operation id with the corrected
request must reach normal resource validation rather than an uncertain-retry
conflict.  Each story's positive live journey is run beside this file.
"""

from uuid import uuid4

import pytest


MISSING_ID = "10000000-0000-4000-8000-000000000001"


def _path(live, suffix):
    route, separator, remainder = suffix.partition("/")
    return live.path(route) + (separator + remainder if separator else "")


def _durable_counts(live, operation_id=None):
    tenant = live.fixture["tenant_a"]
    with live.db() as connection:
        connection.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        counts = {
            "registry": connection.execute(
                "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s", (tenant,)
            ).fetchone()["n"],
            "audit": connection.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s", (tenant,)
            ).fetchone()["n"],
            "outbox": connection.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s", (tenant,)
            ).fetchone()["n"],
        }
        if operation_id is not None:
            counts["receipt"] = connection.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=%s",
                (tenant, operation_id),
            ).fetchone()["n"]
        return counts


@pytest.mark.parametrize(
    ("story_id", "malformed_suffix", "recovery_suffix"),
    [
        pytest.param("APL-610", "dashboards/not-a-uuid", f"dashboards/{MISSING_ID}", id="APL-610"),
        pytest.param(
            "APL-434",
            "dashboards/not-a-uuid/preview?viewport=TABLE&drill_level=PROGRAMME",
            f"dashboards/{MISSING_ID}/preview?viewport=TABLE&drill_level=PROGRAMME",
            id="APL-434",
        ),
        pytest.param(
            "APL-616",
            f"dashboards/not-a-uuid/geographic-preview?widget_id={MISSING_ID}",
            f"dashboards/{MISSING_ID}/geographic-preview?widget_id={MISSING_ID}",
            id="APL-616",
        ),
        pytest.param(
            "APL-618",
            "dashboard-alert-rules/not-a-uuid/incidents",
            f"dashboard-alert-rules/{MISSING_ID}/incidents",
            id="APL-618",
        ),
        pytest.param(
            "APL-620",
            "external-analytics-connections/not-a-uuid/extracts",
            f"external-analytics-connections/{MISSING_ID}/extracts",
            id="APL-620",
        ),
        pytest.param("APL-625", "evaluations/not-a-uuid", f"evaluations/{MISSING_ID}", id="APL-625"),
        pytest.param(
            "APL-630",
            "evaluation-methodologies/not-a-uuid/history",
            f"evaluation-methodologies/{MISSING_ID}/history",
            id="APL-630",
        ),
        pytest.param(
            "APL-632",
            "analysis-packages/not-a-uuid/export",
            f"analysis-packages/{MISSING_ID}/export",
            id="APL-632",
        ),
        pytest.param(
            "APL-634",
            "learning-questions/not-a-uuid/summary",
            f"learning-questions/{MISSING_ID}/summary",
            id="APL-634",
        ),
        pytest.param(
            "APL-639",
            "management-actions/not-a-uuid/history",
            f"management-actions/{MISSING_ID}/history",
            id="APL-639",
        ),
    ],
)
def test_malformed_story_selector_fails_closed_then_well_formed_lookup_recovers(
    live, story_id, malformed_suffix, recovery_suffix
):
    before = _durable_counts(live)
    malformed = live.request(_path(live, malformed_suffix))
    assert malformed.status_code in {404, 422}, (story_id, malformed.status_code, malformed.text)
    assert _durable_counts(live) == before, story_id

    recovered = live.request(_path(live, recovery_suffix))
    assert recovered.status_code == 404, (story_id, recovered.status_code, recovered.text)
    assert recovered.json()["code"] == "RESOURCE_UNAVAILABLE", story_id
    assert _durable_counts(live) == before, story_id


COMMAND_CASES = [
    pytest.param(
        "APL-613",
        f"dashboards/{MISSING_ID}/actions/run-pivot",
        {"widget_id": MISSING_ID, "row_dimension": "region", "statistic": "SUM"},
        id="APL-613",
    ),
    pytest.param(
        "APL-646",
        "findings",
        {
            "statement": "Synthetic recovery probe.",
            "method": "Triangulation.",
            "observation": "Synthetic observation.",
            "interpretation": "Synthetic interpretation.",
            "supporting_evidence": [
                {"object_type": "Evidence", "object_id": MISSING_ID, "revision_id": MISSING_ID}
            ],
            "contradictory_evidence": [],
            "confidence_rationale": "No confidence claimed.",
            "limitations": ["Synthetic recovery probe."],
            "reviewer_id": MISSING_ID,
            "ai_confidence": None,
        },
        id="APL-646",
    ),
    pytest.param(
        "APL-648",
        "budgets",
        {
            "title": "Synthetic recovery probe",
            "approval_route": [MISSING_ID],
            "rate_assumptions": [{"pair": "USD/USD", "rate": "1.0000"}],
            "lines": [
                {
                    "activity_id": MISSING_ID,
                    "category_id": MISSING_ID,
                    "partner_id": MISSING_ID,
                    "period_id": MISSING_ID,
                    "currency": "USD",
                    "amount": "1.00",
                }
            ],
        },
        id="APL-648",
    ),
    pytest.param(
        "APL-650",
        "expenditure-imports",
        {
            "source_system": "SYNTHETIC_LEDGER",
            "file_sha256": "a" * 64,
            "control_total": "1.00",
            "permitted_exception": None,
            "transactions": [
                {
                    "source_transaction_key": "RECOVERY-PROBE",
                    "posting_date": "2026-08-18",
                    "event_date": "2026-08-15",
                    "amount": "1.00",
                    "currency": "USD",
                    "category_id": MISSING_ID,
                    "funding_allocation_id": MISSING_ID,
                    "adjustment_semantic": "ORIGINAL",
                }
            ],
        },
        id="APL-650",
    ),
    pytest.param(
        "APL-652",
        "finance-variance-views",
        {
            "budget_id": MISSING_ID,
            "budget_revision": MISSING_ID,
            "actual_cutoff": "2026-08-31",
            "actual_data_state": "MISSING",
            "actual_transactions": [],
            "commitments": "0.00",
            "forecast_total": "1.00",
            "forecast_method": "Synthetic recovery probe",
            "forecast_method_version": "2026.1",
            "forecast_assumptions": [],
            "author_id": MISSING_ID,
        },
        id="APL-652",
    ),
]


@pytest.mark.parametrize(("story_id", "suffix", "valid_data"), COMMAND_CASES)
def test_invalid_story_command_has_no_partial_write_and_operation_id_remains_recoverable(
    live, story_id, suffix, valid_data
):
    operation_id = str(uuid4())
    before = _durable_counts(live, operation_id)
    invalid = live.request(
        _path(live, suffix),
        method="POST",
        body={"operation_id": operation_id, "data": {**valid_data, "unexpected_field": True}},
    )
    assert invalid.status_code == 422, (story_id, invalid.status_code, invalid.text)
    assert _durable_counts(live, operation_id) == before, story_id

    corrected = live.request(
        _path(live, suffix),
        method="POST",
        body={"operation_id": operation_id, "data": valid_data},
    )
    assert corrected.status_code in {403, 404, 409}, (story_id, corrected.status_code, corrected.text)
    assert corrected.json()["code"] in {
        "POLICY_DENIED",
        "RESOURCE_UNAVAILABLE",
        "INDEPENDENCE_REQUIRED",
    }, story_id
    assert _durable_counts(live, operation_id) == before, story_id
