"""FR-EVA-006 versioned learning questions and contextual applicability guards."""

from datetime import datetime, timedelta, timezone

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


class LearningAgenda:
    def __init__(self, service):
        self.service = service

    def _command(self, identity, tenant, op, fingerprint, operation_id, correlation, fn):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, operation_id),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            receipt = fn(c, ctx)
            receipt.update(operation_id=operation_id, correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    operation_id,
                    fingerprint,
                    Jsonb(receipt),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return receipt

    def create(self, identity, tenant, body, correlation):
        data = body["data"]

        def apply(c, ctx):
            load(c, ctx, data["decision_id"], "Decision", "decisions.read")
            if not c.execute(
                "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s "
                "AND principal_kind='HUMAN' AND active",
                (tenant, data["owner_id"]),
            ).fetchone():
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            sources = []
            for source in data["evidence"]:
                row = load(c, ctx, source["object_id"], "Evidence", "evidence.read")
                if str(row["head_revision"]) != source["revision_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                sources.append({**source, "classification": row["classification"]})
            payload = {
                **data,
                "evidence": sources,
                "conclusion": None,
                "remaining_uncertainty": None,
                "applicability": "ORIGINAL_CONTEXT_ONLY",
            }
            return write(c, ctx, "LearningQuestion", payload, state="Open")

        return self._command(
            identity,
            tenant,
            "create_learning_question",
            hash_data(body),
            body["operation_id"],
            correlation,
            apply,
        )

    def close(self, identity, tenant, question_id, body, correlation):
        def apply(c, ctx):
            row = load(c, ctx, question_id, "LearningQuestion", "evaluations.read", lock=True)
            if str(row["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if row["lifecycle_state"] != "Open":
                raise DomainError("INVALID_STATE", 409)
            if c.execute(
                "SELECT 1 FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s "
                "AND natural_identity_id=%s",
                (tenant, question_id, ctx.identity.natural_identity_id),
            ).fetchone():
                raise DomainError("INDEPENDENCE_REQUIRED", 409)
            data = body["data"]
            return write(
                c,
                ctx,
                "LearningQuestion",
                {**row["payload"], **data, "closed_revision": str(row["head_revision"])},
                state="Closed",
                previous=row,
            )

        return self._command(
            identity,
            tenant,
            "close_learning_question",
            hash_data({"id": str(question_id), "body": body}),
            body["operation_id"],
            correlation,
            apply,
        )

    def reopen(self, identity, tenant, question_id, body, correlation):
        def apply(c, ctx):
            row = load(c, ctx, question_id, "LearningQuestion", "evaluations.read", lock=True)
            if str(row["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if row["lifecycle_state"] != "Closed":
                raise DomainError("INVALID_STATE", 409)
            history = list(row["payload"].get("prior_reasoning", []))
            history.append(
                {
                    "revision_id": str(row["head_revision"]),
                    "conclusion": row["payload"]["conclusion"],
                    "remaining_uncertainty": row["payload"]["remaining_uncertainty"],
                }
            )
            return write(
                c,
                ctx,
                "LearningQuestion",
                {**row["payload"], "prior_reasoning": history, "reopen_reason": body["data"]["reason"]},
                state="Open",
                previous=row,
            )

        return self._command(
            identity,
            tenant,
            "reopen_learning_question",
            hash_data({"id": str(question_id), "body": body}),
            body["operation_id"],
            correlation,
            apply,
        )

    def summary(self, identity, tenant, question_id, disclosure_id=None):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_learning_question_summary", question_id)
            row = load(c, ctx, question_id, "LearningQuestion", "evaluations.read")
            restricted = [
                item for item in row["payload"]["evidence"] if item["classification"] == "RESTRICTED"
            ]
            if restricted:
                if not disclosure_id:
                    raise DomainError("DISCLOSURE_REVIEW_REQUIRED", 409)
                disclosure = load(c, ctx, disclosure_id, "Disclosure", "disclosures.read")
                if disclosure["lifecycle_state"] != "Approved":
                    raise DomainError("DISCLOSURE_REVIEW_REQUIRED", 409)
            return {
                "question_id": str(question_id),
                "question_revision": str(row["head_revision"]),
                "context": row["payload"]["context"],
                "conclusion": row["payload"]["conclusion"],
                "remaining_uncertainty": row["payload"]["remaining_uncertainty"],
                "evidence": row["payload"]["evidence"],
            }

    def consider_context(self, identity, tenant, question_id, body, correlation):
        def apply(c, ctx):
            row = load(c, ctx, question_id, "LearningQuestion", "evaluations.read", lock=True)
            if str(row["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            return write(
                c,
                ctx,
                "LearningApplicabilityReview",
                {
                    "question_id": str(question_id),
                    "question_revision": str(row["head_revision"]),
                    "source_context": row["payload"]["context"],
                    "target_context": body["data"]["target_context"],
                    "status": "REVIEW_REQUIRED",
                    "transferred_conclusion": None,
                },
                state="Pending",
            )

        return self._command(
            identity,
            tenant,
            "consider_learning_context",
            hash_data({"id": str(question_id), "body": body}),
            body["operation_id"],
            correlation,
            apply,
        )
