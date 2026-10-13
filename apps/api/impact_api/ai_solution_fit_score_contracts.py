"""Closed contracts for six-dimensional, advisor-scored pilot option fit."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.37.0"
UUID = {"type": "string", "format": "uuid"}
ROUTE = "ai-enablement/solution-fit-scores"
IMPLEMENTED = [("get", ROUTE), ("post", ROUTE)]
DIMENSIONS = ("size", "budget", "context", "language", "data_sensitivity", "existing_systems")


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    value = closed(
        {
            "score": {"type": "integer", "minimum": 1, "maximum": 5},
            "explanation": {"type": "string", "minLength": 1, "maxLength": 1000, "pattern": r"\S"},
        },
        ["score", "explanation"],
    )
    dimensions = closed({name: deepcopy(value) for name in DIMENSIONS}, list(DIMENSIONS))
    request = closed(
        {
            "operation_id": deepcopy(UUID),
            "opportunity_id": {"type": "string", "minLength": 1, "maxLength": 120},
            "solution_id": {"type": "string", "minLength": 1, "maxLength": 120},
            "rubric_version": {"const": "pilot-fit-v1"},
            "dimensions": dimensions,
        },
        ["operation_id", "opportunity_id", "solution_id", "rubric_version", "dimensions"],
    )
    schemas["AISolutionFitScoreRequest"] = request
    response_dimensions = closed({name: deepcopy(value) for name in DIMENSIONS}, list(DIMENSIONS))
    response = closed(
        {
            "score_id": deepcopy(UUID),
            "opportunity_id": {"type": "string"},
            "solution_id": {"type": "string"},
            "catalogue_content_version": {"type": "string"},
            "rubric_version": {"const": "pilot-fit-v1"},
            "status": {"enum": ["COMPLETE", "INCOMPLETE"]},
            "advisor_membership_id": deepcopy(UUID),
            "dimensions": response_dimensions,
            "scored_at": {"type": "string", "format": "date-time"},
        },
        [
            "score_id",
            "opportunity_id",
            "solution_id",
            "catalogue_content_version",
            "rubric_version",
            "status",
            "advisor_membership_id",
            "dimensions",
            "scored_at",
        ],
    )
    schemas["AISolutionFitScore"] = response
    schemas["AISolutionFitScoreList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AISolutionFitScore"},
            }
        },
        ["items"],
    )
    path = "/v1/tenants/{tenant_id}/" + ROUTE
    parameters = [{"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(UUID)}]
    errors = {
        code: {
            "description": "Request refused",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}},
        }
        for code in ("400", "401", "403", "404", "409", "422", "429", "503")
    }
    spec["paths"][path] = {
        "get": {
            "operationId": "list_ai_solution_fit_scores",
            "summary": "List latest advisor fit scores for an opportunity",
            "x-capability": "ai.enablement.read",
            "x-contract-version": VERSION,
            "parameters": parameters
            + [
                {
                    "name": "opportunity_id",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1, "maxLength": 120},
                }
            ],
            "responses": {
                "200": {
                    "description": "Latest immutable score per option",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AISolutionFitScoreList"}
                        }
                    },
                },
                **errors,
            },
        },
        "post": {
            "operationId": "create_ai_solution_fit_score",
            "summary": "Record a complete advisor-scored pilot fit",
            "x-capability": "ai.solution-fit.score",
            "x-contract-version": VERSION,
            "parameters": parameters,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AISolutionFitScoreRequest"}}
                },
            },
            "responses": {
                "201": {
                    "description": "Immutable complete fit score",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AISolutionFitScore"}}
                    },
                },
                **errors,
            },
        },
    }
    policy["operations"].extend(
        [
            {
                "operation_id": "list_ai_solution_fit_scores",
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
            },
            {
                "operation_id": "create_ai_solution_fit_score",
                "method": "POST",
                "path": path,
                "capability": "ai.solution-fit.score",
                "role_templates": ["REVIEWER"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300,
                "audit": True,
            },
        ]
    )
