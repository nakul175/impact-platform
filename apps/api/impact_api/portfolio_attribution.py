"""FR-CAL-014 permission-filtered portfolio membership and allocation preview."""

from decimal import Decimal, localcontext
from .contracts import validate
from .domain import DomainError, decimal_value, stored, unavailable
from .store import authorize, context, load, scopes, write


def _revision(c, ctx, revision_id, kind, capability):
    row = c.execute(
        "SELECT * FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        (ctx.tenant_id, revision_id),
    ).fetchone()
    if not row or row["object_type"] != kind or row["restriction_state"] != "AVAILABLE":
        unavailable()
    load(c, ctx, row["object_id"], kind, capability)
    return row


def _result_project(c, ctx, result):
    lineage = load(
        c, ctx, result["payload"]["lineage_manifest_id"], "LineageManifest", "lineage-manifests.read"
    )
    indicator = load(
        c, ctx, lineage["payload"]["indicator_id"], "IndicatorInstance", "indicator-instances.read"
    )
    return str(indicator["payload"]["programme_id"])


def _visible_result_project(c, ctx, result):
    """Return the source project only while every referenced object remains readable."""
    lineage_id = result["payload"]["lineage_manifest_id"]
    if not scopes(c, ctx, "lineage-manifests.read", lineage_id):
        return None
    lineage = load(c, ctx, lineage_id, "LineageManifest", "lineage-manifests.read")
    indicator_id = lineage["payload"]["indicator_id"]
    if not scopes(c, ctx, "indicator-instances.read", indicator_id):
        return None
    indicator = load(c, ctx, indicator_id, "IndicatorInstance", "indicator-instances.read")
    return str(indicator["payload"]["programme_id"])


def _visible_revision(c, ctx, revision_id, kind, capability):
    row = c.execute(
        "SELECT * FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        (ctx.tenant_id, revision_id),
    ).fetchone()
    if (
        not row
        or row["object_type"] != kind
        or row["restriction_state"] != "AVAILABLE"
        or not scopes(c, ctx, capability, row["object_id"])
    ):
        return None
    return row


def validate_portfolio_view(c, ctx, data):
    portfolio_ids = [row["portfolio_id"] for row in data["portfolios"]]
    if len(portfolio_ids) != len(set(portfolio_ids)):
        raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_PORTFOLIO_ID")
    memberships = {
        (row["portfolio_id"], project) for row in data["portfolios"] for project in row["project_ids"]
    }
    for project in {project for _, project in memberships}:
        load(c, ctx, project, "Programme", "programmes.read")
    totals, allocation_keys = {}, set()
    for allocation in data["allocations"]:
        if (allocation["portfolio_id"], allocation["project_id"]) not in memberships:
            raise DomainError("VALIDATION_FAILED", reason="ALLOCATION_REQUIRES_MEMBERSHIP")
        result = _revision(
            c, ctx, allocation["result_revision"], "CalculatedResult", "calculated-results.read"
        )
        if _result_project(c, ctx, result) != allocation["project_id"]:
            raise DomainError("INCOMPATIBLE_MEASURE", reason="RESULT_PROJECT_MISMATCH")
        key = (allocation["project_id"], allocation["result_revision"])
        allocation_key = (allocation["portfolio_id"], *key)
        if allocation_key in allocation_keys:
            raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_ALLOCATION")
        allocation_keys.add(allocation_key)
        totals[key] = totals.get(key, Decimal(0)) + decimal_value(allocation["share"])
    over = any(total > 1 for total in totals.values())
    if over and (not data["nonadditive"] or not data.get("nonadditive_label")):
        raise DomainError("VALIDATION_FAILED", reason="ATTRIBUTION_EXCEEDS_SOURCE")
    if not data["nonadditive"] and data.get("nonadditive_label") is not None:
        raise DomainError("VALIDATION_FAILED", reason="UNEXPECTED_NONADDITIVE_LABEL")
    if data["nonadditive"] and not data.get("nonadditive_label"):
        raise DomainError("VALIDATION_FAILED", reason="NONADDITIVE_LABEL_REQUIRED")
    if data["nonadditive"] != (data["remainder_policy"] == "NOT_APPLICABLE_NONADDITIVE"):
        raise DomainError("VALIDATION_FAILED", reason="REMAINDER_POLICY_MISMATCH")


