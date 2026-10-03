"""Audit export contracts (v0.25 part A, VF-AUD-001).

One operation: POST /v1/tenants/{tenant_id}/audit-exports returns one bounded page of the tenant's
append-only audit events for a time window as JSON Lines with a hash chain, a SHA-256 manifest and a
platform seal. It is capability-gated (audit.export, TENANT scope), purpose-required (the request
names a purpose; a purpose-bound grant must name the same one), needs authentication within the last
300 seconds and is itself recorded as an audit event. Served by an explicit route in main.py."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
SHA256 = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
PREFIX = "/v1/tenants/{tenant_id}/"
ROUTE = "audit-exports"
OPERATION = "create_audit_export"
CAPABILITY = "audit.export"
ROLES = ["OWNER", "TENANT_ADMIN"]
PURPOSES = ["SECURITY_REVIEW", "INCIDENT_INVESTIGATION", "REGULATORY_REQUEST", "INTERNAL_AUDIT"]
MAX_LIMIT = 1000
DEFAULT_LIMIT = 500
MAX_WINDOW_DAYS = 366
FORMAT = "impact-audit-export-v2"  # v2 (v0.27): access-denial lines and the occurrences field
# Explicit routes this module serves (method, path below the tenant prefix).
IMPLEMENTED = [("post", ROUTE)]
VERSION = "1.15.0"


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    schemas["AuditExportRequestData"] = closed(
        {
            "window_start": DATE,
            "window_end": DATE,
            "purpose": {"enum": PURPOSES},
            "reason": text_field(2000),
            "limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT},
            "cursor": {"type": "string", "minLength": 1, "maxLength": 4096},
        },
        ["window_start", "window_end", "purpose", "reason"],
    )
    schemas["AuditExportRequest"] = closed(
        {"operation_id": UUID, "data": {"$ref": "#/components/schemas/AuditExportRequestData"}},
        ["operation_id", "data"],
    )
    schemas["AuditExportManifest"] = closed(
        {
            "format": {"const": FORMAT},
            "export_id": UUID,
            "tenant_id": UUID,
            "window_start": DATE,
            "window_end": DATE,
            "purpose": {"enum": PURPOSES},
            "generated_at": DATE,
            "generated_by": UUID,
            "correlation_id": UUID,
            "page": {"type": "integer", "minimum": 1},
            "first_sequence": {"type": ["integer", "null"], "minimum": 1},
            "event_count": {"type": "integer", "minimum": 0, "maximum": MAX_LIMIT},
            "denial_count": {"type": "integer", "minimum": 0, "maximum": MAX_LIMIT},
            "complete": {"type": "boolean"},
            "media_type": {"const": "application/x-ndjson"},
            "content_sha256": SHA256,
            "content_bytes": {"type": "integer", "minimum": 0},
            "chain_algorithm": {"type": "string"},
            "chain_start": SHA256,
            "chain_end": SHA256,
            "fields": {"type": "array", "items": {"type": "string"}},
            "seal": closed(
                {
                    "algorithm": {"const": "HMAC-SHA256"},
                    "key_id": {"type": "string", "pattern": "^[0-9a-f]{12}$"},
                    "value": SHA256,
                },
                ["algorithm", "key_id", "value"],
            ),
        },
        [
            "format",
            "export_id",
            "tenant_id",
            "window_start",
            "window_end",
            "purpose",
            "generated_at",
            "generated_by",
            "page",
            "event_count",
            "denial_count",
            "complete",
            "media_type",
            "content_sha256",
            "content_bytes",
            "chain_algorithm",
            "chain_start",
            "chain_end",
            "fields",
            "seal",
        ],
    )
    schemas["AuditExport"] = closed(
        {
            "manifest": {"$ref": "#/components/schemas/AuditExportManifest"},
            "content": {"type": "string"},
            "next_cursor": {"type": ["string", "null"], "maxLength": 4096},
        },
        ["manifest", "content", "next_cursor"],
    )
    entry = deepcopy(paths[PREFIX + "uploads"])
    post = entry["post"]
    post.update(
        operationId=OPERATION,
        summary="create audit export",
        description="One bounded page (at most 1000 events, window at most 366 days and not in the future) "
        "of the tenant's audit events and collapsed access denials (v0.27) ordered by occurrence, as JSON Lines with a SHA-256 hash chain, a "
        "manifest with the content digest and an HMAC-SHA256 platform seal. Requires audit.export at TENANT "
        "scope for the stated purpose and authentication within 300 seconds; the export is itself audited. "
        "Identifiers, codes and digests only: no payload, secret or sealed value is exported.",
        **{"x-capability": CAPABILITY, "x-audit-required": True, "x-contract-version": VERSION},
    )
    post["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AuditExport"
    }
    post["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AuditExportRequest"
    }
    paths[PREFIX + ROUTE] = {"parameters": entry["parameters"], "post": post}
    policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != OPERATION]
    policy["operations"].append(
        {
            "operation_id": OPERATION,
            "method": "POST",
            "path": PREFIX + ROUTE,
            "capability": CAPABILITY,
            "role_templates": ROLES,
            "scope": "tenant; explicit TENANT-scope grant required",
            "fresh_assurance_seconds": 300,
            "independence_required": False,
            "purpose_required": True,
            "field_filter_required": True,
            "state_guard": "The request names a purpose; only a TENANT-scope audit.export grant without a purpose "
            "or with that purpose authorises it. Bounded window and page; identifiers, codes and digests only; "
            "the export and its manifest digest are recorded (audit event and receipt).",
            "audit": True,
        }
    )
