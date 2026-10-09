"""JSON-only saved-plan internal-copy contracts; frozen public projection v1."""

from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from impact_api.ai_adoption_contracts import MANAGERS
from impact_api.ai_content_archives import EDITIONS as GUIDANCE_EDITIONS
from impact_api.ai_content_contracts import guidance_variants
from impact_api.measurement_contracts import UUID, closed

VERSION = "1.25.0"
OPERATION = "issue_ai_plan_export"
CAPABILITY = "ai.enablement.export"
ROUTE = "ai-enablement/plans/{object_id}/revisions/{revision_id}/exports"
IMPLEMENTED = [("post", ROUTE)]
PACKAGE_VERSION = "nonprofit-ai-plan-export-v1"
RENDERER_VERSION = "nonprofit-ai-plan-json-v1"
MAX_COPY_BYTES = 1048576
REPLAY_HOURS = 168
DATE = {"type": "string", "format": "date-time"}
HASH = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
GUIDANCE_STATUS = {"enum": ["COMPLETE", "PARTIAL", "UNAVAILABLE"]}
DISCLAIMER = (
    "This is a saved draft planning record for internal use. It is not procurement approval, "
    "a competency certification or official programme impact. Unavailable historical guidance "
    "is not reconstructed. This download cannot be recalled after it is saved locally."
)
PUBLIC_SCHEMA = json.loads(Path(__file__).with_name("ai_plan_public_export_schema_v1.json").read_text())
REQUEST_SCHEMA = closed(
    {
        "operation_id": deepcopy(UUID),
        "data": closed(
            {
                "format": {"const": "JSON"},
                "restriction": {"const": "INTERNAL_SELF"},
                "acknowledged": {"const": True},
            },
            ["format", "restriction", "acknowledged"],
        ),
    },
    ["operation_id", "data"],
)
RECEIPT_SCHEMA = closed(
    {
        "object_id": deepcopy(UUID),
        "revision_id": deepcopy(UUID),
        "business_state": {"const": "Issued"},
        "operation_id": deepcopy(UUID),
        "correlation_id": deepcopy(UUID),
        "saved_at": deepcopy(DATE),
        "content_sha256": deepcopy(HASH),
        "byte_count": {"type": "integer", "minimum": 2, "maximum": MAX_COPY_BYTES},
        "replay_until": deepcopy(DATE),
    },
    [
        "object_id",
        "revision_id",
        "business_state",
        "operation_id",
        "correlation_id",
        "saved_at",
        "content_sha256",
        "byte_count",
        "replay_until",
    ],
)
MANIFEST_SCHEMA = closed(
    {
        "plan_id": deepcopy(UUID),
        "revision_id": deepcopy(UUID),
        "title": {"type": "string", "minLength": 1, "maxLength": 150},
        "saved_at": deepcopy(DATE),
        "generated_at": deepcopy(DATE),
        "schema": {"const": PACKAGE_VERSION},
        "renderer": {"const": RENDERER_VERSION},
        "filename": {
            "type": "string",
            "maxLength": 120,
            "pattern": "^impact-ai-plan-[a-f0-9-]+[.]json$",
        },
        "media_type": {"const": "application/json"},
        "content_sha256": deepcopy(HASH),
        "size_bytes": {"type": "integer", "minimum": 2, "maximum": MAX_COPY_BYTES},
        "replay_expires_at": deepcopy(DATE),
        "guidance_status": deepcopy(GUIDANCE_STATUS),
    },
    [
        "plan_id",
        "revision_id",
        "title",
        "saved_at",
        "generated_at",
        "schema",
        "renderer",
        "filename",
        "media_type",
        "content_sha256",
        "size_bytes",
        "replay_expires_at",
        "guidance_status",
    ],
)


def guidance_schema():
    """The archived guidance exactly as the guidance read returns it: one variant per archive edition
    (v1, and v2 with commercial disclosures since build 0.39.0), labelled by snapshot_schema_version,
    or the unavailable variant. Exports issued before 0.39.0 carry v1 guidance and still validate."""
    return {"oneOf": guidance_variants(lambda version, name: deepcopy(GUIDANCE_EDITIONS[version][name]))}


