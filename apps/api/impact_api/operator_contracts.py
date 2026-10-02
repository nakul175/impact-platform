"""Closed control-plane contracts for operator onboarding and sign-in accounts (v0.26a, gap A3).

An operator nominates a person by e-mail for the platform operator role; the person who signs in with
that verified address (a different natural person) accepts with fresh MFA. An operator, or a tenant
owner for a pending invitation of their tenant, can create that person's sign-in account at the
identity provider; the one-time password appears once, in the live response only.
"""

from jsonschema import Draft202012Validator, FormatChecker
from .domain import DomainError
from .tenant_contracts import UUID, ACTION, obj, text

NULL_UUID = {"anyOf": [UUID, {"type": "null"}]}
DATE = {"type": "string", "format": "date-time"}
NULL_DATE = {"anyOf": [DATE, {"type": "null"}]}
EMAIL = {"type": "string", "format": "email", "maxLength": 254}
NOMINATE = obj(
    {
        "operation_id": UUID,
        "data": obj({"email": EMAIL, "operator_expires_at": DATE, "reason": text(1000)}),
    }
)
NOMINATION_ACTIONS = {"accept", "decline", "cancel"}
ACCOUNT_CREATE = obj(
    {
        "operation_id": UUID,
        "data": obj(
            {
                "email": EMAIL,
                "first_name": text(80),
                "last_name": text(80),
                "nomination_id": NULL_UUID,
                "tenant_id": NULL_UUID,
                "reason": text(1000),
            }
        ),
    }
)
ACCOUNT_REISSUE = obj(
    {
        "operation_id": UUID,
        "expected_revision": UUID,
        "data": obj({"email": EMAIL, "reason": text(1000)}),
    }
)
ACCOUNT_ACTIONS = {"reissue"}
# Operator lifecycle (v0.27): renewal before expiry and deactivation, each by a different active
# operator with fresh assurance and a reason, against the exact operator revision.
RENEW = obj(
    {
        "operation_id": UUID,
        "expected_revision": UUID,
        "data": obj({"expires_at": DATE, "reason": text(1000)}),
    }
)
OPERATOR_ACTIONS = {"renew", "deactivate"}
CHANGE = obj(
    {
        "change_id": UUID,
        "operator_identity_id": UUID,
        "action": {"enum": ["renew", "deactivate"]},
        "actor_identity_id": UUID,
        "actor_name": text(200),
        "reason": text(1000),
        "previous_expires_at": DATE,
        "expires_at": DATE,
        "created_at": DATE,
    }
)
NOMINATION = obj(
    {
        "nomination_id": UUID,
        "revision_id": UUID,
        "state": {"enum": ["Nominated", "Accepted", "Declined", "Cancelled", "Expired"]},
        "email_mask": text(254),
        "nominated_by": UUID,
        "nominator_name": text(200),
        "operator_expires_at": DATE,
        "expires_at": DATE,
        "reason": text(1000),
        "nominee_identity_id": NULL_UUID,
        "accepted_at": NULL_DATE,
        # Whether the nominee's sign-in account was created by the nominating operator, who then saw
        # its one-time password (shown to the reviewer and recorded in the acceptance event).
        "account_created_by_nominator": {"type": "boolean"},
    }
)
OPERATOR = obj(
    {
        "identity_id": UUID,
        "revision_id": UUID,
        "display_name": text(200),
        "email_mask": {"anyOf": [text(254), {"type": "null"}]},
        "active": {"type": "boolean"},
        # Active: active and unexpired; Expired: active flag but past expiry; Deactivated: flag off.
        "state": {"enum": ["Active", "Expired", "Deactivated"]},
        "expires_at": DATE,
        "updated_at": DATE,
        "authority_reference": text(300),
    }
)
OPERATOR_RECEIPT = obj({**OPERATOR["properties"], "operation_id": UUID, "change_id": UUID})
IDENTITY = obj(
    {
        "identity_id": UUID,
        "display_name": text(200),
        "email_mask": {"anyOf": [text(254), {"type": "null"}]},
        "signed_in": {"type": "boolean"},
        "operator": {"type": "boolean"},
    }
)
ACCOUNT = obj(
    {
        "account_id": UUID,
        "revision_id": UUID,
        "email_mask": text(254),
        "identity_id": NULL_UUID,
        "created_by": UUID,
        "tenant_id": NULL_UUID,
        "nomination_id": NULL_UUID,
        "provider_created": {"type": "boolean"},
        "credentials_issued": {"type": "integer", "minimum": 0},
        "created_at": DATE,
        "last_issued_at": NULL_DATE,
    }
)
DIRECTORY = obj(
    {
        "operator": {"type": "boolean"},
        "identity_id": UUID,
        "accounts_enabled": {"type": "boolean"},
        "operators": {"type": "array", "maxItems": 200, "items": OPERATOR},
        "changes": {"type": "array", "maxItems": 100, "items": CHANGE},
        "nominations": {"type": "array", "maxItems": 100, "items": NOMINATION},
        "identities": {"type": "array", "maxItems": 200, "items": IDENTITY},
        "accounts": {"type": "array", "maxItems": 100, "items": ACCOUNT},
    }
)
NOMINATION_RECEIPT = obj({**NOMINATION["properties"], "operation_id": UUID})
ACCOUNT_RECEIPT = obj(
    {
        **ACCOUNT["properties"],
        "operation_id": UUID,
        # Present only in the response that created or reissued the credential; null on a replay
        # (the receipt never holds it) and when an existing account was only registered.
        "temporary_password": {
            "anyOf": [{"type": "string", "minLength": 12, "maxLength": 64}, {"type": "null"}]
        },
        "password_shown": {"type": "boolean"},
        "sign_in_url": {"type": "string", "maxLength": 2000},
    }
)


def validate_body(body, schema):
    if not Draft202012Validator(schema, format_checker=FormatChecker()).is_valid(body):
        raise DomainError("VALIDATION_FAILED")


def add_paths(paths, operation):
    paths["/v1/platform/operators"] = {"get": operation("list_platform_operators", response_schema=DIRECTORY)}
    for action in sorted(OPERATOR_ACTIONS):
        paths["/v1/platform/operators/{identity_id}/actions/" + action] = {
            "parameters": [{"name": "identity_id", "in": "path", "required": True, "schema": UUID}],
            "post": operation(
                action + "_platform_operator", RENEW if action == "renew" else ACTION, OPERATOR_RECEIPT
            ),
        }
    paths["/v1/platform/operator-nominations"] = {
        "post": operation("nominate_platform_operator", NOMINATE, NOMINATION_RECEIPT)
    }
    for action in sorted(NOMINATION_ACTIONS):
        paths["/v1/platform/operator-nominations/{nomination_id}/actions/" + action] = {
            "parameters": [{"name": "nomination_id", "in": "path", "required": True, "schema": UUID}],
            "post": operation("operator_nomination_" + action, ACTION, NOMINATION_RECEIPT),
        }
    paths["/v1/platform/accounts"] = {
        "post": operation("create_provider_account", ACCOUNT_CREATE, ACCOUNT_RECEIPT)
    }
    paths["/v1/platform/accounts/{account_id}/actions/reissue"] = {
        "parameters": [{"name": "account_id", "in": "path", "required": True, "schema": UUID}],
        "post": operation("reissue_provider_account", ACCOUNT_REISSUE, ACCOUNT_RECEIPT),
    }
