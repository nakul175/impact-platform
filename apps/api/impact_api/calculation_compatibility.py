"""FR-CAL-002: explicit semantic compatibility and approved unit-conversion preview."""

from decimal import Decimal, ROUND_HALF_UP, localcontext

from .contracts import validate
from .domain import DomainError, decimal_value, stored, unavailable
from .store import authorize, context, load, write

CATALOGUE_VERSION = "imprana-unit-conversions-2026-10-12.1"
CONVERSIONS = {
    "area-acre-to-hectare-2026-10-12.1": {
        "version": "area-acre-to-hectare-2026-10-12.1",
        "approval_state": "APPROVED",
        "source_unit": "acre",
        "target_unit": "hectare",
        "direction": "SOURCE_TO_TARGET",
        "factor": "0.40468564224",
        "precision": 11,
        "rounding_rule": "HALF_UP",
        "catalogue_version": CATALOGUE_VERSION,
    }
}


def _approved_definition(c, ctx, revision_id):
    row = c.execute(
        "SELECT * FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        (ctx.tenant_id, revision_id),
    ).fetchone()
    if not row or row["object_type"] != "IndicatorDefinition" or row["restriction_state"] != "AVAILABLE":
        unavailable()
    current = load(c, ctx, row["object_id"], "IndicatorDefinition", "indicator-definitions.read")
    if current["lifecycle_state"] != "Approved" or str(current["head_revision"]) != str(revision_id):
        raise DomainError("STATE_TRANSITION_DENIED", 409, reason="APPROVED_DEFINITION_REQUIRED")
    return row


def _dimensions(definition):
    scheme = definition.get("disaggregation") or {}
    return [
        {
            "code": item["code"],
            "version": item["version"],
            "multiselect": item["multiselect"],
            "exhaustive": item["exhaustive"],
            "categories": [category["code"] for category in item["categories"]],
        }
        for item in scheme.get("dimensions", [])
    ]


def _semantic_signature(definition):
    return {
        "measurement_type": definition["measurement_type"],
        "population": definition["population"],
        "inclusion": definition["inclusion"],
        "exclusion": definition["exclusion"],
        "method": definition["method"],
        "time_semantic": definition["time_semantic"],
        "dimensions": _dimensions(definition),
    }


def _scalar_value(definition, raw):
    value = decimal_value(raw)
    if not _valid_count(definition, value):
        raise DomainError("VALIDATION_FAILED", reason="INVALID_MEASUREMENT_VALUE")
    return value


def _valid_count(definition, value):
    return definition["measurement_type"] != "COUNT" or (value >= 0 and value == value.to_integral_value())


class CalculationCompatibility:
    def __init__(self, service):
        self.service = service

    def preview(self, identity, tenant, body, correlation):
        validate("CalculationCompatibilityPreviewRequest", body)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "preview_calculation_compatibility", hidden=True)
            target = _approved_definition(c, ctx, body["target_definition_revision"])
            target_data = target["payload"]
            signature = _semantic_signature(target_data)
            if target_data["combination_rule"] != "SUM":
                raise DomainError("INCOMPATIBLE_MEASURE", reason="COMBINATION_RULE_NOT_SUM")

            normalized = []
            with localcontext() as decimal_context:
                decimal_context.prec = 100
                for item in body["inputs"]:
                    source = _approved_definition(c, ctx, item["definition_revision"])
                    source_data = source["payload"]
                    if _semantic_signature(source_data) != signature:
                        raise DomainError("INCOMPATIBLE_MEASURE", reason="SEMANTIC_MISMATCH")
                    original = _scalar_value(source_data, item["value"])
                    conversion = None
                    converted = original
                    if source_data["unit"] != target_data["unit"]:
                        conversion = CONVERSIONS.get(item.get("conversion_version"))
                        if (
                            not conversion
                            or conversion["approval_state"] != "APPROVED"
                            or conversion["source_unit"] != source_data["unit"]
                            or conversion["target_unit"] != target_data["unit"]
                        ):
                            raise DomainError("INCOMPATIBLE_MEASURE", reason="APPROVED_CONVERSION_REQUIRED")
                        quantum = Decimal(1).scaleb(-conversion["precision"])
                        converted = (original * Decimal(conversion["factor"])).quantize(
                            quantum, rounding=ROUND_HALF_UP
                        )
                    elif item.get("conversion_version") is not None:
                        raise DomainError("VALIDATION_FAILED", reason="UNNECESSARY_CONVERSION")
                    if not _valid_count(target_data, converted):
                        raise DomainError("VALIDATION_FAILED", reason="INVALID_CONVERTED_MEASUREMENT_VALUE")
                    converted_text = stored(converted)
                    normalized.append(
                        {
                            "definition_revision": str(source["revision_id"]),
                            "original_value": format(original, "f"),
                            "original_unit": source_data["unit"],
                            "converted_value": converted_text,
                            "target_unit": target_data["unit"],
                            "conversion": conversion,
                        }
                    )

                total = stored(sum((Decimal(item["converted_value"]) for item in normalized), Decimal(0)))
            response = {
                "compatible": True,
                "target_definition_revision": str(target["revision_id"]),
                "compatibility": signature,
                "inputs": normalized,
                "combined_value": total,
                "unit": target_data["unit"],
            }
            validate("CalculationCompatibilityPreview", response)
            observed = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            write(
                c,
                ctx,
                "AuditEvent",
                {
                    "real_actor_id": str(ctx.principal_id),
                    "effective_actor_id": str(ctx.principal_id),
                    "action_type": "calculation.compatibility.preview",
                    "object_reference": str(target["object_id"]),
                    "outcome": "SUCCEEDED",
                    "occurred_at": observed.isoformat(),
                    "correlation_id": correlation,
                    "specification_ref": "FR-CAL-002",
                },
                "Recorded",
                track_author=False,
            )
            return response
