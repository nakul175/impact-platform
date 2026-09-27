"""Contracts for independently approved frozen internal report packages."""

from copy import deepcopy

from .measurement_contracts import UUID, closed


SPECIAL_READS = {
    "reports/{object_id}/export": ("export_report_package", "reports.read"),
}


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"
    schemas["ReportPackageSubmitData"] = closed({"workflow_version": UUID}, ["workflow_version"])
    schemas["ReportPackageSubmit"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": {"$ref": "#/components/schemas/ReportPackageSubmitData"},
        },
        ["operation_id", "expected_revision", "data"],
    )
    submit_path = prefix + "reports/{object_id}/actions/submit"
    submit = paths[submit_path]["post"]
    submit["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ReportPackageSubmit"
    }
    if "202" in submit["responses"]:
        submit["responses"]["200"] = submit["responses"].pop("202")
    submit["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/Receipt"
    }
    submit.update(**{"x-contract-version": "1.7.0"})
    policy["operations"] = [
        item for item in policy["operations"] if item["operation_id"] != "action_reports_submit"
    ]
    policy["operations"].append(
        {
            "operation_id": "action_reports_submit",
            "method": "POST",
            "path": submit_path,
            "capability": "report.submit",
            "role_templates": ["AUTHOR"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": True,
        }
    )
    candidate = schemas["ReviewCandidate"]["properties"]
    candidate["kind"]["enum"].append("Report")
    candidate["record"]["oneOf"].append({"$ref": "#/components/schemas/Report"})
    export_path = prefix + "reports/{object_id}/export"
    template = deepcopy(paths[prefix + "reports/{object_id}"])
    get = template["get"]
    get.update(
        operationId="export_report_package",
        summary="Export an approved frozen internal report package",
        **{"x-capability": "reports.read", "x-contract-version": "1.7.0"},
    )
    get["responses"]["200"]["content"] = {"text/html": {"schema": {"type": "string"}}}
    paths[export_path] = {"parameters": template["parameters"], "get": get}
    policy["operations"].append(
        {
            "operation_id": "export_report_package",
            "method": "GET",
            "path": export_path,
            "capability": "reports.read",
            "role_templates": [
                "MEL_ADMIN",
                "PROGRAMME_MANAGER",
                "AUTHOR",
                "REVIEWER",
                "ANALYST",
                "DATA_STEWARD",
                "EXTERNAL",
            ],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
    spec["info"]["version"] = policy["version"] = "1.7.0"
