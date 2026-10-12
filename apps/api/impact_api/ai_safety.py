"""Payload-minimal AI safety feedback and append-only scoped shutdowns."""

import re
from uuid import UUID, uuid4

from .domain import DomainError
from .store import authorize, context, load

SENSITIVE = re.compile(
    r"(?i)(?:bearer\s+[a-z0-9._~-]+|(?:api[_ -]?key|password|secret)\s*[:=]|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|\+?\d[\d ()-]{7,}\d)"
)
CONFIGURATION = re.compile(r"^[0-9a-f]{64}$")
USE_CASES = {
    "ADVISORY_DRAFT",
    "EXTRACTION",
    "REPORT_DRAFT",
    "CHAT",
    "INDICATOR_DESIGN",
    "IMPORT_CLEANING",
    "EVIDENCE_QUESTION",
}
DESTINATIONS = {"openai-us"}


def configuration_id(configuration):
    import hashlib
    import json

    return hashlib.sha256(
        json.dumps(configuration, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def require_available(c, tenant, use_case, destination, configuration):
    selectors = [
        ("USE_CASE", use_case),
        ("DESTINATION", destination),
        ("CONFIGURATION", configuration_id(configuration)),
    ]
    for kind, value in selectors:
        latest = c.execute(
            "SELECT action FROM impact.ai_shutdown_event WHERE tenant_id=%s AND scope_kind=%s "
            "AND scope_value=%s ORDER BY sequence DESC LIMIT 1",
            (tenant, kind, value),
        ).fetchone()
        if latest and latest["action"] == "DISABLE":
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_SAFETY_SHUTDOWN")


class AISafety:
    def __init__(self, service):
        self.service = service

    def feedback(self, identity, tenant, body):
        detail = body["safe_detail"].strip()
        if SENSITIVE.search(detail):
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_FEEDBACK_DETAIL_PROHIBITED")
        output = str(UUID(body["output_id"]))
        reviewer = str(UUID(body["reviewer_id"]))
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_safety_feedback", hidden=True)
            if reviewer == str(ctx.principal_id):
                raise DomainError(
                    "VALIDATION_FAILED", 400, reason="AI_FEEDBACK_REVIEWER_INDEPENDENCE_REQUIRED"
                )
            output_query = {
                "ADVISORY": "SELECT 1 FROM impact.ai_advisory_result o JOIN impact.ai_advisory_request r ON r.tenant_id=o.tenant_id AND r.request_id=o.request_id WHERE o.tenant_id=%s AND o.request_id=%s AND r.principal_id=%s",
                "ADVISORY_JOB": "SELECT 1 FROM impact.ai_advisory_job_output o JOIN impact.ai_advisory_job j ON j.tenant_id=o.tenant_id AND j.job_id=o.job_id WHERE o.tenant_id=%s AND o.job_id=%s AND j.requester_id=%s",
                "FORECAST": "SELECT 1 FROM impact.ai_forecast_scenario WHERE tenant_id=%s AND scenario_id=%s AND requester_id=%s",
            }[body["output_kind"]]
            if not c.execute(output_query, (tenant, output, ctx.principal_id)).fetchone():
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            person = c.execute(
                "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s "
                "AND principal_kind='HUMAN' AND active",
                (tenant, reviewer),
            ).fetchone()
            if not person:
                raise DomainError("VALIDATION_FAILED", 400, reason="AI_FEEDBACK_REVIEWER_INVALID")
            row = c.execute(
                "INSERT INTO impact.ai_safety_feedback VALUES(%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp()) RETURNING *",
                (
                    tenant,
                    str(uuid4()),
                    body["output_kind"],
                    output,
                    body["category"],
                    detail,
                    ctx.principal_id,
                    reviewer,
                ),
            ).fetchone()
            return {
                "feedback_id": str(row["feedback_id"]),
                "output_kind": row["output_kind"],
                "output_id": str(row["output_id"]),
                "category": row["category"],
                "reviewer_id": str(row["reviewer_id"]),
                "submitted_at": row["submitted_at"].isoformat(),
                "source_payload_retained": False,
            }

    def change(self, identity, tenant, body):
        if (
            (body["scope_kind"] == "USE_CASE" and body["scope_value"] not in USE_CASES)
            or (body["scope_kind"] == "DESTINATION" and body["scope_value"] not in DESTINATIONS)
            or (body["scope_kind"] == "CONFIGURATION" and not CONFIGURATION.fullmatch(body["scope_value"]))
        ):
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_SHUTDOWN_SCOPE_INVALID")
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "manage_ai_safety_shutdown", hidden=True)
            action = body["action"]
            evidence_object = evidence_revision = approver = None
            if action == "REENABLE":
                if not body.get("disabled_event_id"):
                    raise DomainError("CONFLICT_OPERATION", 409, reason="AI_REENABLE_EVIDENCE_REQUIRED")
                approval = c.execute(
                    "SELECT a.*,e.scope_kind,e.scope_value FROM impact.ai_shutdown_recovery_approval a "
                    "JOIN impact.ai_shutdown_event e ON e.tenant_id=a.tenant_id AND e.event_id=a.shutdown_event_id "
                    "WHERE a.tenant_id=%s AND a.shutdown_event_id=%s",
                    (tenant, str(UUID(body["disabled_event_id"]))),
                ).fetchone()
                if (
                    not approval
                    or approval["scope_kind"] != body["scope_kind"]
                    or approval["scope_value"] != body["scope_value"]
                ):
                    raise DomainError("CONFLICT_OPERATION", 409, reason="AI_REENABLE_APPROVAL_INVALID")
                evidence_object = str(approval["fix_evidence_object_id"])
                evidence_revision = str(approval["fix_evidence_revision_id"])
                approver = str(approval["approved_by"])
                load(c, ctx, evidence_object, "Evidence", "evidence.read")
            latest = c.execute(
                "SELECT event_id,action FROM impact.ai_shutdown_event WHERE tenant_id=%s AND scope_kind=%s "
                "AND scope_value=%s ORDER BY sequence DESC LIMIT 1",
                (tenant, body["scope_kind"], body["scope_value"]),
            ).fetchone()
            if action == "REENABLE" and (not latest or latest["action"] != "DISABLE"):
                raise DomainError("CONFLICT_OPERATION", 409, reason="AI_SHUTDOWN_NOT_DISABLED")
            if action == "REENABLE" and str(latest["event_id"]) != str(UUID(body["disabled_event_id"])):
                raise DomainError("CONFLICT_OPERATION", 409, reason="AI_REENABLE_APPROVAL_STALE")
            if latest and latest["action"] == action:
                raise DomainError("CONFLICT_OPERATION", 409, reason="AI_SHUTDOWN_STATE_UNCHANGED")
            row = c.execute(
                "INSERT INTO impact.ai_shutdown_event(tenant_id,event_id,scope_kind,scope_value,action,reason_category,"
                "fix_evidence_object_id,fix_evidence_revision_id,regression_approved_by,actor_id,occurred_at) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp()) RETURNING *",
                (
                    tenant,
                    str(uuid4()),
                    body["scope_kind"],
                    body["scope_value"],
                    action,
                    "FIX_VERIFIED" if action == "REENABLE" else body["reason_category"],
                    evidence_object,
                    evidence_revision,
                    approver,
                    ctx.principal_id,
                ),
            ).fetchone()
            queued, running = [], []
            if action == "DISABLE":
                affected = c.execute(
                    "SELECT j.job_id,j.state FROM impact.job j WHERE j.tenant_id=%s AND j.job_class='AI_ADVISORY' "
                    "AND j.state IN('Queued','Running') AND CASE %s WHEN 'USE_CASE' THEN j.input_manifest->>'use_case'=%s "
                    "WHEN 'DESTINATION' THEN j.input_manifest->>'destination'=%s WHEN 'CONFIGURATION' THEN "
                    "j.input_manifest->>'configuration_id'=%s ELSE false END FOR UPDATE",
                    (
                        tenant,
                        body["scope_kind"],
                        body["scope_value"],
                        body["scope_value"],
                        body["scope_value"],
                    ),
                ).fetchall()
                queued = [str(item["job_id"]) for item in affected if item["state"] == "Queued"]
                running = [str(item["job_id"]) for item in affected if item["state"] == "Running"]
                if queued:
                    c.execute(
                        "UPDATE impact.job SET state='Cancelled',cancellation_requested_at=statement_timestamp(),"
                        "output_manifest=%s WHERE tenant_id=%s AND job_id=ANY(%s::uuid[]) AND state='Queued'",
                        ('{"outcome":"CANCELLED","reason":"AI_SAFETY_SHUTDOWN"}', tenant, queued),
                    )
                    c.execute(
                        "UPDATE impact.ai_budget_reservation SET state='RELEASED',actual_units=0,settled_at=statement_timestamp() "
                        "WHERE tenant_id=%s AND job_id=ANY(%s::uuid[]) AND state='RESERVED'",
                        (tenant, queued),
                    )
                if running:
                    c.execute(
                        "UPDATE impact.job SET cancellation_requested_at=COALESCE(cancellation_requested_at,statement_timestamp()) "
                        "WHERE tenant_id=%s AND job_id=ANY(%s::uuid[]) AND state='Running'",
                        (tenant, running),
                    )
            artifacts = self._artifacts(c, tenant, body["scope_kind"], body["scope_value"])
            return {
                "event_id": str(row["event_id"]),
                "scope_kind": row["scope_kind"],
                "scope_value": row["scope_value"],
                "state": "DISABLED" if action == "DISABLE" else "ENABLED",
                "queued_jobs_stopped": queued,
                "running_jobs_cancellation_requested": running,
                "affected_artifacts": artifacts,
                "manual_workflows_enabled": True,
                "source_payload_retained": False,
                "occurred_at": row["occurred_at"].isoformat(),
            }

    def approve_recovery(self, identity, tenant, event, body):
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "approve_ai_safety_recovery", hidden=True)
            disabled = c.execute(
                "SELECT * FROM impact.ai_shutdown_event WHERE tenant_id=%s AND event_id=%s AND action='DISABLE'",
                (tenant, event),
            ).fetchone()
            if not disabled or str(disabled["actor_id"]) == str(ctx.principal_id):
                raise DomainError("CONFLICT_OPERATION", 409, reason="AI_RECOVERY_INDEPENDENCE_REQUIRED")
            latest = c.execute(
                "SELECT event_id,action FROM impact.ai_shutdown_event WHERE tenant_id=%s AND scope_kind=%s "
                "AND scope_value=%s ORDER BY sequence DESC LIMIT 1",
                (tenant, disabled["scope_kind"], disabled["scope_value"]),
            ).fetchone()
            if not latest or str(latest["event_id"]) != str(event) or latest["action"] != "DISABLE":
                raise DomainError("CONFLICT_OPERATION", 409, reason="AI_SHUTDOWN_NOT_DISABLED")
            evidence_object = str(UUID(body["fix_evidence_object_id"]))
            evidence_revision = str(UUID(body["fix_evidence_revision_id"]))
            load(c, ctx, evidence_object, "Evidence", "evidence.read")
            exact = c.execute(
                "SELECT 1 FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_id=%s "
                "AND object_type='Evidence' AND restriction_state='AVAILABLE'",
                (tenant, evidence_object, evidence_revision),
            ).fetchone()
            if not exact:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            c.execute(
                "INSERT INTO impact.ai_shutdown_recovery_approval VALUES(%s,%s,%s,%s,%s,statement_timestamp())",
                (tenant, event, evidence_object, evidence_revision, ctx.principal_id),
            )
            return {
                "shutdown_event_id": str(event),
                "fix_evidence_object_id": evidence_object,
                "fix_evidence_revision_id": evidence_revision,
                "approved_by": str(ctx.principal_id),
                "state": "REGRESSION_APPROVED",
            }

    def status(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_safety_shutdowns", hidden=True)
            active = c.execute(
                "SELECT DISTINCT ON(scope_kind,scope_value) scope_kind,scope_value,action,occurred_at "
                "FROM impact.ai_shutdown_event WHERE tenant_id=%s ORDER BY scope_kind,scope_value,sequence DESC",
                (tenant,),
            ).fetchall()
            return {
                "shutdowns": [
                    {
                        "scope_kind": row["scope_kind"],
                        "scope_value": row["scope_value"],
                        "state": "DISABLED" if row["action"] == "DISABLE" else "ENABLED",
                        "occurred_at": row["occurred_at"].isoformat(),
                    }
                    for row in active
                ],
                "affected_artifacts": self._artifacts(c, tenant),
                "manual_workflows_enabled": True,
            }

    @staticmethod
    def _artifacts(c, tenant, scope_kind=None, scope_value=None):
        rows = []
        sources = [
            ("ADVISORY", "ai_advisory_result", "request_id"),
            ("ADVISORY_JOB", "ai_advisory_job_output", "job_id"),
        ]
        if scope_kind is None:
            sources.append(("FORECAST", "ai_forecast_scenario", "scenario_id"))
        if scope_kind == "USE_CASE" and scope_value != "ADVISORY_DRAFT":
            sources = []
        for kind, table, column in sources:
            for row in c.execute(
                f"SELECT DISTINCT {column} AS id FROM impact.{table} WHERE tenant_id=%s ORDER BY {column}",
                (tenant,),
            ).fetchall():
                rows.append({"output_kind": kind, "output_id": str(row["id"])})
        return rows
