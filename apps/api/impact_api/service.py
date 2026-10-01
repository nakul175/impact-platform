"""Transactional first delivery: revisions, independent review and provisional calculations."""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from psycopg.types.json import Jsonb
from .contracts import ENTITIES, OPERATIONS, SPEC, validate
from .domain import (
    RATIO_TYPES,
    aware,
    DomainError,
    calculate,
    decimal_value,
    disaggregate,
    method_limitations,
    unavailable,
    validate_dimensions,
)
from .measurement import Measurement, coverage, definition_ready, valid_value
from .measurement_contracts import READS
from .changes import Changes
from .period_governance import PeriodGovernance
from .period_contracts import READS as PERIOD_READS
from .reporting import Reporting
from .exports import Exports
from .planning import PLANNING_KINDS, Planning
from .forms import Forms
from .imports import NAMESPACE as IMPORT_NAMESPACE, Imports
from .evidence import Evidence
from .work import WorkCenter
from .store import (
    context,
    authorize,
    scopes,
    visible_sql,
    load,
    envelope,
    write,
    references,
    audit,
    hash_data,
    canonical,
)

READ_ROUTES = {
    "programmes",
    "indicator-definitions",
    "indicator-instances",
    "periods",
    "observations",
    "workflows",
    "calculated-results",
    "reports",
    "disclosures",
    "report-templates",
    "memberships",
    "grants",
    "evidence",
    "forms",
    "connections",
    "audit-events",
    "decisions",
    "work-items",
    "notifications",
    "workflow-templates",
    "lineage-manifests",
    *READS,
    "measurement-changes",
    "snapshots",
    *PERIOD_READS,
    "frameworks",
    "targets",
    "submissions",
    "imports",
}


def request_schema(path, method):
    """The request-body schema name the contract gives this path and method, or None when the
    contract does not describe it."""
    try:
        return SPEC["paths"][path][method]["requestBody"]["content"]["application/json"]["schema"][
            "$ref"
        ].split("/")[-1]
    except (KeyError, TypeError, AttributeError):
        return None


WRITE_ROUTES = {
    "programmes",
    "indicator-definitions",
    "indicator-instances",
    "observations",
    "reports",
    "collection-plans",
    "measurement-changes",
    "frameworks",
    "targets",
    "forms",
    "submissions",
    "imports",
    "evidence",
}
REQUEST_ROUTES = {"disclosure-requests": "Disclosure"}
READ_KINDS = {route: ENTITIES[route]["entity"] for route in READ_ROUTES if route in ENTITIES} | {
    "workflow-templates": "WorkflowTemplate",
    "lineage-manifests": "LineageManifest",
    **READS,
    "measurement-changes": "MeasurementChange",
    **PERIOD_READS,
}
ACTIONS = {
    "observations": {"submit"},
    "indicator-definitions": {"submit"},
    "workflows": {"approve", "return", "reject"},
    "indicator-instances": {"calculate", "activate"},
    "programmes": {"ready", "activate", "revise"},
    "collection-plans": {"submit"},
    "measurement-changes": {"submit"},
    "periods": {"close", "restate"},
    "reports": {"submit", "publish", "withdraw", "export", "cancel-export"},
    "work-items": {"recalculate"},
    "notifications": {"acknowledge"},
    "frameworks": {"submit"},
    "targets": {"submit"},
    "forms": {"submit", "publish"},
    "submissions": {"submit"},
    "imports": {"preview", "commit", "cancel"},
    "evidence": {"attach"},
}


def operation(route, verb):
    return verb + "_" + route.replace("-", "_")


def revision(c, ctx, rev, kind, cap):
    row = c.execute(
        "SELECT * FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s", (ctx.tenant_id, rev)
    ).fetchone()
    if not row or row["object_type"] != kind or row["restriction_state"] != "AVAILABLE":
        unavailable()
    load(c, ctx, row["object_id"], kind, cap)
    return row


def source_rows(c, ctx, indicator, period):
    rows = c.execute(
        "SELECT r.object_id,r.head_revision,r.classification,v.restriction_state,v.payload FROM impact.observation_current o JOIN impact.object_registry r ON r.tenant_id=o.tenant_id AND r.object_id=o.object_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE o.tenant_id=%s AND o.indicator_id=%s AND o.event_at>=%s AND o.event_at<%s ORDER BY r.object_id LIMIT 10001",
        (ctx.tenant_id, indicator, period["starts_at"], period["ends_at"]),
    ).fetchall()
    if len(rows) > 10000:
        raise DomainError("LIMIT_EXCEEDED", 422, reason="CALCULATION_INPUT_LIMIT")
    for row in rows:
        if (
            row["restriction_state"] != "AVAILABLE"
            or row["classification"] == "RESTRICTED"
            or not scopes(c, ctx, "observations.read", row["object_id"])
        ):
            unavailable()
    return rows


def source_digest(rows):
    return hash_data([[str(r["object_id"]), str(r["head_revision"])] for r in rows]).hex()


