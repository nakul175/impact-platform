"""Closed contracts for immutable locked value-case baseline revisions."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.47.0"
ROOT = "ai-enablement/value-cases"
ROUTES = [
    ("post", "", "create_ai_value_case_version", "AIValueCaseVersionCreate", "AIValueCaseVersionReceipt"),
    ("get", "/{object_id}", "get_ai_value_case_version", None, "AIValueCaseVersion"),
    ("get", "/{object_id}/revisions/{revision_id}", "get_ai_value_case_revision", None, "AIValueCaseVersion"),
    (
        "post",
        "/{object_id}/actions/approve",
        "approve_ai_value_case",
        "AIValueCaseVersionLock",
        "AIValueCaseVersionReceipt",
    ),
    (
        "post",
        "/{object_id}/actions/lock",
        "lock_ai_value_case_baseline",
        "AIValueCaseVersionLock",
        "AIValueCaseVersionReceipt",
    ),
    (
        "post",
        "/{object_id}/actions/revise",
        "revise_ai_value_case",
        "AIValueCaseVersionRevise",
        "AIValueCaseVersionReceipt",
    ),
]
IMPLEMENTED = [(method, ROOT + suffix) for method, suffix, *_ in ROUTES]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    create = {
        "operation_id": deepcopy(uid),
        "value_case": {"$ref": "#/components/schemas/AIValueCaseRequest"},
    }
    schemas["AIValueCaseVersionCreate"] = closed(create, list(create))
    lock = {"operation_id": deepcopy(uid), "expected_revision": deepcopy(uid)}
    schemas["AIValueCaseVersionLock"] = closed(lock, list(lock))
    revise = {**deepcopy(lock), "value_case": {"$ref": "#/components/schemas/AIValueCaseRequest"}}
    schemas["AIValueCaseVersionRevise"] = closed(revise, list(revise))
    result = {
        "object_id": deepcopy(uid),
        "revision_id": deepcopy(uid),
        "business_state": {"enum": ["Draft", "Approved", "Locked"]},
        "baseline_revision": {"oneOf": [deepcopy(uid), {"type": "null"}]},
        "approved_at": {"type": ["string", "null"], "format": "date-time"},
        "approved_by": {"oneOf": [deepcopy(uid), {"type": "null"}]},
        "trial_result_reference": {
            "oneOf": [
                closed(
                    {
                        "trial_id": deepcopy(uid),
                        "result_id": deepcopy(uid),
                        "opportunity_id": {"type": "string", "minLength": 1, "maxLength": 120},
                        "evidence_reference": {
                            "oneOf": [
                                closed(
                                    {"object_id": deepcopy(uid), "revision_id": deepcopy(uid)},
                                    ["object_id", "revision_id"],
                                ),
                                {"type": "null"},
                            ]
                        },
                    },
                    ["trial_id", "result_id", "opportunity_id", "evidence_reference"],
                ),
                {"type": "null"},
            ]
        },
        "value_case": {"$ref": "#/components/schemas/AIValueCase"},
    }
    schemas["AIValueCaseVersion"] = closed(result, list(result))
    receipt = {key: deepcopy(value) for key, value in result.items() if key != "value_case"}
    receipt.update(
        operation_id=deepcopy(uid),
        correlation_id=deepcopy(uid),
        saved_at={"type": "string", "format": "date-time"},
    )
    schemas["AIValueCaseVersionReceipt"] = closed(receipt, list(receipt))
    for method, suffix, operation, request, response in ROUTES:
        path = "/v1/tenants/{tenant_id}/" + ROOT + suffix
        params = [{"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}]
        for name in ("object_id", "revision_id"):
            if "{" + name + "}" in suffix:
                params.append({"name": name, "in": "path", "required": True, "schema": deepcopy(uid)})
        manage = request is not None
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": "ai.value-case.manage" if manage else "ai.value-case.read",
            "x-contract-version": VERSION,
            "x-audit-required": manage,
            "parameters": params,
            "responses": {
                "201" if operation == "create_ai_value_case_version" else "200": {
                    "description": "Versioned self-reported value case; locked revision remains immutable",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        for code in ("400", "401", "403", "404", "409", "422", "429", "503"):
            entry["responses"][code] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": "ai.value-case.manage" if manage else "ai.value-case.read",
                "role_templates": ["TENANT_ADMIN"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300
                if operation in ("approve_ai_value_case", "lock_ai_value_case_baseline")
                else None,
                "audit": manage,
            }
        )
