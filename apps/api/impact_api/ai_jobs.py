"""Durable AI advisory job submission, budget reservation, status and cancellation."""

import hashlib
import hmac
import json
import re
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from . import ai_policy
from .ai_data_handling import prepare as prepare_transmission
from .ai_enablement import DRAFT_LANGUAGE, USE_CASE, _key
from .ai_enablement_contracts import MAX_POLICY_VERSION, TOOL_PATTERN
from .ai_evaluation_gate import require_exposure
from .domain import DomainError
from .store import authorize, context

JOB_CLASS = "AI_ADVISORY"
ESTIMATED_UNITS = 1
TERMINAL = {"Succeeded", "SucceededWithIssues", "Failed", "Cancelled"}
TOOL = re.compile(TOOL_PATTERN)


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _binding(tenant, job):
    return f"impact-ai-advisory-job-v1:{tenant}:{job}".encode()


def output_binding(tenant, job):
    return f"impact-ai-advisory-job-output-v1:{tenant}:{job}".encode()


class AIJobs:
    def __init__(self, service, enablement):
        self.service = service
        self.enablement = enablement

    def submit(self, identity, tenant, body):
        self._validate(body)
        operation = str(UUID(body["operation_id"]))
        fingerprint = hashlib.sha256(_json(body)).digest()
        tools = body.get("tools", [])
        sources = self._sources(body.get("source_dependencies", []))
        keys = self.enablement._keys()
        if not self.enablement._configured() or not keys:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_NOT_CONFIGURED")
        require_exposure(USE_CASE, self.enablement.provider.evaluation_configuration)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_advisory", hidden=True)
            existing = c.execute(
                "SELECT a.*,j.state,j.cancellation_requested_at FROM impact.ai_advisory_job a "
                "JOIN impact.job j ON j.tenant_id=a.tenant_id AND j.job_id=a.job_id "
                "WHERE a.tenant_id=%s AND a.requester_id=%s AND a.operation_id=%s",
                (tenant, ctx.principal_id, operation),
            ).fetchone()
            if existing:
                if not hmac.compare_digest(bytes(existing["request_fingerprint"]), fingerprint):
                    raise DomainError("CONFLICT_OPERATION", 409, reason="AI_OPERATION_CHANGED")
                return self._view(existing)
            policy = ai_policy.in_force(c, tenant)
            version = body["policy_version"]
            data_class = "CONFIDENTIAL" if body["profile"]["sensitive_data"] else "INTERNAL"
            rule = ai_policy.require(
                policy,
                USE_CASE,
                version,
                data_class,
                self.enablement.provider.destination,
                DRAFT_LANGUAGE,
                tools,
                body["purpose"],
            )
            prepare_transmission(body["profile"], self.enablement.provider.destination, body["purpose"])
            for source in sources:
                self.enablement._check_source(c, ctx, source)
            used = c.execute(
                "SELECT COALESCE(sum(CASE WHEN state='RESERVED' THEN estimated_units ELSE actual_units END),0) AS units "
                "FROM impact.ai_budget_reservation WHERE tenant_id=%s AND policy_version_id=%s",
                (tenant, policy["policy_version_id"]),
            ).fetchone()["units"]
            if used + ESTIMATED_UNITS > rule["budget_units"]:
                raise DomainError("LIMIT_EXCEEDED", 429, reason="AI_BUDGET_EXHAUSTED")
            scope = next(
                (grant["scope_id"] for grant in ctx.grants if grant["capability"] == "ai.advisory.request"),
                None,
            )
            if not scope:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            job = str(uuid4())
            sealed = keys.seal(_key, _json(body), _binding(tenant, job))
            manifest = {"use_case": USE_CASE, "estimated_units": ESTIMATED_UNITS, "input": "SEALED"}
            row = c.execute(
                "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest) "
                "VALUES(%s,%s,%s,%s,%s,'Queued',%s) RETURNING statement_timestamp() AS requested_at,state",
                (tenant, job, JOB_CLASS, ctx.principal_id, scope, Jsonb(manifest)),
            ).fetchone()
            c.execute(
                "INSERT INTO impact.ai_advisory_job VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL)",
                (
                    tenant,
                    job,
                    operation,
                    ctx.principal_id,
                    fingerprint,
                    sealed,
                    policy["policy_version_id"],
                    ESTIMATED_UNITS,
                    row["requested_at"],
                ),
            )
            c.execute(
                "INSERT INTO impact.ai_budget_reservation VALUES(%s,%s,%s,%s,NULL,'RESERVED',%s,NULL)",
                (tenant, job, policy["policy_version_id"], ESTIMATED_UNITS, row["requested_at"]),
            )
            return self._view(
                {
                    "job_id": job,
                    "operation_id": operation,
                    "state": row["state"],
                    "estimated_units": ESTIMATED_UNITS,
                    "requested_at": row["requested_at"],
                    "cancellation_requested_at": None,
                }
            )

    def status(self, identity, tenant, job):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_advisory_job", hidden=True)
            row = self._row(c, tenant, job, ctx.principal_id)
            return self._view(row)

    def cancel(self, identity, tenant, job):
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "cancel_ai_advisory_job", hidden=True)
            row = self._row(c, tenant, job, ctx.principal_id, lock=True)
            if row["state"] in TERMINAL:
                raise DomainError("CONFLICT_OPERATION", 409, reason="AI_JOB_ALREADY_FINISHED")
            at = c.execute("SELECT statement_timestamp() AS at").fetchone()["at"]
            c.execute(
                "UPDATE impact.job SET state='Cancelled',cancellation_requested_at=%s,output_manifest=%s "
                "WHERE tenant_id=%s AND job_id=%s AND state IN('Requested','Validating','Queued')",
                (at, Jsonb({"outcome": "CANCELLED", "complete": False}), tenant, job),
            )
            if c.rowcount:
                c.execute(
                    "UPDATE impact.ai_budget_reservation SET state='RELEASED',actual_units=0,settled_at=%s "
                    "WHERE tenant_id=%s AND job_id=%s AND state='RESERVED'",
                    (at, tenant, job),
                )
            else:
                c.execute(
                    "UPDATE impact.job SET cancellation_requested_at=COALESCE(cancellation_requested_at,%s) "
                    "WHERE tenant_id=%s AND job_id=%s",
                    (at, tenant, job),
                )
            return self._view(self._row(c, tenant, job, ctx.principal_id))

    @staticmethod
    def _row(c, tenant, job, principal, lock=False):
        row = c.execute(
            "SELECT a.*,j.state,j.cancellation_requested_at,j.output_manifest,o.outcome,o.complete,o.label "
            "FROM impact.ai_advisory_job a "
            "JOIN impact.job j ON j.tenant_id=a.tenant_id AND j.job_id=a.job_id "
            "LEFT JOIN impact.ai_advisory_job_output o ON o.tenant_id=a.tenant_id AND o.job_id=a.job_id "
            "WHERE a.tenant_id=%s AND a.job_id=%s AND a.requester_id=%s"
            + (" FOR UPDATE OF j" if lock else ""),
            (tenant, job, principal),
        ).fetchone()
        if not row:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return row

    @staticmethod
    def _view(row):
        return {
            "job_id": str(row["job_id"]),
            "operation_id": str(row["operation_id"]),
            "state": row["state"],
            "estimated_units": row["estimated_units"],
            "requested_at": row["requested_at"].isoformat(),
            "cancellation_requested": row.get("cancellation_requested_at") is not None,
            "progress": 100 if row["state"] in TERMINAL else 0,
            "can_cancel": row["state"] not in TERMINAL,
            "outcome": row.get("outcome"),
            "complete": row.get("complete"),
            "label": row.get("label"),
            "can_publish_final": row.get("complete") is True,
        }

    def _validate(self, body):
        if body.get("consent") is not True or body.get("purpose") != "AI_ADOPTION_ADVISORY":
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_CONSENT_REQUIRED")
        if (
            type(body.get("policy_version")) is not int
            or not 0 <= body["policy_version"] <= MAX_POLICY_VERSION
        ):
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_POLICY_VERSION_REQUIRED")
        self.enablement._validate(body.get("profile"))
        try:
            UUID(body["operation_id"])
        except (KeyError, ValueError, TypeError, AttributeError):
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_OPERATION_INVALID") from None
        tools = body.get("tools", [])
        if (
            not isinstance(tools, list)
            or len(tools) > 10
            or any(not isinstance(x, str) or not TOOL.fullmatch(x) for x in tools)
            or len(set(tools)) != len(tools)
        ):
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_TOOLS_INVALID")

    def _sources(self, sources):
        if not isinstance(sources, list) or len(sources) > 20:
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_SOURCES_INVALID")
        normalized = []
        for source in sources:
            if not isinstance(source, dict) or set(source) != {
                "object_id",
                "revision_id",
                "object_type",
                "capability",
            }:
                raise DomainError("VALIDATION_FAILED", 400, reason="AI_SOURCES_INVALID")
            try:
                normalized.append(
                    {
                        **source,
                        "object_id": str(UUID(source["object_id"])),
                        "revision_id": str(UUID(source["revision_id"])),
                    }
                )
            except (KeyError, ValueError, TypeError, AttributeError):
                raise DomainError("VALIDATION_FAILED", 400, reason="AI_SOURCES_INVALID") from None
            if not isinstance(source["object_type"], str) or not isinstance(source["capability"], str):
                raise DomainError("VALIDATION_FAILED", 400, reason="AI_SOURCES_INVALID")
        if len({(item["object_id"], item["revision_id"]) for item in normalized}) != len(normalized):
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_SOURCES_INVALID")
        return normalized
