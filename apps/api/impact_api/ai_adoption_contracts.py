"""Closed adoption-plan draft contracts; read and management permissions stay separate."""

from copy import deepcopy

from .ai_enablement_contracts import ROLES
from .measurement_contracts import closed

VERSION = "1.21.0"
IMPLEMENTED = [
    ("get", "ai-enablement/plans"),
    ("post", "ai-enablement/plans"),
    ("get", "ai-enablement/plans/{object_id}"),
    ("put", "ai-enablement/plans/{object_id}"),
]
MANAGERS = ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    unique_ids = {"type": "array", "uniqueItems": True, "items": {"type": "string", "maxLength": 100}}
    schemas["AIAdoptionPlanProcurement"] = closed(
        {
            "requirements": {"type": "string", "maxLength": 2000},
            "data_boundary": {"type": "string", "maxLength": 2000},
            "budget_notes": {"type": "string", "maxLength": 500},
            "vendor_questions": {"type": "string", "maxLength": 2000},
        },
        ["requirements", "data_boundary", "budget_notes", "vendor_questions"],
    )
    schemas["AIAdoptionPlanPilot"] = closed(
        {
            "success_measure": {"type": "string", "maxLength": 1000},
            "completed_actions": {
                "type": "array",
                "uniqueItems": True,
                "maxItems": 5,
                "items": {
                    "enum": [
                        "DEFINE_GOAL",
                        "SYNTHETIC_TRIAL",
                        "HUMAN_REVIEW",
                        "TRAIN_STAFF",
                        "REVIEW_OUTCOME",
                    ]
                },
            },
        },
        ["success_measure", "completed_actions"],
    )
    data = {
        "title": {"type": "string", "minLength": 1, "maxLength": 150},
        "profile": {"$ref": "#/components/schemas/AIEnablementProfile"},
        "solution_ids": {**deepcopy(unique_ids), "maxItems": 4},
        "learning_completed": {**deepcopy(unique_ids), "maxItems": 100},
        "procurement": {"$ref": "#/components/schemas/AIAdoptionPlanProcurement"},
        "pilot": {"$ref": "#/components/schemas/AIAdoptionPlanPilot"},
    }
    schemas["AIAdoptionPlanData"] = closed(data, list(data))
    command = {
        "operation_id": {"type": "string", "format": "uuid"},
        "data": {"$ref": "#/components/schemas/AIAdoptionPlanData"},
    }
    schemas["AIAdoptionPlanCreate"] = closed(command, list(command))
    update = {**command, "expected_revision": {"type": "string", "format": "uuid"}}
    schemas["AIAdoptionPlanUpdate"] = closed(update, list(update))
    persisted = {
        **deepcopy(data),
        "content_versions": closed(
            {"catalog": {"type": "string"}, "solutions": {"type": "string"}}, ["catalog", "solutions"]
        ),
    }
    schemas["AIAdoptionPlanStoredData"] = closed(persisted, list(persisted))
    result = {
        "object_id": {"type": "string", "format": "uuid"},
        "revision_id": {"type": "string", "format": "uuid"},
        "business_state": {"const": "Draft"},
        "data": {"$ref": "#/components/schemas/AIAdoptionPlanStoredData"},
    }
    schemas["AIAdoptionPlan"] = closed(result, list(result))
    schemas["AIAdoptionPlanList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIAdoptionPlan"},
            },
            "next_cursor": {"type": ["string", "null"]},
        },
        ["items", "next_cursor"],
    )
    receipt = {
        "object_id": {"type": "string", "format": "uuid"},
        "revision_id": {"type": "string", "format": "uuid"},
        "business_state": {"const": "Draft"},
        "saved_at": {"type": "string", "format": "date-time"},
        "operation_id": {"type": "string", "format": "uuid"},
        "correlation_id": {"type": "string", "format": "uuid"},
    }
    schemas["AIAdoptionPlanReceipt"] = closed(receipt, list(receipt))
    for method, suffix, operation, request, response, write_access in [
        ("get", "", "list_ai_adoption_plans", None, "AIAdoptionPlanList", False),
        ("post", "", "create_ai_adoption_plan", "AIAdoptionPlanCreate", "AIAdoptionPlanReceipt", True),
        ("get", "/{object_id}", "get_ai_adoption_plan", None, "AIAdoptionPlan", False),
        (
            "put",
            "/{object_id}",
            "update_ai_adoption_plan",
            "AIAdoptionPlanUpdate",
            "AIAdoptionPlanReceipt",
            True,
        ),
    ]:
        path = "/v1/tenants/{tenant_id}/ai-enablement/plans" + suffix
        parameters = [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
        if suffix:
            parameters.append(
                {
                    "name": "object_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            )
        if operation == "list_ai_adoption_plans":
            parameters += [
                {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100}},
                {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
            ]
        status = "201" if operation == "create_ai_adoption_plan" else "200"
        capability = "ai.enablement.manage" if write_access else "ai.enablement.read"
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "parameters": parameters,
            "responses": {
                status: {
                    "description": "Unapproved adoption draft or durable save receipt",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for refusal in ["400", "401", "403", "404", "409", "422", "429", "503"]:
            entry["responses"][refusal] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": capability,
                "role_templates": deepcopy(MANAGERS if write_access else ROLES),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": write_access,
            }
        )
