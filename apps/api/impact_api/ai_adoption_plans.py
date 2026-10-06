"""Tenant-shared adoption drafts using the platform's immutable revision and receipt model."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID

from psycopg.types.json import Jsonb

from . import ai_content_archives
from .ai_enablement_catalog import CONTENT_VERSION as CATALOG_VERSION
from .ai_enablement_catalog import validate_profile
from .ai_learning_content import LEGACY_LESSON_ALIASES, canonical_lesson_key, lesson_keys
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
    return lesson_keys()


def validate_plan(data):
    """Closed, bounded drafts; every selected solution and learning action is known."""
    if not isinstance(data, dict) or not PLAN_FIELDS <= set(data) or set(data) - PLAN_FIELDS - {"planning"}:
        _invalid()
    _text(data["title"], 150, required=True)
    try:
        validate_profile(data["profile"])
    except ValueError:
        _invalid("AI_PROFILE_INVALID")
    _ids(data["solution_ids"], SOLUTION_IDS, 4)
    keys = learning_keys()
    aliases = {alias for alias, key in LEGACY_LESSON_ALIASES.items() if key in keys}
    _ids(data["learning_completed"], keys | aliases, len(keys))
    canonical_completed = [canonical_lesson_key(key) for key in data["learning_completed"]]
    if len(canonical_completed) != len(set(canonical_completed)):
        _invalid()
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
    if "planning" in data:
        from .ai_procurement_costs import validate_comparison
        from .ai_pilot_outcomes import validate_pilot_outcomes
        from .ai_task_practice import validate_task_practice

        planning = data["planning"]
        if not isinstance(planning, dict) or set(planning) != {
            "cost_comparison",
            "pilot_evaluation",
            "task_practice",
        }:
            _invalid()
        for field, validator in (
            ("cost_comparison", validate_comparison),
            ("pilot_evaluation", validate_pilot_outcomes),
            ("task_practice", validate_task_practice),
        ):
            if planning[field] is not None:
                validator(planning[field])


def _request(body, update):
    expected = {"operation_id", "data"} | ({"expected_revision"} if update else set())
    if not isinstance(body, dict) or set(body) != expected or not isinstance(body["data"], dict):
        _invalid()
    _uuid(body["operation_id"])
    if update:
        _uuid(body["expected_revision"])


def _content_compatibility(payload, historical_snapshots_available=False):
    """Interpret progress for readers; never rewrite stored revisions or archive claims."""
    current = {"catalog": CATALOG_VERSION, "solutions": SOLUTIONS_VERSION}
    saved = payload.get("content_versions", {})

    def version_status(name):
        version = saved.get(name) if isinstance(saved, dict) else None
        if not isinstance(version, str) or not version:
            return "UNKNOWN"
        return "CURRENT" if version == current[name] else "STALE"

    completed, legacy, unavailable = [], [], []
    for key in payload["learning_completed"]:
        if key in LEGACY_LESSON_ALIASES:
            legacy.append(key)
        canonical = canonical_lesson_key(key)
        if canonical is None:
            unavailable.append(key)
        elif canonical not in completed:
            completed.append(canonical)
    return {
        "current_versions": current,
        "catalog_version_status": version_status("catalog"),
        "solutions_version_status": version_status("solutions"),
        "learning_completed": completed,
        "legacy_learning_keys": legacy,
        "unavailable_learning_keys": unavailable,
        "historical_snapshots_available": historical_snapshots_available,
    }


def _result(row):
    data = deepcopy(row["payload"])
    # Core selectors are private server metadata. Dedicated evidence reads recheck current
    # access to all linked objects; ordinary AI-plan readers cannot infer the private link.
    data.pop("impact_reference", None)
    return {
        "object_id": str(row["object_id"]),
        "revision_id": str(row["head_revision"]),
        "business_state": row["lifecycle_state"],
        "data": data,
        "content_compatibility": _content_compatibility(
            row["payload"], bool(row.get("historical_snapshots_available"))
        ),
    }


class AIAdoptionPlans:
    def __init__(self, service):
        self.service = service

    def get(self, identity, tenant, object_id):
        _uuid(object_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_adoption_plan", object_id, hidden=True)
            row = dict(load(c, ctx, object_id, KIND, READ_CAP))
            row["historical_snapshots_available"] = ai_content_archives.availability(
                c, tenant, object_id, row["head_revision"]
            )
            return _result(row)

    def guidance(self, identity, tenant, object_id, revision_id):
        _uuid(object_id)
        _uuid(revision_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_adoption_guidance", object_id, hidden=True)
            load(c, ctx, object_id, KIND, READ_CAP)
            row = c.execute(
                "SELECT payload FROM impact.object_revision WHERE tenant_id=%s "
                "AND object_id=%s AND revision_id=%s AND object_type=%s AND restriction_state='AVAILABLE'",
                (tenant, object_id, revision_id, KIND),
            ).fetchone()
            if not row:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            return ai_content_archives.result(c, tenant, object_id, revision_id, row["payload"])

    def history(self, identity, tenant, object_id, limit=50, cursor=None):
        _uuid(object_id)
        if type(limit) is not int or not 1 <= limit <= 100:
            _invalid()
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_adoption_revisions", object_id, hidden=True)
            load(c, ctx, object_id, KIND, READ_CAP)
            bound = self.service.cursor_binding(ctx, ROUTE + "/" + object_id + "/revisions")
            key = self.service.cursor_key(bound, cursor)
            if key is not None and (
                not isinstance(key, list) or len(key) != 1 or type(key[0]) is not int or key[0] < 1
            ):
                raise DomainError("INVALID_CURSOR", 400)
            query = (
                "SELECT v.revision_id,v.revision_number,v.created_at,v.payload->>'title' AS title,"
                "s.snapshot_id AS archive_id,s.payload AS archived_guidance,"
                "s.payload_sha256 AS archive_sha256,s.schema_version AS archive_schema_version "
                "FROM impact.object_revision v "
                "LEFT JOIN impact.ai_plan_content_binding b ON b.tenant_id=v.tenant_id "
                "AND b.object_id=v.object_id AND b.revision_id=v.revision_id "
                "LEFT JOIN impact.ai_content_snapshot s ON s.tenant_id=b.tenant_id AND s.snapshot_id=b.snapshot_id "
                "WHERE v.tenant_id=%s AND v.object_id=%s AND v.object_type=%s "
                "AND v.restriction_state='AVAILABLE'"
            )
            params = [tenant, object_id, KIND]
            if key is not None:
                query += " AND v.revision_number<%s"
                params.append(key[0])
            query += " ORDER BY v.revision_number DESC LIMIT %s"
            params.append(limit + 1)
            rows = c.execute(query, params).fetchall()
            page = rows[:limit]
            return {
                "object_id": object_id,
                "items": [
                    {
                        "revision_id": str(row["revision_id"]),
                        "revision_number": row["revision_number"],
                        "saved_at": row["created_at"].isoformat(),
                        "title": row["title"],
                        "historical_snapshots_available": ai_content_archives.joined_availability(row),
                    }
                    for row in page
                ],
                "next_cursor": self.service.next_cursor(bound, [page[-1]["revision_number"]])
                if len(rows) > limit
                else None,
            }

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
                "SELECT r.*,v.payload,s.snapshot_id AS archive_id,s.payload AS archived_guidance,"
                "s.payload_sha256 AS archive_sha256,s.schema_version AS archive_schema_version "
                "FROM impact.object_registry r "
                "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.object_id=r.object_id "
                "AND v.revision_id=r.head_revision "
                "LEFT JOIN impact.ai_plan_content_binding b ON b.tenant_id=r.tenant_id "
                "AND b.object_id=r.object_id AND b.revision_id=r.head_revision "
                "LEFT JOIN impact.ai_content_snapshot s ON s.tenant_id=b.tenant_id AND s.snapshot_id=b.snapshot_id "
                "WHERE r.tenant_id=%s AND r.object_type=%s "
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
            for row in page:
                row["historical_snapshots_available"] = ai_content_archives.joined_availability(row)
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
            if previous and "impact_reference" in previous["payload"]:
                # The closed client DTO cannot supply/clear/refresh this relationship. Keep
                # existing private pins exactly until the dedicated command changes them.
                payload["impact_reference"] = deepcopy(previous["payload"]["impact_reference"])
            retained_planning = bool(
                previous and "planning" not in body["data"] and "planning" in previous["payload"]
            )
            if retained_planning:
                # Older clients cannot erase optional snapshots they do not understand.
                # Explicitly supplied null members remain the supported clearing command.
                payload["planning"] = deepcopy(previous["payload"]["planning"])
            if payload.get("planning", {}).get("task_practice") is not None:
                from .ai_task_practice import CONTENT_VERSION as PRACTICE_VERSION

                if retained_planning:
                    retained_version = previous["payload"].get("content_versions", {}).get("practice")
                    if retained_version is not None:
                        payload["content_versions"]["practice"] = retained_version
                else:
                    payload["content_versions"]["practice"] = PRACTICE_VERSION
            # The receipt fingerprint binds the original request, including aliases.
            # Only a genuinely new save stores canonical progress identifiers.
            payload["learning_completed"] = [
                canonical_lesson_key(key) for key in body["data"]["learning_completed"]
            ]
            receipt = write(c, ctx, KIND, payload, "Draft", previous=previous)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            ai_content_archives.capture(c, ctx, receipt, payload, previous, retained_planning)
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
