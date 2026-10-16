"""Positive user journey for FR-ANA-002 / APL-434 permission-safe filtered drilldown."""

from uuid import uuid4

from impact_api.contracts import validate
from test_dashboards import calculate, measure, ratio_source
from test_forms import temporary_grants
from test_live_application import expect
from test_measurement import create


def test_approved_slice_applies_only_to_compatible_widget_and_drill_level(live):
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "1", "4")
    base = calculate(live, indicator, period)
    ratio_source(live, indicator, keys[1], "3", "4")
    approved_slice = calculate(live, indicator, period)

    revoke = temporary_grants(
        live,
        "author",
        ["dashboards.draft.create", "dashboards.read", "calculated-results.read"],
    )
    try:

        def widget(title, position, compatible, levels, slices):
            return {
                "widget_id": str(uuid4()),
                "type": "METRIC",
                "title": title,
                "binding": {
                    "resource_type": "CALCULATED_RESULT",
                    "object_id": base["object_id"],
                    "revision_id": base["revision_id"],
                },
                "view_mode": "PROVISIONAL",
                "period_id": period["object_id"],
                "dimensions": [],
                "disclosure_context": {
                    "classification": "INTERNAL",
                    "quality_context_required": True,
                },
                "position": position,
                "width": 6,
                "compatible_filters": compatible,
                "drilldown_levels": levels,
                "approved_slices": slices,
            }

        slice_binding = {
            "resource_type": "CALCULATED_RESULT",
            "object_id": approved_slice["object_id"],
            "revision_id": approved_slice["revision_id"],
        }
        dashboard = create(
            live,
            "dashboards",
            {
                "title": "Permission-safe programme filter",
                "mode": "PRIVATE_DRAFT",
                "widgets": [
                    widget(
                        "Programme result",
                        0,
                        ["programme"],
                        ["PROGRAMME"],
                        [
                            {
                                "field": "programme",
                                "value": programme["object_id"],
                                "binding": slice_binding,
                            }
                        ],
                    ),
                    widget("Context only", 1, [], [], []),
                ],
                "filters": {
                    "terms": [
                        {
                            "field": "programme",
                            "operator": "IN",
                            "values": [programme["object_id"]],
                        }
                    ]
                },
            },
        )

        preview = expect(
            live.request(live.path("dashboards", dashboard["object_id"]) + "/preview?viewport=DESKTOP"),
            200,
        )
        validate("DashboardPreview", preview)
        assert preview["current_filters"]["terms"][0]["values"] == [programme["object_id"]]
        applied, ignored = preview["widgets"]
        assert applied["filter_effect"] == "APPLIED"
        assert applied["table_rows"][0]["value"] == approved_slice["data"]["value"]
        assert ignored["filter_effect"] == "NOT_APPLICABLE"
        assert ignored["non_applicable_filters"] == ["programme"]
        assert ignored["table_rows"][0]["value"] == base["data"]["value"]

        drilled = expect(
            live.request(
                live.path("dashboards", dashboard["object_id"])
                + "/preview?viewport=TABLE&drill_level=PROGRAMME"
            ),
            200,
        )
        assert drilled["drill_level"] == "PROGRAMME"
        assert drilled["widgets"][0]["availability"] == "AVAILABLE"
        assert drilled["widgets"][1]["availability"] == "UNAVAILABLE"
        denied = expect(
            live.request(
                live.path("dashboards", dashboard["object_id"])
                + "/preview?viewport=TABLE&drill_level=PARTICIPANT"
            ),
            422,
        )
        assert denied["reason_code"] == "DRILL_LEVEL_NOT_PERMITTED"
    finally:
        revoke()
