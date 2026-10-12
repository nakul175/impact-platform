"""FR-ACC-002 strictly narrowing grant-facet contract."""

from .measurement_contracts import closed

VERSION = "1.74.0"
ROUTE = "grants/{grant_id}/field-policy"
IMPLEMENTED = [("post", ROUTE)]


def augment(spec, policy):
    s = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    categories = {
        "type": "array",
        "uniqueItems": True,
        "maxItems": 4,
        "items": {"enum": ["PUBLIC", "INTERNAL", "SENSITIVE", "DIRECT_IDENTIFIER"]},
    }
    request = {
        "operation_id": uid,
        "record_object_ids": {
            "type": "array",
            "minItems": 1,
            "maxItems": 100,
            "uniqueItems": True,
            "items": uid,
        },
        "readable_field_categories": {**categories, "minItems": 1},
        "writable_field_categories": categories,
    }
    s["FineGrainedGrantFacetAttach"] = closed(request, list(request))
    result = {key: value for key, value in request.items() if key != "operation_id"}
    result.update(grant_id=uid, attached_at={"type": "string", "format": "date-time"})
    s["FineGrainedGrantFacet"] = closed(result, list(result))
    path = "/v1/tenants/{tenant_id}/" + ROUTE
    spec["paths"][path] = {
        "post": {
            "operationId": "attach_fine_grained_grant_facets",
            "summary": "Narrow an approved grant by record condition and field category",
            "x-capability": "grant.approve",
            "x-contract-version": VERSION,
            "parameters": [
                {"name": "tenant_id", "in": "path", "required": True, "schema": uid},
                {"name": "grant_id", "in": "path", "required": True, "schema": uid},
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/FineGrainedGrantFacetAttach"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Immutable narrowing facet attached",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/FineGrainedGrantFacet"}}
                    },
                }
            },
        }
    }
    policy["operations"].append(
        {
            "operation_id": "attach_fine_grained_grant_facets",
            "method": "POST",
            "path": path,
            "capability": "grant.approve",
            "role_templates": ["TENANT_ADMIN"],
            "purpose_required": False,
            "fresh_assurance_seconds": 300,
            "audit": True,
            "state_guard": "Active existing grant only; selected records remain inside its existing scope; writable categories are a subset of readable categories; the facet is attach-once and can only narrow.",
        }
    )
