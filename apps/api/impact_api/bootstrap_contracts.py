"""Closed, separate control-plane contract for reviewed initial authority."""

from jsonschema import Draft202012Validator, FormatChecker
from .domain import DomainError
from .tenant_contracts import UUID, ACTION, obj, text

# initial-access-v2 (v0.26a): the role bundles of bootstrap_profile.json besides TENANT_ADMIN. The
# first five were the whole of initial-access-v1; a v1 manifest still validates (it names no other
# role and carries no purpose_bound list).
ROLE_NAMES = [
    "AUTHOR",
    "REVIEWER",
    "PROGRAMME_MANAGER",
    "ANALYST",
    "EXTERNAL",
    "MEL_ADMIN",
    "DATA_STEWARD",
    "ENUMERATOR",
    "PRIVACY",
    "AUDIT_READER",
    # US-MP-03 (build 0.38.0, profile registered by migration 0042): the Operations Head persona.
    "FINANCE",
]
CAPABILITY_LIST = {"type": "array", "items": text(64), "uniqueItems": True, "maxItems": 200}
MANIFEST = obj(
    {
        "version": text(80),
        "roles": obj({name: CAPABILITY_LIST for name in ["TENANT_ADMIN", *ROLE_NAMES]}, ["TENANT_ADMIN"]),
        # Purpose-required capabilities: inside the delegation ceiling, never in a role template.
        "purpose_bound": CAPABILITY_LIST,
    },
    ["version", "roles"],
)
CREATE = obj(
    {
        "operation_id": UUID,
        "expected_revision": UUID,
        "data": obj(
            {
                "second_identity_id": UUID,
                "profile_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "role_names": {
                    "type": "array",
                    "items": {"enum": ROLE_NAMES},
                    "minItems": 1,
                    "maxItems": len(ROLE_NAMES),
                    "uniqueItems": True,
                },
                "expires_at": {"type": "string", "format": "date-time"},
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
        "owner_identity_id": UUID,
        "second_identity_id": UUID,
        "state": {"enum": ["Requested", "Accepted", "Applied", "Rejected", "Cancelled"]},
        "manifest": MANIFEST,
        "profile_hash": text(64),
        "reason": text(1000),
        "expires_at": {"type": "string", "format": "date-time"},
        "review_expires_at": {"type": "string", "format": "date-time"},
        "scope_id": {"anyOf": [UUID, {"type": "null"}]},
        "second_membership_id": {"anyOf": [UUID, {"type": "null"}]},
    }
)
DIRECTORY = obj(
    {
        "operator": {"type": "boolean"},
        "profile": MANIFEST,
        "profile_hash": text(64),
        "items": {"type": "array", "items": ITEM, "maxItems": 50},
        "next_cursor": {"anyOf": [UUID, {"type": "null"}]},
    }
)
RECEIPT = obj({**ITEM["properties"], "operation_id": UUID})


def validate_body(body, create=False):
    if list(
        Draft202012Validator(CREATE if create else ACTION, format_checker=FormatChecker()).iter_errors(body)
    ):
        raise DomainError("VALIDATION_FAILED")


def add_paths(paths, operation):
    get = operation("list_initial_access", response_schema=DIRECTORY)
    get["parameters"] = [{"name": "cursor", "in": "query", "schema": UUID}]
    paths["/v1/platform/access-bootstraps"] = {"get": get}
    paths["/v1/platform/tenants/{tenant_id}/access-bootstrap"] = {
        "parameters": [{"name": "tenant_id", "in": "path", "required": True, "schema": UUID}],
        "post": operation("request_initial_access", CREATE, RECEIPT),
    }
    for action in sorted(ACTIONS):
        paths["/v1/platform/access-bootstraps/{request_id}/actions/" + action] = {
            "parameters": [{"name": "request_id", "in": "path", "required": True, "schema": UUID}],
            "post": operation("initial_access_" + action, ACTION, RECEIPT),
        }
