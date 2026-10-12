"""Immutable, advisor-authored pilot fit scores for source-backed solution options."""

from datetime import timedelta
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from .ai_solutions_catalog import SolutionsCatalogInvalid, solutions_catalog
from .domain import DomainError
from .store import audit, authorize, context, hash_data

DIMENSIONS = ("size", "budget", "context", "language", "data_sensitivity", "existing_systems")
RUBRIC_VERSION = "pilot-fit-v1"


def invalid(reason="AI_SOLUTION_FIT_INVALID"):
    raise DomainError("VALIDATION_FAILED", 400, reason=reason)


def uid(value):
    try:
        result = str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        invalid()
    if result != value:
        invalid()
    return result


class AISolutionFitScores:
    def __init__(self, service):
        self.service = service

    @staticmethod
    def _catalog_match(opportunity_id, solution_id):
        try:
            catalogue = solutions_catalog()
        except SolutionsCatalogInvalid:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_SOLUTIONS_CATALOG_INVALID") from None
        item = next((item for item in catalogue["solutions"] if item["id"] == solution_id), None)
        if not item or opportunity_id not in item["use_case_ids"]:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return catalogue["content_version"]

    @staticmethod
    def _result(row):
        dimensions = {
            name: {"score": row[name], "explanation": row["explanations"][name]}
            for name in DIMENSIONS
        }
        complete = all(dimensions[name]["score"] is not None for name in DIMENSIONS)
        return {
            "score_id": str(row["score_id"]),
            "opportunity_id": row["opportunity_id"],
            "solution_id": row["solution_id"],
            "catalogue_content_version": row["catalogue_content_version"],
            "rubric_version": row["rubric_version"],
            "status": "COMPLETE" if complete else "INCOMPLETE",
            "advisor_membership_id": str(row["advisor_membership_id"]),
            "dimensions": dimensions,
            "scored_at": row["scored_at"].isoformat(),
        }

    def list(self, identity, tenant, opportunity_id):
        if not isinstance(opportunity_id, str) or not opportunity_id.strip() or len(opportunity_id) > 120:
            invalid()
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_solution_fit_scores", hidden=True)
            rows = c.execute(
                "SELECT DISTINCT ON(solution_id) * FROM impact.ai_solution_fit_score "
                "WHERE tenant_id=%s AND opportunity_id=%s ORDER BY solution_id,scored_at DESC,score_id DESC",
                (tenant, opportunity_id),
            ).fetchall()
            return {"items": [self._result(row) for row in rows]}

    def create(self, identity, tenant, body, correlation):
        required = {"operation_id", "opportunity_id", "solution_id", "rubric_version", "dimensions"}
        if not isinstance(body, dict) or set(body) != required:
            invalid()
        uid(body["operation_id"])
        if body["rubric_version"] != RUBRIC_VERSION:
            invalid("AI_SOLUTION_FIT_RUBRIC_UNSUPPORTED")
        if any(not isinstance(body.get(key), str) or not body[key].strip() or len(body[key]) > 120 for key in ("opportunity_id", "solution_id")):
            invalid()
        dimensions = body["dimensions"]
        if not isinstance(dimensions, dict) or set(dimensions) != set(DIMENSIONS):
            invalid("AI_SOLUTION_FIT_INCOMPLETE")
        for value in dimensions.values():
            if not isinstance(value, dict) or set(value) != {"score", "explanation"}:
                invalid("AI_SOLUTION_FIT_INCOMPLETE")
            if type(value["score"]) is not int or not 1 <= value["score"] <= 5:
                invalid()
            if not isinstance(value["explanation"], str) or not value["explanation"].strip() or len(value["explanation"]) > 1000:
                invalid("AI_SOLUTION_FIT_INCOMPLETE")
        content_version = self._catalog_match(body["opportunity_id"], body["solution_id"])
        name = "create_ai_solution_fit_score"
        fingerprint = hash_data([name, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, name, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            receipt = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, name, body["operation_id"]),
            ).fetchone()
            if receipt:
                if bytes(receipt["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if receipt["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return receipt["outcome"]
            advisor = c.execute(
                "SELECT impact.member_natural_identity(%s,%s) AS natural_id FROM impact.membership_current m "
                "JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id "
                "WHERE m.tenant_id=%s AND m.object_id=%s AND h.lifecycle_state='Active' "
                "AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now())",
                (tenant, ctx.principal_id, tenant, ctx.membership_id),
            ).fetchone()
            if not advisor or not advisor["natural_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            score_id = str(uuid4())
            explanations = {name: dimensions[name]["explanation"].strip() for name in DIMENSIONS}
            c.execute(
                "INSERT INTO impact.ai_solution_fit_score(tenant_id,score_id,opportunity_id,solution_id,catalogue_content_version,rubric_version,size,budget,context,language,data_sensitivity,existing_systems,explanations,advisor_principal_id,advisor_membership_id,advisor_natural_identity_id,scored_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (tenant, score_id, body["opportunity_id"], body["solution_id"], content_version, RUBRIC_VERSION, *[dimensions[name]["score"] for name in DIMENSIONS], Jsonb(explanations), ctx.principal_id, ctx.membership_id, advisor["natural_id"], now),
            )
            row = c.execute("SELECT * FROM impact.ai_solution_fit_score WHERE tenant_id=%s AND score_id=%s", (tenant, score_id)).fetchone()
            result = self._result(row)
            audit(c, ctx, name, {"object_id": score_id, "business_state": "COMPLETE", "saved_at": now.isoformat()}, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (tenant, ctx.principal_id, name, body["operation_id"], fingerprint, Jsonb(result), now + timedelta(days=7)),
            )
            return result
