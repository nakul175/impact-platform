"""FR-CAL-007 governed dimension alignment without invented precision."""

from decimal import Decimal

from .contracts import validate
from .domain import DomainError, decimal_value, stored, unavailable
from .store import authorize, context, load, write


def _revision(c, ctx, revision_id, kind, capability):
    row = c.execute(
        "SELECT * FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        (ctx.tenant_id, revision_id),
    ).fetchone()
    if not row or row["object_type"] != kind or row["restriction_state"] != "AVAILABLE":
        unavailable()
    load(c, ctx, row["object_id"], kind, capability)
    return row


def _dimension(definition, code):
    rows = (definition.get("disaggregation") or {}).get("dimensions", [])
    dimension = next((row for row in rows if row["code"] == code), None)
    if not dimension:
        raise DomainError("VALIDATION_FAILED", reason="DIMENSION_VERSION_NOT_FOUND")
    return dimension


def validate_crosswalk(c, ctx, data):
    source = _revision(
        c, ctx, data["source_definition_revision"], "IndicatorDefinition", "indicator-definitions.read"
    )
    target = _revision(
        c, ctx, data["target_definition_revision"], "IndicatorDefinition", "indicator-definitions.read"
    )
    for row in (source, target):
        load(c, ctx, row["object_id"], "IndicatorDefinition", "indicator-definitions.read")
        approved = c.execute(
            "SELECT 1 FROM impact.decision_current WHERE tenant_id=%s AND candidate_revision=%s AND action='APPROVE' LIMIT 1",
            (ctx.tenant_id, row["revision_id"]),
        ).fetchone()
        if not approved:
            raise DomainError("INVALID_STATE", 409, reason="APPROVED_DEFINITION_REVISION_REQUIRED")
    source_dimension = _dimension(source["payload"], data["source_dimension_code"])
    target_dimension = _dimension(target["payload"], data["target_dimension_code"])
    source_codes = {x["code"] for x in source_dimension["categories"]}
    target_codes = {x["code"] for x in target_dimension["categories"]}
    source_unknown_codes = {
        x["code"]
        for x in source_dimension["categories"]
        if x["code"].upper() in {"UNKNOWN", "UNK"} or "unknown" in x.get("label", "").lower()
    }
    target_unknown_codes = {
        x["code"]
        for x in target_dimension["categories"]
        if x["code"].upper() in {"UNKNOWN", "UNK"} or "unknown" in x.get("label", "").lower()
    }
    by_source = {}
    for mapping in data["mappings"]:
        if mapping["source_category"] not in source_codes or mapping["target_category"] not in target_codes:
            raise DomainError("VALIDATION_FAILED", reason="CATEGORY_NOT_IN_PINNED_DIMENSION")
        by_source.setdefault(mapping["source_category"], []).append(mapping)
        source_unknown = mapping["source_category"] in source_unknown_codes
        target_unknown = mapping["target_category"] in target_unknown_codes
        if source_unknown and not target_unknown:
            raise DomainError("VALIDATION_FAILED", reason="UNKNOWN_CATEGORY_REMAP_REFUSED")
    if data["mapping_type"] == "EXACT":
        if (
            data["information_loss"] != "NONE"
            or data.get("estimation_method") is not None
            or any(len(rows) != 1 or rows[0].get("weight") is not None for rows in by_source.values())
        ):
            raise DomainError("VALIDATION_FAILED", reason="EXACT_MAPPING_CONTRACT_VIOLATION")
        targets = [rows[0]["target_category"] for rows in by_source.values()]
        if len(targets) != len(set(targets)):
            raise DomainError("VALIDATION_FAILED", reason="EXACT_MAPPING_MUST_BE_ONE_TO_ONE")
        if any(source_code != rows[0]["target_category"] for source_code, rows in by_source.items()):
            raise DomainError("VALIDATION_FAILED", reason="EXACT_MAPPING_REQUIRES_IDENTICAL_CODE")
    elif data["mapping_type"] == "MANY_TO_ONE":
        if (
            data["information_loss"] != "POOLING"
            or data.get("estimation_method") is not None
            or any(len(rows) != 1 or rows[0].get("weight") is not None for rows in by_source.values())
        ):
            raise DomainError("VALIDATION_FAILED", reason="POOLING_MAPPING_CONTRACT_VIOLATION")
    else:
        if data["information_loss"] != "ESTIMATED" or not data.get("estimation_method"):
            raise DomainError("VALIDATION_FAILED", reason="ESTIMATION_METHOD_REQUIRED")
        for rows in by_source.values():
            weights = [decimal_value(row.get("weight")) for row in rows if row.get("weight") is not None]
            if (
                len(weights) != len(rows)
                or any(weight < 0 for weight in weights)
                or sum(weights, Decimal(0)) != Decimal(1)
            ):
                raise DomainError("VALIDATION_FAILED", reason="PROPORTIONAL_WEIGHTS_NOT_RECONCILED")


