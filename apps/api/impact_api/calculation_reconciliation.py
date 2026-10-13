"""FR-CAL-015 permission-safe result explanations and causal run reconciliation."""

from decimal import Decimal

from .contracts import validate
from .domain import DomainError, calculate, decimal_value, stored
from .store import authorize, context, load, write


def _manifest(c, ctx, result):
    manifest_id = result["payload"].get("lineage_manifest_id")
    if not manifest_id:
        raise DomainError("INCOMPATIBLE_MEASURE", reason="EXPLANATION_MANIFEST_UNSUPPORTED")
    manifest = load(
        c,
        ctx,
        manifest_id,
        "LineageManifest",
        "lineage-manifests.read",
    )
    data = manifest["payload"]
    required = {
        "execution_id",
        "indicator_id",
        "definition_revision",
        "indicator_revision",
        "period_id",
        "formula",
        "filters",
        "contributions",
    }
    if not required <= set(data):
        raise DomainError("INCOMPATIBLE_MEASURE", reason="EXPLANATION_MANIFEST_UNSUPPORTED")
    return manifest


def _contribution_counts(items):
    included = sum(item["disposition"] == "INCLUDED" for item in items)
    reasons = {}
    for item in items:
        if item["disposition"] == "EXCLUDED":
            reason = item["reason_code"]
            reasons[reason] = reasons.get(reason, 0) + 1
    return (
        included,
        len(items) - included,
        [{"reason_code": reason, "count": count} for reason, count in sorted(reasons.items())],
    )


def _value(payload):
    return decimal_value(payload["value"]) if payload.get("value_state") == "PRESENT" else None


def _revision_id(row):
    return str(row.get("head_revision") or row["revision_id"])


