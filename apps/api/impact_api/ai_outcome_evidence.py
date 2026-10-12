"""Consent-current, fixed-slice cross-organisation outcome evidence for platform operators."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import psycopg
from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load

OUTCOME_KIND = "AICurrentOutcomeObservation"
PURPOSE = "WHAT_WORKS_AGGREGATION"
RULE_VERSION = "outcome-evidence-2026-10-13.1"
POLICY_VERSION = "minimum-five-fixed-cells-2026-10-13.1"
METRICS = {"time", "cost", "quality", "reach", "usage"}


def _invalid(reason="OUTCOME_EVIDENCE_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    try:
        canonical = str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        _invalid()
    if canonical != value:
        _invalid()
    return canonical


def _fresh(identity):
    if (
        not identity.assurance_verified
        or (datetime.now(timezone.utc) - identity.auth_time).total_seconds() > 300
    ):
        raise DomainError("ASSURANCE_REQUIRED", 403, reason="FRESH_MFA_REQUIRED")


def _owner(c, ctx):
    row = c.execute(
        "SELECT m.object_id AS membership_id,h.head_revision AS membership_revision,p.principal_id "
        "FROM impact.tenant_custody t JOIN impact.membership_current m ON m.tenant_id=t.tenant_id AND m.object_id=t.owner_membership_id "
        "JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id "
        "JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id "
        "WHERE t.tenant_id=%s AND h.lifecycle_state='Active' AND p.active AND (m.expires_at IS NULL OR m.expires_at>now())",
        (ctx.tenant_id,),
    ).fetchone()
    if (
        not row
        or str(row["principal_id"]) != str(ctx.principal_id)
        or str(row["membership_id"]) != str(ctx.membership_id)
    ):
        raise DomainError("RESOURCE_UNAVAILABLE", 404)
    return row


def _quarter(date_text):
    year, month = int(date_text[:4]), int(date_text[5:7])
    return f"{year}-Q{(month - 1) // 3 + 1}"


class AIOutcomeEvidence:
    def __init__(self, service, lifecycle):
        self.service, self.lifecycle = service, lifecycle

    def consent(self, identity, tenant, body, correlation):
        required = {
            "operation_id",
            "outcome_observation_id",
            "outcome_observation_revision",
            "decision",
            "allowed_metrics",
            "notice_version",
            "reason",
        }
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        for field in ("operation_id", "outcome_observation_id", "outcome_observation_revision"):
            _uuid(body[field])
        if body["decision"] not in {"GRANTED", "WITHDRAWN"}:
            _invalid()
        if (
            not isinstance(body["allowed_metrics"], list)
            or not body["allowed_metrics"]
            or len(set(body["allowed_metrics"])) != len(body["allowed_metrics"])
            or not set(body["allowed_metrics"]) <= METRICS
        ):
            _invalid()
        if (
            not isinstance(body["notice_version"], str)
            or not body["notice_version"].strip()
            or len(body["notice_version"]) > 100
        ):
            _invalid()
        if not isinstance(body["reason"], str) or not body["reason"].strip() or len(body["reason"]) > 1000:
            _invalid()
        _fresh(identity)
        operation = "record_ai_outcome_sharing_consent"
        fingerprint = hash_data([operation, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            owner = _owner(c, ctx)
            durable = c.execute(
                "SELECT * FROM impact.ai_outcome_sharing_consent WHERE tenant_id=%s AND actor_principal_id=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if durable:
                if bytes(durable["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._consent_result(durable, correlation=str(durable["correlation_id"]))
            current = c.execute(
                "SELECT * FROM impact.ai_outcome_sharing_consent WHERE tenant_id=%s AND outcome_observation_id=%s ORDER BY recorded_at DESC,consent_event_id DESC LIMIT 1",
                (tenant, body["outcome_observation_id"]),
            ).fetchone()
            if body["decision"] == "WITHDRAWN" and not current:
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="CONSENT_NOT_GRANTED")
            if body["decision"] == "WITHDRAWN" and (
                str(current["outcome_observation_revision"]) != body["outcome_observation_revision"]
                or current["decision"] != "GRANTED"
            ):
                raise DomainError("CONFLICT_VERSION", 409, reason="CONSENT_OR_SOURCE_CHANGED")
            metrics = {}
            if body["decision"] == "GRANTED":
                observation = load(c, ctx, body["outcome_observation_id"], OUTCOME_KIND, "ai.enablement.read")
                if str(observation["head_revision"]) != body["outcome_observation_revision"]:
                    raise DomainError("CONFLICT_VERSION", 409, reason="OUTCOME_OBSERVATION_CHANGED")
                for name in body["allowed_metrics"]:
                    measure = observation["payload"]["metrics"].get(name)
                    if measure is not None:
                        metrics[name] = {
                            "value": measure["value"],
                            "unit": measure["unit"],
                            "period_bucket": _quarter(measure["observed_to"]),
                        }
                if not metrics:
                    _invalid("NO_ALLOWED_RECORDED_METRICS")
            event_id = str(uuid4())
            c.execute(
                "INSERT INTO impact.ai_outcome_sharing_consent(tenant_id,consent_event_id,outcome_observation_id,outcome_observation_revision,decision,purpose,notice_version,allowed_metrics,metric_manifest,actor_principal_id,actor_membership_id,actor_membership_revision,operation_id,payload_hash,correlation_id,reason,recorded_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    event_id,
                    body["outcome_observation_id"],
                    body["outcome_observation_revision"],
                    body["decision"],
                    PURPOSE,
                    body["notice_version"],
                    body["allowed_metrics"],
                    Jsonb(metrics),
                    ctx.principal_id,
                    ctx.membership_id,
                    owner["membership_revision"],
                    body["operation_id"],
                    fingerprint,
                    correlation,
                    body["reason"].strip(),
                    now,
                ),
            )
            row = c.execute(
                "SELECT * FROM impact.ai_outcome_sharing_consent WHERE tenant_id=%s AND consent_event_id=%s",
                (tenant, event_id),
            ).fetchone()
            result = self._consent_result(row, correlation)
            audit(c, ctx, operation, result, correlation)
            return result

    @staticmethod
    def _consent_result(row, correlation):
        return {
            "operation_id": str(row["operation_id"]),
            "correlation_id": correlation,
            "consent_event_id": str(row["consent_event_id"]),
            "decision": row["decision"],
            "purpose": row["purpose"],
            "outcome_observation_id": str(row["outcome_observation_id"]),
            "outcome_observation_revision": str(row["outcome_observation_revision"]),
            "notice_version": row["notice_version"],
            "allowed_metrics": row["allowed_metrics"],
            "recorded_at": row["recorded_at"].isoformat(),
        }

    def _operator(self, c, identity, fresh=False):
        if not self.lifecycle.operator(c, identity):
            raise DomainError("POLICY_DENIED", 403, reason="PLATFORM_OPERATOR_REQUIRED")
        if fresh:
            _fresh(identity)

    def prepare(self, identity, body):
        if not isinstance(body, dict) or set(body) != {"operation_id"}:
            _invalid()
        _uuid(body["operation_id"])
        with self.service.db.transaction(platform=True) as c:
            self._operator(c, identity, fresh=True)
            return c.execute(
                "SELECT impact.prepare_ai_outcome_evidence(%s,%s,%s,%s) AS response",
                (identity.identity_id, body["operation_id"], RULE_VERSION, POLICY_VERSION),
            ).fetchone()["response"]

    def action(self, identity, publication_id, action, body):
        _uuid(publication_id)
        if (
            action not in {"approve", "publish"}
            or not isinstance(body, dict)
            or set(body) != {"operation_id", "expected_revision"}
        ):
            _invalid()
        _uuid(body["operation_id"])
        _uuid(body["expected_revision"])
        with self.service.db.transaction(platform=True) as c:
            self._operator(c, identity, fresh=True)
            try:
                return c.execute(
                    "SELECT impact.act_ai_outcome_evidence(%s,%s,%s,%s,%s) AS response",
                    (
                        identity.identity_id,
                        publication_id,
                        action,
                        body["operation_id"],
                        body["expected_revision"],
                    ),
                ).fetchone()["response"]
            except psycopg.Error as error:
                if error.sqlstate == "P0002":
                    raise DomainError("RESOURCE_UNAVAILABLE", 404) from error
                if error.sqlstate == "40001":
                    raise DomainError("CONFLICT_VERSION", 409, reason="CONSENT_OR_SOURCE_CHANGED") from error
                if error.sqlstate == "42501":
                    raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENT_APPROVAL_REQUIRED") from error
                if error.sqlstate == "22023":
                    _invalid()
                raise

    def listing(self, identity):
        with self.service.db.transaction(platform=True) as c:
            self._operator(c, identity)
            return {
                "items": [
                    self._publication(r)
                    for r in c.execute(
                        "SELECT * FROM impact.ai_outcome_evidence_publication ORDER BY prepared_at DESC LIMIT 100"
                    ).fetchall()
                ]
            }

    @staticmethod
    def _publication(row):
        return {
            "publication_id": str(row["publication_id"]),
            "revision_id": str(row["revision_id"]),
            "state": row["state"],
            "rule_version": row["rule_version"],
            "policy_version": row["policy_version"],
            "manifest_hash": bytes(row["manifest_hash"]).hex(),
            "artifact": row["artifact"],
            "prepared_at": row["prepared_at"].isoformat(),
            "approved_at": row["approved_at"].isoformat() if row["approved_at"] else None,
            "published_at": row["published_at"].isoformat() if row["published_at"] else None,
        }
