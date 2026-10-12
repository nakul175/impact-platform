"""Closed adoption-plan draft contracts; read and management permissions stay separate."""

from copy import deepcopy

from .ai_enablement_contracts import ROLES
from .measurement_contracts import closed

VERSION = "1.50.0"
IMPLEMENTED = [
    ("get", "ai-enablement/plans"),
    ("post", "ai-enablement/plans"),
    ("get", "ai-enablement/plans/{object_id}"),
    ("put", "ai-enablement/plans/{object_id}"),
    ("post", "ai-enablement/plans/{object_id}/deployment/actions/generate"),
    ("put", "ai-enablement/plans/{object_id}/deployment/milestones/{milestone_code}"),
    ("post", "ai-enablement/plans/{object_id}/deployment/actions/complete"),
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
    progress = {"enum": ["NOT_STARTED", "IN_PROGRESS", "BLOCKED", "ACCEPTED"]}
    schemas["AIDeploymentMilestone"] = closed(
        {
            "code": {"enum": ["PREPARE", "PILOT", "ROLLOUT"]},
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "owner_principal_id": {"type": "string", "format": "uuid"},
            "acceptance_criteria": {"type": "string", "minLength": 1, "maxLength": 1000},
            "progress": progress,
            "progress_note": {"type": "string", "maxLength": 1000},
        },
        [
            "code",
            "title",
            "owner_principal_id",
            "acceptance_criteria",
            "progress",
            "progress_note",
        ],
    )
    schemas["AIDeploymentPlan"] = closed(
        {
            "template_version": {"const": "accountable-rollout-2026-10-12.1"},
            "state": {"enum": ["ACTIVE", "COMPLETE"]},
            "milestones": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {"$ref": "#/components/schemas/AIDeploymentMilestone"},
            },
        },
        ["template_version", "state", "milestones"],
    )
    data = {
        "title": {"type": "string", "minLength": 1, "maxLength": 150},
        "profile": {"$ref": "#/components/schemas/AIEnablementProfile"},
        "solution_ids": {**deepcopy(unique_ids), "maxItems": 4},
        "learning_completed": {**deepcopy(unique_ids), "maxItems": 100},
        "procurement": {"$ref": "#/components/schemas/AIAdoptionPlanProcurement"},
        "pilot": {"$ref": "#/components/schemas/AIAdoptionPlanPilot"},
    }
    required_data = list(data)
    planning = {
        "cost_comparison": {
            "oneOf": [{"$ref": "#/components/schemas/AICostComparisonRequest"}, {"type": "null"}]
        },
        "pilot_evaluation": {
            "oneOf": [{"$ref": "#/components/schemas/AIPilotEvaluationRequest"}, {"type": "null"}]
        },
        "task_practice": {"oneOf": [{"$ref": "#/components/schemas/AITaskPracticeData"}, {"type": "null"}]},
    }
    schemas["AIAdoptionPlanningInputs"] = closed(planning, list(planning))
    data["planning"] = {"$ref": "#/components/schemas/AIAdoptionPlanningInputs"}
    schemas["AIAdoptionPlanData"] = closed(data, required_data)
    command = {
        "operation_id": {"type": "string", "format": "uuid"},
        "data": {"$ref": "#/components/schemas/AIAdoptionPlanData"},
    }
    schemas["AIAdoptionPlanCreate"] = closed(command, list(command))
    update = {**command, "expected_revision": {"type": "string", "format": "uuid"}}
    schemas["AIAdoptionPlanUpdate"] = closed(update, list(update))
    persisted = {
        **deepcopy(data),
        "deployment": {"$ref": "#/components/schemas/AIDeploymentPlan"},
        "content_versions": closed(
            {"catalog": {"type": "string"}, "solutions": {"type": "string"}}, ["catalog", "solutions"]
        ),
    }
    persisted["content_versions"]["properties"]["practice"] = {"type": "string", "maxLength": 100}
    schemas["AIAdoptionPlanStoredData"] = closed(persisted, [*required_data, "content_versions"])
    result = {
        "object_id": {"type": "string", "format": "uuid"},
        "revision_id": {"type": "string", "format": "uuid"},
        "business_state": {"enum": ["Draft", "Completed"]},
        "data": {"$ref": "#/components/schemas/AIAdoptionPlanStoredData"},
    }
    schemas["AIAdoptionPlan"] = closed(result, list(result))
    version_status = {"enum": ["CURRENT", "STALE", "UNKNOWN"]}
    compatibility = {
        "current_versions": deepcopy(persisted["content_versions"]),
        "catalog_version_status": deepcopy(version_status),
        "solutions_version_status": deepcopy(version_status),
        "learning_completed": {**deepcopy(unique_ids), "maxItems": 100},
        "legacy_learning_keys": {**deepcopy(unique_ids), "maxItems": 100},
        "unavailable_learning_keys": {**deepcopy(unique_ids), "maxItems": 100},
        "historical_snapshots_available": {"const": False},
    }
    schemas["AIAdoptionPlanCompatibility"] = closed(compatibility, list(compatibility))
    result["content_compatibility"] = {"$ref": "#/components/schemas/AIAdoptionPlanCompatibility"}
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
        "business_state": {"enum": ["Draft", "Completed"]},
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

    base_command = {
        "operation_id": {"type": "string", "format": "uuid"},
        "expected_revision": {"type": "string", "format": "uuid"},
    }
    schemas["AIDeploymentGenerate"] = closed(
        {
            **base_command,
            "owners": closed(
                {code: {"type": "string", "format": "uuid"} for code in ["PREPARE", "PILOT", "ROLLOUT"]},
                ["PREPARE", "PILOT", "ROLLOUT"],
            ),
        },
        [*base_command, "owners"],
    )
    schemas["AIDeploymentProgress"] = closed(
        {
            **base_command,
            "progress": progress,
            "progress_note": {"type": "string", "maxLength": 1000},
        },
        [*base_command, "progress", "progress_note"],
    )
    schemas["AIDeploymentComplete"] = closed(base_command, list(base_command))
    for method, suffix, operation, request in [
        ("post", "/deployment/actions/generate", "generate_ai_deployment_plan", "AIDeploymentGenerate"),
        (
            "put",
            "/deployment/milestones/{milestone_code}",
            "update_ai_deployment_milestone",
            "AIDeploymentProgress",
        ),
        ("post", "/deployment/actions/complete", "complete_ai_deployment_plan", "AIDeploymentComplete"),
    ]:
        path = "/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}" + suffix
        parameters = [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            },
            {
                "name": "object_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            },
        ]
        if "{milestone_code}" in suffix:
            parameters.append(
                {
                    "name": "milestone_code",
                    "in": "path",
                    "required": True,
                    "schema": {"enum": ["PREPARE", "PILOT", "ROLLOUT"]},
                }
            )
        spec["paths"][path] = {
            method: {
                "operationId": operation,
                "summary": operation.replace("_", " "),
                "x-capability": "ai.enablement.manage",
                "x-contract-version": VERSION,
                "parameters": parameters,
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
                },
                "responses": {
                    "200": {
                        "description": "Durable deployment-plan revision receipt",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AIAdoptionPlanReceipt"}
                            }
                        },
                    },
                    **{
                        refusal: {
                            "description": "Request refused",
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                            },
                        }
                        for refusal in ["400", "401", "403", "404", "409", "422", "503"]
                    },
                },
            }
        }
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": "ai.enablement.manage",
                "role_templates": deepcopy(MANAGERS),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": True,
                "state_guard": "Current plan revision under tenant lock; milestone progress requires the named current owner.",
            }
        )
