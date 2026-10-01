from copy import deepcopy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api"))
from impact_api.administration_contracts import augment  # noqa: E402
from impact_api.measurement_contracts import augment as augment_measurement  # noqa: E402
from impact_api.changes_contracts import augment as augment_changes  # noqa: E402
from impact_api.period_contracts import augment as augment_periods  # noqa: E402
from impact_api.reporting_contracts import augment as augment_reporting  # noqa: E402
from impact_api.work_contracts import augment as augment_work  # noqa: E402
from impact_api.publication_contracts import augment as augment_publication  # noqa: E402
from impact_api.planning_contracts import augment as augment_planning  # noqa: E402
from impact_api.calculation_contracts import augment as augment_calculation  # noqa: E402
from impact_api.forms_contracts import augment as augment_forms  # noqa: E402
from impact_api.import_contracts import augment as augment_imports  # noqa: E402
from impact_api.evidence_contracts import augment as augment_evidence  # noqa: E402
from impact_api.tenant_contracts import openapi as platform_openapi  # noqa: E402
from impact_api.version import DOMAIN_API  # noqa: E402

spec = json.loads((ROOT / "packages/contracts/openapi-baseline.json").read_text())
policy = json.loads((ROOT / "specification/contracts/access-policy.json").read_text())
schemas = spec["components"]["schemas"]
uuid = {"type": "string", "format": "uuid"}
spec["info"]["version"] = "1.2.0"
policy["version"] = "1.2.0"
for route, action, cap, data, roles in [
    (
        "observations",
        "submit",
        "observation.submit",
        deepcopy(schemas["ActionIndicatorDefinitionsSubmitData"]),
        ["AUTHOR", "PROGRAMME_MANAGER"],
    ),
    (
        "indicator-instances",
        "calculate",
        "indicator.calculate",
        {
            "type": "object",
            "additionalProperties": False,
            "properties": {"period_id": uuid},
            "required": ["period_id"],
        },
        ["MEL_ADMIN", "PROGRAMME_MANAGER"],
    ),
]:
    name = "Action" + "".join(p.title() for p in route.split("-")) + action.title()
    op = "action_" + route.replace("-", "_") + "_" + action
    schemas[name + "Data"] = data
    schemas[name] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "operation_id": uuid,
            "expected_revision": uuid,
            "data": {"$ref": "#/components/schemas/" + name + "Data"},
        },
        "required": ["operation_id", "expected_revision", "data"],
    }
    entry = deepcopy(
        spec["paths"]["/v1/tenants/{tenant_id}/indicator-definitions/{object_id}/actions/submit"]
    )
    entry["post"].update(operationId=op, summary=name, **{"x-capability": cap})
    entry["post"]["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/" + name
    }
    path = "/v1/tenants/{tenant_id}/" + route + "/{object_id}/actions/" + action
    spec["paths"][path] = entry
    policy["operations"].append(
        {
            "operation_id": op,
            "method": "POST",
            "path": path,
            "capability": cap,
            "role_templates": roles,
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": True,
        }
    )
for route, kind in [("workflow-templates", "WorkflowTemplate"), ("lineage-manifests", "LineageManifest")]:
    schemas[kind] = deepcopy(schemas["Programme"])
    schemas[kind]["properties"]["data"] = {"$ref": "#/components/schemas/" + kind + "Data"}
    schemas[kind + "Data"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": (
            {"title": {"type": "string"}, "required_approvals": {"const": 1}, "independent": {"const": True}}
            if kind == "WorkflowTemplate"
            else {
                "source_revisions": {"type": "array", "items": uuid, "maxItems": 10000},
                "digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            }
        ),
    }
    schemas[kind + "List"] = deepcopy(schemas["ProgrammeList"])
    schemas[kind + "List"]["properties"]["items"]["items"] = {"$ref": "#/components/schemas/" + kind}
    for item in [False, True]:
        suffix = "/{object_id}" if item else ""
        path = "/v1/tenants/{tenant_id}/" + route + suffix
        entry = {
            k: deepcopy(v)
            for k, v in spec["paths"]["/v1/tenants/{tenant_id}/programmes" + suffix].items()
            if k in {"parameters", "get"}
        }
        op = ("get_" if item else "list_") + route.replace("-", "_")
        entry["get"].update(
            operationId=op, summary="Read permitted " + route, **{"x-capability": route + ".read"}
        )
        entry["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + kind + ("" if item else "List")
        }
        spec["paths"][path] = entry
        policy["operations"].append(
            {
                "operation_id": op,
                "method": "GET",
                "path": path,
                "capability": route + ".read",
                "role_templates": ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )
event = json.loads((ROOT / "specification/contracts/event.schema.json").read_text())
event["properties"]["event_type"]["enum"].append("object.changed")
event["properties"]["schema_version"] = {"const": "1.1"}
augment(spec, policy)
augment_measurement(spec, policy)
augment_changes(spec, policy)
augment_periods(spec, policy)
augment_reporting(spec, policy)
augment_work(spec, policy)
augment_publication(spec, policy)
augment_planning(spec, policy)
augment_calculation(spec, policy)
augment_forms(spec, policy)
augment_imports(spec, policy)
augment_evidence(spec, policy)
# A baseline policy row whose operation no longer exists in the contract (its path and method
# were taken over by an implemented operation under another identifier) is dropped: the policy
# must describe exactly the operations of the contract (#19: create_organisation_units, superseded
# by create_organisation_unit on the same POST).
contract_operations = {
    operation["operationId"]
    for node in spec["paths"].values()
    for operation in node.values()
    if isinstance(operation, dict) and "operationId" in operation
}
policy["operations"] = [row for row in policy["operations"] if row["operation_id"] in contract_operations]
# The published domain API version comes from VERSION.json (impact_api/version.py).
spec["info"]["version"] = DOMAIN_API
policy["version"] = DOMAIN_API
for name, value in [("openapi.json", spec), ("access-policy.json", policy), ("event.schema.json", event)]:
    (ROOT / "packages/contracts" / name).write_text(json.dumps(value, indent=2) + "\n")
(ROOT / "packages/contracts/openapi-platform.json").write_text(
    json.dumps(platform_openapi(), indent=2) + "\n"
)