def document_schema():
    public = {"$ref": "#/$defs/AIAdoptionPlanStoredData"}
    plan = closed(
        {
            "object_id": deepcopy(UUID),
            "revision_id": deepcopy(UUID),
            "saved_at": deepcopy(DATE),
            "schema_version": {"type": "string", "minLength": 1, "maxLength": 64},
            "data": public,
        },
        ["object_id", "revision_id", "saved_at", "schema_version", "data"],
    )
    fields = {
        "schema_version": {"const": PACKAGE_VERSION},
        "renderer_version": {"const": RENDERER_VERSION},
        "tenant_id": deepcopy(UUID),
        "issuance_id": deepcopy(UUID),
        "generated_at": deepcopy(DATE),
        "restriction": {"const": "INTERNAL_SELF"},
        "record_status": {"const": "Draft"},
        "declared_components": {"const": ["PUBLIC_PLAN", "ARCHIVED_GUIDANCE"]},
        "plan": plan,
        "guidance": guidance_schema(),
        "disclaimer": {"const": DISCLAIMER},
    }
    return {**closed(fields, list(fields)), "$defs": deepcopy(PUBLIC_SCHEMA["$defs"])}


DOCUMENT_SCHEMA = document_schema()
REQUEST_VALIDATOR = Draft202012Validator(REQUEST_SCHEMA, format_checker=FormatChecker())
PUBLIC_VALIDATOR = Draft202012Validator(PUBLIC_SCHEMA, format_checker=FormatChecker())
DOCUMENT_VALIDATOR = Draft202012Validator(DOCUMENT_SCHEMA, format_checker=FormatChecker())
RECEIPT_VALIDATOR = Draft202012Validator(RECEIPT_SCHEMA, format_checker=FormatChecker())
MANIFEST_VALIDATOR = Draft202012Validator(MANIFEST_SCHEMA, format_checker=FormatChecker())
POLICY = {
    "operation_id": OPERATION,
    "method": "POST",
    "path": "/v1/tenants/{tenant_id}/" + ROUTE,
    "capability": CAPABILITY,
    "role_templates": deepcopy(MANAGERS),
    "purpose_required": False,
    "fresh_assurance_seconds": 300,
    "independence_required": False,
    "field_filter_required": True,
    "audit": True,
    "state_guard": (
        "Current self member with scoped export and read authority on an exact AVAILABLE saved revision; "
        "retained original JSON bytes, separate unapproved draft record and actual archived guidance only."
    ),
}


def _openapi(value):
    if isinstance(value, dict):
        return {
            name: "#/components/schemas/AIPlanExportV1" + item.split("/")[-1]
            if name == "$ref" and isinstance(item, str) and item.startswith("#/$defs/")
            else _openapi(item)
            for name, item in value.items()
            if name != "$defs"
        }
    if isinstance(value, list):
        return [_openapi(item) for item in value]
    return deepcopy(value)


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    for name, schema in PUBLIC_SCHEMA["$defs"].items():
        schemas["AIPlanExportV1" + name] = _openapi(schema)
    schemas["AIPlanExportRequest"] = deepcopy(REQUEST_SCHEMA)
    schemas["AIPlanExportReceipt"] = deepcopy(RECEIPT_SCHEMA)
    schemas["AIPlanExportManifest"] = deepcopy(MANIFEST_SCHEMA)
    schemas["AIPlanExportDocumentV1"] = _openapi(DOCUMENT_SCHEMA)
    schemas["AIPlanExport"] = closed(
        {
            "manifest": {"$ref": "#/components/schemas/AIPlanExportManifest"},
            "content": {"type": "string", "minLength": 2, "maxLength": MAX_COPY_BYTES},
            "receipt": {"$ref": "#/components/schemas/AIPlanExportReceipt"},
        },
        ["manifest", "content", "receipt"],
    )
    entry = {
        "operationId": OPERATION,
        "summary": "Issue an internal copy of one exact saved AI-plan revision",
        "description": (
            "JSON-only self download of a draft planning record. Separate ai.enablement.export and current "
            "exact-revision read authority are required on issue and every replay. Original bytes, digest, "
            "manifest time, audit identity and nondelivery outbox intent remain bound atomically."
        ),
        "x-capability": CAPABILITY,
        "x-contract-version": VERSION,
        "x-audit-required": True,
        "parameters": [
            {"name": name, "in": "path", "required": True, "schema": deepcopy(UUID)}
            for name in ("tenant_id", "object_id", "revision_id")
        ],
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIPlanExportRequest"}}},
        },
        "responses": {
            "200": {
                "description": "Exact UTF-8 content string and original digest manifest; not delivery proof",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AIPlanExport"}}},
            }
        },
    }
    for code in ("400", "401", "403", "404", "409", "422", "429", "503"):
        entry["responses"][code] = {
            "description": "Request refused without exposing hidden records or private fields",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        }
    spec["paths"][POLICY["path"]] = {"post": entry}
    policy["operations"].append(deepcopy(POLICY))
