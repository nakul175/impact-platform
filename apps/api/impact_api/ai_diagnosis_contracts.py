"""Closed manual diagnosis contracts with separate TENANT read/manage capabilities."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.30.0"
ROOT = "ai-enablement/diagnoses"
ROUTES = [
    ("get", "", "list_ai_diagnoses", None, "AIDiagnosisList"),
    ("post", "", "create_ai_diagnosis", "AIDiagnosisCreate", "AIDiagnosisReceipt"),
    ("get", "/{object_id}", "get_ai_diagnosis", None, "AIDiagnosis"),
    ("put", "/{object_id}", "update_ai_diagnosis", "AIDiagnosisUpdate", "AIDiagnosisReceipt"),
    (
        "post",
        "/{object_id}/actions/complete",
        "complete_ai_diagnosis",
        "AIDiagnosisComplete",
        "AIDiagnosisReceipt",
    ),
    ("post", "/{object_id}/actions/revise", "revise_ai_diagnosis", "AIDiagnosisRevise", "AIDiagnosisReceipt"),
    ("get", "/{object_id}/revisions", "list_ai_diagnosis_revisions", None, "AIDiagnosisHistory"),
    ("get", "/{object_id}/revisions/{revision_id}", "get_ai_diagnosis_revision", None, "AIDiagnosis"),
]
IMPLEMENTED = [(method, ROOT + suffix) for method, suffix, *_ in ROUTES]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    # Bound the two shared runtime refusals without changing published older Error readers.
    schemas["AIDiagnosisError"] = deepcopy(schemas["Error"])
    codes = schemas["AIDiagnosisError"]["properties"]["code"]["enum"]
    for code in ("INVALID_CURSOR", "IDEMPOTENCY_EXPIRED"):
        if code not in codes:
            codes.append(code)
    uid = {"type": "string", "format": "uuid"}
    problem = {
        "problem_id": deepcopy(uid),
        "description": {"type": "string", "maxLength": 1000},
        "affected_area": {"type": "string", "maxLength": 150},
        "supporting_evidence": {"type": "string", "maxLength": 4000},
    }
    required_problem = list(problem)
    schemas["AIDiagnosisEvidenceReference"] = closed(
        {"object_id": deepcopy(uid), "revision_id": deepcopy(uid)}, ["object_id", "revision_id"]
    )
    problem["evidence_references"] = {
        "type": "array",
        "maxItems": 5,
        "uniqueItems": True,
        "items": {"$ref": "#/components/schemas/AIDiagnosisEvidenceReference"},
    }
    schemas["AIDiagnosisProblem"] = closed(problem, required_problem)
    data = {
        "title": {"type": "string", "minLength": 1, "maxLength": 150},
        "problems": {
            "type": "array",
            "maxItems": 20,
            "items": {"$ref": "#/components/schemas/AIDiagnosisProblem"},
        },
        "priority_order": {"type": "array", "maxItems": 20, "uniqueItems": True, "items": deepcopy(uid)},
    }
    schemas["AIDiagnosisData"] = closed(data, list(data))
    create = {"operation_id": deepcopy(uid), "data": {"$ref": "#/components/schemas/AIDiagnosisData"}}
    schemas["AIDiagnosisCreate"] = closed(create, list(create))
    update = {**create, "expected_revision": deepcopy(uid)}
    schemas["AIDiagnosisUpdate"] = closed(update, list(update))
    complete = {"operation_id": deepcopy(uid), "expected_revision": deepcopy(uid)}
    schemas["AIDiagnosisComplete"] = closed(complete, list(complete))
    revise = {**complete, "reason": {"type": "string", "minLength": 1, "maxLength": 1000}}
    schemas["AIDiagnosisRevise"] = closed(revise, list(revise))
    stored = {
        **deepcopy(data),
        "completed_at": {"type": "string", "format": "date-time"},
        "completed_by": deepcopy(uid),
        "correction_reason": {"type": "string", "minLength": 1, "maxLength": 1000},
    }
    schemas["AIDiagnosisStoredData"] = closed(stored, list(data))
    state = {"enum": ["Draft", "Completed"]}
    result = {
        "object_id": deepcopy(uid),
        "revision_id": deepcopy(uid),
        "business_state": deepcopy(state),
        "data": {"$ref": "#/components/schemas/AIDiagnosisStoredData"},
    }
    schemas["AIDiagnosis"] = closed(result, list(result))
    receipt = {key: deepcopy(value) for key, value in result.items() if key != "data"}
    receipt.update(
        operation_id=deepcopy(uid),
        correlation_id=deepcopy(uid),
        saved_at={"type": "string", "format": "date-time"},
    )
    schemas["AIDiagnosisReceipt"] = closed(receipt, list(receipt))
    listing = {
        "items": {"type": "array", "maxItems": 100, "items": {"$ref": "#/components/schemas/AIDiagnosis"}},
        "next_cursor": {"type": ["string", "null"]},
    }
    schemas["AIDiagnosisList"] = closed(listing, list(listing))
    history_item = {
        "revision_id": deepcopy(uid),
        "revision_number": {"type": "integer", "minimum": 1},
        "saved_at": {"type": "string", "format": "date-time"},
        "business_state": deepcopy(state),
        "title": {"type": "string", "maxLength": 150},
    }
    schemas["AIDiagnosisHistoryItem"] = closed(history_item, list(history_item))
    history = {
        "object_id": deepcopy(uid),
        "items": {
            "type": "array",
            "maxItems": 100,
            "items": {"$ref": "#/components/schemas/AIDiagnosisHistoryItem"},
        },
        "next_cursor": {"type": ["string", "null"]},
    }
    schemas["AIDiagnosisHistory"] = closed(history, list(history))
    for method, suffix, operation, request, response in ROUTES:
        path = "/v1/tenants/{tenant_id}/" + ROOT + suffix
        parameters = [{"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}]
        for name in ("object_id", "revision_id"):
            if "{" + name + "}" in suffix:
                parameters.append({"name": name, "in": "path", "required": True, "schema": deepcopy(uid)})
        if operation in ("list_ai_diagnoses", "list_ai_diagnosis_revisions"):
            parameters += [
                {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100}},
                {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
            ]
        write_access = request is not None
        capability = "ai.diagnosis.manage" if write_access else "ai.diagnosis.read"
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "parameters": parameters,
            "responses": {},
        }
        status = "201" if operation == "create_ai_diagnosis" else "200"
        entry["responses"][status] = {
            "description": "Manual diagnosis or durable command receipt; completion is not approval",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
        }
        for refusal in ("400", "401", "403", "404", "409", "422", "429", "503"):
            entry["responses"][refusal] = {
                "description": "Request refused",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}
                },
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
                "capability": capability,
                "role_templates": ["TENANT_ADMIN"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300
                if operation in ("complete_ai_diagnosis", "revise_ai_diagnosis")
                else None,
                "audit": write_access,
            }
        )
