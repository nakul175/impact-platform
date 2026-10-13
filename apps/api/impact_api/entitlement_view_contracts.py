"""US-CM-03 effective entitlement view contract."""

from copy import deepcopy
from .measurement_contracts import closed, text_field

VERSION = "1.66.0"
UUID = {"type": "string", "format": "uuid"}
ROOT = "/v1/tenants/{tenant_id}/effective-entitlements"
IMPLEMENTED = [("get", "effective-entitlements")]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    source = closed(
        {
            "source_type": {"enum": ["DIRECT_SUBSCRIPTION", "SPONSORSHIP"]},
            "source_id": deepcopy(UUID),
            "source_tenant_id": deepcopy(UUID),
            "reference": text_field(100),
            "chargeable": {"type": "boolean"},
        },
        ["source_type", "source_id", "source_tenant_id", "reference", "chargeable"],
    )
    item = closed(
        {
            "entitlement": {"const": "PLATFORM_ACCESS"},
            "sources": {"type": "array", "minItems": 1, "maxItems": 2000, "items": source},
            "charge_count": {"type": "integer", "minimum": 0, "maximum": 1},
            "charge_source_id": {"oneOf": [deepcopy(UUID), {"type": "null"}]},
            "duplicate_charge_prevented": {"type": "boolean"},
        },
        ["entitlement", "sources", "charge_count", "charge_source_id", "duplicate_charge_prevented"],
    )
    schemas["EffectiveEntitlementList"] = closed(
        {"items": {"type": "array", "maxItems": 1, "items": item}}, ["items"]
    )
    parameters = deepcopy(spec["paths"]["/v1/tenants/{tenant_id}/subscriptions"]["parameters"])
    spec["paths"][ROOT] = {
        "parameters": parameters,
        "get": {
            "operationId": "list_effective_entitlements",
            "summary": "Combine direct and sponsored platform access without duplicate charges",
            "x-capability": "subscriptions.read",
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "Source-labelled effective entitlements",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/EffectiveEntitlementList"}
                        }
                    },
                }
            },
        },
    }
    policy["operations"] = [
        row for row in policy["operations"] if row["operation_id"] != "list_effective_entitlements"
    ]
    policy["operations"].append(
        {
            "operation_id": "list_effective_entitlements",
            "method": "GET",
            "path": ROOT,
            "capability": "subscriptions.read",
            "role_templates": ["TENANT_ADMIN", "PROGRAMME_MANAGER", "ANALYST"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
            "state_guard": "Every effective entitlement has explicit direct/sponsor sources; one entitlement has at most one charge source.",
        }
    )
