"""FR-EVA-001 controlled evaluation registration and document stage gates."""

from datetime import datetime, timedelta, timezone

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


class EvaluationRegistry:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body, correlation):
        op = "create_evaluation_registration"
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
                return old["outcome"]
            data = body["data"]
            load(c, ctx, data["programme_id"], "Programme", "programmes.read")
            load(c, ctx, data["period_id"], "Period", "periods.read")
            independence = data["independence"]
            if independence["claimed"] and not independence.get("basis"):
                raise DomainError("VALIDATION_FAILED", reason="INDEPENDENCE_BASIS_REQUIRED")
            payload = {
                **data,
                "independence": {
                    **independence,
                    "verification": "SELF_DECLARED_UNVERIFIED" if independence["claimed"] else "NOT_CLAIMED",
                },
                "sensitive_processing_approved": False,
                "stage": "REGISTERED",
            }
            receipt = write(c, ctx, "EvaluationRegistration", payload)
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

    def gate(self, identity, tenant, evaluation_id, body, correlation):
        op = "evaluate_evaluation_stage_gate"
        fingerprint = hash_data({"evaluation_id": str(evaluation_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "patch_dashboards", evaluation_id)
            old = c.execute(
                "SELECT payload_hash,outcome FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            evaluation = load(c, ctx, evaluation_id, "EvaluationRegistration", lock=True)
            requested = body["data"]["stage"]
            required = set(evaluation["payload"]["required_documents"][requested])
            provided = {}
            for document in body["data"]["documents"]:
                row = load(c, ctx, document["object_id"], "Evidence", "evidence.read")
                if str(row["head_revision"]) != document["revision_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                provided[document["kind"]] = document
            missing = sorted(required - set(provided))
            status = "PASSED" if not missing else "BLOCKED"
            outcome = {
                "evaluation_id": str(evaluation_id),
                "stage": requested,
                "status": status,
                "missing_document_kinds": missing,
                "pinned_documents": [provided[key] for key in sorted(provided)],
                "sensitive_processing_approved": False,
            }
            if status == "PASSED":
                payload = {
                    **evaluation["payload"],
                    "stage": requested,
                    "last_gate": outcome,
                }
                receipt = write(
                    c,
                    ctx,
                    "EvaluationRegistration",
                    payload,
                    state=requested.title().replace("_", ""),
                    previous=evaluation,
                )
                audit(c, ctx, op, receipt, correlation)
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
