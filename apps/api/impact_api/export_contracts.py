"""Contracts for worker-rendered PDF, XLSX and DOCX report exports and their controlled delivery
(v0.23). Runs after the reporting and publication augments."""

from copy import deepcopy

from .measurement_contracts import DATE, UUID, closed

FORMATS = ["PDF", "XLSX", "DOCX"]
EXPORT_ROLES = ["AUTHOR", "MEL_ADMIN", "PROGRAMME_MANAGER", "REVIEWER", "ANALYST"]
RECIPIENT_ROLES = [
    "AUTHOR",
    "REVIEWER",
    "MEL_ADMIN",
    "PROGRAMME_MANAGER",
    "ANALYST",
    "DATA_STEWARD",
    "EXTERNAL",
    "PRIVACY",
]
# Reads served by explicit routes in main.py: path below the tenant -> (operation, media type,
# capability). The listing answers JSON; the downloads answer the artifact's bytes.
SPECIAL_READS = {
    "reports/{object_id}/exports": ("list_report_exports", "application/json", "report.export"),
    "reports/{object_id}/exports/{job_id}/download": (
        "download_report_export",
        "application/octet-stream",
        "report.export",
    ),
    "publications/{object_id}/download.pdf": (
        "download_controlled_publication_pdf",
        "application/pdf",
        "publication.download",
    ),
    "publications/{object_id}/download.xlsx": (
        "download_controlled_publication_xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "publication.download",
    ),
    "publications/{object_id}/download.docx": (
        "download_controlled_publication_docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "publication.download",
    ),
}
SHA256 = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
ERROR_CLASS = {"type": "string", "pattern": "^[A-Z0-9_]{1,64}$"}


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"
    version = "1.14.0"

    def replace_policy(row):
        policy["operations"] = [
            item for item in policy["operations"] if item["operation_id"] != row["operation_id"]
        ]
        policy["operations"].append(row)

    # Actions on an approved report: request one export job, request its cancellation.
    for action, name, data in [
        ("export", "ActionReportsExport", closed({"format": {"enum": FORMATS}}, ["format"])),
        ("cancel-export", "ActionReportsCancelExport", closed({"job_id": UUID}, ["job_id"])),
    ]:
        schemas[name + "Data"] = data
        schemas[name] = closed(
            {
                "operation_id": UUID,
                "expected_revision": UUID,
                "data": {"$ref": "#/components/schemas/" + name + "Data"},
            },
            ["operation_id", "expected_revision", "data"],
        )
        path = prefix + "reports/{object_id}/actions/" + action
        entry = deepcopy(paths[prefix + "indicator-instances/{object_id}/actions/calculate"])
        op = "action_reports_" + action.replace("-", "_")
        entry["post"].update(
            operationId=op,
            summary=op.replace("_", " "),
            **{"x-capability": "report.export", "x-contract-version": version},
        )
        entry["post"]["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + name
        }
        entry["post"]["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/Receipt"
        }
        paths[path] = entry
        replace_policy(
            {
                "operation_id": op,
                "method": "POST",
                "path": path,
                "capability": "report.export",
                "role_templates": EXPORT_ROLES,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": True,
            }
        )

    schemas["ReportExport"] = closed(
        {
            "job_id": UUID,
            "report_id": UUID,
            "report_revision": UUID,
            "format": {"enum": FORMATS},
            "renderer_version": {"type": "string", "pattern": "^[a-z0-9.-]{1,32}$"},
            "state": {"enum": ["Queued", "Running", "Succeeded", "Failed", "Cancelled"]},
            "attempts": {"type": "integer", "minimum": 0},
            "last_error_class": {"oneOf": [ERROR_CLASS, {"type": "null"}]},
            "cancellation_requested": {"type": "boolean"},
            "cancellation_outcome": {"oneOf": [ERROR_CLASS, {"type": "null"}]},
            "requested_at": DATE,
            "completed_at": {"oneOf": [DATE, {"type": "null"}]},
            "media_type": {"oneOf": [{"type": "string", "maxLength": 128}, {"type": "null"}]},
            "content_sha256": {"oneOf": [SHA256, {"type": "null"}]},
            "size_bytes": {"oneOf": [{"type": "integer", "minimum": 1}, {"type": "null"}]},
        },
        [
            "job_id",
            "report_id",
            "report_revision",
            "format",
            "renderer_version",
            "state",
            "attempts",
            "last_error_class",
            "cancellation_requested",
            "requested_at",
            "completed_at",
            "content_sha256",
        ],
    )
    schemas["ReportExportList"] = closed(
        {"items": {"type": "array", "items": {"$ref": "#/components/schemas/ReportExport"}, "maxItems": 100}},
        ["items"],
    )

    # A disclosure may also deliver export artifacts. The requester names formats; the server pins
    # each to the exact succeeded artifact of the disclosed report revision before review, so the
    # reviewer approves exact bytes (a server-owned field the request schema does not accept).
    formats = {"type": "array", "items": {"enum": FORMATS}, "uniqueItems": True, "minItems": 1, "maxItems": 3}
    pinned = {
        "type": "array",
        "maxItems": 3,
        "items": closed(
            {"format": {"enum": FORMATS}, "job_id": UUID, "content_sha256": SHA256},
            ["format", "job_id", "content_sha256"],
        ),
    }
    for name in ["DisclosureData", "DisclosureDraftData"]:
        schemas[name]["properties"].update(
            export_formats=deepcopy(formats), export_artifacts=deepcopy(pinned)
        )
    schemas["CommandRequestDisclosureData"]["properties"]["export_formats"] = deepcopy(formats)

    template = paths[prefix + "reports/{object_id}/export"]
    for route, (operation_id, media_type, capability) in SPECIAL_READS.items():
        entry = deepcopy(template)
        if "{job_id}" in route:
            entry["parameters"].append({"name": "job_id", "in": "path", "required": True, "schema": UUID})
        get = entry["get"]
        get.update(
            operationId=operation_id,
            summary=operation_id.replace("_", " "),
            **{"x-capability": capability, "x-contract-version": version},
        )
        get["responses"]["200"]["content"] = (
            {"application/json": {"schema": {"$ref": "#/components/schemas/ReportExportList"}}}
            if media_type == "application/json"
            else {media_type: {"schema": {"type": "string", "contentMediaType": media_type}}}
        )
        paths[prefix + route] = entry
        replace_policy(
            {
                "operation_id": operation_id,
                "method": "GET",
                "path": prefix + route,
                "capability": capability,
                "role_templates": EXPORT_ROLES if capability == "report.export" else RECIPIENT_ROLES,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )
