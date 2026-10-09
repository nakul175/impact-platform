"""Tenant-authorised planning and AI drafts with bounded attempts and sealed replay."""

from datetime import datetime, timezone
import hashlib
import hmac
import json
import logging
import re
from uuid import UUID

from cryptography.exceptions import InvalidTag
import psycopg

from . import ai_policy
from .ai_enablement_contracts import MAX_POLICY_VERSION, TOOL_PATTERN
from .ai_enablement_catalog import assess, catalog, validate_profile
from .ai_solutions_catalog import solutions_catalog
from .domain import DomainError
from .keyring import ring
from .store import audit, authorize, context, write

DISCLAIMER = "AI advisory draft: staff must verify claims and approve decisions. This does not authorise spending, data disclosure or official impact calculations."
USE_CASE = "ADVISORY_DRAFT"
# The advisory instructions and the workspace are English; the policy must cover this language.
DRAFT_LANGUAGE = "en"
REQUEST_FIELDS = {"operation_id", "profile", "consent", "policy_version"}
TOOL = re.compile(TOOL_PATTERN)
LOG = logging.getLogger("impact")


def _key(secret):
    return hmac.new(secret.encode(), b"impact-ai-advisory-sealing-v1", hashlib.sha256).digest()


def _binding(tenant, request):
    return f"impact-ai-advisory-v1:{tenant}:{request}".encode()


def _json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _error(reason, status=503):
    return DomainError(
        "SERVICE_UNAVAILABLE" if status == 503 else "CONFLICT_OPERATION", status, reason=reason
    )


