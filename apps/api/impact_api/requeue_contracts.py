"""Closed control-plane contract for the operator re-queue of held or DEAD deliveries (platform API 1.5.0)."""

from jsonschema import Draft202012Validator, FormatChecker
from .domain import DomainError
from .tenant_contracts import UUID, obj, text

DATE = {"type": "string", "format": "date-time"}
NULL_DATE = {"anyOf": [DATE, {"type": "null"}]}
# The row's revision is its lease generation, as a decimal string (it is advanced by every claim,
# re-queue and release, so a stale view never moves a row).
REVISION = {"type": "string", "pattern": "^(0|[1-9][0-9]{0,18})$"}
ACTIONS = {"requeue", "release"}
CHANNELS = {"enum": ["IN_APP", "EMAIL"]}
TEMPLATES = {"enum": ["IN_APP_NOTICE", "MEMBER_INVITATION", "RECOVERY_CHANNEL_VERIFICATION"]}
STATES = {"enum": ["PENDING", "LEASED", "SENT", "DEAD", "SUPERSEDED"]}
ERROR_CLASS = {"anyOf": [{"type": "string", "pattern": "^[A-Z][A-Z0-9_]{0,63}$"}, {"type": "null"}]}
ACTION = obj({"operation_id": UUID, "expected_revision": REVISION, "data": obj({"reason": text(1000)})})
ITEM = obj(
    {
        "tenant_id": UUID,
        "operating_name": text(200),
        "lifecycle_state": text(20),
        "event_id": UUID,
        "channel": CHANNELS,
        "template": TEMPLATES,
        "state": STATES,
        "held": {"type": "boolean"},
        "attempts": {"type": "integer", "minimum": 0},
        "last_error_class": ERROR_CLASS,
        "last_attempt_at": NULL_DATE,
        "completed_at": NULL_DATE,
        "revision": REVISION,
        "permitted_actions": {"type": "array", "items": {"enum": sorted(ACTIONS)}, "uniqueItems": True},
    }
)
DIRECTORY = obj({"items": {"type": "array", "maxItems": 50, "items": ITEM}})
RECEIPT = obj(
    {
        "operation_id": UUID,
        "tenant_id": UUID,
        "event_id": UUID,
        "action": {"enum": sorted(ACTIONS)},
        "state": STATES,
        "held": {"type": "boolean"},
        "attempts": {"type": "integer", "minimum": 0},
        "previous_state": STATES,
        "previous_attempts": {"type": "integer", "minimum": 0},
        "previous_error_class": ERROR_CLASS,
        "revision": REVISION,
        "reason": text(1000),
    }
)


def validate_body(body):
    if not Draft202012Validator(ACTION, format_checker=FormatChecker()).is_valid(body):
        raise DomainError("VALIDATION_FAILED")


def add_paths(paths, operation):
    get = operation("list_delivery_attention", response_schema=DIRECTORY)
    get["parameters"] = [{"name": "tenant_id", "in": "query", "required": False, "schema": UUID}]
    paths["/v1/platform/deliveries"] = {"get": get}
    for action in sorted(ACTIONS):
        paths["/v1/platform/tenants/{tenant_id}/deliveries/{event_id}/actions/" + action] = {
            "parameters": [
                {"name": "tenant_id", "in": "path", "required": True, "schema": UUID},
                {"name": "event_id", "in": "path", "required": True, "schema": UUID},
            ],
            "post": operation("delivery_" + action, ACTION, RECEIPT),
        }
