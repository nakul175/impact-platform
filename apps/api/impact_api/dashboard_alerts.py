"""FR-ANA-009 governed alert rules and cooldown-coalesced incidents."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


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
            authorize(c, ctx, "create_dashboards")
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
            authorize(c, ctx, "patch_dashboards", rule_id)
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
            rule = load(c, ctx, rule_id, "DashboardAlertRule", lock=True)
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
            kind, reason = evaluate(rule["payload"], result)
            if kind == "NO_TRIGGER":
                outcome = {
                    "rule_id": str(rule_id),
                    "outcome": kind,
                    "reason_code": reason,
                    "incident_id": None,
                    "result_revision": str(result["head_revision"]) if result else None,
                    "coalesced": False,
                }
                self._remember(c, ctx, op, body["operation_id"], fingerprint, outcome)
                return outcome
            cutoff = datetime.now(timezone.utc) - timedelta(seconds=rule["payload"]["cooldown_seconds"])
            existing = c.execute(
                "SELECT r.*,v.payload FROM impact.object_registry r JOIN impact.object_revision v "
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
                "recipient_ids": rule["payload"]["recipient_ids"],
                "occurrence_count": (existing["payload"]["occurrence_count"] + 1) if existing else 1,
                "last_evaluated_at": datetime.now(timezone.utc).isoformat(),
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
                "coalesced": bool(existing),
            }
            self._remember(c, ctx, op, body["operation_id"], fingerprint, outcome)
            return outcome

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
