"""Scoped proactive suggestions that remain unconfirmed until individual review."""

from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from . import ai_policy
from .ai_safety import require_available
from .domain import DomainError
from .service import revision
from .store import authorize, context, hash_data, load

USE_CASE = "PROACTIVE_FINDINGS"
PURPOSE = "PROACTIVE_FINDING_SUGGESTION"


class AIProactiveFindings:
    def __init__(self, service, destination, configuration):
        self.service = service
        self.destination = destination
        self.configuration = configuration

    def configure(self, identity, tenant, body):
        fingerprint = hash_data(["configure_ai_detection_task", body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "configure_ai_detection_task", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_detection_task WHERE tenant_id=%s AND created_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._task_view(replay)
            scope = revision(c, ctx, body["scope_revision_id"], "Programme", "programmes.read")
            if str(scope["object_id"]) != body["scope_object_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            head = load(c, ctx, body["scope_object_id"], "Programme", "programmes.read")
            if str(head["head_revision"]) != body["scope_revision_id"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="DETECTION_SCOPE_CHANGED")
            self._person(c, tenant, body["owner_principal_id"])
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                body["policy_version"],
                head["classification"],
                self.destination,
                body["language"],
                (),
                PURPOSE,
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            row = c.execute(
                "INSERT INTO impact.ai_detection_task VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp()) RETURNING *",
                (
                    tenant,
                    uuid4(),
                    body["task_code"],
                    UUID(body["scope_object_id"]),
                    UUID(body["scope_revision_id"]),
                    UUID(body["owner_principal_id"]),
                    body["cooldown_seconds"],
                    body["noise_limit"],
                    body["enabled"],
                    body["policy_version"],
                    ctx.principal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                ),
            ).fetchone()
            return self._task_view(row)

    def suggest(self, identity, tenant, body):
        fingerprint = hash_data(["create_ai_suggested_finding", body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_suggested_finding", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_suggested_finding WHERE tenant_id=%s AND created_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._suggestion_view(replay)
            task = c.execute(
                "SELECT * FROM impact.ai_detection_task WHERE tenant_id=%s AND task_id=%s FOR UPDATE",
                (tenant, body["task_id"]),
            ).fetchone()
            if not task or not task["enabled"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404, reason="DETECTION_TASK_NOT_ENABLED")
            scope = revision(c, ctx, task["scope_revision_id"], "Programme", "programmes.read")
            if str(scope["object_id"]) != str(task["scope_object_id"]):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            scope_head = load(c, ctx, task["scope_object_id"], "Programme", "programmes.read")
            if str(scope_head["head_revision"]) != str(task["scope_revision_id"]):
                raise DomainError("CONFLICT_VERSION", 409, reason="DETECTION_SCOPE_CHANGED")
            self._person(c, tenant, task["owner_principal_id"])
            latest = c.execute(
                "SELECT created_at FROM impact.ai_suggested_finding WHERE tenant_id=%s AND task_id=%s ORDER BY created_at DESC LIMIT 1",
                (tenant, task["task_id"]),
            ).fetchone()
            if (
                latest
                and c.execute(
                    "SELECT %s > statement_timestamp()-(%s * interval '1 second') AS active",
                    (latest["created_at"], task["cooldown_seconds"]),
                ).fetchone()["active"]
            ):
                raise DomainError("CONFLICT_OPERATION", 409, reason="DETECTION_COOLDOWN_ACTIVE")
            recent = c.execute(
                "SELECT count(*) AS n FROM impact.ai_suggested_finding WHERE tenant_id=%s AND task_id=%s AND created_at>statement_timestamp()-interval '24 hours'",
                (tenant, task["task_id"]),
            ).fetchone()["n"]
            if recent >= task["noise_limit"]:
                raise DomainError("CONFLICT_OPERATION", 409, reason="DETECTION_NOISE_LIMIT_REACHED")
            results = self._revisions(
                c, ctx, body["affected_results"], "CalculatedResult", "calculated-results.read"
            )
            evidence = self._revisions(c, ctx, body["evidence"], "Evidence", "evidence.read")
            policy = ai_policy.in_force(c, tenant)
            highest = max(
                [item["classification"] for item in results + evidence],
                key=["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"].index,
            )
            ai_policy.require(
                policy,
                USE_CASE,
                task["policy_version"],
                highest,
                self.destination,
                body["language"],
                (),
                PURPOSE,
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            row = c.execute(
                "INSERT INTO impact.ai_suggested_finding VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'SUGGESTED',%s,%s,%s,statement_timestamp()) RETURNING *",
                (
                    tenant,
                    uuid4(),
                    task["task_id"],
                    body["detection_event_key"],
                    Jsonb(body["affected_results"]),
                    Jsonb(body["evidence"]),
                    body["summary"],
                    body["limitation"],
                    body["proposed_follow_up"],
                    task["owner_principal_id"],
                    ctx.principal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                ),
            ).fetchone()
            for selector in body["affected_results"]:
                c.execute(
                    "INSERT INTO impact.ai_suggested_finding_result VALUES(%s,%s,%s,%s)",
                    (tenant, row["suggestion_id"], selector["object_id"], selector["revision_id"]),
                )
            for selector in body["evidence"]:
                c.execute(
                    "INSERT INTO impact.ai_suggested_finding_evidence VALUES(%s,%s,%s,%s)",
                    (tenant, row["suggestion_id"], selector["object_id"], selector["revision_id"]),
                )
            return self._suggestion_view(row)

    def review(self, identity, tenant, suggestion_id, body):
        fingerprint = hash_data(["review_ai_suggested_finding", str(suggestion_id), body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "review_ai_suggested_finding", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_finding_feedback WHERE tenant_id=%s AND reviewed_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint or str(replay["suggestion_id"]) != str(
                    suggestion_id
                ):
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._feedback_view(replay)
            if not c.execute(
                "SELECT 1 FROM impact.ai_suggested_finding WHERE tenant_id=%s AND suggestion_id=%s FOR UPDATE",
                (tenant, suggestion_id),
            ).fetchone():
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if c.execute(
                "SELECT 1 FROM impact.ai_finding_feedback WHERE tenant_id=%s AND suggestion_id=%s",
                (tenant, suggestion_id),
            ).fetchone():
                raise DomainError("CONFLICT_OPERATION", 409, reason="FINDING_ALREADY_REVIEWED")
            assigned = body["assigned_to"] if body["decision"] == "ASSIGNED" else None
            if assigned:
                self._person(c, tenant, assigned)
            row = c.execute(
                "INSERT INTO impact.ai_finding_feedback VALUES(%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp()) RETURNING *",
                (
                    tenant,
                    suggestion_id,
                    body["decision"],
                    body["reason"],
                    UUID(assigned) if assigned else None,
                    ctx.principal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                ),
            ).fetchone()
            return self._feedback_view(row)

    @staticmethod
    def _revisions(c, ctx, selectors, kind, capability):
        seen, rows = set(), []
        for selector in selectors:
            if selector["revision_id"] in seen:
                raise DomainError("VALIDATION_FAILED", reason="FINDING_SOURCE_DUPLICATED")
            seen.add(selector["revision_id"])
            row = revision(c, ctx, selector["revision_id"], kind, capability)
            if str(row["object_id"]) != selector["object_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            rows.append(row)
        return rows

    @staticmethod
    def _person(c, tenant, principal):
        if not c.execute(
            "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s AND principal_kind='HUMAN' AND active",
            (tenant, principal),
        ).fetchone():
            raise DomainError("VALIDATION_FAILED", reason="FINDING_OWNER_INVALID")

    @staticmethod
    def _task_view(row):
        return {
            key: (str(row[key]) if key.endswith("_id") else row[key])
            for key in (
                "task_id",
                "task_code",
                "scope_object_id",
                "scope_revision_id",
                "owner_principal_id",
                "cooldown_seconds",
                "noise_limit",
                "enabled",
                "policy_version",
            )
        }

    @staticmethod
    def _suggestion_view(row):
        return {
            "suggestion_id": str(row["suggestion_id"]),
            "task_id": str(row["task_id"]),
            "affected_results": row["affected_result_revisions"],
            "evidence": row["evidence_revisions"],
            "summary": row["summary"],
            "limitation": row["limitation"],
            "proposed_follow_up": row["proposed_follow_up"],
            "owner_principal_id": str(row["owner_principal_id"]),
            "status": "SUGGESTED",
            "confirmed_finding": False,
        }

    @staticmethod
    def _feedback_view(row):
        return {
            "suggestion_id": str(row["suggestion_id"]),
            "decision": row["decision"],
            "assigned_to": str(row["assigned_to"]) if row["assigned_to"] else None,
            "reason": row["reason"],
            "source_values_changed": False,
        }
