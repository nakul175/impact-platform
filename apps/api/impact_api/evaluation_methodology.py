"""FR-EVA-002 versioned sampling methodology and guarded sample exports."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


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
    if weighted and missing:
        raise DomainError("VALIDATION_FAILED", reason="MISSING_WEIGHTS_BLOCK_WEIGHTED_OUTPUT")
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
            authorize(c, ctx, "create_dashboards")
            old = c.execute(
                "SELECT payload_hash,outcome FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            evaluation = load(c, ctx, body["data"]["evaluation_id"], "EvaluationRegistration", lock=True)
            payload = {
                **body["data"],
                "evaluation_revision": str(evaluation["head_revision"]),
                "methodology_revision": "1",
                "amendment": None,
                "review_state": "REVIEWED",
            }
            _validate(payload)
            receipt = write(c, ctx, "EvaluationMethodology", payload, state="Reviewed")
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
            authorize(c, ctx, "patch_dashboards", methodology_id)
            old = c.execute(
                "SELECT payload_hash,outcome FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            current = load(c, ctx, methodology_id, "EvaluationMethodology", lock=True)
            if current["payload"]["review_state"] != "REVIEWED":
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
            authorize(c, ctx, "patch_dashboards", methodology_id)
            old = c.execute(
                "SELECT payload_hash,outcome FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            current = load(c, ctx, methodology_id, "EvaluationMethodology", lock=True)
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
            authorize(c, ctx, "preview_dashboards", methodology_id)
            current = load(c, ctx, methodology_id, "EvaluationMethodology")
            if current["payload"]["review_state"] != "REVIEWED":
                raise DomainError("INVALID_STATE", 409, reason="METHODOLOGY_NOT_REVIEWED")
            return sample_export(
                current["payload"],
                body["weighted"],
                body["population_estimate"],
            )
