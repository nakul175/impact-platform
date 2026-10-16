"""Positive user journey for FR-CAL-013 / APL-607 weighted composites."""

from test_calculation_methods import build
from test_live_application import expect


def test_manager_previews_transparent_weighted_composite(live):
    target, first, second = [build(live, scheme=None)[0] for _ in range(3)]
    with live.db() as database:
        approved = {
            item["object_id"]: str(
                database.execute(
                    "SELECT d.candidate_revision FROM impact.decision_current d JOIN impact.object_revision r ON r.tenant_id=d.tenant_id AND r.revision_id=d.candidate_revision WHERE r.object_id=%s AND d.action='APPROVE'",
                    (item["object_id"],),
                ).fetchone()["candidate_revision"]
            )
            for item in (first, second)
        }
    components = [
        {
            "code": "reach",
            "definition_revision": approved[first["object_id"]],
            "weight": "0.4",
            "input_min": "0",
            "input_max": "100",
            "required": True,
        },
        {
            "code": "quality",
            "definition_revision": approved[second["object_id"]],
            "weight": "0.6",
            "input_min": "0",
            "input_max": "100",
            "required": True,
        },
    ]
    data = {
        "title": "Transparent programme composite",
        "target_definition_id": target["object_id"],
        "output_unit": "score",
        "ast": {
            "kind": "COMPOSITE",
            "components": components,
            "missing_policy": "BLOCK",
            "interpretation": "Normalised weighted mean of approved reach and quality definitions.",
        },
    }
    samples = [
        {
            "definition_revision": component["definition_revision"],
            "values": [{"value": value, "eligible": True, "distinct_key": None, "dimensions": {}}],
        }
        for component, value in zip(components, ["60", "80"])
    ]
    preview = expect(
        live.request(
            live.path("formula-definitions") + "/preview",
            method="POST",
            body={"data": data, "samples": samples},
        ),
        200,
    )
    assert preview["value_state"] == "PRESENT" and preview["value"] == "72"
    assert [
        (x["code"], x["normalized_value"], x["effective_weight"], x["contribution"])
        for x in preview["component_contributions"]
    ] == [("reach", "60", "0.4", "24"), ("quality", "80", "0.6", "48")]
    assert {x["code"] for x in preview["sensitivity"]} == {"reach", "quality"}
    assert set(preview["referenced_definition_revisions"]) == set(approved.values())

    denied = expect(
        live.request(
            live.path("formula-definitions") + "/preview",
            actor="enumerator",
            method="POST",
            body={"data": data, "samples": samples},
        ),
        404,
    )
    assert denied["code"] == "RESOURCE_UNAVAILABLE"
