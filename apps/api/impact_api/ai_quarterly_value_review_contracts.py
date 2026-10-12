"""Closed contracts for quarterly value reviews and tracked agreed actions."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.55.0"
ROOT = "ai-enablement/quarterly-value-reviews"
IMPLEMENTED = [
    ("post", ROOT),
    ("get", ROOT + "/{review_id}"),
    ("post", ROOT + "/{review_id}/agreements"),
    ("post", ROOT + "/{review_id}/actions"),
    ("post", ROOT + "/{review_id}/actions/{action_id}/progress"),
    ("post", ROOT + "/{review_id}/actions/complete"),
]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    operation = {"operation_id": deepcopy(uid), "expected_revision": deepcopy(uid)}
    start = {
        "operation_id": deepcopy(uid),
        "outcome_observation_id": deepcopy(uid),
        "outcome_observation_revision": deepcopy(uid),
    }
    schemas["AIQuarterlyValueReviewStart"] = closed(start, list(start))
    agreement_create = {
        **deepcopy(operation),
        "agreement_id": deepcopy(uid),
        "text": {"type": "string", "minLength": 1, "maxLength": 2000, "pattern": r"\S"},
    }
    schemas["AIQuarterlyValueReviewAgreementCreate"] = closed(agreement_create, list(agreement_create))
    action_create = {
        **deepcopy(operation),
        "action_id": deepcopy(uid),
        "agreement_id": deepcopy(uid),
        "title": {"type": "string", "minLength": 1, "maxLength": 300, "pattern": r"\S"},
        "owner_membership_id": deepcopy(uid),
        "due_on": {"type": "string", "format": "date"},
    }
    schemas["AIQuarterlyValueReviewActionCreate"] = closed(action_create, list(action_create))
    progress = {
        **deepcopy(operation),
        "status": {"enum": ["OPEN", "IN_PROGRESS", "BLOCKED", "DONE"]},
        "note": {"type": "string", "minLength": 1, "maxLength": 2000, "pattern": r"\S"},
    }
    schemas["AIQuarterlyValueReviewActionProgress"] = closed(progress, list(progress))
    complete = {
        **deepcopy(operation),
        "summary": {"type": "string", "minLength": 1, "maxLength": 4000, "pattern": r"\S"},
    }
    schemas["AIQuarterlyValueReviewComplete"] = closed(complete, list(complete))
    template_section = closed({"key": {"type": "string"}, "title": {"type": "string"}}, ["key", "title"])
    template = closed(
        {
            "edition": {"const": "quarterly-value-review-2026-10-12.1"},
            "title": {"type": "string"},
            "sections": {
                "type": "array",
                "minItems": 4,
                "maxItems": 4,
                "items": template_section,
            },
        },
        ["edition", "title", "sections"],
    )
    source_fields = {
        "outcome_observation_id": deepcopy(uid),
        "outcome_observation_revision": deepcopy(uid),
        "plan_id": deepcopy(uid),
        "plan_revision": deepcopy(uid),
        "deployment_attestation_id": deepcopy(uid),
        "baseline_object_id": deepcopy(uid),
        "baseline_revision": deepcopy(uid),
        "opportunity_id": {"type": "string"},
    }
    source = closed(source_fields, list(source_fields))
    agreement = closed(
        {
            "agreement_id": deepcopy(uid),
            "text": {"type": "string"},
            "agreed_at": {"type": "string", "format": "date-time"},
            "agreed_by": deepcopy(uid),
        },
        ["agreement_id", "text", "agreed_at", "agreed_by"],
    )
    event = closed(
        {
            "status": progress["status"],
            "note": {"type": "string"},
            "recorded_at": {"type": "string", "format": "date-time"},
            "recorded_by": deepcopy(uid),
        },
        ["status", "note", "recorded_at", "recorded_by"],
    )
    action = closed(
        {
            "action_id": deepcopy(uid),
            "agreement_id": deepcopy(uid),
            "title": {"type": "string"},
            "owner_membership_id": deepcopy(uid),
            "owner_principal_id": deepcopy(uid),
            "due_on": {"type": "string", "format": "date"},
            "status": progress["status"],
            "created_at": {"type": "string", "format": "date-time"},
            "created_by": deepcopy(uid),
            "progress": {"type": "array", "maxItems": 20, "items": event},
        },
        [
            "action_id",
            "agreement_id",
            "title",
            "owner_membership_id",
            "owner_principal_id",
            "due_on",
            "status",
            "created_at",
            "created_by",
            "progress",
        ],
    )
    review_fields = {
        "template": template,
        "period_start": {"type": "string", "format": "date"},
        "period_end": {"type": "string", "format": "date"},
        "due_on": {"type": "string", "format": "date"},
        "source": source,
        "agreements": {"type": "array", "maxItems": 50, "items": agreement},
        "actions": {"type": "array", "maxItems": 50, "items": action},
        "started_at": {"type": "string", "format": "date-time"},
        "started_by": deepcopy(uid),
        "advisor_principal_id": deepcopy(uid),
        "advisor_membership_id": deepcopy(uid),
        "advisor_natural_identity_id": deepcopy(uid),
        "completed_at": {"type": ["string", "null"], "format": "date-time"},
        "completed_by": {"type": ["string", "null"], "format": "uuid"},
        "completion_summary": {"type": ["string", "null"]},
    }
    schemas["AIQuarterlyValueReviewData"] = closed(review_fields, list(review_fields))
    response = {
        "object_id": deepcopy(uid),
        "revision_id": deepcopy(uid),
        "business_state": {"enum": ["InProgress", "Completed"]},
        "review": {"$ref": "#/components/schemas/AIQuarterlyValueReviewData"},
    }
    schemas["AIQuarterlyValueReview"] = closed(response, list(response))
    receipt = {
        **deepcopy(response),
        "operation_id": deepcopy(uid),
        "correlation_id": deepcopy(uid),
        "saved_at": {"type": "string", "format": "date-time"},
    }
    schemas["AIQuarterlyValueReviewReceipt"] = closed(receipt, list(receipt))

    root = "/v1/tenants/{tenant_id}/" + ROOT
    tenant = {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}
    routes = [
        ("post", root, "start_ai_quarterly_value_review", "AIQuarterlyValueReviewStart", False),
        ("get", root + "/{review_id}", "get_ai_quarterly_value_review", None, False),
        (
            "post",
            root + "/{review_id}/agreements",
            "record_ai_quarterly_review_agreement",
            "AIQuarterlyValueReviewAgreementCreate",
            False,
        ),
        (
            "post",
            root + "/{review_id}/actions",
            "record_ai_quarterly_review_action",
            "AIQuarterlyValueReviewActionCreate",
            False,
        ),
        (
            "post",
            root + "/{review_id}/actions/{action_id}/progress",
            "track_ai_quarterly_review_action",
            "AIQuarterlyValueReviewActionProgress",
            False,
        ),
        (
            "post",
            root + "/{review_id}/actions/complete",
            "complete_ai_quarterly_value_review",
            "AIQuarterlyValueReviewComplete",
            True,
        ),
    ]
    for method, path, operation_id, request_schema, fresh in routes:
        parameters = [deepcopy(tenant)]
        for name in ("review_id", "action_id"):
            if "{" + name + "}" in path:
                parameters.append({"name": name, "in": "path", "required": True, "schema": deepcopy(uid)})
        entry = {
            "operationId": operation_id,
            "summary": operation_id.replace("_", " "),
            "x-capability": "ai.diagnosis.review",
            "x-contract-version": VERSION,
            "parameters": parameters,
            "responses": {
                "200" if method == "get" else "201": {
                    "description": "Current exact quarterly value review",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AIQuarterlyValueReview"
                                if method == "get"
                                else "#/components/schemas/AIQuarterlyValueReviewReceipt"
                            }
                        }
                    },
                }
            },
        }
        if request_schema:
            entry["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/" + request_schema}}
                },
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": method.upper(),
                "path": path,
                "capability": entry["x-capability"],
                "role_templates": ["REVIEWER"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if fresh else None,
                "audit": method == "post",
            }
        )
