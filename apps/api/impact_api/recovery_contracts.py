"""Closed recovery-contact enrolment contracts; no account recovery bypass."""

from jsonschema import Draft202012Validator, FormatChecker
from .domain import DomainError
from .tenant_contracts import UUID, ACTION, RECOVERY_STATUS, obj, text

NULL_UUID = {"anyOf": [UUID, {"type": "null"}]}
DATE = {"type": "string", "format": "date-time"}
CREATE = obj(
    {
        "operation_id": UUID,
        "expected_revision": UUID,
        "data": obj(
            {
                "nominee_identity_id": UUID,
                "expected_contact_revision": NULL_UUID,
                "expires_at": DATE,
                "reason": text(1000),
            }
        ),
    }
)
ACTIONS = {"verify", "approve", "reject", "cancel", "decline", "revoke"}
# Channel verification (v0.16): the nominee proves control of the registered mailbox with a
# single-use code sent by the worker. Evidence only; eligibility and permissions are unchanged.
CHANNEL_REQUEST = obj(
    {
        "operation_id": UUID,
        "expected_revision": UUID,
        "data": obj({"email": {"type": "string", "format": "email", "maxLength": 254}, "reason": text(1000)}),
    }
)
CHANNEL_CONFIRM = obj(
    {
        "operation_id": UUID,
        "expected_revision": UUID,
        "data": obj(
            {"challenge_id": UUID, "code": {"type": "string", "pattern": "^[0-9]{8}$"}, "reason": text(1000)}
        ),
    }
)
CHANNEL_ACTIONS = {"channel-request": CHANNEL_REQUEST, "channel-confirm": CHANNEL_CONFIRM}
CHANNEL = obj(
    {
        "state": {"enum": ["NONE", "PENDING", "VERIFIED", "EXPIRED", "FAILED", "SUPERSEDED"]},
        "challenge_id": NULL_UUID,
        "expires_at": {"anyOf": [DATE, {"type": "null"}]},
        "verified_at": {"anyOf": [DATE, {"type": "null"}]},
        "attempts_remaining": {"type": "integer", "minimum": 0, "maximum": 5},
    }
)
STATUS = RECOVERY_STATUS
ITEM = obj(
    {
        "contact_id": UUID,
        "tenant_id": UUID,
        "revision_id": UUID,
        "operating_name": text(200),
        "owner_identity_id": UUID,
        "nominee_identity_id": UUID,
        "state": {
            "enum": [
                "Nominated",
                "Verified",
                "Active",
                "Replaced",
                "Revoked",
                "Declined",
                "Cancelled",
                "Rejected",
            ]
        },
        "display_name": text(200),
        "email_mask": text(300),
        "reason": text(1000),
        "replaces_contact_id": NULL_UUID,
        "expires_at": DATE,
        "review_expires_at": DATE,
        "verified_at": {"anyOf": [DATE, {"type": "null"}]},
        "approved_at": {"anyOf": [DATE, {"type": "null"}]},
        "approved_by": NULL_UUID,
        "verification_method": {"const": "REGISTERED_IDENTITY_MFA"},
        "verification": STATUS,
        "channel_verification": CHANNEL,
    }
)
DIRECTORY = obj(
    {
        "operator": {"type": "boolean"},
        "items": {"type": "array", "maxItems": 50, "items": ITEM},
        "next_cursor": NULL_UUID,
    }
)
RECEIPT = obj({**ITEM["properties"], "operation_id": UUID})


def validate_body(body, create=False, action=None):
    schema = CREATE if create else CHANNEL_ACTIONS.get(action, ACTION)
    if not Draft202012Validator(schema, format_checker=FormatChecker()).is_valid(body):
        raise DomainError("VALIDATION_FAILED")


def add_paths(paths, operation):
    get = operation("list_recovery_contacts", response_schema=DIRECTORY)
    get["parameters"] = [{"name": "cursor", "in": "query", "schema": UUID}]
    paths["/v1/platform/recovery-contacts"] = {"get": get}
    paths["/v1/platform/tenants/{tenant_id}/recovery-contacts"] = {
        "parameters": [{"name": "tenant_id", "in": "path", "required": True, "schema": UUID}],
        "post": operation("nominate_recovery_contact", CREATE, RECEIPT),
    }
    for action in sorted(ACTIONS | set(CHANNEL_ACTIONS)):
        paths["/v1/platform/recovery-contacts/{contact_id}/actions/" + action] = {
            "parameters": [{"name": "contact_id", "in": "path", "required": True, "schema": UUID}],
            "post": operation(
                "recovery_contact_" + action.replace("-", "_"), CHANNEL_ACTIONS.get(action, ACTION), RECEIPT
            ),
        }
