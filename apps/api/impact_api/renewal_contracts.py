"""Closed control-plane contract for reviewed renewal of delegated authority."""

from jsonschema import Draft202012Validator, FormatChecker
from .domain import DomainError
from .tenant_contracts import UUID, ACTION, obj, text

DATE = {"type": "string", "format": "date-time"}
NULL_UUID = {"anyOf": [UUID, {"type": "null"}]}
NULL_DATE = {"anyOf": [DATE, {"type": "null"}]}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
PRINCIPAL = obj(
    {
        "principal_id": UUID,
        "identity_id": UUID,
        "membership_id": UUID,
        "scope_id": UUID,
        "capabilities": {"type": "array", "items": text(64), "uniqueItems": True, "maxItems": 500},
        "expires_at": DATE,
        "assignment_ids": {"type": "array", "items": UUID, "uniqueItems": True, "maxItems": 50},
        "grant_ids": {"type": "array", "items": UUID, "uniqueItems": True, "maxItems": 500},
    }
)
MANIFEST = obj(
    {
        "version": text(80),
        "authority_ids": {"type": "array", "items": UUID, "uniqueItems": True, "maxItems": 1000},
        "principals": {"type": "array", "items": PRINCIPAL, "minItems": 2, "maxItems": 2},
    }
)
CREATE = obj(
    {
        "operation_id": UUID,
        "expected_revision": UUID,
        "data": obj(
            {
                "second_identity_id": UUID,
                "authority_hash": HASH,
                "expires_at": DATE,
                "reason": text(1000),
            }
        ),
    }
)
ACTIONS = {"accept", "approve", "reject", "cancel"}
ITEM = obj(
    {
        "request_id": UUID,
        "tenant_id": UUID,
        "revision_id": UUID,
        "operating_name": text(200),
        "bootstrap_request_id": UUID,
        "owner_identity_id": UUID,
        "second_identity_id": UUID,
        "state": {"enum": ["Requested", "Accepted", "Applied", "Rejected", "Cancelled"]},
        "manifest": MANIFEST,
        "authority_hash": HASH,
        "previous_expires_at": DATE,
        "expires_at": DATE,
        "review_expires_at": DATE,
        "reason": text(1000),
        "accepted_at": NULL_DATE,
        "approved_by": NULL_UUID,
        "applied_at": NULL_DATE,
    }
)
DIRECTORY = obj(
    {
        "operator": {"type": "boolean"},
        "items": {"type": "array", "items": ITEM, "maxItems": 50},
        "next_cursor": NULL_UUID,
    }
)
REASONS = [
    "AUTHORITY_UNAVAILABLE",
    "SECOND_ADMIN_UNAVAILABLE",
    "TENANT_NOT_ACTIVE",
    "TENANT_NOT_READY",
    "RENEWAL_PENDING",
    "ACCESS_UPGRADE_PENDING",
]
AUTHORITY = obj(
    {
        "tenant_id": UUID,
        "tenant_revision": UUID,
        "bootstrap_request_id": NULL_UUID,
        "owner_identity_id": UUID,
        "second_identity_id": NULL_UUID,
        "authority_hash": {"anyOf": [HASH, {"type": "null"}]},
        "earliest_expires_at": NULL_DATE,
        "principals": {"type": "array", "items": PRINCIPAL, "maxItems": 2},
        "renewable": {"type": "boolean"},
        "reason_unavailable": {"anyOf": [{"enum": REASONS}, {"type": "null"}]},
    }
)
RECEIPT = obj({**ITEM["properties"], "operation_id": UUID})


def validate_body(body, create=False):
    if not Draft202012Validator(CREATE if create else ACTION, format_checker=FormatChecker()).is_valid(body):
        raise DomainError("VALIDATION_FAILED")


def add_paths(paths, operation):
    get = operation("list_authority_renewals", response_schema=DIRECTORY)
    get["parameters"] = [{"name": "cursor", "in": "query", "schema": UUID}]
    paths["/v1/platform/authority-renewals"] = {"get": get}
    tenant = [{"name": "tenant_id", "in": "path", "required": True, "schema": UUID}]
    paths["/v1/platform/tenants/{tenant_id}/authority"] = {
        "parameters": tenant,
        "get": operation("get_delegated_authority", response_schema=AUTHORITY),
    }
    paths["/v1/platform/tenants/{tenant_id}/authority-renewal"] = {
        "parameters": tenant,
        "post": operation("request_authority_renewal", CREATE, RECEIPT),
    }
    for action in sorted(ACTIONS):
        paths["/v1/platform/authority-renewals/{request_id}/actions/" + action] = {
            "parameters": [{"name": "request_id", "in": "path", "required": True, "schema": UUID}],
            "post": operation("authority_renewal_" + action, ACTION, RECEIPT),
        }