class Service:
    def __init__(self, s, db):
        self.s, self.db = s, db
        self.measurement = Measurement(self)
        self.changes = Changes(self)
        self.periods = PeriodGovernance(self)
        self.reporting = Reporting(self)
        self.exports = Exports(self)
        self.work = WorkCenter(self)
        self.forms = Forms(self)
        self.imports = Imports(self)
        self.planning = Planning(self)
        self.evidence = Evidence(self)

    def tenants(self, identity):
        with self.db.transaction(identity=True) as c:
            ids = c.execute("SELECT * FROM impact.identity_tenants(%s)", (identity.identity_id,)).fetchall()
        result = []
        for item in ids:
            tenant = str(item["tenant_id"])
            try:
                with self.db.transaction(tenant) as c:
                    context(c, identity, tenant)
                    name = c.execute(
                        "SELECT operating_name FROM impact.tenant_current WHERE tenant_id=%s", (tenant,)
                    ).fetchone()
                    result.append(
                        {
                            "tenant_id": tenant,
                            "name": name["operating_name"] if name else "Workspace " + tenant[:6],
                        }
                    )
            except DomainError:
                continue
        return {"items": result}

    def access(self, identity, tenant):
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            return {
                "tenant_id": tenant,
                "principal_id": ctx.principal_id,
                "capabilities": sorted({g["capability"] for g in ctx.grants if g["purpose"] is None}),
                "policy_epoch": ctx.policy_epoch,
                "subject_epoch": ctx.subject_epoch,
            }

    def result(self, c, ctx, row):
        result = envelope(row)
        if row["object_type"] in {"WorkItem", "Notification"}:
            return self.work.decorate(c, ctx, row, result)
        if row["object_type"] == "MeasurementChange":
            from .changes import TARGETS

            target = row["payload"]
            load(
                c,
                ctx,
                target["target_id"],
                target["target_kind"],
                TARGETS[target["target_kind"]][0] + ".read",
            )
        if row["object_type"] == "CalculatedResult":
            bound = c.execute(
                "SELECT * FROM impact.result_binding WHERE tenant_id=%s AND result_id=%s",
                (ctx.tenant_id, row["object_id"]),
            ).fetchone()
            if bound:
                load(c, ctx, bound["indicator_id"], "IndicatorInstance", "indicator-instances.read")
                period = load(c, ctx, bound["period_id"], "Period", "periods.read")["payload"]
                stale = self.work.stale(c, ctx, row["head_revision"]) or (
                    source_digest(source_rows(c, ctx, bound["indicator_id"], period))
                    != bound["source_digest"]
                )
                plan = self.measurement.plan(c, ctx, bound["indicator_id"], bound["period_id"])
                stale = stale or (str(plan["head_revision"]) if plan else None) != (
                    str(bound["plan_revision"]) if bound["plan_revision"] else None
                )
                result["data"] = {
                    **result["data"],
                    "freshness": {**result["data"]["freshness"], "stale": stale},
                }
                if stale:
                    result["data"]["freshness"]["stale_reason"] = (
                        "Source revisions or the approved collection plan changed since this calculation."
                    )
        if row["object_type"] == "LineageManifest":
            for rev in row["payload"].get("source_revisions", []):
                revision(c, ctx, rev, "Observation", "observations.read")
            if row["payload"].get("plan_revision"):
                revision(c, ctx, row["payload"]["plan_revision"], "CollectionPlan", "collection-plans.read")
        return result

    def get(self, identity, tenant, route, obj):
        if route not in READ_ROUTES:
            unavailable()
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, operation(route, "get"), obj, hidden=True)
            return self.result(c, ctx, load(c, ctx, obj, READ_KINDS[route]))

    def cursor_binding(self, ctx, route):
        return hash_data(
            [
                ctx.tenant_id,
                ctx.principal_id,
                ctx.policy_epoch,
                ctx.subject_epoch,
                route,
                sorted(
                    [
                        str(g["object_id"]),
                        g["capability"],
                        str(g["scope_id"]),
                        str(g["expires_at"]),
                        g["purpose"] or "",
                    ]
                    for g in ctx.grants
                ),
            ]
        ).hex()

    def cursor(self, payload):
        raw = base64.urlsafe_b64encode(canonical(payload)).rstrip(b"=")
        mac = hmac.new(self.s.cookie_secret.encode(), raw, hashlib.sha256).hexdigest()
        return raw.decode() + "." + mac

    def cursor_key(self, bound, cursor):
        """The keyset position of a signed cursor, or None; a cursor that is forged, expired or bound
        to another tenant, principal, visibility or route is INVALID_CURSOR."""
        if not cursor:
            return None
        try:
            raw, mac = cursor.split(".")
            if len(cursor) > 4096 or not hmac.compare_digest(
                mac, hmac.new(self.s.cookie_secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
            ):
                raise ValueError
            data = json.loads(base64.urlsafe_b64decode(raw + "=" * ((-len(raw)) % 4)))
            if data["binding"] != bound or data["expires"] < time.time():
                raise ValueError
            return data["key"]
        except (ValueError, KeyError, TypeError):
            raise DomainError("INVALID_CURSOR", 400) from None

    def next_cursor(self, bound, key):
        return self.cursor({"binding": bound, "expires": int(time.time()) + 900, "key": key})

    def listing(self, identity, tenant, route, limit=50, cursor=None):
        if route not in READ_ROUTES:
            unavailable()
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            cap = route + ".read"
            if not any(g["capability"] == cap and g["purpose"] is None for g in ctx.grants):
                raise DomainError("POLICY_DENIED", 403)
            bound = self.cursor_binding(ctx, route)
            key = self.cursor_key(bound, cursor)
            predicate, args = visible_sql(ctx, cap)
            personal, personal_args = self.work.listing_filter(route, ctx)
            q = (
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type=%s AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' AND "
                + predicate
                + " AND "
                + personal
            )
            params = [tenant, READ_KINDS[route]] + args + personal_args
            if key:
                q += " AND (r.created_at,r.object_id)>(%s::timestamptz,%s::uuid)"
                params += key
            q += " ORDER BY r.created_at,r.object_id LIMIT %s"
            params += [limit + 1]
            rows = c.execute(q, params).fetchall()
            page = rows[:limit]
            next_cursor = None
            if len(rows) > limit:
                next_cursor = self.cursor(
                    {
                        "binding": bound,
                        "expires": int(time.time()) + 900,
                        "key": [page[-1]["created_at"].isoformat(), str(page[-1]["object_id"])],
                    }
                )
            return {
                "items": [self.result(c, ctx, r) for r in page],
                "next_cursor": next_cursor,
                "scope_label": "Records permitted by your current access",
            }

    def validate_data(self, c, ctx, kind, data, owner_id=None):
        validate(kind + "Data", data)
        references(c, ctx, kind, data)
        if kind in PLANNING_KINDS:
            self.planning.validate(c, ctx, kind, data, owner_id)
        if kind == "MeasurementChange":
            self.changes.validate(c, ctx, data)
        if kind == "Form":
            self.forms.validate_form(c, ctx, data)
        if kind == "CollectionPlan":
            self.measurement.validate_plan(c, ctx, data)
        if kind == "Programme":
            for field, ref_kind, cap in [
                ("reporting_calendar_id", "ReportingCalendar", "reporting-calendars.read"),
                ("geography_id", "Geography", "geographies.read"),
            ]:
                if data.get(field):
                    load(c, ctx, data[field], ref_kind, cap)
        if kind == "IndicatorInstance" and data.get("programme_id"):
            programme = load(c, ctx, data["programme_id"], "Programme", "programmes.read")
            if programme["lifecycle_state"] not in {"Draft", "Active"}:
                raise DomainError("INVALID_STATE", 409, reason="PROGRAMME_CONFIGURATION_FROZEN")
        if (
            kind == "Programme"
            and data.get("starts_at")
            and data.get("ends_at")
            and datetime.fromisoformat(data["starts_at"].replace("Z", "+00:00"))
            > datetime.fromisoformat(data["ends_at"].replace("Z", "+00:00"))
        ):
            raise DomainError("VALIDATION_FAILED", reason="DATE_ORDER")
        if kind == "IndicatorInstance" and data.get("definition_version"):
            d = revision(
                c, ctx, data["definition_version"], "IndicatorDefinition", "indicator-definitions.read"
            )
            head = load(c, ctx, d["object_id"])
            if (
                head["lifecycle_state"] != "Approved"
                or str(head["head_revision"]) != data["definition_version"]
            ):
                raise DomainError("INVALID_STATE", 409)
        if kind == "Observation":
            for field in ["event_at", "captured_at"]:
                if data.get(field) is not None:
                    aware(data[field])
            if data.get("dimension_values"):
                # Codes must belong to the scheme pinned by the indicator's approved definition; a draft
                # may still omit an exhaustive dimension, which submission then requires.
                if not data.get("indicator_id"):
                    raise DomainError("VALIDATION_FAILED", reason="INVALID_DIMENSION_VALUES")
                instance = load(c, ctx, data["indicator_id"], "IndicatorInstance", "indicator-instances.read")
                pinned = revision(
                    c,
                    ctx,
                    instance["payload"]["definition_version"],
                    "IndicatorDefinition",
                    "indicator-definitions.read",
                )["payload"]
                validate_dimensions(pinned, data, complete=False)
            if data.get("dataset_id"):
                raise DomainError("INCOMPATIBLE_MEASURE", reason="DATASET_CAPTURE_NOT_IMPLEMENTED")
            n, d = data.get("numerator"), data.get("denominator")
            if (n is None) != (d is None) or (
                data.get("value_state") != "PRESENT" and (n is not None or d is not None)
            ):
                raise DomainError("VALIDATION_FAILED", reason="INVALID_COMPONENTS")
            if n is not None and (decimal_value(n) < 0 or decimal_value(d) < 0):
                raise DomainError("VALIDATION_FAILED", reason="INVALID_COMPONENTS")
        if kind == "Report":
            self.reporting.reconcile(c, ctx, data)

    def command(self, identity, tenant, route, body, correlation, obj=None, action=None):
        if action:
            if action not in ACTIONS.get(route, set()):
                unavailable()
            op = "action_" + route.replace("-", "_") + "_" + action.replace("-", "_")
        else:
            if route not in WRITE_ROUTES and route not in REQUEST_ROUTES:
                unavailable()
            op = (
                "request_disclosure"
                if route == "disclosure-requests"
                else operation(route, "patch" if obj else "create")
            )
        path = (
            "/v1/tenants/{tenant_id}/"
            + route
            + ("/{object_id}" if obj else "")
            + ("/actions/" + action if action else "")
        )
        contract = request_schema(path, "post" if action or not obj else "patch")
        if contract is None or op not in OPERATIONS:
            # A route the code knows but the regenerated contract or policy does not describe is
            # not served: the same not-found envelope as any other unknown route, never a 503.
            unavailable()
        validate(contract, body)
        fingerprint = hash_data([op, obj, body])
        now = datetime.now(timezone.utc)
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, op, obj, hidden=bool(obj))
            if action in {
                "submit",
                "calculate",
                "activate",
                "ready",
                "revise",
                "close",
                "restate",
                "recalculate",
                "publish",
                "withdraw",
                "preview",
                "commit",
                "cancel",
                "export",
                "cancel-export",
            } and not any(
                g["capability"] == OPERATIONS[op]["capability"]
                and g["scope_type"] == "TENANT"
                and g["purpose"] is None
                for g in ctx.grants
            ):
                raise DomainError("POLICY_DENIED", 403, reason="DERIVED_SCOPE_NOT_IMPLEMENTED")
            # Serializes writes per tenant so source sets and calculations are consistent.
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                load(c, ctx, old["outcome"]["object_id"])
                return old["outcome"]
            previous = load(c, ctx, obj, READ_KINDS[route], lock=True) if obj else None
            if previous and str(previous["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            kind = REQUEST_ROUTES.get(route, READ_KINDS.get(route))
            if route == "disclosure-requests":
                receipt = self.reporting.request_disclosure(c, ctx, body["data"])
            elif action == "submit" and kind == "Submission":
                receipt = self.forms.submit(c, ctx, previous, body["data"], correlation)
            elif action == "publish" and kind == "Form":
                receipt = self.forms.publish(c, ctx, previous, body["data"])
            elif kind == "ImportJob" and action == "preview":
                receipt = self.imports.preview(c, ctx, previous)
            elif kind == "ImportJob" and action == "commit":
                receipt = self.imports.commit(c, ctx, previous, body["data"], correlation)
            elif kind == "ImportJob" and action == "cancel":
                receipt = self.imports.cancel(c, ctx, previous, body["data"])
            elif kind == "ImportJob" and not action:
                receipt = self.imports.save(c, ctx, previous, body["data"])
            elif action == "submit":
                receipt = self.submit(c, ctx, kind, previous, body["data"])
            elif action in {"approve", "return", "reject"}:
                receipt = self.review(c, ctx, previous, action, body["data"], correlation)
            elif action == "calculate":
                receipt = self.calculate(c, ctx, previous, body["data"], correlation=correlation)
            elif action in {"ready", "activate", "revise"}:
                receipt = self.measurement.transition(c, ctx, kind, previous, action, body["data"])
            elif action == "close":
                receipt = self.periods.close_request(c, ctx, previous, body["data"])
            elif action == "restate":
                receipt = self.periods.restate_request(c, ctx, previous, body["data"])
            elif action == "recalculate":
                receipt = self.work.recalculate(c, ctx, previous, body["data"], correlation)
            elif action == "acknowledge":
                receipt = self.work.acknowledge(c, ctx, previous, body["data"])
            elif action == "publish":
                receipt = self.reporting.publish(c, ctx, previous, body["data"])
            elif action == "withdraw":
                receipt = self.reporting.withdraw(c, ctx, previous, body["data"], correlation)
            elif action == "attach":
                receipt = self.evidence.attach(c, ctx, previous, body["data"])
            elif action == "export":
                receipt = self.exports.request(c, ctx, previous, body["data"])
            elif action == "cancel-export":
                receipt = self.exports.cancel(c, ctx, previous, body["data"])
            else:
                # A published form is revised by a new draft revision: the published version stays in
                # the publication register and keeps serving collection until a successor publishes.
                editable = {"Draft", "Returned", "Published"} if kind == "Form" else {"Draft", "Returned"}
                if previous and previous["lifecycle_state"] not in editable:
                    raise DomainError("INVALID_STATE", 409)
                data = {**(previous["payload"] if previous else {}), **body["data"]}
                if kind == "Observation":
                    data["approval_state"] = "DRAFT"
                if kind == "Observation" and data.get("source_namespace") in {"FORM", IMPORT_NAMESPACE}:
                    # Reserved for observations produced from a submitted form response or a
                    # committed import batch.
                    raise DomainError("VALIDATION_FAILED", reason="SOURCE_NAMESPACE_RESERVED")
                if kind == "Submission":
                    data["review_state"] = "DRAFT"
                    self.forms.validate_submission(c, ctx, data, previous)
                if kind == "Target":
                    # Pinned again by the next submission; never carried into an edited draft.
                    data.pop("indicator_version", None)
                if kind == "Evidence":
                    # Name, media type, size, digest and verdict come from the CLEAN upload only.
                    data = self.evidence.stamp(c, ctx, data, previous)
                if kind == "Framework":
                    data = self.planning.stamp_exceptions(
                        c, ctx, previous["payload"] if previous else None, data
                    )
                self.validate_data(
                    c, ctx, kind, data, str(previous["owner_id"]) if previous else ctx.principal_id
                )
                if kind == "Observation" and data.get("source_namespace") and data.get("source_key"):
                    existing = c.execute(
                        "SELECT object_id FROM impact.source_key_registry WHERE tenant_id=%s AND namespace=%s AND source_key=%s",
                        (tenant, data["source_namespace"], data["source_key"]),
                    ).fetchone()
                    if existing and str(existing["object_id"]) != obj:
                        raise DomainError("SOURCE_KEY_CONFLICT", 409)
                receipt = write(c, ctx, kind, data, previous=previous)
                if kind == "Observation" and data.get("source_namespace") and data.get("source_key"):
                    c.execute(
                        "INSERT INTO impact.source_key_registry VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                        (tenant, data["source_namespace"], data["source_key"], receipt["object_id"]),
                    )
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt

    def submit(self, c, ctx, kind, row, data):
        if row["lifecycle_state"] not in {"Draft", "Returned"}:
            raise DomainError("INVALID_STATE", 409)
        payload = dict(row["payload"])
        required = (
            [
                "source_namespace",
                "source_key",
                "indicator_id",
                "event_at",
                "captured_at",
                "capture_zone",
                "value_state",
                "source_version",
            ]
            if kind == "Observation"
            else [
                "code",
                "name",
                "measurement_type",
                "unit",
                "population",
                "inclusion",
                "exclusion",
                "method",
                "source_mode",
                "time_semantic",
                "combination_rule",
                "display_decimals",
            ]
        )
        if kind == "CollectionPlan":
            required = ["title", "indicator_id", "period_id", "obligations"]
        if kind == "MeasurementChange":
            required = ["target_kind", "target_id", "target_revision", "reason", "proposed_data"]
        if kind == "Report":
            required = ["template_version", "snapshot_id", "language", "audience_class", "sections"]
        if kind == "Form":
            required = []
            payload = self.forms.prepare_submit(c, ctx, row)
        if kind in PLANNING_KINDS:
            # Framework completeness and target rules are checked, and the target's definition
            # revision pinned, by the planning module.
            required = []
            payload = self.planning.prepare_submit(c, ctx, kind, row)
        if any(k not in payload or payload[k] in (None, "") for k in required):
            raise DomainError("VALIDATION_FAILED", reason="SUBMISSION_INCOMPLETE")
        if kind == "CollectionPlan":
            payload["indicator_revision"] = str(
                load(c, ctx, payload["indicator_id"], "IndicatorInstance", "indicator-instances.read")[
                    "head_revision"
                ]
            )
        self.validate_data(c, ctx, kind, payload, str(row["owner_id"]))
        candidate_memberships = []
        if kind == "IndicatorDefinition":
            definition_ready(payload)
        if kind == "CollectionPlan":
            self.measurement.validate_plan(c, ctx, payload, complete=True)
        if kind == "Report":
            self.reporting.reconcile(c, ctx, payload, complete=True)
        if kind == "Observation":
            instance = load(c, ctx, payload["indicator_id"], "IndicatorInstance", "indicator-instances.read")
            programme = load(c, ctx, instance["payload"]["programme_id"], "Programme", "programmes.read")
            if instance["lifecycle_state"] != "Active" or programme["lifecycle_state"] != "Active":
                raise DomainError("INVALID_STATE", 409, reason="ACTIVE_MEASUREMENT_REQUIRED")
            self.periods.assert_source_mutable(
                c, ctx, payload["indicator_id"], payload["event_at"], row["object_id"]
            )
            reviewer = instance["payload"].get("reviewer_id")
            if reviewer:
                if not self.measurement.eligible(c, ctx, reviewer, "workflow.approve"):
                    raise DomainError("INVALID_STATE", 409, reason="ASSIGNMENT_INELIGIBLE")
                candidate_memberships = [str(self.measurement.principal(c, ctx, reviewer)["membership_id"])]
            definition = revision(
                c,
                ctx,
                instance["payload"]["definition_version"],
                "IndicatorDefinition",
                "indicator-definitions.read",
            )["payload"]
            if definition["source_mode"] != "MANUAL":
                raise DomainError("INCOMPATIBLE_MEASURE")
            validate_dimensions(definition, payload)
            if payload["value_state"] == "PRESENT" and not valid_value(definition, payload):
                raise DomainError("VALIDATION_FAILED", reason="INVALID_MEASUREMENT_VALUE")
            if definition["measurement_type"] in RATIO_TYPES and payload["value_state"] == "PRESENT":
                if payload.get("numerator") is None or payload.get("denominator") is None:
                    raise DomainError("VALIDATION_FAILED", reason="COMPONENTS_REQUIRED")
                if definition["measurement_type"] == "PERCENTAGE" and decimal_value(
                    payload["numerator"]
                ) > decimal_value(payload["denominator"]):
                    raise DomainError("VALIDATION_FAILED", reason="INVALID_COMPONENTS")
            payload["approval_state"] = "SUBMITTED"
        template_row = revision(
            c, ctx, data["workflow_version"], "WorkflowTemplate", "workflow-templates.read"
        )
        template_head = load(c, ctx, template_row["object_id"])
        if (
            template_head["lifecycle_state"] != "Active"
            or str(template_head["head_revision"]) != data["workflow_version"]
        ):
            raise DomainError("INVALID_STATE", 409, reason="ACTIVE_WORKFLOW_REQUIRED")
        template = template_row["payload"]
        if template.get("required_approvals") != 1 or template.get("independent") is not True:
            raise DomainError("INVALID_STATE", 409, reason="UNSUPPORTED_WORKFLOW")
        candidate = write(c, ctx, kind, payload, "Submitted", row, track_author=False)
        workflow = write(
            c,
            ctx,
            "Workflow",
            {
                "candidate_id": str(row["object_id"]),
                "candidate_revision": candidate["revision_id"],
                "workflow_version": data["workflow_version"],
                "stages": [
                    {
                        "stage_id": str(uuid4()),
                        "position": 0,
                        "required_approvals": 1,
                        "candidate_membership_ids": candidate_memberships,
                        "required_capability": "workflow.approve",
                        "independent": True,
                    }
                ],
            },
            "InReview",
            track_author=False,
        )
        c.execute(
            "INSERT INTO impact.workflow_author SELECT tenant_id,%s,natural_identity_id,%s FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s",
            (workflow["object_id"], candidate["revision_id"], ctx.tenant_id, row["object_id"]),
        )
        if kind == "MeasurementChange":
            self.changes.protect_authors(c, ctx, payload, workflow["object_id"], candidate["revision_id"])
        return workflow

    def review(self, c, ctx, row, action, data, correlation):
        workflow = row["payload"]
        if (
            row["lifecycle_state"] != "InReview"
            or workflow["candidate_revision"] != data["candidate_revision"]
        ):
            raise DomainError("CONFLICT_VERSION", 409)
        authors = c.execute(
            "SELECT 1 FROM impact.workflow_author WHERE tenant_id=%s AND workflow_id=%s AND candidate_revision=%s AND natural_identity_id=%s",
            (ctx.tenant_id, row["object_id"], data["candidate_revision"], ctx.identity.natural_identity_id),
        ).fetchone()
        if authors:
            raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
        stages = workflow.get("stages", [])
        if len(stages) != 1 or stages[0]["required_approvals"] != 1 or not stages[0]["independent"]:
            raise DomainError("INVALID_STATE", 409, reason="UNSUPPORTED_WORKFLOW")
        stage = stages[0]
        if not scopes(c, ctx, stage["required_capability"], row["object_id"]) or (
            stage["candidate_membership_ids"] and ctx.membership_id not in stage["candidate_membership_ids"]
        ):
            raise DomainError("POLICY_DENIED", 403)
        candidate = load(c, ctx, workflow["candidate_id"], lock=True)
        if candidate["object_type"] not in {
            "Observation",
            "IndicatorDefinition",
            "CollectionPlan",
            "MeasurementChange",
            "PeriodClose",
            "RestatementRequest",
            "Report",
            "Disclosure",
            "Form",
            *PLANNING_KINDS,
        }:
            raise DomainError("INVALID_STATE", 409)
        candidate_route = next(r for r, k in READ_KINDS.items() if k == candidate["object_type"])
        if not scopes(c, ctx, candidate_route + ".read", candidate["object_id"]):
            unavailable()
        if str(candidate["head_revision"]) != data["candidate_revision"]:
            raise DomainError("CONFLICT_VERSION", 409)
        if action != "approve" and not data["reason"].strip():
            raise DomainError("VALIDATION_FAILED")
        if action == "approve" and candidate["object_type"] == "CollectionPlan":
            self.measurement.validate_plan(c, ctx, candidate["payload"], complete=True)
        if action == "approve" and candidate["object_type"] == "Observation":
            self.periods.assert_source_mutable(
                c,
                ctx,
                candidate["payload"]["indicator_id"],
                candidate["payload"]["event_at"],
                candidate["object_id"],
            )
        if action == "approve" and candidate["object_type"] == "MeasurementChange":
            self.changes.apply(c, ctx, candidate, correlation)
        if action == "approve" and candidate["object_type"] == "PeriodClose":
            self.periods.apply_close(c, ctx, candidate, correlation)
        if action == "approve" and candidate["object_type"] == "RestatementRequest":
            self.periods.apply_restatement(c, ctx, candidate, correlation)
        if action == "approve" and candidate["object_type"] == "Report":
            self.reporting.reconcile(c, ctx, candidate["payload"], complete=True)
        if action == "approve" and candidate["object_type"] == "Disclosure":
            self.reporting.validate_disclosure(c, ctx, candidate["payload"])
        if action == "approve" and candidate["object_type"] in PLANNING_KINDS:
            self.planning.check_approval(c, ctx, candidate)
        if action == "approve" and candidate["object_type"] == "Form":
            self.forms.check_approval(c, ctx, candidate)
        decision_id = str(uuid4())
        now = datetime.now(timezone.utc)
        c.execute(
            "INSERT INTO impact.review_decision VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                decision_id,
                row["object_id"],
                stage["stage_id"],
                ctx.identity.natural_identity_id,
                data["candidate_revision"],
                action.upper(),
                now,
            ),
        )
        write(
            c,
            ctx,
            "Decision",
            {
                "candidate_revision": data["candidate_revision"],
                "workflow_version": workflow["workflow_version"],
                "action": action.upper(),
                "reason": data["reason"],
                "evidence_revisions": [],
                "actor_id": ctx.principal_id,
                "decided_at": now.isoformat(),
            },
            "Recorded",
            object_id=decision_id,
            track_author=False,
        )
        state = {"approve": "Approved", "return": "Returned", "reject": "Rejected"}[action]
        payload = dict(candidate["payload"])
        if candidate["object_type"] == "Observation":
            payload["approval_state"] = state.upper()
        approved = write(c, ctx, candidate["object_type"], payload, state, candidate, track_author=False)
        if action == "approve" and candidate["object_type"] == "CollectionPlan":
            c.execute(
                "INSERT INTO impact.collection_plan_binding VALUES(%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    payload["indicator_id"],
                    payload["period_id"],
                    candidate["object_id"],
                    approved["revision_id"],
                ),
            )
            self.work.invalidate(
                c,
                ctx,
                payload["indicator_id"],
                payload["period_id"],
                approved["revision_id"],
                "PLAN_APPROVED",
                correlation,
            )
        if action == "approve" and candidate["object_type"] == "Observation":
            self.work.invalidate_observation(
                c,
                ctx,
                payload,
                approved["revision_id"],
                "SOURCE_APPROVED",
                correlation,
            )
        if action == "approve" and candidate["object_type"] == "Report":
            self.reporting.bind(c, ctx, candidate, approved)
        if action == "approve" and candidate["object_type"] in PLANNING_KINDS:
            self.planning.record_approval(c, ctx, candidate, approved, row)
        return write(c, ctx, "Workflow", workflow, state, row, track_author=False)

    def calculate(self, c, ctx, indicator, data, correlation=None):
        programme = load(c, ctx, indicator["payload"]["programme_id"], "Programme", "programmes.read")
        if indicator["lifecycle_state"] != "Active" or programme["lifecycle_state"] != "Active":
            raise DomainError("INVALID_STATE", 409, reason="ACTIVE_MEASUREMENT_REQUIRED")
        period = load(c, ctx, data["period_id"], "Period", "periods.read")
        if period["lifecycle_state"] != "Open":
            raise DomainError("INVALID_STATE", 409, reason="OPEN_CALENDAR_PERIOD_REQUIRED")
        period_state = self.periods.state(c, ctx, programme["object_id"], period["object_id"])[
            "lifecycle_state"
        ]
        if period_state not in {"Open", "RestatementOpen"}:
            raise DomainError("INVALID_STATE", 409, reason="OPEN_PERIOD_REQUIRED")
        if (
            period_state == "RestatementOpen"
            and not c.execute(
                "SELECT 1 FROM impact.restatement_source_permission WHERE tenant_id=%s AND programme_id=%s AND period_id=%s AND expires_at>now() LIMIT 1",
                (ctx.tenant_id, programme["object_id"], period["object_id"]),
            ).fetchone()
        ):
            raise DomainError("INVALID_STATE", 409, reason="RESTATEMENT_WINDOW_EXPIRED")
        definition = revision(
            c,
            ctx,
            indicator["payload"]["definition_version"],
            "IndicatorDefinition",
            "indicator-definitions.read",
        )
        rows = source_rows(c, ctx, indicator["object_id"], period["payload"])
        digest = source_digest(rows)
        cutoff = datetime.now(timezone.utc)
        plan = self.measurement.plan(c, ctx, indicator["object_id"], data["period_id"])
        measured, included_revisions = (
            coverage(plan, rows, definition["payload"], cutoff) if plan else (None, None)
        )
        numeric_rows = [
            r for r in rows if included_revisions is None or str(r["head_revision"]) in included_revisions
        ]
        for row in rows:
            # Codes were checked at submission against this pinned, immutable definition; checked again
            # so that no contribution can enter a category the approved scheme does not declare. Only an
            # approved row must be complete: a draft may still lack an exhaustive code.
            validate_dimensions(
                definition["payload"],
                row["payload"],
                complete=row["payload"].get("approval_state") == "APPROVED",
            )
        sources = [r["payload"] for r in numeric_rows]
        result = calculate(definition["payload"], sources)
        breakdown = disaggregate(definition["payload"], sources)
        now = cutoff.isoformat()
        plan_pin = {"plan_revision": str(plan["head_revision"])} if plan else {}
        lineage = write(
            c,
            ctx,
            "LineageManifest",
            {"source_revisions": [str(r["head_revision"]) for r in rows], "digest": digest, **plan_pin},
            "Recorded",
            track_author=False,
        )
        run = str(uuid4())
        scope = next(
            g["scope_id"]
            for g in ctx.grants
            if g["capability"] == "indicator.calculate"
            and g["scope_type"] == "TENANT"
            and g["purpose"] is None
        )
        c.execute(
            "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest) VALUES(%s,%s,'CALCULATION',%s,%s,'Succeeded',%s)",
            (
                ctx.tenant_id,
                run,
                ctx.principal_id,
                scope,
                Jsonb(
                    {
                        "source_revisions": [str(r["head_revision"]) for r in rows],
                        "digest": digest,
                        **plan_pin,
                    }
                ),
            ),
        )
        approved = sum(
            r["payload"].get("approval_state") == "APPROVED" and r["payload"].get("value_state") == "PRESENT"
            for r in rows
        )
        result.update(
            indicator_version=indicator["payload"]["definition_version"],
            period_id=data["period_id"],
            dimensions={},
            **({"disaggregation": breakdown} if definition["payload"].get("disaggregation") else {}),
            run_id=run,
            mode="PROVISIONAL",
            coverage=measured
            or {
                "expected_count": 0,
                "received_count": len(rows),
                "approved_count": approved,
                "excluded_count": len(rows) - approved,
                "complete": False,
            },
            freshness={"calculated_at": now, "source_cutoff_at": now, "stale": False},
            limitations=[
                {
                    "code": "PERIOD_CLOSE_REQUIRED" if plan else "COLLECTION_PLAN_REQUIRED",
                    "message": "Coverage uses the approved plan. A governed period close is required for official results."
                    if plan
                    else "Expected coverage is not configured; this result remains provisional.",
                }
            ]
            + method_limitations(definition["payload"]),
            lineage_manifest_id=lineage["object_id"],
        )
        receipt = write(c, ctx, "CalculatedResult", result, "Calculated", track_author=False)
        excepted_keys = {
            (item["source_namespace"], item["source_key"])
            for item in (plan["payload"]["obligations"] if plan else [])
            if item.get("eligibility", "REQUIRED") == "EXCEPTED"
        }
        for row in rows:
            included = (
                row["payload"].get("approval_state") == "APPROVED"
                and row["payload"].get("value_state") == "PRESENT"
            )
            if included_revisions is not None:
                included = str(row["head_revision"]) in included_revisions
            c.execute(
                "INSERT INTO impact.lineage_edge VALUES(%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    receipt["revision_id"],
                    row["head_revision"],
                    str(row["object_id"]),
                    "INCLUDED" if included else "EXCLUDED",
                    None
                    if included
                    else "APPROVED_OBLIGATION_EXCLUSION"
                    if (
                        row["payload"].get("source_namespace"),
                        row["payload"].get("source_key"),
                    )
                    in excepted_keys
                    else "NOT_ELIGIBLE_UNDER_PLAN"
                    if plan
                    else "NOT_APPROVED_PRESENT",
                ),
            )
        c.execute(
            "INSERT INTO impact.result_binding(tenant_id,result_id,indicator_id,period_id,source_digest,plan_revision) VALUES(%s,%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                receipt["object_id"],
                indicator["object_id"],
                data["period_id"],
                digest,
                plan_pin.get("plan_revision"),
            ),
        )
        self.work.resolve(
            c,
            ctx,
            indicator["object_id"],
            data["period_id"],
            receipt,
            correlation or str(uuid4()),
        )
        return receipt

    def receipt(self, identity, tenant, opid, command_type):
        if command_type not in OPERATIONS:
            unavailable()
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            row = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, command_type, opid),
            ).fetchone()
            if not row:
                unavailable()
            outcome = row["outcome"]
            load(c, ctx, outcome["object_id"])
            authorize(c, ctx, command_type, outcome["object_id"], hidden=True)
            return outcome
