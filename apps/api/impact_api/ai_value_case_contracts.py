"""Closed contracts for deterministic self-reported value-case calculations."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.44.0"
ROOT = "ai-enablement/value-case"
IMPLEMENTED = [("post", ROOT)]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    amount = {"type": "string", "pattern": r"^(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?$"}
    signed = {"type": "string", "pattern": r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]{1,6})?$"}
    source = {
        "source_label": {"type": "string", "minLength": 1, "maxLength": 200},
        "annual_operating_cost": deepcopy(amount),
    }
    schemas["AIValueCaseSource"] = closed(source, list(source))
    cost_input = {
        field: deepcopy(amount)
        for field in ("licences_annual", "setup_one_off", "training_one_off", "staff_time_annual")
    }
    schemas["AIValueCaseCostInput"] = closed(cost_input, list(cost_input))
    request = {
        "opportunity_id": {"type": "string", "minLength": 1, "maxLength": 100},
        "horizon_years": {"type": "integer", "enum": [1, 2, 3]},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "baseline": {"$ref": "#/components/schemas/AIValueCaseSource"},
        "trial": {"$ref": "#/components/schemas/AIValueCaseSource"},
        "costs": {"$ref": "#/components/schemas/AIValueCaseCostInput"},
        "assumptions": {
            "type": "array",
            "minItems": 1,
            "maxItems": 20,
            "items": {"type": "string", "minLength": 1, "maxLength": 500},
        },
    }
    schemas["AIValueCaseRequest"] = closed(request, list(request))
    cost_output = {field: deepcopy(signed) for field in ("licences", "setup", "training", "staff_time")}
    schemas["AIValueCaseCosts"] = closed(cost_output, list(cost_output))
    result = {
        "status": {"const": "COMPLETE_SELF_REPORTED_DRAFT"},
        "opportunity_id": deepcopy(request["opportunity_id"]),
        "horizon_years": deepcopy(request["horizon_years"]),
        "currency": deepcopy(request["currency"]),
        "source": closed({"baseline": request["baseline"], "trial": request["trial"]}, ["baseline", "trial"]),
        "costs": {"$ref": "#/components/schemas/AIValueCaseCosts"},
        **{
            field: deepcopy(signed)
            for field in (
                "total_cost_of_ownership",
                "baseline_operating_cost",
                "trial_operating_cost",
                "gross_cost_benefit",
                "net_benefit",
                "roi_percent",
                "cost_benefit_ratio",
            )
        },
        "assumptions": deepcopy(request["assumptions"]),
        "disclaimer": {"type": "string", "minLength": 1, "maxLength": 500},
    }
    schemas["AIValueCase"] = closed(result, list(result))
    path = "/v1/tenants/{tenant_id}/" + ROOT
    spec["paths"][path] = {
        "parameters": [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ],
        "post": {
            "operationId": "calculate_ai_value_case",
            "summary": "Calculate a self-reported 1-3 year value case",
            "x-capability": "ai.enablement.read",
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIValueCaseRequest"}}
                },
            },
            "responses": {
                "200": {
                    "description": "Complete deterministic draft",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIValueCase"}}},
                }
            },
        },
    }
    policy["operations"].append(
        {
            "operation_id": "calculate_ai_value_case",
            "method": "POST",
            "path": path,
            "capability": "ai.enablement.read",
            "role_templates": ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER", "FINANCE"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
