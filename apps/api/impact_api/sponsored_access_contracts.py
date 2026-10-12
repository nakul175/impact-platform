"""US-CM-02 closed contracts for accepted sponsored access."""

from copy import deepcopy
from .measurement_contracts import closed, text_field

VERSION = "1.65.0"
UUID = {"type": "string", "format": "uuid"}
ROOT = "/v1/tenants/{tenant_id}/sponsored-cohorts"
ACCESS = "/v1/tenants/{tenant_id}/sponsored-access"
IMPLEMENTED = [
    ("post", "sponsored-cohorts"),
    ("post", "sponsored-access/{enrolment_id}/actions/accept"),
    ("get", "sponsored-access"),
]


def operation(operation_id, summary, capability, request=None, response=None):
    item = {
        "operationId": operation_id,
        "summary": summary,
        "x-capability": capability,
        "x-contract-version": VERSION,
        "responses": {
            "200": {
                "description": "Succeeded",
                "content": {"application/json": {"schema": response or {"type": "object"}}},
            }
        },
    }
    if request:
        item["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": request}},
        }
    return item


def augment(spec, policy):
    s = spec["components"]["schemas"]
    s["SponsoredCohortCreate"] = closed(
        {
            "operation_id": deepcopy(UUID),
            "title": text_field(200),
            "duration_days": {"type": "integer", "minimum": 1, "maximum": 3660},
            "budget": {
                "type": "string",
                "pattern": "^(?=.*[1-9])(?:0|[1-9][0-9]{0,25})(?:\\.[0-9]{1,12})?$",
            },
            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
            "terms_version": text_field(100),
            "grantee_tenant_ids": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1000,
                "uniqueItems": True,
                "items": deepcopy(UUID),
            },
        },
        [
            "operation_id",
            "title",
            "duration_days",
            "budget",
            "currency",
            "terms_version",
            "grantee_tenant_ids",
        ],
    )
    s["SponsoredAccessAccept"] = closed(
        {"operation_id": deepcopy(UUID), "terms_version": text_field(100)},
        ["operation_id", "terms_version"],
    )
    enrolment = closed(
        {"enrolment_id": deepcopy(UUID), "grantee_tenant_id": deepcopy(UUID), "status": {"const": "INVITED"}},
        ["enrolment_id", "grantee_tenant_id", "status"],
    )
    s["SponsoredCohort"] = closed(
        {
            "cohort_id": deepcopy(UUID),
            "title": text_field(200),
            "duration_days": {"type": "integer"},
            "budget": {"type": "string"},
            "currency": {"type": "string"},
            "terms_version": text_field(100),
            "enrolments": {"type": "array", "items": enrolment},
        },
        ["cohort_id", "title", "duration_days", "budget", "currency", "terms_version", "enrolments"],
    )
    entitlement = closed(
        {
            "enrolment_id": deepcopy(UUID),
            "sponsor_tenant_id": deepcopy(UUID),
            "status": {"const": "ACCEPTED"},
            "access_starts_at": {"type": "string", "format": "date-time"},
            "access_ends_at": {"type": "string", "format": "date-time"},
            "no_charge": {"const": True},
            "data_authority_granted": {"const": False},
        },
        [
            "enrolment_id",
            "sponsor_tenant_id",
            "status",
            "access_starts_at",
            "access_ends_at",
            "no_charge",
            "data_authority_granted",
        ],
    )
    s["SponsoredAccessEntitlement"] = entitlement
    s["SponsoredAccessList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 1000,
                "items": {"$ref": "#/components/schemas/SponsoredAccessEntitlement"},
            }
        },
        ["items"],
    )
    tenant_parameters = deepcopy(spec["paths"]["/v1/tenants/{tenant_id}/subscriptions"]["parameters"])
    enrolment_parameters = tenant_parameters + [
        {"name": "enrolment_id", "in": "path", "required": True, "schema": deepcopy(UUID)}
    ]
    spec["paths"][ROOT] = {
        "parameters": tenant_parameters,
        "post": operation(
            "create_sponsored_cohort",
            "Create a named sponsored cohort",
            "subscription.admin",
            {"$ref": "#/components/schemas/SponsoredCohortCreate"},
            {"$ref": "#/components/schemas/SponsoredCohort"},
        ),
    }
    spec["paths"][ACCESS + "/{enrolment_id}/actions/accept"] = {
        "parameters": enrolment_parameters,
        "post": operation(
            "accept_sponsored_access",
            "Accept exact sponsorship terms",
            "subscription.admin",
            {"$ref": "#/components/schemas/SponsoredAccessAccept"},
            {"$ref": "#/components/schemas/SponsoredAccessEntitlement"},
        ),
    }
    spec["paths"][ACCESS] = {
        "parameters": tenant_parameters,
        "get": operation(
            "list_sponsored_access",
            "List current accepted no-charge access",
            "subscriptions.read",
            response={"$ref": "#/components/schemas/SponsoredAccessList"},
        ),
    }
    for method, path, op_id, capability, roles in [
        (
            "POST",
            ROOT,
            "create_sponsored_cohort",
            "subscription.admin",
            ["TENANT_ADMIN", "PROGRAMME_MANAGER"],
        ),
        (
            "POST",
            ACCESS + "/{enrolment_id}/actions/accept",
            "accept_sponsored_access",
            "subscription.admin",
            ["TENANT_ADMIN"],
        ),
        (
            "GET",
            ACCESS,
            "list_sponsored_access",
            "subscriptions.read",
            ["TENANT_ADMIN", "PROGRAMME_MANAGER", "ANALYST"],
        ),
    ]:
        policy["operations"] = [row for row in policy["operations"] if row["operation_id"] != op_id]
        policy["operations"].append(
            {
                "operation_id": op_id,
                "method": method,
                "path": path,
                "capability": capability,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if method == "POST" else None,
                "audit": method == "POST",
                "state_guard": "Acceptance is grantee-tenant bound, exact-terms, time-bounded and no-charge; it grants no data authority.",
            }
        )
