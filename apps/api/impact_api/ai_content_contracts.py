"""Versioned, closed historical guidance; current scoped plan access is always required."""

from copy import deepcopy

from .ai_content_archives import CONTENT_SCHEMAS, SCHEMA_VERSION
from .ai_enablement_contracts import ROLES
from .measurement_contracts import UUID, closed

VERSION = "1.23.0"
IMPLEMENTED = [
    ("get", "ai-enablement/plans/{object_id}/revisions/{revision_id}/guidance"),
    ("get", "ai-enablement/plans/{object_id}/revisions"),
]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    components = {}
    for name in ("catalog", "solutions", "practice"):
        payload_name = "AIArchived" + name.capitalize() + "V1"
        schemas[payload_name] = deepcopy(CONTENT_SCHEMAS[name])
        available = closed(
            {
                "status": {"const": "AVAILABLE"},
                "content_version": {"type": "string", "minLength": 1, "maxLength": 100},
                "payload": {"$ref": "#/components/schemas/" + payload_name},
            },
            ["status", "content_version", "payload"],
        )
        unavailable = closed(
            {
                "status": {"const": "UNAVAILABLE"},
                "content_version": {"type": ["string", "null"], "maxLength": 100},
                "payload": {"type": "null"},
            },
            ["status", "content_version", "payload"],
        )
        components[name] = {"oneOf": [available, unavailable]}
    result = {
        "object_id": deepcopy(UUID),
        "revision_id": deepcopy(UUID),
        "status": {"enum": ["COMPLETE", "PARTIAL", "UNAVAILABLE"]},
        "snapshot_schema_version": {"enum": [SCHEMA_VERSION, None]},
        "captured_at": {"type": ["string", "null"], "format": "date-time"},
        "snapshot_sha256": {"type": ["string", "null"], "pattern": "^[a-f0-9]{64}$"},
        **components,
        "disclaimer": {"type": "string", "maxLength": 1000},
    }
    schemas["AIAdoptionPlanGuidance"] = closed(result, list(result))
    schemas["AIAdoptionPlanCompatibility"]["properties"]["historical_snapshots_available"] = {
        "type": "boolean"
    }
    path = "/v1/tenants/{tenant_id}/" + IMPLEMENTED[0][1]
    entry = {
        "operationId": "get_ai_adoption_guidance",
        "summary": "Read editorial guidance captured for an exact saved adoption-plan revision",
        "x-capability": "ai.enablement.read",
        "x-contract-version": VERSION,
        "parameters": [
            {"name": name, "in": "path", "required": True, "schema": deepcopy(UUID)}
            for name in ("tenant_id", "object_id", "revision_id")
        ],
        "responses": {
            "200": {
                "description": "Actual archived guidance or explicit historical unavailability",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIAdoptionPlanGuidance"}}
                },
            }
        },
    }
    for status in ("400", "401", "403", "404", "503"):
        entry["responses"][status] = {
            "description": "Request refused; hidden and missing revisions are indistinguishable",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        }
    spec["paths"][path] = {"get": entry}
    policy["operations"].append(
        {
            "operation_id": "get_ai_adoption_guidance",
            "method": "GET",
            "path": path,
            "capability": "ai.enablement.read",
            "role_templates": deepcopy(ROLES),
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
    item = {
        "revision_id": deepcopy(UUID),
        "revision_number": {"type": "integer", "minimum": 1},
        "saved_at": {"type": "string", "format": "date-time"},
        "title": {"type": "string", "maxLength": 150},
        "historical_snapshots_available": {"type": "boolean"},
    }
    schemas["AIAdoptionRevision"] = closed(item, list(item))
    history = {
        "object_id": deepcopy(UUID),
        "items": {
            "type": "array",
            "maxItems": 100,
            "items": {"$ref": "#/components/schemas/AIAdoptionRevision"},
        },
        "next_cursor": {"type": ["string", "null"]},
    }
    schemas["AIAdoptionRevisionList"] = closed(history, list(history))
    history_path = "/v1/tenants/{tenant_id}/" + IMPLEMENTED[1][1]
    history_entry = deepcopy(entry)
    history_entry["operationId"] = "list_ai_adoption_revisions"
    history_entry["summary"] = "List available saved revisions of a currently readable adoption plan"
    history_entry["parameters"] = [
        parameter for parameter in history_entry["parameters"] if parameter["name"] != "revision_id"
    ] + [
        {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100}},
        {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
    ]
    history_entry["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AIAdoptionRevisionList"
    }
    spec["paths"][history_path] = {"get": history_entry}
    policy["operations"].append(
        {
            "operation_id": "list_ai_adoption_revisions",
            "method": "GET",
            "path": history_path,
            "capability": "ai.enablement.read",
            "role_templates": deepcopy(ROLES),
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
