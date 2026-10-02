"""Privacy execution contracts (v0.25 part B): data-subject request cases for a member of the
tenant (access export and erasure propagation) and read-only views of the retention schedule and
its proof records.

The design contract's privacy-case routes are kept and tightened to what this build implements:
every case operation is purpose-required and names its purpose (`DATA_SUBJECT_REQUEST`, a closed
set) in the request; a grant for the capability with exactly that purpose authorises it, a
purpose-less grant never does. Approval and execution need 300 s fresh assurance; approval also
needs a natural person independent of every author of the case and of the subject. One added read
returns the store plan an approver confirms by its SHA-256; one added download returns the access
export package (JSON with a SHA-256 manifest).

Not implemented and therefore not exported: participant subjects (no participant records exist),
rejection and hold actions, retention-policy objects (the schedule is a fixed catalogue in
`impact_api.retention`), backup expiry and external-recipient tracking."""

from copy import deepcopy

from .measurement_contracts import closed, text_field
from .retention import SCHEDULE

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
SHA256 = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
PURPOSES = ["DATA_SUBJECT_REQUEST"]
PURPOSE = {"enum": PURPOSES}
REQUEST_TYPES = ["ACCESS", "ERASURE"]
PREFIX = "/v1/tenants/{tenant_id}/"
INTAKE_ROLES = ["PRIVACY", "TENANT_ADMIN"]
OFFICER_ROLES = ["PRIVACY"]
RETENTION_ROLES = ["PRIVACY", "TENANT_ADMIN"]
STORES = ["MEMBER_PROFILE", "INVITATION_REGISTER", "DATABASE", "PROJECTION", "OUTBOX", "OBJECT_STORE"]
# Operations this build serves (method, path below the tenant prefix), all by explicit routes.
IMPLEMENTED = [
    ("get", "privacy-cases"),
    ("post", "privacy-cases"),
    ("get", "privacy-cases/{object_id}"),
    ("patch", "privacy-cases/{object_id}"),
    ("get", "privacy-cases/{object_id}/plan"),
    ("post", "privacy-cases/{object_id}/actions/approve"),
    ("post", "privacy-cases/{object_id}/actions/execute"),
    ("get", "privacy-cases/{object_id}/export"),
    ("get", "retention-schedule"),
    ("get", "retention-proofs"),
]
VERSION = "1.15.0"


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    ids = {"type": "array", "items": UUID, "maxItems": 50, "uniqueItems": True}
    draft = {
        "request_type": {"enum": REQUEST_TYPES},
        "subject_membership_id": UUID,
        "reason": text_field(2000),
        "verification_note": text_field(2000),
        "handling_authority": text_field(64),
        "deadline": DATE,
        "evidence_ids": ids,
        "import_ids": ids,
        "purpose": PURPOSE,
    }
    schemas["PrivacyCaseDraftData"] = closed(deepcopy(draft))
    server = {
        "subject_principal_id": UUID,
        "approved_by": UUID,
        "approved_at": DATE,
        "approved_revision": UUID,
        "plan_sha256": SHA256,
        "executed_by": UUID,
        "executed_at": DATE,
        "completed_at": DATE,
        "outcome": {"enum": ["COMPLETED", "PARTIALLY_COMPLETED"]},
        "package_id": UUID,
        "package_sha256": SHA256,
        "manifest": {"type": "object"},
    }
    data = closed({**deepcopy(draft), **{k: {**v, "readOnly": True} for k, v in server.items()}})
    schemas["PrivacyCaseData"] = data
    schemas["PrivacyCaseCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                deepcopy(draft),
                ["request_type", "subject_membership_id", "reason", "verification_note", "purpose"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["PrivacyCasePatch"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": {**closed(deepcopy(draft), ["purpose"]), "minProperties": 2},
        },
        ["operation_id", "expected_revision", "data"],
    )
    schemas["ActionPrivacyCasesApproveData"] = closed(
        {"purpose": PURPOSE, "plan_sha256": SHA256, "reason": text_field(2000)},
        ["purpose", "plan_sha256", "reason"],
    )
    schemas["ActionPrivacyCasesExecuteData"] = closed(
        {"purpose": PURPOSE, "approved_plan_hash": SHA256}, ["purpose", "approved_plan_hash"]
    )
    for name in ["ActionPrivacyCasesApprove", "ActionPrivacyCasesExecute"]:
        schemas[name] = closed(
            {
                "operation_id": UUID,
                "expected_revision": UUID,
                "data": {"$ref": "#/components/schemas/" + name + "Data"},
            },
            ["operation_id", "expected_revision", "data"],
        )
    entry = closed(
        {
            "store": {"enum": STORES},
            "action": {"enum": ["REDACT", "DELETE", "SUPERSEDE"]},
            "object_id": UUID,
            "object_type": {"type": "string", "maxLength": 64},
            "state": {"enum": ["APPROVED", "EXECUTING", "COMPLETED", "FAILED", "HELD"]},
            "reason": {"type": ["string", "null"], "maxLength": 64},
            "hold_review_at": {"type": ["string", "null"], "format": "date-time"},
        },
        ["store", "action", "object_id", "object_type", "state", "reason", "hold_review_at"],
    )
    schemas["PrivacyPlanEntry"] = entry
    schemas["PrivacyCasePlan"] = closed(
        {
            "case_id": UUID,
            "revision_id": UUID,
            "request_type": {"enum": REQUEST_TYPES},
            "subject_membership_id": UUID,
            "subject_principal_id": UUID,
            "plan_sha256": SHA256,
            "approved": {"type": "boolean"},
            "entries": {
                "type": "array",
                "maxItems": 2000,
                "items": {"$ref": "#/components/schemas/PrivacyPlanEntry"},
            },
        },
        [
            "case_id",
            "revision_id",
            "request_type",
            "subject_membership_id",
            "subject_principal_id",
            "plan_sha256",
            "approved",
            "entries",
        ],
    )
    schemas["RetentionScheduleItem"] = closed(
        {
            "data_class": {"type": "string"},
            "store": {"type": "string"},
            "trigger": {"type": "string"},
            "retention_days": {"type": "integer", "minimum": 0},
            "action": {"enum": ["DELETE", "REDACT", "EXPIRE"]},
            "basis": {"type": "string"},
            "source": {"enum": ["DEFAULT", "APPROVED_POLICY"]},
            "policy_id": {"type": ["string", "null"], "format": "uuid"},
        },
        ["data_class", "store", "trigger", "retention_days", "action", "basis", "source", "policy_id"],
    )
    schemas["RetentionSchedule"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 50,
                "items": {"$ref": "#/components/schemas/RetentionScheduleItem"},
            },
            "next_cursor": {"type": "null"},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    schemas["RetentionProof"] = closed(
        {
            "proof_id": UUID,
            "job_id": UUID,
            "lease_generation": {"type": "integer", "minimum": 1},
            "data_class": {"type": "string"},
            "action": {"enum": ["DELETE", "REDACT", "EXPIRE"]},
            "retention_days": {"type": "integer", "minimum": 0},
            "cutoff": DATE,
            "affected_count": {"type": "integer", "minimum": 0},
            "items_sha256": SHA256,
            "executed_at": DATE,
            "worker_id": {"type": "string"},
        },
        [
            "proof_id",
            "job_id",
            "lease_generation",
            "data_class",
            "action",
            "retention_days",
            "cutoff",
            "affected_count",
            "items_sha256",
            "executed_at",
            "worker_id",
        ],
    )
    schemas["RetentionProofList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/RetentionProof"},
            },
            "next_cursor": {"type": "null"},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )

    purpose_parameter = {
        "name": "purpose",
        "in": "query",
        "required": True,
        "schema": {"enum": PURPOSES},
        "description": "The purpose under which the caller acts; a grant with exactly this purpose is required.",
    }
    base = PREFIX + "privacy-cases"
    item = base + "/{object_id}"
    for path, method in [(base, "get"), (item, "get")]:
        operation = paths[path][method]
        operation["parameters"] = [p for p in operation.get("parameters", []) if p["name"] != "purpose"] + [
            deepcopy(purpose_parameter)
        ]
    paths[item]["patch"]["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/PrivacyCasePatch"
    }
    paths[item + "/actions/execute"]["post"]["responses"] = deepcopy(
        paths[item + "/actions/approve"]["post"]["responses"]
    )

    def read(path, op, cap, schema, description, purpose=True, media="application/json"):
        template = deepcopy(paths[item]["get"])
        template["parameters"] = [deepcopy(purpose_parameter)] if purpose else []
        template["responses"]["200"]["content"] = {
            media: {"schema": {"$ref": "#/components/schemas/" + schema}}
        }
        template.update(
            operationId=op, summary=op.replace("_", " "), description=description, **{"x-capability": cap}
        )
        node = paths.setdefault(path, {})
        node["parameters"] = (
            deepcopy(paths[item]["parameters"])
            if "{object_id}" in path
            else [deepcopy(paths[base]["parameters"][0])]
        )
        node["get"] = template

    schemas["PrivacyExportPackage"] = {"type": "object"}
    read(
        item + "/plan",
        "get_privacy_case_plan",
        "privacy-cases.read",
        "PrivacyCasePlan",
        "The per-store plan the case would execute now (erasure) or the export scope (access), with its "
        "SHA-256; an approver confirms exactly this hash.",
    )
    read(
        item + "/export",
        "read_privacy_case_export",
        "privacy.export",
        "PrivacyExportPackage",
        "The access-request export package of a completed ACCESS case as a JSON attachment: only the "
        "subject's data held by this tenant, with a per-section SHA-256 manifest. Mediated, recorded per "
        "download; refused once the package has expired.",
    )
    read(
        PREFIX + "retention-schedule",
        "list_retention_schedule",
        "retention.read",
        "RetentionSchedule",
        "The retention schedule the worker's RETENTION_SWEEP applies, per data class.",
        purpose=False,
    )
    read(
        PREFIX + "retention-proofs",
        "list_retention_proofs",
        "retention.read",
        "RetentionProofList",
        "The latest proof records of this tenant's retention sweeps (newest first, at most 100).",
        purpose=False,
    )

    rows = {
        "list_privacy_cases": ("privacy-cases.read", INTAKE_ROLES, None),
        "get_privacy_cases": ("privacy-cases.read", INTAKE_ROLES, None),
        "create_privacy_cases": ("privacy-cases.draft.create", INTAKE_ROLES, None),
        "patch_privacy_cases": ("privacy-cases.draft.edit", INTAKE_ROLES, None),
        "get_privacy_case_plan": ("privacy-cases.read", INTAKE_ROLES, None),
        "action_privacy_cases_approve": ("privacy.approve", OFFICER_ROLES, 300),
        "action_privacy_cases_execute": ("privacy.execute", OFFICER_ROLES, 300),
        "read_privacy_case_export": ("privacy.export", OFFICER_ROLES, 300),
    }
    paths_by_op = {
        operation["operationId"]: (path, method)
        for path, node in paths.items()
        for method, operation in node.items()
        if isinstance(operation, dict) and "operationId" in operation
    }
    guards = {
        "action_privacy_cases_approve": "Independent natural person: never an author of the case nor the "
        "subject. Confirms the plan SHA-256 the approver reviewed; a changed plan is refused.",
        "action_privacy_cases_execute": "Executes exactly the approved plan (hash re-computed and compared). "
        "Erasure removes or redacts the subject's personal data in each store; held items stay and are "
        "reported; approved official results are never altered. Access writes one bounded export package.",
        "read_privacy_case_export": "Mediated JSON attachment, re-authorised per request with purpose and "
        "fresh assurance, recorded in privacy_export_access and the audit trail.",
    }
    policy["operations"] = [p for p in policy["operations"] if p["operation_id"] not in rows]
    for op, (cap, roles, fresh) in rows.items():
        path, method = paths_by_op[op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": path,
                "capability": cap,
                "role_templates": roles,
                "purpose_required": True,
                "purposes": PURPOSES,
                "fresh_assurance_seconds": fresh,
                "independence_required": op == "action_privacy_cases_approve",
                "audit": op not in {"list_privacy_cases", "get_privacy_cases", "get_privacy_case_plan"},
                "state_guard": guards.get(
                    op, "Purpose-bound grant required; the subject must be a member of this tenant."
                ),
            }
        )
    for op in ["list_retention_schedule", "list_retention_proofs"]:
        path, method = paths_by_op[op]
        policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": "GET",
                "path": path,
                "capability": "retention.read",
                "role_templates": RETENTION_ROLES,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )
    for method, route in IMPLEMENTED:
        paths[PREFIX + route][method]["x-contract-version"] = VERSION
    schemas["RetentionScheduleItem"]["properties"]["data_class"]["enum"] = sorted(
        c["data_class"] for c in SCHEDULE
    )
