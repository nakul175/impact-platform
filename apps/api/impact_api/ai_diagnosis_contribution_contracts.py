"""Closed contracts for governed contributions to one existing diagnosis."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.34.0"
ROOT = "ai-enablement/diagnoses/{object_id}"
ROUTES = [
    (
        "get",
        "/contributor-invitations",
        "list_ai_diagnosis_contributor_invitations",
        None,
        "AIDiagnosisContributorInvitationList",
    ),
    (
        "post",
        "/contributor-invitations",
        "create_ai_diagnosis_contributor_invitation",
        "AIDiagnosisContributorInvitationCreate",
        "AIDiagnosisContributorInvitation",
    ),
    ("get", "/contributions", "list_ai_diagnosis_contributions", None, "AIDiagnosisContributionList"),
    (
        "post",
        "/contributions",
        "submit_ai_diagnosis_contribution",
        "AIDiagnosisContributionSubmit",
        "AIDiagnosisContribution",
    ),
    (
        "post",
        "/contributions/{contribution_id}/actions/accept",
        "accept_ai_diagnosis_contribution",
        "AIDiagnosisContributionDecision",
        "AIDiagnosisContributionDecisionReceipt",
    ),
    (
        "post",
        "/contributions/{contribution_id}/actions/reject",
        "reject_ai_diagnosis_contribution",
        "AIDiagnosisContributionRejection",
        "AIDiagnosisContributionDecisionReceipt",
    ),
]
IMPLEMENTED = [(method, ROOT + suffix) for method, suffix, *_ in ROUTES]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    roles = ["PROBLEM_OWNER", "EVIDENCE_CONTRIBUTOR", "PRIORITISATION_CONTRIBUTOR"]
    sections = ["PROBLEM_DESCRIPTION", "AFFECTED_AREA", "SUPPORTING_EVIDENCE", "PRIORITY_ORDER"]
    operation = {"operation_id": deepcopy(uid)}
    invitation = {
        "assignment_id": deepcopy(uid),
        "diagnosis_id": deepcopy(uid),
        "diagnosis_revision": deepcopy(uid),
        "member_invitation_id": deepcopy(uid),
        "contribution_role": {"enum": roles},
        "problem_ids": {
            "type": "array",
            "minItems": 1,
            "maxItems": 20,
            "uniqueItems": True,
            "items": deepcopy(uid),
        },
        "sections": {
            "type": "array",
            "minItems": 1,
            "maxItems": 4,
            "uniqueItems": True,
            "items": {"enum": sections},
        },
        "delivery_state": {"enum": ["QUEUED", "DELIVERED", "FAILED", "EXPIRED", "REVOKED", "ACCEPTED"]},
        "created_at": {"type": "string", "format": "date-time"},
    }
    schemas["AIDiagnosisContributorInvitation"] = closed(invitation, list(invitation))
    invitation_create = {
        **deepcopy(operation),
        "expected_diagnosis_revision": deepcopy(uid),
        "member_invitation_id": deepcopy(uid),
        "contribution_role": {"enum": roles},
        "problem_ids": deepcopy(invitation["problem_ids"]),
        "sections": deepcopy(invitation["sections"]),
    }
    schemas["AIDiagnosisContributorInvitationCreate"] = closed(invitation_create, list(invitation_create))
    schemas["AIDiagnosisContributorInvitationList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIDiagnosisContributorInvitation"},
            }
        },
        ["items"],
    )
    evidence_ref = {"object_id": deepcopy(uid), "revision_id": deepcopy(uid)}
    patch_fields = {
        "description": {"type": "string", "maxLength": 1000},
        "affected_area": {"type": "string", "maxLength": 150},
        "supporting_evidence": {"type": "string", "maxLength": 4000},
        "evidence_references": {
            "type": "array",
            "maxItems": 5,
            "uniqueItems": True,
            "items": closed(evidence_ref, list(evidence_ref)),
        },
    }
    schemas["AIDiagnosisContributionProblemPatch"] = closed(
        {"problem_id": deepcopy(uid), "fields": closed(patch_fields, [])},
        ["problem_id", "fields"],
    )
    patch = {
        "problem_updates": {
            "type": "array",
            "maxItems": 20,
            "items": {"$ref": "#/components/schemas/AIDiagnosisContributionProblemPatch"},
        },
        "priority_order": {
            "type": ["array", "null"],
            "maxItems": 20,
            "uniqueItems": True,
            "items": deepcopy(uid),
        },
    }
    schemas["AIDiagnosisContributionPatch"] = closed(patch, list(patch))
    submit = {
        **deepcopy(operation),
        "assignment_id": deepcopy(uid),
        "expected_diagnosis_revision": deepcopy(uid),
        "patch": {"$ref": "#/components/schemas/AIDiagnosisContributionPatch"},
    }
    schemas["AIDiagnosisContributionSubmit"] = closed(submit, list(submit))
    contribution = {
        "contribution_id": deepcopy(uid),
        "assignment_id": deepcopy(uid),
        "diagnosis_id": deepcopy(uid),
        "base_revision": deepcopy(uid),
        "contribution_role": {"enum": roles},
        "patch": {"$ref": "#/components/schemas/AIDiagnosisContributionPatch"},
        "submitted_at": {"type": "string", "format": "date-time"},
        "decision": {"enum": ["PENDING", "ACCEPTED", "REJECTED"]},
    }
    schemas["AIDiagnosisContribution"] = closed(contribution, list(contribution))
    schemas["AIDiagnosisContributionList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIDiagnosisContribution"},
            }
        },
        ["items"],
    )
    decision = {**deepcopy(operation), "expected_diagnosis_revision": deepcopy(uid)}
    schemas["AIDiagnosisContributionDecision"] = closed(decision, list(decision))
    schemas["AIDiagnosisContributionRejection"] = closed(
        {**deepcopy(decision), "reason": {"type": "string", "minLength": 1, "maxLength": 1000}},
        [*decision, "reason"],
    )
    receipt = {
        "operation_id": deepcopy(uid),
        "contribution_id": deepcopy(uid),
        "decision": {"enum": ["ACCEPTED", "REJECTED"]},
        "diagnosis_id": deepcopy(uid),
        "diagnosis_revision": deepcopy(uid),
        "saved_at": {"type": "string", "format": "date-time"},
    }
    schemas["AIDiagnosisContributionDecisionReceipt"] = closed(receipt, list(receipt))
    for method, suffix, operation_id, request, response in ROUTES:
        path = "/v1/tenants/{tenant_id}/" + ROOT + suffix
        parameters = [
            {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)},
            {"name": "object_id", "in": "path", "required": True, "schema": deepcopy(uid)},
        ]
        if "{contribution_id}" in suffix:
            parameters.append(
                {"name": "contribution_id", "in": "path", "required": True, "schema": deepcopy(uid)}
            )
        contribute = operation_id == "submit_ai_diagnosis_contribution"
        capability = "ai.diagnosis.contribute" if contribute else "ai.diagnosis.contributors.manage"
        entry = {
            "operationId": operation_id,
            "summary": operation_id.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "parameters": parameters,
            "responses": {
                "201" if method == "post" and "actions" not in suffix else "200": {
                    "description": "Governed assignment, contribution or immutable decision",
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
                "role_templates": ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"]
                if not contribute
                else ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300
                if operation_id in ("accept_ai_diagnosis_contribution", "reject_ai_diagnosis_contribution")
                else None,
                "audit": method == "post",
            }
        )
