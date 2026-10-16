"""Positive user journey for FR-ANA-006 / APL-616 disclosure-safe geographic analysis."""

import json
from uuid import uuid4

from impact_api.contracts import validate
from test_calculation_methods import build, observation_data
from test_forms import temporary_grants
from test_live_application import expect
from test_measurement import action, approve, create, get, submit


BOUNDARY_VERSION = "22222222-2222-4222-8222-222222222222"
DISTRICT = {
    "dimensions": [
        {
            "code": "district",
            "label": "District",
            "version": BOUNDARY_VERSION,
            "multiselect": False,
            "exhaustive": True,
            "categories": [
                {"code": "NORTH", "label": "North district"},
                {"code": "SOUTH", "label": "South district"},
            ],
        }
    ]
}


def test_analyst_previews_one_coordinate_free_map_and_equivalent_table(live):
    _, indicator, period, keys = build(live, scheme=DISTRICT)
    for key, value, district in zip(keys, ["8", "4", "3"], ["NORTH", "NORTH", "SOUTH"]):
        observation = create(
            live,
            "observations",
            observation_data(indicator, key, value, {"district": district}),
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
            "title": "District delivery map",
            "mode": "PRIVATE_DRAFT",
            "widgets": [
                {
                    "widget_id": widget_id,
                    "type": "MAP",
                    "title": "Delivery by district",
                    "binding": {
                        "resource_type": "CALCULATED_RESULT",
                        "object_id": result["object_id"],
                        "revision_id": result["revision_id"],
                    },
                    "view_mode": "PROVISIONAL",
                    "period_id": period["object_id"],
                    "dimensions": ["district"],
                    "disclosure_context": {
                        "classification": "INTERNAL",
                        "quality_context_required": True,
                    },
                    "position": 0,
                    "width": 12,
                    "compatible_filters": [],
                    "drilldown_levels": [],
                    "approved_slices": [],
                    "geographic_config": {
                        "dimension": "district",
                        "boundary_version": BOUNDARY_VERSION,
                        "layer": "AGGREGATE",
                        "granularity": "DISTRICT",
                        "legend": "Approved delivery observations",
                        "missingness": "SHOW_MISSING",
                        "external_map": True,
                    },
                }
            ],
            "filters": {"terms": []},
        },
    )

    preview = expect(
        live.request(
            live.path("dashboards", dashboard["object_id"]) + "/geographic-preview?widget_id=" + widget_id,
            actor="author",
        ),
        200,
    )
    validate("DashboardGeographicPreview", preview)
    assert preview["boundary_status"] == "MATCH"
    assert preview["data_boundary_versions"] == [BOUNDARY_VERSION]
    assert preview["coordinate_delivery"] == "NO_COORDINATES_IN_PLATFORM_PAYLOAD"
    assert preview["map_request"] == preview["equivalent_table"]
    assert {(row["geography_key"], row["value"]) for row in preview["map_request"]} == {
        ("NORTH", "12"),
        ("SOUTH", "3"),
    }
    serialized = json.dumps(preview).lower()
    for forbidden in ["latitude", "longitude", "geometry", "coordinate"]:
        if forbidden == "coordinate":
            assert '"coordinate_delivery"' in serialized
            remainder = serialized.replace('"coordinate_delivery"', "")
            assert '"coordinate' not in remainder
        else:
            assert f'"{forbidden}"' not in serialized
    revoke()
