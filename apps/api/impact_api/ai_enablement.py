"""Tenant-authorised planning and AI drafts with bounded attempts and sealed replay."""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import logging
import re
from uuid import UUID

from cryptography.exceptions import InvalidTag
import psycopg

from . import ai_policy
from .ai_data_handling import prepare as prepare_transmission
from .ai_execution_boundary import runtime_tools, untrusted_envelope
from .ai_evaluation_gate import require_exposure
from .ai_safety import require_available as require_safety_available
from .ai_enablement_contracts import MAX_POLICY_VERSION, TOOL_PATTERN
from .ai_enablement_catalog import assess, catalog, validate_profile
from .ai_solutions_catalog import (
    SolutionsCatalogInvalid,
    public_disclosures,
    solutions_catalog,
    vetting_publication,
)
from .domain import DomainError
from .keyring import ring
from .store import audit, authorize, context, load, write

DISCLAIMER = "AI advisory draft: staff must verify claims and approve decisions. This does not authorise spending, data disclosure or official impact calculations."
USE_CASE = "ADVISORY_DRAFT"
# The advisory instructions and the workspace are English; the policy must cover this language.
DRAFT_LANGUAGE = "en"
REQUEST_FIELDS = {"operation_id", "profile", "consent", "policy_version", "purpose"}
TOOL = re.compile(TOOL_PATTERN)
OBJECT_TYPE = re.compile(r"^[A-Z][A-Za-z0-9]{0,99}$")
CAPABILITY = re.compile(r"^[a-z][a-z0-9.-]{0,99}$")
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

    def _configured(self):
        return bool(self.enabled and self.provider and self.provider.configured and self._keys())

    def _available(self):
        if not self._configured():
            return False
        try:
            require_exposure(USE_CASE, self.provider.evaluation_configuration)
        except DomainError:
            return False
        return True

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
            try:
                return {"assessment": assess(profile)}
            except ValueError:
                raise DomainError(
                    "SERVICE_UNAVAILABLE", 503, reason="AI_MATURITY_FRAMEWORK_INVALID"
                ) from None

    def solutions(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "get_ai_solutions")
            try:
                return solutions_catalog()
            except SolutionsCatalogInvalid as error:
                # Fail closed (US-DC-04): a listing without a valid commercial disclosure means the
                # catalogue is not served at all, never served with that listing unlabelled.
                LOG.error("AI solutions catalogue refused: %s", error)
                raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_SOLUTIONS_CATALOG_INVALID") from None

    @staticmethod
    def public_vetting():
        try:
            return vetting_publication()
        except SolutionsCatalogInvalid:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_VETTING_PUBLICATION_INVALID") from None

    @staticmethod
    def public_disclosures():
        try:
            return public_disclosures()
        except SolutionsCatalogInvalid:
            raise DomainError(
                "SERVICE_UNAVAILABLE", 503, reason="AI_DISCLOSURE_PUBLICATION_INVALID"
            ) from None

    def solution_shortlist(self, identity, tenant, opportunity_id, expanded=False):
        if (
            not isinstance(opportunity_id, str)
            or not opportunity_id.strip()
            or len(opportunity_id) > 120
            or type(expanded) is not bool
        ):
            raise DomainError("VALIDATION_FAILED", 400, reason="AI_SHORTLIST_INVALID")
        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "get_ai_solution_shortlist")
            try:
                catalog = solutions_catalog()
            except SolutionsCatalogInvalid as error:
                LOG.error("AI solutions shortlist refused: %s", error)
                raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_SOLUTIONS_CATALOG_INVALID") from None
            matches = [item for item in catalog["solutions"] if opportunity_id in item["use_case_ids"]]
            shown = matches if expanded else matches[:3]
            return {
                "content_version": catalog["content_version"],
                "opportunity_id": opportunity_id,
                "expanded": expanded,
                "default_limit": 3,
                "total_vetted": len(matches),
                "items": [
                    {
                        "solution": item,
                        "vetting_basis": "SOURCE_BACKED_EDITORIAL_EDITION",
                        "opportunity_id": opportunity_id,
                    }
                    for item in shown
                ],
            }

    def cost_comparison(self, identity, tenant, body):
        from .ai_procurement_costs import compare_costs

        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "compare_ai_procurement_costs")
            return compare_costs(body)

    def value_case(self, identity, tenant, body):
        from .ai_value_case import calculate_value_case

        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "calculate_ai_value_case")
            return calculate_value_case(body)

    def value_case_export(self, identity, tenant, body):
        from .ai_value_case_export import export_value_case

        with self.service.db.transaction(tenant) as c:
            self._authority(c, identity, tenant, "export_ai_value_case")
            return export_value_case(body)

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
            or set(body) - REQUEST_FIELDS - {"tools", "source_dependencies"}
            or body["consent"] is not True
        ):
            raise DomainError("VALIDATION_FAILED", reason="AI_CONSENT_REQUIRED")
        version = body.get("policy_version")
        if type(version) is not int or not 0 <= version <= MAX_POLICY_VERSION:
            raise DomainError("VALIDATION_FAILED", reason="AI_POLICY_VERSION_REQUIRED")
        tools = body.get("tools", [])
        sources = body.get("source_dependencies", [])
        if (
            not isinstance(tools, list)
            or len(tools) > 10
            or any(not isinstance(tool, str) or not TOOL.fullmatch(tool) for tool in tools)
            or len(set(tools)) != len(tools)
        ):
            raise DomainError("VALIDATION_FAILED", reason="AI_TOOLS_INVALID")
        if not isinstance(sources, list) or len(sources) > 20:
            raise DomainError("VALIDATION_FAILED", reason="AI_SOURCES_INVALID")
        normalized_sources = []
        for source in sources:
            if (
                not isinstance(source, dict)
                or set(source) != {"object_id", "revision_id", "object_type", "capability"}
                or not isinstance(source["object_type"], str)
                or not OBJECT_TYPE.fullmatch(source["object_type"])
                or not isinstance(source["capability"], str)
                or not CAPABILITY.fullmatch(source["capability"])
            ):
                raise DomainError("VALIDATION_FAILED", reason="AI_SOURCES_INVALID")
            try:
                item = {
                    **source,
                    "object_id": str(UUID(source["object_id"])),
                    "revision_id": str(UUID(source["revision_id"])),
                }
            except (ValueError, TypeError, AttributeError):
                raise DomainError("VALIDATION_FAILED", reason="AI_SOURCES_INVALID") from None
            normalized_sources.append(item)
        if len({(x["object_id"], x["revision_id"]) for x in normalized_sources}) != len(normalized_sources):
            raise DomainError("VALIDATION_FAILED", reason="AI_SOURCES_INVALID")
        self._validate(body["profile"])
        try:
            request = str(UUID(body["operation_id"]))
        except (ValueError, TypeError, AttributeError):
            raise DomainError("VALIDATION_FAILED", reason="AI_OPERATION_INVALID") from None
        # Bind replay to the submitted body, independent of later catalogue updates.
        # The claimed metadata and sealed outcome retain their original content version.
        try:
            assessment = assess(body["profile"])
        except ValueError:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_MATURITY_FRAMEWORK_INVALID") from None
        _, embedded_attempts = untrusted_envelope(organization_brief=body["profile"], assessment=assessment)
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
                self._source_access(c, ctx, tenant, request)
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
            if not self._configured():
                raise _error("AI_NOT_CONFIGURED")
            require_exposure(USE_CASE, self.provider.evaluation_configuration)
            for source in normalized_sources:
                self._check_source(c, ctx, source)
            # FR-AI-001: the tenant policy in force is read under the tenant lock and checked before
            # any reservation or provider call. An unreadable policy fails the transaction (closed).
            policy = ai_policy.in_force(c, tenant)
            rule = ai_policy.require(
                policy,
                USE_CASE,
                version,
                "CONFIDENTIAL" if body["profile"]["sensitive_data"] else "INTERNAL",
                getattr(self.provider, "destination", None),
                DRAFT_LANGUAGE,
                tools,
                body["purpose"],
            )
            require_safety_available(
                c, tenant, USE_CASE, self.provider.destination, self.provider.evaluation_configuration
            )
            minimized_profile, handling = prepare_transmission(
                body["profile"], getattr(self.provider, "destination", None), body["purpose"]
            )
            requester = str(ctx.principal_id)
            policy_trace = {
                "policy_version": policy["version"],
                "policy_version_id": policy["policy_version_id"],
                "use_case": USE_CASE,
                "purpose": body["purpose"],
                "data_classes": rule["data_classes"],
                "destinations": rule["destinations"],
                "review_mode": rule["review_mode"],
                "tools": tools,
            }
            # Policy permission never creates a runtime tool. This advisory runtime deliberately
            # exposes an empty server-owned catalogue, so document/model text cannot execute one.
            runtime_tools({}, tools)
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
                    "data_handling": handling,
                    "source_dependencies": normalized_sources,
                    "permitted_audience": [str(ctx.principal_id)],
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
            for ordinal, source in enumerate(normalized_sources, 1):
                c.execute(
                    "INSERT INTO impact.ai_advisory_source VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (
                        tenant,
                        request,
                        ordinal,
                        source["object_id"],
                        source["revision_id"],
                        source["object_type"],
                        source["capability"],
                    ),
                )
            audit(c, ctx, "create_ai_advisory", receipt, correlation)
            if embedded_attempts:
                audit(
                    c,
                    ctx,
                    "ai_untrusted_instruction_observed",
                    {
                        "object_id": receipt["object_id"],
                        "revision_id": receipt["revision_id"],
                        "categories": embedded_attempts,
                        "executed_actions": 0,
                    },
                    correlation,
                )
        # The claim has committed. Never call the provider while holding a database transaction.
        output, failure = None, None
        try:
            # Only the minimized copy and its separately recomputed assessment cross the boundary.
            generated = self.provider.generate(minimized_profile, assess(minimized_profile))
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
            output["trace"] = {
                "requester_principal_id": requester,
                "scope": {"use_case": USE_CASE, "purpose": body["purpose"]},
                "source_versions": [
                    {key: item[key] for key in ("object_id", "revision_id", "object_type")}
                    for item in normalized_sources
                ],
                "use_case_configuration": policy_trace,
                "model_identifier": generated["model"],
                "tool_receipts": [],
                "proposed_changes": [],
                "review_decisions": [],
                "applied_domain_receipts": [],
                "output_version": hashlib.sha256(generated["text"].encode()).hexdigest(),
                "retention_until": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
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
            # Authority may narrow while the provider is running. Recheck before persistence and
            # disclosure so a late response cannot reintroduce newly restricted source material.
            self._source_access(c, ctx, tenant, request)
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

    @staticmethod
    def _check_source(c, ctx, source):
        load(c, ctx, source["object_id"], source["object_type"], source["capability"])
        exact = c.execute(
            "SELECT 1 FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_id=%s AND object_type=%s AND restriction_state='AVAILABLE'",
            (ctx.tenant_id, source["object_id"], source["revision_id"], source["object_type"]),
        ).fetchone()
        if not exact:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)

    def _source_access(self, c, ctx, tenant, request):
        rows = c.execute(
            "SELECT source_object_id,source_revision_id,source_object_type,required_capability FROM impact.ai_advisory_source WHERE tenant_id=%s AND request_id=%s ORDER BY ordinal",
            (tenant, request),
        ).fetchall()
        for row in rows:
            self._check_source(
                c,
                ctx,
                {
                    "object_id": str(row["source_object_id"]),
                    "revision_id": str(row["source_revision_id"]),
                    "object_type": row["source_object_type"],
                    "capability": row["required_capability"],
                },
            )
