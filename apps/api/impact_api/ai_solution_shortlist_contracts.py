"""Bounded source-backed option shortlist for one opportunity/use case."""

from copy import deepcopy

from .ai_solutions_catalog import catalog_schema
from .measurement_contracts import closed

VERSION = "1.36.0"
ROUTE = "ai-enablement/solution-shortlist"
IMPLEMENTED = [("get", ROUTE)]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    listing = deepcopy(catalog_schema()["properties"]["solutions"]["items"])
    item = closed(
        {
            "solution": listing,
            "vetting_basis": {"const": "SOURCE_BACKED_EDITORIAL_EDITION"},
            "opportunity_id": {"type": "string", "minLength": 1, "maxLength": 120},
        },
        ["solution", "vetting_basis", "opportunity_id"],
    )
    schemas["AISolutionShortlist"] = closed(
        {
            "content_version": {"type": "string"},
            "opportunity_id": {"type": "string"},
            "expanded": {"type": "boolean"},
            "default_limit": {"const": 3},
            "total_vetted": {"type": "integer", "minimum": 0, "maximum": 100},
            "items": {"type": "array", "maxItems": 100, "items": item},
        },
        ["content_version", "opportunity_id", "expanded", "default_limit", "total_vetted", "items"],
    )
    path = "/v1/tenants/{tenant_id}/" + ROUTE
    spec["paths"][path] = {
        "get": {
            "operationId": "get_ai_solution_shortlist",
            "summary": "Get a bounded source-backed shortlist",
            "x-capability": "ai.enablement.read",
            "x-contract-version": VERSION,
            "parameters": [
                {
                    "name": "tenant_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                },
                {
                    "name": "opportunity_id",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1, "maxLength": 120},
                },
                {
                    "name": "expanded",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "boolean", "default": False},
                },
            ],
            "responses": {
                "200": {
                    "description": "At most three by default; all source-backed matches only after explicit expansion",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AISolutionShortlist"}}
                    },
                },
                "400": {
                    "description": "Invalid opportunity",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}
                    },
                },
                "401": {
                    "description": "Authentication required",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}
                    },
                },
                "403": {
                    "description": "Policy denied",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}
                    },
                },
                "503": {
                    "description": "Catalogue unavailable",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}
                    },
                },
            },
        }
    }
    policy["operations"].append(
        {
            "operation_id": "get_ai_solution_shortlist",
            "method": "GET",
            "path": path,
            "capability": "ai.enablement.read",
            "role_templates": [
                "TENANT_ADMIN",
                "MEL_ADMIN",
                "PROGRAMME_MANAGER",
                "AUTHOR",
                "REVIEWER",
                "ANALYST",
                "DATA_STEWARD",
                "FINANCE",
            ],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
