"""Closed contracts for self-reported observations against locked baselines."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.53.0"
IMPLEMENTED = [
    ("post", "ai-enablement/outcome-observations"),
    ("get", "ai-enablement/outcomes-dashboard"),
]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    decimal = {"type": "string", "pattern": r"^-?(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?$"}
    measure = closed(
        {
            "value": decimal,
            "unit": {"type": "string", "minLength": 1, "maxLength": 80},
            "basis": {"type": "string", "minLength": 1, "maxLength": 500},
            "observed_from": {"type": "string", "format": "date"},
            "observed_to": {"type": "string", "format": "date"},
        },
        ["value", "unit", "basis", "observed_from", "observed_to"],
    )
    schemas["AICurrentOutcomeMeasure"] = measure
    metrics = {
        name: {"$ref": "#/components/schemas/AICurrentOutcomeMeasure"}
        for name in ("time", "cost", "quality", "reach", "usage")
    }
    schemas["AICurrentOutcomeMetrics"] = closed(metrics, list(metrics))
    create = {
        "operation_id": deepcopy(uid),
        "plan_id": deepcopy(uid),
        "plan_revision": deepcopy(uid),
        "deployment_attestation_id": deepcopy(uid),
        "baseline_object_id": deepcopy(uid),
        "baseline_revision": deepcopy(uid),
        "opportunity_id": {"type": "string", "minLength": 1, "maxLength": 100},
        "metrics": {"$ref": "#/components/schemas/AICurrentOutcomeMetrics"},
        "notes": {"type": "string", "maxLength": 4000},
    }
    schemas["AICurrentOutcomeObservationCreate"] = closed(create, list(create))
    receipt = {
        "object_id": deepcopy(uid),
        "revision_id": deepcopy(uid),
        "business_state": {"const": "Recorded"},
        "saved_at": {"type": "string", "format": "date-time"},
        "operation_id": deepcopy(uid),
        "correlation_id": deepcopy(uid),
        "selectors": closed(
            {
                name: deepcopy(create[name])
                for name in (
                    "plan_id",
                    "plan_revision",
                    "deployment_attestation_id",
                    "baseline_object_id",
                    "baseline_revision",
                    "opportunity_id",
                )
            },
            [
                "plan_id",
                "plan_revision",
                "deployment_attestation_id",
                "baseline_object_id",
                "baseline_revision",
                "opportunity_id",
            ],
        ),
    }
    schemas["AICurrentOutcomeObservationReceipt"] = closed(receipt, list(receipt))
    comparison = {
        "metric": {"enum": ["time", "cost", "quality", "reach", "usage"]},
        "baseline": {"oneOf": [{"$ref": "#/components/schemas/AICurrentOutcomeMeasure"}, {"type": "null"}]},
        "current": {"oneOf": [{"$ref": "#/components/schemas/AICurrentOutcomeMeasure"}, {"type": "null"}]},
        "status": {"enum": ["COMPARABLE", "INCOMPATIBLE", "NOT_RECORDED", "BASELINE_NOT_RECORDED"]},
        "delta": {"type": ["string", "null"]},
    }
    schemas["AIOutcomeComparison"] = closed(comparison, list(comparison))
    dashboard = {
        "plan_id": deepcopy(uid),
        "plan_revision": deepcopy(uid),
        "deployment_attestation_id": deepcopy(uid),
        "deployed_solution_id": {"type": "string"},
        "baseline_object_id": deepcopy(uid),
        "baseline_revision": deepcopy(uid),
        "opportunity_id": {"type": "string"},
        "pattern_edition": {"type": "string"},
        "observation_id": {"type": ["string", "null"], "format": "uuid"},
        "observation_revision": {"type": ["string", "null"], "format": "uuid"},
        "reporting_basis": {"const": "SELF_REPORTED"},
        "comparisons": {
            "type": "array",
            "minItems": 5,
            "maxItems": 5,
            "items": {"$ref": "#/components/schemas/AIOutcomeComparison"},
        },
        "disclaimer": {"type": "string"},
    }
    schemas["AIOutcomesDashboard"] = closed(dashboard, list(dashboard))
    root = "/v1/tenants/{tenant_id}/ai-enablement"
    tenant_param = {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}
    spec["paths"][root + "/outcome-observations"] = {
        "parameters": [tenant_param],
        "post": {
            "operationId": "create_ai_outcome_observation",
            "summary": "Record self-reported current outcomes",
            "x-capability": "ai.enablement.manage",
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AICurrentOutcomeObservationCreate"}
                    }
                },
            },
            "responses": {
                "201": {
                    "description": "Immutable observation receipt",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AICurrentOutcomeObservationReceipt"}
                        }
                    },
                }
            },
        },
    }
    spec["paths"][root + "/outcomes-dashboard"] = {
        "parameters": [
            tenant_param,
            {"name": "plan_id", "in": "query", "required": True, "schema": deepcopy(uid)},
            {"name": "baseline_object_id", "in": "query", "required": True, "schema": deepcopy(uid)},
            {
                "name": "opportunity_id",
                "in": "query",
                "required": True,
                "schema": {"type": "string", "maxLength": 100},
            },
        ],
        "get": {
            "operationId": "get_ai_outcome_dashboard",
            "summary": "Compare current outcomes with the exact locked baseline",
            "x-capability": "ai.outcomes.read",
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "Self-reported locked-baseline comparison",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIOutcomesDashboard"}}
                    },
                }
            },
        },
    }
    for operation, method, suffix, capability, audit_flag in [
        ("create_ai_outcome_observation", "POST", "/outcome-observations", "ai.enablement.manage", True),
        ("get_ai_outcome_dashboard", "GET", "/outcomes-dashboard", "ai.outcomes.read", False),
    ]:
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method,
                "path": root + suffix,
                "capability": capability,
                "role_templates": ["TENANT_ADMIN"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": audit_flag,
            }
        )
