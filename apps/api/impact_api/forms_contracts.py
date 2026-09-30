"""Web form contracts (v0.20): the design contract's form and submission routes, tightened to what
this build implements, one added submit-for-review action and one read of the published version.

Field definitions are carried inside the Form revision (the design's separate FormField objects are
not implemented), so the approved and published revision pins every field, rule and indicator
binding a submission is validated against."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
DECIMAL = r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"
NULLABLE_DECIMAL = {"type": ["string", "null"], "pattern": DECIMAL}
CODE = r"^[A-Za-z][A-Za-z0-9_]{0,63}$"
FIELD_TYPES = ["TEXT", "DECIMAL", "INTEGER", "BOOLEAN", "SINGLE_CHOICE"]
VALUE_ROLES = ["VALUE", "NUMERATOR", "DENOMINATOR"]
REVIEW_STATES = ["DRAFT", "SUBMITTED", "QUARANTINED"]
ANSWER_KINDS = ["TEXT", "DECIMAL", "INTEGER", "BOOLEAN", "SINGLE_CHOICE", "Missing"]
SPECIAL_READS = {"forms/{object_id}/published": ("get_form_published", "forms.read", "PublishedForm")}
VERSION = "1.13.0"
ROLES = ["AUTHOR", "PROGRAMME_MANAGER", "MEL_ADMIN"]


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"

    # One field of a form version: stable identity and code, type, prompt, answer rules and, when it
    # feeds a measurement, the indicator instance and the role its answer plays. A SINGLE_CHOICE
    # field may instead supply a disaggregation dimension code for the indicators it accompanies.
    # Only field_id, stable_code and position are required by the schema (the seeded legacy form
    # carries nothing else); the service requires the rest before a version can be submitted.
    schemas["FormFieldBinding"] = closed(
        {
            "field_id": UUID,
            "stable_code": {"type": "string", "pattern": CODE},
            "position": {"type": "integer", "minimum": 0, "maximum": 199},
            "section_code": {"type": "string", "minLength": 1, "maxLength": 64},
            "field_type": {"enum": FIELD_TYPES},
            "label": text_field(200),
            "help": {"type": ["string", "null"], "maxLength": 2000},
            "required": {"type": "boolean"},
            "minimum": NULLABLE_DECIMAL,
            "maximum": NULLABLE_DECIMAL,
            "max_length": {"type": ["integer", "null"], "minimum": 1, "maximum": 20000},
            "choices": {"type": "array", "items": {"$ref": "#/components/schemas/Choice"}, "maxItems": 100},
            "indicator_id": {"type": ["string", "null"], "format": "uuid"},
            "value_role": {"oneOf": [{"type": "null"}, {"enum": VALUE_ROLES}]},
            "dimension_code": {"type": ["string", "null"], "pattern": CODE},
            # Bounded relevance: the field applies only when an earlier choice or yes/no field holds
            # the stated code ("true"/"false" for BOOLEAN). No expression language in this build.
            "relevant_when": {
                "oneOf": [
                    {"type": "null"},
                    closed(
                        {
                            "field_code": {"type": "string", "pattern": CODE},
                            "equals": {"type": "string", "minLength": 1, "maxLength": 64},
                        },
                        ["field_code", "equals"],
                    ),
                ]
            },
        },
        ["field_id", "stable_code", "position"],
    )
    form = {
        "code": {"type": "string", "minLength": 1, "maxLength": 64},
        "title": text_field(200),
        "programme_id": UUID,
        "fields": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/FormFieldBinding"},
            "maxItems": 200,
        },
        # Logic rules, translations and compatibility mappings are not implemented in this build.
        "logic": {"type": "array", "maxItems": 0},
        "translation_versions": {"type": "array", "maxItems": 0},
        "compatibility_policy": {"enum": ["LOCK_PUBLISHED"]},
    }
    schemas["FormDraftData"] = closed(deepcopy(form))
    schemas["FormData"] = closed(deepcopy(form))
    schemas["FormPatch"]["properties"]["data"] = {
        "allOf": [{"$ref": "#/components/schemas/FormDraftData"}],
        "minProperties": 1,
    }

    answers = {
        "type": "object",
        "maxProperties": 200,
        "patternProperties": {
            CODE: {"oneOf": [{"$ref": "#/components/schemas/Answer" + k} for k in ANSWER_KINDS]}
        },
        "additionalProperties": False,
    }
    submission = {
        "form_version": UUID,
        "event_at": DATE,
        "captured_at": DATE,
        "capture_zone": text_field(64),
        "answers": answers,
        # The planned unit this response reports for. With it, each observation's source key is
        # "<unit_key>/<indicator_id>" so a collection plan can name the obligation in advance;
        # without it the key is "<submission_id>/<indicator_id>", an unplanned contribution.
        "unit_key": {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$"},
    }
    schemas["SubmissionDraftData"] = closed(deepcopy(submission))
    # Server-owned: the review state, receipt time, uploader, author, the observations the
    # submission produced and why a submission was quarantined.
    schemas["SubmissionData"] = closed(
        {
            **deepcopy(submission),
            "review_state": {"enum": REVIEW_STATES},
            "server_received_at": DATE,
            "authenticated_uploader_id": UUID,
            "original_author_id": UUID,
            "observation_ids": {"type": "array", "items": UUID, "maxItems": 200},
            "quarantine_reason": {"type": ["string", "null"], "maxLength": 64},
        }
    )
    schemas["SubmissionPatch"]["properties"]["data"] = {
        "allOf": [{"$ref": "#/components/schemas/SubmissionDraftData"}],
        "minProperties": 1,
    }
    schemas["ActionSubmissionsSubmitData"] = closed({"workflow_version": UUID}, ["workflow_version"])

    # Submit a form draft for independent review (the design names publish but no submit).
    schemas["ActionFormsSubmitData"] = closed({"workflow_version": UUID}, ["workflow_version"])
    schemas["ActionFormsSubmit"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": {"$ref": "#/components/schemas/ActionFormsSubmitData"},
        },
        ["operation_id", "expected_revision", "data"],
    )
    entry = deepcopy(paths[prefix + "frameworks/{object_id}/actions/submit"])
    entry["post"].update(
        operationId="action_forms_submit",
        summary="action forms submit",
        **{"x-capability": "form.submit", "x-contract-version": VERSION},
    )
    entry["post"]["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ActionFormsSubmit"
    }
    paths[prefix + "forms/{object_id}/actions/submit"] = entry
    policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != "action_forms_submit"]
    policy["operations"].append(
        {
            "operation_id": "action_forms_submit",
            "method": "POST",
            "path": prefix + "forms/{object_id}/actions/submit",
            "capability": "form.submit",
            "role_templates": ROLES,
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": True,
        }
    )

    for route in ["forms", "submissions"]:
        for suffix, methods in [("", ["get", "post"]), ("/{object_id}", ["get", "patch"])]:
            for method in methods:
                paths[prefix + route + suffix][method]["x-contract-version"] = VERSION
    for action in ["forms/{object_id}/actions/publish", "submissions/{object_id}/actions/submit"]:
        paths[prefix + action]["post"]["x-contract-version"] = VERSION

    schemas["PublishedForm"] = closed(
        {
            "form_id": UUID,
            "version_number": {"type": "integer", "minimum": 1},
            "form_version": UUID,
            "approved_revision": UUID,
            "supersedes_revision": {"type": ["string", "null"], "format": "uuid"},
            "published_at": {"type": "string"},
            "data": {"$ref": "#/components/schemas/FormData"},
            "versions": {
                "type": "array",
                "maxItems": 1000,
                "items": closed(
                    {"version_number": {"type": "integer", "minimum": 1}, "form_version": UUID},
                    ["version_number", "form_version"],
                ),
            },
        },
        ["form_id", "version_number", "form_version", "published_at", "data", "versions"],
    )
    for route, (op, cap, schema) in SPECIAL_READS.items():
        template = deepcopy(paths[prefix + "forms/{object_id}"])
        get = template["get"]
        get.pop("parameters", None)
        get["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + schema
        }
        get.update(
            operationId=op,
            summary=op.replace("_", " "),
            **{"x-capability": cap, "x-contract-version": VERSION},
        )
        paths[prefix + route] = {"parameters": template["parameters"], "get": get}
        policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": "GET",
                "path": prefix + route,
                "capability": cap,
                "role_templates": ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ENUMERATOR"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )

    candidate = schemas["ReviewCandidate"]["properties"]
    if "Form" not in candidate["kind"]["enum"]:
        candidate["kind"]["enum"].append("Form")
        candidate["record"]["oneOf"].append({"$ref": "#/components/schemas/Form"})
    spec["info"]["version"] = policy["version"] = VERSION
