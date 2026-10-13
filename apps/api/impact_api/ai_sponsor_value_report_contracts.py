"""Closed contracts for explicit recipient-bound sponsor value reports."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.54.0"
ROOT = "ai-enablement/sponsor-value-reports"
IMPLEMENTED = [("post", ROOT), ("get", ROOT + "/{object_id}")]
ITEMS = [
    "ROI_PERCENT",
    "NET_BENEFIT",
    "REALISED_BENEFIT",
    "REALISED_COST",
    "USAGE",
    "TIME",
    "COST",
    "QUALITY",
    "REACH",
]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    money = {"type": "string", "pattern": r"^(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?$"}
    realised = {
        "currency": {"type": "string", "pattern": "^[A-Za-z]{3}$"},
        "observed_from": {"type": "string", "format": "date"},
        "observed_to": {"type": "string", "format": "date"},
        "realised_benefit": money,
        "realised_cost": deepcopy(money),
        "source_note": {"type": "string", "minLength": 1, "maxLength": 2000},
    }
    schemas["AISponsorRealisedValues"] = closed(realised, list(realised))
    create = {
        "operation_id": deepcopy(uid),
        "sponsor_membership_id": deepcopy(uid),
        "expires_at": {"type": "string", "format": "date-time"},
        "title": {"type": "string", "minLength": 1, "maxLength": 150},
        "value_case_object_id": deepcopy(uid),
        "value_case_revision": deepcopy(uid),
        "outcome_observation_id": deepcopy(uid),
        "outcome_observation_revision": deepcopy(uid),
        "realised": {"$ref": "#/components/schemas/AISponsorRealisedValues"},
        "selected_items": {
            "type": "array",
            "minItems": 1,
            "maxItems": len(ITEMS),
            "uniqueItems": True,
            "items": {"enum": ITEMS},
        },
    }
    schemas["AISponsorValueReportCreate"] = closed(create, list(create))
    receipt = {
        "object_id": deepcopy(uid),
        "revision_id": deepcopy(uid),
        "business_state": {"const": "Published"},
        "saved_at": {"type": "string", "format": "date-time"},
        "operation_id": deepcopy(uid),
        "correlation_id": deepcopy(uid),
    }
    schemas["AISponsorValueReportReceipt"] = closed(receipt, list(receipt))
    report = {
        "object_id": deepcopy(uid),
        "revision_id": deepcopy(uid),
        "business_state": {"const": "Published"},
        "title": {"type": "string"},
        "selected_items": create["selected_items"],
        "items": {
            "type": "object",
            "propertyNames": {"enum": ITEMS},
            "additionalProperties": {
                "oneOf": [deepcopy(money), {"type": "object"}],
            },
        },
        "currency": {"type": "string"},
        "observed_from": {"type": "string", "format": "date"},
        "observed_to": {"type": "string", "format": "date"},
        "reporting_basis": {"const": "SELF_REPORTED_REALISED"},
        "generated_at": {"type": "string", "format": "date-time"},
        "expires_at": {"type": "string", "format": "date-time"},
        "disclaimer": {"type": "string"},
        "manifest": closed(
            {
                "renderer_version": {"const": "ai-sponsor-value-report-v1"},
                "media_type": {"const": "application/json"},
                "content_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "size_bytes": {"type": "integer", "minimum": 1},
            },
            ["renderer_version", "media_type", "content_sha256", "size_bytes"],
        ),
        "content_base64": {"type": "string", "contentEncoding": "base64"},
    }
    schemas["AISponsorValueReport"] = closed(report, list(report))
    base = "/v1/tenants/{tenant_id}/" + ROOT
    tenant = {"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}
    spec["paths"][base] = {
        "parameters": [tenant],
        "post": {
            "operationId": "create_ai_sponsor_value_report",
            "summary": "Generate an organisation-selected sponsor value report",
            "x-capability": "ai.enablement.manage",
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AISponsorValueReportCreate"}
                    }
                },
            },
            "responses": {
                "201": {
                    "description": "Immutable recipient-bound report receipt",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AISponsorValueReportReceipt"}
                        }
                    },
                }
            },
        },
    }
    spec["paths"][base + "/{object_id}"] = {
        "parameters": [
            tenant,
            {"name": "object_id", "in": "path", "required": True, "schema": deepcopy(uid)},
        ],
        "get": {
            "operationId": "get_ai_sponsor_value_report",
            "summary": "Read one report as its named sponsor recipient",
            "x-capability": "publication.download",
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "Selected report fields only",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AISponsorValueReport"}}
                    },
                }
            },
        },
    }
    policy["operations"] += [
        {
            "operation_id": "create_ai_sponsor_value_report",
            "method": "POST",
            "path": base,
            "capability": "ai.enablement.manage",
            "role_templates": ["TENANT_ADMIN"],
            "purpose_required": False,
            "fresh_assurance_seconds": 300,
            "audit": True,
        },
        {
            "operation_id": "get_ai_sponsor_value_report",
            "method": "GET",
            "path": base + "/{object_id}",
            "capability": "publication.download",
            "role_templates": ["EXTERNAL"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": True,
        },
    ]
