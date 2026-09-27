"""Additive manual measurement configuration contracts."""

from copy import deepcopy
import json

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
ROLES = ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER"]
READS = {
    "collection-plans": "CollectionPlan",
    "reporting-calendars": "ReportingCalendar",
    "geographies": "Geography",
}
SPECIAL_READS = {
    "programmes/{object_id}/readiness": ("programme_readiness", "programmes.read", "ProgrammeReadiness"),
    "workflows/{object_id}/candidate": ("workflow_candidate", "workflows.read", "ReviewCandidate"),
    "measurement-members": ("measurement_members", "measurement-members.read", "MeasurementMembers"),
}


def closed(properties, required=()):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(required),
    }


def text_field(maximum=200):
    return {"type": "string", "minLength": 1, "maxLength": maximum, "pattern": r"\S"}


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"

    def register(path, method, entry, op, cap, roles=ROLES):
        entry.update(
            operationId=op,
            summary=op.replace("_", " "),
            **{"x-capability": cap, "x-contract-version": "1.4.0"},
        )
        paths.setdefault(path, {})[method] = entry
        policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": path,
                "capability": cap,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": method != "get",
            }
        )

    for name in ["IndicatorDefinitionData", "IndicatorDefinitionDraftData"]:
        schemas[name]["properties"].update(
            numerator_meaning=text_field(2000), denominator_meaning=text_field(2000)
        )
    schemas["CollectionPlanData"] = closed(
        {
            "title": text_field(),
            "indicator_id": UUID,
            "period_id": UUID,
            "obligations": {
                "type": "array",
                "minItems": 1,
                "maxItems": 500,
                "items": closed(
                    {
                        "label": text_field(),
                        "source_namespace": text_field(64),
                        "source_key": text_field(200),
                        "due_at": DATE,
                    },
                    ["label", "source_namespace", "source_key", "due_at"],
                ),
            },
        }
    )
    schemas["ReportingCalendarData"] = closed(
        {"title": text_field(), "zone": text_field(), "frequency": text_field()}
    )
    schemas["GeographyData"] = closed({"title": text_field(), "code": text_field(64)})
    for route, kind in READS.items():
        for suffix in ["", "List", "DraftData", "Create", "Patch"]:
            if suffix == "DraftData":
                schemas[kind + suffix] = deepcopy(schemas[kind + "Data"])
            else:
                schemas[kind + suffix] = json.loads(
                    json.dumps(schemas["Programme" + suffix]).replace("Programme", kind)
                )
        for item in [False, True]:
            suffix = "/{object_id}" if item else ""
            path = prefix + route + suffix
            template = paths[prefix + "programmes" + suffix]
            paths[path] = {"parameters": deepcopy(template["parameters"])}
            for method in ["get", "patch" if item else "post"] if route == "collection-plans" else ["get"]:
                entry = json.loads(json.dumps(template[method]).replace("Programme", kind))
                verb = ("get" if item else "list") if method == "get" else ("patch" if item else "create")
                cap = route + (".read" if method == "get" else ".draft.edit" if item else ".draft.create")
                register(
                    path,
                    method,
                    entry,
                    verb + "_" + route.replace("-", "_"),
                    cap,
                    ROLES if method == "get" else ["AUTHOR", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                )
    # This pin is written by submission, never accepted from a draft command.
    schemas["CollectionPlanData"]["properties"]["indicator_revision"] = UUID
    for route, action, cap, props, required in [
        (
            "collection-plans",
            "submit",
            "collection-plan.submit",
            {"workflow_version": UUID},
            ["workflow_version"],
        ),
        ("indicator-instances", "activate", "indicator.activate", {}, []),
        ("programmes", "ready", "programme.activate", {}, []),
        ("programmes", "activate", "programme.activate", {}, []),
        ("programmes", "revise", "programme.activate", {"reason": text_field(2000)}, ["reason"]),
    ]:
        name = "Measurement" + "".join(x.title() for x in route.split("-")) + action.title()
        schemas[name + "Data"] = closed(props, required)
        schemas[name] = closed(
            {
                "operation_id": UUID,
                "expected_revision": UUID,
                "data": {"$ref": "#/components/schemas/" + name + "Data"},
            },
            ["operation_id", "expected_revision", "data"],
        )
        entry = deepcopy(paths[prefix + "indicator-definitions/{object_id}/actions/submit"])
        entry["post"]["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + name
        }
        path = prefix + route + "/{object_id}/actions/" + action
        paths[path] = {"parameters": entry["parameters"]}
        register(
            path,
            "post",
            entry["post"],
            "action_" + route.replace("-", "_") + "_" + action,
            cap,
            ["AUTHOR", "MEL_ADMIN", "PROGRAMME_MANAGER"]
            if action == "submit"
            else ["MEL_ADMIN", "PROGRAMME_MANAGER"],
        )
    schemas["ProgrammeReadiness"] = closed(
        {
            "ready": {"type": "boolean"},
            "revision_id": UUID,
            "checks": {
                "type": "array",
                "items": closed(
                    {"code": text_field(), "passed": {"type": "boolean"}, "message": text_field(2000)},
                    ["code", "passed", "message"],
                ),
            },
        },
        ["ready", "revision_id", "checks"],
    )
    schemas["ReviewCandidate"] = closed(
        {
            "kind": {"enum": ["Observation", "IndicatorDefinition", "CollectionPlan"]},
            "record": {
                "oneOf": [
                    {"$ref": "#/components/schemas/" + k}
                    for k in ["Observation", "IndicatorDefinition", "CollectionPlan"]
                ]
            },
        },
        ["kind", "record"],
    )
    schemas["MeasurementMembers"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 1000,
                "items": closed(
                    {
                        "principal_id": UUID,
                        "display_name": text_field(),
                        "collector": {"type": "boolean"},
                        "reviewer": {"type": "boolean"},
                    },
                    ["principal_id", "display_name", "collector", "reviewer"],
                ),
            }
        },
        ["items"],
    )
    for route, (op, cap, schema) in SPECIAL_READS.items():
        template = deepcopy(paths[prefix + "programmes" + ("/{object_id}" if "{object_id}" in route else "")])
        entry = template["get"]
        entry.pop("parameters", None)
        entry["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + schema
        }
        paths[prefix + route] = {"parameters": template["parameters"]}
        register(prefix + route, "get", entry, op, cap)
    schemas["Coverage"]["properties"].update(
        {
            k: {"type": "integer", "minimum": 0}
            for k in ["valid_count", "pending_count", "missing_count", "overdue_count", "unplanned_count"]
        }
    )
    schemas["Coverage"]["properties"].update(
        plan_revision=UUID,
        approval_percent={"type": "string"},
        obligations={
            "type": "array",
            "maxItems": 500,
            "items": closed(
                {
                    "label": text_field(),
                    "source_namespace": text_field(64),
                    "source_key": text_field(200),
                    "due_at": DATE,
                    "status": {"enum": ["APPROVED", "PENDING", "MISSING", "EXCLUDED"]},
                    "overdue": {"type": "boolean"},
                },
                ["label", "source_namespace", "source_key", "due_at", "status", "overdue"],
            ),
        },
    )
    schemas["LineageManifestData"]["properties"]["plan_revision"] = UUID
    spec["info"]["version"] = policy["version"] = "1.4.0"
