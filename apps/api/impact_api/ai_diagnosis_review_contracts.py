"""Closed contracts for assigned human review of an exact diagnosis revision."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.35.0"
UUID = {"type": "string", "format": "uuid"}
ROUTES = [
    (
        "post",
        "ai-enablement/diagnoses/{object_id}/advisor-reviews",
        "request_ai_diagnosis_review",
        "AIDiagnosisReviewRequest",
        "AIDiagnosisReview",
    ),
    (
        "get",
        "ai-enablement/diagnoses/{object_id}/advisor-reviews",
        "list_ai_diagnosis_reviews",
        None,
        "AIDiagnosisReviewList",
    ),
    (
        "get",
        "ai-enablement/diagnosis-review-queue",
        "list_ai_diagnosis_review_queue",
        None,
        "AIDiagnosisReviewList",
    ),
    (
        "get",
        "ai-enablement/diagnosis-reviews/{review_id}",
        "get_ai_diagnosis_review",
        None,
        "AIDiagnosisReview",
    ),
    (
        "post",
        "ai-enablement/diagnosis-reviews/{review_id}/actions/start",
        "start_ai_diagnosis_review",
        "AIDiagnosisReviewAction",
        "AIDiagnosisReview",
    ),
    (
        "post",
        "ai-enablement/diagnosis-reviews/{review_id}/comments",
        "comment_ai_diagnosis_review",
        "AIDiagnosisReviewComment",
        "AIDiagnosisReview",
    ),
    (
        "post",
        "ai-enablement/diagnosis-reviews/{review_id}/actions/validate",
        "validate_ai_diagnosis_review",
        "AIDiagnosisReviewAction",
        "AIDiagnosisReview",
    ),
]
IMPLEMENTED = [(method, route) for method, route, *_ in ROUTES]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    schemas["AIDiagnosisReviewRequest"] = closed(
        {
            "operation_id": deepcopy(UUID),
            "expected_diagnosis_revision": deepcopy(UUID),
            "advisor_membership_id": deepcopy(UUID),
        },
        ["operation_id", "expected_diagnosis_revision", "advisor_membership_id"],
    )
    schemas["AIDiagnosisReviewAction"] = closed(
        {"operation_id": deepcopy(UUID), "expected_diagnosis_revision": deepcopy(UUID)},
        ["operation_id", "expected_diagnosis_revision"],
    )
    schemas["AIDiagnosisReviewComment"] = closed(
        {
            "operation_id": deepcopy(UUID),
            "expected_diagnosis_revision": deepcopy(UUID),
            "comment": {"type": "string", "minLength": 1, "maxLength": 4000, "pattern": r"\S"},
        },
        ["operation_id", "expected_diagnosis_revision", "comment"],
    )
    event = closed(
        {
            "event_id": deepcopy(UUID),
            "kind": {"enum": ["STARTED", "COMMENTED", "VALIDATED"]},
            "comment": {"type": ["string", "null"]},
            "actor_id": deepcopy(UUID),
            "recorded_at": {"type": "string", "format": "date-time"},
        },
        ["event_id", "kind", "comment", "actor_id", "recorded_at"],
    )
    review = {
        "review_id": deepcopy(UUID),
        "diagnosis_id": deepcopy(UUID),
        "diagnosis_revision": deepcopy(UUID),
        "advisor_membership_id": deepcopy(UUID),
        "requested_at": {"type": "string", "format": "date-time"},
        "status": {"enum": ["QUEUED", "IN_REVIEW", "VALIDATED", "PREVIOUS_REVISION_VALIDATED"]},
        "events": {"type": "array", "maxItems": 100, "items": event},
    }
    schemas["AIDiagnosisReview"] = closed(review, list(review))
    schemas["AIDiagnosisReviewList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIDiagnosisReview"},
            }
        },
        ["items"],
    )
    for method, route, operation_id, request, response in ROUTES:
        path = "/v1/tenants/{tenant_id}/" + route
        parameters = [{"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(UUID)}]
        for name in ("object_id", "review_id"):
            if "{" + name + "}" in route:
                parameters.append({"name": name, "in": "path", "required": True, "schema": deepcopy(UUID)})
        reviewer = "diagnosis-review" in route and "diagnoses/{object_id}" not in route
        capability = (
            "ai.diagnosis.review"
            if reviewer
            else "ai.diagnosis.manage"
            if operation_id == "request_ai_diagnosis_review"
            else "ai.diagnosis.read"
        )
        entry = {
            "operationId": operation_id,
            "summary": operation_id.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "parameters": parameters,
            "responses": {
                "201" if method == "post" else "200": {
                    "description": "Exact diagnosis review",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for refusal in ("400", "401", "403", "404", "409", "422", "429", "503"):
            entry["responses"][refusal] = {
                "description": "Request refused",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIDiagnosisError"}}
                },
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": method.upper(),
                "path": path,
                "capability": capability,
                "role_templates": ["REVIEWER"]
                if reviewer
                else ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if operation_id == "validate_ai_diagnosis_review" else None,
                "audit": method == "post",
            }
        )
