"""Permission-safe geographic projection shared by map and equivalent table (FR-ANA-006)."""

from .domain import DomainError, unavailable
from .store import authorize, context, load


class DashboardGeography:
    def __init__(self, service):
        self.service = service

    def preview(self, identity, tenant, dashboard_id, widget_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "preview_dashboard_geography", dashboard_id, hidden=True)
            dashboard = load(c, ctx, dashboard_id, "Dashboard", "dashboards.read")
            widget = next(
                (
                    item
                    for item in dashboard["payload"].get("widgets", [])
                    if item["widget_id"] == str(widget_id)
                ),
                None,
            )
            if not widget or widget.get("type") != "MAP" or not widget.get("geographic_config"):
                unavailable()
            binding = widget["binding"]
            if binding["resource_type"] != "CALCULATED_RESULT":
                unavailable()
            result = load(c, ctx, binding["object_id"], "CalculatedResult", "calculated-results.read")
            if str(result["head_revision"]) != binding["revision_id"]:
                unavailable()
            config = widget["geographic_config"]
            if config["external_map"] and config["granularity"] == "POINT":
                raise DomainError("POLICY_DENIED", 403, reason="EXTERNAL_POINT_MAP_NOT_PERMITTED")
            raw = [
                entry
                for entry in result["payload"].get("disaggregation", [])
                if entry.get("dimension") == config["dimension"]
            ]
            versions = sorted({entry["dimension_version"] for entry in raw if entry.get("dimension_version")})
            selected = config["boundary_version"]
            boundary_status = (
                "UNVERSIONED" if not versions else "MATCH" if versions == [selected] else "MISMATCH"
            )
            rows, missing = [], 0
            for entry in raw:
                state = entry.get("value_state")
                visible = state == "PRESENT" and entry.get("value") is not None
                if not visible:
                    missing += 1
                    if config["missingness"] != "SHOW_MISSING":
                        continue
                row = {
                    "geography_key": entry.get("category"),
                    "value_state": state,
                    "value": entry.get("value") if visible else None,
                    "displayed_value": entry.get("displayed_value") if visible else None,
                    "disclosure": "VISIBLE" if visible else "SUPPRESSED",
                    "boundary_version": entry.get("dimension_version"),
                    "tooltip": {
                        "label": entry.get("category"),
                        "displayed_value": entry.get("displayed_value") if visible else None,
                        "value_state": state,
                    },
                }
                rows.append(row)
            # The same coordinate-free rows feed both renderings. No hidden tooltip/download payload exists.
            return {
                "dashboard_id": str(dashboard["object_id"]),
                "dashboard_revision": str(dashboard["head_revision"]),
                "widget_id": str(widget_id),
                "period_id": widget["period_id"],
                "boundary_version": selected,
                "data_boundary_versions": versions,
                "boundary_status": boundary_status,
                "layer": config["layer"],
                "granularity": config["granularity"],
                "legend": config["legend"],
                "missingness": config["missingness"],
                "coordinate_delivery": "NO_COORDINATES_IN_PLATFORM_PAYLOAD",
                "map_request": rows,
                "equivalent_table": rows,
                "sortable_fields": ["geography_key", "value", "value_state"],
                "missing_count": missing if config["missingness"] == "EXCLUDE_WITH_COUNT" else None,
            }
