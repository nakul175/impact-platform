"""FR-ACC-005 permission-safe derivative contracts."""

from .measurement_contracts import closed

VERSION = "1.77.0"
IMPLEMENTED = [
    ("post", "derivatives/{derivative_id}/revisions"),
    ("get", "derivatives/{derivative_id}/revisions/{revision_id}"),
]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    source = closed(
        {
            "object_id": {"type": "string", "format": "uuid"},
            "revision_id": {"type": "string", "format": "uuid"},
            "object_type": {"type": "string"},
            "capability": {"type": "string"},
        },
        ["object_id", "revision_id", "object_type", "capability"],
    )
    schemas["DerivativeManifestRequest"] = closed(
        {
            "revision_id": {"type": "string", "format": "uuid"},
            "kind": {"enum": ["Dashboard", "Search", "Analysis", "AIArtifact", "ApprovedAggregate"]},
            "disclosure_mode": {"enum": ["PRIVATE", "APPROVED_AGGREGATE"]},
            "sources": {"type": "array", "minItems": 1, "maxItems": 100, "items": source},
        },
        ["revision_id", "kind", "disclosure_mode", "sources"],
    )
    base = "/v1/tenants/{tenant_id}/derivatives/{derivative_id}/revisions"
    params = [
        {"name": "tenant_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}},
        {
            "name": "derivative_id",
            "in": "path",
            "required": True,
            "schema": {"type": "string", "format": "uuid"},
        },
    ]
    spec["paths"][base] = {
        "post": {
            "operationId": "create_derivative_manifest",
            "summary": "Create immutable derivative source provenance",
            "x-capability": "reports.write",
            "x-contract-version": VERSION,
            "parameters": params,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/DerivativeManifestRequest"}}
                },
            },
            "responses": {"200": {"description": "Immutable derivative manifest"}},
        }
    }
    spec["paths"][base + "/{revision_id}"] = {
        "get": {
            "operationId": "read_derivative_manifest",
            "summary": "Read a derivative only while every source remains readable",
            "x-capability": "reports.read",
            "x-contract-version": VERSION,
            "parameters": params
            + [
                {
                    "name": "revision_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            "responses": {
                "200": {"description": "Manifest with exact source revisions"},
                "404": {"description": "Derivative or a source is unavailable"},
            },
        }
    }
    for op, method, path, cap, guard in [
        (
            "create_derivative_manifest",
            "POST",
            base,
            "reports.write",
            "All exact sources must be currently readable; mixed sources remain private unless the object is an approved aggregate.",
        ),
        (
            "read_derivative_manifest",
            "GET",
            base + "/{revision_id}",
            "reports.read",
            "Every immutable source dependency is rechecked against current authority before disclosure.",
        ),
    ]:
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method,
                "path": path,
                "capability": cap,
                "role_templates": ["TENANT_ADMIN", "PROGRAMME_MANAGER", "ANALYST"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": method == "POST",
                "state_guard": guard,
            }
        )
