"""FR-EVA-002 versioned sampling methodology and guarded sample exports."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from psycopg.types.json import Jsonb

from .domain import DomainError
from .independence import require_object_independence
from .store import audit, authorize, context, envelope, hash_data, load, visible_sql, write


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


def sample_export(methodology, weighted, population_estimate):
    strata = methodology["strata"]
    eligible = sum(item["eligible_count"] for item in strata)
    sampled = sum(item["sampled_count"] for item in strata)
    missing = [item["code"] for item in strata if item.get("weight") is None]
    invalid = [
        item["code"]
        for item in strata
        if item.get("weight") is not None and Decimal(str(item["weight"])) <= 0
    ]
    if invalid:
        raise DomainError("VALIDATION_FAILED", reason="INVALID_EXPANSION_WEIGHT")
    if weighted and missing:
        raise DomainError("VALIDATION_FAILED", reason="MISSING_WEIGHTS_BLOCK_WEIGHTED_OUTPUT")
    if population_estimate and not weighted:
        raise DomainError("VALIDATION_FAILED", reason="POPULATION_ESTIMATE_REQUIRES_WEIGHTED_OUTPUT")
    expansion = methodology.get("expansion_method")
    if population_estimate and not expansion:
        raise DomainError("VALIDATION_FAILED", reason="POPULATION_EXPANSION_METHOD_REQUIRED")
    estimate = None
    if population_estimate:
        estimate = sum(Decimal(str(item["sampled_count"])) * Decimal(str(item["weight"])) for item in strata)
    return {
        "methodology_revision": methodology["methodology_revision"],
        "eligible_denominator": eligible,
        "sample_count": sampled,
        "sample_count_label": "SAMPLE_COUNT_NOT_ALL_BENEFICIARIES",
        "weighted": weighted,
        "missing_weight_strata": missing,
        "expansion_method": expansion,
        "population_estimate": format(estimate, "f") if estimate is not None else None,
        "strata": strata,
        "nonresponse_rules": methodology["nonresponse_rules"],
    }


def _validate(data):
    strata = data["strata"]
    if len({item["code"] for item in strata}) != len(strata):
        raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_STRATUM")
    if any(item["sampled_count"] > item["eligible_count"] for item in strata):
        raise DomainError("VALIDATION_FAILED", reason="SAMPLE_EXCEEDS_ELIGIBLE_FRAME")
    if any(item["nonresponse_count"] > item["sampled_count"] for item in strata):
        raise DomainError("VALIDATION_FAILED", reason="NONRESPONSE_EXCEEDS_SAMPLE")
    if any(item.get("weight") is not None and Decimal(str(item["weight"])) <= 0 for item in strata):
        raise DomainError("VALIDATION_FAILED", reason="INVALID_EXPANSION_WEIGHT")
    if data.get("expansion_method") and any(item.get("weight") is None for item in strata):
        raise DomainError("VALIDATION_FAILED", reason="EXPANSION_REQUIRES_ALL_WEIGHTS")


class EvaluationMethodology:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body, correlation):
        op = "create_evaluation_methodology"
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op)
            evaluation = load(
                c,
                ctx,
                body["data"]["evaluation_id"],
                "EvaluationRegistration",
                "evaluations.read",
                lock=True,
            )
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
            payload = {
                **body["data"],
                "evaluation_revision": str(evaluation["head_revision"]),
                "methodology_revision": "1",
                "amendment": None,
                "review_state": "PENDING",
                "review": None,
            }
            _validate(payload)
            receipt = write(c, ctx, "EvaluationMethodology", payload, state="ReviewPending")
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            _remember(c, ctx, op, body["operation_id"], fingerprint, receipt)
            return receipt

    def amend(self, identity, tenant, methodology_id, body, correlation):
        op = "amend_evaluation_methodology"
        fingerprint = hash_data({"methodology_id": str(methodology_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op, methodology_id, hidden=True)
            current = load(
                c, ctx, methodology_id, "EvaluationMethodology", "evaluations.draft.edit", lock=True
            )
            load(c, ctx, current["payload"]["evaluation_id"], "EvaluationRegistration", "evaluations.read")
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
            if str(current["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if current["payload"]["review_state"] not in {"REVIEWED", "REJECTED"}:
                raise DomainError("INVALID_STATE", 409, reason="METHODOLOGY_REVIEW_PENDING")
            if not body["data"]["changes"]:
                raise DomainError("VALIDATION_FAILED", reason="METHODOLOGY_CHANGE_REQUIRED")
            payload = {
                **current["payload"],
                **body["data"]["changes"],
                "methodology_revision": str(int(current["payload"]["methodology_revision"]) + 1),
                "amendment": {
                    "reason": body["data"]["reason"],
                    "relative_to_data_inspection": body["data"]["relative_to_data_inspection"],
                    "amended_at": datetime.now(timezone.utc).isoformat(),
                    "amended_by": str(ctx.principal_id),
                },
                "review_state": "PENDING",
            }
            _validate(payload)
            receipt = write(c, ctx, "EvaluationMethodology", payload, state="ReviewPending", previous=current)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            _remember(c, ctx, op, body["operation_id"], fingerprint, receipt)
            return receipt

    def review(self, identity, tenant, methodology_id, body, correlation):
        op = "review_evaluation_methodology"
        fingerprint = hash_data({"methodology_id": str(methodology_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op, methodology_id, hidden=True)
            current = load(
                c, ctx, methodology_id, "EvaluationMethodology", "evaluations.draft.edit", lock=True
            )
            load(c, ctx, current["payload"]["evaluation_id"], "EvaluationRegistration", "evaluations.read")
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
            require_object_independence(c, ctx, methodology_id)
            if str(current["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if current["payload"]["review_state"] != "PENDING":
                raise DomainError("INVALID_STATE", 409)
            decision = body["data"]["decision"]
            payload = {
                **current["payload"],
                "review_state": "REVIEWED" if decision == "APPROVE" else "REJECTED",
                "review": {
                    "decision": decision,
                    "reason": body["data"]["reason"],
                    "reviewed_at": datetime.now(timezone.utc).isoformat(),
                    "reviewed_by": str(ctx.principal_id),
                },
            }
            state = "Reviewed" if decision == "APPROVE" else "Rejected"
            receipt = write(c, ctx, "EvaluationMethodology", payload, state=state, previous=current)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            _remember(c, ctx, op, body["operation_id"], fingerprint, receipt)
            return receipt

    def export(self, identity, tenant, methodology_id, body):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "export_evaluation_sample", methodology_id, hidden=True)
            current = load(c, ctx, methodology_id, "EvaluationMethodology", "evaluations.read")
            load(c, ctx, current["payload"]["evaluation_id"], "EvaluationRegistration", "evaluations.read")
            if current["payload"]["review_state"] != "REVIEWED":
                raise DomainError("INVALID_STATE", 409, reason="METHODOLOGY_NOT_REVIEWED")
            return sample_export(
                current["payload"],
                body["weighted"],
                body["population_estimate"],
            )

    def read(self, identity, tenant, methodology_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_evaluation_methodology", methodology_id, hidden=True)
            current = load(c, ctx, methodology_id, "EvaluationMethodology", "evaluations.read")
            load(c, ctx, current["payload"]["evaluation_id"], "EvaluationRegistration", "evaluations.read")
            return envelope(current)

    def listing(self, identity, tenant, evaluation_id, limit=50, cursor=None):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_evaluation_methodologies")
            load(c, ctx, evaluation_id, "EvaluationRegistration", "evaluations.read")
            bound = self.service.cursor_binding(ctx, f"evaluation-methodologies:{evaluation_id}")
            key = self.service.cursor_key(bound, cursor)
            predicate, args = visible_sql(ctx, "evaluations.read")
            query = (
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
                "AND r.object_type='EvaluationMethodology' AND v.restriction_state='AVAILABLE' "
                "AND v.payload->>'evaluation_id'=%s AND " + predicate
            )
            params = [tenant, str(evaluation_id), *args]
            if key:
                query += " AND (r.created_at,r.object_id)>(%s::timestamptz,%s::uuid)"
                params += key
            rows = c.execute(
                query + " ORDER BY r.created_at,r.object_id LIMIT %s", [*params, limit + 1]
            ).fetchall()
            page = rows[:limit]
            return {
                "items": [envelope(row) for row in page],
                "next_cursor": self.service.next_cursor(
                    bound, [page[-1]["created_at"].isoformat(), str(page[-1]["object_id"])]
                )
                if len(rows) > limit
                else None,
                "scope_label": "Methodologies for the selected evaluation",
            }

    def history(self, identity, tenant, methodology_id, limit=50, cursor=None):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_evaluation_methodology_history", methodology_id, hidden=True)
            current = load(c, ctx, methodology_id, "EvaluationMethodology", "evaluations.read")
            load(c, ctx, current["payload"]["evaluation_id"], "EvaluationRegistration", "evaluations.read")
            bound = self.service.cursor_binding(ctx, f"evaluation-methodologies/{methodology_id}/history")
            key = self.service.cursor_key(bound, cursor)
            before = key[0] if key else 2147483647
            rows = c.execute(
                "SELECT revision_id,revision_number,created_at,author_id,payload FROM impact.object_revision "
                "WHERE tenant_id=%s AND object_id=%s AND object_type='EvaluationMethodology' "
                "AND revision_number<%s ORDER BY revision_number DESC LIMIT %s",
                (tenant, methodology_id, before, limit + 1),
            ).fetchall()
            page = rows[:limit]
            return {
                "items": [
                    {
                        "revision_id": str(row["revision_id"]),
                        "revision_number": row["revision_number"],
                        "recorded_at": row["created_at"].isoformat(),
                        "recorded_by": str(row["author_id"]),
                        "data": row["payload"],
                    }
                    for row in page
                ],
                "next_cursor": self.service.next_cursor(bound, [page[-1]["revision_number"]])
                if len(rows) > limit
                else None,
                "scope_label": "Immutable methodology amendment and review history",
            }
