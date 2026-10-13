"""Closed typed numerical analysis executed by the governed decimal tool."""

from decimal import Decimal, ROUND_HALF_UP, localcontext

from . import ai_policy
from .ai_safety import require_available
from .domain import DomainError, NUMBER
from .service import revision
from .store import authorize, context, hash_data, load

USE_CASE = "NUMERIC_ANALYSIS"
PURPOSE = "GOVERNED_NUMERIC_ANALYSIS"
TOOL = "governed.pool_ratio.v1"


def decimal(value):
    if not isinstance(value, str) or not NUMBER.fullmatch(value):
        raise DomainError("VALIDATION_FAILED", reason="ANALYSIS_SOURCE_VALUE_INVALID")
    return Decimal(value)


class AINumericAnalysis:
    def __init__(self, service, destination, configuration):
        self.service = service
        self.destination = destination
        self.configuration = configuration

    def execute(self, identity, tenant, body):
        plan = body["plan"]
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "execute_ai_numeric_analysis", hidden=True)
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                body["policy_version"],
                "CONFIDENTIAL",
                self.destination,
                body["language"],
                (TOOL,),
                PURPOSE,
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            period = load(c, ctx, plan["period_id"], "Period", "periods.read")
            if str(period["head_revision"]) != plan["period_revision_id"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="ANALYSIS_PERIOD_CHANGED")
            inputs = []
            numerator = Decimal(0)
            denominator = Decimal(0)
            with localcontext() as decimal_context:
                decimal_context.prec = 100
                for selector in plan["sources"]:
                    source = revision(
                        c,
                        ctx,
                        selector["revision_id"],
                        "CalculatedResult",
                        "calculated-results.read",
                    )
                    if str(source["object_id"]) != selector["object_id"]:
                        raise DomainError("RESOURCE_UNAVAILABLE", 404)
                    payload = source["payload"]
                    if (
                        payload.get("value_state") != "PRESENT"
                        or payload.get("numerator") is None
                        or payload.get("denominator") is None
                        or str(payload.get("period_id")) != plan["period_id"]
                        or payload.get("formula", {}).get("measurement_type") not in {"RATIO", "PERCENTAGE"}
                        or (plan["source_mode"] == "OFFICIAL" and payload.get("mode") != "OFFICIAL")
                    ):
                        raise DomainError("VALIDATION_FAILED", reason="ANALYSIS_SOURCE_INCOMPATIBLE")
                    n = decimal(payload["numerator"])
                    d = decimal(payload["denominator"])
                    if n < 0 or d < 0:
                        raise DomainError("VALIDATION_FAILED", reason="ANALYSIS_SOURCE_VALUE_INVALID")
                    numerator += n
                    denominator += d
                    inputs.append(
                        {
                            "object_id": str(source["object_id"]),
                            "revision_id": str(source["revision_id"]),
                            "numerator": format(n, "f"),
                            "denominator": format(d, "f"),
                        }
                    )
                if denominator == 0:
                    raise DomainError("VALIDATION_FAILED", reason="ANALYSIS_ZERO_DENOMINATOR")
                ratio = numerator / denominator
                percent = (ratio * Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            numerator_text = format(numerator, "f")
            denominator_text = format(denominator, "f")
            percent_text = format(percent, ".2f")
            claim = f"{percent_text} percent ({numerator_text}/{denominator_text})"
            if body.get("drafted_claim") is not None and body["drafted_claim"] != claim:
                raise DomainError("VALIDATION_FAILED", reason="AI_NUMERIC_CLAIM_MISMATCH")
            receipt_id = hash_data(
                [
                    TOOL,
                    plan,
                    inputs,
                    numerator_text,
                    denominator_text,
                    percent_text,
                ]
            ).hex()
            return {
                "state": "ANSWERED",
                "plan": plan,
                "answer": claim,
                "value": percent_text,
                "unit": "percent",
                "numerator": numerator_text,
                "denominator": denominator_text,
                "result_references": inputs,
                "calculation_receipt": {
                    "receipt_id": receipt_id,
                    "tool": TOOL,
                    "precision_digits": 100,
                    "rounding_rule": "HALF_UP",
                    "operation": "POOL_RATIO",
                },
                "model_recomputed": False,
                "arbitrary_query_executed": False,
                "official_claim_matches_tool": True,
            }
