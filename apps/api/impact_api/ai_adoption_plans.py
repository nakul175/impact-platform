"""Tenant-shared adoption drafts using the platform's immutable revision and receipt model."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID

from psycopg.types.json import Jsonb

from .ai_enablement_catalog import CONTENT_VERSION as CATALOG_VERSION
from .ai_enablement_catalog import catalog, validate_profile
from .ai_solutions_catalog import CONTENT_VERSION as SOLUTIONS_VERSION
from .ai_solutions_catalog import SOLUTION_IDS
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, visible_sql, write

KIND = "AIAdoptionPlan"
ROUTE = "ai-enablement/plans"
READ_CAP = "ai.enablement.read"
PILOT_ACTIONS = ("DEFINE_GOAL", "SYNTHETIC_TRIAL", "HUMAN_REVIEW", "TRAIN_STAFF", "REVIEW_OUTCOME")
PLAN_FIELDS = {"title", "profile", "solution_ids", "learning_completed", "procurement", "pilot"}
PROCUREMENT_LIMITS = {
    "requirements": 2000,
    "data_boundary": 2000,
    "budget_notes": 500,
    "vendor_questions": 2000,
}


def _invalid(reason="AI_ADOPTION_PLAN_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    if not isinstance(value, str):
        _invalid()
    try:
        return str(UUID(value))
    except (ValueError, AttributeError):
        _invalid()


def _text(value, maximum, required=False):
    if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
        _invalid()


def _ids(value, allowed, maximum):
    if (
        not isinstance(value, list)
        or len(value) > maximum
        or any(not isinstance(item, str) or item not in allowed for item in value)
        or len(value) != len(set(value))
    ):
        _invalid()


def learning_keys():
    return frozenset(
        f"{path['id']}:{index}" for path in catalog()["learning_paths"] for index in range(len(path["steps"]))
    )


def validate_plan(data):
    """Closed, bounded drafts; every selected solution and learning action is known."""
    if not isinstance(data, dict) or set(data) != PLAN_FIELDS:
        _invalid()
    _text(data["title"], 150, required=True)
    try:
        validate_profile(data["profile"])
    except ValueError:
        _invalid("AI_PROFILE_INVALID")
    _ids(data["solution_ids"], SOLUTION_IDS, 4)
    keys = learning_keys()
    _ids(data["learning_completed"], keys, len(keys))
    procurement = data["procurement"]
    if not isinstance(procurement, dict) or set(procurement) != set(PROCUREMENT_LIMITS):
        _invalid()
    for field, maximum in PROCUREMENT_LIMITS.items():
        _text(procurement[field], maximum)
    pilot = data["pilot"]
    if not isinstance(pilot, dict) or set(pilot) != {"success_measure", "completed_actions"}:
        _invalid()
    _text(pilot["success_measure"], 1000)
    _ids(pilot["completed_actions"], PILOT_ACTIONS, len(PILOT_ACTIONS))


def _request(body, update):
    expected = {"operation_id", "data"} | ({"expected_revision"} if update else set())
    if not isinstance(body, dict) or set(body) != expected or not isinstance(body["data"], dict):
        _invalid()
    _uuid(body["operation_id"])
    if update:
        _uuid(body["expected_revision"])


def _result(row):
    return {
        "object_id": str(row["object_id"]),
        "revision_id": str(row["head_revision"]),
        "business_state": row["lifecycle_state"],
        "data": deepcopy(row["payload"]),
    }


class AIAdoptionPlans:
    def __init__(self, service):
        self.service = service

    def get(self, identity, tenant, object_id):
        _uuid(object_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_adoption_plan", object_id, hidden=True)
            return _result(load(c, ctx, object_id, KIND, READ_CAP))

    def listing(self, identity, tenant, limit=50, cursor=None):
        if type(limit) is not int or not 1 <= limit <= 100:
            _invalid()
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            # A scoped reader may list only their scope; no read grant means hidden.
            if not any(g["capability"] == READ_CAP and g["purpose"] is None for g in ctx.grants):
                authorize(c, ctx, "list_ai_adoption_plans", hidden=True)
            bound = self.service.cursor_binding(ctx, ROUTE)
            key = self.service.cursor_key(bound, cursor)
            if key is not None:
                if not isinstance(key, list) or len(key) != 1:
                    raise DomainError("INVALID_CURSOR", 400)
                try:
                    after = str(UUID(key[0]))
                except (TypeError, ValueError, AttributeError):
                    raise DomainError("INVALID_CURSOR", 400) from None
            predicate, args = visible_sql(ctx, READ_CAP)
            query = (
                "SELECT r.*,v.payload FROM impact.object_registry r "
                "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.object_id=r.object_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type=%s "
                "AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' AND " + predicate
            )
            params = [tenant, KIND, *args]
            if key is not None:
                query += " AND r.object_id>%s::uuid"
                params.append(after)
            query += " ORDER BY r.object_id LIMIT %s"
            params.append(limit + 1)
            rows = c.execute(query, params).fetchall()
            page = rows[:limit]
            return {
                "items": [_result(row) for row in page],
                "next_cursor": self.service.next_cursor(bound, [str(page[-1]["object_id"])])
                if len(rows) > limit
                else None,
            }

    def save(self, identity, tenant, body, correlation, object_id=None):
        _request(body, object_id is not None)
        if object_id is not None:
            _uuid(object_id)
        operation = "update_ai_adoption_plan" if object_id is not None else "create_ai_adoption_plan"
        # Catalogue updates never change the fingerprint of an already saved request.
        fingerprint = hash_data([operation, object_id, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, object_id, hidden=True)
            authorize(c, ctx, "get_ai_adoption_plan", object_id, hidden=True)
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
                load(c, ctx, old["outcome"]["object_id"], KIND, READ_CAP)
                authorize(c, ctx, operation, old["outcome"]["object_id"], hidden=True)
                return old["outcome"]
            previous = load(c, ctx, object_id, KIND, READ_CAP, lock=True) if object_id else None
            if previous and str(previous["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if previous and previous["lifecycle_state"] != "Draft":
                raise DomainError("STATE_TRANSITION_DENIED", 409)
            validate_plan(body["data"])
            if previous is None:
                count = c.execute(
                    "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s AND object_type=%s",
                    (tenant, KIND),
                ).fetchone()["n"]
                if count >= 1000:
                    raise DomainError("LIMIT_EXCEEDED", 429, reason="AI_ADOPTION_PLAN_LIMIT")
            payload = {
                **deepcopy(body["data"]),
                "content_versions": {"catalog": CATALOG_VERSION, "solutions": SOLUTIONS_VERSION},
            }
            receipt = write(c, ctx, KIND, payload, "Draft", previous=previous)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, operation, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    operation,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt
