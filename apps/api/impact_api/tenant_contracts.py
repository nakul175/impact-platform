"""Closed control-plane contracts, separate from tenant capability delegation."""

from jsonschema import Draft202012Validator, FormatChecker
from .domain import DomainError
from .version import PLATFORM_API

UUID = {"type": "string", "format": "uuid"}


def obj(properties, required=None):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties) if required is None else required,
    }


def text(limit):
    return {"type": "string", "minLength": 1, "maxLength": limit, "pattern": "\\S"}


CREATE = obj(
    {
        "operation_id": UUID,
        "data": obj(
            {
                "owner_identity_id": UUID,
                "qualification_id": UUID,
                "operating_name": text(200),
                "reporting_zone": text(80),
                "retention_days": {"type": "integer", "minimum": 1, "maximum": 36500},
                "privacy_reference": text(300),
                "reason": text(1000),
            }
        ),
    }
)
ACTION = obj({"operation_id": UUID, "expected_revision": UUID, "data": obj({"reason": text(1000)})})
ACTIONS = {"accept-owner", "activate", "suspend", "reactivate", "begin-closure"}

RECOVERY_STATUS = obj(
    {
        "contact_id": {"anyOf": [UUID, {"type": "null"}]},
        "revision_id": {"anyOf": [UUID, {"type": "null"}]},
        "eligible": {"type": "boolean"},
        "reason": {
            "enum": [
                "VERIFIED",
                "NONE",
                "NOT_ACTIVE",
                "EXPIRED",
                "OWNER_CHANGED",
                "IDENTITY_CHANGED",
                "AUTHENTICATION_REVOKED",
            ]
        },
        "expires_at": {"anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}]},
    }
)

READINESS_KEYS = [
    "owner_accepted",
    "qualified_deployment",
    "qualification_unchanged",
    "environment_matches",
    "region_matches",
    "identity_policy_matches",
    "privacy_policy_matches",
    "retention_supported",
    "recovery_evidence_present",
    "owner_membership_active",
    "recovery_contact_verified",
]
TENANT = obj(
    {
        "tenant_id": UUID,
        "revision_id": UUID,
        "state": {"enum": ["Requested", "Provisioning", "Active", "Suspended", "Closing"]},
        "operating_name": text(200),
        "owner_identity_id": UUID,
        "region": text(80),
        "reporting_zone": text(80),
        "retention_days": {"type": "integer", "minimum": 1},
        "privacy_reference": text(300),
        "owner_expires_at": {"type": "string", "format": "date-time"},
        "readiness": obj({key: {"type": "boolean"} for key in READINESS_KEYS}),
        "recovery_contact": RECOVERY_STATUS,
        "impact": obj(
            {
                key: {"type": "integer", "minimum": 0}
                for key in ["unfinished_jobs", "active_schedules", "unsent_events", "retention_holds"]
            }
        ),
    }
)
RECEIPT = obj({**TENANT["properties"], "operation_id": UUID})
DIRECTORY = obj(
    {
        "operator": {"type": "boolean"},
        "items": {"type": "array", "maxItems": 50, "items": TENANT},
        "next_cursor": {"anyOf": [UUID, {"type": "null"}]},
        "qualifications": {
            "type": "array",
            "maxItems": 100,
            "items": obj(
                {
                    "qualification_id": UUID,
                    "region": text(80),
                    "environment": text(20),
                    "privacy_reference": text(300),
                    "retention_max_days": {"type": "integer", "minimum": 1},
                }
            ),
        },
    }
)


def openapi():
    from .bootstrap_contracts import add_paths
    from .metrics_contracts import add_paths as add_metrics_paths
    from .recovery_contracts import add_paths as add_recovery_paths
    from .renewal_contracts import add_paths as add_renewal_paths
    from .requeue_contracts import add_paths as add_requeue_paths
    from .worker_contracts import add_paths as add_worker_paths

    def operation(name, request_schema=None, response_schema=DIRECTORY):
        node = {
            "operationId": name,
            "security": [{"bearerAuth": []}, {"cookieAuth": []}],
            "description": "Control-plane authority or nominated identity; never tenant role inheritance. Cookie mutations require Origin and X-CSRF-Token. Mutations require fresh MFA assurance. Activation requires an independent natural identity.",
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {"application/json": {"schema": response_schema}},
                },
                "default": {
                    "description": "Structured domain error: code, message, retryable, correlation_id, permitted_actions, field_errors, optional reason_code."
                },
            },
        }
        if request_schema:
            node["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": request_schema}},
            }
        return node

    get = operation("list_tenant_lifecycle")
    get["parameters"] = [{"name": "cursor", "in": "query", "required": False, "schema": UUID}]
    paths = {"/v1/platform/tenants": {"get": get, "post": operation("request_tenant", CREATE, RECEIPT)}}
    for action in sorted(ACTIONS):
        paths["/v1/platform/tenants/{tenant_id}/actions/" + action] = {
            "parameters": [{"name": "tenant_id", "in": "path", "required": True, "schema": UUID}],
            "post": operation("tenant_" + action.replace("-", "_"), ACTION, RECEIPT),
        }
    add_paths(paths, operation)
    add_recovery_paths(paths, operation)
    add_renewal_paths(paths, operation)
    add_worker_paths(paths, operation)
    add_requeue_paths(paths, operation)
    add_metrics_paths(paths, operation)
    return {
        "openapi": "3.1.0",
        "info": {"title": "Impact control-plane API", "version": PLATFORM_API},
        "paths": paths,
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer"},
                "cookieAuth": {"type": "apiKey", "in": "cookie", "name": "__Host-impact_session"},
            }
        },
    }


def validate_body(body, create=False):
    errors = list(
        Draft202012Validator(CREATE if create else ACTION, format_checker=FormatChecker()).iter_errors(body)
    )
    if errors:
        raise DomainError("VALIDATION_FAILED")
    return body
