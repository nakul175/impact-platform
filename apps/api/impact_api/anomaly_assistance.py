"""FR-DQ-007 reviewable anomaly suggestions that never modify source data."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from psycopg.types.json import Jsonb

from .domain import DomainError
from .imports import ANOMALY, robust_outlier
from .store import audit, authorize, context, hash_data, load, write


class AnomalyAssistance:
    def __init__(self, service):
        self.service = service

    def run(self, identity, tenant, body, correlation):
        op = "create_anomaly_run"
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
            window = body["data"]["comparison_window"]
            starts = datetime.fromisoformat(window["starts_at"].replace("Z", "+00:00"))
            ends = datetime.fromisoformat(window["ends_at"].replace("Z", "+00:00"))
            if starts >= ends:
                raise DomainError("VALIDATION_FAILED", reason="ANOMALY_WINDOW_INVALID")
            if not c.execute(
                "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s AND active",
                (tenant, body["data"]["owner_id"]),
            ).fetchone():
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            eligible = []
            indicator_ids = set()
            for item in body["data"]["eligible_observations"]:
                current = load(c, ctx, item["object_id"], "Observation", "observations.read")
                row = c.execute(
                    "SELECT payload,payload_sha256 FROM impact.object_revision "
                    "WHERE tenant_id=%s AND object_id=%s AND revision_id=%s "
                    "AND object_type='Observation' AND restriction_state='AVAILABLE'",
                    (tenant, item["object_id"], item["revision_id"]),
                ).fetchone()
                if not row or str(current["object_id"]) != item["object_id"]:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                payload = row["payload"]
                if payload.get("value_state") != "PRESENT" or payload.get("value") is None:
                    continue
                event_at = datetime.fromisoformat(payload["event_at"].replace("Z", "+00:00"))
                if not starts <= event_at < ends:
                    continue
                indicator_ids.add(payload["indicator_id"])
                eligible.append(
                    {
                        **item,
                        "event_at": payload.get("event_at"),
                        "value": payload["value"],
                        "source_hash": bytes(row["payload_sha256"]).hex(),
                    }
                )
            if len(indicator_ids) > 1:
                raise DomainError("VALIDATION_FAILED", reason="ANOMALY_MEASURES_NOT_COMPARABLE")
            eligible.sort(key=lambda item: (item["event_at"] or "", item["revision_id"]))
            findings = []
            if len(eligible) > ANOMALY["minimum_history"]:
                candidate, history = eligible[-1], eligible[:-1]
                finding = robust_outlier(
                    Decimal(candidate["value"]), [Decimal(item["value"]) for item in history]
                )
                if finding:
                    findings.append(
                        {
                            "observation_id": candidate["object_id"],
                            "observation_revision": candidate["revision_id"],
                            "state": "SUGGESTED",
                            "severity": "REVIEW",
                            "owner_id": body["data"]["owner_id"],
                            "explanation": "Robust median absolute deviation exceeded the reviewed threshold; this is a statistical review suggestion, not a fraud label.",
                            "method_output": finding,
                            "review": None,
                        }
                    )
            run_payload = {
                "method_version": "ROBUST_MAD_1",
                "method_parameters": ANOMALY,
                "eligible_observations": eligible,
                "comparison_window": body["data"]["comparison_window"],
                "explanation": "Compares the latest eligible present value with earlier eligible values using robust median absolute deviation.",
                "source_mutation": False,
                "person_fraud_label": False,
            }
            run_receipt = write(c, ctx, "AnomalyRun", run_payload, state="Completed")
            saved = []
            for finding in findings:
                receipt = write(
                    c,
                    ctx,
                    "AnomalyFinding",
                    {**finding, "run_id": run_receipt["object_id"]},
                    state="Suggested",
                )
                saved.append({**finding, "finding_id": receipt["object_id"]})
            outcome = {
                "run_id": run_receipt["object_id"],
                "run_revision": run_receipt["revision_id"],
                "method_version": "ROBUST_MAD_1",
                "eligible_revision_count": len(eligible),
                "findings": saved,
                "source_mutation": False,
                "person_fraud_label": False,
            }
            audit(c, ctx, op, run_receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return outcome

    def review(self, identity, tenant, finding_id, body, correlation):
        op = "review_anomaly_finding"
        fingerprint = hash_data({"finding_id": str(finding_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "patch_dashboards", finding_id)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            finding = load(c, ctx, finding_id, "AnomalyFinding", lock=True)
            decision = body["data"]["decision"]
            reason = body["data"].get("reason")
            if decision == "DISMISSED" and not reason:
                raise DomainError("VALIDATION_FAILED", reason="DISMISSAL_REASON_REQUIRED")
            payload = {
                **finding["payload"],
                "state": decision,
                "review": {
                    "decision": decision,
                    "reason": reason,
                    "reviewer_id": str(ctx.principal_id),
                    "reviewed_at": datetime.now(timezone.utc).isoformat(),
                    "confirmed_quality_defect": decision == "CONFIRMED",
                    "minimised_feedback": True,
                },
            }
            receipt = write(c, ctx, "AnomalyFinding", payload, state=decision.title(), previous=finding)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            outcome = {
                **receipt,
                "decision": decision,
                "confirmed_quality_defect": decision == "CONFIRMED",
                "source_mutation": False,
            }
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return outcome
