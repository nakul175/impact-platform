"""US-AS-01 advisor-led bounded option trial contracts."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.70.0"
UUID = {"type": "string", "format": "uuid"}
ROUTE = "ai-enablement/trials"
IMPLEMENTED = [
    ("get", ROUTE),
    ("post", ROUTE),
    ("post", ROUTE + "/{trial_id}/results"),
    ("post", "ai-enablement/value-cases/from-trial"),
]


def augment(spec, policy):
    s = spec["components"]["schemas"]
    reference = closed(
        {"object_id": deepcopy(UUID), "revision_id": deepcopy(UUID)}, ["object_id", "revision_id"]
    )
    common = {
        "operation_id": deepcopy(UUID),
        "opportunity_id": {"type": "string", "minLength": 1, "maxLength": 120},
        "solution_id": {"type": "string", "minLength": 1, "maxLength": 120},
        "starts_on": {"type": "string", "format": "date"},
        "duration_days": {"type": "integer", "minimum": 1, "maximum": 28},
        "success_criteria": {"type": "string", "minLength": 1, "maxLength": 2000, "pattern": "\\S"},
    }
    own = closed(
        {**deepcopy(common), "data_mode": {"const": "OWN_EVIDENCE"}, "evidence_reference": reference},
        [*common, "data_mode", "evidence_reference"],
    )
    sample = closed(
        {
            **deepcopy(common),
            "data_mode": {"const": "SAMPLE"},
            "sample_id": {"const": "SYNTHETIC_TABULAR_V1"},
        },
        [*common, "data_mode", "sample_id"],
    )
    s["AITrialCreate"] = {"oneOf": [own, sample]}
    result = closed(
        {
            "trial_id": deepcopy(UUID),
            "opportunity_id": common["opportunity_id"],
            "solution_id": common["solution_id"],
            "catalogue_content_version": {"type": "string", "minLength": 1, "maxLength": 100},
            "starts_on": common["starts_on"],
            "ends_on": common["starts_on"],
            "duration_days": common["duration_days"],
            "data_mode": {"enum": ["OWN_EVIDENCE", "SAMPLE"]},
            "evidence_reference": {"oneOf": [reference, {"type": "null"}]},
            "sample_id": {"type": ["string", "null"], "enum": ["SYNTHETIC_TABULAR_V1", None]},
            "success_criteria": common["success_criteria"],
            "advisor_membership_id": deepcopy(UUID),
            "status": {"enum": ["PLANNED", "ACTIVE", "ENDED"]},
            "created_at": {"type": "string", "format": "date-time"},
        },
        [
            "trial_id",
            "opportunity_id",
            "solution_id",
            "catalogue_content_version",
            "starts_on",
            "ends_on",
            "duration_days",
            "data_mode",
            "evidence_reference",
            "sample_id",
            "success_criteria",
            "advisor_membership_id",
            "status",
            "created_at",
        ],
    )
    s["AITrial"] = result
    s["AITrialList"] = closed(
        {"items": {"type": "array", "maxItems": 100, "items": {"$ref": "#/components/schemas/AITrial"}}},
        ["items"],
    )
    source = {"$ref": "#/components/schemas/AIValueCaseSource"}
    result_create = {
        "operation_id": deepcopy(UUID),
        "trial_source": source,
        "evidence_reference": {"oneOf": [reference, {"type": "null"}]},
    }
    s["AITrialResultCreate"] = closed(result_create, list(result_create))
    result = {
        "result_id": deepcopy(UUID),
        "trial_id": deepcopy(UUID),
        "opportunity_id": common["opportunity_id"],
        "trial_source": source,
        "evidence_reference": result_create["evidence_reference"],
        "recorded_at": {"type": "string", "format": "date-time"},
    }
    s["AITrialResult"] = closed(result, list(result))
    from_trial = {
        "operation_id": deepcopy(UUID),
        "trial_id": deepcopy(UUID),
        "horizon_years": {"type": "integer", "enum": [1, 2, 3]},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "baseline": source,
        "costs": {"$ref": "#/components/schemas/AIValueCaseCostInput"},
        "assumptions": {
            "type": "array",
            "minItems": 1,
            "maxItems": 20,
            "items": {"type": "string", "minLength": 1, "maxLength": 500},
        },
    }
    s["AIValueCaseFromTrialCreate"] = closed(from_trial, list(from_trial))
    path = "/v1/tenants/{tenant_id}/" + ROUTE
    params = [{"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(UUID)}]
    spec["paths"][path] = {
        "get": _operation(
            "list_ai_option_trials",
            "List advisor-led option trials",
            "ai.enablement.read",
            None,
            "AITrialList",
            params
            + [
                {
                    "name": "opportunity_id",
                    "in": "query",
                    "required": True,
                    "schema": common["opportunity_id"],
                }
            ],
        ),
        "post": _operation(
            "create_ai_option_trial",
            "Create a maximum-28-day advisor-led trial",
            "ai.solution-fit.score",
            "AITrialCreate",
            "AITrial",
            params,
        ),
    }
    trial_result_path = path + "/{trial_id}/results"
    spec["paths"][trial_result_path] = {
        "post": _operation(
            "record_ai_trial_result",
            "Record immutable completed-trial results",
            "ai.solution-fit.score",
            "AITrialResultCreate",
            "AITrialResult",
            params + [{"name": "trial_id", "in": "path", "required": True, "schema": deepcopy(UUID)}],
        )
    }
    from_trial_path = "/v1/tenants/{tenant_id}/ai-enablement/value-cases/from-trial"
    spec["paths"][from_trial_path] = {
        "post": _operation(
            "create_ai_value_case_from_trial",
            "Build a value case from the matching recorded trial",
            "ai.value-case.manage",
            "AIValueCaseFromTrialCreate",
            "AIValueCaseVersionReceipt",
            params,
        )
    }
    policy["operations"].extend(
        [
            {
                "operation_id": "list_ai_option_trials",
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
                "operation_id": "create_ai_option_trial",
                "method": "POST",
                "path": path,
                "capability": "ai.solution-fit.score",
                "role_templates": ["REVIEWER"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300,
                "audit": True,
                "state_guard": "Current natural-person advisor; option is catalogue-mapped; own data is one currently authorised exact Evidence revision or the fixed synthetic sample; duration is1-28days and immutable.",
            },
        ]
    )
    policy["operations"].extend(
        [
            {
                "operation_id": "record_ai_trial_result",
                "method": "POST",
                "path": trial_result_path,
                "capability": "ai.solution-fit.score",
                "role_templates": ["REVIEWER"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300,
                "audit": True,
            },
            {
                "operation_id": "create_ai_value_case_from_trial",
                "method": "POST",
                "path": from_trial_path,
                "capability": "ai.value-case.manage",
                "role_templates": ["TENANT_ADMIN"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": True,
            },
        ]
    )


def _operation(operation_id, summary, capability, request, response, parameters):
    node = {
        "operationId": operation_id,
        "summary": summary,
        "x-capability": capability,
        "x-contract-version": VERSION,
        "parameters": parameters,
        "responses": {
            "201" if request else "200": {
                "description": "Success",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
            }
        },
    }
    if request:
        node["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
        }
    return node
