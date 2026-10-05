"""Closed, deterministic nonprofit planning tools; no procurement or impact approval."""

from copy import deepcopy

from .ai_enablement_contracts import ROLES
from .measurement_contracts import closed

VERSION = "1.22.0"
IMPLEMENTED = [
    ("post", "ai-enablement/cost-comparison"),
    ("post", "ai-enablement/pilot-evaluation"),
    ("get", "ai-enablement/task-templates"),
]
DECIMAL = {
    "type": "string",
    "maxLength": 39,
    "pattern": r"^(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?$",
}
SLUG = {"type": "string", "pattern": r"^[a-z][a-z0-9_-]{0,63}$", "maxLength": 64}


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    practice = {
        "template_id": {"type": "string", "maxLength": 64},
        "brief": {"type": "string", "maxLength": 2500},
        "draft": {"type": "string", "maxLength": 2500},
        "review_notes": {"type": "string", "maxLength": 2500},
        "checked_steps": {
            "type": "array",
            "maxItems": 10,
            "uniqueItems": True,
            "items": {"type": "string", "maxLength": 64},
        },
    }
    schemas["AITaskPracticeData"] = closed(practice, list(practice))
    guidance = {"type": "array", "maxItems": 20, "items": {"type": "string", "maxLength": 2500}}
    step = {"id": {"type": "string", "maxLength": 64}, "label": {"type": "string", "maxLength": 500}}
    template = {
        "id": {"type": "string", "maxLength": 64},
        "title": {"type": "string", "maxLength": 150},
        "purpose": {"type": "string", "maxLength": 1000},
        "input_guidance": deepcopy(guidance),
        "example_brief": {"type": "string", "maxLength": 2500},
        "allowed_inputs": deepcopy(guidance),
        "prohibited_inputs": deepcopy(guidance),
        "prompt_framework": deepcopy(guidance),
        "review_steps": {"type": "array", "maxItems": 10, "items": closed(step, list(step))},
    }
    schemas["AITaskPracticeTemplate"] = closed(template, list(template))
    templates = {
        "content_version": {"type": "string", "maxLength": 100},
        "templates": {
            "type": "array",
            "maxItems": 20,
            "items": {"$ref": "#/components/schemas/AITaskPracticeTemplate"},
        },
        "disclaimer": {"type": "string", "maxLength": 1000},
    }
    schemas["AITaskPracticeTemplates"] = closed(templates, list(templates))
    line = {
        "id": deepcopy(SLUG),
        "category": {
            "enum": [
                "SETUP",
                "SUBSCRIPTION",
                "USAGE",
                "INTEGRATION",
                "TRAINING",
                "REVIEW",
                "SUPPORT",
                "EXIT",
                "OTHER",
            ]
        },
        "label": {"type": "string", "minLength": 1, "maxLength": 150},
        "quantity": deepcopy(DECIMAL),
        "unit_amount": {"oneOf": [deepcopy(DECIMAL), {"type": "null"}]},
        "cadence": {"enum": ["ONE_OFF", "MONTHLY"]},
    }
    schemas["AICostLine"] = closed(line, list(line))
    offer = {
        "id": deepcopy(SLUG),
        "name": {"type": "string", "minLength": 1, "maxLength": 150},
        "lines": {
            "type": "array",
            "minItems": 1,
            "maxItems": 20,
            "items": {"$ref": "#/components/schemas/AICostLine"},
        },
    }
    schemas["AICostOffer"] = closed(offer, list(offer))
    comparison = {
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$", "minLength": 3, "maxLength": 3},
        "period_months": {"type": "integer", "minimum": 1, "maximum": 60},
        "offers": {
            "type": "array",
            "minItems": 1,
            "maxItems": 4,
            "items": {"$ref": "#/components/schemas/AICostOffer"},
        },
    }
    schemas["AICostComparisonRequest"] = closed(comparison, list(comparison))
    # Exact products can exceed input storage width. These are response strings,
    # never rounded values substituted for the original bounded input amounts.
    exact = {"type": "string", "maxLength": 100, "pattern": r"^[0-9]+(?:\.[0-9]+)?$"}
    result_offer = {
        "id": deepcopy(SLUG),
        "name": {"type": "string", "maxLength": 150},
        "known_subtotal": deepcopy(exact),
        "complete_total": {"oneOf": [deepcopy(exact), {"type": "null"}]},
        "missing_line_ids": {"type": "array", "maxItems": 20, "items": deepcopy(SLUG)},
    }
    schemas["AICostOfferResult"] = closed(result_offer, list(result_offer))
    result = {
        "currency": deepcopy(comparison["currency"]),
        "period_months": deepcopy(comparison["period_months"]),
        "status": {"enum": ["COMPLETE", "INCOMPLETE"]},
        "offers": {
            "type": "array",
            "minItems": 1,
            "maxItems": 4,
            "items": {"$ref": "#/components/schemas/AICostOfferResult"},
        },
        "cheapest_offer_ids": {"type": "array", "maxItems": 4, "uniqueItems": True, "items": deepcopy(SLUG)},
        "disclaimer": {"type": "string", "maxLength": 1000},
    }
    schemas["AICostComparisonResult"] = closed(result, list(result))
    sample = {
        "sample_size": {"type": "integer", "minimum": 1, "maximum": 10000},
        "total_drafting_minutes": deepcopy(DECIMAL),
        "total_review_minutes": deepcopy(DECIMAL),
        "factual_corrections": {"type": "integer", "minimum": 0, "maximum": 1000000},
    }
    schemas["AIPilotSample"] = closed(sample, list(sample))
    evaluation = {
        "task_label": {"type": "string", "minLength": 1, "maxLength": 150},
        "baseline": {"$ref": "#/components/schemas/AIPilotSample"},
        "pilot": {"$ref": "#/components/schemas/AIPilotSample"},
        "comparable": {"type": "boolean"},
        "notes": {"type": "string", "maxLength": 1000},
    }
    schemas["AIPilotEvaluationRequest"] = closed(evaluation, list(evaluation))
    displayed = {"type": "string", "maxLength": 100, "pattern": r"^-?[0-9]+(?:\.[0-9]{1,6})?$"}
    measures = {
        name: deepcopy(displayed)
        for name in ("total_minutes", "minutes_per_item", "factual_corrections_per_item")
    }
    schemas["AIPilotMeasures"] = closed(measures, list(measures))
    improvement = {
        "status": {"enum": ["DEFINED", "UNDEFINED"]},
        "percent": {"oneOf": [deepcopy(displayed), {"type": "null"}]},
        "reason": {"enum": ["COMPARABLE_SAMPLES", "ZERO_BASELINE", "SAMPLES_NOT_COMPARABLE"]},
    }
    result = {
        "status": {"const": "SELF_REPORTED_DRAFT"},
        "task_label": deepcopy(evaluation["task_label"]),
        "comparable": {"type": "boolean"},
        "notes": deepcopy(evaluation["notes"]),
        "source": closed(
            {
                "baseline": {"$ref": "#/components/schemas/AIPilotSample"},
                "pilot": {"$ref": "#/components/schemas/AIPilotSample"},
            },
            ["baseline", "pilot"],
        ),
        "baseline": {"$ref": "#/components/schemas/AIPilotMeasures"},
        "pilot": {"$ref": "#/components/schemas/AIPilotMeasures"},
        "improvement": closed(improvement, list(improvement)),
        "disclaimer": {"type": "string", "maxLength": 1000},
    }
    schemas["AIPilotEvaluationResult"] = closed(result, list(result))
    for route, operation, request, response in [
        (
            "cost-comparison",
            "compare_ai_procurement_costs",
            "AICostComparisonRequest",
            "AICostComparisonResult",
        ),
        ("pilot-evaluation", "evaluate_ai_pilot", "AIPilotEvaluationRequest", "AIPilotEvaluationResult"),
    ]:
        path = "/v1/tenants/{tenant_id}/ai-enablement/" + route
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": "ai.enablement.read",
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
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            },
            "responses": {
                "200": {
                    "description": "Deterministic unapproved planning result; no record or external action",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        for status in ("400", "401", "403", "404", "422", "503"):
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"].setdefault(path, {})["post"] = entry
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": "POST",
                "path": path,
                "capability": "ai.enablement.read",
                "role_templates": deepcopy(ROLES),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )
    path = "/v1/tenants/{tenant_id}/ai-enablement/task-templates"
    entry = {
        "operationId": "get_ai_task_templates",
        "summary": "Get guided nonprofit task practice",
        "x-capability": "ai.enablement.read",
        "x-contract-version": VERSION,
        "parameters": [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ],
        "responses": {
            "200": {
                "description": "Versioned editorial exercises; no generated or approved output",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AITaskPracticeTemplates"}}
                },
            }
        },
    }
    for status in ("401", "403", "404", "503"):
        entry["responses"][status] = {
            "description": "Request refused",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        }
    spec["paths"].setdefault(path, {})["get"] = entry
    policy["operations"].append(
        {
            "operation_id": "get_ai_task_templates",
            "method": "GET",
            "path": path,
            "capability": "ai.enablement.read",
            "role_templates": deepcopy(ROLES),
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
