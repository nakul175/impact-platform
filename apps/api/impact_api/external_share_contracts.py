"""FR-ACC-006 external share lifecycle contracts."""

from .measurement_contracts import closed

VERSION = "1.78.0"
IMPLEMENTED = [
    ("post", "external-shares"),
    ("get", "external-shares/{share_id}"),
    ("post", "external-shares/{share_id}/revocation"),
]


def augment(spec, policy):
    s = spec["components"]["schemas"]
    s["ExternalShareRequest"] = closed(
        {
            "derivative_id": {"type": "string", "format": "uuid"},
            "revision_id": {"type": "string", "format": "uuid"},
            "audience_principal_id": {"type": "string", "format": "uuid"},
            "actions": {
                "type": "array",
                "minItems": 1,
                "maxItems": 8,
                "uniqueItems": True,
                "items": {"enum": ["read", "download"]},
            },
            "reason": {"type": "string", "minLength": 1, "maxLength": 500},
            "expires_at": {"type": "string", "format": "date-time"},
        },
        ["derivative_id", "revision_id", "audience_principal_id", "actions", "reason", "expires_at"],
    )
    base = "/v1/tenants/{tenant_id}/external-shares"
    tenant = {
        "name": "tenant_id",
        "in": "path",
        "required": True,
        "schema": {"type": "string", "format": "uuid"},
    }
    share = {
        "name": "share_id",
        "in": "path",
        "required": True,
        "schema": {"type": "string", "format": "uuid"},
    }
    spec["paths"][base] = {
        "post": {
            "operationId": "create_external_share",
            "summary": "Share an exact derivative revision with one authenticated principal for at most seven days",
            "x-capability": "reports.share",
            "x-contract-version": VERSION,
            "parameters": [tenant],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/ExternalShareRequest"}}
                },
            },
            "responses": {"200": {"description": "Versioned share"}},
        }
    }
    spec["paths"][base + "/{share_id}"] = {
        "get": {
            "operationId": "read_external_share",
            "summary": "Read an unexpired share as its named audience",
            "x-capability": "reports.read",
            "x-contract-version": VERSION,
            "parameters": [tenant, share],
            "responses": {
                "200": {"description": "Currently authorised shared derivative"},
                "404": {"description": "Unavailable without artifact preview"},
            },
        }
    }
    spec["paths"][base + "/{share_id}/revocation"] = {
        "post": {
            "operationId": "revoke_external_share",
            "summary": "Revoke an owned share immediately",
            "x-capability": "reports.share",
            "x-contract-version": VERSION,
            "parameters": [tenant, share],
            "responses": {"200": {"description": "Revoked"}},
        }
    }
    rows = [
        (
            "create_external_share",
            "POST",
            base,
            "reports.share",
            ["TENANT_ADMIN", "PROGRAMME_MANAGER", "ANALYST"],
            True,
            "Exact revision, active audience, actions, owner, reason and expiry no later than seven days are mandatory.",
        ),
        (
            "read_external_share",
            "GET",
            base + "/{share_id}",
            "reports.read",
            ["TENANT_MEMBER"],
            False,
            "Audience, expiry, revocation and every source are revalidated; failure returns no preview.",
        ),
        (
            "revoke_external_share",
            "POST",
            base + "/{share_id}/revocation",
            "reports.share",
            ["TENANT_ADMIN", "PROGRAMME_MANAGER", "ANALYST"],
            True,
            "Only the current owner can revoke; repetition is idempotent.",
        ),
    ]
    for op, method, path, cap, roles, audit, guard in rows:
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method,
                "path": path,
                "capability": cap,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": audit,
                "state_guard": guard,
            }
        )
