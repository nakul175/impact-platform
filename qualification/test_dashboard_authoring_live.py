"""Positive user journey for FR-ANA-001 / APL-610 dashboard authoring."""

from uuid import uuid4
from test_calculation_methods import build, calculate_result, observation_data
from test_forms import temporary_grants
from test_live_application import expect
from test_measurement import approve, create, submit


def test_analyst_previews_ten_widgets_and_copies_private_dashboard(live):
    _, indicator, period, keys = build(live, scheme=None)
    row = create(live, "observations", observation_data(indicator, keys[0], "7", {}))
    approve(live, submit(live, "observations", row))
    result = calculate_result(live, indicator, period)
    revoke = temporary_grants(
        live,
        "author",
        ["dashboards.draft.create", "dashboards.read", "calculated-results.read", "evaluations.draft.edit"],
    )
    widgets = [
        {
            "widget_id": str(uuid4()),
            "type": "METRIC",
            "title": f"Delivery metric {position + 1}",
            "binding": {
                "resource_type": "CALCULATED_RESULT",
                "object_id": result["object_id"],
                "revision_id": result["revision_id"],
            },
            "view_mode": "PROVISIONAL",
            "period_id": period["object_id"],
            "dimensions": [],
            "disclosure_context": {"classification": "INTERNAL", "quality_context_required": True},
            "position": position,
            "width": 12,
            "compatible_filters": [],
            "drilldown_levels": [],
            "approved_slices": [],
        }
        for position in range(10)
    ]
    dashboard = create(
        live,
        "dashboards",
        {
            "title": "Ten metric delivery view",
            "mode": "PRIVATE_DRAFT",
            "widgets": widgets,
            "filters": {"terms": []},
        },
    )
    mobile = expect(
        live.request(live.path("dashboards", dashboard["object_id"]) + "/preview?viewport=MOBILE"), 200
    )
    assert mobile["viewport"] == "MOBILE" and len(mobile["widgets"]) == 10
    assert all(item["availability"] == "AVAILABLE" for item in mobile["widgets"])
    assert all(item["chart_values"] == ["7"] for item in mobile["widgets"])
    assert all(item["table_rows"][0]["value"] == item["chart_values"][0] for item in mobile["widgets"])
    assert all(item["quality_context"] is not None for item in mobile["widgets"])
    copied = expect(
        live.request(
            live.path("dashboards", dashboard["object_id"]) + "/actions/copy",
            method="POST",
            body={"operation_id": str(uuid4()), "data": {"title": "Private working copy"}},
        ),
        201,
    )
    copy_preview = expect(
        live.request(live.path("dashboards", copied["object_id"]) + "/preview?viewport=TABLE"), 200
    )
    assert copy_preview["mode"] == "PRIVATE_DRAFT" and copy_preview["title"] == "Private working copy"
    revoke()
