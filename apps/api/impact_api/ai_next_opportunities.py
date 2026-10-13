"""Explainable Improve-stage suggestions whose uptake always starts a new Diagnose cycle."""

from datetime import datetime, timedelta, timezone
from uuid import UUID, NAMESPACE_URL, uuid5

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write

CYCLE_KIND = "AIImproveDiagnosisCycle"
DIAGNOSIS_KIND = "AIDiagnosis"


def _invalid(reason="NEXT_OPPORTUNITY_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    try:
        canonical = str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        _invalid()
    if canonical != value:
        _invalid()
    return canonical


def _owner(c, ctx):
    owner = c.execute(
        "SELECT m.object_id AS membership_id,h.head_revision AS membership_revision,p.principal_id "
        "FROM impact.tenant_custody t JOIN impact.membership_current m ON m.tenant_id=t.tenant_id "
        "AND m.object_id=t.owner_membership_id JOIN impact.object_registry h ON h.tenant_id=m.tenant_id "
        "AND h.object_id=m.object_id JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id "
        "AND p.identity_id=m.identity_id WHERE t.tenant_id=%s AND h.lifecycle_state='Active' "
        "AND p.active AND (m.expires_at IS NULL OR m.expires_at>now())",
        (ctx.tenant_id,),
    ).fetchone()
    if (
        not owner
        or str(owner["principal_id"]) != str(ctx.principal_id)
        or str(owner["membership_id"]) != str(ctx.membership_id)
    ):
        raise DomainError("RESOURCE_UNAVAILABLE", 404)
    return owner


def _suggestion_id(tenant, diagnosis_id, revision_id, problem_id):
    return str(uuid5(NAMESPACE_URL, f"impact:{tenant}:improve:{diagnosis_id}:{revision_id}:{problem_id}"))


class AINextOpportunities:
    def __init__(self, service, diagnoses):
        self.service, self.diagnoses = service, diagnoses

    def _suggestions(self, c, identity, tenant):
        ctx = context(c, identity, tenant)
        authorize(c, ctx, "list_ai_next_opportunities", hidden=True)
        _owner(c, ctx)
        rows = c.execute(
            "SELECT q.object_id AS review_id,q.head_revision AS review_revision,"
            "o.payload->>'diagnosis_id' AS object_id,o.payload->>'diagnosis_revision' AS head_revision "
            "FROM impact.object_registry q JOIN impact.object_revision qv ON qv.tenant_id=q.tenant_id "
            "AND qv.revision_id=q.head_revision JOIN impact.object_revision o ON o.tenant_id=q.tenant_id "
            "AND o.object_id=(qv.payload->'source'->>'outcome_observation_id')::uuid "
            "AND o.revision_id=(qv.payload->'source'->>'outcome_observation_revision')::uuid "
            "WHERE q.tenant_id=%s AND q.object_type='AIQuarterlyValueReview' "
            "AND q.lifecycle_state='Completed' AND qv.restriction_state='AVAILABLE' "
            "AND o.restriction_state='AVAILABLE' ORDER BY qv.created_at DESC,q.object_id DESC LIMIT 1",
            (tenant,),
        ).fetchall()
        result = []
        for row in rows:
            payload = self.diagnoses.revision(c, tenant, str(row["object_id"]), str(row["head_revision"]))
            self.diagnoses.check_evidence(c, identity, tenant, payload)
            by_id = {p["problem_id"]: p for p in payload["problems"]}
            for rank, problem_id in enumerate(payload["priority_order"], 1):
                problem = by_id[problem_id]
                suggestion_id = _suggestion_id(
                    tenant, str(row["object_id"]), str(row["head_revision"]), problem_id
                )
                taken = c.execute(
                    "SELECT 1 FROM impact.object_registry h JOIN impact.object_revision v ON v.tenant_id=h.tenant_id "
                    "AND v.revision_id=h.head_revision WHERE h.tenant_id=%s AND h.object_type=%s "
                    "AND v.payload->>'suggestion_id'=%s LIMIT 1",
                    (tenant, CYCLE_KIND, suggestion_id),
                ).fetchone()
                if not taken:
                    result.append(
                        {
                            "suggestion_id": suggestion_id,
                            "title": problem["description"].strip()[:150],
                            "affected_area": problem["affected_area"],
                            "explanation": f"Priority {rank} in the current completed diagnosis; uptake starts a new Draft diagnosis.",
                            "source_diagnosis_id": str(row["object_id"]),
                            "source_diagnosis_revision": str(row["head_revision"]),
                            "source_problem_id": problem_id,
                            "source_review_id": str(row["review_id"]),
                            "source_review_revision": str(row["review_revision"]),
                        }
                    )
        return result[:20]

    def listing(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            return {"stage": "Improve", "items": self._suggestions(c, identity, tenant)}

    def take_up(self, identity, tenant, suggestion_id, body, correlation):
        _uuid(suggestion_id)
        if not isinstance(body, dict) or set(body) != {"operation_id"}:
            _invalid()
        _uuid(body["operation_id"])
        operation = "take_up_ai_next_opportunity"
        fingerprint = hash_data([operation, suggestion_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            authorize(c, ctx, "create_ai_diagnosis", hidden=True)
            owner = _owner(c, ctx)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = datetime.now(timezone.utc)
            durable = c.execute(
                "SELECT * FROM impact.ai_improve_diagnosis_cycle WHERE tenant_id=%s AND taker_principal_id=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if durable:
                if bytes(durable["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return {
                    "operation_id": str(durable["operation_id"]),
                    "correlation_id": str(durable["correlation_id"]),
                    "cycle_id": str(durable["cycle_id"]),
                    "cycle_revision": str(durable["cycle_revision"]),
                    "cycle_state": "Diagnose",
                    "diagnosis_id": str(durable["created_diagnosis_id"]),
                    "diagnosis_revision": str(durable["created_diagnosis_revision"]),
                    "diagnosis_state": "Draft",
                    "saved_at": durable["taken_up_at"].isoformat(),
                }
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, operation, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                load(c, ctx, old["outcome"]["cycle_id"], CYCLE_KIND, "ai.diagnosis.read")
                load(c, ctx, old["outcome"]["diagnosis_id"], DIAGNOSIS_KIND, "ai.diagnosis.read")
                return old["outcome"]
            suggestions = {item["suggestion_id"]: item for item in self._suggestions(c, identity, tenant)}
            suggestion = suggestions.get(suggestion_id)
            if not suggestion:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if c.execute(
                "SELECT 1 FROM impact.ai_improve_diagnosis_cycle WHERE tenant_id=%s AND suggestion_id=%s",
                (tenant, suggestion_id),
            ).fetchone():
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="SUGGESTION_ALREADY_TAKEN_UP")
            diagnosis_payload = {
                "title": "Diagnose: " + suggestion["title"],
                "problems": [],
                "priority_order": [],
                "diagnosis_state": "Draft",
            }
            diagnosis = write(c, ctx, DIAGNOSIS_KIND, diagnosis_payload, "Draft")
            cycle_payload = {
                **suggestion,
                "diagnosis_id": diagnosis["object_id"],
                "diagnosis_revision": diagnosis["revision_id"],
                "diagnosis_state": "Draft",
                "taken_up_at": now.isoformat(),
                "taken_up_by": str(ctx.principal_id),
                "owner_membership_id": str(ctx.membership_id),
                "owner_membership_revision": str(owner["membership_revision"]),
            }
            cycle = write(c, ctx, CYCLE_KIND, cycle_payload, "Diagnose")
            outcome = {
                "operation_id": body["operation_id"],
                "correlation_id": correlation,
                "cycle_id": cycle["object_id"],
                "cycle_revision": cycle["revision_id"],
                "cycle_state": "Diagnose",
                "diagnosis_id": diagnosis["object_id"],
                "diagnosis_revision": diagnosis["revision_id"],
                "diagnosis_state": "Draft",
                "saved_at": cycle["saved_at"],
            }
            audit(c, ctx, operation, outcome, correlation)
            c.execute(
                "INSERT INTO impact.ai_improve_diagnosis_cycle(tenant_id,cycle_id,cycle_revision,suggestion_id,source_review_id,source_review_revision,source_diagnosis_id,source_diagnosis_revision,source_problem_id,created_diagnosis_id,created_diagnosis_revision,taker_principal_id,taker_membership_id,taker_membership_revision,operation_id,payload_hash,correlation_id,taken_up_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    cycle["object_id"],
                    cycle["revision_id"],
                    suggestion_id,
                    suggestion["source_review_id"],
                    suggestion["source_review_revision"],
                    suggestion["source_diagnosis_id"],
                    suggestion["source_diagnosis_revision"],
                    suggestion["source_problem_id"],
                    diagnosis["object_id"],
                    diagnosis["revision_id"],
                    ctx.principal_id,
                    ctx.membership_id,
                    owner["membership_revision"],
                    body["operation_id"],
                    fingerprint,
                    correlation,
                    now,
                ),
            )
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