class CalculationReconciliation:
    def __init__(self, service):
        self.service = service

    def explain(self, identity, tenant, object_id, correlation):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_calculated_result_explanation", object_id, hidden=True)
            result = load(c, ctx, object_id, "CalculatedResult", "calculated-results.read")
            manifest = _manifest(c, ctx, result)
            included, excluded, reasons = _contribution_counts(manifest["payload"]["contributions"])
            payload = result["payload"]
            if "coverage" not in payload:
                raise DomainError("INCOMPATIBLE_MEASURE", reason="EXPLANATION_RESULT_UNSUPPORTED")
            formula = manifest["payload"]["formula"]
            adjustments = []
            if formula.get("negative_adjustment_basis"):
                adjustments.append(
                    {
                        "code": "NEGATIVE_ADJUSTMENT",
                        "message": formula["negative_adjustment_basis"],
                    }
                )
            if formula.get("cumulative_baseline") is not None:
                adjustments.append(
                    {
                        "code": "CUMULATIVE_BASELINE",
                        "message": (
                            "Starting baseline "
                            + formula["cumulative_baseline"]
                            + ": "
                            + formula["cumulative_baseline_basis"]
                        ),
                    }
                )
            response = {
                "result_id": str(result["object_id"]),
                "result_revision": str(result["head_revision"]),
                "rule_version": manifest["payload"]["definition_revision"],
                "source_set": {
                    "manifest_id": str(manifest["object_id"]),
                    "execution_id": manifest["payload"]["execution_id"],
                    "included_count": included,
                    "excluded_count": excluded,
                    "excluded_reasons": reasons,
                },
                "formula": formula,
                "filters": manifest["payload"]["filters"],
                "adjustments": adjustments,
                "coverage": payload["coverage"],
                "approval": {
                    "mode": payload["mode"],
                    "lifecycle_state": result["lifecycle_state"],
                },
            }
            validate("CalculationExplanation", response)
            self._audit(c, ctx, result, correlation, "calculation.explanation.read")
            return response

    def compare(self, identity, tenant, earlier_id, later_id, correlation):
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "compare_calculated_result_runs", hidden=True)
            earlier = load(c, ctx, earlier_id, "CalculatedResult", "calculated-results.read")
            later = load(c, ctx, later_id, "CalculatedResult", "calculated-results.read")
            response = self._compare_rows(c, ctx, earlier, later)
            validate("CalculationComparison", response)
            self._audit(c, ctx, later, correlation, "calculation.runs.compare")
            return response

    def _compare_rows(self, c, ctx, earlier, later):
        old_manifest, new_manifest = _manifest(c, ctx, earlier), _manifest(c, ctx, later)
        old_data, new_data = old_manifest["payload"], new_manifest["payload"]
        if old_data["indicator_id"] != new_data["indicator_id"]:
            raise DomainError("INCOMPATIBLE_MEASURE", reason="COMPARISON_INDICATOR_MISMATCH")
        causes = []
        if (
            old_data["definition_revision"] != new_data["definition_revision"]
            or old_data["indicator_revision"] != new_data["indicator_revision"]
        ):
            causes.append({"category": "RULE", "effect": None, "reference_state": "PERMITTED"})
        for category, field in (
            ("PERIOD", "period_id"),
            ("TARGET", "target_revision"),
            ("PERMISSION", "permission_epoch"),
            ("DISCLOSURE", "disclosure_revision"),
        ):
            if old_data.get(field) != new_data.get(field):
                causes.append(
                    {
                        "category": category,
                        "effect": "0" if category in {"TARGET", "PERMISSION", "DISCLOSURE"} else None,
                        "reference_state": ("WITHHELD" if category == "DISCLOSURE" else "PERMITTED"),
                    }
                )
        source_effect, filter_effect, withheld = self._numeric_bridge(
            c, ctx, earlier, later, old_data, new_data
        )
        if source_effect is not None:
            causes.append(
                {"category": "SOURCE", "effect": stored(source_effect), "reference_state": "PERMITTED"}
            )
        if filter_effect is not None:
            causes.append(
                {"category": "FILTER", "effect": stored(filter_effect), "reference_state": "PERMITTED"}
            )
        if withheld:
            permission = next((item for item in causes if item["category"] == "PERMISSION"), None)
            if permission:
                permission.update(effect=None, reference_state="WITHHELD")
            else:
                causes.append({"category": "PERMISSION", "effect": None, "reference_state": "WITHHELD"})
        before, after = _value(earlier["payload"]), _value(later["payload"])
        difference = after - before if before is not None and after is not None else None
        unvalued = [item for item in causes if item["effect"] is None]
        if (
            difference is not None
            and source_effect is None
            and filter_effect is None
            and len(unvalued) == 1
            and unvalued[0]["category"] in {"RULE", "PERIOD"}
            and not withheld
        ):
            unvalued[0]["effect"] = stored(difference)
        explained = sum(
            (decimal_value(item["effect"]) for item in causes if item["effect"] is not None),
            Decimal(0),
        )
        reconciled = (
            difference is not None
            and not withheld
            and all(item["effect"] is not None for item in causes)
            and explained == difference
        )
        return {
            "earlier_result_revision": _revision_id(earlier),
            "later_result_revision": _revision_id(later),
            "difference": stored(difference) if difference is not None else None,
            "causes": causes,
            "explained_difference": stored(explained) if difference is not None else None,
            "reconciled": reconciled,
            "approval_blocked": not reconciled,
        }

    def assert_report_reconciled(self, c, ctx, report):
        """Every changed numeric binding since the prior report revision must have a complete,
        permission-safe causal bridge. A first report has no prior numerical difference."""
        from .service import revision

        prior = c.execute(
            "SELECT approved.* FROM impact.object_revision approved "
            "JOIN impact.object_revision submitted ON submitted.tenant_id=approved.tenant_id "
            "AND submitted.revision_id=approved.predecessor_revision "
            "JOIN impact.decision_current decision ON decision.tenant_id=submitted.tenant_id "
            "AND decision.candidate_revision=submitted.revision_id AND decision.action='APPROVE' "
            "WHERE approved.tenant_id=%s AND approved.object_id=%s "
            "AND approved.object_type='Report' AND approved.revision_number<%s "
            "AND approved.restriction_state='AVAILABLE' "
            "ORDER BY approved.revision_number DESC LIMIT 1",
            (ctx.tenant_id, report["object_id"], report["revision_number"]),
        ).fetchone()
        if not prior:
            return

        def bindings(payload):
            return {
                (section["section_code"], binding["binding_code"]): binding["result_revision"]
                for section in payload.get("sections", [])
                for binding in section.get("bindings", [])
            }

        old, new = bindings(prior["payload"]), bindings(report["payload"])
        for key in sorted(set(old) & set(new)):
            if old[key] == new[key]:
                continue
            earlier = revision(c, ctx, old[key], "CalculatedResult", "calculated-results.read")
            later = revision(c, ctx, new[key], "CalculatedResult", "calculated-results.read")
            if not self._compare_rows(c, ctx, earlier, later)["reconciled"]:
                raise DomainError("INVALID_STATE", 409, reason="REPORT_DIFFERENCE_UNRECONCILED")

    def _numeric_bridge(self, c, ctx, earlier, later, old_data, new_data):
        if (
            old_data["definition_revision"] != new_data["definition_revision"]
            or old_data["period_id"] != new_data["period_id"]
        ):
            return None, None, False
        from .service import revision

        definition = revision(
            c, ctx, old_data["definition_revision"], "IndicatorDefinition", "indicator-definitions.read"
        )["payload"]
        old_items = {item["source_object_id"]: item for item in old_data["contributions"]}
        new_items = {item["source_object_id"]: item for item in new_data["contributions"]}
        new_payloads = {}
        withheld = False
        for source_revision in new_data.get("source_revisions", []):
            try:
                source = revision(c, ctx, source_revision, "Observation", "observations.read")
            except DomainError as error:
                if error.status != 404:
                    raise
                withheld = True
                continue
            new_payloads[str(source["object_id"])] = source["payload"]
        if withheld:
            return None, None, True
        old_included = [
            new_payloads[object_id]
            for object_id, item in old_items.items()
            if item["disposition"] == "INCLUDED" and object_id in new_payloads
        ] + [
            new_payloads[object_id]
            for object_id, item in new_items.items()
            if object_id not in old_items and item["disposition"] == "INCLUDED"
        ]
        new_included = [
            new_payloads[object_id]
            for object_id, item in new_items.items()
            if item["disposition"] == "INCLUDED" and object_id in new_payloads
        ]
        before, after = _value(earlier["payload"]), _value(later["payload"])
        bridge = _value(calculate(definition, old_included))
        recomputed_after = _value(calculate(definition, new_included))
        if None in {before, after, bridge, recomputed_after} or recomputed_after != after:
            return None, None, False
        return bridge - before, after - bridge, False

    @staticmethod
    def _audit(c, ctx, result, correlation, action):
        observed = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
        write(
            c,
            ctx,
            "AuditEvent",
            {
                "real_actor_id": str(ctx.principal_id),
                "effective_actor_id": str(ctx.principal_id),
                "action_type": action,
                "object_reference": str(result["object_id"]),
                "outcome": "SUCCEEDED",
                "occurred_at": observed.isoformat(),
                "correlation_id": correlation,
                "specification_ref": "FR-CAL-015",
            },
            "Recorded",
            track_author=False,
        )
