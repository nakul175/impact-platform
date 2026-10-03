"""Import contracts (v0.21): the design contract's import routes, tightened to what this build
implements — a bounded tabular source carried in the request body, a header-name mapping to indicator
instances, a unit column and one period, a staging preview that classifies every row, and an atomic
commit of the staged outcome.

An import batch carries its own file and mapping. Batches above the threshold queue an application
executor job; smaller batches commit synchronously. Upload sessions and reusable mapping versions
remain outside this bounded implementation.

Since v0.27 an imported value's source key is `<unit key>/<indicator id>/<period id>`, so a
collection plan can name it in advance; the preview reports each staged value's key and, when the
caller can read the approved plan, whether the plan names it."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
DECIMAL = r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"
CODE = r"^[A-Za-z][A-Za-z0-9_]{0,63}$"
UNIT_KEY = r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$"
HEX64 = r"^[0-9a-f]{64}$"
VERSION = "1.14.0"
ASYNC_THRESHOLD = 50  # staged rows; 51–500 queue, 1–50 retain the existing synchronous path
# Bounds (the request body cap is 256 KiB for every command; these keep a batch inside it and keep
# a commit to a bounded number of observations in one transaction).
MAX_CONTENT = 196608
MAX_ROWS = 500
MAX_OBSERVATIONS = 500
MAX_COLUMNS = 40
FORMATS = ["CSV", "XLSX"]
DATE_PATTERNS = ["ISO_8601", "YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"]
VALUE_ROLES = ["VALUE", "NUMERATOR", "DENOMINATOR"]
MISSING_STATES = ["MISSING", "NOT_COLLECTED", "NOT_APPLICABLE"]
OUTCOMES = ["ACCEPTED", "QUARANTINED", "DUPLICATE"]
VALUE_STATES = ["PRESENT", "MISSING", "NOT_COLLECTED", "NOT_APPLICABLE", "UNDEFINED"]
ROLES = ["DATA_STEWARD", "MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR"]
READ_ROLES = ["DATA_STEWARD", "MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST"]
HEADER = {"type": "string", "minLength": 1, "maxLength": 100}
REASON = {"type": "string", "pattern": r"^[A-Z][A-Z0-9_]{0,63}$"}


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"

    # The mapping binds source columns by header name, never by position: a renamed or missing
    # column pauses the batch instead of shifting values into another indicator (FR-DAT-002).
    schemas["ImportColumnBinding"] = closed(
        {
            "column": HEADER,
            "indicator_id": UUID,
            "value_role": {"enum": VALUE_ROLES},
            # The unit the column is stated in; it must equal the pinned definition's unit.
            "unit": text_field(64),
            "minimum": {"type": ["string", "null"], "pattern": DECIMAL},
            "maximum": {"type": ["string", "null"], "pattern": DECIMAL},
        },
        ["column", "indicator_id", "value_role", "unit"],
    )
    schemas["ImportColumnMapping"] = closed(
        {
            "unit_column": HEADER,
            "event_at_column": {"oneOf": [{"type": "null"}, HEADER]},
            "columns": {
                "type": "array",
                "minItems": 1,
                "maxItems": 20,
                "items": {"$ref": "#/components/schemas/ImportColumnBinding"},
            },
            "dimension_columns": {
                "type": "array",
                "maxItems": 10,
                "items": closed(
                    {"column": HEADER, "dimension_code": {"type": "string", "pattern": CODE}},
                    ["column", "dimension_code"],
                ),
            },
            # Source tokens that declare an explicit value state (for example "NA" → NOT_APPLICABLE).
            # A blank cell is always MISSING; a token is never read as a number.
            "missing_codes": {
                "type": "object",
                "maxProperties": 10,
                "patternProperties": {r"^\S{1,32}$": {"enum": MISSING_STATES}},
                "additionalProperties": False,
            },
        },
        ["unit_column", "columns"],
    )
    draft = {
        "format": {"enum": FORMATS},
        "file_name": text_field(200),
        # CSV text, or the base64 of an .xlsx file (first worksheet only).
        "content": {"type": "string", "minLength": 1, "maxLength": MAX_CONTENT},
        "programme_id": UUID,
        "period_id": UUID,
        "mode": {"enum": ["APPEND"]},
        "atomic": {"type": "boolean"},
        "date_pattern": {"enum": DATE_PATTERNS},
        "mapping": {"$ref": "#/components/schemas/ImportColumnMapping"},
    }
    observation = closed(
        {
            "indicator_id": UUID,
            # The plannable source identity of the value: `<unit key>/<indicator id>/<period id>`
            # (v0.27). A collection plan obligation with namespace IMPORT and this key makes the
            # value a planned one; `planned` says whether the approved plan names it and is absent
            # when the plan could not be evaluated (no approved plan, or not readable by the caller).
            "source_key": {"type": "string", "maxLength": 200},
            "planned": {"type": "boolean"},
            "value_state": {"enum": VALUE_STATES},
            "value": {"type": ["string", "null"]},
            "numerator": {"type": ["string", "null"]},
            "denominator": {"type": ["string", "null"]},
            "dimension_values": {"type": "object", "maxProperties": 10},
            "observation_id": UUID,
        },
        ["indicator_id", "value_state"],
    )
    row = closed(
        {
            "row_number": {"type": "integer", "minimum": 2},
            "row_key": {"type": ["string", "null"], "maxLength": 1000},
            "outcome": {"enum": OUTCOMES},
            "reasons": {"type": "array", "maxItems": 40, "items": REASON},
            "warnings": {"type": "array", "maxItems": 40, "items": REASON},
            # Raw cell text of the mapped columns next to its interpretation (FR-DAT-001).
            "raw": {"type": "object", "maxProperties": MAX_COLUMNS},
            "event_at": {"type": ["string", "null"]},
            "observations": {"type": "array", "maxItems": 20, "items": observation},
            "anomalies": {"type": "array", "maxItems": 20},
        },
        ["row_number", "outcome", "reasons", "warnings"],
    )
    preview = closed(
        {
            "previewed_at": DATE,
            "previewed_by": UUID,
            "preview_hash": {"type": "string", "pattern": HEX64},
            "rule_set": {"type": "string", "maxLength": 64},
            "anomaly_method": {"type": "object"},
            "header": {"type": "array", "maxItems": MAX_COLUMNS, "items": {"type": "string"}},
            "dropped_columns": {"type": "array", "maxItems": MAX_COLUMNS, "items": {"type": "string"}},
            "blank_rows": {"type": "integer", "minimum": 0},
            "counts": closed(
                {
                    k: {"type": "integer", "minimum": 0}
                    for k in [
                        "rows",
                        "accepted",
                        "quarantined",
                        "duplicate",
                        "warnings",
                        "observations",
                        # Accepted values no approved plan names (v0.27); they block period close.
                        "unplanned",
                    ]
                },
                ["rows", "accepted", "quarantined", "duplicate", "warnings", "observations"],
            ),
            # The indicators whose approved collection plan was compared with the staged keys.
            "plan_check": closed(
                {"evaluated_indicators": {"type": "array", "maxItems": 20, "items": UUID}},
                ["evaluated_indicators"],
            ),
            "rows": {"type": "array", "maxItems": MAX_ROWS, "items": row},
        },
        ["previewed_at", "previewed_by", "preview_hash", "counts", "rows"],
    )
    committed = closed(
        {
            "committed_at": DATE,
            "committed_by": UUID,
            "preview_hash": {"type": "string", "pattern": HEX64},
            "observation_ids": {"type": "array", "maxItems": MAX_OBSERVATIONS, "items": UUID},
            "accepted_warnings": {"type": "boolean"},
        },
        ["committed_at", "committed_by", "preview_hash", "observation_ids"],
    )
    commit_request = closed(
        {
            "job_id": UUID,
            "principal_id": UUID,
            "identity_id": UUID,
            "auth_time": DATE,
            "preview_hash": {"type": "string", "pattern": HEX64},
            "workflow_version": UUID,
            "accept_warnings": {"type": "boolean"},
        },
        [
            "job_id",
            "principal_id",
            "identity_id",
            "auth_time",
            "preview_hash",
            "workflow_version",
            "accept_warnings",
        ],
    )
    processing = closed(
        {
            "job_id": UUID,
            "state": {"enum": ["Queued", "Running", "Committed", "Failed", "Cancelled"]},
            "attempts": {"type": "integer", "minimum": 0},
            "last_error_class": {"type": ["string", "null"], "pattern": REASON["pattern"]},
            "completed_at": {"type": ["string", "null"], "format": "date-time"},
        },
        ["job_id", "state", "attempts", "last_error_class", "completed_at"],
    )
    schemas["ImportJobDraftData"] = closed(deepcopy(draft))
    # Server-owned: the reserved source namespace, the content digest and receipt time, the staged
    # preview, the commit manifest and the cancellation reason.
    schemas["ImportJobData"] = closed(
        {
            **deepcopy(draft),
            "source_namespace": {"const": "IMPORT"},
            "content_sha256": {"type": "string", "pattern": HEX64},
            "received_at": DATE,
            "preview": {"oneOf": [{"type": "null"}, preview]},
            "committed": {"oneOf": [{"type": "null"}, committed]},
            "commit_request": {"oneOf": [{"type": "null"}, commit_request]},
            "processing": processing,
            "cancel_reason": {"type": ["string", "null"], "maxLength": 2000},
        }
    )
    schemas["ImportJobPatch"]["properties"]["data"] = {
        "allOf": [{"$ref": "#/components/schemas/ImportJobDraftData"}],
        "minProperties": 1,
    }
    schemas["ActionImportsPreviewData"] = closed({})
    schemas["ActionImportsCommitData"] = closed(
        {
            "preview_hash": {"type": "string", "pattern": HEX64},
            "workflow_version": UUID,
            # A staged batch with warnings (non-blocking quality findings) commits only when the
            # committer explicitly accepts them; blocking findings never commit.
            "accept_warnings": {"type": "boolean"},
        },
        ["preview_hash", "workflow_version"],
    )
    schemas["ActionImportsCancelData"] = closed({"reason": text_field(2000)}, ["reason"])

    # Create and edit a batch draft (the design only lists reads and a job request).
    for suffix, method, template, op, cap, body in [
        ("", "post", "frameworks", "create_imports", "imports.draft.create", "ImportJobCreate"),
        (
            "/{object_id}",
            "patch",
            "frameworks/{object_id}",
            "patch_imports",
            "imports.draft.edit",
            "ImportJobPatch",
        ),
    ]:
        entry = deepcopy(paths[prefix + template][method])
        entry.update(operationId=op, summary=op.replace("_", " "), **{"x-capability": cap})
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + body
        }
        paths[prefix + "imports" + suffix][method] = entry
        policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": prefix + "imports" + suffix,
                "capability": cap,
                "role_templates": ROLES,
                "scope": "tenant + object/programme/assignment scope; explicit grant required",
                "fresh_assurance_seconds": None,
                "independence_required": False,
                "purpose_required": False,
                "field_filter_required": False,
                "state_guard": "Draft or Previewed only; an edit discards the staged preview. Server-owned "
                "namespace, digest, receipt, preview and commit fields are never accepted.",
                "audit": True,
            }
        )
    for action in ["preview", "commit", "cancel"]:
        post = paths[prefix + "imports/{object_id}/actions/" + action]["post"]
        post["responses"]["200"] = deepcopy(
            paths[prefix + "frameworks/{object_id}/actions/submit"]["post"]["responses"]["200"]
        )
        post["responses"].pop("202", None)
    for route in ["imports", "imports/{object_id}"]:
        for method in [m for m in ["get", "post", "patch"] if m in paths[prefix + route]]:
            paths[prefix + route][method]["x-contract-version"] = VERSION
    for action in ["preview", "commit", "cancel"]:
        paths[prefix + "imports/{object_id}/actions/" + action]["post"]["x-contract-version"] = VERSION

    guards = {
        "action_imports_preview": "Draft or Previewed only. Parses the bounded source, validates every row "
        "against the mapping and the pinned indicator definitions, classifies each row ACCEPTED, "
        "QUARANTINED or DUPLICATE, records the quality checks, each value's plannable source key "
        "(<unit>/<indicator>/<period>) and whether the approved collection plan names it, and the preview "
        "hash; writes no observation.",
        "action_imports_commit": "Previewed only; expected_revision is the staged preview and preview_hash "
        "must equal the outcome recomputed now. Atomic batches refuse any non-accepted row; warnings need "
        "accept_warnings. Up to 50 staged rows commit synchronously; larger batches queue an "
        "IMPORT_COMMIT job for an application-role executor that rechecks the committer's current "
        "authority. Writes one IMPORT observation per accepted row and bound indicator under the "
        "staged source key and submits each into the independent observation review in the same "
        "transaction; the caller must also hold observation.submit (TENANT scope, no purpose). Values an "
        "approved plan names count as planned at period close; others block it (UNPLANNED_VALUES).",
        "action_imports_cancel": "Draft or Previewed only; nothing was committed, so nothing is rolled back.",
    }
    for row in policy["operations"]:
        if row["operation_id"] in guards:
            row["role_templates"] = ROLES
            row["state_guard"] = guards[row["operation_id"]]
        if row["operation_id"] == "action_imports_commit":
            row["additional_capabilities"] = [
                "observation.submit",
                "indicator-instances.read",
                "indicator-definitions.read",
                "programmes.read",
                "periods.read",
                "workflow-templates.read",
            ]
        if row["operation_id"] in {"list_imports", "get_imports"}:
            # Import batches carry the raw source rows; external partners do not read them here.
            row["role_templates"] = READ_ROLES
