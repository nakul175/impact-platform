"""Closed adoption-plan draft contracts; read and management permissions stay separate."""

from copy import deepcopy

from .ai_enablement_contracts import ROLES
from .measurement_contracts import closed

VERSION = "1.72.0"
IMPLEMENTED = [
    ("get", "ai-enablement/plans"),
    ("post", "ai-enablement/plans"),
    ("get", "ai-enablement/plans/{object_id}"),
    ("put", "ai-enablement/plans/{object_id}"),
    ("post", "ai-enablement/plans/{object_id}/deployment/actions/generate"),
    ("put", "ai-enablement/plans/{object_id}/deployment/milestones/{milestone_code}"),
    ("post", "ai-enablement/plans/{object_id}/deployment/actions/complete"),
    ("post", "ai-enablement/plans/{object_id}/deployment/actions/attest"),
    ("get", "ai-enablement/plans/{object_id}/role-training"),
    ("post", "ai-enablement/plans/{object_id}/role-training/modules/{module_key}/actions/complete"),
    ("get", "ai-enablement/plans/{object_id}/champion-appointments"),
    ("post", "ai-enablement/plans/{object_id}/champion-appointments"),
    ("get", "ai-enablement/plans/{object_id}/champion-guide"),
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
            "workflow_touchpoints": {
                "type": "array",
                "minItems": 1,
                "maxItems": 20,
                "items": {"$ref": "#/components/schemas/AIWorkflowTouchpoint"},
            },
        },
        ["template_version", "state", "milestones", "workflow_touchpoints"],
    )
    schemas["AITrainingDeploymentAttestation"] = closed(
        {
            "attestation_id": {"type": "string", "format": "uuid"},
            "solution_id": {"type": "string", "minLength": 1, "maxLength": 100},
            "deployed_at": {"type": "string", "format": "date-time"},
            "deployment_reference": {"type": "string", "minLength": 1, "maxLength": 500},
            "attested_by": {"type": "string", "format": "uuid"},
            "attested_at": {"type": "string", "format": "date-time"},
            "agreement_revision_id": {"type": "string", "format": "uuid"},
        },
        [
            "attestation_id",
            "solution_id",
            "deployed_at",
            "deployment_reference",
            "attested_by",
            "attested_at",
        ],
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
        "training_deployment": {"$ref": "#/components/schemas/AITrainingDeploymentAttestation"},
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
    schemas["AIWorkflowTouchpoint"] = closed(
        {
            "touchpoint_id": {"type": "string", "pattern": "^[a-z][a-z0-9_-]{0,63}$"},
            "workflow_name": {"type": "string", "minLength": 1, "maxLength": 200},
            "source_system": {"type": "string", "minLength": 1, "maxLength": 200},
            "source_record_key": {"type": "string", "minLength": 1, "maxLength": 200},
            "solution_use": {"type": "string", "minLength": 1, "maxLength": 500},
            "capture_mode": {"const": "READ_EXISTING"},
            "duplicate_entry_required": {"const": False},
        },
        [
            "touchpoint_id",
            "workflow_name",
            "source_system",
            "source_record_key",
            "solution_use",
            "capture_mode",
            "duplicate_entry_required",
        ],
    )
    schemas["AIDeploymentGenerate"] = closed(
        {
            **base_command,
            "owners": closed(
                {code: {"type": "string", "format": "uuid"} for code in ["PREPARE", "PILOT", "ROLLOUT"]},
                ["PREPARE", "PILOT", "ROLLOUT"],
            ),
            "workflow_touchpoints": {
                "type": "array",
                "minItems": 1,
                "maxItems": 20,
                "items": {"$ref": "#/components/schemas/AIWorkflowTouchpoint"},
            },
        },
        [*base_command, "owners", "workflow_touchpoints"],
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

    schemas["AITrainingDeploymentAttest"] = closed(
        {
            **base_command,
            "solution_id": {"type": "string", "minLength": 1, "maxLength": 100},
            "deployed_at": {"type": "string", "format": "date-time"},
            "deployment_reference": {"type": "string", "minLength": 1, "maxLength": 500},
        },
        [*base_command, "solution_id", "deployed_at", "deployment_reference"],
    )
    module = closed(
        {
            "key": {"type": "string", "minLength": 1, "maxLength": 100},
            "version": {"const": "role-training-2026-10-12.1"},
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "lesson": {"type": "string", "minLength": 1, "maxLength": 4000},
            "exercise": {"type": "string", "minLength": 1, "maxLength": 2000},
            "completed": {"type": "boolean"},
            "completed_at": {"type": ["string", "null"], "format": "date-time"},
        },
        ["key", "version", "title", "lesson", "exercise", "completed", "completed_at"],
    )
    schemas["AIRoleTraining"] = closed(
        {
            "plan_id": {"type": "string", "format": "uuid"},
            "plan_revision": {"type": "string", "format": "uuid"},
            "solution_id": {"type": "string", "minLength": 1, "maxLength": 100},
            "deployment_attestation_id": {"type": "string", "format": "uuid"},
            "role": {"const": "AUTHOR"},
            "content_version": {"const": "role-training-2026-10-12.1"},
            "modules": {"type": "array", "minItems": 1, "maxItems": 20, "items": module},
        },
        [
            "plan_id",
            "plan_revision",
            "solution_id",
            "deployment_attestation_id",
            "role",
            "content_version",
            "modules",
        ],
    )
    schemas["AIRoleTrainingComplete"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "expected_plan_revision": {"type": "string", "format": "uuid"},
            "solution_id": {"type": "string", "minLength": 1, "maxLength": 100},
            "module_version": {"const": "role-training-2026-10-12.1"},
        },
        ["operation_id", "expected_plan_revision", "solution_id", "module_version"],
    )
    errors = {
        code: {
            "description": "Request refused",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        }
        for code in ["400", "401", "403", "404", "409", "422", "503"]
    }
    attest_path = "/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}/deployment/actions/attest"
    training_path = "/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}/role-training"
    complete_path = training_path + "/modules/{module_key}/actions/complete"
    common = [
        {"name": "tenant_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}},
        {"name": "object_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}},
    ]
    spec["paths"][attest_path] = {
        "post": {
            "operationId": "attest_ai_solution_deployment",
            "summary": "attest actual solution deployment",
            "x-capability": "ai.enablement.manage",
            "x-contract-version": VERSION,
            "parameters": common,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AITrainingDeploymentAttest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Deployment attestation revision receipt",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIAdoptionPlanReceipt"}}
                    },
                },
                **errors,
            },
        }
    }
    spec["paths"][training_path] = {
        "get": {
            "operationId": "get_ai_role_training",
            "summary": "get learner role training",
            "x-capability": "ai.enablement.read",
            "x-contract-version": VERSION,
            "parameters": common
            + [
                {
                    "name": "solution_id",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1, "maxLength": 100},
                }
            ],
            "responses": {
                "200": {
                    "description": "Current learner role modules and completion",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIRoleTraining"}}
                    },
                },
                **errors,
            },
        }
    }
    spec["paths"][complete_path] = {
        "post": {
            "operationId": "complete_ai_role_training_module",
            "summary": "record learner module completion",
            "x-capability": "ai.enablement.read",
            "x-contract-version": VERSION,
            "parameters": common
            + [
                {
                    "name": "module_key",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1, "maxLength": 100},
                }
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIRoleTrainingComplete"}}
                },
            },
            "responses": {
                "200": {
                    "description": "Learner-scoped role training state",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIRoleTraining"}}
                    },
                },
                **errors,
            },
        }
    }
    for operation_id, method, path, capability, roles, audit_enabled in [
        ("attest_ai_solution_deployment", "POST", attest_path, "ai.enablement.manage", MANAGERS, True),
        ("get_ai_role_training", "GET", training_path, "ai.enablement.read", ["AUTHOR"], False),
        ("complete_ai_role_training_module", "POST", complete_path, "ai.enablement.read", ["AUTHOR"], True),
    ]:
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": method,
                "path": path,
                "capability": capability,
                "role_templates": deepcopy(roles),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": audit_enabled,
                "state_guard": "Current active Data Author role and explicit deployed-solution attestation; completion belongs only to the authenticated learner.",
            }
        )

    check_in = closed(
        {
            "check_in_id": {"type": "string", "format": "uuid"},
            "scheduled_at": {"type": "string", "format": "date-time"},
            "title": {"type": "string", "minLength": 1, "maxLength": 150},
        },
        ["check_in_id", "scheduled_at", "title"],
    )
    appointment = closed(
        {
            "plan_id": {"type": "string", "format": "uuid"},
            "plan_revision": {"type": "string", "format": "uuid"},
            "deployment_attestation_id": {"type": "string", "format": "uuid"},
            "solution_id": {"type": "string", "minLength": 1, "maxLength": 100},
            "role": {"const": "CHAMPION"},
            "guide_id": {"const": "internal-champion-guide"},
            "guide_version": {"const": "internal-champion-guide-2026-10-12.1"},
            "guide_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "champion_principal_id": {"type": "string", "format": "uuid"},
            "champion_membership_id": {"type": "string", "format": "uuid"},
            "support_owner_principal_id": {"type": "string", "format": "uuid"},
            "support_owner_membership_id": {"type": "string", "format": "uuid"},
            "check_ins": {"type": "array", "minItems": 1, "maxItems": 12, "items": check_in},
            "appointed_by": {"type": "string", "format": "uuid"},
            "appointed_at": {"type": "string", "format": "date-time"},
            "confirmed_at": {"type": "string", "format": "date-time"},
        },
        [
            "plan_id",
            "plan_revision",
            "deployment_attestation_id",
            "solution_id",
            "role",
            "guide_id",
            "guide_version",
            "guide_hash",
            "champion_principal_id",
            "champion_membership_id",
            "support_owner_principal_id",
            "support_owner_membership_id",
            "check_ins",
            "appointed_by",
            "appointed_at",
            "confirmed_at",
        ],
    )
    schemas["AIChampionAppointment"] = closed(
        {
            "object_id": {"type": "string", "format": "uuid"},
            "revision_id": {"type": "string", "format": "uuid"},
            "business_state": {"const": "Completed"},
            "appointment": appointment,
        },
        ["object_id", "revision_id", "business_state", "appointment"],
    )
    schemas["AIChampionAppointmentCreate"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "expected_plan_revision": {"type": "string", "format": "uuid"},
            "champion_membership_id": {"type": "string", "format": "uuid"},
            "support_owner_membership_id": {"type": "string", "format": "uuid"},
            "check_ins": {
                "type": "array",
                "minItems": 1,
                "maxItems": 12,
                "items": closed(
                    {
                        "scheduled_at": {"type": "string", "format": "date-time"},
                        "title": {"type": "string", "minLength": 1, "maxLength": 150},
                    },
                    ["scheduled_at", "title"],
                ),
            },
        },
        [
            "operation_id",
            "expected_plan_revision",
            "champion_membership_id",
            "support_owner_membership_id",
            "check_ins",
        ],
    )
    schemas["AIChampionAppointmentList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIChampionAppointment"},
            }
        },
        ["items"],
    )
    guide_section = closed(
        {
            "key": {"type": "string", "minLength": 1, "maxLength": 100},
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "body": {"type": "string", "minLength": 1, "maxLength": 2000},
        },
        ["key", "title", "body"],
    )
    schemas["AIChampionGuide"] = closed(
        {
            "guide_id": {"const": "internal-champion-guide"},
            "version": {"const": "internal-champion-guide-2026-10-12.1"},
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "sections": {"type": "array", "minItems": 1, "maxItems": 12, "items": guide_section},
            "plan_id": {"type": "string", "format": "uuid"},
            "plan_revision": {"type": "string", "format": "uuid"},
            "solution_id": {"type": "string", "minLength": 1, "maxLength": 100},
            "deployment_attestation_id": {"type": "string", "format": "uuid"},
            "role": {"const": "CHAMPION"},
        },
        [
            "guide_id",
            "version",
            "title",
            "sections",
            "plan_id",
            "plan_revision",
            "solution_id",
            "deployment_attestation_id",
            "role",
        ],
    )
    appointments_path = "/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}/champion-appointments"
    guide_path = "/v1/tenants/{tenant_id}/ai-enablement/plans/{object_id}/champion-guide"
    spec["paths"][appointments_path] = {
        "get": {
            "operationId": "list_ai_champion_appointments",
            "summary": "list visible internal champion appointments",
            "x-capability": "ai.enablement.read",
            "x-contract-version": VERSION,
            "parameters": common,
            "responses": {
                "200": {
                    "description": "Visible current-deployment appointments",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AIChampionAppointmentList"}
                        }
                    },
                },
                **errors,
            },
        },
        "post": {
            "operationId": "appoint_ai_internal_champion",
            "summary": "appoint an internal champion with support",
            "x-capability": "ai.enablement.manage",
            "x-contract-version": VERSION,
            "parameters": common,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AIChampionAppointmentCreate"}
                    }
                },
            },
            "responses": {
                "201": {
                    "description": "Confirmed internal champion appointment",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIChampionAppointment"}}
                    },
                },
                **errors,
            },
        },
    }
    spec["paths"][guide_path] = {
        "get": {
            "operationId": "get_ai_champion_guide",
            "summary": "open the appointed champion guide",
            "x-capability": "ai.enablement.read",
            "x-contract-version": VERSION,
            "parameters": common
            + [
                {
                    "name": "solution_id",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1, "maxLength": 100},
                }
            ],
            "responses": {
                "200": {
                    "description": "Pinned internal champion guide",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIChampionGuide"}}
                    },
                },
                **errors,
            },
        }
    }
    for operation_id, method, path, capability, roles, audit_enabled in [
        ("list_ai_champion_appointments", "GET", appointments_path, "ai.enablement.read", ROLES, False),
        ("appoint_ai_internal_champion", "POST", appointments_path, "ai.enablement.manage", ["OWNER"], True),
        ("get_ai_champion_guide", "GET", guide_path, "ai.enablement.read", ROLES, False),
    ]:
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": method,
                "path": path,
                "capability": capability,
                "role_templates": deepcopy(roles),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": audit_enabled,
                "state_guard": "Exact current deployed-solution attestation; active participant memberships and scoped authority. CHAMPION is a solution appointment, not an IAM grant.",
            }
        )
