"""Closed, tenant-fenced control-plane contract for reviewed ceiling widening."""

from jsonschema import Draft202012Validator, FormatChecker

from .bootstrap_contracts import MANIFEST as PROFILE_MANIFEST
from .domain import DomainError
from .renewal_contracts import DATE, HASH, NULL_DATE, NULL_UUID, PRINCIPAL
from .tenant_contracts import ACTION, UUID, obj, text

ACTIONS = {"accept", "approve", "reject", "cancel"}
CAPABILITIES = {"type": "array", "items": text(64), "uniqueItems": True, "maxItems": 500}
CURSOR = {"type": "string", "minLength": 1, "maxLength": 4096}
NULL_CURSOR = {"anyOf": [CURSOR, {"type": "null"}]}
AUTHORITY_ROW = obj(
    {"authority_id": UUID, "principal_id": UUID, "capability": text(64), "scope_id": UUID, "expires_at": DATE}
)
PINNED_REVISION = obj({"object_id": UUID, "revision_id": UUID, "payload_sha256": HASH})
MANAGED_ROLE = obj(
    {
        "object_id": UUID,
        "revision_id": UUID,
        "payload_sha256": HASH,
        "state": text(30),
        "name": text(80),
    }
)
CURRENT_MANIFEST = obj(
    {
        "version": text(80),
        "authority_ids": {"type": "array", "items": UUID, "uniqueItems": True, "maxItems": 1000},
        "principals": {"type": "array", "items": PRINCIPAL, "minItems": 2, "maxItems": 2},
        "authority_rows": {"type": "array", "items": AUTHORITY_ROW, "maxItems": 1000},
        "grant_revisions": {"type": "array", "items": PINNED_REVISION, "maxItems": 1000},
        "membership_revisions": {"type": "array", "items": PINNED_REVISION, "minItems": 2, "maxItems": 2},
        "managed_roles": {"type": "array", "items": MANAGED_ROLE, "maxItems": 50},
        "source_request_id": UUID,
        "source_manifest": PROFILE_MANIFEST,
    }
)
CREATE = obj(
    {
        "operation_id": UUID,
        "expected_revision": UUID,
        "data": obj(
            {"second_identity_id": UUID, "authority_hash": HASH, "profile_hash": HASH, "reason": text(1000)}
        ),
    }
)
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
        "current_manifest": CURRENT_MANIFEST,
        "authority_hash": HASH,
        "profile_hash": HASH,
        "target_manifest": PROFILE_MANIFEST,
        "new_capabilities": CAPABILITIES,
        "review_expires_at": DATE,
        "accepted_at": NULL_DATE,
        "approved_by": NULL_UUID,
        "applied_at": NULL_DATE,
        "reason": text(1000),
    }
)
DIRECTORY = obj(
    {
        "operator": {"type": "boolean"},
        "items": {"type": "array", "items": ITEM, "maxItems": 50},
        "next_cursor": NULL_CURSOR,
    }
)
REASONS = [
    "AUTHORITY_UNAVAILABLE",
    "SECOND_ADMIN_UNAVAILABLE",
    "TENANT_NOT_ACTIVE",
    "TENANT_NOT_READY",
    "RENEWAL_PENDING",
    "ACCESS_UPGRADE_PENDING",
    "ACCESS_PROFILE_ALREADY_HELD",
    "ACCESS_PROFILE_INCOMPATIBLE",
    "ACCESS_PROFILE_NOT_REGISTERED",
    "ACCESS_PROFILE_ROLE_CONFLICT",
]
PREVIEW = obj(
    {
        "tenant_id": UUID,
        "tenant_revision": UUID,
        "owner_identity_id": UUID,
        "second_identity_id": NULL_UUID,
        "authority_hash": {"anyOf": [HASH, {"type": "null"}]},
        "profile_hash": HASH,
        "target_manifest": PROFILE_MANIFEST,
        "current_manifest": {"anyOf": [CURRENT_MANIFEST, {"type": "null"}]},
        "new_capabilities": CAPABILITIES,
        "upgradable": {"type": "boolean"},
        "reason_unavailable": {"anyOf": [{"enum": REASONS}, {"type": "null"}]},
    }
)
RECEIPT = obj({**ITEM["properties"], "operation_id": UUID})


def validate_body(body, create=False):
    if not Draft202012Validator(CREATE if create else ACTION, format_checker=FormatChecker()).is_valid(body):
        raise DomainError("VALIDATION_FAILED")


def add_paths(paths, operation):
    global_listing = operation("list_access_upgrade_inbox", response_schema=DIRECTORY)
    global_listing["parameters"] = [{"name": "cursor", "in": "query", "schema": CURSOR}]
    paths["/v1/platform/access-upgrades"] = {"get": global_listing}
    parameters = [{"name": "tenant_id", "in": "path", "required": True, "schema": UUID}]
    base = "/v1/platform/tenants/{tenant_id}"
    listing = operation("list_access_upgrades", response_schema=DIRECTORY)
    listing["parameters"] = [{"name": "cursor", "in": "query", "schema": CURSOR}]
    paths[base + "/access-upgrades"] = {"parameters": parameters, "get": listing}
    paths[base + "/access-upgrade-preview"] = {
        "parameters": parameters,
        "get": operation("get_access_upgrade_preview", response_schema=PREVIEW),
    }
    paths[base + "/access-upgrade"] = {
        "parameters": parameters,
        "post": operation("request_access_upgrade", CREATE, RECEIPT),
    }
    for action in sorted(ACTIONS):
        paths[base + "/access-upgrades/{request_id}/actions/" + action] = {
            "parameters": parameters
            + [{"name": "request_id", "in": "path", "required": True, "schema": UUID}],
            "post": operation("access_upgrade_" + action, ACTION, RECEIPT),
        }