class DimensionCrosswalk:
    def __init__(self, service):
        self.service = service

    def preview(self, identity, tenant, object_id, body, correlation):
        validate("DimensionCrosswalkPreviewRequest", body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "preview_dimension_crosswalk", object_id, hidden=True)
            crosswalk_revision = _revision(
                c, ctx, body["crosswalk_revision"], "DimensionCrosswalk", "calculated-results.read"
            )
            crosswalk = load(c, ctx, object_id, "DimensionCrosswalk", "calculated-results.read")
            if (
                str(crosswalk_revision["object_id"]) != str(object_id)
                or crosswalk["lifecycle_state"] != "Approved"
                or str(crosswalk["head_revision"]) != body["crosswalk_revision"]
            ):
                raise DomainError("INVALID_STATE", 409, reason="CURRENT_APPROVED_CROSSWALK_REQUIRED")
            data = crosswalk_revision["payload"]
            validate_crosswalk(c, ctx, data)
            mappings = {}
            for row in data["mappings"]:
                mappings.setdefault(row["source_category"], []).append(row)
            totals, unmapped, suppressed = {}, [], []
            for item in body["inputs"]:
                rows = mappings.get(item["source_category"], [])
                if not rows:
                    unmapped.append(item["source_category"])
                    continue
                if all(row["suppressed"] for row in rows):
                    suppressed.append(item["source_category"])
                    continue
                value = decimal_value(item["value"])
                for row in rows:
                    if row["suppressed"]:
                        suppressed.append(item["source_category"])
                        continue
                    contribution = (
                        value * decimal_value(row["weight"])
                        if data["mapping_type"] == "PROPORTIONAL"
                        else value
                    )
                    totals[row["target_category"]] = (
                        totals.get(row["target_category"], Decimal(0)) + contribution
                    )
            result = {
                "crosswalk_revision": body["crosswalk_revision"],
                "mapping_type": data["mapping_type"],
                "information_loss": data["information_loss"],
                "mapped": [
                    {"target_category": code, "value": stored(value)}
                    for code, value in sorted(totals.items())
                ],
                "unmapped_source_categories": sorted(set(unmapped)),
                "suppressed_source_categories": sorted(set(suppressed)),
            }
            validate("DimensionCrosswalkPreview", result)
            observed = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            write(
                c,
                ctx,
                "AuditEvent",
                {
                    "real_actor_id": str(ctx.principal_id),
                    "effective_actor_id": str(ctx.principal_id),
                    "action_type": "dimension.crosswalk.preview",
                    "object_reference": str(object_id),
                    "outcome": "SUCCEEDED",
                    "occurred_at": observed.isoformat(),
                    "correlation_id": correlation,
                    "specification_ref": "FR-CAL-007",
                },
                "Recorded",
                track_author=False,
            )
            return result
