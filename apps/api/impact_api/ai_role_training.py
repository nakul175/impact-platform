"""Learner-scoped role training for an explicitly attested deployed solution."""

from datetime import datetime, timedelta, timezone

from psycopg.types.json import Jsonb

from .ai_adoption_plans import KIND as PLAN_KIND, READ_CAP
from .ai_learning_content import (
    ROLE_TRAINING_MODULES,
    TRAINING_CONTENT_VERSION,
    lesson_by_key,
)
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write

KIND = "AITrainingCompletion"
ROLE = "AUTHOR"
VIEW_OPERATION = "get_ai_role_training"
COMPLETE_OPERATION = "complete_ai_role_training_module"


def _invalid(reason="ROLE_TRAINING_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _author_role(c, ctx, plan_id):
    row = c.execute(
        "SELECT 1 FROM impact.member_role_assignment a "
        "JOIN impact.object_revision v ON v.tenant_id=a.tenant_id AND v.revision_id=a.role_revision "
        "JOIN impact.object_registry h ON h.tenant_id=v.tenant_id AND h.object_id=v.object_id "
        "WHERE a.tenant_id=%s AND a.membership_id=%s AND a.expires_at>now() "
        "AND h.lifecycle_state='Active' AND v.restriction_state='AVAILABLE' "
        "AND v.payload->>'managed_by'='impact-access-v1' AND v.payload->>'name'=%s "
        "AND EXISTS(SELECT 1 FROM impact.grant_current g "
        "JOIN impact.object_registry gh ON gh.tenant_id=g.tenant_id AND gh.object_id=g.object_id "
        "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
        "WHERE g.tenant_id=a.tenant_id AND g.object_id=ANY(a.grant_ids) "
        "AND g.subject_id=%s AND g.capability=%s AND g.purpose IS NULL "
        "AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now()) "
        "AND gh.lifecycle_state='Active' AND (s.scope_type='TENANT' OR EXISTS("
        "SELECT 1 FROM impact.scope_member sm WHERE sm.tenant_id=g.tenant_id "
        "AND sm.scope_id=g.scope_id AND sm.object_id=%s))) LIMIT 1",
        (ctx.tenant_id, ctx.membership_id, ROLE, ctx.principal_id, READ_CAP, plan_id),
    ).fetchone()
    if not row:
        raise DomainError("RESOURCE_UNAVAILABLE", 404)


def _deployment(plan, solution_id):
    attestation = plan["payload"].get("training_deployment")
    if (
        not attestation
        or attestation.get("solution_id") != solution_id
        or solution_id not in plan["payload"].get("solution_ids", [])
    ):
        raise DomainError("RESOURCE_UNAVAILABLE", 404)
    return attestation


def _completed(c, ctx, plan_id, attestation_id, solution_id):
    rows = c.execute(
        "SELECT v.payload FROM impact.object_registry r JOIN impact.object_revision v "
        "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
        "WHERE r.tenant_id=%s AND r.object_type=%s AND r.lifecycle_state='Completed' "
        "AND v.author_id=%s AND v.restriction_state='AVAILABLE' "
        "AND v.payload->>'learner_principal_id'=%s "
        "AND v.payload->>'learner_membership_id'=%s "
        "AND v.payload->>'plan_id'=%s AND v.payload->>'attestation_id'=%s "
        "AND v.payload->>'solution_id'=%s AND v.payload->>'role'=%s "
        "AND v.payload->>'module_version'=%s LIMIT 101",
        (
            ctx.tenant_id,
            KIND,
            ctx.principal_id,
            ctx.principal_id,
            ctx.membership_id,
            str(plan_id),
            attestation_id,
            solution_id,
            ROLE,
            TRAINING_CONTENT_VERSION,
        ),
    ).fetchall()
    if len(rows) > 100:
        raise DomainError("LIMIT_EXCEEDED", 422, reason="TRAINING_COMPLETION_LIMIT")
    return {row["payload"]["module_key"]: row["payload"] for row in rows}


def _module(key):
    if key not in ROLE_TRAINING_MODULES[ROLE]:
        raise DomainError("RESOURCE_UNAVAILABLE", 404)
    item = lesson_by_key(key)
    if not item:
        raise DomainError("RESOURCE_UNAVAILABLE", 404)
    return item


def _result(plan_id, plan_revision, attestation, completed):
    modules = []
    for key in ROLE_TRAINING_MODULES[ROLE]:
        item = _module(key)
        modules.append(
            {
                "key": key,
                "version": TRAINING_CONTENT_VERSION,
                "title": item[1],
                "lesson": item[2],
                "exercise": item[3],
                "completed": key in completed,
                "completed_at": completed.get(key, {}).get("completed_at"),
            }
        )
    return {
        "plan_id": str(plan_id),
        "plan_revision": str(plan_revision),
        "solution_id": attestation["solution_id"],
        "deployment_attestation_id": attestation["attestation_id"],
        "role": ROLE,
        "content_version": TRAINING_CONTENT_VERSION,
        "modules": modules,
    }


class AIRoleTraining:
    def __init__(self, service):
        self.service = service

    def get(self, identity, tenant, plan_id, solution_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, VIEW_OPERATION, plan_id, hidden=True)
            plan = load(c, ctx, plan_id, PLAN_KIND, READ_CAP)
            _author_role(c, ctx, plan_id)
            attestation = _deployment(plan, solution_id)
            return _result(
                plan_id,
                plan["head_revision"],
                attestation,
                _completed(c, ctx, plan_id, attestation["attestation_id"], solution_id),
            )

    def complete(self, identity, tenant, plan_id, module_key, body, correlation):
        if not isinstance(body, dict) or set(body) != {
            "operation_id",
            "expected_plan_revision",
            "solution_id",
            "module_version",
        }:
            _invalid()
        if body["module_version"] != TRAINING_CONTENT_VERSION:
            raise DomainError("CONFLICT_VERSION", 409, reason="TRAINING_CONTENT_CHANGED")
        _module(module_key)
        operation = COMPLETE_OPERATION
        fingerprint = hash_data([operation, plan_id, module_key, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, plan_id, hidden=True)
            plan = load(c, ctx, plan_id, PLAN_KIND, READ_CAP, lock=True)
            _author_role(c, ctx, plan_id)
            attestation = _deployment(plan, body["solution_id"])
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, operation, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                if old["outcome"].get("deployment_attestation_id") != attestation["attestation_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                return old["outcome"]
            if str(plan["head_revision"]) != body["expected_plan_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            completed = _completed(
                c, ctx, plan_id, attestation["attestation_id"], body["solution_id"]
            )
            if module_key in completed:
                outcome = _result(plan_id, plan["head_revision"], attestation, completed)
            else:
                receipt = write(
                    c,
                    ctx,
                    KIND,
                    {
                        "plan_id": str(plan_id),
                        "plan_revision": str(plan["head_revision"]),
                        "attestation_id": attestation["attestation_id"],
                        "solution_id": body["solution_id"],
                        "role": ROLE,
                        "module_key": module_key,
                        "module_version": TRAINING_CONTENT_VERSION,
                        "learner_principal_id": ctx.principal_id,
                        "learner_membership_id": ctx.membership_id,
                        "completed_at": now.isoformat(),
                    },
                    "Completed",
                )
                receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
                audit(c, ctx, operation, receipt, correlation)
                completed = _completed(
                    c, ctx, plan_id, attestation["attestation_id"], body["solution_id"]
                )
                outcome = _result(plan_id, plan["head_revision"], attestation, completed)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    operation,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    now + timedelta(days=7),
                ),
            )
            return outcome
