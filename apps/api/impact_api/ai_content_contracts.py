"""Versioned, closed historical guidance; current scoped plan access is always required."""

from copy import deepcopy

from .ai_content_archives import COMPONENTS, EDITIONS
from .ai_enablement_contracts import ROLES
from .measurement_contracts import UUID, closed

VERSION = "1.23.0"
IMPLEMENTED = [
    ("get", "ai-enablement/plans/{object_id}/revisions/{revision_id}/guidance"),
    ("get", "ai-enablement/plans/{object_id}/revisions"),
]


def unavailable_component():
    return closed(
        {
            "status": {"const": "UNAVAILABLE"},
            "content_version": {"type": ["string", "null"], "maxLength": 100},
            "payload": {"type": "null"},
        },
        ["status", "content_version", "payload"],
    )


def guidance_variants(payload_schema):
    """One closed variant per archive edition, binding its label to its own payload shapes, plus the
    unavailable variant. `payload_schema(version, name)` gives a component's payload schema."""
    common = {
        "object_id": deepcopy(UUID),
        "revision_id": deepcopy(UUID),
    }
    variants = []
    for version in EDITIONS:
        components = {}
        for name in COMPONENTS:
            available = closed(
                {
                    "status": {"const": "AVAILABLE"},
                    "content_version": {"type": "string", "minLength": 1, "maxLength": 100},
                    "payload": payload_schema(version, name),
                },
                ["status", "content_version", "payload"],
            )
            components[name] = {"oneOf": [available, unavailable_component()]}
        result = {
            **deepcopy(common),
            "status": {"enum": ["COMPLETE", "PARTIAL"]},
            "snapshot_schema_version": {"const": version},
            "captured_at": {"type": "string", "format": "date-time"},
            "snapshot_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            **components,
            "disclaimer": {"type": "string", "maxLength": 1000},
        }
        variants.append(closed(result, list(result)))
    result = {
        **deepcopy(common),
        "status": {"const": "UNAVAILABLE"},
        "snapshot_schema_version": {"type": "null"},
        "captured_at": {"type": "null"},
        "snapshot_sha256": {"type": "null"},
        **{name: unavailable_component() for name in COMPONENTS},
        "disclaimer": {"type": "string", "maxLength": 1000},
    }
    variants.append(closed(result, list(result)))
    return variants


def archived_component_names(schemas):
    """Register AIArchived<Component>V<n> per edition; an identical component reuses the earlier name."""
    names, registered = {}, []
    for version, components in EDITIONS.items():
        suffix = "V" + version.rsplit("-v", 1)[-1]
        for name in COMPONENTS:
            schema = components[name]
            prefix = "AIArchived" + name.capitalize()
            ref = next((ref for kept, ref in registered if ref.startswith(prefix) and kept == schema), None)
            if ref is None:
                ref = prefix + suffix
                schemas[ref] = deepcopy(schema)
                registered.append((schema, ref))
            names[version, name] = ref
    return names


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    names = archived_component_names(schemas)
    schemas["AIAdoptionPlanGuidance"] = {
        "oneOf": guidance_variants(
            lambda version, name: {"$ref": "#/components/schemas/" + names[version, name]}
        )
    }
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
