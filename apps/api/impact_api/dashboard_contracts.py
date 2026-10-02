"""Dashboard read contracts (v0.24): a programme dashboard for one period and an indicator series
across periods. Both are read-only, bounded and keyset-paginated with signed cursors; the
capability is the design contract's `dashboards.read` (the design's authored Dashboard object and
its draft/publish operations are not implemented)."""

from copy import deepcopy

from .measurement_contracts import closed

UUID = {"type": "string", "format": "uuid"}
NULLABLE_UUID = {"type": ["string", "null"], "format": "uuid"}
DECIMAL = r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"
NULLABLE_DECIMAL = {"type": ["string", "null"], "pattern": DECIMAL}
NULLABLE_TEXT = {"type": ["string", "null"], "maxLength": 2000}
NULLABLE_COUNT = {"type": ["integer", "null"], "minimum": 0}
VALUE_STATES = ["PRESENT", "MISSING", "NOT_COLLECTED", "NOT_APPLICABLE", "INVALID", "UNDEFINED"]
SPECIAL_READS = {
    "programmes/{object_id}/dashboard": ("programme_dashboard", "dashboards.read", "ProgrammeDashboard"),
    "indicator-instances/{object_id}/dashboard-series": (
        "indicator_dashboard_series",
        "dashboards.read",
        "IndicatorDashboardSeries",
    ),
}
# Per-operation contract tag; the integrator aligns it with the build's API version.
VERSION = "1.14.0"
ROLES = ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST", "DATA_STEWARD", "EXTERNAL"]


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"

    category = closed(
        {
            "dimension": {"type": ["string", "null"]},
            "dimension_version": {"type": ["string", "null"]},
            "category": {"type": ["string", "null"]},
            "additivity": {"type": ["string", "null"]},
            "contributor_count": {"type": "integer", "minimum": 0},
            "value_state": {"enum": VALUE_STATES + [None]},
            "value": NULLABLE_DECIMAL,
            "displayed_value": NULLABLE_TEXT,
            "reason_code": NULLABLE_TEXT,
        },
        ["category", "value_state", "value", "displayed_value"],
    )
    # A value is the stored decimal string; the display is derived from it once. A value that is not
    # PRESENT carries no value and no display, never zero.
    schemas["DashboardValue"] = closed(
        {
            "mode": {"enum": ["OFFICIAL", "PROVISIONAL"]},
            "result_id": UUID,
            "result_revision": UUID,
            "value_state": {"enum": VALUE_STATES},
            "value": NULLABLE_DECIMAL,
            "displayed_value": NULLABLE_TEXT,
            "numerator": NULLABLE_DECIMAL,
            "denominator": NULLABLE_DECIMAL,
            "reason_code": NULLABLE_TEXT,
            "calculated_at": NULLABLE_TEXT,
            "disaggregation": {"type": "array", "maxItems": 500, "items": category},
        },
        ["mode", "result_id", "result_revision", "value_state", "value", "displayed_value", "disaggregation"],
    )
    value = {"oneOf": [{"type": "null"}, {"$ref": "#/components/schemas/DashboardValue"}]}
    schemas["DashboardTarget"] = closed(
        {
            "target_id": UUID,
            "revision_id": UUID,
            "target_kind": {"type": "string"},
            "target_basis": {"type": "string"},
            "direction": {"type": "string"},
            "value_state": {"enum": VALUE_STATES},
            "value": NULLABLE_DECIMAL,
            "low": NULLABLE_DECIMAL,
            "high": NULLABLE_DECIMAL,
            "binding_version": {"type": ["integer", "null"], "minimum": 1},
            "displayed_value": NULLABLE_TEXT,
            "displayed_low": NULLABLE_TEXT,
            "displayed_high": NULLABLE_TEXT,
        },
        ["target_id", "revision_id", "target_kind", "target_basis", "direction", "value_state", "value"],
    )
    target = {"oneOf": [{"type": "null"}, {"$ref": "#/components/schemas/DashboardTarget"}]}
    status = {
        "oneOf": [
            {"type": "null"},
            closed(
                {
                    "status": {"type": "string"},
                    "attainment_percent": {"type": ["string", "null"]},
                    "deviation": NULLABLE_DECIMAL,
                    "displayed_deviation": NULLABLE_TEXT,
                    "reason_code": NULLABLE_TEXT,
                    "compared_with": {"enum": ["OFFICIAL", "PROVISIONAL", None]},
                },
                ["status", "attainment_percent", "deviation", "reason_code", "compared_with"],
            ),
        ]
    }
    counts = {
        k: NULLABLE_COUNT
        for k in [
            "expected_count",
            "required_count",
            "received_count",
            "approved_count",
            "pending_count",
            "missing_count",
            "excluded_count",
            "excepted_count",
            "overdue_count",
        ]
    }
    schemas["DashboardCoverage"] = closed(
        {
            "source": {"enum": ["CLOSE_SNAPSHOT", "COLLECTION_PLAN"]},
            "plan_revision": NULLABLE_UUID,
            **counts,
            "applicability": {"enum": ["APPLICABLE", "NOT_APPLICABLE", "UNAVAILABLE"]},
            "approval_percent": {"type": ["string", "null"], "pattern": r"^[0-9]{1,3}\.[0-9]{2}$"},
            "complete": {"type": "boolean"},
            "reason_code": NULLABLE_TEXT,
        },
        ["source", "applicability", "approval_percent", "expected_count", "required_count", "reason_code"],
    )
    schemas["DashboardFreshness"] = closed(
        {
            "stale": {"type": ["boolean", "null"]},
            "stale_reasons": {
                "type": "array",
                "items": {
                    "enum": [
                        "SOURCES_CHANGED_SINCE_CLOSE",
                        "PLAN_CHANGED_SINCE_CLOSE",
                        "SOURCES_CHANGED_SINCE_CALCULATION",
                        "PLAN_CHANGED_SINCE_CALCULATION",
                        "RECALCULATION_PENDING",
                        "PROVISIONAL_NEWER_THAN_OFFICIAL",
                    ]
                },
            },
            "source_check": {"enum": ["CHECKED", "NOT_PERMITTED", "NO_VALUE"]},
            "snapshot_id": NULLABLE_UUID,
            "snapshot_version": {"type": ["integer", "null"], "minimum": 1},
            "locked_at": NULLABLE_TEXT,
            "official_calculated_at": NULLABLE_TEXT,
            "provisional_calculated_at": NULLABLE_TEXT,
            "last_source_change_at": NULLABLE_TEXT,
            "checked_at": {"type": "string"},
        },
        ["stale", "stale_reasons", "source_check", "checked_at"],
    )
    head = {
        "indicator_id": UUID,
        "indicator_label": {"type": "string", "maxLength": 2000},
        "definition_revision": NULLABLE_UUID,
        "unit": {"type": ["string", "null"]},
        "measurement_type": {"type": ["string", "null"]},
        "combination_rule": {"type": ["string", "null"]},
        "display_decimals": {"type": "integer", "minimum": 0, "maximum": 6},
        "lifecycle_state": {"type": ["string", "null"]},
    }
    cell = {"official": value, "provisional": value, "target": target, "baseline": target, "status": status}
    period = {
        "period_id": UUID,
        "period_code": {"type": ["string", "null"]},
        "starts_at": NULLABLE_TEXT,
        "ends_at": NULLABLE_TEXT,
        "period_state": {"enum": ["Open", "Locked", "RestatementOpen"]},
    }
    card = closed(
        {
            **deepcopy(head),
            **deepcopy(cell),
            "coverage": {"$ref": "#/components/schemas/DashboardCoverage"},
            "freshness": {"$ref": "#/components/schemas/DashboardFreshness"},
        },
        ["indicator_id", "official", "provisional", "target", "baseline", "status", "coverage", "freshness"],
    )
    schemas["ProgrammeDashboard"] = closed(
        {
            "programme_id": UUID,
            "programme_title": {"type": ["string", "null"]},
            "period": closed(deepcopy(period), ["period_id", "period_state"]),
            "snapshot": {
                "oneOf": [
                    {"type": "null"},
                    closed(
                        {
                            "snapshot_id": UUID,
                            "snapshot_version": {"type": "integer", "minimum": 1},
                            "locked_at": NULLABLE_TEXT,
                        },
                        ["snapshot_id", "snapshot_version"],
                    ),
                ]
            },
            "stale_rule": {"type": "string"},
            # One page of at most 100 indicators; no total is given.
            "indicators": {"type": "array", "maxItems": 100, "items": card},
            "next_cursor": {"type": ["string", "null"], "maxLength": 4096},
        },
        ["programme_id", "period", "snapshot", "stale_rule", "indicators", "next_cursor"],
    )
    point = closed(
        {
            **deepcopy(period),
            "snapshot_version": {"type": ["integer", "null"], "minimum": 1},
            "locked_at": NULLABLE_TEXT,
            **deepcopy(cell),
        },
        ["period_id", "period_state", "official", "provisional", "target", "baseline", "status"],
    )
    schemas["IndicatorDashboardSeries"] = closed(
        {
            **deepcopy(head),
            "programme_id": UUID,
            # One page of at most 100 periods in calendar order; no total is given.
            "points": {"type": "array", "maxItems": 100, "items": point},
            "next_cursor": {"type": ["string", "null"], "maxLength": 4096},
        },
        ["indicator_id", "programme_id", "points", "next_cursor"],
    )

    page = [
        {
            "name": "limit",
            "in": "query",
            "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50},
        },
        {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
    ]
    for route, (op, cap, schema) in SPECIAL_READS.items():
        base = route.split("/")[0]
        template = deepcopy(paths[prefix + base + "/{object_id}"])
        entry = template["get"]
        entry.pop("parameters", None)
        entry["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + schema
        }
        entry.update(
            operationId=op,
            summary=op.replace("_", " "),
            **{"x-capability": cap, "x-contract-version": VERSION},
        )
        entry["parameters"] = deepcopy(page) + (
            [{"name": "period_id", "in": "query", "required": True, "schema": UUID}]
            if op == "programme_dashboard"
            else []
        )
        paths[prefix + route] = {"parameters": template["parameters"], "get": entry}
        policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": "GET",
                "path": prefix + route,
                "capability": cap,
                "role_templates": ROLES,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )
