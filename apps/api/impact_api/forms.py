"""Web forms (v0.20): form versions with independent approval and publication, and submissions that
become observations through the existing observation review path.

A form version is a Form revision. Its fields, answer rules and indicator bindings live inside the
revision, so the version a reviewer approves is exactly the version collection is validated
against. Publication writes one row into the insert-only `impact.form_publication` register; a
submission pins the published revision it was captured on and, when that version has since been
superseded, is kept unchanged and quarantined rather than mapped or completed (FR-FRM-003)."""

from datetime import datetime, timezone
from decimal import localcontext

from .domain import RATIO_TYPES, DomainError, decimal_value, ratio, stored, validate_dimensions
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
        declared = set()
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
                field = dimensions.get(dim["code"])
                if field and not {ch["code"] for ch in field.get("choices") or []} <= {
                    cat["code"] for cat in dim["categories"]
                }:
                    raise fail("ANSWER_CODE_NOT_ALLOWED")
                if field and dim.get("multiselect"):
                    raise fail("FORM_BINDING_INVALID")
        if set(dimensions) - declared and (complete or indicators):
            raise fail("FORM_BINDING_INVALID")

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

    # Submissions --------------------------------------------------------------------------------
    def validate_submission(self, c, ctx, data, previous=None):
        if previous and any(previous["payload"].get(k) != data.get(k) for k in ["form_version", "unit_key"]):
            raise fail("FORM_VERSION_IMMUTABLE")
        if not data.get("form_version"):
            return None
        version = self.version_of(c, ctx, data["form_version"])
        evaluate(version["payload"], data.get("answers") or {}, complete=False)
        return version

    def submit(self, c, ctx, row, data, correlation=None):
        from .service import revision

        if row["lifecycle_state"] != "Draft":
            raise DomainError("INVALID_STATE", 409)
        payload = dict(row["payload"])
        if any(not payload.get(k) for k in ["form_version", "event_at", "captured_at", "capture_zone"]):
            raise fail("SUBMISSION_INCOMPLETE")
        version = self.version_of(c, ctx, payload["form_version"])
        current = self.publication(c, ctx, version["form_id"])
        stamped = {
            **payload,
            "server_received_at": datetime.now(timezone.utc).isoformat(),
            "authenticated_uploader_id": ctx.principal_id,
            "original_author_id": str(row["created_by"]),
            "observation_ids": [],
        }
        if current["version_number"] != version["version_number"]:
            # Captured on a superseded version: kept exactly as received, never completed or mapped
            # to the new version, and contributes nothing (FR-FRM-003, FSD ST06 Quarantined).
            stamped.update(review_state="QUARANTINED", quarantine_reason="FORM_VERSION_SUPERSEDED")
            return write(c, ctx, "Submission", stamped, "Quarantined", row, track_author=False)
        form = version["payload"]
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
        for indicator_id, roles in bound.items():
            instance = load(c, ctx, indicator_id, "IndicatorInstance")
            definition = revision(
                c,
                ctx,
                instance["payload"]["definition_version"],
                "IndicatorDefinition",
                "indicator-definitions.read",
            )["payload"]
            observation = self.observation(c, ctx, row, payload, definition, roles, state, dimension_answers)
            observation["indicator_id"] = indicator_id
            stamped["observation_ids"].append(
                self.record(c, ctx, observation, data["workflow_version"], correlation)
            )
        stamped["review_state"] = "SUBMITTED"
        stamped["quarantine_reason"] = None
        return write(c, ctx, "Submission", stamped, "Submitted", row, track_author=False)

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

    def record(self, c, ctx, data, workflow_version, correlation=None):
        """Write one draft observation under the response's source identity and submit it into the
        existing independent review, exactly as a manual observation is submitted. The observation
        and its review workflow each get their own audit and outbox event in this transaction, as a
        manual create and submit would; the command's receipt is the submission's."""
        tenant = ctx.tenant_id
        if c.execute(
            "SELECT 1 FROM impact.source_key_registry WHERE tenant_id=%s AND namespace=%s AND source_key=%s",
            (tenant, data["source_namespace"], data["source_key"]),
        ).fetchone():
            raise DomainError("SOURCE_KEY_CONFLICT", 409)
        data = {**data, "approval_state": "DRAFT"}
        self.service.validate_data(c, ctx, "Observation", data, ctx.principal_id)
        receipt = write(c, ctx, "Observation", data)
        c.execute(
            "INSERT INTO impact.source_key_registry VALUES(%s,%s,%s,%s)",
            (tenant, data["source_namespace"], data["source_key"], receipt["object_id"]),
        )
        draft = load(c, ctx, receipt["object_id"], "Observation", lock=True)
        workflow = self.service.submit(c, ctx, "Observation", draft, {"workflow_version": workflow_version})
        submitted = load(c, ctx, receipt["object_id"], "Observation")
        op = "action_submissions_submit"
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
