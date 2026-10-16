"""Governed saved-dashboard drafts, safe copies and current-authority previews (FR-ANA-001)."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from psycopg.types.json import Jsonb

from .domain import DomainError, unavailable
from .store import audit, authorize, context, hash_data, load, write

BINDINGS = {
    "CALCULATED_RESULT": ("CalculatedResult", "calculated-results.read"),
    "EVIDENCE": ("Evidence", "evidence.read"),
}
VIEWPORTS = {"DESKTOP", "MOBILE", "TABLE"}


def validate_dashboard(c, ctx, data):
    """Every widget keeps a visible quality context and an exact currently-readable binding."""
    widgets = data.get("widgets") or []
    if data.get("mode") != "PRIVATE_DRAFT":
        raise DomainError("VALIDATION_FAILED", reason="DASHBOARD_PRIVATE_DRAFT_REQUIRED")
    if len({item["widget_id"] for item in widgets}) != len(widgets) or len(
        {item["position"] for item in widgets}
    ) != len(widgets):
        raise DomainError("VALIDATION_FAILED", reason="DASHBOARD_LAYOUT_DUPLICATE")
    for item in widgets:
        if item["disclosure_context"].get("quality_context_required") is not True:
            raise DomainError("VALIDATION_FAILED", reason="QUALITY_CONTEXT_REQUIRED")
        geographic = item.get("geographic_config")
        if item["type"] == "MAP":
            if not geographic or item["binding"]["resource_type"] != "CALCULATED_RESULT":
                raise DomainError("VALIDATION_FAILED", reason="GEOGRAPHIC_RESULT_BINDING_REQUIRED")
            if (geographic["granularity"] == "POINT") != (
                geographic["layer"] == "AUTHORISED_POINT_REFERENCE"
            ):
                raise DomainError("VALIDATION_FAILED", reason="GEOGRAPHIC_LAYER_GRANULARITY_MISMATCH")
            if geographic["external_map"] and geographic["granularity"] == "POINT":
                raise DomainError("VALIDATION_FAILED", reason="EXTERNAL_POINT_MAP_NOT_PERMITTED")
        bindings = [item["binding"]] + [entry["binding"] for entry in item.get("approved_slices", [])]
        for binding in bindings:
            kind, capability = BINDINGS[binding["resource_type"]]
            row = load(c, ctx, binding["object_id"], kind, capability)
            if str(row["head_revision"]) != binding["revision_id"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="DASHBOARD_BINDING_REBIND_REQUIRED")


class DashboardAuthoring:
    def __init__(self, service):
        self.service = service

    def preview(self, identity, tenant, dashboard_id, viewport, drill_level=None):
        if viewport not in VIEWPORTS:
            raise DomainError("VALIDATION_FAILED", fields=[{"path": "viewport", "message": "Unsupported."}])
        if drill_level not in {None, "PORTFOLIO", "PARTNER", "PROGRAMME"}:
            raise DomainError("VALIDATION_FAILED", reason="DRILL_LEVEL_NOT_PERMITTED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "preview_dashboards", dashboard_id, hidden=True)
            dashboard = load(c, ctx, dashboard_id, "Dashboard", "dashboards.read")
            items = []
            terms = dashboard["payload"]["filters"]["terms"]
            for widget in sorted(dashboard["payload"]["widgets"], key=lambda value: value["position"]):
                compatible = set(widget.get("compatible_filters", []))
                applicable = [term for term in terms if term["field"] in compatible]
                non_applicable = [term["field"] for term in terms if term["field"] not in compatible]
                binding = widget["binding"]
                filter_effect = "NONE" if not terms else "NOT_APPLICABLE" if not applicable else "UNAVAILABLE"
                if applicable:
                    slices = widget.get("approved_slices", [])
                    if len(applicable) == 1 and len(applicable[0]["values"]) == 1:
                        selected = next(
                            (
                                item
                                for item in slices
                                if item["field"] == applicable[0]["field"]
                                and item["value"] == applicable[0]["values"][0]
                            ),
                            None,
                        )
                        if selected:
                            binding = selected["binding"]
                            filter_effect = "APPLIED"
                if drill_level and drill_level not in widget.get("drilldown_levels", []):
                    filter_effect = "UNAVAILABLE"
                kind, capability = BINDINGS[binding["resource_type"]]
                try:
                    if filter_effect == "UNAVAILABLE":
                        unavailable()
                    current = load(c, ctx, binding["object_id"], kind, capability)
                    if str(current["head_revision"]) != binding["revision_id"]:
                        unavailable()
                    payload = current["payload"]
                    if kind == "CalculatedResult":
                        present = payload.get("value_state") == "PRESENT"
                        value = payload.get("value") if present else None
                        displayed = payload.get("displayed_value") if present else None
                        table_rows = [
                            {
                                "label": widget["title"],
                                "value": value,
                                "displayed_value": displayed,
                                "value_state": payload.get("value_state"),
                            }
                        ]
                        chart_values = [value]
                    else:
                        table_rows, chart_values = [], []
                    items.append(
                        {
                            **widget,
                            "availability": "AVAILABLE",
                            "chart_values": chart_values,
                            "table_rows": table_rows,
                            "quality_context": {
                                "mode": payload.get("mode"),
                                "coverage": payload.get("coverage"),
                                "freshness": payload.get("freshness"),
                                "limitations": payload.get("limitations", []),
                            },
                            "filter_effect": filter_effect,
                            "non_applicable_filters": non_applicable,
                        }
                    )
                except DomainError as error:
                    if error.status != 404:
                        raise
                    # Never return cached payload, value or quality details after authority or pin loss.
                    items.append(
                        {
                            **widget,
                            "availability": "UNAVAILABLE",
                            "chart_values": [],
                            "table_rows": [],
                            "quality_context": None,
                            "filter_effect": filter_effect,
                            "non_applicable_filters": non_applicable,
                        }
                    )
            return {
                "dashboard_id": str(dashboard["object_id"]),
                "dashboard_revision": str(dashboard["head_revision"]),
                "title": dashboard["payload"]["title"],
                "mode": dashboard["payload"]["mode"],
                "viewport": viewport,
                "drill_level": drill_level,
                "current_filters": dashboard["payload"]["filters"],
                "widgets": items,
            }

    def copy(self, identity, tenant, source_id, body, correlation):
        op = "action_dashboards_copy"
        fingerprint = hash_data({"source_id": str(source_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op, source_id, hidden=True)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                load(c, ctx, old["outcome"]["object_id"], "Dashboard", "dashboards.read")
                return old["outcome"]
            source = load(c, ctx, source_id, "Dashboard", "dashboards.read", lock=True)
            payload = {
                **source["payload"],
                "title": body["data"].get("title", source["payload"]["title"] + " copy"),
                "mode": "PRIVATE_DRAFT",
            }
            validate_dashboard(c, ctx, payload)
            receipt = write(c, ctx, "Dashboard", payload)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return receipt

    def copy_to_workspace(self, identity, tenant, source_id, body, correlation):
        """Copy configuration only into another workspace; authority and grants never travel."""
        target_tenant = body["data"]["target_tenant_id"]
        op = "action_dashboards_copy_to_workspace"
        fingerprint = hash_data({"source_tenant_id": str(tenant), "source_id": str(source_id), "body": body})
        # Resolve an uncertain committed outcome before consulting a source that may have
        # legitimately changed since the original copy.
        with self.service.db.transaction(target_tenant) as c:
            target_ctx = context(c, identity, target_tenant)
            authorize(c, target_ctx, op, hidden=True)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (target_tenant, target_ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
        with self.service.db.transaction(tenant) as c:
            source_ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, source_ctx, "action_dashboards_copy_to_workspace", source_id, hidden=True)
            source = load(c, source_ctx, source_id, "Dashboard", "dashboards.read", lock=True)
            if str(source["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="DASHBOARD_REVISION_CHANGED")
            payload = deepcopy(source["payload"])
            payload.update(
                title=body["data"].get("title", source["payload"]["title"] + " copy"),
                mode="PRIVATE_DRAFT",
            )
            # A destination draft preserves layout and binding kinds, but never stores
            # source-workspace object or revision identifiers. Fresh opaque selectors make
            # every copied widget unavailable until it is explicitly rebound in destination.
            for widget in payload["widgets"]:
                bindings = [widget["binding"]] + [
                    item["binding"] for item in widget.get("approved_slices", [])
                ]
                for binding in bindings:
                    binding["object_id"] = str(uuid4())
                    binding["revision_id"] = str(uuid4())
        with self.service.db.transaction(target_tenant) as c:
            target_ctx = context(c, identity, target_tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (target_tenant,))
            authorize(c, target_ctx, op, hidden=True)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (target_tenant, target_ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            # Do not validate source bindings in the destination: they deliberately remain
            # unavailable selectors until separately rebound to destination-owned artifacts.
            receipt = write(c, target_ctx, "Dashboard", payload)
            receipt.update(
                operation_id=body["operation_id"],
                correlation_id=correlation,
                grants_created=False,
                unavailable_binding_count=len(payload["widgets"]),
            )
            audit(c, target_ctx, op, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    target_tenant,
                    target_ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return receipt
