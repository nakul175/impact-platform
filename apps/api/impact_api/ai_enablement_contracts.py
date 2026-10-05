"""Nonprofit AI enablement: editorial assessment and separately permitted advisory drafts."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.20.0"
IMPLEMENTED = [
    ("get", "ai-enablement/catalog"),
    ("post", "ai-enablement/assessment"),
    ("post", "ai-enablement/advisory"),
    ("get", "ai-enablement/solutions"),
]
ROLES = ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST", "DATA_STEWARD"]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    schemas["AIEnablementProfile"] = closed(
        {
            "sector": {"enum": ["GENERAL", "EDUCATION", "HEALTH", "LIVELIHOODS", "ENVIRONMENT"]},
            "team_size": {"type": "integer", "minimum": 1, "maximum": 100000},
            "goal": {"type": "string", "minLength": 1, "maxLength": 1000},
            "data_readiness": {"enum": ["NONE", "BASIC", "STRUCTURED"]},
            "ai_experience": {"enum": ["NONE", "EXPERIMENTING", "REGULAR"]},
            "sensitive_data": {"type": "boolean"},
        },
        ["sector", "team_size", "goal", "data_readiness", "ai_experience", "sensitive_data"],
    )
    schemas["AIAssessmentRequest"] = closed(
        {"profile": {"$ref": "#/components/schemas/AIEnablementProfile"}}, ["profile"]
    )
    schemas["AIAdvisoryRequest"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "profile": {"$ref": "#/components/schemas/AIEnablementProfile"},
            "consent": {"const": True},
        },
        ["operation_id", "profile", "consent"],
    )
    # This increment publishes versioned editorial content, not an authored domain object.
    schemas["AIEnablementCatalog"] = {
        "type": "object",
        "required": [
            "schema_version",
            "content_version",
            "provenance",
            "journey",
            "use_cases",
            "learning_paths",
            "procurement_criteria",
            "marketplace_status",
            "advisory_available",
        ],
    }
    schemas["AIEnablementAssessment"] = closed({"assessment": {"type": "object"}}, ["assessment"])
    schemas["AISolutionsCatalog"] = {
        "type": "object",
        "required": ["content_version", "checked_on", "explanation", "solutions", "comparison_criteria"],
    }
    schemas["AIAdvisoryDraft"] = closed(
        {
            "status": {"const": "DRAFT"},
            "text": {"type": "string", "maxLength": 12000},
            "assessment": {"type": "object"},
            "model": {"type": "string"},
            "disclaimer": {"type": "string"},
        },
        ["status", "text", "assessment", "model", "disclaimer"],
    )
    for method, route, op, cap, request, response, roles in [
        (
            "get",
            "ai-enablement/catalog",
            "get_ai_enablement_catalog",
            "ai.enablement.read",
            None,
            "AIEnablementCatalog",
            ROLES,
        ),
        (
            "post",
            "ai-enablement/assessment",
            "assess_ai_enablement",
            "ai.enablement.read",
            "AIAssessmentRequest",
            "AIEnablementAssessment",
            ROLES,
        ),
        (
            "get",
            "ai-enablement/solutions",
            "get_ai_solutions",
            "ai.enablement.read",
            None,
            "AISolutionsCatalog",
            ROLES,
        ),
        (
            "post",
            "ai-enablement/advisory",
            "create_ai_advisory",
            "ai.advisory.request",
            "AIAdvisoryRequest",
            "AIAdvisoryDraft",
            ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
        ),
    ]:
        path = "/v1/tenants/{tenant_id}/" + route
        node = {
            "parameters": [
                {
                    "name": "tenant_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            ]
        }
        entry = {
            "operationId": op,
            "summary": op.replace("_", " "),
            "x-capability": cap,
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "Editorial content or unapproved draft",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ["400", "401", "403", "404", "409", "429", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        node[method] = entry
        spec["paths"][path] = node
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": path,
                "capability": cap,
                "role_templates": deepcopy(roles),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": op == "create_ai_advisory",
            }
        )
