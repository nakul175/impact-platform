"""US-CM-08 local-currency tax invoice contracts."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.68.0"
UUID = {"type": "string", "format": "uuid"}
COUNTRY = {"type": "string", "pattern": "^[A-Z]{2}$"}
MONEY = {"type": "string", "pattern": "^(?=.*[1-9])(?:0|[1-9][0-9]{0,25})(?:\\.[0-9]{1,12})?$"}
RATE = {"type": "string", "pattern": "^(?:0|[1-9][0-9]{0,2})(?:\\.[0-9]{1,5})?$"}
IMPLEMENTED = [
    ("post", "billing-profile"),
    ("post", "commercial-invoices/{invoice_id}/actions/issue"),
    ("get", "commercial-invoices/{invoice_id}"),
]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    schemas["BillingProfileConfigure"] = closed(
        {"operation_id": deepcopy(UUID), "country_code": COUNTRY}, ["operation_id", "country_code"]
    )
    schemas["BillingProfileResult"] = closed(
        {
            "country_code": COUNTRY,
            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
            "tax_name": {"type": "string", "minLength": 1, "maxLength": 32},
            "tax_rate": RATE,
            "configured_at": {"type": "string", "format": "date-time"},
        },
        ["country_code", "currency", "tax_name", "tax_rate", "configured_at"],
    )
    schemas["CommercialInvoiceIssue"] = closed({"operation_id": deepcopy(UUID)}, ["operation_id"])
    schemas["CommercialInvoiceIssued"] = closed(
        {
            "invoice_id": deepcopy(UUID),
            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
            "country_code": COUNTRY,
            "subtotal": MONEY,
            "tax_name": {"type": "string", "minLength": 1, "maxLength": 32},
            "tax_rate": RATE,
            "tax_amount": MONEY,
            "total": MONEY,
            "issued_at": {"type": "string", "format": "date-time"},
        },
        [
            "invoice_id",
            "currency",
            "country_code",
            "subtotal",
            "tax_name",
            "tax_rate",
            "tax_amount",
            "total",
            "issued_at",
        ],
    )
    tenant = deepcopy(spec["paths"]["/v1/tenants/{tenant_id}/subscriptions"]["parameters"])
    invoice = tenant + [{"name": "invoice_id", "in": "path", "required": True, "schema": deepcopy(UUID)}]
    spec["paths"]["/v1/tenants/{tenant_id}/billing-profile"] = {
        "parameters": tenant,
        "post": _operation(
            "configure_billing_profile",
            "Configure an active billing market",
            "subscription.admin",
            "BillingProfileConfigure",
            "BillingProfileResult",
        ),
    }
    issue = _operation(
        "issue_commercial_invoice",
        "Issue an invoice with a pinned local tax snapshot",
        "subscription.admin",
        "CommercialInvoiceIssue",
        "CommercialInvoiceIssued",
    )
    spec["paths"]["/v1/tenants/{tenant_id}/commercial-invoices/{invoice_id}/actions/issue"] = {
        "parameters": invoice,
        "post": issue,
    }
    read = _operation(
        "read_commercial_invoice",
        "Read an issued local-currency tax invoice",
        "subscriptions.read",
        None,
        "CommercialInvoiceIssued",
    )
    spec["paths"]["/v1/tenants/{tenant_id}/commercial-invoices/{invoice_id}"] = {
        "parameters": invoice,
        "get": read,
    }
    for method, path, op, cap, roles, audit in [
        (
            "POST",
            "billing-profile",
            "configure_billing_profile",
            "subscription.admin",
            ["TENANT_ADMIN"],
            True,
        ),
        (
            "POST",
            "commercial-invoices/{invoice_id}/actions/issue",
            "issue_commercial_invoice",
            "subscription.admin",
            ["TENANT_ADMIN"],
            True,
        ),
        (
            "GET",
            "commercial-invoices/{invoice_id}",
            "read_commercial_invoice",
            "subscriptions.read",
            ["TENANT_ADMIN", "PROGRAMME_MANAGER"],
            False,
        ),
    ]:
        policy["operations"] = [row for row in policy["operations"] if row["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method,
                "path": "/v1/tenants/{tenant_id}/" + path,
                "capability": cap,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if method == "POST" else None,
                "audit": audit,
                "state_guard": "Only active configured markets; INR requires a pinned positive GST line before immutable issuance.",
            }
        )


def _operation(operation_id, summary, capability, request, response):
    node = {
        "operationId": operation_id,
        "summary": summary,
        "x-capability": capability,
        "x-contract-version": VERSION,
        "responses": {
            "200": {
                "description": "Success",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
            }
        },
    }
    if request:
        node["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
        }
    return node
