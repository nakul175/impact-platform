"""US-CM-09 organisation agreement coverage contracts."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.69.0"
UUID = {"type": "string", "format": "uuid"}
TEXT = {"type": "string", "minLength": 1, "maxLength": 500, "pattern": "\\S"}
IMPLEMENTED = [("post", "agreements"), ("get", "agreements")]


def augment(spec, policy):
    s = spec["components"]["schemas"]
    s["OrganisationAgreementConfigure"] = closed(
        {
            "operation_id": deepcopy(UUID),
            "master_agreement_reference": deepcopy(TEXT),
            "dpa_reference": deepcopy(TEXT),
            "effective_on": {"type": "string", "format": "date"},
            "partner_terms_flow_down_confirmed": {"const": True},
        },
        [
            "operation_id",
            "master_agreement_reference",
            "dpa_reference",
            "effective_on",
            "partner_terms_flow_down_confirmed",
        ],
    )
    deployment = closed(
        {
            "deployment_attestation_id": deepcopy(UUID),
            "plan_id": deepcopy(UUID),
            "solution_id": {"type": "string", "minLength": 1, "maxLength": 100},
            "agreement_revision_id": deepcopy(UUID),
        },
        ["deployment_attestation_id", "plan_id", "solution_id", "agreement_revision_id"],
    )
    properties = {
        "revision_id": deepcopy(UUID),
        "master_agreement_reference": deepcopy(TEXT),
        "dpa_reference": deepcopy(TEXT),
        "effective_on": {"type": "string", "format": "date"},
        "coverage_scope": {"const": "ALL_PLATFORM_SOLUTIONS"},
        "partner_terms_mode": {"const": "MASTER_AGREEMENT_FLOW_DOWN"},
        "separate_contract_required": {"const": False},
        "separate_dpa_required": {"const": False},
    }
    s["OrganisationAgreementResult"] = closed(properties, list(properties))
    s["OrganisationAgreementView"] = closed(
        {**properties, "deployments": {"type": "array", "maxItems": 1000, "items": deployment}},
        [*properties, "deployments"],
    )
    parameters = deepcopy(spec["paths"]["/v1/tenants/{tenant_id}/subscriptions"]["parameters"])
    path = "/v1/tenants/{tenant_id}/agreements"
    spec["paths"][path] = {
        "parameters": parameters,
        "post": _operation(
            "configure_organisation_agreement",
            "Record one master agreement and DPA bundle",
            "subscription.admin",
            "OrganisationAgreementConfigure",
            "OrganisationAgreementResult",
        ),
        "get": _operation(
            "read_organisation_agreements",
            "Read the single current agreement bundle and covered deployments",
            "subscriptions.read",
            None,
            "OrganisationAgreementView",
        ),
    }
    for method, op, cap, roles, audit in [
        ("POST", "configure_organisation_agreement", "subscription.admin", ["TENANT_ADMIN"], True),
        (
            "GET",
            "read_organisation_agreements",
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
                "path": path,
                "capability": cap,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if method == "POST" else None,
                "audit": audit,
                "state_guard": "One current bundle covers all platform solutions; deployment pins a revision and cannot request a separate contract or DPA.",
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
