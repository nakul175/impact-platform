"""FR-DQ-007 reviewable anomaly suggestions that never modify source data."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from psycopg.types.json import Jsonb

from .domain import DomainError
from .imports import ANOMALY, robust_outlier
from .store import (
    audit,
    authorize,
    context,
    currently_readable,
    envelope,
    field_allowed,
    hash_data,
    load,
    visible_sql,
    write,
)


class AnomalyAssistance:
    def __init__(self, service):
        self.service = service

    def run(self, identity, tenant, body, correlation):
        op = "create_anomaly_run"
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op)
            window = body["data"]["comparison_window"]
            starts = datetime.fromisoformat(window["starts_at"].replace("Z", "+00:00"))
            ends = datetime.fromisoformat(window["ends_at"].replace("Z", "+00:00"))
            if starts >= ends:
                raise DomainError("VALIDATION_FAILED", reason="ANOMALY_WINDOW_INVALID")
            if not c.execute(
                "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s "
                "AND principal_kind='HUMAN' AND active",
                (tenant, body["data"]["owner_id"]),
            ).fetchone():
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            eligible = []
            indicator_ids = set()
            selected = {
                (item["object_id"], item["revision_id"]) for item in body["data"]["eligible_observations"]
            }
            if len(selected) != len(body["data"]["eligible_observations"]):
                raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_ELIGIBLE_REVISION")
            for item in body["data"]["eligible_observations"]:
                current = load(c, ctx, item["object_id"], "Observation", "observations.read")
                if not field_allowed(c, ctx, "observations.read", item["object_id"], "INTERNAL"):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                row = c.execute(
                    "SELECT payload,payload_sha256 FROM impact.object_revision "
                    "WHERE tenant_id=%s AND object_id=%s AND revision_id=%s "
                    "AND object_type='Observation' AND restriction_state='AVAILABLE'",
                    (tenant, item["object_id"], item["revision_id"]),
                ).fetchone()
                if not row or str(current["object_id"]) != item["object_id"]:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                payload = row["payload"]
                if any(
                    payload.get(key)
                    for key in (
                        "person_id",
                        "participant_id",
                        "respondent_id",
                        "subject_id",
                        "individual_id",
                        "household_id",
                    )
                ) or payload.get("granularity") in {"PERSON", "INDIVIDUAL", "HOUSEHOLD"}:
                    raise DomainError("VALIDATION_FAILED", reason="PERSON_LEVEL_ANOMALY_REFUSED")
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
                        "_value": payload["value"],
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
                    Decimal(candidate["_value"]), [Decimal(item["_value"]) for item in history]
                )
                if finding:
                    findings.append(
                        {
                            "observation_id": candidate["object_id"],
                            "observation_revision": candidate["revision_id"],
                            "source_hash": candidate["source_hash"],
                            "method_version": "ROBUST_MAD_1",
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
                "eligible_observations": [
                    {key: value for key, value in item.items() if key != "_value"} for item in eligible
                ],
                "comparison_window": body["data"]["comparison_window"],
                "explanation": "Compares the latest eligible present value with earlier eligible values using robust median absolute deviation.",
                "source_mutation": False,
                "person_fraud_label": False,
            }
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
            run_receipt = write(c, ctx, "AnomalyRun", run_payload, state="Completed")
            saved = []
            for finding in findings:
                receipt = write(
                    c,
                    ctx,
                    "AnomalyFinding",
                    {
                        **finding,
                        "run_id": run_receipt["object_id"],
                        "run_revision": run_receipt["revision_id"],
                    },
                    state="Suggested",
                )
                c.execute(
                    "UPDATE impact.object_registry SET owner_id=%s WHERE tenant_id=%s AND object_id=%s",
                    (body["data"]["owner_id"], tenant, receipt["object_id"]),
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
            authorize(c, ctx, op, finding_id, hidden=True)
            finding = load(c, ctx, finding_id, "AnomalyFinding", "dashboards.draft.edit", lock=True)
            self._require_source(c, ctx, finding["payload"])
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
            decision = body["data"]["decision"]
            reason = body["data"].get("reason_code")
            if finding["payload"]["state"] not in {"SUGGESTED", "DEFERRED"}:
                raise DomainError("CONFLICT_STATE", 409)
            if decision == "DISMISSED" and not reason:
                raise DomainError("VALIDATION_FAILED", reason="DISMISSAL_REASON_REQUIRED")
            now = datetime.now(timezone.utc)
            payload = {
                **finding["payload"],
                "state": decision,
                "review": {
                    "decision": decision,
                    "reason_code": reason,
                    "reviewer_id": str(ctx.principal_id),
                    "reviewed_at": now.isoformat(),
                    "confirmed_quality_defect": decision == "CONFIRMED",
                    "minimised_feedback": True,
                    "feedback_policy": "ANOMALY_FEEDBACK_MINIMISATION_V1",
                    "feedback_fields": [
                        "decision",
                        "reason_code",
                        "method_version",
                        "observation_revision",
                    ],
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

    def read_run(self, identity, tenant, run_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_anomaly_run", run_id, hidden=True)
            row = load(c, ctx, run_id, "AnomalyRun", "dashboards.read")
            if not all(
                self._source_readable(c, ctx, source) for source in row["payload"]["eligible_observations"]
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            return envelope(row)

    def list_runs(self, identity, tenant, limit=50):
        return self._listing(identity, tenant, "AnomalyRun", "list_anomaly_runs", limit)

    def read_finding(self, identity, tenant, finding_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_anomaly_finding", finding_id, hidden=True)
            row = load(c, ctx, finding_id, "AnomalyFinding", "dashboards.read")
            self._require_source(c, ctx, row["payload"])
            return envelope(row)

    def list_findings(self, identity, tenant, limit=50):
        return self._listing(identity, tenant, "AnomalyFinding", "list_anomaly_findings", limit)

    def _listing(self, identity, tenant, object_type, operation, limit):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, operation)
            predicate, args = visible_sql(ctx, "dashboards.read")
            rows = c.execute(
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type=%s "
                "AND v.restriction_state='AVAILABLE' AND "
                + predicate
                + " ORDER BY r.created_at DESC,r.object_id DESC LIMIT %s",
                [tenant, object_type, *args, limit],
            ).fetchall()
            readable = []
            for row in rows:
                sources = (
                    row["payload"]["eligible_observations"]
                    if object_type == "AnomalyRun"
                    else [row["payload"]]
                )
                if all(self._source_readable(c, ctx, source) for source in sources):
                    readable.append(envelope(row))
            return {
                "items": readable,
                "next_cursor": None,
                "scope_label": "Reviewable anomaly assistance",
            }

    @staticmethod
    def _source_readable(c, ctx, source):
        object_id = source.get("observation_id") or source.get("object_id")
        return currently_readable(c, ctx, object_id, "Observation", "observations.read") and field_allowed(
            c, ctx, "observations.read", object_id, "INTERNAL"
        )

    def _require_source(self, c, ctx, source):
        if not self._source_readable(c, ctx, source):
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        object_id = source.get("observation_id") or source.get("object_id")
        revision_id = source.get("observation_revision") or source.get("revision_id")
        row = c.execute(
            "SELECT payload_sha256 FROM impact.object_revision WHERE tenant_id=%s "
            "AND object_id=%s AND revision_id=%s AND object_type='Observation' "
            "AND restriction_state='AVAILABLE'",
            (ctx.tenant_id, object_id, revision_id),
        ).fetchone()
        if not row or bytes(row["payload_sha256"]).hex() != source["source_hash"]:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
