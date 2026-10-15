"""FR-ANA-009 governed alert rules and cooldown-coalesced incidents."""

from calendar import monthrange
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import (
    audit,
    authorize,
    context,
    currently_readable,
    envelope,
    hash_data,
    load,
    visible_sql,
    write,
)


def advance(value, cadence):
    """Advance a UTC schedule without approximating a calendar month as a fixed duration."""
    if cadence == "DAILY":
        return value + timedelta(days=1)
    if cadence == "WEEKLY":
        return value + timedelta(days=7)
    year, month = value.year, value.month + 1
    if month == 13:
        year, month = year + 1, 1
    return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))


def evaluate(rule, result, now=None):
    """Classify missing/stale/threshold independently; absent values never become zero."""
    now = now or datetime.now(timezone.utc)
    if result is None:
        return "MISSINGNESS", "RESULT_ABSENT"
    payload = result["payload"]
    if payload.get("value_state") != "PRESENT" or payload.get("value") is None:
        return "MISSINGNESS", "VALUE_NOT_PRESENT"
    freshness = payload.get("freshness") or {}
    calculated_at = freshness.get("calculated_at")
    stale = bool(freshness.get("stale"))
    if calculated_at:
        age = now - datetime.fromisoformat(calculated_at.replace("Z", "+00:00"))
        stale = stale or age.total_seconds() > rule["max_freshness_seconds"]
    if stale or not calculated_at:
        return "STALE_INPUT", "RESULT_STALE"
    coverage = payload.get("coverage") or {}
    percent = coverage.get("approval_percent")
    if percent is None or Decimal(str(percent)) < Decimal(str(rule["minimum_coverage"])):
        return "MISSINGNESS", "COVERAGE_BELOW_MINIMUM"
    if payload.get("mode") != "OFFICIAL":
        return "NO_TRIGGER", "OFFICIAL_RESULT_REQUIRED"
    try:
        value = Decimal(str(payload["value"]))
        threshold = Decimal(str(rule["threshold"]))
    except (InvalidOperation, TypeError, ValueError):
        return "MISSINGNESS", "VALUE_NOT_NUMERIC"
    breached = value < threshold if rule["operator"] == "LT" else value > threshold
    return ("THRESHOLD", "CONDITION_MET") if breached else ("NO_TRIGGER", "CONDITION_NOT_MET")


