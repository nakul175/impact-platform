"""Evidence object store contracts (v0.22): the design contract's upload and evidence routes,
tightened to what this build implements (WHOLE-mode EVIDENCE_MEDIA uploads, file-backed or
external-reference evidence drafts, mediated content download), one added attach action and two
reads of the evidence cited by an observation or a calculated result.

Not implemented and therefore not exported: MULTIPART parts, upload cancellation, SOURCE_IMPORT
uploads, evidence verification and publication handling records."""

from copy import deepcopy

from .content_safety import MAX_EVIDENCE_BYTES, MEDIA_TYPES
from .measurement_contracts import closed, text_field

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
SHA256 = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
TARGET_KINDS = {"Observation": "observations", "CalculatedResult": "calculated-results"}
PREFIX = "/v1/tenants/{tenant_id}/"
# Special reads (GET, served by explicit routes in main.py).
SPECIAL_READS = {
    "observations/{object_id}/evidence": (
        "list_observation_evidence",
        "evidence.read",
        "EvidenceAttachmentList",
    ),
    "calculated-results/{object_id}/evidence": (
        "list_calculated_result_evidence",
        "evidence.read",
        "EvidenceAttachmentList",
    ),
}
# Upload and content operations this build serves (method, path below the tenant prefix).
IMPLEMENTED = [
    ("post", "uploads"),
    ("get", "uploads/{object_id}"),
    ("put", "uploads/{object_id}/content"),
    ("post", "uploads/{object_id}/actions/complete"),
    ("get", "evidence/{object_id}/content"),
]
ATTACH_ROLES = ["AUTHOR", "DATA_STEWARD"]
VERSION = "1.14.0"


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]

    # Upload declaration: evidence media only, whole-file mode, an allow-listed media type and a
    # declared file name whose extension that type permits.
    schemas["UploadCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "purpose": {"enum": ["EVIDENCE_MEDIA"]},
                    "content_type": {"enum": sorted(MEDIA_TYPES)},
                    "expected_bytes": {"type": "integer", "minimum": 1, "maximum": MAX_EVIDENCE_BYTES},
                    "content_sha256": SHA256,
                    "mode": {"enum": ["WHOLE"]},
                    "filename": {"type": "string", "minLength": 1, "maxLength": 200},
                },
                ["purpose", "content_type", "expected_bytes", "content_sha256", "mode", "filename"],
            ),
        },
        ["operation_id", "data"],
    )
    status = deepcopy(schemas["UploadStatus"])
    status["properties"].update(
        filename={"type": "string", "maxLength": 200},
        content_type={"enum": sorted(MEDIA_TYPES)},
        purpose={"enum": ["EVIDENCE_MEDIA"]},
        content_received={"type": "boolean"},
        scan_detail={"type": ["string", "null"], "maxLength": 64},
    )
    status["properties"]["expected_bytes"]["maximum"] = MAX_EVIDENCE_BYTES
    status["properties"]["parts"]["maxItems"] = 0
    schemas["UploadStatus"] = status
    schemas["UploadComplete"]["properties"]["data"]["properties"]["parts"]["maxItems"] = 0

    # Evidence drafts: the design fields without publication handling records (not implemented).
    # A file-backed draft names a CLEAN upload of the caller; the server copies its name, media
    # type, size, digest and verdict into the revision (never from the body).
    draft = {
        "upload_id": UUID,
        "external_reference": {"type": "string", "minLength": 1, "maxLength": 2000, "pattern": "^https://"},
        "source": text_field(2000),
        "evidence_date": DATE,
        "evidence_type": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]{0,63}$"},
    }
    schemas["EvidenceDraftData"] = closed(deepcopy(draft))
    data = deepcopy(schemas["EvidenceData"])
    data["properties"].pop("publication_handling_id", None)
    data["properties"].update(
        deepcopy(draft),
        filename={"type": "string", "maxLength": 200, "readOnly": True},
        media_type={"enum": sorted(MEDIA_TYPES), "readOnly": True},
        byte_size={"type": "integer", "minimum": 1, "readOnly": True},
    )
    schemas["EvidenceData"] = data
    schemas["EvidencePatch"]["properties"]["data"] = {
        "allOf": [{"$ref": "#/components/schemas/EvidenceDraftData"}],
        "minProperties": 1,
    }

    # Attach the head revision of an evidence object to the current revision of an observation or
    # a calculated result. The cited record is unchanged; the citation is an insert-only register row.
    schemas["ActionEvidenceAttachData"] = closed(
        {
            "target_kind": {"enum": sorted(TARGET_KINDS)},
            "target_id": UUID,
            "target_revision": UUID,
            "reason": text_field(2000),
        },
        ["target_kind", "target_id", "target_revision", "reason"],
    )
    schemas["ActionEvidenceAttach"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": {"$ref": "#/components/schemas/ActionEvidenceAttachData"},
        },
        ["operation_id", "expected_revision", "data"],
    )
    entry = deepcopy(paths[PREFIX + "evidence/{object_id}/actions/verify"])
    entry["post"].update(
        operationId="action_evidence_attach",
        summary="action evidence attach",
        description="Cite the evidence head revision (expected_revision) from the current revision of an "
        "observation or calculated result the caller can read. File-backed evidence must be CLEAN. The "
        "cited record is not changed.",
        **{"x-capability": "evidence.attach"},
    )
    entry["post"]["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ActionEvidenceAttach"
    }
    paths[PREFIX + "evidence/{object_id}/actions/attach"] = entry
    policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != "action_evidence_attach"]
    policy["operations"].append(
        {
            "operation_id": "action_evidence_attach",
            "method": "POST",
            "path": PREFIX + "evidence/{object_id}/actions/attach",
            "capability": "evidence.attach",
            "role_templates": ATTACH_ROLES,
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": True,
            "state_guard": "File-backed evidence must hold a CLEAN upload; the caller must also read the "
            "target (observations.read or calculated-results.read). Insert-only citation of exact revisions.",
        }
    )

    attachment = closed(
        {
            "attachment_id": UUID,
            "evidence_id": UUID,
            "evidence_revision": UUID,
            "evidence_revision_number": {"type": "integer", "minimum": 1},
            "evidence_head_revision": UUID,
            "target_kind": {"enum": sorted(TARGET_KINDS)},
            "target_id": UUID,
            "target_revision": UUID,
            "target_is_current": {"type": "boolean"},
            "evidence_type": {"type": ["string", "null"]},
            "filename": {"type": ["string", "null"], "maxLength": 200},
            "media_type": {"type": ["string", "null"]},
            "byte_size": {"type": ["integer", "null"]},
            "integrity_sha256": {"type": ["string", "null"]},
            "external_reference": {"type": ["string", "null"]},
            "scan_state": {"type": ["string", "null"]},
            "downloadable": {"type": "boolean"},
            "reason": {"type": "string"},
            "attached_by": UUID,
            "attached_at": {"type": "string"},
        },
        ["attachment_id", "evidence_id", "evidence_revision", "target_kind", "target_id", "target_revision"],
    )
    schemas["EvidenceAttachment"] = attachment
    schemas["EvidenceAttachmentList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 200,
                "items": {"$ref": "#/components/schemas/EvidenceAttachment"},
            },
            "next_cursor": {"type": "null"},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    for route, (op, cap, schema) in SPECIAL_READS.items():
        template = deepcopy(paths[PREFIX + "evidence/{object_id}"])
        get = template["get"]
        get.pop("parameters", None)
        get["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + schema
        }
        get.update(
            operationId=op,
            summary=op.replace("_", " "),
            description="Evidence revisions cited by revisions of this record. Requires read access to the "
            "record and evidence.read; citations of evidence the caller cannot read are omitted.",
            **{"x-capability": cap},
        )
        paths[PREFIX + route] = {"parameters": template["parameters"], "get": get}
        policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": "GET",
                "path": PREFIX + route,
                "capability": cap,
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

    for row in policy["operations"]:
        if row["operation_id"] == "read_evidence_content":
            # Every mediated download is recorded (evidence_access register and an audit event).
            row["audit"] = True
            row["state_guard"] = (
                "Mediated content response through the API only: re-authorised per request, tenant-fenced, "
                "only a CLEAN blob whose bytes still match the recorded SHA-256; attachment disposition, "
                "nosniff, no-store; each response recorded. No range requests, no signed redirect."
            )
        if row["operation_id"] == "get_uploads":
            row["state_guard"] = "Owner of the upload only; any other caller receives RESOURCE_UNAVAILABLE."
        if row["operation_id"] == "put_upload_content":
            row["state_guard"] = (
                "WHOLE mode only, owner only, request body at most 25,000,000 bytes (the 256 KiB JSON cap does "
                "not apply to this route alone). Exact byte count and SHA-256, magic-byte sniffing against the "
                "declared allow-listed type; identical replay returns the same status, different bytes conflict."
            )
        if row["operation_id"] == "complete_upload":
            row["state_guard"] = (
                "Seals the received whole file (no parts) and scans it with the configured scanner outside the "
                "transaction; the blob stays quarantined until the verdict is CLEAN. Replays re-run a scan that "
                "was interrupted."
            )

    # Every operation this module implements first appeared in the implemented contract of domain API
    # 1.14.0 (build 0.24.0); the design contract's 1.1.0 tag described the design, not this build.
    implemented = [("post", "evidence"), ("patch", "evidence/{object_id}")]
    implemented += [("post", "evidence/{object_id}/actions/attach")]
    implemented += [("get", route) for route in SPECIAL_READS] + IMPLEMENTED
    for method, route in implemented:
        paths[PREFIX + route][method]["x-contract-version"] = VERSION
