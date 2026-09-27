"""Contracts for independently reviewed, recipient-controlled report publication."""

from copy import deepcopy

from .measurement_contracts import DATE, UUID, closed, text_field


SPECIAL_READS = {
    "reports/{object_id}/export.csv": (
        "export_report_package_csv",
        "text/csv",
        "reports.read",
    ),
    "publications/{object_id}/view": (
        "view_controlled_publication",
        "text/html",
        "publication.download",
    ),
    "publications/{object_id}/download.csv": (
        "download_controlled_publication_csv",
        "text/csv",
        "publication.download",
    ),
}
DIRECTORY_READS = {"publication-recipients": "list_publication_recipients"}


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"
    purposes = ["FUNDER_REPORTING", "PARTNER_REPORTING", "INTERNAL_OVERSIGHT"]

    schemas["ControlledPublicationRecipient"] = closed(
        {"membership_id": UUID, "allow_download": {"type": "boolean"}},
        ["membership_id", "allow_download"],
    )
    schemas["PublicationRecipientOption"] = closed(
        {"membership_id": UUID, "label": text_field(200), "external": {"type": "boolean"}},
        ["membership_id", "label", "external"],
    )
    schemas["PublicationRecipientList"] = closed(
        {
            "items": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/PublicationRecipientOption"},
                "maxItems": 500,
            }
        },
        ["items"],
    )
    recipients = {
        "type": "array",
        "items": {"$ref": "#/components/schemas/ControlledPublicationRecipient"},
        "minItems": 1,
        "maxItems": 100,
    }
    for name in ["DisclosureData", "DisclosureDraftData"]:
        properties = schemas[name]["properties"]
        properties["recipients"] = deepcopy(recipients)
        properties["purpose"] = {"enum": purposes}
        properties["public"] = {"const": False}
        properties.update(
            published_at=DATE,
            withdrawn_at=DATE,
            withdrawal_reason=text_field(2000),
        )

    request = schemas["CommandRequestDisclosureData"]
    request["properties"].update(
        recipients=deepcopy(recipients),
        purpose={"enum": purposes},
        public={"const": False},
        workflow_version=UUID,
    )
    if "workflow_version" not in request["required"]:
        request["required"].append("workflow_version")

    candidate = schemas["ReviewCandidate"]["properties"]
    if "Disclosure" not in candidate["kind"]["enum"]:
        candidate["kind"]["enum"].append("Disclosure")
        candidate["record"]["oneOf"].append({"$ref": "#/components/schemas/Disclosure"})

    def configure_action(action, capability, roles):
        path = prefix + "reports/{object_id}/actions/" + action
        entry = paths[path]["post"]
        entry.update(**{"x-contract-version": "1.9.0", "x-capability": capability})
        if "202" in entry["responses"]:
            entry["responses"]["200"] = entry["responses"].pop("202")
        entry["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/Receipt"
        }
        operation_id = "action_reports_" + action
        policy["operations"] = [item for item in policy["operations"] if item["operation_id"] != operation_id]
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": "POST",
                "path": path,
                "capability": capability,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": 300,
                "audit": True,
            }
        )

    configure_action("publish", "report.publish", ["MEL_ADMIN"])
    configure_action("withdraw", "report.withdraw", ["MEL_ADMIN", "PRIVACY"])

    for item in policy["operations"]:
        if item["operation_id"] in {"list_disclosures", "get_disclosures"}:
            item.update(
                role_templates=["MEL_ADMIN", "PRIVACY"],
                purpose_required=False,
                field_filter_required=False,
            )
        elif item["operation_id"] == "request_disclosure":
            item.update(
                role_templates=["AUTHOR", "PRIVACY"],
                purpose_required=False,
                fresh_assurance_seconds=None,
            )

    template = paths[prefix + "reports/{object_id}/export"]
    for route, (operation_id, media_type, capability) in SPECIAL_READS.items():
        entry = deepcopy(template)
        get = entry["get"]
        get.update(
            operationId=operation_id,
            summary=operation_id.replace("_", " "),
            **{"x-capability": capability, "x-contract-version": "1.9.0"},
        )
        get["responses"]["200"]["content"] = {
            media_type: {"schema": {"type": "string", "contentMediaType": media_type}}
        }
        paths[prefix + route] = entry
        policy["operations"] = [item for item in policy["operations"] if item["operation_id"] != operation_id]
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": "GET",
                "path": prefix + route,
                "capability": capability,
                "role_templates": [
                    "AUTHOR",
                    "REVIEWER",
                    "MEL_ADMIN",
                    "PROGRAMME_MANAGER",
                    "ANALYST",
                    "DATA_STEWARD",
                    "EXTERNAL",
                    "PRIVACY",
                ],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )

    directory = deepcopy(paths[prefix + "measurement-members"])
    directory["get"].update(
        operationId="list_publication_recipients",
        summary="List bounded eligible publication recipients",
        **{"x-capability": "disclosure.request", "x-contract-version": "1.9.0"},
    )
    directory["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/PublicationRecipientList"
    }
    paths[prefix + "publication-recipients"] = directory
    policy["operations"] = [
        item for item in policy["operations"] if item["operation_id"] != "list_publication_recipients"
    ]
    policy["operations"].append(
        {
            "operation_id": "list_publication_recipients",
            "method": "GET",
            "path": prefix + "publication-recipients",
            "capability": "disclosure.request",
            "role_templates": ["AUTHOR", "PRIVACY"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )

    spec["info"]["version"] = policy["version"] = "1.9.0"
