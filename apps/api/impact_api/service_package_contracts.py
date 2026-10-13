"""US-CM-06 priced package and same-invoice purchase contracts."""

from copy import deepcopy
from .measurement_contracts import closed, text_field

VERSION = "1.67.0"
UUID = {"type": "string", "format": "uuid"}
ROOT = "service-packages"
PURCHASE = "subscriptions/{subscription_id}/service-packages"
IMPLEMENTED = [("get", ROOT), ("post", PURCHASE)]


def augment(spec, policy):
    s = spec["components"]["schemas"]
    package = closed(
        {
            "package_code": text_field(64),
            "title": text_field(200),
            "scope": text_field(2000),
            "price": {"type": "string", "pattern": "^(?=.*[1-9])[0-9]{1,26}(?:\\.[0-9]{1,12})?$"},
            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        },
        ["package_code", "title", "scope", "price", "currency"],
    )
    s["ServicePackageList"] = closed(
        {"items": {"type": "array", "minItems": 1, "maxItems": 100, "items": package}}, ["items"]
    )
    s["ServicePackagePurchase"] = closed(
        {"operation_id": deepcopy(UUID), "package_code": text_field(64)}, ["operation_id", "package_code"]
    )
    s["ServicePackagePurchaseResult"] = closed(
        {
            "invoice_id": deepcopy(UUID),
            "subscription_id": deepcopy(UUID),
            "item_id": deepcopy(UUID),
            **package["properties"],
            "quantity": {"const": 1},
            "separate_invoice_created": {"const": False},
        },
        [
            "invoice_id",
            "subscription_id",
            "item_id",
            *package["required"],
            "quantity",
            "separate_invoice_created",
        ],
    )
    tenant = deepcopy(spec["paths"]["/v1/tenants/{tenant_id}/subscriptions"]["parameters"])
    subscription = tenant + [
        {"name": "subscription_id", "in": "path", "required": True, "schema": deepcopy(UUID)}
    ]
    spec["paths"]["/v1/tenants/{tenant_id}/" + ROOT] = {
        "parameters": tenant,
        "get": {
            "operationId": "list_service_packages",
            "summary": "List fixed-fee packages with scope and price",
            "x-capability": "subscriptions.read",
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "Priced package catalogue",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/ServicePackageList"}}
                    },
                }
            },
        },
    }
    spec["paths"]["/v1/tenants/{tenant_id}/" + PURCHASE] = {
        "parameters": subscription,
        "post": {
            "operationId": "purchase_service_package",
            "summary": "Add a fixed-fee package to the subscription invoice",
            "x-capability": "subscription.admin",
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/ServicePackagePurchase"}}
                },
            },
            "responses": {
                "200": {
                    "description": "Package line on the subscription invoice",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ServicePackagePurchaseResult"}
                        }
                    },
                }
            },
        },
    }
    for method, path, op, cap, roles in [
        ("GET", ROOT, "list_service_packages", "subscriptions.read", ["TENANT_ADMIN", "PROGRAMME_MANAGER"]),
        ("POST", PURCHASE, "purchase_service_package", "subscription.admin", ["TENANT_ADMIN"]),
    ]:
        full = "/v1/tenants/{tenant_id}/" + path
        policy["operations"] = [r for r in policy["operations"] if r["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method,
                "path": full,
                "capability": cap,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if method == "POST" else None,
                "audit": method == "POST",
                "state_guard": "Only code-owned packages with nonblank scope and positive fixed price; purchase line uses the active subscription's single open invoice.",
            }
        )
