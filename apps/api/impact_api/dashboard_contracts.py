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
    # v0.27: drill-down to the source observations behind a card; portfolio across programmes.
    "indicator-instances/{object_id}/dashboard-sources": (
        "indicator_dashboard_sources",
        "dashboards.read",
        "IndicatorDashboardSources",
    ),
    "indicator-definitions/{object_id}/portfolio": (
        "indicator_definition_portfolio",
        "dashboards.read",
        "IndicatorPortfolio",
    ),
}
PERIOD_REQUIRED = {"programme_dashboard", "indicator_dashboard_sources", "indicator_definition_portfolio"}
# Per-operation contract tag; the integrator aligns it with the build's API version.
VERSION = "1.19.0"
ROLES = ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST", "DATA_STEWARD", "EXTERNAL"]
IMPLEMENTED = {
    ("get", "dashboards/{object_id}/preview"),
    ("post", "dashboards/{object_id}/actions/copy"),
    ("post", "dashboards/{object_id}/pivot-preview"),
    ("post", "dashboards/{object_id}/actions/run-pivot"),
    ("get", "dashboards/{object_id}/pivot-jobs/{job_id}"),
    ("post", "dashboards/{object_id}/pivot-jobs/{job_id}/actions/cancel"),
    ("get", "dashboards/{object_id}/geographic-preview"),
}


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"

    binding = closed(
        {
            "resource_type": {"enum": ["CALCULATED_RESULT", "EVIDENCE"]},
            "object_id": UUID,
            "revision_id": UUID,
        },
        ["resource_type", "object_id", "revision_id"],
    )
    disclosure = closed(
        {
            "classification": {"enum": ["PUBLIC", "INTERNAL", "CONFIDENTIAL"]},
            "quality_context_required": {"const": True},
        },
        ["classification", "quality_context_required"],
    )
    geographic_config = closed(
        {
            "dimension": {"type": "string", "minLength": 1, "maxLength": 64},
            "boundary_version": UUID,
            "layer": {"enum": ["AUTHORISED_POINT_REFERENCE", "AGGREGATE"]},
            "granularity": {"enum": ["COUNTRY", "REGION", "DISTRICT", "POINT"]},
            "legend": {"type": "string", "minLength": 1, "maxLength": 200},
            "missingness": {"enum": ["SHOW_MISSING", "EXCLUDE_WITH_COUNT", "EXCLUDE_WITHOUT_COUNT"]},
            "external_map": {"type": "boolean"},
        },
        ["dimension", "boundary_version", "layer", "granularity", "legend", "missingness", "external_map"],
    )
    widget = closed(
        {
            "widget_id": UUID,
            "type": {"enum": ["METRIC", "TABLE", "TREND", "TARGET", "NARRATIVE", "EVIDENCE", "MAP"]},
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "binding": binding,
            "view_mode": {"enum": ["OFFICIAL", "PROVISIONAL"]},
            "period_id": UUID,
            "dimensions": {
                "type": "array",
                "maxItems": 5,
                "uniqueItems": True,
                "items": {"type": "string", "minLength": 1, "maxLength": 64},
            },
            "disclosure_context": disclosure,
            "position": {"type": "integer", "minimum": 0, "maximum": 9},
            "width": {"type": "integer", "minimum": 1, "maximum": 12},
            "compatible_filters": {
                "type": "array",
                "uniqueItems": True,
                "maxItems": 6,
                "items": {"enum": ["programme", "period", "geography", "dimension", "indicator", "approval"]},
            },
            "drilldown_levels": {
                "type": "array",
                "uniqueItems": True,
                "maxItems": 3,
                "items": {"enum": ["PORTFOLIO", "PARTNER", "PROGRAMME"]},
            },
            "approved_slices": {
                "type": "array",
                "maxItems": 20,
                "items": closed(
                    {
                        "field": {
                            "enum": ["programme", "period", "geography", "dimension", "indicator", "approval"]
                        },
                        "value": {"type": "string", "minLength": 1, "maxLength": 200},
                        "binding": binding,
                    },
                    ["field", "value", "binding"],
                ),
            },
            "geographic_config": {"oneOf": [{"type": "null"}, geographic_config]},
        },
        [
            "widget_id",
            "type",
            "title",
            "binding",
            "view_mode",
            "period_id",
            "dimensions",
            "disclosure_context",
            "position",
            "width",
            "compatible_filters",
            "drilldown_levels",
            "approved_slices",
        ],
    )
    schemas["Widget"] = widget
    widget["allOf"] = [
        {
            "if": {"properties": {"type": {"const": "MAP"}}, "required": ["type"]},
            "then": {
                "required": ["geographic_config"],
                "properties": {"geographic_config": geographic_config},
            },
        }
    ]
    for name in ["DashboardData", "DashboardDraftData"]:
        schemas[name] = closed(
            {
                "title": {"type": "string", "minLength": 1, "maxLength": 200},
                "mode": {"const": "PRIVATE_DRAFT"},
                "widgets": {"type": "array", "minItems": 1, "maxItems": 10, "items": widget},
                "filters": schemas["FilterSet"],
            },
            ["title", "mode", "widgets", "filters"],
        )
    schemas["DashboardCopyData"] = closed({"title": {"type": "string", "minLength": 1, "maxLength": 200}}, [])
    schemas["DashboardCopy"] = closed(
        {"operation_id": UUID, "data": {"$ref": "#/components/schemas/DashboardCopyData"}},
        ["operation_id", "data"],
    )
    preview_widget = closed(
        {
            **deepcopy(widget["properties"]),
            "availability": {"enum": ["AVAILABLE", "UNAVAILABLE"]},
            "chart_values": {"type": "array", "maxItems": 100, "items": NULLABLE_DECIMAL},
            "table_rows": {"type": "array", "maxItems": 100, "items": {"type": "object"}},
            "quality_context": {"type": ["object", "null"]},
            "filter_effect": {"enum": ["NONE", "APPLIED", "NOT_APPLICABLE", "UNAVAILABLE"]},
            "non_applicable_filters": {"type": "array", "items": {"type": "string"}},
        },
        list(widget["required"])
        + [
            "availability",
            "chart_values",
            "table_rows",
            "quality_context",
            "filter_effect",
            "non_applicable_filters",
        ],
    )
    schemas["DashboardPreview"] = closed(
        {
            "dashboard_id": UUID,
            "dashboard_revision": UUID,
            "title": {"type": "string"},
            "mode": {"const": "PRIVATE_DRAFT"},
            "viewport": {"enum": ["DESKTOP", "MOBILE", "TABLE"]},
            "drill_level": {"enum": ["PORTFOLIO", "PARTNER", "PROGRAMME", None]},
            "current_filters": schemas["FilterSet"],
            "widgets": {"type": "array", "maxItems": 10, "items": preview_widget},
        },
        [
            "dashboard_id",
            "dashboard_revision",
            "title",
            "mode",
            "viewport",
            "drill_level",
            "current_filters",
            "widgets",
        ],
    )
    pivot_data = closed(
        {
            "widget_id": UUID,
            "row_dimension": {"type": "string", "minLength": 1, "maxLength": 64},
            "statistic": {"enum": ["DISTINCT_COUNT", "SUM", "MEAN"]},
        },
        ["widget_id", "row_dimension", "statistic"],
    )
    schemas["DashboardPivotData"] = pivot_data
    schemas["DashboardPivotRun"] = closed(
        {"operation_id": UUID, "data": {"$ref": "#/components/schemas/DashboardPivotData"}},
        ["operation_id", "data"],
    )
    schemas["DashboardPivotCancel"] = closed({"operation_id": UUID}, ["operation_id"])
    pivot_cell = closed(
        {
            "category": NULLABLE_TEXT,
            "value_state": {"enum": VALUE_STATES + [None]},
            "value": NULLABLE_DECIMAL,
            "displayed_value": NULLABLE_TEXT,
            "disclosure": {"enum": ["VISIBLE", "SUPPRESSED"]},
            "additivity": {"type": "string", "maxLength": 64},
        },
        ["category", "value_state", "value", "displayed_value", "disclosure", "additivity"],
    )
    schemas["DashboardPivotResult"] = closed(
        {
            "execution": {"enum": ["SYNC", "ASYNC_CANCELLABLE_JOB"]},
            "job_id": NULLABLE_UUID,
            "result_id": UUID,
            "result_revision": UUID,
            "statistic": {"enum": ["DISTINCT_COUNT", "SUM", "MEAN"]},
            "row_dimension": {"type": "string"},
            "estimated_cardinality": {"type": "integer", "minimum": 0},
            "cells": {"type": "array", "maxItems": 10000, "items": pivot_cell},
            "grand_total": NULLABLE_DECIMAL,
            "grand_total_basis": {"enum": ["ELIGIBLE_SOURCE_RESULT", "UNROUNDED_ELIGIBLE_VALUES"]},
            "cells_may_exceed_grand_total": {"type": "boolean"},
            "explanation": {"type": "string", "maxLength": 500},
        },
        [
            "execution",
            "job_id",
            "result_id",
            "result_revision",
            "statistic",
            "row_dimension",
            "estimated_cardinality",
            "cells",
            "grand_total",
            "grand_total_basis",
            "cells_may_exceed_grand_total",
            "explanation",
        ],
    )
    schemas["DashboardPivotJob"] = closed(
        {
            "job_id": UUID,
            "state": {
                "enum": [
                    "Requested",
                    "Validating",
                    "Queued",
                    "Running",
                    "Cancelling",
                    "Succeeded",
                    "SucceededWithIssues",
                    "Failed",
                    "Cancelled",
                ]
            },
            "cancellation_requested": {"type": "boolean"},
            "result": {"oneOf": [{"type": "null"}, {"$ref": "#/components/schemas/DashboardPivotResult"}]},
        },
        ["job_id", "state", "cancellation_requested", "result"],
    )
    geographic_row = closed(
        {
            "geography_key": {"type": ["string", "null"], "maxLength": 200},
            "value_state": {"enum": VALUE_STATES + [None]},
            "value": NULLABLE_DECIMAL,
            "displayed_value": NULLABLE_TEXT,
            "disclosure": {"enum": ["VISIBLE", "SUPPRESSED"]},
            "boundary_version": NULLABLE_UUID,
            "tooltip": closed(
                {
                    "label": {"type": ["string", "null"]},
                    "displayed_value": NULLABLE_TEXT,
                    "value_state": {"enum": VALUE_STATES + [None]},
                },
                ["label", "displayed_value", "value_state"],
            ),
        },
        [
            "geography_key",
            "value_state",
            "value",
            "displayed_value",
            "disclosure",
            "boundary_version",
            "tooltip",
        ],
    )
    schemas["DashboardGeographicPreview"] = closed(
        {
            "dashboard_id": UUID,
            "dashboard_revision": UUID,
            "widget_id": UUID,
            "period_id": UUID,
            "boundary_version": UUID,
            "data_boundary_versions": {"type": "array", "uniqueItems": True, "items": UUID},
            "boundary_status": {"enum": ["MATCH", "MISMATCH", "UNVERSIONED"]},
            "layer": {"enum": ["AUTHORISED_POINT_REFERENCE", "AGGREGATE"]},
            "granularity": {"enum": ["COUNTRY", "REGION", "DISTRICT", "POINT"]},
            "legend": {"type": "string"},
            "missingness": {"enum": ["SHOW_MISSING", "EXCLUDE_WITH_COUNT", "EXCLUDE_WITHOUT_COUNT"]},
            "coordinate_delivery": {"const": "NO_COORDINATES_IN_PLATFORM_PAYLOAD"},
            "map_request": {"type": "array", "maxItems": 1000, "items": geographic_row},
            "equivalent_table": {"type": "array", "maxItems": 1000, "items": geographic_row},
            "sortable_fields": {
                "type": "array",
                "items": {"enum": ["geography_key", "value", "value_state"]},
            },
            "missing_count": {"type": ["integer", "null"], "minimum": 0},
        },
        [
            "dashboard_id",
            "dashboard_revision",
            "widget_id",
            "period_id",
            "boundary_version",
            "data_boundary_versions",
            "boundary_status",
            "layer",
            "granularity",
            "legend",
            "missingness",
            "coordinate_delivery",
            "map_request",
            "equivalent_table",
            "sortable_fields",
            "missing_count",
        ],
    )

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
            "version_label": {"enum": ["Original target", "Revised target", "Baseline"]},
            "applicable_period": closed(
                {
                    "period_id": NULLABLE_UUID,
                    "period_code": NULLABLE_TEXT,
                    "starts_at": NULLABLE_TEXT,
                    "ends_at": NULLABLE_TEXT,
                },
                ["period_id", "period_code", "starts_at", "ends_at"],
            ),
            "time_semantic": NULLABLE_TEXT,
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
                    "direction": {"enum": ["HIGHER", "LOWER", "RANGE", "MILESTONE"]},
                    "deviation_formula": {"const": "actual - target"},
                    "attainment_formula": {"enum": ["actual / target × 100", "target / actual × 100"]},
                    "baseline_change_formula": {
                        "const": "(actual - baseline) / baseline × 100; undefined when baseline is zero or negative"
                    },
                    "time_semantic": NULLABLE_TEXT,
                    "time_semantic_compatibility": {"enum": ["COMPATIBLE", "BLOCKED"]},
                    "change_from_baseline": NULLABLE_DECIMAL,
                    "change_from_baseline_percent": {"type": ["string", "null"]},
                    "change_from_baseline_reason": NULLABLE_TEXT,
                },
                [
                    "status",
                    "attainment_percent",
                    "deviation",
                    "reason_code",
                    "compared_with",
                    "direction",
                    "deviation_formula",
                    "attainment_formula",
                    "baseline_change_formula",
                    "time_semantic",
                    "time_semantic_compatibility",
                    "change_from_baseline",
                    "change_from_baseline_percent",
                    "change_from_baseline_reason",
                ],
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
            "data_state": {"enum": ["LIVE_APPROVED", "PROVISIONAL", "SNAPSHOT", "UNAVAILABLE"]},
            "last_source_success_at": NULLABLE_TEXT,
            "approval_cutoff_at": NULLABLE_TEXT,
            "calculation_at": NULLABLE_TEXT,
            "last_valid_data_at": NULLABLE_TEXT,
            "dashboard_fetched_at": {"type": "string"},
            "freshness_basis": {"const": "SOURCE_AND_CALCULATION_STATE"},
            "checked_at": {"type": "string"},
        },
        [
            "stale",
            "stale_reasons",
            "source_check",
            "data_state",
            "last_source_success_at",
            "approval_cutoff_at",
            "calculation_at",
            "last_valid_data_at",
            "dashboard_fetched_at",
            "freshness_basis",
            "checked_at",
        ],
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

    # Drill-down (v0.27): the source observations behind the value a card shows, as the reader may
    # see them; `source_check` PARTIAL means rows are withheld, never how many.
    source = closed(
        {
            "observation_id": UUID,
            "revision_id": UUID,
            "source_namespace": {"type": ["string", "null"]},
            "source_key": {"type": ["string", "null"]},
            "event_at": NULLABLE_TEXT,
            "value_state": {"enum": VALUE_STATES + [None]},
            "value": NULLABLE_DECIMAL,
            "displayed_value": NULLABLE_TEXT,
            "numerator": NULLABLE_DECIMAL,
            "denominator": NULLABLE_DECIMAL,
            "approval_state": {"type": ["string", "null"]},
            "lifecycle_state": {"type": ["string", "null"]},
            "contribution": {"enum": ["INCLUDED", "EXCLUDED", "NOT_IN_RESULT", None]},
            "contribution_reason": NULLABLE_TEXT,
            "changed_since_calculation": {"type": "boolean"},
            "updated_at": NULLABLE_TEXT,
        },
        ["observation_id", "revision_id", "value_state", "value", "displayed_value", "contribution"],
    )
    schemas["IndicatorDashboardSources"] = closed(
        {
            **deepcopy(head),
            "programme_id": UUID,
            "period": closed(deepcopy(period), ["period_id", "period_state"]),
            "value": closed(
                {
                    "mode": {"enum": ["OFFICIAL", "PROVISIONAL", None]},
                    "result_id": NULLABLE_UUID,
                    "result_revision": NULLABLE_UUID,
                },
                ["mode", "result_id", "result_revision"],
            ),
            "source_check": {"enum": ["COMPLETE", "PARTIAL"]},
            "items": {"type": "array", "maxItems": 100, "items": source},
            "next_cursor": {"type": ["string", "null"], "maxLength": 4096},
        },
        ["indicator_id", "programme_id", "period", "value", "source_check", "items", "next_cursor"],
    )
    # Portfolio (v0.27): one definition across programmes; a pooled total only where the method
    # pools, from stored components, and only over a complete, fully official set.
    pooled_block = closed(
        {
            "method": {"type": ["string", "null"]},
            "value_state": {"enum": VALUE_STATES},
            "value": NULLABLE_DECIMAL,
            "displayed_value": NULLABLE_TEXT,
            "numerator": NULLABLE_DECIMAL,
            "denominator": NULLABLE_DECIMAL,
            "instance_count": {"type": "integer", "minimum": 0},
            "contributing_count": {"type": "integer", "minimum": 0},
            "reason_code": NULLABLE_TEXT,
        },
        [
            "method",
            "value_state",
            "value",
            "displayed_value",
            "instance_count",
            "contributing_count",
            "reason_code",
        ],
    )
    programme_row = closed(
        {
            **deepcopy(head),
            "programme_id": UUID,
            "programme_title": {"type": ["string", "null"]},
            "period_state": {"enum": ["Open", "Locked", "RestatementOpen"]},
            "snapshot_version": {"type": ["integer", "null"], "minimum": 1},
            "locked_at": NULLABLE_TEXT,
            "official": value,
            "coverage": {"$ref": "#/components/schemas/DashboardCoverage"},
        },
        ["indicator_id", "programme_id", "period_state", "official", "coverage"],
    )
    schemas["IndicatorPortfolio"] = closed(
        {
            "definition_id": UUID,
            "definition_name": {"type": ["string", "null"]},
            "unit": {"type": ["string", "null"]},
            "measurement_type": {"type": ["string", "null"]},
            "combination_rule": {"type": ["string", "null"]},
            "display_decimals": {"type": "integer", "minimum": 0, "maximum": 6},
            "period": closed(
                {k: v for k, v in deepcopy(period).items() if k != "period_state"}, ["period_id"]
            ),
            "scope": {"enum": ["COMPLETE", "PARTIAL"]},
            "comparison": closed(
                {
                    "coverage_threshold": {"type": "string", "pattern": DECIMAL},
                    "visible_scope": {"enum": ["ALL_AUTHORISED_MEMBERS", "PARTIAL_AUTHORISED_SCOPE"]},
                    "hidden_members_disclosed": {"const": False},
                    "raw_cross_group_ranking": {"const": "REFUSED"},
                    "groups": {
                        "type": "array",
                        "maxItems": 500,
                        "items": closed(
                            {
                                "compatibility_key": closed(
                                    {
                                        "definition_revision": NULLABLE_UUID,
                                        "period_id": UUID,
                                        "starts_at": NULLABLE_TEXT,
                                        "ends_at": NULLABLE_TEXT,
                                    },
                                    ["definition_revision", "period_id", "starts_at", "ends_at"],
                                ),
                                "compatible": {"type": "boolean"},
                                "mismatch_flags": {
                                    "type": "array",
                                    "maxItems": 8,
                                    "items": {"enum": ["DEFINITION_REVISION"]},
                                },
                                "ranking": closed(
                                    {
                                        "status": {"enum": ["QUALIFIED", "UNAVAILABLE"]},
                                        "method": {
                                            "const": "DESCENDING_OFFICIAL_VALUE_WITHIN_EXACT_DEFINITION_VERSION"
                                        },
                                        "unqualified_league_table": {"const": False},
                                        "review_status": {"const": "REQUIRED_FOR_UNQUALIFIED_RANKING"},
                                        "items": {
                                            "type": "array",
                                            "maxItems": 500,
                                            "items": closed(
                                                {
                                                    "indicator_id": UUID,
                                                    "programme_id": UUID,
                                                    "programme_title": NULLABLE_TEXT,
                                                    "displayed_value": NULLABLE_TEXT,
                                                    "denominator": NULLABLE_DECIMAL,
                                                    "rank": {"type": "integer", "minimum": 1},
                                                },
                                                [
                                                    "indicator_id",
                                                    "programme_id",
                                                    "programme_title",
                                                    "displayed_value",
                                                    "denominator",
                                                    "rank",
                                                ],
                                            ),
                                        },
                                        "excluded": {
                                            "type": "array",
                                            "maxItems": 500,
                                            "items": closed(
                                                {
                                                    "indicator_id": UUID,
                                                    "programme_id": UUID,
                                                    "programme_title": NULLABLE_TEXT,
                                                    "displayed_value": NULLABLE_TEXT,
                                                    "denominator": NULLABLE_DECIMAL,
                                                    "reason_code": {
                                                        "enum": [
                                                            "OFFICIAL_VALUE_UNAVAILABLE",
                                                            "BELOW_COVERAGE_THRESHOLD",
                                                            "VALUE_NOT_NUMERIC",
                                                        ]
                                                    },
                                                },
                                                [
                                                    "indicator_id",
                                                    "programme_id",
                                                    "programme_title",
                                                    "displayed_value",
                                                    "denominator",
                                                    "reason_code",
                                                ],
                                            ),
                                        },
                                    },
                                    [
                                        "status",
                                        "method",
                                        "unqualified_league_table",
                                        "review_status",
                                        "items",
                                        "excluded",
                                    ],
                                ),
                            },
                            ["compatibility_key", "compatible", "mismatch_flags", "ranking"],
                        ),
                    },
                },
                ["coverage_threshold", "visible_scope", "hidden_members_disclosed", "raw_cross_group_ranking", "groups"],
            ),
            "versions": {
                "type": "array",
                "maxItems": 500,
                "items": closed(
                    {
                        "definition_revision": NULLABLE_UUID,
                        "version_number": {"type": ["integer", "null"]},
                        "combination_rule": {"type": ["string", "null"]},
                        "instance_count": {"type": "integer", "minimum": 0},
                        "pooled": pooled_block,
                    },
                    ["definition_revision", "instance_count", "pooled"],
                ),
            },
            "programmes": {"type": "array", "maxItems": 100, "items": programme_row},
            "next_cursor": {"type": ["string", "null"], "maxLength": 4096},
        },
        ["definition_id", "period", "scope", "comparison", "versions", "programmes", "next_cursor"],
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
        entry["responses"]["200"]["content"]["application/json"]["schema"] = (
            {"$ref": "#/components/schemas/" + schema},
        )
        entry.update(
            operationId=op,
            summary=op.replace("_", " "),
            **{"x-capability": cap, "x-contract-version": VERSION},
        )
        entry["parameters"] = deepcopy(page) + (
            [{"name": "period_id", "in": "query", "required": True, "schema": UUID}]
            if op in PERIOD_REQUIRED
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

    dashboard_item = paths[prefix + "dashboards/{object_id}"]
    preview = deepcopy(dashboard_item["get"])
    preview.update(
        operationId="preview_dashboards",
        summary="Preview an authored dashboard",
        **{"x-capability": "dashboards.read", "x-contract-version": VERSION},
    )
    preview["parameters"] = [
        {
            "name": "viewport",
            "in": "query",
            "schema": {"enum": ["DESKTOP", "MOBILE", "TABLE"], "default": "DESKTOP"},
        },
        {
            "name": "drill_level",
            "in": "query",
            "schema": {"enum": ["PORTFOLIO", "PARTNER", "PROGRAMME"]},
        },
    ]
    preview["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPreview"
    }
    paths[prefix + "dashboards/{object_id}/preview"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": preview,
    }
    geographic_preview = deepcopy(preview)
    geographic_preview.update(
        operationId="preview_dashboard_geography",
        summary="Preview a disclosure-filtered geographic map and table",
        **{"x-capability": "dashboards.read", "x-contract-version": VERSION},
    )
    geographic_preview["parameters"] = [
        {"name": "widget_id", "in": "query", "required": True, "schema": UUID}
    ]
    geographic_preview["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardGeographicPreview"
    }
    paths[prefix + "dashboards/{object_id}/geographic-preview"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": geographic_preview,
    }
    copy_entry = deepcopy(paths[prefix + "dashboards"]["post"])
    copy_entry.update(
        operationId="action_dashboards_copy",
        summary="Copy a dashboard into a private draft",
        **{"x-capability": "dashboards.draft.create", "x-contract-version": VERSION},
    )
    copy_entry["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardCopy"
    }
    paths[prefix + "dashboards/{object_id}/actions/copy"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": copy_entry,
    }
    pivot_preview = deepcopy(copy_entry)
    pivot_preview.update(
        operationId="preview_dashboard_pivot",
        summary="Preview a governed dashboard pivot",
        **{"x-capability": "dashboards.read", "x-contract-version": VERSION},
    )
    pivot_preview["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPivotData"
    }
    pivot_preview["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPivotResult"
    }
    paths[prefix + "dashboards/{object_id}/pivot-preview"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": pivot_preview,
    }
    pivot_run = deepcopy(pivot_preview)
    pivot_run.update(operationId="action_dashboard_pivot_run", summary="Run a governed dashboard pivot")
    pivot_run["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPivotRun"
    }
    paths[prefix + "dashboards/{object_id}/actions/run-pivot"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": pivot_run,
    }
    job_parameters = deepcopy(dashboard_item["parameters"]) + [
        {"name": "job_id", "in": "path", "required": True, "schema": UUID}
    ]
    job_get = deepcopy(preview)
    job_get.update(operationId="read_dashboard_pivot_job", summary="Read a dashboard pivot job")
    job_get["parameters"] = []
    job_get["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPivotJob"
    }
    paths[prefix + "dashboards/{object_id}/pivot-jobs/{job_id}"] = {
        "parameters": job_parameters,
        "get": job_get,
    }
    job_cancel = deepcopy(job_get)
    job_cancel.update(operationId="cancel_dashboard_pivot_job", summary="Cancel a queued dashboard pivot")
    job_cancel["requestBody"] = deepcopy(copy_entry["requestBody"])
    job_cancel["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPivotCancel"
    }
    job_cancel["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPivotJob"
    }
    paths[prefix + "dashboards/{object_id}/pivot-jobs/{job_id}/actions/cancel"] = {
        "parameters": job_parameters,
        "post": job_cancel,
    }
    for op, method, path, cap, audit_event in [
        ("preview_dashboards", "GET", prefix + "dashboards/{object_id}/preview", "dashboards.read", False),
        (
            "preview_dashboard_geography",
            "GET",
            prefix + "dashboards/{object_id}/geographic-preview",
            "dashboards.read",
            False,
        ),
        (
            "action_dashboards_copy",
            "POST",
            prefix + "dashboards/{object_id}/actions/copy",
            "dashboards.draft.create",
            True,
        ),
        (
            "preview_dashboard_pivot",
            "POST",
            prefix + "dashboards/{object_id}/pivot-preview",
            "dashboards.read",
            False,
        ),
        (
            "action_dashboard_pivot_run",
            "POST",
            prefix + "dashboards/{object_id}/actions/run-pivot",
            "dashboards.read",
            True,
        ),
        (
            "read_dashboard_pivot_job",
            "GET",
            prefix + "dashboards/{object_id}/pivot-jobs/{job_id}",
            "dashboards.read",
            False,
        ),
        (
            "cancel_dashboard_pivot_job",
            "POST",
            prefix + "dashboards/{object_id}/pivot-jobs/{job_id}/actions/cancel",
            "dashboards.read",
            True,
        ),
    ]:
        policy["operations"] = [row for row in policy["operations"] if row["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method,
                "path": path,
                "capability": cap,
                "role_templates": ROLES,
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": audit_event,
            }
        )
