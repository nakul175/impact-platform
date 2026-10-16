"""Story-bound authorization refusals for the completed analytics and evaluation slice.

Each case exercises the operation that distinguishes the named story.  The fixture
``revoked`` principal has an AUTHOR role label but no current membership authority;
``enumerator`` has a current membership but none of the required area capabilities.
This keeps role labels, current authority and resource selectors separate.
"""

from uuid import uuid4

import pytest

OBJECT_ID = "10000000-0000-4000-8000-000000000001"


def _path(live, suffix):
    route, separator, remainder = suffix.partition("/")
    return live.path(route) + (separator + remainder if separator else "")


@pytest.mark.parametrize(
    ("story_id", "suffix"),
    [
        pytest.param("APL-610", f"dashboards/{OBJECT_ID}", id="APL-610-dashboard-authoring"),
        pytest.param(
            "APL-434",
            f"dashboards/{OBJECT_ID}/preview?viewport=TABLE&drill_level=PROGRAMME",
            id="APL-434-filtered-drilldown",
        ),
        pytest.param(
            "APL-616",
            f"dashboards/{OBJECT_ID}/geographic-preview?widget_id={OBJECT_ID}",
            id="APL-616-geographic-analysis",
        ),
        pytest.param(
            "APL-618",
            f"dashboard-alert-rules/{OBJECT_ID}/incidents",
            id="APL-618-dashboard-alerts",
        ),
        pytest.param(
            "APL-620",
            f"external-analytics-connections/{OBJECT_ID}/extracts",
            id="APL-620-external-analytics",
        ),
        pytest.param("APL-625", f"evaluations/{OBJECT_ID}", id="APL-625-evaluation-registry"),
        pytest.param(
            "APL-630",
            f"evaluation-methodologies/{OBJECT_ID}/history",
            id="APL-630-evaluation-methodology",
        ),
        pytest.param(
            "APL-632",
            f"analysis-packages/{OBJECT_ID}/export",
            id="APL-632-analysis-packages",
        ),
        pytest.param(
            "APL-634",
            f"learning-questions/{OBJECT_ID}/summary",
            id="APL-634-learning-agenda",
        ),
        pytest.param(
            "APL-639",
            f"management-actions/{OBJECT_ID}/history",
            id="APL-639-management-responses",
        ),
    ],
)
def test_revoked_membership_cannot_read_story_resource(live, story_id, suffix):
    """A stale role label never restores current read or export authority."""

    response = live.request(_path(live, suffix), actor="revoked")
    assert response.status_code in {401, 404}, (story_id, response.status_code, response.text)


@pytest.mark.parametrize(
    ("story_id", "suffix", "data"),
    [
        pytest.param(
            "APL-613",
            f"dashboards/{OBJECT_ID}/actions/run-pivot",
            {"widget_id": OBJECT_ID, "row_dimension": "region", "statistic": "SUM"},
            id="APL-613-dashboard-pivots",
        ),
        pytest.param(
            "APL-646",
            "findings",
            {
                "statement": "Synthetic finding.",
                "method": "Triangulation.",
                "observation": "Synthetic observation.",
                "interpretation": "Synthetic interpretation.",
                "supporting_evidence": [
                    {
                        "object_type": "Evidence",
                        "object_id": OBJECT_ID,
                        "revision_id": OBJECT_ID,
                    }
                ],
                "contradictory_evidence": [],
                "confidence_rationale": "No confidence claimed.",
                "limitations": ["Synthetic authorization probe."],
                "reviewer_id": OBJECT_ID,
                "ai_confidence": None,
            },
            id="APL-646-triangulated-findings",
        ),
        pytest.param(
            "APL-648",
            "budgets",
            {
                "title": "Synthetic authorization probe",
                "approval_route": [OBJECT_ID],
                "rate_assumptions": [{"pair": "USD/USD", "rate": "1.0000"}],
                "lines": [
                    {
                        "activity_id": OBJECT_ID,
                        "category_id": OBJECT_ID,
                        "partner_id": OBJECT_ID,
                        "period_id": OBJECT_ID,
                        "currency": "USD",
                        "amount": "1.00",
                    }
                ],
            },
            id="APL-648-budget-versions",
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
                        "source_transaction_key": "AUTH-PROBE",
                        "posting_date": "2026-08-18",
                        "event_date": "2026-08-15",
                        "amount": "1.00",
                        "currency": "USD",
                        "category_id": OBJECT_ID,
                        "funding_allocation_id": OBJECT_ID,
                        "adjustment_semantic": "ORIGINAL",
                    }
                ],
            },
            id="APL-650-expenditure-ingestion",
        ),
        pytest.param(
            "APL-652",
            "finance-variance-views",
            {
                "budget_id": OBJECT_ID,
                "budget_revision": OBJECT_ID,
                "actual_cutoff": "2026-08-31",
                "actual_data_state": "MISSING",
                "actual_transactions": [],
                "commitments": "0.00",
                "forecast_total": "1.00",
                "forecast_method": "Synthetic authorization probe",
                "forecast_method_version": "2026.1",
                "forecast_assumptions": [],
                "author_id": OBJECT_ID,
            },
            id="APL-652-finance-variance",
        ),
    ],
)
def test_revoked_membership_cannot_execute_story_operation(live, story_id, suffix, data):
    """Current membership is checked before accepting a story command."""

    response = live.request(
        _path(live, suffix),
        actor="revoked",
        method="POST",
        body={"operation_id": str(uuid4()), "data": data},
    )
    assert response.status_code in {401, 404}, (story_id, response.status_code, response.text)


@pytest.mark.parametrize(
    ("story_id", "suffix"),
    [
        pytest.param("APL-610", "dashboards", id="APL-610-current-member-no-capability"),
        pytest.param("APL-625", "evaluations", id="APL-625-current-member-no-capability"),
        pytest.param(
            "APL-630",
            f"evaluation-methodologies/{OBJECT_ID}",
            id="APL-630-current-member-no-capability",
        ),
    ],
)
def test_current_enumerator_without_area_capability_is_refused(live, story_id, suffix):
    """A current tenant membership does not imply analytics or evaluation access."""

    response = live.request(_path(live, suffix), actor="enumerator")
    assert response.status_code in {403, 404}, (story_id, response.status_code, response.text)
    refused = response.json()
    assert refused["code"] in {"POLICY_DENIED", "RESOURCE_UNAVAILABLE"}, story_id
