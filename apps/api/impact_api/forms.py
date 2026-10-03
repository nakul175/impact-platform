"""Web forms (v0.20): form versions with independent approval and publication, and submissions that
become observations through the existing observation review path.

A form version is a Form revision. Its fields, answer rules and indicator bindings live inside the
revision, so the version a reviewer approves is exactly the version collection is validated
against. Publication writes one row into the insert-only `impact.form_publication` register; a
submission pins the published revision it was captured on and, when that version has since been
superseded, is kept unchanged and quarantined rather than mapped or completed (FR-FRM-003)."""

from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal, localcontext

from .contracts import validate
from .domain import RATIO_TYPES, DomainError, aware, decimal_value, ratio, stored, validate_dimensions
from .store import audit, authorize, context, load, write

NAMESPACE = "FORM"
NUMERIC = {"DECIMAL", "INTEGER"}
MISSING_STATES = {
    "NOT_COLLECTED": "NOT_COLLECTED",
    "NOT_APPLICABLE": "NOT_APPLICABLE",
    "DECLINED": "MISSING",
    "UNKNOWN": "MISSING",
}


def fail(reason, status=422, code="VALIDATION_FAILED"):
    return DomainError(code, status, reason=reason)


def fields_of(form):
    return sorted(form.get("fields") or [], key=lambda f: f["position"])


# Languages (v0.27, FR-FRM-004) --------------------------------------------------------------------
def languages_of(form):
    """The language codes a form version offers: its default language, then each translation. A
    form without a declared default language offers none and accepts no stated language."""
    codes = [form["default_language"]] if form.get("default_language") else []
    return codes + [t["language"] for t in form.get("translation_versions") or []]


def translation_gaps(form, translation):
    """Every field label and active choice label the translation still lacks, in field order.
    Help text is optional in every language; a missing translated help falls back to nothing."""
    gaps = []
    texts = translation.get("fields") or {}
    for field in fields_of(form):
        text = texts.get(field["stable_code"]) or {}
        if not text.get("label"):
            gaps.append({"field_code": field["stable_code"], "choice_code": None})
        labels = text.get("choices") or {}
        for choice in field.get("choices") or []:
            if choice.get("active", True) and not labels.get(choice["code"]):
                gaps.append({"field_code": field["stable_code"], "choice_code": choice["code"]})
    return gaps


def language_completeness(form):
    languages = [
        {
            "language": t["language"],
            "name": t.get("name"),
            "complete": not translation_gaps(form, t),
            "gaps": translation_gaps(form, t),
        }
        for t in form.get("translation_versions") or []
    ]
    return {
        "default_language": form.get("default_language"),
        "languages": languages,
        "complete": all(entry["complete"] for entry in languages),
    }


def validate_translations(form, complete):
    """Translations only add text under stable codes: no unknown field or choice code, one entry
    per language, never the default language twice, and never a translation without a declared
    default language (there would be nothing to fall back to). A complete version has no gaps."""
    translations = form.get("translation_versions") or []
    if translations and not form.get("default_language"):
        raise fail("FORM_LANGUAGE_INVALID")
    codes = [t["language"] for t in translations]
    if len(set(codes)) != len(codes) or form.get("default_language") in codes:
        raise fail("FORM_LANGUAGE_INVALID")
    by_code = {f["stable_code"]: f for f in form.get("fields") or []}
    for translation in translations:
        for code, text in (translation.get("fields") or {}).items():
            field = by_code.get(code)
            if not field:
                raise fail("FORM_TRANSLATION_INVALID")
            allowed = {ch["code"] for ch in field.get("choices") or []}
            if set(text.get("choices") or {}) - allowed:
                raise fail("FORM_TRANSLATION_INVALID")
        if complete and translation_gaps(form, translation):
            raise fail("FORM_TRANSLATION_INCOMPLETE")


def answer_value(field, answer):
    """Check one supplied answer against its field. Returns None for an explicit MISSING answer,
    otherwise the answer's value as a string (decimal string, integer string, code or text)."""
    kind = answer["kind"]
    if kind == "MISSING":
        return None
    if kind != field.get("field_type"):
        raise fail("ANSWER_TYPE_MISMATCH")
    value = answer["value"]
    if kind == "BOOLEAN":
        return "true" if value else "false"
    if kind == "SINGLE_CHOICE":
        if value not in {c["code"] for c in field.get("choices", []) if c.get("active", True)}:
            raise fail("ANSWER_CODE_NOT_ALLOWED")
        return value
    if kind == "TEXT":
        if field.get("max_length") and len(value) > field["max_length"]:
            raise fail("ANSWER_OUT_OF_RANGE")
        return value
    number = decimal_value(value) if kind == "DECIMAL" else decimal_value(str(value))
    low, high = field.get("minimum"), field.get("maximum")
    if (low is not None and number < decimal_value(low)) or (
        high is not None and number > decimal_value(high)
    ):
        raise fail("ANSWER_OUT_OF_RANGE")
    return str(value) if kind == "INTEGER" else value


