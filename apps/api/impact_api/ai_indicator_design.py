"""Governed indicator draft proposals from approved definitions and current programme context."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from psycopg.types.json import Jsonb

from . import ai_policy
from .ai_runtime_activation import activated
from .ai_safety import require_available
from .contracts import validate
from .domain import DomainError
from .measurement import definition_ready
from .store import audit, authorize, context, hash_data, load, write

USE_CASE = "INDICATOR_DESIGN"
PURPOSE = "INDICATOR_DESIGN_ASSISTANCE"
FIELDS = (
    "code",
    "name",
    "measurement_type",
    "unit",
    "population",
    "inclusion",
    "exclusion",
    "method",
    "source_mode",
    "time_semantic",
    "combination_rule",
    "display_decimals",
    "numerator_meaning",
    "denominator_meaning",
    "disaggregation",
)


def proposal(definition, programme, proxy_basis):
    data = {field: definition[field] for field in FIELDS if field in definition}
    warnings = []
    if data.get("measurement_type") in {"RATIO", "PERCENTAGE"}:
        if not str(data.get("denominator_meaning", "")).strip():
            warnings.append("ELIGIBLE_DENOMINATOR_MISSING")
        warnings.append("DENOMINATOR_ELIGIBILITY_REQUIRES_HUMAN_REVIEW")
    if not str(data.get("population", "")).strip():
        warnings.append("POPULATION_MISSING")
    else:
        warnings.append("POPULATION_REQUIRES_PROGRAMME_CONTEXT_REVIEW")
    if proxy_basis == "PROXY":
        warnings.append("PROXY_SUITABILITY_REQUIRES_HUMAN_REVIEW")
    if not str(data.get("method", "")).strip() or not data.get("source_mode"):
        warnings.append("EVIDENCE_METHOD_MISSING")
    return {
        "proposed_fields": data,
        "warnings": warnings,
        "programme_context": {
            "programme_id": str(programme["object_id"]),
            "programme_revision_id": str(programme["head_revision"]),
            "title": programme["payload"].get("name") or programme["payload"].get("title"),
        },
        "model_confidence": None,
        "can_approve": False,
        "standard_mapping_created": False,
    }


class AIIndicatorDesign:
    def __init__(self, service, destination, configuration):
        self.service = service
        self.destination = destination
        self.configuration = configuration

    def _sources(self, c, ctx, body):
        definition = load(
            c,
            ctx,
            UUID(body["library_definition_id"]),
            "IndicatorDefinition",
            "indicator-definitions.read",
        )
        programme = load(c, ctx, UUID(body["programme_id"]), "Programme", "programmes.read")
        if (
            definition["lifecycle_state"] != "Approved"
            or str(definition["head_revision"]) != body["library_definition_revision_id"]
        ):
            raise DomainError("CONFLICT_VERSION", 409, reason="APPROVED_DEFINITION_CHANGED")
        if str(programme["head_revision"]) != body["programme_revision_id"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="PROGRAMME_CONTEXT_CHANGED")
        definition_ready(definition["payload"])
        return definition, programme

    def _policy(self, c, tenant, body, classification):
        policy = ai_policy.in_force(c, tenant)
        ai_policy.require(
            policy,
            USE_CASE,
            body["policy_version"],
            classification,
            self.destination,
            body["language"],
            (),
            PURPOSE,
            activated_use_cases=activated(self.service),
        )
        require_available(c, tenant, USE_CASE, self.destination, self.configuration)

    def propose(self, identity, tenant, body):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "create_ai_indicator_proposal", hidden=True)
            definition, programme = self._sources(c, ctx, body)
            classification = max(
                (definition["classification"], programme["classification"]),
                key=ai_policy.CLASS_RANK.get,
            )
            self._policy(c, tenant, body, classification)
            result = proposal(definition["payload"], programme, body["proxy_basis"])
            return {
                **result,
                "library_definition_id": str(definition["object_id"]),
                "library_definition_revision_id": str(definition["head_revision"]),
            }

    def create_draft(self, identity, tenant, body, correlation):
        fingerprint = hash_data(["create_ai_indicator_draft", None, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_indicator_draft", hidden=True)
            authorize(c, ctx, "create_indicator_definitions", hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type='create_ai_indicator_draft' AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                load(c, ctx, old["outcome"]["object_id"], "IndicatorDefinition")
                return old["outcome"]
            definition, programme = self._sources(c, ctx, body)
            classification = max(
                (definition["classification"], programme["classification"]),
                key=ai_policy.CLASS_RANK.get,
            )
            self._policy(c, tenant, body, classification)
            candidate = proposal(definition["payload"], programme, body["proxy_basis"])
            selected = body["selected_fields"]
            if any(field not in FIELDS for field in selected):
                raise DomainError("VALIDATION_FAILED", 400, reason="INDICATOR_FIELD_SELECTION_INVALID")
            data = {field: candidate["proposed_fields"][field] for field in selected}
            validate("IndicatorDefinitionDraftData", data)
            self.service.validate_data(c, ctx, "IndicatorDefinition", data, ctx.principal_id)
            receipt = write(c, ctx, "IndicatorDefinition", data, "Draft")
            receipt.update(
                operation_id=body["operation_id"],
                correlation_id=correlation,
                source_definition_revision_id=str(definition["head_revision"]),
                programme_revision_id=str(programme["head_revision"]),
                warnings=candidate["warnings"],
                submit_ready=self._ready(data),
                standard_mapping_created=False,
            )
            audit(c, ctx, "create_ai_indicator_draft", receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,'create_ai_indicator_draft',%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt

    @staticmethod
    def _ready(data):
        try:
            definition_ready(data)
            return True
        except DomainError:
            return False
