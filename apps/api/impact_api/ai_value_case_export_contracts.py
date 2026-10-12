"""Closed contract for complete value-case PDF/DOCX exports."""

from .measurement_contracts import closed

VERSION = "1.46.0"
ROOT = "ai-enablement/value-case/export"
IMPLEMENTED = [("post", ROOT)]
MEDIA = {
    "PDF": "application/pdf",
    "DOCX": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    schemas["AIValueCaseExportRequest"] = closed(
        {
            "format": {"enum": list(MEDIA)},
            "title": {"type": "string", "minLength": 1, "maxLength": 150},
            "value_case": {"$ref": "#/components/schemas/AIValueCaseRequest"},
        },
        ["format", "title", "value_case"],
    )
    schemas["AIValueCaseExportManifest"] = closed(
        {
            "format": {"enum": list(MEDIA)},
            "filename": {
                "type": "string",
                "pattern": r"^impact-value-case-[a-f0-9]{16}[.](?:pdf|docx)$",
            },
            "media_type": {"enum": list(MEDIA.values())},
            "content_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            "size_bytes": {"type": "integer", "minimum": 1, "maximum": 10485760},
            "renderer_version": {"const": "ai-value-case-export-v1"},
            "assumption_count": {"type": "integer", "minimum": 1, "maximum": 20},
        },
        [
            "format",
            "filename",
            "media_type",
            "content_sha256",
            "size_bytes",
            "renderer_version",
            "assumption_count",
        ],
    )
    schemas["AIValueCaseExport"] = closed(
        {
            "manifest": {"$ref": "#/components/schemas/AIValueCaseExportManifest"},
            "content_base64": {
                "type": "string",
                "contentEncoding": "base64",
                "maxLength": 13981016,
            },
        },
        ["manifest", "content_base64"],
    )
    path = "/v1/tenants/{tenant_id}/" + ROOT
    operation = {
        "operationId": "export_ai_value_case",
        "summary": "Render a complete board/funder value case as PDF or DOCX",
        "description": (
            "The server recalculates the complete value case from closed source inputs and renders "
            "every submitted assumption. Partial result payloads and omitted assumptions are refused."
        ),
        "x-capability": "ai.enablement.export",
        "x-contract-version": VERSION,
        "parameters": [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/AIValueCaseExportRequest"}}
            },
        },
        "responses": {
            "200": {
                "description": "Complete downloadable artifact with digest manifest",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIValueCaseExport"}}
                },
            }
        },
    }
    for code in ("400", "401", "403", "422", "429", "503"):
        operation["responses"][code] = {
            "description": "Request refused without an incomplete artifact",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        }
    spec["paths"][path] = {"post": operation}
    policy["operations"].append(
        {
            "operation_id": "export_ai_value_case",
            "method": "POST",
            "path": path,
            "capability": "ai.enablement.export",
            "role_templates": ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
            "purpose_required": False,
            "fresh_assurance_seconds": 300,
            "audit": False,
        }
    )