class AIEnablement:
    def __init__(self, service, provider, enabled=False):
        self.service, self.provider, self.enabled = service, provider, enabled

    def _keys(self):
        return ring(self.service.s, "delivery")

    def _available(self):
        return bool(self.enabled and self.provider and self.provider.configured and self._keys())

    def server_ready(self):
        """The server switch: AI enabled, a configured provider and sealing keys (no tenant policy)."""
        return self._available()

    def _authority(self, c, identity, tenant, operation, write_access=False):
        ctx = context(c, identity, tenant, write=write_access)
        authorize(c, ctx, "get_ai_enablement_catalog", hidden=True)
        if operation != "get_ai_enablement_catalog":
            authorize(c, ctx, operation, hidden=True)
        return ctx

    def catalog(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "get_ai_enablement_catalog")
            # Server switch, tenant policy and use case must all be on (FR-AI-001). The editorial guide
            # never depends on the policy: an unreadable policy only reports advisory as unavailable
            # (the advisory request itself still fails closed on its own read).
            available = False
            if self._available():
                try:
                    with c.transaction():
                        available = ai_policy.enabled(ai_policy.in_force(c, tenant), USE_CASE)
                except psycopg.Error as error:
                    LOG.warning("AI policy unreadable for the catalogue sqlstate=%s", error.sqlstate)
            return {**catalog(), "advisory_available": available}

    def assessment(self, identity, tenant, profile):
        self._validate(profile)
        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "assess_ai_enablement")
            return {"assessment": assess(profile)}

    def solutions(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "get_ai_solutions")
            return solutions_catalog()

    def cost_comparison(self, identity, tenant, body):
        from .ai_procurement_costs import compare_costs

        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "compare_ai_procurement_costs")
            return compare_costs(body)

    def pilot_evaluation(self, identity, tenant, body):
        from .ai_pilot_outcomes import evaluate_pilot_outcomes

        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "evaluate_ai_pilot")
            return evaluate_pilot_outcomes(body)

    def task_templates(self, identity, tenant):
        from .ai_task_practice import task_templates

        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "get_ai_task_templates")
            return task_templates()

    @staticmethod
    def _validate(profile):
        try:
            validate_profile(profile)
        except ValueError:
            raise DomainError("VALIDATION_FAILED", reason="AI_PROFILE_INVALID") from None

    def advisory(self, identity, tenant, body, correlation):
        if (
            not isinstance(body, dict)
            or not REQUEST_FIELDS - {"policy_version"} <= set(body)
            or set(body) - REQUEST_FIELDS - {"tools"}
            or body["consent"] is not True
        ):
            raise DomainError("VALIDATION_FAILED", reason="AI_CONSENT_REQUIRED")
        version = body.get("policy_version")
        if type(version) is not int or not 0 <= version <= MAX_POLICY_VERSION:
            raise DomainError("VALIDATION_FAILED", reason="AI_POLICY_VERSION_REQUIRED")
        tools = body.get("tools", [])
        if (
            not isinstance(tools, list)
            or len(tools) > 10
            or any(not isinstance(tool, str) or not TOOL.fullmatch(tool) for tool in tools)
            or len(set(tools)) != len(tools)
        ):
            raise DomainError("VALIDATION_FAILED", reason="AI_TOOLS_INVALID")
        self._validate(body["profile"])
        try:
            request = str(UUID(body["operation_id"]))
        except (ValueError, TypeError, AttributeError):
            raise DomainError("VALIDATION_FAILED", reason="AI_OPERATION_INVALID") from None
        # Bind replay to the submitted body, independent of later catalogue updates.
        # The claimed metadata and sealed outcome retain their original content version.
        assessment = assess(body["profile"])
        fingerprint = hashlib.sha256(_json(body)).digest()
        keys = self._keys()
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = self._authority(c, identity, tenant, "create_ai_advisory", True)
            existing = c.execute(
                "SELECT * FROM impact.ai_advisory_request WHERE tenant_id=%s AND request_id=%s",
                (tenant, request),
            ).fetchone()
            if existing:
                if str(existing["principal_id"]) != str(ctx.principal_id) or not hmac.compare_digest(
                    bytes(existing["fingerprint"]), fingerprint
                ):
                    raise _error("AI_OPERATION_CHANGED", 409)
                result = c.execute(
                    "SELECT * FROM impact.ai_advisory_result WHERE tenant_id=%s AND request_id=%s",
                    (tenant, request),
                ).fetchone()
                if not result:
                    raise _error("AI_REQUEST_IN_FLIGHT", 409)
                if result["failure_reason"]:
                    raise _error(result["failure_reason"])
                try:
                    return json.loads(keys.unseal(_key, result["sealed_output"], _binding(tenant, request)))
                except (InvalidTag, ValueError, TypeError):
                    raise _error("AI_RESULT_UNREADABLE") from None
            if not self._available():
                raise _error("AI_NOT_CONFIGURED")
            # FR-AI-001: the tenant policy in force is read under the tenant lock and checked before
            # any reservation or provider call. An unreadable policy fails the transaction (closed).
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                version,
                "CONFIDENTIAL" if body["profile"]["sensitive_data"] else "INTERNAL",
                getattr(self.provider, "destination", None),
                DRAFT_LANGUAGE,
                tools,
            )
            count = c.execute(
                "SELECT count(*) AS n FROM impact.ai_advisory_request WHERE tenant_id=%s AND reserved_at > statement_timestamp()-interval '24 hours'",
                (tenant,),
            ).fetchone()["n"]
            if count >= 3:
                raise DomainError("LIMIT_EXCEEDED", 429, reason="AI_DAILY_LIMIT")
            receipt = write(
                c,
                ctx,
                "AIAdvisoryRequest",
                {
                    "content_version": assessment["content_version"],
                    "status": "RESERVED",
                    "use_case": USE_CASE,
                    "policy_version": policy["version"],
                },
                "Recorded",
            )
            # The reservation records the exact policy version that allowed it (migration 0041).
            c.execute(
                "INSERT INTO impact.ai_advisory_request(tenant_id,request_id,object_id,principal_id,fingerprint,reserved_at,policy_version_id) VALUES(%s,%s,%s,%s,%s,statement_timestamp(),%s)",
                (
                    tenant,
                    request,
                    receipt["object_id"],
                    ctx.principal_id,
                    fingerprint,
                    policy["policy_version_id"],
                ),
            )
            audit(c, ctx, "create_ai_advisory", receipt, correlation)
        # The claim has committed. Never call the provider while holding a database transaction.
        output, failure = None, None
        try:
            generated = self.provider.generate(body["profile"], assessment)
            if (
                not isinstance(generated, dict)
                or not isinstance(generated.get("text"), str)
                or not generated["text"].strip()
                or len(generated["text"]) > 12000
                or not isinstance(generated.get("model"), str)
                or not generated["model"]
                or len(generated["model"]) > 200
            ):
                raise ValueError("Invalid provider draft")
            output = {
                "status": "DRAFT",
                "text": generated["text"],
                "assessment": assessment,
                "model": generated["model"],
                "disclaimer": DISCLAIMER,
            }
        except Exception:
            # No provider exception, response body, prompt or credential is persisted or exposed.
            failure = "AI_PROVIDER_UNAVAILABLE"
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = self._authority(c, identity, tenant, "create_ai_advisory", True)
            metadata = c.execute(
                "SELECT r.object_id,o.head_revision AS revision_id,o.lifecycle_state AS business_state "
                "FROM impact.ai_advisory_request r JOIN impact.object_registry o "
                "ON o.tenant_id=r.tenant_id AND o.object_id=r.object_id "
                "WHERE r.tenant_id=%s AND r.request_id=%s",
                (tenant, request),
            ).fetchone()
            if not metadata:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            sealed = keys.seal(_key, _json(output), _binding(tenant, request)) if output else None
            c.execute(
                "INSERT INTO impact.ai_advisory_result(tenant_id,request_id,sealed_output,failure_reason,completed_at) VALUES(%s,%s,%s,%s,statement_timestamp())",
                (tenant, request, sealed, failure),
            )
            audit(
                c,
                ctx,
                "ai_advisory_failed" if failure else "ai_advisory_completed",
                {
                    **metadata,
                    "object_id": str(metadata["object_id"]),
                    "revision_id": str(metadata["revision_id"]),
                    "saved_at": datetime.now(timezone.utc).isoformat(),
                },
                correlation,
            )
        if failure:
            raise _error(failure)
        return output
