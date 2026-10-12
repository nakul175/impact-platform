"""Contracts for deterministic Improve suggestions and mandatory Diagnose-cycle uptake."""
from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.56.0"
ROOT = "ai-enablement/next-opportunities"
IMPLEMENTED = [("get", ROOT), ("post", ROOT + "/{suggestion_id}/actions/take-up")]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    suggestion = closed({
        "suggestion_id": deepcopy(uid), "title": {"type": "string"},
        "affected_area": {"type": "string"}, "explanation": {"type": "string"},
        "source_diagnosis_id": deepcopy(uid), "source_diagnosis_revision": deepcopy(uid),
        "source_problem_id": deepcopy(uid),
        "source_review_id": deepcopy(uid), "source_review_revision": deepcopy(uid),
    }, ["suggestion_id", "title", "affected_area", "explanation", "source_diagnosis_id", "source_diagnosis_revision", "source_problem_id", "source_review_id", "source_review_revision"])
    schemas["AINextOpportunitySuggestion"] = suggestion
    schemas["AINextOpportunityList"] = closed({"stage": {"const": "Improve"}, "items": {"type": "array", "maxItems": 20, "items": suggestion}}, ["stage", "items"])
    schemas["AINextOpportunityTakeUp"] = closed({"operation_id": deepcopy(uid)}, ["operation_id"])
    receipt = {
        "operation_id": deepcopy(uid), "correlation_id": deepcopy(uid), "cycle_id": deepcopy(uid),
        "cycle_revision": deepcopy(uid), "cycle_state": {"const": "Diagnose"},
        "diagnosis_id": deepcopy(uid), "diagnosis_revision": deepcopy(uid),
        "diagnosis_state": {"const": "Draft"}, "saved_at": {"type": "string", "format": "date-time"},
    }
    schemas["AINextOpportunityReceipt"] = closed(receipt, list(receipt))
    root = "/v1/tenants/{tenant_id}/" + ROOT
    tenant = {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}
    sid = {"name": "suggestion_id", "in": "path", "required": True, "schema": deepcopy(uid)}
    operations = [
        ("get", root, "list_ai_next_opportunities", None, "AINextOpportunityList", [tenant]),
        ("post", root + "/{suggestion_id}/actions/take-up", "take_up_ai_next_opportunity", "AINextOpportunityTakeUp", "AINextOpportunityReceipt", [tenant, sid]),
    ]
    for method, path, operation_id, request, response, parameters in operations:
        spec["paths"][path] = spec["paths"].get(path, {})
        capability = "ai.diagnosis.manage" if method == "post" else "ai.diagnosis.read"
        op = {"operationId": operation_id, "x-capability": capability, "x-contract-version": VERSION, "parameters": parameters,
              "responses": {"201" if method == "post" else "200": {"description": "Success", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}}}}}
        if request:
            op["requestBody"] = {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}}}
        spec["paths"][path][method] = op
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": method.upper(),
                "path": path,
                "capability": capability,
                "role_templates": ["TENANT_ADMIN"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if method == "post" else None,
                "audit": method == "post",
            }
        )
