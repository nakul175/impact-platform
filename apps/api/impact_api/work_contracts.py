"""Contracts for reviewed exclusions, personal work and recalculation recovery."""

from copy import deepcopy

from .measurement_contracts import DATE, UUID, closed, text_field


def _extend_obligation(item):
    item["properties"].update(
        {
            "eligibility": {"enum": ["REQUIRED", "EXCEPTED"]},
            "exclusion_reason": text_field(2000),
            "exclusion_effective_at": DATE,
        }
    )
    item.setdefault("allOf", []).append(
        {
            "if": {
                "properties": {"eligibility": {"const": "EXCEPTED"}},
                "required": ["eligibility"],
            },
            "then": {"required": ["exclusion_reason", "exclusion_effective_at"]},
            "else": {
                "not": {
                    "anyOf": [
                        {"required": ["exclusion_reason"]},
                        {"required": ["exclusion_effective_at"]},
                    ]
                }
            },
        }
    )


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"

    for name in ["CollectionPlanData", "CollectionPlanDraftData"]:
        _extend_obligation(schemas[name]["properties"]["obligations"]["items"])
    for variant in schemas["MeasurementChangeData"]["oneOf"]:
        if variant["properties"]["target_kind"].get("const") == "CollectionPlan":
            _extend_obligation(variant["properties"]["proposed_data"]["properties"]["obligations"]["items"])
    schemas["MeasurementChangeDraftData"] = deepcopy(schemas["MeasurementChangeData"])

    coverage = schemas["Coverage"]["properties"]
    coverage.update(
        required_count={"type": "integer", "minimum": 0},
        excepted_count={"type": "integer", "minimum": 0},
    )
    obligation = coverage["obligations"]["items"]
    obligation["properties"].update(
        eligibility={"enum": ["REQUIRED", "EXCEPTED"]},
        exclusion_reason=text_field(2000),
        exclusion_effective_at=DATE,
    )
    obligation["properties"]["status"]["enum"].append("EXCEPTED")

    def action(route, action_name, capability, roles):
        schema_name = "Action" + "".join(part.title() for part in route.split("-")) + action_name.title()
        schemas[schema_name + "Data"] = closed({})
        schemas[schema_name] = closed(
            {
                "operation_id": UUID,
                "expected_revision": UUID,
                "data": {"$ref": "#/components/schemas/" + schema_name + "Data"},
            },
            ["operation_id", "expected_revision", "data"],
        )
        template = deepcopy(paths[prefix + "indicator-instances/{object_id}/actions/calculate"])
        op = "action_" + route.replace("-", "_") + "_" + action_name
        template["post"].update(
            operationId=op,
            summary=op.replace("_", " "),
            **{"x-capability": capability, "x-contract-version": "1.8.0"},
        )
        template["post"]["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + schema_name
        }
        template["post"]["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/Receipt"
        }
        paths[prefix + route + "/{object_id}/actions/" + action_name] = template
        policy["operations"] = [item for item in policy["operations"] if item["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": "POST",
                "path": prefix + route + "/{object_id}/actions/" + action_name,
                "capability": capability,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": True,
            }
        )

    action(
        "notifications",
        "acknowledge",
        "notifications.acknowledge",
        ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER", "ANALYST", "EXTERNAL"],
    )
    action(
        "work-items",
        "recalculate",
        "indicator.calculate",
        ["MEL_ADMIN", "PROGRAMME_MANAGER"],
    )
    spec["info"]["version"] = policy["version"] = "1.8.0"
