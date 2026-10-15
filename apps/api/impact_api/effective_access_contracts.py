"""FR-ACC-003 safe own and administrator effective-access explanations."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.75.0"
IMPLEMENTED = [("post", "access/effective/self"), ("post", "access/effective/simulations")]
MEMBER_ROLES = [
    "TENANT_ADMIN",
    "MEL_ADMIN",
    "AUTHOR",
    "REVIEWER",
    "PROGRAMME_MANAGER",
    "DATA_STEWARD",
    "ENUMERATOR",
    "ANALYST",
    "PRIVACY",
    "AUDIT_READER",
    "EXTERNAL",
    "FINANCE",
]


def augment(spec, policy):
    s = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    request = {
        "operation_id": {"type": "string", "minLength": 1, "maxLength": 120},
        "object_id": {"oneOf": [deepcopy(uid), {"type": "null"}]},
        "purpose": {"type": ["string", "null"], "minLength": 1, "maxLength": 100},
        "field_category": {
            "type": ["string", "null"],
            "enum": [None, "PUBLIC", "INTERNAL", "SENSITIVE", "DIRECT_IDENTIFIER"],
        },
        "field_access": {"type": ["string", "null"], "enum": [None, "READ", "WRITE"]},
    }
    s["OwnEffectiveAccessRequest"] = closed(request, ["operation_id", "object_id"])
    simulation = {**deepcopy(request), "subject_principal_id": deepcopy(uid)}
    s["EffectiveAccessSimulationRequest"] = closed(
        simulation, ["operation_id", "object_id", "subject_principal_id"]
    )
    path_item = closed(
        {
            "path_id": {"type": "string", "pattern": "^PATH-[1-9][0-9]*$"},
            "source": {"enum": ["DIRECT", "GROUP"]},
            "scope_type": {"enum": ["TENANT", "PROGRAMME", "ASSIGNMENT", "OBJECT_SET"]},
            "record_condition_applied": {"type": "boolean"},
            "readable_field_categories": {
                "type": ["array", "null"],
                "items": {"type": "string"},
                "maxItems": 16,
            },
            "writable_field_categories": {
                "type": ["array", "null"],
                "items": {"type": "string"},
                "maxItems": 16,
            },
            "decision": {"enum": ["PERMITTED", "DENIED"]},
            "restrictions": {
                "type": "array",
                "items": {"enum": ["OUTSIDE_SCOPE", "RECORD_CONDITION", "FIELD_CATEGORY"]},
                "uniqueItems": True,
            },
        },
        [
            "path_id",
            "source",
            "scope_type",
            "record_condition_applied",
            "readable_field_categories",
            "writable_field_categories",
            "decision",
            "restrictions",
        ],
    )
    result = {
        "operation_id": request["operation_id"],
        "capability": {"type": "string", "minLength": 1, "maxLength": 100},
        "decision": {"enum": ["PERMITTED", "DENIED"]},
        "grant_paths": {"type": "array", "maxItems": 100, "items": path_item},
        "restrictions": {
            "type": "array",
            "items": {
                "enum": [
                    "OUTSIDE_SCOPE",
                    "RECORD_CONDITION",
                    "FIELD_CATEGORY",
                    "RESOURCE_UNAVAILABLE",
                ]
            },
            "uniqueItems": True,
        },
        "missing_assurance": {
            "type": "array",
            "items": {
                "enum": [
                    "CURRENT_SESSION_ASSURANCE",
                    "MFA_ASSURANCE",
                    "FRESH_AUTHENTICATION",
                    "PURPOSE_REQUIRED",
                    "PURPOSE_MISMATCH",
                ]
            },
            "uniqueItems": True,
        },
    }
    s["OwnEffectiveAccess"] = closed(result, list(result))
    s["SimulatedEffectiveAccess"] = closed(deepcopy(result), list(result))
    for suffix, operation, request_schema, response_schema, capability, roles in [
        (
            "self",
            "explain_own_effective_access",
            "OwnEffectiveAccessRequest",
            "OwnEffectiveAccess",
            "notifications.read",
            MEMBER_ROLES,
        ),
        (
            "simulations",
            "simulate_effective_access",
            "EffectiveAccessSimulationRequest",
            "SimulatedEffectiveAccess",
            "grants.read",
            ["TENANT_ADMIN"],
        ),
    ]:
        path = "/v1/tenants/{tenant_id}/access/effective/" + suffix
        spec["paths"][path] = {
            "post": {
                "operationId": operation,
                "summary": "Explain effective access without hidden resource names or values",
                "x-capability": capability,
                "x-contract-version": VERSION,
                "parameters": [
                    {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/" + request_schema}}
                    },
                },
                "responses": {
                    "200": {
                        "description": "Sanitized grant paths, restrictions and missing assurance",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/" + response_schema}
                            }
                        },
                    }
                },
            }
        }
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": "POST",
                "path": path,
                "capability": capability,
                "role_templates": deepcopy(roles),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
                "state_guard": "Self explains only the current principal. Simulation requires tenant-wide grants.read and a current in-tenant subject; outputs contain no resource names or field values.",
            }
        )
