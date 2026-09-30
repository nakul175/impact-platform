"""Manual measurement readiness and immutable contributor obligations.

All writes run inside Service.command's tenant lock and durable receipt transaction.
There is no background actor, inferred permission, automatic approval or period close.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from psycopg.types.json import Jsonb
from .domain import (
    RATIO_TYPES,
    DomainError,
    calculate,
    decimal_value,
    method_supported,
    unavailable,
    validate_dimensions,
    validate_scheme,
)
from .store import load, scopes, write, envelope, context, authorize


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def definition_ready(data):
    required = ["code", "name", "unit", "population", "inclusion", "exclusion", "method"]
    if any(not str(data.get(k, "")).strip() for k in required):
        raise DomainError("VALIDATION_FAILED", reason="DEFINITION_INCOMPLETE")
    ratio = data.get("measurement_type") in RATIO_TYPES
    if data.get("source_mode") != "MANUAL" or not method_supported(data):
        raise DomainError("INCOMPATIBLE_MEASURE", reason="CONFIGURATION_NOT_IMPLEMENTED")
    if ratio and any(not str(data.get(k, "")).strip() for k in ["numerator_meaning", "denominator_meaning"]):
        raise DomainError("VALIDATION_FAILED", reason="COMPONENT_MEANINGS_REQUIRED")
    validate_scheme(data)


def valid_value(definition, payload):
    if payload.get("value_state") != "PRESENT":
        return False
    try:
        validate_dimensions(definition, payload)
        if definition["measurement_type"] in RATIO_TYPES and (
            payload.get("numerator") is None or payload.get("denominator") is None
        ):
            return False
        if definition["measurement_type"] == "COUNT":
            value = decimal_value(payload.get("value"))
            if value < 0 or value != value.to_integral_value():
                return False
        calculate(definition, [{**payload, "approval_state": "APPROVED"}])
        return True
    except (DomainError, KeyError):
        return False


def coverage(plan, rows, definition, now):
    """Each explicit source pair is one obligation, never one row toward a guessed total."""
    observations = {(r["payload"].get("source_namespace"), r["payload"].get("source_key")): r for r in rows}
    keys = {(o["source_namespace"], o["source_key"]) for o in plan["payload"]["obligations"]}
    result = {
        k: 0
        for k in [
            "received_count",
            "valid_count",
            "approved_count",
            "pending_count",
            "missing_count",
            "excluded_count",
            "excepted_count",
            "overdue_count",
        ]
    }
    details, included = [], set()
    for item in plan["payload"]["obligations"]:
        row = observations.get((item["source_namespace"], item["source_key"]))
        eligibility = item.get("eligibility", "REQUIRED")
        status = "EXCEPTED" if eligibility == "EXCEPTED" else "MISSING"
        if row:
            result["received_count"] += 1
            payload = row["payload"]
            valid = valid_value(definition, payload)
            result["valid_count"] += int(valid)
            if eligibility == "EXCEPTED":
                status = "EXCEPTED"
            elif valid and payload.get("approval_state") == "APPROVED":
                status = "APPROVED"
                included.add(str(row["head_revision"]))
            elif valid and payload.get("approval_state") != "REJECTED":
                status = "PENDING"
            elif payload.get("value_state") not in {"MISSING", "NOT_COLLECTED"}:
                status = "EXCLUDED"
        result[status.lower() + "_count"] += 1
        overdue = status not in {"APPROVED", "EXCEPTED"} and instant(item["due_at"]) < now
        result["overdue_count"] += int(overdue)
        details.append({**item, "eligibility": eligibility, "status": status, "overdue": overdue})
    expected = len(details)
    required = expected - result["excepted_count"]
    result.update(
        expected_count=expected,
        required_count=required,
        unplanned_count=sum(
            (r["payload"].get("source_namespace"), r["payload"].get("source_key")) not in keys for r in rows
        ),
        complete=required > 0 and result["approved_count"] == required,
    )
    if required:
        # With no required obligation coverage is not applicable (CAL08): no percentage, never 100.
        result["approval_percent"] = format(
            (Decimal(result["approved_count"] * 100) / Decimal(required)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            ".2f",
        )
    result.update(
        plan_revision=str(plan["head_revision"]),
        obligations=details,
    )
    return result, included


class Measurement:
    def __init__(self, service):
        self.service = service

    def principal(self, c, ctx, principal):
        if not principal:
            return None
        return c.execute(
            "SELECT p.principal_id,m.object_id AS membership_id,COALESCE(mp.display_name,'Workspace member') AS display_name FROM impact.tenant_principal p JOIN impact.membership_current m ON m.tenant_id=p.tenant_id AND m.identity_id=p.identity_id JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id LEFT JOIN impact.member_profile mp ON mp.tenant_id=m.tenant_id AND mp.membership_id=m.object_id WHERE p.tenant_id=%s AND p.principal_id=%s AND p.active AND r.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now())",
            (ctx.tenant_id, str(principal)),
        ).fetchone()

    def eligible(self, c, ctx, principal, capability):
        return bool(
            self.principal(c, ctx, principal)
            and c.execute(
                "SELECT 1 FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id WHERE g.tenant_id=%s AND g.subject_id=%s AND g.capability=%s AND g.purpose IS NULL AND r.lifecycle_state='Active' AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now()) AND s.scope_type='TENANT' LIMIT 1",
                (ctx.tenant_id, principal, capability),
            ).fetchone()
        )

    def plan(self, c, ctx, indicator_id, period_id):
        binding = c.execute(
            "SELECT * FROM impact.collection_plan_binding WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s",
            (ctx.tenant_id, indicator_id, period_id),
        ).fetchone()
        if not binding:
            return None
        row = load(c, ctx, binding["plan_id"], "CollectionPlan", "collection-plans.read")
        if row["lifecycle_state"] != "Approved" or row["head_revision"] != binding["plan_revision"]:
            unavailable()
        return row

    def validate_plan(self, c, ctx, data, complete=False, approved=False):
        if complete and any(k not in data for k in ["title", "indicator_id", "period_id", "obligations"]):
            raise DomainError("VALIDATION_FAILED", reason="PLAN_INCOMPLETE")
        indicator = (
            load(c, ctx, data["indicator_id"], "IndicatorInstance", "indicator-instances.read")
            if data.get("indicator_id")
            else None
        )
        period = load(c, ctx, data["period_id"], "Period", "periods.read") if data.get("period_id") else None
        if complete:
            if data.get("indicator_revision"):
                pinned = c.execute(
                    "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_id=%s AND restriction_state='AVAILABLE'",
                    (ctx.tenant_id, indicator["object_id"], data["indicator_revision"]),
                ).fetchone()

                def semantic(p):
                    return {k: v for k, v in p.items() if k not in {"collector_id", "reviewer_id"}}

                if not pinned or semantic(pinned["payload"]) != semantic(indicator["payload"]):
                    raise DomainError("CONFLICT_VERSION", 409, reason="PLAN_INDICATOR_CHANGED")
            if period["lifecycle_state"] != "Open" or indicator["lifecycle_state"] not in {"Draft", "Active"}:
                raise DomainError("INVALID_STATE", 409, reason="OPEN_PERIOD_REQUIRED")
            programme = load(c, ctx, indicator["payload"]["programme_id"], "Programme", "programmes.read")
            if programme["lifecycle_state"] not in {"Draft", "Ready", "Active"}:
                raise DomainError("INVALID_STATE", 409)
            calendar = c.execute(
                "SELECT object_id FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s AND object_type='ReportingCalendar' AND restriction_state='AVAILABLE'",
                (ctx.tenant_id, period["payload"]["calendar_version"]),
            ).fetchone()
            if not calendar or str(calendar["object_id"]) != programme["payload"].get(
                "reporting_calendar_id"
            ):
                raise DomainError("VALIDATION_FAILED", reason="CALENDAR_MISMATCH")
            p = programme["payload"]
            if (
                not p.get("starts_at")
                or not p.get("ends_at")
                or instant(period["payload"]["starts_at"]) < instant(p["starts_at"])
                or instant(period["payload"]["ends_at"]) > instant(p["ends_at"])
            ):
                raise DomainError("VALIDATION_FAILED", reason="PERIOD_OUTSIDE_PROGRAMME")
        seen = set()
        if complete:
            reserved = c.execute(
                "SELECT 1 FROM impact.collection_plan_binding b JOIN impact.object_revision v ON v.tenant_id=b.tenant_id AND v.revision_id=b.plan_revision CROSS JOIN LATERAL jsonb_array_elements(v.payload->'obligations') o JOIN jsonb_to_recordset(%s::jsonb) AS supplied(source_namespace text,source_key text) ON o->>'source_namespace'=supplied.source_namespace AND o->>'source_key'=supplied.source_key WHERE b.tenant_id=%s AND (b.indicator_id<>%s OR b.period_id<>%s) LIMIT 1",
                (Jsonb(data["obligations"]), ctx.tenant_id, indicator["object_id"], period["object_id"]),
            ).fetchone()
            if reserved:
                raise DomainError("VALIDATION_FAILED", reason="SOURCE_KEY_UNAVAILABLE")
        for obligation in data.get("obligations", []):
            key = (obligation["source_namespace"], obligation["source_key"])
            if key in seen or any(
                obligation[k] != obligation[k].strip() for k in ["source_namespace", "source_key"]
            ):
                raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_OR_PADDED_SOURCE_KEY")
            seen.add(key)
            eligibility = obligation.get("eligibility", "REQUIRED")
            if eligibility == "EXCEPTED":
                if not str(obligation.get("exclusion_reason", "")).strip() or not obligation.get(
                    "exclusion_effective_at"
                ):
                    raise DomainError("VALIDATION_FAILED", reason="EXCLUSION_JUSTIFICATION_REQUIRED")
                effective = instant(obligation["exclusion_effective_at"])
                if effective > datetime.now(timezone.utc) + timedelta(minutes=5):
                    raise DomainError("VALIDATION_FAILED", reason="EXCLUSION_EFFECTIVE_DATE_IN_FUTURE")
            if period and instant(obligation["due_at"]) < instant(period["payload"]["starts_at"]):
                raise DomainError("VALIDATION_FAILED", reason="DUE_BEFORE_PERIOD")
            # A source key is globally unique in a tenant. Detect impossible obligations without exposing its owner.
            existing = c.execute(
                "SELECT o.indicator_id,o.event_at FROM impact.source_key_registry s JOIN impact.observation_current o ON o.tenant_id=s.tenant_id AND o.object_id=s.object_id WHERE s.tenant_id=%s AND s.namespace=%s AND s.source_key=%s",
                (ctx.tenant_id, *key),
            ).fetchone()
            if (
                existing
                and indicator
                and period
                and (
                    str(existing["indicator_id"]) != str(indicator["object_id"])
                    or not instant(period["payload"]["starts_at"])
                    <= existing["event_at"]
                    < instant(period["payload"]["ends_at"])
                )
            ):
                raise DomainError("VALIDATION_FAILED", reason="SOURCE_KEY_UNAVAILABLE")
        if complete and not any(
            item.get("eligibility", "REQUIRED") == "REQUIRED" for item in data["obligations"]
        ):
            raise DomainError("VALIDATION_FAILED", reason="AT_LEAST_ONE_REQUIRED_OBLIGATION")
        if complete and not approved and self.plan(c, ctx, indicator["object_id"], period["object_id"]):
            raise DomainError("INVALID_STATE", 409, reason="PLAN_ALREADY_APPROVED")

    def indicator_ready(self, c, ctx, row):
        from .service import revision

        data = row["payload"]
        if any(
            not data.get(k)
            for k in [
                "programme_id",
                "definition_version",
                "local_applicability",
                "collector_id",
                "reviewer_id",
            ]
        ):
            raise DomainError("VALIDATION_FAILED", reason="INDICATOR_INCOMPLETE")
        definition = revision(
            c, ctx, data["definition_version"], "IndicatorDefinition", "indicator-definitions.read"
        )
        head = load(c, ctx, definition["object_id"])
        if head["lifecycle_state"] != "Approved" or str(head["head_revision"]) != data["definition_version"]:
            raise DomainError("INVALID_STATE", 409, reason="APPROVED_DEFINITION_REQUIRED")
        definition_ready(definition["payload"])
        programme = load(c, ctx, data["programme_id"], "Programme", "programmes.read")
        if programme["lifecycle_state"] not in {"Draft", "Ready", "Active"}:
            raise DomainError("INVALID_STATE", 409)
        for field, cap in [
            ("collector_id", "observations.draft.create"),
            ("reviewer_id", "workflow.approve"),
        ]:
            if not self.eligible(c, ctx, data[field], cap):
                raise DomainError("VALIDATION_FAILED", reason="ASSIGNMENT_INELIGIBLE")
        natural = [
            c.execute(
                "SELECT impact.member_natural_identity(%s,%s) AS person", (ctx.tenant_id, data[k])
            ).fetchone()["person"]
            for k in ["collector_id", "reviewer_id"]
        ]
        if not all(natural) or natural[0] == natural[1]:
            raise DomainError("VALIDATION_FAILED", reason="INDEPENDENT_ASSIGNMENTS_REQUIRED")
        plans = c.execute(
            "SELECT period_id FROM impact.collection_plan_binding WHERE tenant_id=%s AND indicator_id=%s ORDER BY period_id LIMIT 501",
            (ctx.tenant_id, row["object_id"]),
        ).fetchall()
        if not plans:
            raise DomainError("VALIDATION_FAILED", reason="APPROVED_PLAN_REQUIRED")
        if len(plans) > 500:
            raise DomainError("LIMIT_EXCEEDED", 422)
        for plan in plans:
            approved_plan = self.plan(c, ctx, row["object_id"], plan["period_id"])
            self.validate_plan(c, ctx, approved_plan["payload"], complete=True, approved=True)
        return self.plan(c, ctx, row["object_id"], plans[0]["period_id"])

    def readiness(self, c, ctx, row):
        checks = []

        def check(code, passed, message):
            checks.append({"code": code, "passed": bool(passed), "message": message})

        data = row["payload"]
        required = [
            "code",
            "title",
            "programme_type",
            "starts_at",
            "ends_at",
            "reporting_calendar_id",
            "geography_id",
        ]
        check(
            "PROGRAMME_DETAILS",
            all(str(data.get(k, "")).strip() for k in required),
            "Programme code, title, type, dates, calendar and geography are required.",
        )
        check(
            "ACTIVE_OWNER",
            self.principal(c, ctx, row["owner_id"]),
            "The programme owner must have an active membership.",
        )
        for field, kind, cap in [
            ("reporting_calendar_id", "ReportingCalendar", "reporting-calendars.read"),
            ("geography_id", "Geography", "geographies.read"),
        ]:
            ref = load(c, ctx, data[field], kind, cap) if data.get(field) else None
            check(
                field.upper(),
                ref and ref["lifecycle_state"] == "Active",
                "Select an active " + field.replace("_id", "").replace("_", " ") + ".",
            )
        indicators = c.execute(
            "SELECT object_id FROM impact.indicator_instance_current WHERE tenant_id=%s AND programme_id=%s ORDER BY object_id LIMIT 501",
            (ctx.tenant_id, row["object_id"]),
        ).fetchall()
        if len(indicators) > 500:
            raise DomainError("LIMIT_EXCEEDED", 422)
        check(
            "INDICATORS_ASSIGNED",
            indicators,
            "At least one active indicator with an approved collection plan is required.",
        )
        for item in indicators:
            indicator = load(c, ctx, item["object_id"], "IndicatorInstance", "indicator-instances.read")
            try:
                self.indicator_ready(c, ctx, indicator)
                if indicator["lifecycle_state"] != "Active":
                    raise DomainError("INVALID_STATE", reason="INDICATOR_NOT_ACTIVE")
                check(
                    "INDICATOR_" + str(item["object_id"]),
                    True,
                    "Indicator configuration and assignments are ready.",
                )
            except DomainError as exc:
                if exc.status in {403, 404}:
                    raise
                check("INDICATOR_" + str(item["object_id"]), False, exc.reason or exc.code)
        return {
            "ready": all(x["passed"] for x in checks),
            "revision_id": str(row["head_revision"]),
            "checks": checks,
        }

    def transition(self, c, ctx, kind, row, action, data):
        if kind == "IndicatorInstance":
            if row["lifecycle_state"] != "Draft":
                raise DomainError("INVALID_STATE", 409)
            self.indicator_ready(c, ctx, row)
            return write(
                c,
                ctx,
                kind,
                row["payload"],
                "Active",
                row,
                track_author=False,
            )
        expected = {"ready": "Draft", "activate": "Ready", "revise": "Ready"}[action]
        if row["lifecycle_state"] != expected:
            raise DomainError("INVALID_STATE", 409)
        if action != "revise" and not self.readiness(c, ctx, row)["ready"]:
            raise DomainError("VALIDATION_FAILED", reason="PROGRAMME_NOT_READY")
        return write(
            c,
            ctx,
            kind,
            row["payload"],
            {"ready": "Ready", "activate": "Active", "revise": "Draft"}[action],
            row,
            track_author=False,
        )

    def read(self, identity, tenant, op, obj=None):
        from .service import READ_KINDS

        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, op, obj, hidden=bool(obj))
            if op == "programme_readiness":
                return self.readiness(c, ctx, load(c, ctx, obj, "Programme"))
            if op == "workflow_candidate":
                workflow = load(c, ctx, obj, "Workflow")
                row = load(c, ctx, workflow["payload"]["candidate_id"])
                route = next((r for r, k in READ_KINDS.items() if k == row["object_type"]), None)
                if (
                    row["object_type"]
                    not in {
                        "Observation",
                        "IndicatorDefinition",
                        "CollectionPlan",
                        "MeasurementChange",
                        "PeriodClose",
                        "RestatementRequest",
                        "Report",
                        "Disclosure",
                        "Framework",
                        "Target",
                    }
                    or not route
                    or not scopes(c, ctx, route + ".read", row["object_id"])
                ):
                    unavailable()
                if str(row["head_revision"]) != workflow["payload"]["candidate_revision"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                result = {"kind": row["object_type"], "record": self.service.result(c, ctx, row)}
                if row["object_type"] == "MeasurementChange":
                    from .changes import TARGETS

                    target_route = TARGETS[row["payload"]["target_kind"]][0]
                    result["current_target"] = envelope(
                        load(
                            c,
                            ctx,
                            row["payload"]["target_id"],
                            row["payload"]["target_kind"],
                            target_route + ".read",
                        )
                    )
                if row["object_type"] in {"Framework", "Target"}:
                    result.update(self.service.planning.candidate_context(c, ctx, row))
                if row["object_type"] in {"PeriodClose", "RestatementRequest"}:
                    result["current_target"] = envelope(
                        load(c, ctx, row["payload"]["period_id"], "Period", "periods.read")
                    )
                return result
            if not scopes(c, ctx, "measurement-members.read"):
                raise DomainError("POLICY_DENIED", 403)
            principals = c.execute(
                "SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND active ORDER BY principal_id LIMIT 1001",
                (tenant,),
            ).fetchall()
            if len(principals) > 1000:
                raise DomainError("LIMIT_EXCEEDED", 422)
            items = []
            for principal in principals:
                member = self.principal(c, ctx, principal["principal_id"])
                if member:
                    collector = self.eligible(
                        c, ctx, str(principal["principal_id"]), "observations.draft.create"
                    )
                    reviewer = self.eligible(c, ctx, str(principal["principal_id"]), "workflow.approve")
                    if collector or reviewer:
                        items.append(
                            {
                                "principal_id": str(member["principal_id"]),
                                "display_name": member["display_name"],
                                "collector": collector,
                                "reviewer": reviewer,
                            }
                        )
            return {"items": items}