class PortfolioAttribution:
    def __init__(self, service):
        self.service = service

    def preview(self, identity, tenant, object_id, body, correlation):
        validate("PortfolioAttributionPreviewRequest", body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "preview_portfolio_attribution", object_id, hidden=True)
            revision = _revision(
                c, ctx, body["view_revision"], "PortfolioAllocationView", "calculated-results.read"
            )
            view = load(c, ctx, object_id, "PortfolioAllocationView", "calculated-results.read")
            if (
                str(revision["object_id"]) != str(object_id)
                or view["lifecycle_state"] != "Approved"
                or str(view["head_revision"]) != body["view_revision"]
            ):
                raise DomainError("INVALID_STATE", 409, reason="CURRENT_APPROVED_ALLOCATION_VIEW_REQUIRED")
            data = revision["payload"]
            visible_projects = set()
            portfolios = []
            for portfolio in data["portfolios"]:
                projects = []
                for project in portfolio["project_ids"]:
                    if not scopes(c, ctx, "programmes.read", project):
                        continue
                    load(c, ctx, project, "Programme", "programmes.read")
                    projects.append(project)
                    visible_projects.add(project)
                portfolios.append(
                    {
                        "portfolio_id": portfolio["portfolio_id"],
                        "title": portfolio["title"],
                        "project_ids": sorted(projects),
                        "project_count": len(set(projects)),
                    }
                )
            allocations, shares, source_values = [], {}, {}
            with localcontext() as decimal_context:
                decimal_context.prec = 100
                for allocation in data["allocations"]:
                    if allocation["project_id"] not in visible_projects:
                        continue
                    result = _visible_revision(
                        c, ctx, allocation["result_revision"], "CalculatedResult", "calculated-results.read"
                    )
                    if result is None:
                        continue
                    source_project = _visible_result_project(c, ctx, result)
                    if source_project is None or source_project != allocation["project_id"]:
                        continue
                    if result["payload"].get("value_state") != "PRESENT":
                        raise DomainError("INCOMPATIBLE_MEASURE", reason="PRESENT_RESULT_REQUIRED")
                    value = decimal_value(result["payload"]["value"])
                    share = decimal_value(allocation["share"])
                    key = (allocation["project_id"], allocation["result_revision"])
                    shares[key] = shares.get(key, Decimal(0)) + share
                    source_values[key] = value
                    allocations.append({**allocation, "allocated_value": stored(value * share)})
                remainders = {
                    result_revision: stored(source_values[(project, result_revision)] * (Decimal(1) - share))
                    for (project, result_revision), share in shares.items()
                    if share <= 1
                }
            result = {
                "view_revision": body["view_revision"],
                "portfolios": portfolios,
                "organisation_unique_project_count": len(visible_projects),
                "allocations": allocations,
                "remainders": remainders,
                "nonadditive": data["nonadditive"],
                "label": data["nonadditive_label"]
                or "Funding attribution; remainder policy " + data["remainder_policy"],
                "causal_ownership": False,
            }
            validate("PortfolioAttributionPreview", result)
            observed = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            write(
                c,
                ctx,
                "AuditEvent",
                {
                    "real_actor_id": str(ctx.principal_id),
                    "effective_actor_id": str(ctx.principal_id),
                    "action_type": "portfolio.attribution.preview",
                    "object_reference": str(object_id),
                    "outcome": "SUCCEEDED",
                    "occurred_at": observed.isoformat(),
                    "correlation_id": correlation,
                    "specification_ref": "FR-CAL-014",
                },
                "Recorded",
                track_author=False,
            )
            return result
