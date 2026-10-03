"""Web form contracts (v0.20): the design contract's form and submission routes, tightened to what
this build implements, one added submit-for-review action and one read of the published version.

Field definitions are carried inside the Form revision (the design's separate FormField objects are
not implemented), so the approved and published revision pins every field, rule and indicator
binding a submission is validated against."""

import json
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
# A collection language: a BCP-47 primary subtag with at most two further subtags ("en", "hi",
# "pt-BR", "sr-Latn-RS"). Codes are the identity of a language version; display names are text.
LANGUAGE = r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8}){0,2}$"
UNIT_KEY = r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$"
SPECIAL_READS = {
    "forms/{object_id}/published": ("get_form_published", "forms.read", "PublishedForm"),
    # v0.27: the language completeness of a form version, for its translators and reviewers.
    "forms/{object_id}/completeness": ("get_form_completeness", "forms.read", "FormCompleteness"),
    # v0.27: expected versus received units of a collection round.
    "collection-rounds/{object_id}/coverage": (
        "get_round_coverage",
        "collection-rounds.read",
        "RoundCoverage",
    ),
}
VERSION = "1.13.0"
ROUNDS_VERSION = "1.17.0"
ROLES = ["AUTHOR", "PROGRAMME_MANAGER", "MEL_ADMIN"]
READERS = ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ENUMERATOR"]
SUPERVISORS = ["MEL_ADMIN", "PROGRAMME_MANAGER"]


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
    # One language version of the instrument (v0.27, FR-FRM-004): language-specific label, help
    # and choice labels keyed by the stable field and choice codes, which never change. The field
    # definitions carry the text of the form's default language; a translation only adds text.
    schemas["FormTranslation"] = closed(
        {
            "language": {"type": "string", "pattern": LANGUAGE},
            "name": text_field(64),
            "fields": {
                "type": "object",
                "maxProperties": 200,
                "patternProperties": {
                    CODE: closed(
                        {
                            "label": text_field(200),
                            "help": {"type": ["string", "null"], "maxLength": 2000},
                            "choices": {
                                "type": "object",
                                "maxProperties": 100,
                                "patternProperties": {r"^.{1,64}$": text_field(200)},
                                "additionalProperties": False,
                            },
                        }
                    )
                },
                "additionalProperties": False,
            },
        },
        ["language", "fields"],
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
        # Logic rules and compatibility mappings are not implemented in this build.
        "logic": {"type": "array", "maxItems": 0},
        # The language of the field definitions themselves and the additional language versions
        # reviewed and published with them (v0.27). A form without a default language is a
        # single-language instrument whose language is undeclared, as every form before v0.27 was.
        "default_language": {"type": "string", "pattern": LANGUAGE},
        "translation_versions": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/FormTranslation"},
            "maxItems": 20,
        },
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
        "unit_key": {"type": "string", "pattern": UNIT_KEY},
        # The language presented to the respondent (v0.27): the version's default language or one
        # of its published translations. Answers carry stable codes whatever the language.
        "language": {"type": "string", "pattern": LANGUAGE},
        # The assignment this response fulfils (v0.27, FR-FRM-005): pins the round and the unit.
        "assignment_id": UUID,
    }
    schemas["SubmissionDraftData"] = closed(deepcopy(submission))
    # Server-owned: the review state, receipt time, uploader, author, the observations the
    # submission produced, why a submission was quarantined and, for a correction, the revision it
    # supersedes and the stated reason.
    schemas["SubmissionData"] = closed(
        {
            **deepcopy(submission),
            "review_state": {"enum": REVIEW_STATES},
            "server_received_at": DATE,
            "authenticated_uploader_id": UUID,
            "original_author_id": UUID,
            "observation_ids": {"type": "array", "items": UUID, "maxItems": 200},
            "quarantine_reason": {"type": ["string", "null"], "maxLength": 64},
            "correction_of_revision": {"type": ["string", "null"], "format": "uuid"},
            "correction_reason": {"type": ["string", "null"], "maxLength": 2000},
        }
    )
    schemas["SubmissionPatch"]["properties"]["data"] = {
        "allOf": [{"$ref": "#/components/schemas/SubmissionDraftData"}],
        "minProperties": 1,
    }
    schemas["ActionSubmissionsSubmitData"] = closed({"workflow_version": UUID}, ["workflow_version"])
    # Correct returned work (v0.27, FR-FRM-006): the full corrected answer set and the reason. A
    # correction is a new Submission revision; the observations it re-submits are new revisions of
    # the returned observations, never edits of a reviewed one.
    schemas["ActionSubmissionsCorrectData"] = closed(
        {
            "workflow_version": UUID,
            "reason": {"type": "string", "minLength": 1, "maxLength": 2000},
            "answers": deepcopy(answers),
        },
        ["workflow_version", "reason", "answers"],
    )
    schemas["ActionSubmissionsCorrect"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": {"$ref": "#/components/schemas/ActionSubmissionsCorrectData"},
        },
        ["operation_id", "expected_revision", "data"],
    )
    correct = deepcopy(paths[prefix + "submissions/{object_id}/actions/submit"])
    correct["post"].update(
        operationId="action_submissions_correct",
        summary="action submissions correct",
        **{"x-capability": "submission.correct", "x-contract-version": ROUNDS_VERSION},
    )
    correct["post"]["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ActionSubmissionsCorrect"
    }
    paths[prefix + "submissions/{object_id}/actions/correct"] = correct
    policy["operations"] = [
        p for p in policy["operations"] if p["operation_id"] != "action_submissions_correct"
    ]
    policy["operations"].append(
        {
            "operation_id": "action_submissions_correct",
            "method": "POST",
            "path": prefix + "submissions/{object_id}/actions/correct",
            "capability": "submission.correct",
            "role_templates": ["AUTHOR", "ENUMERATOR"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": True,
            "additional_capabilities_when_bound": [
                "observation.submit",
                "indicator-instances.read",
                "indicator-definitions.read",
                "programmes.read",
                "workflow-templates.read",
            ],
            "state_guard": (
                "Submitted only, with every produced observation Returned by its reviewer. The corrected "
                "answers are validated against the pinned version; each returned observation gets a new "
                "revision submitted into the same review, and the corrector joins its authors."
            ),
        }
    )

    # Collection rounds (v0.27, FR-FRM-005): a supervisor's definition of one round of collection
    # on a published form version — the period, the due time and the units expected to report —
    # on the route collection-rounds, cloned from the design's assignments route.
    schemas["CollectionRoundDraftData"] = closed(
        {
            "form_id": UUID,
            "form_version": UUID,
            "period_id": UUID,
            "title": text_field(200),
            "due_at": DATE,
            "expected_units": {
                "type": "array",
                "items": {"type": "string", "pattern": UNIT_KEY},
                "maxItems": 500,
                "uniqueItems": True,
            },
        }
    )
    schemas["CollectionRoundData"] = deepcopy(schemas["CollectionRoundDraftData"])
    for name in ["", "List", "Create", "Patch"]:
        schema = deepcopy(schemas["Assignment" + name])
        text = json.dumps(schema).replace("Assignment", "CollectionRound")
        schemas["CollectionRound" + name] = json.loads(text)
    for suffix in ["", "/{object_id}"]:
        entry = json.loads(
            json.dumps(paths[prefix + "assignments" + suffix]).replace("Assignment", "CollectionRound")
        )
        for method, node in entry.items():
            if method == "parameters":
                continue
            node["operationId"] = node["operationId"].replace("assignments", "collection_rounds")
            node["summary"] = node["summary"].replace("assignments", "collection rounds")
            node["x-capability"] = node["x-capability"].replace("assignments", "collection-rounds")
            node["x-contract-version"] = ROUNDS_VERSION
        paths[prefix + "collection-rounds" + suffix] = entry
    rounds = {
        "list_collection_rounds": ("GET", "", "collection-rounds.read", READERS, False),
        "create_collection_rounds": ("POST", "", "collection-rounds.draft.create", SUPERVISORS, True),
        "get_collection_rounds": ("GET", "/{object_id}", "collection-rounds.read", READERS, False),
        "patch_collection_rounds": (
            "PATCH",
            "/{object_id}",
            "collection-rounds.draft.edit",
            SUPERVISORS,
            True,
        ),
    }
    policy["operations"] = [p for p in policy["operations"] if p["operation_id"] not in rounds]
    for op, (method, suffix, cap, roles, audited) in rounds.items():
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method,
                "path": prefix + "collection-rounds" + suffix,
                "capability": cap,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": audited,
            }
        )

    # Assignments (design route, implemented in v0.27): one stable task per round and unit. The
    # assignee changes only through reassign, which records the previous assignee and the reason
    # in the new revision; the revision chain is the history.
    assignment = {
        "round_id": UUID,
        "form_version": UUID,
        "assignee_id": UUID,
        "unit_key": {"type": "string", "pattern": UNIT_KEY},
        "due_at": DATE,
        # The design's subject scope: kept in the contract for the seeded legacy record, refused
        # on new assignments (ASSIGNMENT_SCOPE_NOT_IMPLEMENTED); this build assigns units.
        "scope_id": UUID,
    }
    schemas["AssignmentDraftData"] = closed(deepcopy(assignment))
    schemas["AssignmentData"] = closed(
        {
            **deepcopy(assignment),
            "previous_assignee_id": {"type": ["string", "null"], "format": "uuid"},
            "reason": {"type": ["string", "null"], "maxLength": 2000},
        }
    )
    schemas["AssignmentPatch"]["properties"]["data"] = {
        "allOf": [{"$ref": "#/components/schemas/AssignmentDraftData"}],
        "minProperties": 1,
    }
    for suffix, methods in [("", ["get", "post"]), ("/{object_id}", ["get", "patch"])]:
        for method in methods:
            paths[prefix + "assignments" + suffix][method]["x-contract-version"] = ROUNDS_VERSION
    paths[prefix + "assignments/{object_id}/actions/reassign"]["post"]["x-contract-version"] = ROUNDS_VERSION
    for row in policy["operations"]:
        if row["operation_id"] == "action_assignments_reassign":
            row["state_guard"] = (
                "Open (Draft) assignments only; a completed assignment is never reassigned. The new "
                "assignee must be an active principal other than the current one; the previous assignee "
                "and the reason are recorded in the new revision."
            )

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
    # Language completeness of the head revision (v0.27): every declared language with the field
    # and choice texts it still lacks. A version with a gap cannot be published.
    gap = closed(
        {
            "field_code": {"type": "string", "pattern": CODE},
            "choice_code": {"type": ["string", "null"], "maxLength": 64},
        },
        ["field_code", "choice_code"],
    )
    schemas["FormCompleteness"] = closed(
        {
            "form_id": UUID,
            "revision_id": UUID,
            "lifecycle_state": {"type": "string", "maxLength": 64},
            "default_language": {"type": ["string", "null"], "pattern": LANGUAGE},
            "languages": {
                "type": "array",
                "maxItems": 21,
                "items": closed(
                    {
                        "language": {"type": "string", "pattern": LANGUAGE},
                        "name": {"type": ["string", "null"], "maxLength": 64},
                        "complete": {"type": "boolean"},
                        "gaps": {"type": "array", "items": gap, "maxItems": 20200},
                    },
                    ["language", "name", "complete", "gaps"],
                ),
            },
            "complete": {"type": "boolean"},
        },
        ["form_id", "revision_id", "lifecycle_state", "default_language", "languages", "complete"],
    )
    # Coverage of one round (v0.27): expected units against assignments and received responses.
    # Zero expected units is not applicable, never 100 %; the percentage is Σreceived/Σexpected.
    schemas["RoundCoverage"] = closed(
        {
            "round_id": UUID,
            "form_version": UUID,
            "period_id": UUID,
            "expected_count": {"type": "integer", "minimum": 0},
            "assigned_count": {"type": "integer", "minimum": 0},
            "received_count": {"type": "integer", "minimum": 0},
            "missing_count": {"type": "integer", "minimum": 0},
            "unassigned_count": {"type": "integer", "minimum": 0},
            "coverage_percent": {"type": ["string", "null"], "pattern": r"^[0-9]{1,3}\.[0-9]{2}$"},
            "coverage_state": {"enum": ["MEASURED", "NOT_APPLICABLE"]},
            "units": {
                "type": "array",
                "maxItems": 500,
                "items": closed(
                    {
                        "unit_key": {"type": "string", "pattern": UNIT_KEY},
                        "assignment_id": {"type": ["string", "null"], "format": "uuid"},
                        "assignee_id": {"type": ["string", "null"], "format": "uuid"},
                        "assignment_state": {"type": ["string", "null"], "maxLength": 64},
                        "received": {"type": "boolean"},
                        "submission_id": {"type": ["string", "null"], "format": "uuid"},
                    },
                    [
                        "unit_key",
                        "assignment_id",
                        "assignee_id",
                        "assignment_state",
                        "received",
                        "submission_id",
                    ],
                ),
            },
        },
        [
            "round_id",
            "form_version",
            "period_id",
            "expected_count",
            "assigned_count",
            "received_count",
            "missing_count",
            "unassigned_count",
            "coverage_percent",
            "coverage_state",
            "units",
        ],
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
            **{
                "x-capability": cap,
                "x-contract-version": VERSION if op == "get_form_published" else ROUNDS_VERSION,
            },
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

    for row in policy["operations"]:
        if row["operation_id"] == "action_forms_publish":
            # Publishing opens a version to collection, a governance state change like period close
            # and report publication: fresh authentication within 300 seconds.
            row["fresh_assurance_seconds"] = 300
        if row["operation_id"] == "action_submissions_submit":
            # Submitting a response to a form with indicator bindings creates draft observations and
            # submits them for independent review exactly as a manual observation submit does, so it
            # also requires observation.submit at TENANT scope (reason OBSERVATION_SUBMIT_REQUIRED
            # when absent) and the reads that submit performs with the submitter's own access.
            row["additional_capabilities_when_bound"] = [
                "observation.submit",
                "indicator-instances.read",
                "indicator-definitions.read",
                "programmes.read",
                "workflow-templates.read",
            ]
            row["state_guard"] = (
                "Draft only; pinned published form version. When the version binds indicators, the caller "
                "must also hold observation.submit (TENANT scope, no purpose) and read access to the bound "
                "indicator instances, their definitions and programme, and the workflow template; each "
                "created observation follows the manual observation review path."
            )

    candidate = schemas["ReviewCandidate"]["properties"]
    if "Form" not in candidate["kind"]["enum"]:
        candidate["kind"]["enum"].append("Form")
        candidate["record"]["oneOf"].append({"$ref": "#/components/schemas/Form"})
    spec["info"]["version"] = policy["version"] = VERSION
