"""Contracts for consented, minimum-five cross-organisation outcome evidence."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.57.0"
TENANT_IMPLEMENTED = [("post", "ai-enablement/outcome-sharing-consents")]
PLATFORM_IMPLEMENTED = [
    ("get", "/v1/platform/outcome-evidence-publications"),
    ("post", "/v1/platform/outcome-evidence-publications"),
    ("post", "/v1/platform/outcome-evidence-publications/{publication_id}/actions/{action}"),
]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    schemas["AIOutcomeSharingConsentCreate"] = closed(
        {
            "operation_id": deepcopy(uid),
            "outcome_observation_id": deepcopy(uid),
            "outcome_observation_revision": deepcopy(uid),
            "decision": {"enum": ["GRANTED", "WITHDRAWN"]},
            "allowed_metrics": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "uniqueItems": True,
                "items": {"enum": ["time", "cost", "quality", "reach", "usage"]},
            },
            "notice_version": {"type": "string", "minLength": 1, "maxLength": 100},
            "reason": {"type": "string", "minLength": 1, "maxLength": 1000},
        },
        [
            "operation_id",
            "outcome_observation_id",
            "outcome_observation_revision",
            "decision",
            "allowed_metrics",
            "notice_version",
            "reason",
        ],
    )
    consent = {
        "operation_id": deepcopy(uid),
        "correlation_id": deepcopy(uid),
        "consent_event_id": deepcopy(uid),
        "decision": {"enum": ["GRANTED", "WITHDRAWN"]},
        "purpose": {"const": "WHAT_WORKS_AGGREGATION"},
        "outcome_observation_id": deepcopy(uid),
        "outcome_observation_revision": deepcopy(uid),
        "notice_version": {"type": "string"},
        "allowed_metrics": {"type": "array", "items": {"type": "string"}},
        "recorded_at": {"type": "string", "format": "date-time"},
    }
    schemas["AIOutcomeSharingConsentReceipt"] = closed(consent, list(consent))
    schemas["AIOutcomeEvidencePrepare"] = closed({"operation_id": deepcopy(uid)}, ["operation_id"])
    schemas["AIOutcomeEvidenceAction"] = closed(
        {"operation_id": deepcopy(uid), "expected_revision": deepcopy(uid)},
        ["operation_id", "expected_revision"],
    )
    cell = closed(
        {
            "metric": {"type": "string"},
            "unit": {"type": "string"},
            "period_bucket": {"type": "string", "pattern": "^[0-9]{4}-Q[1-4]$"},
            "status": {"enum": ["RELEASABLE", "WITHHELD"]},
            "reason": {"type": ["string", "null"]},
            "mean_value": {"type": ["string", "null"]},
            "organisation_count": {"type": ["integer", "null"], "minimum": 5},
        },
        ["metric", "unit", "period_bucket", "status", "reason", "mean_value", "organisation_count"],
    )
    artifact = closed(
        {
            "rule_version": {"type": "string"},
            "policy_version": {"type": "string"},
            "reporting_basis": {"const": "SELF_REPORTED"},
            "items": {"type": "array", "items": cell},
            "limitations": {"type": "string"},
        },
        ["rule_version", "policy_version", "reporting_basis", "items", "limitations"],
    )
    publication = closed(
        {
            "publication_id": deepcopy(uid),
            "revision_id": deepcopy(uid),
            "state": {"enum": ["PREPARED", "APPROVED", "PUBLISHED"]},
            "rule_version": {"type": "string"},
            "policy_version": {"type": "string"},
            "manifest_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            "artifact": artifact,
            "prepared_at": {"type": "string", "format": "date-time"},
            "approved_at": {"type": ["string", "null"], "format": "date-time"},
            "published_at": {"type": ["string", "null"], "format": "date-time"},
        },
        [
            "publication_id",
            "revision_id",
            "state",
            "rule_version",
            "policy_version",
            "manifest_hash",
            "artifact",
            "prepared_at",
            "approved_at",
            "published_at",
        ],
    )
    schemas["AIOutcomeEvidencePublication"] = publication
    schemas["AIOutcomeEvidencePublicationList"] = closed(
        {"items": {"type": "array", "items": publication}}, ["items"]
    )

    tenant_path = "/v1/tenants/{tenant_id}/ai-enablement/outcome-sharing-consents"
    tenant_param = {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}
    spec["paths"][tenant_path] = {
        "post": {
            "operationId": "record_ai_outcome_sharing_consent",
            "x-capability": "ai.enablement.manage",
            "x-contract-version": VERSION,
            "parameters": [tenant_param],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AIOutcomeSharingConsentCreate"}
                    }
                },
            },
            "responses": {
                "201": {
                    "description": "Consent decision recorded",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AIOutcomeSharingConsentReceipt"}
                        }
                    },
                }
            },
        }
    }
    policy["operations"].append(
        {
            "operation_id": "record_ai_outcome_sharing_consent",
            "method": "POST",
            "path": tenant_path,
            "capability": "ai.enablement.manage",
            "role_templates": ["TENANT_ADMIN"],
            "purpose_required": False,
            "fresh_assurance_seconds": 300,
            "audit": True,
        }
    )

    root = "/v1/platform/outcome-evidence-publications"
    pub_param = {"name": "publication_id", "in": "path", "required": True, "schema": deepcopy(uid)}
    action_param = {
        "name": "action",
        "in": "path",
        "required": True,
        "schema": {"enum": ["approve", "publish"]},
    }
    operations = [
        ("get", root, "list_ai_outcome_evidence_publications", None, "AIOutcomeEvidencePublicationList", []),
        (
            "post",
            root,
            "prepare_ai_outcome_evidence_publication",
            "AIOutcomeEvidencePrepare",
            "AIOutcomeEvidencePublication",
            [],
        ),
        (
            "post",
            root + "/{publication_id}/actions/{action}",
            "act_ai_outcome_evidence_publication",
            "AIOutcomeEvidenceAction",
            "AIOutcomeEvidencePublication",
            [pub_param, action_param],
        ),
    ]
    for method, path, operation_id, request, response, params in operations:
        op = {
            "operationId": operation_id,
            "x-capability": "platform.operator",
            "x-contract-version": VERSION,
            "parameters": params,
            "responses": {
                "200" if method == "get" else "201": {
                    "description": "Success",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            op["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        spec["paths"].setdefault(path, {})[method] = op
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": method.upper(),
                "path": path,
                "capability": "platform.operator",
                "role_templates": ["PLATFORM_OPERATOR"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if method == "post" else None,
                "audit": method == "post",
            }
        )
