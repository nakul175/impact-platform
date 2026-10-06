"""Closed deliberate impact-reference command and read-only governed evidence view."""

from copy import deepcopy

from .ai_adoption_contracts import MANAGERS
from .ai_enablement_contracts import ROLES
from .ai_impact_references import REFERENCE_VERSION
from .measurement_contracts import UUID, closed

VERSION = "1.24.0"
IMPLEMENTED = [
    ("put", "ai-enablement/plans/{object_id}/impact-reference"),
    ("get", "ai-enablement/plans/{object_id}/impact-reference/result"),
]


def _nullable(schema):
    return {"oneOf": [{"type": "null"}, schema]}


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    inputs = {
        "programme_id": deepcopy(UUID),
        "indicator_id": deepcopy(UUID),
        "period_id": deepcopy(UUID),
        "interpretation_note": {"type": "string", "maxLength": 1000},
    }
    schemas["AIImpactReferenceInput"] = closed(inputs, list(inputs))
    command = {
        "operation_id": deepcopy(UUID),
        "expected_revision": deepcopy(UUID),
        "data": _nullable({"$ref": "#/components/schemas/AIImpactReferenceInput"}),
    }
    schemas["AIImpactReferenceCommand"] = closed(command, list(command))
    persisted = {
        **deepcopy(inputs),
        "schema_version": {"const": REFERENCE_VERSION},
        **{
            name + suffix: deepcopy(UUID)
            for name in ("programme", "indicator", "definition", "period", "calendar")
            for suffix in ("_id", "_revision")
        },
        "snapshot_id": {"type": ["string", "null"], "format": "uuid"},
        "snapshot_revision": {"type": ["string", "null"], "format": "uuid"},
        "snapshot_version": {"type": ["integer", "null"], "minimum": 1},
    }
    schemas["AIImpactReference"] = closed(persisted, list(persisted))
    # Core IDs and pins are private server metadata. Ordinary plan reads project them out;
    # only this separately authorized result includes the reference.
    programme = schemas["ProgrammeDashboard"]["properties"]
    status = {
        name: {"enum": ["CURRENT", "CHANGED"]}
        for name in ("programme", "indicator", "definition", "period", "calendar")
    }
    status["snapshot"] = {"enum": ["CURRENT", "CHANGED", "ABSENT"]}
    result = {
        "object_id": deepcopy(UUID),
        "revision_id": deepcopy(UUID),
        "status": {"const": "LINKED"},
        "reference": {"$ref": "#/components/schemas/AIImpactReference"},
        "reference_status": closed(status, list(status)),
        "programme_title": {"type": ["string", "null"], "maxLength": 2000},
        "period": deepcopy(programme["period"]),
        "indicator": deepcopy(programme["indicators"]["items"]),
        "stale_rule": {"type": "string", "maxLength": 2000},
        "disclaimer": {"type": "string", "maxLength": 1000},
    }
    schemas["AIImpactReferenceResult"] = closed(result, list(result))
    for method, route, operation, response, manage in [
        ("put", IMPLEMENTED[0][1], "set_ai_impact_reference", "AIAdoptionPlanReceipt", True),
        ("get", IMPLEMENTED[1][1], "get_ai_impact_reference_result", "AIImpactReferenceResult", False),
    ]:
        path = "/v1/tenants/{tenant_id}/" + route
        capability = "ai.enablement.manage" if manage else "ai.enablement.read"
        entry = {
            "operationId": operation,
            "summary": "Deliberately link, refresh or clear pinned programme evidence"
            if manage
            else "Read currently authorized evidence for an AI-plan impact reference",
            "x-capability": capability,
            "x-contract-version": VERSION,
            "parameters": [
                {"name": name, "in": "path", "required": True, "schema": deepcopy(UUID)}
                for name in ("tenant_id", "object_id")
            ],
            "responses": {
                "200": {
                    "description": "Saved relationship revision"
                    if manage
                    else "Governed evidence; official and provisional values remain separate",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if manage:
            entry["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIImpactReferenceCommand"}}
                },
            }
        for code in ("400", "401", "403", "404", "409", "422", "503"):
            entry["responses"][code] = {
                "description": "Request refused without exposing hidden core records",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"][path] = {method: entry}
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": capability,
                "role_templates": deepcopy(MANAGERS if manage else ROLES),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": manage,
            }
        )