def evaluate(form, answers, complete):
    """Validate a response against a form version. Returns {code: (relevant, value_or_None,
    answer_or_None)} in field order. Relevance is evaluated in position order, so a field depends
    only on earlier fields and no cycle can form. A draft (complete=False) checks only what is
    supplied; a submission also requires every relevant required field and refuses answers to
    fields that are not relevant, so a tampered payload cannot carry a hidden answer."""
    fields = fields_of(form)
    codes = {f["stable_code"] for f in fields}
    if set(answers) - codes:
        raise fail("ANSWER_FIELD_UNKNOWN")
    state = {}
    for field in fields:
        code = field["stable_code"]
        rule = field.get("relevant_when")
        relevant = True
        if rule:
            upstream = state[rule["field_code"]]
            relevant = upstream[0] and upstream[1] == rule["equals"]
        answer = answers.get(code)
        value = answer_value(field, answer) if answer else None
        if complete and not relevant and answer and answer != {"kind": "MISSING", "reason": "NOT_APPLICABLE"}:
            raise fail("ANSWER_NOT_RELEVANT")
        if complete and relevant and field.get("required") and not answer:
            raise fail("REQUIRED_ANSWER_MISSING")
        state[code] = (relevant, value, answer)
    return state


class Forms:
    def __init__(self, service):
        self.service = service

    # Form versions ------------------------------------------------------------------------------
    def validate_form(self, c, ctx, data, complete=False):
        from .service import revision

        fields = data.get("fields") or []
        if complete:
            if any(not data.get(k) for k in ["code", "title", "programme_id", "compatibility_policy"]):
                raise fail("SUBMISSION_INCOMPLETE")
            if not fields:
                raise fail("FORM_FIELDS_REQUIRED")
        programme = None
        if data.get("programme_id"):
            programme = load(c, ctx, data["programme_id"], "Programme", "programmes.read")
        for key in ["field_id", "stable_code", "position"]:
            if len({f[key] for f in fields}) != len(fields):
                raise fail("FORM_FIELD_DUPLICATE")
        by_code = {f["stable_code"]: f for f in fields}
        indicators, dimensions = {}, {}
        for field in fields_of(data):
            kind = field.get("field_type")
            if complete and (not kind or not field.get("label") or "required" not in field):
                raise fail("SUBMISSION_INCOMPLETE")
            choices = field.get("choices") or []
            if kind == "SINGLE_CHOICE":
                if complete and not choices:
                    raise fail("FORM_FIELD_INVALID")
                if len({ch["code"] for ch in choices}) != len(choices):
                    raise fail("FORM_FIELD_INVALID")
            elif choices:
                raise fail("FORM_FIELD_INVALID")
            low, high = field.get("minimum"), field.get("maximum")
            if (low is not None or high is not None) and kind not in NUMERIC:
                raise fail("FORM_FIELD_INVALID")
            if low is not None and high is not None and decimal_value(low) > decimal_value(high):
                raise fail("FORM_FIELD_INVALID")
            if kind == "INTEGER" and any(v is not None and "." in v for v in [low, high]):
                raise fail("FORM_FIELD_INVALID")
            if field.get("max_length") is not None and kind != "TEXT":
                raise fail("FORM_FIELD_INVALID")
            rule = field.get("relevant_when")
            if rule:
                upstream = by_code.get(rule["field_code"])
                if not upstream or upstream["position"] >= field["position"]:
                    raise fail("FORM_RELEVANCE_INVALID")
                allowed = (
                    {"true", "false"}
                    if upstream.get("field_type") == "BOOLEAN"
                    else {ch["code"] for ch in upstream.get("choices") or []}
                    if upstream.get("field_type") == "SINGLE_CHOICE"
                    else set()
                )
                if rule["equals"] not in allowed:
                    raise fail("FORM_RELEVANCE_INVALID")
            if field.get("indicator_id"):
                if kind not in NUMERIC or not field.get("value_role") or field.get("dimension_code"):
                    raise fail("FORM_BINDING_INVALID")
                indicators.setdefault(field["indicator_id"], []).append(field)
            elif field.get("value_role"):
                raise fail("FORM_BINDING_INVALID")
            if field.get("dimension_code"):
                if kind != "SINGLE_CHOICE" or field["dimension_code"] in dimensions:
                    raise fail("FORM_BINDING_INVALID")
                dimensions[field["dimension_code"]] = field
        declared, exhaustive = set(), {}
        for indicator_id, bound in indicators.items():
            instance = load(c, ctx, indicator_id, "IndicatorInstance", "indicator-instances.read")
            if programme and instance["payload"].get("programme_id") != str(programme["object_id"]):
                raise fail("FORM_BINDING_INVALID")
            definition = revision(
                c,
                ctx,
                instance["payload"]["definition_version"],
                "IndicatorDefinition",
                "indicator-definitions.read",
            )["payload"]
            if definition.get("source_mode") != "MANUAL":
                raise DomainError("INCOMPATIBLE_MEASURE", reason="FORM_BINDING_INVALID")
            roles = sorted(f["value_role"] for f in bound)
            expected = (
                ["DENOMINATOR", "NUMERATOR"] if definition["measurement_type"] in RATIO_TYPES else ["VALUE"]
            )
            if (
                complete
                and roles != expected
                or not set(roles) <= set(expected)
                or len(set(roles)) != len(roles)
            ):
                raise fail("FORM_BINDING_INVALID")
            if len({str(f.get("relevant_when")) for f in bound}) != 1:
                raise fail("FORM_BINDING_INVALID")
            for dim in (definition.get("disaggregation") or {}).get("dimensions", []):
                declared.add(dim["code"])
                if dim.get("exhaustive"):
                    exhaustive.setdefault(dim["code"], []).extend(bound)
                field = dimensions.get(dim["code"])
                if field and not {ch["code"] for ch in field.get("choices") or []} <= {
                    cat["code"] for cat in dim["categories"]
                }:
                    raise fail("ANSWER_CODE_NOT_ALLOWED")
                if field and dim.get("multiselect"):
                    raise fail("FORM_BINDING_INVALID")
        if set(dimensions) - declared and (complete or indicators):
            raise fail("FORM_BINDING_INVALID")
        validate_translations(data, complete)
        if complete:
            # A field that supplies an exhaustive dimension must be answered wherever the bound
            # value is: required, and either always relevant or relevant under exactly the bound
            # fields' rule. Otherwise a published version could accept a PRESENT value whose
            # dimension is blank or hidden, and that response could never be submitted.
            for code in exhaustive:
                field = dimensions.get(code)
                if not field:
                    continue
                rule = field.get("relevant_when")
                if not field.get("required") or (
                    rule and any(str(rule) != str(b.get("relevant_when")) for b in exhaustive[code])
                ):
                    raise fail("FORM_DIMENSION_FIELD_INVALID")

    def prepare_submit(self, c, ctx, row):
        payload = dict(row["payload"])
        self.validate_form(c, ctx, payload, complete=True)
        return payload

    def check_approval(self, c, ctx, candidate):
        self.validate_form(c, ctx, candidate["payload"], complete=True)

    def publication(self, c, ctx, form_id):
        return c.execute(
            "SELECT * FROM impact.form_publication WHERE tenant_id=%s AND form_id=%s ORDER BY version_number DESC LIMIT 1",
            (ctx.tenant_id, str(form_id)),
        ).fetchone()

    def version_of(self, c, ctx, form_version):
        """The published register row of a form revision; unknown, unpublished and invisible
        revisions are all unavailable."""
        row = c.execute(
            "SELECT p.*,v.payload FROM impact.form_publication p JOIN impact.object_revision v ON v.tenant_id=p.tenant_id AND v.revision_id=p.form_revision WHERE p.tenant_id=%s AND p.form_revision=%s",
            (ctx.tenant_id, str(form_version)),
        ).fetchone()
        if not row:
            raise fail("FORM_VERSION_NOT_PUBLISHED", 409, "INVALID_STATE")
        load(c, ctx, row["form_id"], "Form", "forms.read")
        return row

    def publish(self, c, ctx, row, data):
        """Publish the independently approved revision: a new revision with the same content in state
        Published and one register row. The previous version stays readable and is superseded."""
        if (
            row["lifecycle_state"] != "Approved"
            or str(row["head_revision"]) != data["approved_candidate_revision"]
        ):
            raise DomainError("CONFLICT_VERSION", 409)
        self.validate_form(c, ctx, row["payload"], complete=True)
        current = self.publication(c, ctx, row["object_id"])
        receipt = write(c, ctx, "Form", row["payload"], "Published", row, track_author=False)
        c.execute(
            "INSERT INTO impact.form_publication(tenant_id,form_id,version_number,form_revision,approved_revision,supersedes_revision,published_by,published_at) VALUES(%s,%s,%s,%s,%s,%s,%s,statement_timestamp())",
            (
                ctx.tenant_id,
                str(row["object_id"]),
                current["version_number"] + 1 if current else 1,
                receipt["revision_id"],
                str(row["head_revision"]),
                str(current["form_revision"]) if current else None,
                ctx.principal_id,
            ),
        )
        return receipt

    # Collection rounds and assignments (v0.27, FR-FRM-005) --------------------------------------
    def validate_round(self, c, ctx, data, previous=None):
        """A round names a published version of its form, a period and the units expected to
        report. Form, version and period are pinned at creation; title, due time and the expected
        units may change while no assignment covers a removed unit."""
        if previous and any(
            previous["payload"].get(k) != data.get(k) for k in ["form_id", "form_version", "period_id"]
        ):
            raise fail("ROUND_IMMUTABLE")
        if any(not data.get(k) for k in ["form_id", "form_version", "period_id", "title", "due_at"]):
            raise fail("ROUND_INCOMPLETE")
        aware(data["due_at"])
        load(c, ctx, data["form_id"], "Form", "forms.read")
        version = self.version_of(c, ctx, data["form_version"])
        if str(version["form_id"]) != data["form_id"]:
            raise fail("FORM_VERSION_NOT_PUBLISHED", 409, "INVALID_STATE")
        load(c, ctx, data["period_id"], "Period", "periods.read")
        if previous:
            removed = set(previous["payload"].get("expected_units") or []) - set(
                data.get("expected_units") or []
            )
            if (
                removed
                and c.execute(
                    "SELECT 1 FROM impact.assignment_current WHERE tenant_id=%s AND round_id=%s AND unit_key=ANY(%s)",
                    (ctx.tenant_id, str(previous["object_id"]), sorted(removed)),
                ).fetchone()
            ):
                raise fail("ROUND_UNIT_ASSIGNED", 409, "INVALID_STATE")

    def validate_assignment(self, c, ctx, data, previous=None):
        """One stable task per round and unit. The round, version, unit and assignee are pinned at
        creation; only the due time is patched, and the assignee changes only through reassign."""
        if previous and any(
            previous["payload"].get(k) != data.get(k)
            for k in ["round_id", "form_version", "unit_key", "assignee_id", "previous_assignee_id", "reason"]
        ):
            raise fail("ASSIGNMENT_IMMUTABLE")
        if data.get("scope_id"):
            # The design's subject scope is not implemented: this build assigns units of a round.
            raise fail("ASSIGNMENT_SCOPE_NOT_IMPLEMENTED")
        if any(not data.get(k) for k in ["round_id", "form_version", "assignee_id", "unit_key", "due_at"]):
            raise fail("ASSIGNMENT_INCOMPLETE")
        aware(data["due_at"])
        round_row = load(c, ctx, data["round_id"], "CollectionRound", "collection-rounds.read")
        if round_row["payload"]["form_version"] != data["form_version"]:
            raise fail("ASSIGNMENT_FORM_VERSION_MISMATCH")
        if data["unit_key"] not in (round_row["payload"].get("expected_units") or []):
            raise fail("ASSIGNMENT_UNIT_NOT_EXPECTED")
        if not previous:
            if c.execute(
                "SELECT 1 FROM impact.assignment_current WHERE tenant_id=%s AND round_id=%s AND unit_key=%s",
                (ctx.tenant_id, data["round_id"], data["unit_key"]),
            ).fetchone():
                raise fail("ASSIGNMENT_UNIT_TAKEN", 409, "INVALID_STATE")
            self.assert_assignee(c, ctx, data["assignee_id"])

    def assert_assignee(self, c, ctx, principal):
        # The assignee must be a current member able to submit responses; an assignment is work,
        # never authority: it grants nothing, and approval stays with an independent reviewer.
        if not self.service.measurement.eligible(c, ctx, principal, "submission.submit"):
            raise fail("ASSIGNEE_INELIGIBLE", 409, "INVALID_STATE")

    def reassign(self, c, ctx, row, data):
        """A new revision of the same assignment with the new assignee, the previous one and the
        reason; the task identity and every earlier revision stay. A completed assignment is never
        reassigned, so the old holder can never produce a second completed visit."""
        if row["lifecycle_state"] != "Draft":
            raise fail("ASSIGNMENT_COMPLETED", 409, "INVALID_STATE")
        if data["assignee_id"] == row["payload"]["assignee_id"]:
            raise fail("ASSIGNEE_UNCHANGED")
        self.assert_assignee(c, ctx, data["assignee_id"])
        payload = {
            **row["payload"],
            "assignee_id": data["assignee_id"],
            "previous_assignee_id": row["payload"]["assignee_id"],
            "reason": data["reason"],
        }
        return write(c, ctx, "Assignment", payload, "Draft", row, track_author=False)

    def held_assignment(self, c, ctx, data, lock=False):
        """The open assignment a response fulfils, which the caller must currently hold."""
        assignment = load(c, ctx, data["assignment_id"], "Assignment", "assignments.read", lock=lock)
        if assignment["payload"].get("form_version") != data.get("form_version"):
            raise fail("ASSIGNMENT_FORM_VERSION_MISMATCH")
        if assignment["lifecycle_state"] != "Draft":
            raise fail("ASSIGNMENT_COMPLETED", 409, "INVALID_STATE")
        if assignment["payload"].get("assignee_id") != ctx.principal_id:
            raise DomainError("POLICY_DENIED", 403, reason="ASSIGNMENT_NOT_HELD")
        return assignment

    # Submissions --------------------------------------------------------------------------------
    def validate_submission(self, c, ctx, data, previous=None):
        if previous and any(
            previous["payload"].get(k) != data.get(k) for k in ["form_version", "unit_key", "assignment_id"]
        ):
            raise fail("FORM_VERSION_IMMUTABLE")
        if not data.get("form_version"):
            # The version is pinned at creation and immutable afterwards, so a draft without one
            # could never be submitted.
            raise fail("FORM_VERSION_REQUIRED")
        version = self.version_of(c, ctx, data["form_version"])
        if data.get("language") and data["language"] not in languages_of(version["payload"]):
            # The language shown to the respondent must be one the published version carries.
            raise fail("FORM_LANGUAGE_NOT_AVAILABLE")
        if data.get("assignment_id") and not previous:
            assignment = self.held_assignment(c, ctx, data)
            unit = assignment["payload"]["unit_key"]
            if data.get("unit_key") not in (None, unit):
                raise fail("ASSIGNMENT_UNIT_MISMATCH")
            # The response reports for the assigned unit, so its observations carry the unit's
            # planned source key.
            data["unit_key"] = unit
        evaluate(version["payload"], data.get("answers") or {}, complete=False)
        return version

    def submit(self, c, ctx, row, data, correlation=None):
        if row["lifecycle_state"] != "Draft":
            raise DomainError("INVALID_STATE", 409)
        payload = dict(row["payload"])
        if any(not payload.get(k) for k in ["form_version", "event_at", "captured_at", "capture_zone"]):
            raise fail("SUBMISSION_INCOMPLETE")
        version = self.version_of(c, ctx, payload["form_version"])
        current = self.publication(c, ctx, version["form_id"])
        assignment = (
            self.held_assignment(c, ctx, payload, lock=True) if payload.get("assignment_id") else None
        )
        stamped = {
            **payload,
            "server_received_at": datetime.now(timezone.utc).isoformat(),
            "authenticated_uploader_id": ctx.principal_id,
            "original_author_id": str(row["created_by"]),
            "observation_ids": [],
        }
        if current["version_number"] != version["version_number"]:
            # Captured on a superseded version: kept exactly as received, never completed or mapped
            # to the new version, and contributes nothing (FR-FRM-003, FSD ST06 Quarantined). Its
            # assignment stays open: nothing eligible was received.
            stamped.update(review_state="QUARANTINED", quarantine_reason="FORM_VERSION_SUPERSEDED")
            return write(c, ctx, "Submission", stamped, "Quarantined", row, track_author=False)
        form = version["payload"]
        self.produce(c, ctx, row, payload, form, data["workflow_version"], correlation, stamped)
        stamped["review_state"] = "SUBMITTED"
        stamped["quarantine_reason"] = None
        receipt = write(c, ctx, "Submission", stamped, "Submitted", row, track_author=False)
        if assignment:
            # The visit is complete: the assignment closes in the same transaction, so neither its
            # holder nor a later holder can produce another eligible completed visit from it.
            done = write(
                c, ctx, "Assignment", assignment["payload"], "Completed", assignment, track_author=False
            )
            audit(c, ctx, "action_submissions_submit", done, correlation)
        return receipt

    def produce(self, c, ctx, row, payload, form, workflow_version, correlation, stamped, corrections=None):
        """Validate the answers against the version and turn them into one observation per bound
        indicator, submitted into the observation review. With `corrections` (observation id per
        indicator) the observations are new revisions of those returned observations."""
        from .service import revision

        state = evaluate(form, payload.get("answers") or {}, complete=True)
        dimension_answers = {
            f["dimension_code"]: state[f["stable_code"]][1]
            for f in fields_of(form)
            if f.get("dimension_code") and state[f["stable_code"]][0] and state[f["stable_code"]][1]
        }
        bound = {}
        for field in fields_of(form):
            if field.get("indicator_id"):
                bound.setdefault(field["indicator_id"], {})[field["value_role"]] = field
        if bound and not any(
            g["capability"] == "observation.submit" and g["scope_type"] == "TENANT" and g["purpose"] is None
            for g in ctx.grants
        ):
            # A form with indicator bindings creates observations and submits them for review, so
            # the submitter must hold what a manual observation submit needs (declared in the
            # policy row of action_submissions_submit), not only submission.submit.
            raise DomainError("POLICY_DENIED", 403, reason="OBSERVATION_SUBMIT_REQUIRED")
        op = "action_submissions_correct" if corrections is not None else "action_submissions_submit"
        for indicator_id, roles in bound.items():
            instance = load(c, ctx, indicator_id, "IndicatorInstance", "indicator-instances.read")
            definition = revision(
                c,
                ctx,
                instance["payload"]["definition_version"],
                "IndicatorDefinition",
                "indicator-definitions.read",
            )["payload"]
            observation = self.observation(c, ctx, row, payload, definition, roles, state, dimension_answers)
            observation["indicator_id"] = indicator_id
            if corrections is not None:
                if indicator_id not in corrections:
                    # The version's bindings changed under the response: nothing to correct.
                    raise fail("CORRECTION_TARGET_MISSING", 409, "INVALID_STATE")
                stamped["observation_ids"].append(
                    self.record(
                        c,
                        ctx,
                        observation,
                        workflow_version,
                        correlation,
                        row["object_id"],
                        op,
                        returned=corrections[indicator_id],
                    )
                )
            else:
                stamped["observation_ids"].append(
                    self.record(c, ctx, observation, workflow_version, correlation, row["object_id"], op)
                )

    def correct(self, c, ctx, row, data, correlation=None):
        """Correction of returned work (FR-FRM-006): a Submitted response whose observations were
        all returned by their reviewer receives a new Submitted revision with the corrected answers
        and the reason; each returned observation gets a new Draft revision authored by the
        corrector and is submitted into the same independent review. Nothing reviewed is edited."""
        if row["lifecycle_state"] != "Submitted" or row["payload"].get("review_state") != "SUBMITTED":
            raise DomainError("INVALID_STATE", 409, reason="CORRECTION_REQUIRES_SUBMITTED_RESPONSE")
        payload = dict(row["payload"])
        version = self.version_of(c, ctx, payload["form_version"])
        if self.publication(c, ctx, version["form_id"])["version_number"] != version["version_number"]:
            raise fail("FORM_VERSION_SUPERSEDED", 409, "INVALID_STATE")
        returned = {}
        for observation_id in payload.get("observation_ids") or []:
            observation = load(c, ctx, observation_id, "Observation", "observations.read", lock=True)
            if observation["lifecycle_state"] != "Returned":
                raise DomainError("INVALID_STATE", 409, reason="CORRECTION_REQUIRES_RETURNED_WORK")
            returned[observation["payload"]["indicator_id"]] = observation
        if not returned:
            raise DomainError("INVALID_STATE", 409, reason="CORRECTION_REQUIRES_RETURNED_WORK")
        corrected = {**payload, "answers": data["answers"]}
        stamped = {
            **corrected,
            "server_received_at": datetime.now(timezone.utc).isoformat(),
            "authenticated_uploader_id": ctx.principal_id,
            "observation_ids": [],
            "correction_of_revision": str(row["head_revision"]),
            "correction_reason": data["reason"],
        }
        self.produce(
            c,
            ctx,
            row,
            corrected,
            version["payload"],
            data["workflow_version"],
            correlation,
            stamped,
            returned,
        )
        return write(c, ctx, "Submission", stamped, "Submitted", row)

    def observation(self, c, ctx, row, payload, definition, roles, state, dimension_answers):
        """The observation one indicator receives from one response. A blank is never zero: an
        omitted answer is MISSING, an explicit reason keeps its state, a field that is not relevant
        is NOT_APPLICABLE and only a complete answer is PRESENT."""
        indicator = next(iter(roles.values()))["indicator_id"]
        base = {
            "source_namespace": NAMESPACE,
            "source_key": (payload.get("unit_key") or str(row["object_id"])) + "/" + indicator,
            "event_at": payload["event_at"],
            "captured_at": payload["captured_at"],
            "capture_zone": payload["capture_zone"],
            "source_version": payload["form_version"],
            "value": None,
            "dimension_values": {},
        }
        entries = [state[f["stable_code"]] for f in roles.values()]
        if not entries[0][0]:
            return {**base, "value_state": "NOT_APPLICABLE"}
        values = {role: state[f["stable_code"]][1] for role, f in roles.items()}
        if any(v is None for v in values.values()):
            reasons = {(e[2] or {}).get("reason") for e in entries if e[2] and e[2]["kind"] == "MISSING"}
            states = {MISSING_STATES[r] for r in reasons if r}
            return {
                **base,
                "value_state": states.pop()
                if len(states) == 1 and len(reasons) == len(entries)
                else "MISSING",
            }
        dims = {
            d["code"]: dimension_answers[d["code"]]
            for d in (definition.get("disaggregation") or {}).get("dimensions", [])
            if d["code"] in dimension_answers
        }
        result = {**base, "value_state": "PRESENT", "dimension_values": dims}
        if definition["measurement_type"] in RATIO_TYPES:
            n, d = decimal_value(values["NUMERATOR"]), decimal_value(values["DENOMINATOR"])
            # Negative components and a PERCENTAGE numerator above its denominator are refused
            # before a zero denominator is recorded as UNDEFINED.
            if n < 0 or d < 0 or (definition["measurement_type"] == "PERCENTAGE" and n > d):
                raise fail("INVALID_COMPONENTS")
            try:
                with localcontext() as ctx_:
                    ctx_.prec = 60
                    value = ratio(definition, n, d)
            except DomainError:
                raise fail("INVALID_COMPONENTS") from None
            if value is None:
                # A zero denominator has no ratio: UNDEFINED, never zero, and carries no components.
                return {**base, "value_state": "UNDEFINED"}
            result.update(
                value=stored(value), numerator=values["NUMERATOR"], denominator=values["DENOMINATOR"]
            )
        else:
            result["value"] = values["VALUE"]
        validate_dimensions(definition, result)
        return result

    def record(
        self,
        c,
        ctx,
        data,
        workflow_version,
        correlation=None,
        submission_id=None,
        op="action_submissions_submit",
        returned=None,
    ):
        """Write one draft observation under the response's source identity and submit it into the
        existing independent review, exactly as a manual observation is submitted. The observation
        and its review workflow each get their own audit and outbox event in this transaction, as a
        manual create and submit would; the command's receipt is the submission's. A correction
        (`returned`) writes the corrected content as a new Draft revision of the returned
        observation — same object, same source key, the returned revision kept — and the corrector
        joins its authors, so the corrector can never approve it."""
        tenant = ctx.tenant_id
        data = {**data, "approval_state": "DRAFT"}
        self.service.validate_data(c, ctx, "Observation", data, ctx.principal_id)
        if returned is not None:
            if returned["payload"]["source_key"] != data["source_key"]:
                raise fail("CORRECTION_TARGET_MISSING", 409, "INVALID_STATE")
            receipt = write(c, ctx, "Observation", data, "Draft", returned)
        else:
            if c.execute(
                "SELECT 1 FROM impact.source_key_registry WHERE tenant_id=%s AND namespace=%s AND source_key=%s",
                (tenant, data["source_namespace"], data["source_key"]),
            ).fetchone():
                raise DomainError("SOURCE_KEY_CONFLICT", 409)
            receipt = write(c, ctx, "Observation", data)
            c.execute(
                "INSERT INTO impact.source_key_registry VALUES(%s,%s,%s,%s)",
                (tenant, data["source_namespace"], data["source_key"], receipt["object_id"]),
            )
        if submission_id:
            # Everyone who authored the response is an author of the observations it produces, so
            # a person who drafted the answers cannot approve them after someone else submits.
            c.execute(
                "INSERT INTO impact.object_natural_author SELECT tenant_id,%s,natural_identity_id FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s ON CONFLICT DO NOTHING",
                (receipt["object_id"], tenant, str(submission_id)),
            )
        draft = load(c, ctx, receipt["object_id"], "Observation", lock=True)
        workflow = self.service.submit(c, ctx, "Observation", draft, {"workflow_version": workflow_version})
        submitted = load(c, ctx, receipt["object_id"], "Observation")
        audit(
            c,
            ctx,
            op,
            {
                **receipt,
                "revision_id": str(submitted["head_revision"]),
                "business_state": submitted["lifecycle_state"],
            },
            correlation,
        )
        audit(c, ctx, op, workflow, correlation)
        return receipt["object_id"]

    # Read model ---------------------------------------------------------------------------------
    def read(self, identity, tenant, op, obj):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, op, obj, hidden=True)
            if op == "get_form_completeness":
                row = load(c, ctx, obj, "Form", "forms.read")
                return {
                    "form_id": str(obj),
                    "revision_id": str(row["head_revision"]),
                    "lifecycle_state": row["lifecycle_state"],
                    **language_completeness(row["payload"]),
                }
            if op == "get_round_coverage":
                return self.coverage(c, ctx, load(c, ctx, obj, "CollectionRound", "collection-rounds.read"))
            load(c, ctx, obj, "Form", "forms.read")
            versions = c.execute(
                "SELECT p.*,v.payload FROM impact.form_publication p JOIN impact.object_revision v ON v.tenant_id=p.tenant_id AND v.revision_id=p.form_revision WHERE p.tenant_id=%s AND p.form_id=%s ORDER BY p.version_number",
                (tenant, str(obj)),
            ).fetchall()
            if not versions:
                raise DomainError("RESOURCE_UNAVAILABLE", 404, reason="FORM_NOT_PUBLISHED")
            current = versions[-1]
            return {
                "form_id": str(obj),
                "version_number": current["version_number"],
                "form_version": str(current["form_revision"]),
                "approved_revision": str(current["approved_revision"]),
                "supersedes_revision": str(current["supersedes_revision"])
                if current["supersedes_revision"]
                else None,
                "published_at": current["published_at"].isoformat(),
                "data": current["payload"],
                "versions": [
                    {"version_number": v["version_number"], "form_version": str(v["form_revision"])}
                    for v in versions
                ],
            }

    def coverage(self, c, ctx, round_row):
        """Expected units of a round against their assignments and the responses submitted on
        them. A unit is received when a Submitted (not quarantined) response names its
        assignment; coverage is Σreceived/Σexpected rounded half-up to two places, and a round
        that expects no unit is not applicable rather than 100 %."""
        payload = round_row["payload"]
        expected = list(payload.get("expected_units") or [])
        rows = c.execute(
            "SELECT a.object_id,a.unit_key,a.assignee_id,r.lifecycle_state,s.object_id AS submission_id FROM impact.assignment_current a JOIN impact.object_registry r ON r.tenant_id=a.tenant_id AND r.object_id=a.object_id LEFT JOIN LATERAL (SELECT s.object_id FROM impact.submission_current s WHERE s.tenant_id=a.tenant_id AND s.assignment_id=a.object_id AND s.review_state='SUBMITTED' ORDER BY s.object_id LIMIT 1) s ON true WHERE a.tenant_id=%s AND a.round_id=%s ORDER BY a.unit_key,a.object_id",
            (ctx.tenant_id, str(round_row["object_id"])),
        ).fetchall()
        by_unit = {row["unit_key"]: row for row in rows}
        units = []
        for unit in expected:
            row = by_unit.get(unit)
            units.append(
                {
                    "unit_key": unit,
                    "assignment_id": str(row["object_id"]) if row else None,
                    "assignee_id": str(row["assignee_id"]) if row and row["assignee_id"] else None,
                    "assignment_state": row["lifecycle_state"] if row else None,
                    "received": bool(row and row["submission_id"]),
                    "submission_id": str(row["submission_id"]) if row and row["submission_id"] else None,
                }
            )
        received = sum(1 for u in units if u["received"])
        assigned = sum(1 for u in units if u["assignment_id"])
        percent = None
        if expected:
            percent = str(
                (Decimal(received) * 100 / Decimal(len(expected))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
        result = {
            "round_id": str(round_row["object_id"]),
            "form_version": payload["form_version"],
            "period_id": payload["period_id"],
            "expected_count": len(expected),
            "assigned_count": assigned,
            "received_count": received,
            "missing_count": len(expected) - received,
            "unassigned_count": len(expected) - assigned,
            "coverage_percent": percent,
            "coverage_state": "MEASURED" if expected else "NOT_APPLICABLE",
            "units": units,
        }
        return validate("RoundCoverage", result)
