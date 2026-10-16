"""FR-EVA-007 accountable recommendation responses and action follow-through."""

from datetime import date, datetime, timedelta, timezone

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, envelope, hash_data, load, write


class ManagementResponses:
    def __init__(self, service):
        self.service = service

    def _run(self, identity, tenant, op, key, body, correlation, fn):
        fingerprint = hash_data({"key": str(key), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op, key)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            receipt = fn(c, ctx)
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

    def create_recommendation(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            source = load(c, ctx, body["data"]["source_object_id"], "Evidence", "evidence.read")
            if str(source["head_revision"]) != body["data"]["source_revision"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="RECOMMENDATION_SOURCE_CHANGED")
            return write(c, ctx, "EvaluationRecommendation", body["data"], state="Issued")

        return self._run(
            identity,
            tenant,
            "create_evaluation_recommendation",
            tenant,
            body,
            correlation,
            apply,
        )

    def read(self, identity, tenant, object_id, kind, operation):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, operation, object_id, hidden=True)
            return envelope(load(c, ctx, object_id, kind))

    def history(self, identity, tenant, object_id, kind, operation):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, operation, object_id, hidden=True)
            load(c, ctx, object_id, kind)
            rows = c.execute(
                "SELECT revision_id,predecessor_revision,revision_number,payload,created_at FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s ORDER BY revision_number",
                (tenant, object_id),
            ).fetchall()
            return {
                "object_id": str(object_id),
                "items": [
                    {
                        **row,
                        "revision_id": str(row["revision_id"]),
                        "predecessor_revision": (
                            str(row["predecessor_revision"]) if row["predecessor_revision"] else None
                        ),
                        "created_at": row["created_at"].isoformat(),
                    }
                    for row in rows
                ],
            }

    def respond(self, identity, tenant, recommendation_id, body, correlation):
        def apply(c, ctx):
            recommendation = load(c, ctx, recommendation_id, "EvaluationRecommendation", lock=True)
            data = body["data"]
            response = write(
                c,
                ctx,
                "ManagementResponse",
                {
                    "recommendation_id": str(recommendation_id),
                    "recommendation_revision": str(recommendation["head_revision"]),
                    "response": data["response"],
                    "reason": data["reason"],
                    "visible": True,
                },
                state="Recorded",
            )
            if data["response"] in {"ACCEPT", "PARTIALLY_ACCEPT"}:
                if (
                    not data["accepted_scope"]
                    or not data["owner_id"]
                    or not data["due_date"]
                    or not data["required_completion_evidence"]
                ):
                    raise DomainError("VALIDATION_FAILED", reason="ACCEPTED_ACTION_FIELDS_REQUIRED")
                response["action"] = write(
                    c,
                    ctx,
                    "ManagementAction",
                    {
                        "management_response_id": response["object_id"],
                        "accepted_scope": data["accepted_scope"],
                        "owner_id": data["owner_id"],
                        "due_date": data["due_date"],
                        "required_completion_evidence": data["required_completion_evidence"],
                        "completion_evidence": [],
                        "action_completion": "PENDING",
                        "outcome_improvement": "PENDING_FOLLOW_UP_MEASUREMENT",
                    },
                    state="Open",
                )
            return response

        return self._run(
            identity,
            tenant,
            "respond_to_evaluation_recommendation",
            recommendation_id,
            body,
            correlation,
            apply,
        )

    def complete(self, identity, tenant, action_id, body, correlation):
        def apply(c, ctx):
            action = load(c, ctx, action_id, "ManagementAction", lock=True)
            evidence = []
            for pin in body["data"]["evidence"]:
                row = load(c, ctx, pin["object_id"], "Evidence", "evidence.read")
                if str(row["head_revision"]) != pin["revision_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                evidence.append(pin)
            payload = {
                **action["payload"],
                "completion_evidence": evidence,
                "action_completion": "COMPLETE",
                "outcome_improvement": "PENDING_FOLLOW_UP_MEASUREMENT",
            }
            return write(c, ctx, "ManagementAction", payload, state="Completed", previous=action)

        return self._run(identity, tenant, "complete_management_action", action_id, body, correlation, apply)

    def evaluate_overdue(self, identity, tenant, action_id, body, correlation):
        def apply(c, ctx):
            action = load(c, ctx, action_id, "ManagementAction", lock=True)
            if action["lifecycle_state"] == "Completed":
                raise DomainError("INVALID_STATE", 409, reason="ACTION_ALREADY_COMPLETED")
            if date.fromisoformat(action["payload"]["due_date"]) >= date.today():
                raise DomainError("INVALID_STATE", 409, reason="ACTION_NOT_OVERDUE")
            payload = {
                **action["payload"],
                "escalation": {"status": "OVERDUE", "reason": body["data"]["reason"]},
                "action_completion": "PENDING",
            }
            return write(c, ctx, "ManagementAction", payload, state="Escalated", previous=action)

        return self._run(
            identity, tenant, "escalate_overdue_management_action", action_id, body, correlation, apply
        )
