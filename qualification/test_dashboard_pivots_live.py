"""Positive user journey for FR-ANA-005 / APL-613 governed dashboard pivots."""

from uuid import uuid4

from impact_api.contracts import validate
from test_calculation_methods import build, observation_data
from test_forms import temporary_grants
from test_live_application import expect
from test_measurement import action, approve, create, get, submit


DIMENSION_VERSION = "11111111-1111-4111-8111-111111111111"
REGION = {
    "dimensions": [
        {
            "code": "region",
            "label": "Region",
            "version": DIMENSION_VERSION,
            "multiselect": False,
            "exhaustive": True,
            "categories": [
                {"code": "NORTH", "label": "North"},
                {"code": "SOUTH", "label": "South"},
            ],
        }
    ]
}


def test_analyst_previews_a_source_based_dashboard_pivot_through_the_http_api(live):
    _, indicator, period, keys = build(live, scheme=REGION)
    for key, value, region in zip(keys, ["7", "5", "3"], ["NORTH", "NORTH", "SOUTH"]):
        observation = create(
            live,
            "observations",
            observation_data(indicator, key, value, {"region": region}),
        )
        approve(live, submit(live, "observations", observation))
    calculated = action(
        live,
        "indicator-instances",
        indicator,
        "calculate",
        {"period_id": period["object_id"]},
    )
    result = get(live, "calculated-results", calculated["object_id"])

    revoke = temporary_grants(
        live,
        "author",
        ["dashboards.draft.create", "dashboards.read", "calculated-results.read"],
    )
    widget_id = str(uuid4())
    dashboard = create(
        live,
        "dashboards",
        {
            "title": "Regional delivery pivot",
            "mode": "PRIVATE_DRAFT",
            "widgets": [
                {
                    "widget_id": widget_id,
                    "type": "TABLE",
                    "title": "Delivery by region",
                    "binding": {
                        "resource_type": "CALCULATED_RESULT",
                        "object_id": result["object_id"],
                        "revision_id": result["revision_id"],
                    },
                    "view_mode": "PROVISIONAL",
                    "period_id": period["object_id"],
                    "dimensions": ["region"],
                    "disclosure_context": {
                        "classification": "INTERNAL",
                        "quality_context_required": True,
                    },
                    "position": 0,
                    "width": 12,
                    "compatible_filters": [],
                    "drilldown_levels": [],
                    "approved_slices": [],
                }
            ],
            "filters": {"terms": []},
        },
    )

    body = {"widget_id": widget_id, "row_dimension": "region", "statistic": "SUM"}
    pivot = expect(
        live.request(
            live.path("dashboards", dashboard["object_id"]) + "/pivot-preview",
            actor="author",
            method="POST",
            body=body,
        ),
        200,
    )
    validate("DashboardPivotResult", pivot)
    assert pivot["execution"] == "SYNC" and pivot["job_id"] is None
    assert pivot["result_revision"] == result["revision_id"]
    assert pivot["grand_total"] == "15"
    assert pivot["grand_total_basis"] == "ELIGIBLE_SOURCE_RESULT"
    assert {(cell["category"], cell["value"]) for cell in pivot["cells"]} == {
        ("NORTH", "12"),
        ("SOUTH", "3"),
    }
    assert "never from displayed cells" in pivot["explanation"]
    revoke()
