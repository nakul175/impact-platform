"""FR-ACC-001 closed batch resource-check contract."""

from .measurement_contracts import closed

VERSION = "1.73.0"
ROUTE = "access-checks/resources"
IMPLEMENTED = [("post", ROUTE)]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    selector = {
        "selector_id": {"type": "string", "pattern": "^[a-z][a-z0-9_-]{0,63}$"},
        "object_id": {"type": "string", "format": "uuid"},
        "object_type": {"type": "string", "pattern": "^[A-Z][A-Za-z0-9]{0,99}$"},
        "capability": {"type": "string", "pattern": "^[a-z][a-z0-9.-]{0,99}$"},
    }
    schemas["ResourceAccessSelector"] = closed(selector, list(selector))
    schemas["ResourceAccessBatch"] = closed(
        {
            "selectors": {
                "type": "array",
                "minItems": 1,
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/ResourceAccessSelector"},
            }
        },
        ["selectors"],
    )
    outcome = closed(
        {"selector_id": selector["selector_id"], "permitted": {"const": True}}, ["selector_id", "permitted"]
    )
    schemas["PermittedResourceAccessBatch"] = closed(
        {"permitted": {"type": "array", "maxItems": 100, "items": outcome}}, ["permitted"]
    )
    path = "/v1/tenants/{tenant_id}/" + ROUTE
    spec["paths"][path] = {
        "post": {
            "operationId": "check_permitted_resources",
            "summary": "Resolve each protected selector and disclose permitted outcomes only",
            "x-capability": "grants.read",
            "x-contract-version": VERSION,
            "parameters": [
                {
                    "name": "tenant_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/ResourceAccessBatch"}}
                },
            },
            "responses": {
                "200": {
                    "description": "Only currently permitted selector outcomes; denied and unknown selectors are omitted",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/PermittedResourceAccessBatch"}
                        }
                    },
                }
            },
        }
    }
    policy["operations"].append(
        {
            "operation_id": "check_permitted_resources",
            "method": "POST",
            "path": path,
            "capability": "grants.read",
            "role_templates": ["TENANT_ADMIN"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
            "state_guard": "Every item is resolved against current tenant, type, availability and requested capability; denied/unknown items emit no row and policy resolution errors fail closed.",
        }
    )