class DashboardAlerts:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body, correlation):
        op = "create_dashboard_alert_rule"
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "create_dashboard_alert_rule")
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            data = body["data"]
            load(c, ctx, data["measure_id"], "IndicatorInstance", "indicator-instances.read")
            for recipient in data["recipient_ids"]:
                if not c.execute(
                    "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s AND active",
                    (tenant, recipient),
                ).fetchone():
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            # A new rule is due immediately so it can classify an already missed reporting
            # period. A completed evaluation advances this server-owned instant by its cadence.
            data = {**data, "next_evaluation_at": now.isoformat()}
            receipt = write(c, ctx, "DashboardAlertRule", data)
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
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return receipt

    def run(self, identity, tenant, rule_id, body, correlation):
        op = "evaluate_dashboard_alert_rule"
        fingerprint = hash_data({"rule_id": str(rule_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "evaluate_dashboard_alert_rule", rule_id)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            rule = load(c, ctx, rule_id, "DashboardAlertRule", lock=True)
            due = datetime.fromisoformat(rule["payload"]["next_evaluation_at"].replace("Z", "+00:00"))
            period = load(c, ctx, body["data"]["period_id"], "Period", "periods.read")
            repeated_period = rule["payload"].get("last_period_id") == str(period["object_id"])
            if now < due and not repeated_period:
                raise DomainError("INVALID_STATE", 409, reason="ALERT_NOT_DUE")
            period_end = datetime.fromisoformat(period["payload"]["ends_at"].replace("Z", "+00:00"))
            if period_end > due and not repeated_period:
                raise DomainError("INVALID_STATE", 409, reason="PERIOD_NOT_DUE")
            for recipient in rule["payload"]["recipient_ids"]:
                if not c.execute(
                    "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s AND active",
                    (tenant, recipient),
                ).fetchone():
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
            measure = load(
                c,
                ctx,
                rule["payload"]["measure_id"],
                "IndicatorInstance",
                "indicator-instances.read",
            )
            result = None
            if body["data"].get("result_id"):
                result = load(
                    c,
                    ctx,
                    body["data"]["result_id"],
                    "CalculatedResult",
                    "calculated-results.read",
                    lock=True,
                )
                bound = c.execute(
                    "SELECT 1 FROM impact.result_binding WHERE tenant_id=%s AND result_id=%s "
                    "AND indicator_id=%s AND period_id=%s",
                    (tenant, result["object_id"], measure["object_id"], period["object_id"]),
                ).fetchone()
                if not bound or result["payload"].get("indicator_version") != measure["payload"].get(
                    "definition_version"
                ):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
            kind, reason = evaluate(rule["payload"], result, now)
            next_due = due
            while not repeated_period and next_due <= now:
                next_due = advance(next_due, rule["payload"]["evaluation_cadence"])
            updated_rule = {
                **rule["payload"],
                "last_evaluated_at": now.isoformat(),
                "last_period_id": str(period["object_id"]),
                "next_evaluation_at": next_due.isoformat(),
            }
            rule_receipt = write(
                c,
                ctx,
                "DashboardAlertRule",
                updated_rule,
                state=rule["lifecycle_state"],
                previous=rule,
            )
            if kind == "NO_TRIGGER":
                outcome = {
                    "rule_id": str(rule_id),
                    "outcome": kind,
                    "reason_code": reason,
                    "incident_id": None,
                    "result_revision": str(result["head_revision"]) if result else None,
                    "evaluation_period_id": str(period["object_id"]),
                    "occurrence_count": 0,
                    "coalesced": False,
                }
                audit(c, ctx, op, rule_receipt, correlation)
                self._remember(c, ctx, op, body["operation_id"], fingerprint, outcome)
                return outcome
            cutoff = now - timedelta(seconds=rule["payload"]["cooldown_seconds"])
            existing = c.execute(
                "SELECT r.*,v.payload,v.revision_number FROM impact.object_registry r JOIN impact.object_revision v "
                "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
                "WHERE r.tenant_id=%s AND r.object_type='DashboardAlertIncident' "
                "AND v.payload->>'rule_id'=%s AND v.payload->>'alert_type'=%s AND r.updated_at>%s "
                "ORDER BY r.updated_at DESC LIMIT 1 FOR UPDATE OF r",
                (tenant, str(rule_id), kind, cutoff),
            ).fetchone()
            payload = {
                "rule_id": str(rule_id),
                "alert_type": kind,
                "reason_code": reason,
                "result_id": str(result["object_id"]) if result else None,
                "result_revision": str(result["head_revision"]) if result else None,
                "evaluation_period_id": str(period["object_id"]),
                "recipient_ids": rule["payload"]["recipient_ids"],
                "occurrence_count": (existing["payload"]["occurrence_count"] + 1) if existing else 1,
                "last_evaluated_at": now.isoformat(),
            }
            receipt = write(
                c,
                ctx,
                "DashboardAlertIncident",
                payload,
                state="Active",
                previous=existing,
            )
            audit(c, ctx, op, receipt, correlation)
            outcome = {
                "rule_id": str(rule_id),
                "outcome": kind,
                "reason_code": reason,
                "incident_id": receipt["object_id"],
                "result_revision": payload["result_revision"],
                "evaluation_period_id": payload["evaluation_period_id"],
                "occurrence_count": payload["occurrence_count"],
                "coalesced": bool(existing),
            }
            self._remember(c, ctx, op, body["operation_id"], fingerprint, outcome)
            return outcome

    def read(self, identity, tenant, rule_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_dashboard_alert_rule", rule_id, hidden=True)
            rule = load(c, ctx, rule_id, "DashboardAlertRule", "dashboards.read")
            load(
                c,
                ctx,
                rule["payload"]["measure_id"],
                "IndicatorInstance",
                "indicator-instances.read",
            )
            return envelope(rule)

    def listing(self, identity, tenant, limit=50, cursor=None):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_dashboard_alert_rules")
            bound = self.service.cursor_binding(ctx, "dashboard-alert-rules")
            key = self.service.cursor_key(bound, cursor)
            predicate, args = visible_sql(ctx, "dashboards.read")
            query = (
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
                "AND r.object_type='DashboardAlertRule' AND v.restriction_state='AVAILABLE' AND " + predicate
            )
            params = [tenant, *args]
            if key:
                query += " AND (r.created_at,r.object_id)>(%s::timestamptz,%s::uuid)"
                params += key
            rows = c.execute(
                query + " ORDER BY r.created_at,r.object_id LIMIT %s", [*params, limit + 1]
            ).fetchall()
            page = rows[:limit]
            visible = [
                row
                for row in page
                if currently_readable(
                    c,
                    ctx,
                    row["payload"]["measure_id"],
                    "IndicatorInstance",
                    "indicator-instances.read",
                )
            ]
            return {
                "items": [envelope(row) for row in visible],
                "next_cursor": self.service.next_cursor(
                    bound, [page[-1]["created_at"].isoformat(), str(page[-1]["object_id"])]
                )
                if len(rows) > limit
                else None,
                "scope_label": "Alert rules permitted by your current access",
            }

    def incidents(self, identity, tenant, rule_id, limit=50, cursor=None):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            load(c, ctx, rule_id, "DashboardAlertRule", "dashboards.read")
            bound = self.service.cursor_binding(ctx, f"dashboard-alert-rules/{rule_id}/incidents")
            key = self.service.cursor_key(bound, cursor)
            query = (
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
                "AND r.object_type='DashboardAlertIncident' AND v.restriction_state='AVAILABLE' "
                "AND v.payload->>'rule_id'=%s"
            )
            params = [tenant, str(rule_id)]
            if key:
                query += " AND (r.created_at,r.object_id)>(%s::timestamptz,%s::uuid)"
                params += key
            rows = c.execute(
                query + " ORDER BY r.created_at,r.object_id LIMIT %s", [*params, limit + 1]
            ).fetchall()
            page = rows[:limit]
            items = []
            for row in page:
                item = envelope(row)
                result_id = item["data"].get("result_id")
                if result_id and not currently_readable(
                    c, ctx, result_id, "CalculatedResult", "calculated-results.read"
                ):
                    item["data"] = {**item["data"], "result_id": None, "result_revision": None}
                items.append(item)
            return {
                "items": items,
                "next_cursor": self.service.next_cursor(
                    bound, [page[-1]["created_at"].isoformat(), str(page[-1]["object_id"])]
                )
                if len(rows) > limit
                else None,
                "scope_label": "Incidents for this alert rule",
            }

    @staticmethod
    def _remember(c, ctx, op, operation_id, fingerprint, outcome):
        c.execute(
            "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
            (
                ctx.tenant_id,
                ctx.principal_id,
                op,
                operation_id,
                fingerprint,
                Jsonb(outcome),
                datetime.now(timezone.utc) + timedelta(days=7),
            ),
        )
