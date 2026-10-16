"""FR-EVA-001 controlled evaluation registration and document stage gates."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from psycopg.types.json import Jsonb

from .domain import DomainError
from .independence import require_object_independence
from .service import revision
from .store import audit, authorize, context, envelope, hash_data, load, visible_sql, write


def required_stage_documents(payload, stage):
    required = set(payload["required_documents"][stage])
    required.add("METHODOLOGY")
    if payload["sensitive_processing"]:
        required.update({"ETHICS", "SAFEGUARDING"})
    if stage == "PUBLICATION":
        required.add("DISCLOSURE_REVIEW")
    return required


def validate_stage_transition(current, requested):
    allowed = {
        "REGISTERED": {"FIELD_COLLECTION"},
        "FIELD_COLLECTION": {"FIELD_COLLECTION", "PUBLICATION"},
        "PUBLICATION": set(),
    }
    if requested not in allowed.get(current, set()):
        raise DomainError("CONFLICT_STATE", 409)


class EvaluationRegistry:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body, correlation):
        op = "create_evaluation_registration"
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op)
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
            programme = load(c, ctx, data["programme_id"], "Programme", "programmes.read")
            period = load(c, ctx, data["period_id"], "Period", "periods.read")
            if period["payload"].get("programme_id") and str(period["payload"]["programme_id"]) != str(
                programme["object_id"]
            ):
                raise DomainError("VALIDATION_FAILED", reason="PERIOD_PROGRAMME_MISMATCH")
            if data.get("programme_baseline_id"):
                baseline = revision(
                    c,
                    ctx,
                    data["programme_baseline_id"],
                    "Programme",
                    "programmes.read",
                )
                if str(baseline["object_id"]) != str(programme["object_id"]):
                    raise DomainError("VALIDATION_FAILED", reason="BASELINE_PROGRAMME_MISMATCH")
            if Decimal(data["budget"]["amount"]) <= 0:
                raise DomainError("VALIDATION_FAILED", reason="EVALUATION_BUDGET_INVALID")
            independence = data["independence"]
            if independence["claimed"]:
                if not all(
                    independence.get(key) for key in ("basis", "evidence_object_id", "evidence_revision_id")
                ):
                    raise DomainError("VALIDATION_FAILED", reason="INDEPENDENCE_EVIDENCE_REQUIRED")
                evidence = load(c, ctx, independence["evidence_object_id"], "Evidence", "evidence.read")
                if str(evidence["head_revision"]) != independence["evidence_revision_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                if evidence["payload"].get("evidence_type") != "INDEPENDENCE_BASIS":
                    raise DomainError("VALIDATION_FAILED", reason="INDEPENDENCE_EVIDENCE_KIND")
            elif any(
                independence.get(key) for key in ("basis", "evidence_object_id", "evidence_revision_id")
            ):
                raise DomainError("VALIDATION_FAILED", reason="INDEPENDENCE_NOT_CLAIMED")
            payload = {
                **data,
                "programme_revision_id": str(programme["head_revision"]),
                "period_revision_id": str(period["head_revision"]),
                "independence": {
                    **independence,
                    "verification": "EVIDENCE_ATTACHED_UNVERIFIED"
                    if independence["claimed"]
                    else "NOT_CLAIMED",
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
            authorize(c, ctx, op, evaluation_id, hidden=True)
            evaluation = load(
                c,
                ctx,
                evaluation_id,
                "EvaluationRegistration",
                "evaluations.draft.edit",
                lock=True,
            )
            require_object_independence(c, ctx, evaluation_id)
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
            if str(evaluation["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            requested = body["data"]["stage"]
            validate_stage_transition(evaluation["payload"]["stage"], requested)
            required = required_stage_documents(evaluation["payload"], requested)
            provided = {}
            seen_objects = set()
            for document in body["data"]["documents"]:
                if document["kind"] in provided or document["object_id"] in seen_objects:
                    raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_STAGE_DOCUMENT")
                row = load(c, ctx, document["object_id"], "Evidence", "evidence.read")
                if str(row["head_revision"]) != document["revision_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                if row["payload"].get("evidence_type") != document["kind"]:
                    raise DomainError("VALIDATION_FAILED", reason="DOCUMENT_KIND_MISMATCH")
                if row["payload"].get("upload_id") and row["payload"].get("scan_state") != "CLEAN":
                    raise DomainError("VALIDATION_FAILED", reason="DOCUMENT_NOT_CLEAN")
                if row["payload"].get("verification_state") == "REJECTED":
                    raise DomainError("VALIDATION_FAILED", reason="DOCUMENT_REJECTED")
                provided[document["kind"]] = document
                seen_objects.add(document["object_id"])
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
            payload = {
                **evaluation["payload"],
                "stage": requested if status == "PASSED" else evaluation["payload"]["stage"],
                "sensitive_processing_approved": (
                    outcome["sensitive_processing_approved"]
                    or evaluation["payload"].get("sensitive_processing_approved", False)
                ),
                "last_gate": outcome,
            }
            receipt = write(
                c,
                ctx,
                "EvaluationRegistration",
                payload,
                state=(
                    requested.title().replace("_", "")
                    if status == "PASSED"
                    else evaluation["lifecycle_state"]
                ),
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

    def read(self, identity, tenant, evaluation_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_evaluations", evaluation_id, hidden=True)
            return envelope(load(c, ctx, evaluation_id, "EvaluationRegistration", "evaluations.read"))

    def listing(self, identity, tenant, programme_id=None, limit=50, cursor=None):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_evaluation_registrations")
            if programme_id:
                load(c, ctx, programme_id, "Programme", "programmes.read")
            bound = self.service.cursor_binding(ctx, f"evaluations:{programme_id or 'all'}")
            key = self.service.cursor_key(bound, cursor)
            predicate, args = visible_sql(ctx, "evaluations.read")
            query = (
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
                "AND r.object_type='EvaluationRegistration' AND v.restriction_state='AVAILABLE' AND "
                + predicate
            )
            params = [tenant, *args]
            if programme_id:
                query += " AND v.payload->>'programme_id'=%s"
                params.append(str(programme_id))
            if key:
                query += " AND (r.created_at,r.object_id)>(%s::timestamptz,%s::uuid)"
                params += key
            query += " ORDER BY r.created_at,r.object_id LIMIT %s"
            params.append(limit + 1)
            rows = c.execute(query, params).fetchall()
            page = rows[:limit]
            return {
                "items": [envelope(row) for row in page],
                "next_cursor": self.service.next_cursor(
                    bound, [page[-1]["created_at"].isoformat(), str(page[-1]["object_id"])]
                )
                if len(rows) > limit
                else None,
                "scope_label": "Controlled evaluation registrations",
            }

    def gates(self, identity, tenant, evaluation_id, limit=50, cursor=None):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_evaluation_stage_gates", evaluation_id, hidden=True)
            load(c, ctx, evaluation_id, "EvaluationRegistration", "evaluations.read")
            bound = self.service.cursor_binding(ctx, f"evaluations/{evaluation_id}/stage-gates")
            key = self.service.cursor_key(bound, cursor)
            before = key[0] if key else 2147483647
            rows = c.execute(
                "SELECT revision_id,revision_number,created_at,author_id,payload->'last_gate' AS gate "
                "FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
                "AND object_type='EvaluationRegistration' AND payload ? 'last_gate' "
                "AND revision_number<%s ORDER BY revision_number DESC LIMIT %s",
                (tenant, evaluation_id, before, limit + 1),
            ).fetchall()
            page = rows[:limit]
            return {
                "items": [
                    {
                        "revision_id": str(row["revision_id"]),
                        "revision_number": row["revision_number"],
                        "recorded_at": row["created_at"].isoformat(),
                        "recorded_by": str(row["author_id"]),
                        "gate": row["gate"],
                    }
                    for row in page
                ],
                "next_cursor": self.service.next_cursor(bound, [page[-1]["revision_number"]])
                if len(rows) > limit
                else None,
                "scope_label": "Immutable evaluation stage-gate decisions",
            }
