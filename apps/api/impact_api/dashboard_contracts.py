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
VERSION = "1.33.0"
ROLES = ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST", "DATA_STEWARD", "EXTERNAL"]
IMPLEMENTED = {
    ("get", "dashboards/{object_id}/preview"),
    ("post", "dashboards/{object_id}/actions/copy"),
    ("get", "dashboards/{object_id}/sharing-preview"),
    ("post", "dashboards/{object_id}/actions/publish"),
    ("get", "dashboards/{object_id}/publications/{publication_id}"),
    ("post", "dashboard-alert-rules"),
    ("get", "dashboard-alert-rules"),
    ("get", "dashboard-alert-rules/{object_id}"),
    ("get", "dashboard-alert-rules/{object_id}/incidents"),
    ("post", "dashboard-alert-rules/{object_id}/actions/evaluate"),
    ("post", "external-analytics-connections"),
    ("get", "external-analytics-connections"),
    ("get", "external-analytics-connections/{object_id}"),
    ("get", "external-analytics-connections/{object_id}/extracts"),
    ("post", "external-analytics-connections/{object_id}/actions/refresh"),
    ("post", "external-analytics-connections/{object_id}/actions/revoke"),
    ("post", "anomaly-runs"),
    ("get", "anomaly-runs"),
    ("get", "anomaly-runs/{object_id}"),
    ("get", "anomaly-findings"),
    ("get", "anomaly-findings/{object_id}"),
    ("post", "anomaly-findings/{object_id}/actions/review"),
    ("post", "evaluations"),
    ("get", "evaluations"),
    ("get", "evaluations/{object_id}"),
    ("get", "evaluations/{object_id}/stage-gates"),
    ("post", "evaluations/{object_id}/actions/stage-gate"),
    ("post", "evaluation-methodologies"),
    ("get", "evaluation-methodologies"),
    ("get", "evaluation-methodologies/{object_id}"),
    ("get", "evaluation-methodologies/{object_id}/history"),
    ("post", "evaluation-methodologies/{object_id}/actions/amend"),
    ("post", "evaluation-methodologies/{object_id}/actions/review"),
    ("post", "evaluation-methodologies/{object_id}/sample-export"),
    ("post", "analysis-packages"),
    ("get", "analysis-packages/{object_id}/export"),
    ("post", "analysis-packages/{object_id}/results"),
    ("post", "learning-questions"),
    ("post", "learning-questions/{object_id}/actions/close"),
    ("post", "learning-questions/{object_id}/actions/reopen"),
    ("get", "learning-questions/{object_id}/summary"),
    ("post", "learning-questions/{object_id}/actions/consider-context"),
    ("post", "evaluation-recommendations/{object_id}/response"),
    ("post", "management-actions/{object_id}/actions/complete"),
    ("post", "management-actions/{object_id}/actions/escalate-overdue"),
    ("post", "qualitative-codebooks"),
    ("post", "qualitative-assignments"),
    ("post", "qualitative-adjudications"),
    ("post", "qualitative-agreements"),
    ("post", "transcription-requests"),
    ("post", "transcript-corrections"),
    ("post", "quotation-references"),
    ("post", "findings"),
    ("post", "finding-revisions"),
    ("post", "finding-publications"),
    ("post", "budgets"),
    ("post", "budget-revisions"),
    ("post", "budget-approvals"),
    ("post", "expenditure-imports"),
    ("post", "finance-variance-views"),
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
    schemas["DashboardPublishData"] = closed(
        {
            "audience": {"enum": ["INTERNAL", "PUBLIC"]},
            "expires_at": {"type": "string", "format": "date-time"},
        },
        ["audience", "expires_at"],
    )
    schemas["DashboardPublish"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": {"$ref": "#/components/schemas/DashboardPublishData"},
        },
        ["operation_id", "expected_revision", "data"],
    )
    publication_binding = closed(
        {
            "widget_id": UUID,
            "binding": deepcopy(binding),
            "classification": {"type": ["string", "null"], "maxLength": 32},
            "availability": {"enum": ["AVAILABLE", "UNAVAILABLE"]},
        },
        ["widget_id", "binding", "classification", "availability"],
    )
    schemas["DashboardSharingPreview"] = closed(
        {
            "dashboard_id": UUID,
            "dashboard_revision": UUID,
            "recipient_id": UUID,
            "grants_created": {"const": False},
            "widgets": {"type": "array", "maxItems": 10, "items": publication_binding},
            "unavailable_binding_count": {"type": "integer", "minimum": 0, "maximum": 10},
        },
        [
            "dashboard_id",
            "dashboard_revision",
            "recipient_id",
            "grants_created",
            "widgets",
            "unavailable_binding_count",
        ],
    )
    schemas["DashboardPublicationStatus"] = closed(
        {
            "publication_id": UUID,
            "dashboard_id": UUID,
            "dashboard_revision": UUID,
            "audience": {"enum": ["INTERNAL", "PUBLIC"]},
            "expires_at": {"type": "string", "format": "date-time"},
            "status": {"enum": ["ACTIVE", "SUSPENDED"]},
            "reason_code": {"enum": [None, "EXPIRED", "SOURCE_AUTHORITY_OR_SENSITIVITY_CHANGED"]},
        },
        [
            "publication_id",
            "dashboard_id",
            "dashboard_revision",
            "audience",
            "expires_at",
            "status",
            "reason_code",
        ],
    )
    alert_rule_data = closed(
        {
            "measure_id": UUID,
            "operator": {"enum": ["LT", "GT"]},
            "threshold": {"type": "string", "pattern": DECIMAL},
            "minimum_coverage": {"type": "integer", "minimum": 0, "maximum": 100},
            "max_freshness_seconds": {"type": "integer", "minimum": 60, "maximum": 31536000},
            "evaluation_cadence": {"enum": ["DAILY", "WEEKLY", "MONTHLY"]},
            "recipient_ids": {
                "type": "array",
                "minItems": 1,
                "maxItems": 50,
                "uniqueItems": True,
                "items": deepcopy(UUID),
            },
            "cooldown_seconds": {"type": "integer", "minimum": 60, "maximum": 2592000},
        },
        [
            "measure_id",
            "operator",
            "threshold",
            "minimum_coverage",
            "max_freshness_seconds",
            "evaluation_cadence",
            "recipient_ids",
            "cooldown_seconds",
        ],
    )
    schemas["DashboardAlertRuleCreate"] = closed(
        {"operation_id": UUID, "data": alert_rule_data}, ["operation_id", "data"]
    )
    schemas["DashboardAlertEvaluate"] = closed(
        {
            "operation_id": UUID,
            "data": closed({"period_id": UUID, "result_id": NULLABLE_UUID}, ["period_id"]),
        },
        ["operation_id", "data"],
    )
    schemas["DashboardAlertOutcome"] = closed(
        {
            "rule_id": UUID,
            "outcome": {"enum": ["MISSINGNESS", "STALE_INPUT", "THRESHOLD", "NO_TRIGGER"]},
            "reason_code": {"type": "string", "maxLength": 64},
            "incident_id": NULLABLE_UUID,
            "result_revision": NULLABLE_UUID,
            "evaluation_period_id": UUID,
            "occurrence_count": {"type": "integer", "minimum": 0},
            "coalesced": {"type": "boolean"},
        },
        [
            "rule_id",
            "outcome",
            "reason_code",
            "incident_id",
            "result_revision",
            "evaluation_period_id",
            "occurrence_count",
            "coalesced",
        ],
    )
    alert_rule_view_data = deepcopy(alert_rule_data)
    alert_rule_view_data["properties"].update(
        {
            "next_evaluation_at": {"type": "string", "format": "date-time"},
            "last_evaluated_at": {"type": "string", "format": "date-time"},
            "last_period_id": UUID,
        }
    )
    alert_rule_view_data["required"].append("next_evaluation_at")
    resource_base = {
        "object_id": UUID,
        "tenant_id": UUID,
        "revision_id": UUID,
        "schema_version": {"type": "string"},
        "lifecycle_state": {"type": "string"},
        "classification": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "created_by": UUID,
        "updated_at": {"type": "string", "format": "date-time"},
        "updated_by": UUID,
    }
    resource_required = list(resource_base)
    schemas["DashboardAlertRule"] = closed(
        {**resource_base, "owner_id": UUID, "data": alert_rule_view_data},
        resource_required + ["data"],
    )
    schemas["DashboardAlertRuleList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/DashboardAlertRule"},
            },
            "next_cursor": {"type": ["string", "null"], "maxLength": 4096},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    alert_incident_data = closed(
        {
            "rule_id": UUID,
            "alert_type": {"enum": ["MISSINGNESS", "STALE_INPUT", "THRESHOLD"]},
            "reason_code": {"type": "string", "maxLength": 64},
            "result_id": NULLABLE_UUID,
            "result_revision": NULLABLE_UUID,
            "evaluation_period_id": UUID,
            "recipient_ids": {"type": "array", "maxItems": 50, "items": UUID},
            "occurrence_count": {"type": "integer", "minimum": 1},
            "last_evaluated_at": {"type": "string", "format": "date-time"},
        },
        [
            "rule_id",
            "alert_type",
            "reason_code",
            "result_id",
            "result_revision",
            "evaluation_period_id",
            "recipient_ids",
            "occurrence_count",
            "last_evaluated_at",
        ],
    )
    schemas["DashboardAlertIncident"] = closed(
        {**resource_base, "owner_id": UUID, "data": alert_incident_data}, resource_required + ["data"]
    )
    schemas["DashboardAlertIncidentList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/DashboardAlertIncident"},
            },
            "next_cursor": {"type": ["string", "null"], "maxLength": 4096},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    external_dataset = closed(
        {
            "kind": {"enum": ["CalculatedResult", "Evidence"]},
            "object_id": UUID,
            "revision_id": UUID,
            "fields": {
                "type": "array",
                "minItems": 1,
                "maxItems": 12,
                "uniqueItems": True,
                "items": {"type": "string", "minLength": 1, "maxLength": 64},
            },
        },
        ["kind", "object_id", "revision_id", "fields"],
    )
    schemas["ExternalAnalyticsConnectionCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "datasets": {"type": "array", "minItems": 1, "maxItems": 50, "items": external_dataset},
                    "destination": {"type": "string", "minLength": 1, "maxLength": 500},
                    "reuse_terms": {"type": "string", "minLength": 1, "maxLength": 2000},
                    "backup_owner_id": UUID,
                    "expires_at": {"type": "string", "format": "date-time"},
                },
                ["datasets", "destination", "reuse_terms", "backup_owner_id", "expires_at"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["ExternalAnalyticsRefresh"] = closed(
        {
            "operation_id": UUID,
            "credential": {"type": "string", "minLength": 32, "maxLength": 200},
        },
        ["operation_id", "credential"],
    )
    schemas["ExternalAnalyticsRevoke"] = closed({"operation_id": UUID}, ["operation_id"])
    receipt_properties = deepcopy(schemas["Receipt"]["properties"])
    schemas["ExternalAnalyticsConnectionReceipt"] = closed(
        {
            **receipt_properties,
            "service_identity_id": {"type": "string", "minLength": 32, "maxLength": 64},
            "credential": {"type": "string", "minLength": 32, "maxLength": 200},
        },
        list(schemas["Receipt"]["required"]) + ["service_identity_id", "credential"],
    )
    external_package_item = closed(
        {
            "object_id": UUID,
            "revision_id": UUID,
            "kind": {"enum": ["CalculatedResult", "Evidence"]},
            "fields": {"type": "object", "additionalProperties": True, "maxProperties": 12},
            "definition_revision": NULLABLE_UUID,
            "definition": {
                "oneOf": [
                    {"type": "null"},
                    closed(
                        {
                            "name": NULLABLE_TEXT,
                            "unit": NULLABLE_TEXT,
                            "measurement_type": NULLABLE_TEXT,
                        },
                        ["name", "unit", "measurement_type"],
                    ),
                ]
            },
            "unit": NULLABLE_TEXT,
            "value_state": {"enum": VALUE_STATES + [None]},
            "freshness": {"type": ["object", "null"]},
        },
        [
            "object_id",
            "revision_id",
            "kind",
            "fields",
            "definition_revision",
            "definition",
            "unit",
            "value_state",
            "freshness",
        ],
    )
    schemas["ExternalAnalyticsExtract"] = closed(
        {
            "connection_id": UUID,
            "extract_id": UUID,
            "extracted_at": {"type": "string", "format": "date-time"},
            "package": {"type": "array", "maxItems": 50, "items": external_package_item},
        },
        ["connection_id", "extract_id", "extracted_at", "package"],
    )
    schemas["ExternalAnalyticsRevocation"] = closed(
        {
            **receipt_properties,
            "last_successful_extract": {"type": ["object", "null"]},
            "remote_copy_status": {"const": "TRACKED_NOT_REMOTELY_ERASED"},
        },
        list(schemas["Receipt"]["required"]) + ["last_successful_extract", "remote_copy_status"],
    )
    schemas["ExternalAnalyticsConnection"] = closed(
        {**resource_base, "owner_id": UUID, "data": {"type": "object", "additionalProperties": True}},
        resource_required + ["data"],
    )
    schemas["ExternalAnalyticsConnectionList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/ExternalAnalyticsConnection"},
            },
            "next_cursor": {"type": ["string", "null"]},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    schemas["ExternalAnalyticsExtractRecord"] = closed(
        {**resource_base, "owner_id": UUID, "data": {"type": "object", "additionalProperties": True}},
        resource_required + ["data"],
    )
    schemas["ExternalAnalyticsExtractList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/ExternalAnalyticsExtractRecord"},
            },
            "next_cursor": {"type": ["string", "null"]},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    eligible_observation = closed({"object_id": UUID, "revision_id": UUID}, ["object_id", "revision_id"])
    schemas["AnomalyRunCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "method_version": {"const": "ROBUST_MAD_1"},
                    "eligible_observations": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 100,
                        "items": eligible_observation,
                    },
                    "comparison_window": closed(
                        {
                            "starts_at": {"type": "string", "format": "date-time"},
                            "ends_at": {"type": "string", "format": "date-time"},
                        },
                        ["starts_at", "ends_at"],
                    ),
                    "owner_id": UUID,
                },
                [
                    "method_version",
                    "eligible_observations",
                    "comparison_window",
                    "owner_id",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["AnomalyFindingReview"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "decision": {"enum": ["CONFIRMED", "DISMISSED", "DEFERRED"]},
                    "reason_code": {
                        "type": ["string", "null"],
                        "enum": [
                            "EXPECTED_SEASONALITY",
                            "KNOWN_EVENT",
                            "DATA_CORRECT",
                            "INSUFFICIENT_CONTEXT",
                            "OTHER",
                            None,
                        ],
                    },
                },
                ["decision"],
            ),
        },
        ["operation_id", "data"],
    )
    anomaly_finding = closed(
        {
            "finding_id": UUID,
            "observation_id": UUID,
            "observation_revision": UUID,
            "source_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "method_version": {"const": "ROBUST_MAD_1"},
            "state": {"const": "SUGGESTED"},
            "severity": {"const": "REVIEW"},
            "owner_id": UUID,
            "explanation": {"type": "string", "maxLength": 1000},
            "method_output": closed(
                {
                    "median": {"type": "string", "pattern": DECIMAL},
                    "mad": {"type": "string", "pattern": DECIMAL},
                    "score": {"type": "string", "pattern": DECIMAL},
                },
                ["median", "mad", "score"],
            ),
            "review": {"type": "null"},
        },
        [
            "finding_id",
            "observation_id",
            "observation_revision",
            "source_hash",
            "method_version",
            "state",
            "severity",
            "owner_id",
            "explanation",
            "method_output",
            "review",
        ],
    )
    schemas["AnomalyRunOutcome"] = closed(
        {
            "run_id": UUID,
            "run_revision": UUID,
            "method_version": {"const": "ROBUST_MAD_1"},
            "eligible_revision_count": {"type": "integer", "minimum": 0, "maximum": 100},
            "findings": {"type": "array", "maxItems": 1, "items": anomaly_finding},
            "source_mutation": {"const": False},
            "person_fraud_label": {"const": False},
        },
        [
            "run_id",
            "run_revision",
            "method_version",
            "eligible_revision_count",
            "findings",
            "source_mutation",
            "person_fraud_label",
        ],
    )
    schemas["AnomalyReviewOutcome"] = closed(
        {
            **receipt_properties,
            "decision": {"enum": ["CONFIRMED", "DISMISSED", "DEFERRED"]},
            "confirmed_quality_defect": {"type": "boolean"},
            "source_mutation": {"const": False},
        },
        list(schemas["Receipt"]["required"]) + ["decision", "confirmed_quality_defect", "source_mutation"],
    )
    schemas["AnomalyResource"] = closed(
        {**resource_base, "owner_id": UUID, "data": {"type": "object", "additionalProperties": True}},
        resource_required + ["data"],
    )
    schemas["AnomalyResourceList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AnomalyResource"},
            },
            "next_cursor": {"type": ["string", "null"]},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    document_kind = {
        "enum": [
            "METHODOLOGY",
            "ETHICS",
            "SAFEGUARDING",
            "ANALYSIS_PLAN",
            "DISCLOSURE_REVIEW",
        ]
    }
    schemas["EvaluationRegistrationCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "title": {"type": "string", "minLength": 1, "maxLength": 200},
                    "study_type": {"enum": ["BASELINE", "MIDLINE", "ENDLINE", "OTHER"]},
                    "programme_id": UUID,
                    "period_id": UUID,
                    "questions": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 50,
                        "items": {"type": "string", "minLength": 1, "maxLength": 1000},
                    },
                    "study_design": {"type": "string", "minLength": 1, "maxLength": 4000},
                    "programme_baseline_id": NULLABLE_UUID,
                    "evaluator": {"type": "string", "minLength": 1, "maxLength": 500},
                    "independence": closed(
                        {
                            "claimed": {"type": "boolean"},
                            "basis": {
                                "enum": [
                                    None,
                                    "EXTERNAL_EVALUATOR",
                                    "INDEPENDENT_COMMITTEE",
                                    "CONTRACTUAL_SEPARATION",
                                ]
                            },
                            "evidence_object_id": NULLABLE_UUID,
                            "evidence_revision_id": NULLABLE_UUID,
                        },
                        ["claimed"],
                    ),
                    "ethics_requirements": {
                        "type": "array",
                        "maxItems": 30,
                        "items": {"type": "string", "maxLength": 500},
                    },
                    "budget": closed(
                        {
                            "amount": {
                                "type": "string",
                                "pattern": r"^(0*[1-9][0-9]{0,25})(\.[0-9]{1,12})?$",
                            },
                            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
                        },
                        ["amount", "currency"],
                    ),
                    "deliverables": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 50,
                        "items": {"type": "string", "maxLength": 500},
                    },
                    "required_documents": closed(
                        {
                            "FIELD_COLLECTION": {
                                "type": "array",
                                "uniqueItems": True,
                                "items": document_kind,
                            },
                            "PUBLICATION": {
                                "type": "array",
                                "uniqueItems": True,
                                "items": document_kind,
                            },
                        },
                        ["FIELD_COLLECTION", "PUBLICATION"],
                    ),
                    "sensitive_processing": {"type": "boolean"},
                },
                [
                    "title",
                    "study_type",
                    "programme_id",
                    "period_id",
                    "questions",
                    "study_design",
                    "evaluator",
                    "independence",
                    "ethics_requirements",
                    "budget",
                    "deliverables",
                    "required_documents",
                    "sensitive_processing",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["EvaluationStageGate"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": closed(
                {
                    "stage": {"enum": ["FIELD_COLLECTION", "PUBLICATION"]},
                    "documents": {
                        "type": "array",
                        "maxItems": 20,
                        "items": closed(
                            {"kind": document_kind, "object_id": UUID, "revision_id": UUID},
                            ["kind", "object_id", "revision_id"],
                        ),
                    },
                },
                ["stage", "documents"],
            ),
        },
        ["operation_id", "expected_revision", "data"],
    )
    schemas["EvaluationStageGateOutcome"] = closed(
        {
            "evaluation_id": UUID,
            "stage": {"enum": ["FIELD_COLLECTION", "PUBLICATION"]},
            "status": {"enum": ["PASSED", "BLOCKED"]},
            "missing_document_kinds": {
                "type": "array",
                "uniqueItems": True,
                "items": document_kind,
            },
            "pinned_documents": {
                "type": "array",
                "maxItems": 20,
                "items": closed(
                    {"kind": document_kind, "object_id": UUID, "revision_id": UUID},
                    ["kind", "object_id", "revision_id"],
                ),
            },
            "sensitive_processing_approved": {"type": "boolean"},
        },
        [
            "evaluation_id",
            "stage",
            "status",
            "missing_document_kinds",
            "pinned_documents",
            "sensitive_processing_approved",
        ],
    )
    schemas["EvaluationRegistrationResource"] = closed(
        {
            **resource_base,
            "owner_id": UUID,
            "data": closed(
                {
                    **deepcopy(schemas["EvaluationRegistrationCreate"]["properties"]["data"]["properties"]),
                    "independence": closed(
                        {
                            "claimed": {"type": "boolean"},
                            "basis": {
                                "enum": [
                                    None,
                                    "EXTERNAL_EVALUATOR",
                                    "INDEPENDENT_COMMITTEE",
                                    "CONTRACTUAL_SEPARATION",
                                ]
                            },
                            "evidence_object_id": NULLABLE_UUID,
                            "evidence_revision_id": NULLABLE_UUID,
                            "verification": {"enum": ["NOT_CLAIMED", "EVIDENCE_ATTACHED_UNVERIFIED"]},
                        },
                        ["claimed", "verification"],
                    ),
                    "programme_revision_id": UUID,
                    "period_revision_id": UUID,
                    "sensitive_processing_approved": {"const": False},
                    "stage": {"enum": ["REGISTERED", "FIELD_COLLECTION", "PUBLICATION"]},
                    "last_gate": {"type": ["object", "null"]},
                },
                list(schemas["EvaluationRegistrationCreate"]["properties"]["data"]["required"])
                + ["programme_revision_id", "period_revision_id", "sensitive_processing_approved", "stage"],
            ),
        },
        resource_required + ["data"],
    )
    schemas["EvaluationRegistrationList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/EvaluationRegistrationResource"},
            },
            "next_cursor": {"type": ["string", "null"]},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    schemas["EvaluationStageGateHistory"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": closed(
                    {
                        "revision_id": UUID,
                        "revision_number": {"type": "integer", "minimum": 1},
                        "recorded_at": {"type": "string", "format": "date-time"},
                        "recorded_by": UUID,
                        "gate": {"$ref": "#/components/schemas/EvaluationStageGateOutcome"},
                    },
                    ["revision_id", "revision_number", "recorded_at", "recorded_by", "gate"],
                ),
            },
            "next_cursor": {"type": ["string", "null"]},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    stratum = closed(
        {
            "code": {"type": "string", "minLength": 1, "maxLength": 100},
            "eligible_count": {"type": "integer", "minimum": 0},
            "sampled_count": {"type": "integer", "minimum": 0},
            "weight": {"type": ["string", "null"], "pattern": r"^(0*[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"},
            "nonresponse_count": {"type": "integer", "minimum": 0},
        },
        ["code", "eligible_count", "sampled_count", "weight", "nonresponse_count"],
    )
    methodology_fields = {
        "sampling_frame": {"type": "string", "minLength": 1, "maxLength": 4000},
        "eligibility_rules": {"type": "string", "minLength": 1, "maxLength": 4000},
        "assignment_method": {"type": "string", "minLength": 1, "maxLength": 4000},
        "strata": {"type": "array", "minItems": 1, "maxItems": 100, "items": stratum},
        "nonresponse_rules": {"type": "string", "minLength": 1, "maxLength": 4000},
        "analysis_plan": {"type": "string", "minLength": 1, "maxLength": 8000},
        "expansion_method": {"enum": [None, "HORVITZ_THOMPSON", "POST_STRATIFIED_WEIGHTED_SUM"]},
    }
    schemas["EvaluationMethodologyCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {"evaluation_id": UUID, **methodology_fields},
                [
                    "evaluation_id",
                    "sampling_frame",
                    "eligibility_rules",
                    "assignment_method",
                    "strata",
                    "nonresponse_rules",
                    "analysis_plan",
                    "expansion_method",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["EvaluationMethodologyAmend"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": closed(
                {
                    "reason": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "relative_to_data_inspection": {"enum": ["BEFORE_INSPECTION", "AFTER_INSPECTION"]},
                    "changes": closed(methodology_fields, []),
                },
                ["reason", "relative_to_data_inspection", "changes"],
            ),
        },
        ["operation_id", "expected_revision", "data"],
    )
    schemas["EvaluationMethodologyReview"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": closed(
                {
                    "decision": {"enum": ["APPROVE", "REJECT"]},
                    "reason": {"type": "string", "minLength": 1, "maxLength": 1000},
                },
                ["decision", "reason"],
            ),
        },
        ["operation_id", "expected_revision", "data"],
    )
    schemas["EvaluationSampleExportRequest"] = closed(
        {
            "weighted": {"type": "boolean"},
            "population_estimate": {"type": "boolean"},
        },
        ["weighted", "population_estimate"],
    )
    schemas["EvaluationSampleExport"] = closed(
        {
            "methodology_revision": {"type": "string", "pattern": "^[1-9][0-9]*$"},
            "eligible_denominator": {"type": "integer", "minimum": 0},
            "sample_count": {"type": "integer", "minimum": 0},
            "sample_count_label": {"const": "SAMPLE_COUNT_NOT_ALL_BENEFICIARIES"},
            "weighted": {"type": "boolean"},
            "missing_weight_strata": {
                "type": "array",
                "items": {"type": "string", "maxLength": 100},
            },
            "expansion_method": methodology_fields["expansion_method"],
            "population_estimate": NULLABLE_DECIMAL,
            "strata": methodology_fields["strata"],
            "nonresponse_rules": methodology_fields["nonresponse_rules"],
        },
        [
            "methodology_revision",
            "eligible_denominator",
            "sample_count",
            "sample_count_label",
            "weighted",
            "missing_weight_strata",
            "expansion_method",
            "population_estimate",
            "strata",
            "nonresponse_rules",
        ],
    )
    methodology_data = closed(
        {
            "evaluation_id": UUID,
            **methodology_fields,
            "evaluation_revision": UUID,
            "methodology_revision": {"type": "string", "pattern": "^[1-9][0-9]*$"},
            "amendment": {"type": ["object", "null"]},
            "review_state": {"enum": ["PENDING", "REVIEWED", "REJECTED"]},
            "review": {"type": ["object", "null"]},
        },
        [
            "evaluation_id",
            *methodology_fields.keys(),
            "evaluation_revision",
            "methodology_revision",
            "review_state",
        ],
    )
    schemas["EvaluationMethodologyResource"] = closed(
        {**resource_base, "owner_id": UUID, "data": methodology_data}, resource_required + ["data"]
    )
    schemas["EvaluationMethodologyList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/EvaluationMethodologyResource"},
            },
            "next_cursor": {"type": ["string", "null"]},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    schemas["EvaluationMethodologyHistory"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": closed(
                    {
                        "revision_id": UUID,
                        "revision_number": {"type": "integer", "minimum": 1},
                        "recorded_at": {"type": "string", "format": "date-time"},
                        "recorded_by": UUID,
                        "data": methodology_data,
                    },
                    ["revision_id", "revision_number", "recorded_at", "recorded_by", "data"],
                ),
            },
            "next_cursor": {"type": ["string", "null"]},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    analysis_variable = {
        "enum": [
            "value_state",
            "value",
            "displayed_value",
            "numerator",
            "denominator",
            "event_at",
            "approval_state",
            "mode",
            "freshness",
            "indicator_id",
            "period_id",
        ]
    }
    schemas["AnalysisPackageCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "evaluation_id": UUID,
                    "methodology_id": UUID,
                    "methodology_revision": UUID,
                    "sources": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 500,
                        "items": closed(
                            {
                                "kind": {"enum": ["Observation", "CalculatedResult"]},
                                "object_id": UUID,
                                "revision_id": UUID,
                            },
                            ["kind", "object_id", "revision_id"],
                        ),
                    },
                    "variables": {
                        "type": "array",
                        "minItems": 1,
                        "uniqueItems": True,
                        "items": analysis_variable,
                    },
                    "filters": {
                        "type": "array",
                        "maxItems": 20,
                        "items": closed(
                            {
                                "field": analysis_variable,
                                "operator": {"enum": ["EQ", "IN", "GTE", "LTE"]},
                                "values": {
                                    "type": "array",
                                    "minItems": 1,
                                    "maxItems": 100,
                                    "items": {"type": ["string", "number", "boolean", "null"]},
                                },
                            },
                            ["field", "operator", "values"],
                        ),
                    },
                    "dictionary": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 50,
                        "items": closed(
                            {
                                "variable": analysis_variable,
                                "definition": {"type": "string", "minLength": 1, "maxLength": 1000},
                                "unit": NULLABLE_TEXT,
                            },
                            ["variable", "definition", "unit"],
                        ),
                    },
                    "reviewed_code_evidence": {
                        "type": "array",
                        "maxItems": 20,
                        "items": closed(
                            {"object_id": UUID, "revision_id": UUID},
                            ["object_id", "revision_id"],
                        ),
                    },
                },
                [
                    "evaluation_id",
                    "methodology_id",
                    "methodology_revision",
                    "sources",
                    "variables",
                    "filters",
                    "dictionary",
                    "reviewed_code_evidence",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["AnalysisPackageExport"] = closed(
        {
            "package_id": UUID,
            "package_revision": UUID,
            "integrity_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "content": {"type": "object"},
        },
        ["package_id", "package_revision", "integrity_sha256", "content"],
    )
    schemas["AnalysisResultRegister"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "title": {"type": "string", "minLength": 1, "maxLength": 200},
                    "result": {"type": "object", "maxProperties": 50},
                },
                ["title", "result"],
            ),
        },
        ["operation_id", "data"],
    )
    evidence_pin = closed({"object_id": UUID, "revision_id": UUID}, ["object_id", "revision_id"])
    schemas["LearningQuestionCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "decision_id": UUID,
                    "question": {"type": "string", "minLength": 1, "maxLength": 2000},
                    "context": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "evidence_gaps": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 20,
                        "items": {"type": "string", "minLength": 1, "maxLength": 1000},
                    },
                    "planned_inquiry": {"type": "string", "minLength": 1, "maxLength": 2000},
                    "owner_id": UUID,
                    "review_date": {"type": "string", "format": "date"},
                    "evidence": {"type": "array", "minItems": 3, "maxItems": 50, "items": evidence_pin},
                    "unresolved_assumptions": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 20,
                        "items": closed(
                            {
                                "assumption": {"type": "string", "minLength": 1, "maxLength": 1000},
                                "follow_up_study_required": {"const": True},
                            },
                            ["assumption", "follow_up_study_required"],
                        ),
                    },
                },
                [
                    "decision_id",
                    "question",
                    "context",
                    "evidence_gaps",
                    "planned_inquiry",
                    "owner_id",
                    "review_date",
                    "evidence",
                    "unresolved_assumptions",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["LearningQuestionClose"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": closed(
                {
                    "conclusion": {"type": "string", "minLength": 1, "maxLength": 4000},
                    "remaining_uncertainty": {"type": "string", "minLength": 1, "maxLength": 4000},
                },
                ["conclusion", "remaining_uncertainty"],
            ),
        },
        ["operation_id", "expected_revision", "data"],
    )
    schemas["LearningQuestionReopen"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": closed({"reason": {"type": "string", "minLength": 1, "maxLength": 2000}}, ["reason"]),
        },
        ["operation_id", "expected_revision", "data"],
    )
    schemas["LearningContextConsider"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": closed(
                {"target_context": {"type": "string", "minLength": 1, "maxLength": 1000}}, ["target_context"]
            ),
        },
        ["operation_id", "expected_revision", "data"],
    )
    schemas["LearningQuestionSummary"] = {"type": "object"}
    schemas["ManagementResponseCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "response": {"enum": ["ACCEPT", "PARTIALLY_ACCEPT", "REJECT"]},
                    "reason": {"type": "string", "minLength": 1, "maxLength": 2000},
                    "accepted_scope": NULLABLE_TEXT,
                    "owner_id": NULLABLE_UUID,
                    "due_date": {"type": ["string", "null"], "format": "date"},
                    "required_completion_evidence": {
                        "type": "array",
                        "maxItems": 20,
                        "items": {"type": "string", "minLength": 1, "maxLength": 500},
                    },
                },
                [
                    "response",
                    "reason",
                    "accepted_scope",
                    "owner_id",
                    "due_date",
                    "required_completion_evidence",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["ManagementActionComplete"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {"evidence": {"type": "array", "minItems": 1, "maxItems": 20, "items": evidence_pin}},
                ["evidence"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["ManagementActionEscalate"] = closed(
        {
            "operation_id": UUID,
            "data": closed({"reason": {"type": "string", "minLength": 1, "maxLength": 2000}}, ["reason"]),
        },
        ["operation_id", "data"],
    )
    code_id = {"type": "string", "pattern": "^[A-Z][A-Z0-9_-]{0,63}$"}
    schemas["QualitativeCodebookCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "version": {"type": "string", "minLength": 1},
                    "codes": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 500,
                        "items": closed(
                            {
                                "code_id": code_id,
                                "meaning": {"type": "string", "minLength": 1},
                                "inclusion_examples": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {"type": "string"},
                                },
                                "exclusion_examples": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {"type": "string"},
                                },
                            },
                            ["code_id", "meaning", "inclusion_examples", "exclusion_examples"],
                        ),
                    },
                },
                ["version", "codes"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["QualitativeAssignmentCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "source_type": {"enum": ["Evidence", "TranscriptArtifact"]},
                    "source_id": UUID,
                    "unit_id": {"type": "string", "minLength": 1},
                    "excerpt": {"type": "string", "minLength": 1},
                    "memo": NULLABLE_TEXT,
                    "codebook_id": UUID,
                    "codebook_revision": UUID,
                    "code_ids": {"type": "array", "minItems": 1, "uniqueItems": True, "items": code_id},
                },
                [
                    "source_type",
                    "source_id",
                    "unit_id",
                    "excerpt",
                    "memo",
                    "codebook_id",
                    "codebook_revision",
                    "code_ids",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["QualitativeAdjudicationCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "left_assignment_id": UUID,
                    "right_assignment_id": UUID,
                    "final_code_ids": {"type": "array", "minItems": 1, "items": code_id},
                    "rationale": {"type": "string", "minLength": 1},
                },
                ["left_assignment_id", "right_assignment_id", "final_code_ids", "rationale"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["QualitativeAgreementCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "pairs": {
                        "type": "array",
                        "minItems": 1,
                        "items": closed(
                            {"left_assignment_id": UUID, "right_assignment_id": UUID},
                            ["left_assignment_id", "right_assignment_id"],
                        ),
                    }
                },
                ["pairs"],
            ),
        },
        ["operation_id", "data"],
    )
    segment = closed(
        {
            "segment_id": {"type": "string", "minLength": 1},
            "start_ms": {"type": ["integer", "null"], "minimum": 0},
            "end_ms": {"type": ["integer", "null"], "minimum": 0},
            "speaker": NULLABLE_TEXT,
            "text": {"type": "string", "minLength": 1},
        },
        ["segment_id", "start_ms", "end_ms", "speaker", "text"],
    )
    schemas["TranscriptionRequest"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "recording_id": UUID,
                    "destination_id": UUID,
                    "language": {"type": "string", "minLength": 2},
                    "task": {"enum": ["TRANSCRIBE", "TRANSLATE"]},
                    "segments": {"type": "array", "minItems": 1, "items": segment},
                },
                ["recording_id", "destination_id", "language", "task", "segments"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["TranscriptCorrection"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "artifact_id": UUID,
                    "segment_id": {"type": "string", "minLength": 1},
                    "corrected_text": {"type": "string", "minLength": 1},
                },
                ["artifact_id", "segment_id", "corrected_text"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["QuotationReferenceCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "artifact_id": UUID,
                    "segment_id": {"type": "string", "minLength": 1},
                    "original_meaning_reviewed": {"type": "boolean"},
                },
                ["artifact_id", "segment_id", "original_meaning_reviewed"],
            ),
        },
        ["operation_id", "data"],
    )
    finding_pin = closed(
        {"object_type": {"type": "string", "minLength": 1}, "object_id": UUID, "revision_id": UUID},
        ["object_type", "object_id", "revision_id"],
    )
    schemas["FindingCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "statement": {"type": "string", "minLength": 1},
                    "method": {"type": "string", "minLength": 1},
                    "observation": {"type": "string", "minLength": 1},
                    "interpretation": {"type": "string", "minLength": 1},
                    "supporting_evidence": {"type": "array", "minItems": 1, "items": finding_pin},
                    "contradictory_evidence": {"type": "array", "items": finding_pin},
                    "confidence_rationale": {"type": "string", "minLength": 1},
                    "limitations": {"type": "array", "items": {"type": "string"}},
                    "reviewer_id": UUID,
                    "ai_confidence": {"type": ["number", "null"]},
                },
                [
                    "statement",
                    "method",
                    "observation",
                    "interpretation",
                    "supporting_evidence",
                    "contradictory_evidence",
                    "confidence_rationale",
                    "limitations",
                    "reviewer_id",
                    "ai_confidence",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["FindingRevise"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "finding_id": UUID,
                    "expected_revision": UUID,
                    "interpretation": {"type": "string", "minLength": 1},
                    "supporting_evidence": {"type": "array", "minItems": 1, "items": finding_pin},
                    "contradictory_evidence": {"type": "array", "items": finding_pin},
                },
                [
                    "finding_id",
                    "expected_revision",
                    "interpretation",
                    "supporting_evidence",
                    "contradictory_evidence",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["FindingPublish"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "finding_id": UUID,
                    "expected_revision": UUID,
                    "preserve_contradictory_evidence": {"type": "boolean"},
                    "disclosed_limitation": NULLABLE_TEXT,
                },
                [
                    "finding_id",
                    "expected_revision",
                    "preserve_contradictory_evidence",
                    "disclosed_limitation",
                ],
            ),
        },
        ["operation_id", "data"],
    )
    budget_line = closed(
        {
            "activity_id": UUID,
            "category_id": UUID,
            "partner_id": UUID,
            "period_id": UUID,
            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
            "amount": {"type": "string", "pattern": DECIMAL},
        },
        ["activity_id", "category_id", "partner_id", "period_id", "currency", "amount"],
    )
    schemas["BudgetCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "title": {"type": "string", "minLength": 1},
                    "approval_route": {"type": "array", "minItems": 1, "items": UUID},
                    "rate_assumptions": {"type": "array", "items": {"type": "object"}},
                    "lines": {"type": "array", "minItems": 1, "items": budget_line},
                },
                ["title", "approval_route", "rate_assumptions", "lines"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["BudgetRevise"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "budget_id": UUID,
                    "expected_revision": UUID,
                    "rate_assumptions": {"type": "array", "items": {"type": "object"}},
                    "lines": {"type": "array", "minItems": 1, "items": budget_line},
                },
                ["budget_id", "expected_revision", "rate_assumptions", "lines"],
            ),
        },
        ["operation_id", "data"],
    )
    schemas["BudgetApprove"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {"budget_id": UUID, "expected_revision": UUID}, ["budget_id", "expected_revision"]
            ),
        },
        ["operation_id", "data"],
    )
    expenditure_transaction = closed(
        {
            "source_transaction_key": {"type": "string", "minLength": 1},
            "posting_date": {"type": "string", "format": "date"},
            "event_date": {"type": "string", "format": "date"},
            "amount": {"type": "string", "pattern": DECIMAL},
            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
            "category_id": UUID,
            "funding_allocation_id": UUID,
            "adjustment_semantic": {"enum": ["ORIGINAL", "REVERSAL", "REPLACEMENT"]},
        },
        [
            "source_transaction_key",
            "posting_date",
            "event_date",
            "amount",
            "currency",
            "category_id",
            "funding_allocation_id",
            "adjustment_semantic",
        ],
    )
    schemas["ExpenditureImport"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "source_system": {"type": "string", "minLength": 1},
                    "file_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "control_total": {"type": "string", "pattern": DECIMAL},
                    "permitted_exception": NULLABLE_TEXT,
                    "transactions": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 10000,
                        "items": expenditure_transaction,
                    },
                },
                ["source_system", "file_sha256", "control_total", "permitted_exception", "transactions"],
            ),
        },
        ["operation_id", "data"],
    )
    transaction_pin = closed({"object_id": UUID, "revision_id": UUID}, ["object_id", "revision_id"])
    schemas["FinanceVarianceSave"] = closed(
        {
            "operation_id": UUID,
            "data": closed(
                {
                    "budget_id": UUID,
                    "budget_revision": UUID,
                    "actual_cutoff": {"type": "string", "format": "date"},
                    "actual_data_state": {"enum": ["COMPLETE", "MISSING"]},
                    "actual_transactions": {"type": "array", "items": transaction_pin},
                    "commitments": {"type": "string", "pattern": DECIMAL},
                    "forecast_total": {"type": "string", "pattern": DECIMAL},
                    "forecast_method": {"type": "string", "minLength": 1},
                    "forecast_method_version": {"type": "string", "minLength": 1},
                    "forecast_assumptions": {"type": "array", "items": {"type": "string", "minLength": 1}},
                    "author_id": UUID,
                },
                [
                    "budget_id",
                    "budget_revision",
                    "actual_cutoff",
                    "actual_data_state",
                    "actual_transactions",
                    "commitments",
                    "forecast_total",
                    "forecast_method",
                    "forecast_method_version",
                    "forecast_assumptions",
                    "author_id",
                ],
            ),
        },
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
                [
                    "coverage_threshold",
                    "visible_scope",
                    "hidden_members_disclosed",
                    "raw_cross_group_ranking",
                    "groups",
                ],
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
        **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
    )
    copy_entry["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardCopy"
    }
    paths[prefix + "dashboards/{object_id}/actions/copy"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": copy_entry,
    }
    sharing_preview = deepcopy(preview)
    sharing_preview.update(
        operationId="preview_dashboard_sharing",
        summary="Preview dashboard bindings for a recipient without granting access",
        **{"x-capability": "dashboards.read", "x-contract-version": VERSION},
    )
    sharing_preview["parameters"] = [
        {
            "name": "recipient_id",
            "in": "query",
            "required": True,
            "schema": deepcopy(UUID),
        }
    ]
    sharing_preview["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardSharingPreview"
    }
    paths[prefix + "dashboards/{object_id}/sharing-preview"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": sharing_preview,
    }
    publish_entry = deepcopy(copy_entry)
    publish_entry.update(
        operationId="action_dashboards_publish",
        summary="Publish an immutable pinned dashboard configuration",
        **{"x-capability": "dashboards.draft.edit", "x-contract-version": VERSION},
    )
    publish_entry["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPublish"
    }
    publish_entry["responses"]["201"] = publish_entry["responses"].pop("200")
    publish_entry["responses"]["201"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/Receipt"
    }
    paths[prefix + "dashboards/{object_id}/actions/publish"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": publish_entry,
    }
    publication_parameters = deepcopy(dashboard_item["parameters"]) + [
        {"name": "publication_id", "in": "path", "required": True, "schema": deepcopy(UUID)}
    ]
    publication_status = deepcopy(preview)
    publication_status.update(
        operationId="read_dashboard_publication",
        summary="Read a dashboard publication with current sensitivity revalidation",
        **{"x-capability": "dashboards.read", "x-contract-version": VERSION},
    )
    publication_status["parameters"] = []
    publication_status["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardPublicationStatus"
    }
    paths[prefix + "dashboards/{object_id}/publications/{publication_id}"] = {
        "parameters": publication_parameters,
        "get": publication_status,
    }
    alert_create = deepcopy(paths[prefix + "dashboards"]["post"])
    alert_create.update(
        operationId="create_dashboard_alert_rule",
        summary="Create a governed dashboard alert rule",
        **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
    )
    alert_create["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardAlertRuleCreate"
    }
    alert_create["responses"]["201"] = alert_create["responses"].pop("200")
    alert_create["responses"]["201"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/Receipt"
    }
    alert_list = deepcopy(paths[prefix + "dashboards"]["get"])
    alert_list.update(
        operationId="list_dashboard_alert_rules",
        summary="List governed dashboard alert rules",
        **{"x-capability": "dashboards.read", "x-contract-version": VERSION},
    )
    alert_list["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardAlertRuleList"
    }
    paths[prefix + "dashboard-alert-rules"] = {"get": alert_list, "post": alert_create}
    alert_read = deepcopy(paths[prefix + "dashboards/{object_id}"]["get"])
    alert_read.update(
        operationId="read_dashboard_alert_rule",
        summary="Read a governed dashboard alert rule and its current cadence",
        **{"x-capability": "dashboards.read", "x-contract-version": VERSION},
    )
    alert_read["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardAlertRule"
    }
    paths[prefix + "dashboard-alert-rules/{object_id}"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": alert_read,
    }
    incident_list = deepcopy(alert_list)
    incident_list.update(
        operationId="list_dashboard_alert_incidents",
        summary="List durable cooldown-coalesced incidents for an alert rule",
    )
    incident_list["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardAlertIncidentList"
    }
    paths[prefix + "dashboard-alert-rules/{object_id}/incidents"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": incident_list,
    }
    alert_evaluate = deepcopy(copy_entry)
    alert_evaluate.update(
        operationId="evaluate_dashboard_alert_rule",
        summary="Evaluate a rule without treating missing values as zero",
        **{"x-capability": "dashboards.draft.edit", "x-contract-version": VERSION},
    )
    alert_evaluate["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardAlertEvaluate"
    }
    alert_evaluate["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DashboardAlertOutcome"
    }
    paths[prefix + "dashboard-alert-rules/{object_id}/actions/evaluate"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": alert_evaluate,
    }
    external_create = deepcopy(alert_create)
    external_create.update(
        operationId="create_external_analytics_connection",
        summary="Create a dataset-scoped external analytics identity",
        **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
    )
    external_create["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsConnectionCreate"
    }
    external_create["responses"]["201"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsConnectionReceipt"
    }
    external_list = deepcopy(alert_list)
    external_list.update(
        operationId="list_external_analytics_connections",
        summary="List governed external analytics connections",
    )
    external_list["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsConnectionList"
    }
    paths[prefix + "external-analytics-connections"] = {
        "get": external_list,
        "post": external_create,
    }
    external_read = deepcopy(alert_read)
    external_read.update(
        operationId="read_external_analytics_connection",
        summary="Read a governed external analytics connection without its credential",
    )
    external_read["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsConnection"
    }
    paths[prefix + "external-analytics-connections/{object_id}"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": external_read,
    }
    extract_list = deepcopy(external_list)
    extract_list.update(
        operationId="list_external_analytics_extracts",
        summary="List retained external extract disclosures",
    )
    extract_list["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsExtractList"
    }
    paths[prefix + "external-analytics-connections/{object_id}/extracts"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": extract_list,
    }
    external_refresh = deepcopy(alert_evaluate)
    external_refresh.update(
        operationId="refresh_external_analytics_connection",
        summary="Refresh an exact governed external data package",
        **{"x-capability": "dashboards.draft.edit", "x-contract-version": VERSION},
    )
    external_refresh["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsRefresh"
    }
    external_refresh["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsExtract"
    }
    paths[prefix + "external-analytics-connections/{object_id}/actions/refresh"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": external_refresh,
    }
    external_revoke = deepcopy(external_refresh)
    external_revoke.update(
        operationId="revoke_external_analytics_connection",
        summary="Revoke an external analytics identity while retaining extract history",
    )
    external_revoke["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsRevoke"
    }
    external_revoke["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExternalAnalyticsRevocation"
    }
    paths[prefix + "external-analytics-connections/{object_id}/actions/revoke"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": external_revoke,
    }
    anomaly_run = deepcopy(external_create)
    anomaly_run.update(
        operationId="create_anomaly_run",
        summary="Run versioned suggestion-only anomaly assistance",
        **{"x-capability": "dashboards.draft.create", "x-contract-version": VERSION},
    )
    anomaly_run["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnomalyRunCreate"
    }
    anomaly_run["responses"]["201"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnomalyRunOutcome"
    }
    anomaly_list = deepcopy(external_list)
    anomaly_list.update(operationId="list_anomaly_runs", summary="List readable anomaly runs")
    anomaly_list["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnomalyResourceList"
    }
    paths[prefix + "anomaly-runs"] = {"post": anomaly_run, "get": anomaly_list}
    anomaly_read = deepcopy(external_read)
    anomaly_read.update(operationId="read_anomaly_run", summary="Read a versioned anomaly run")
    anomaly_read["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnomalyResource"
    }
    paths[prefix + "anomaly-runs/{object_id}"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": anomaly_read,
    }
    finding_list = deepcopy(anomaly_list)
    finding_list.update(operationId="list_anomaly_findings", summary="List reviewable anomaly findings")
    paths[prefix + "anomaly-findings"] = {"get": finding_list}
    finding_read = deepcopy(anomaly_read)
    finding_read.update(operationId="read_anomaly_finding", summary="Read the current anomaly finding review")
    paths[prefix + "anomaly-findings/{object_id}"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": finding_read,
    }
    anomaly_review = deepcopy(alert_evaluate)
    anomaly_review.update(
        operationId="review_anomaly_finding",
        summary="Confirm, dismiss or defer an anomaly suggestion without changing source data",
        **{"x-capability": "dashboards.draft.edit", "x-contract-version": VERSION},
    )
    anomaly_review["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnomalyFindingReview"
    }
    anomaly_review["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnomalyReviewOutcome"
    }
    paths[prefix + "anomaly-findings/{object_id}/actions/review"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": anomaly_review,
    }
    evaluation_create = deepcopy(anomaly_run)
    evaluation_create.update(
        operationId="create_evaluation_registration",
        summary="Register a controlled evaluation without approving sensitive processing",
        **{"x-capability": "dashboards.draft.create", "x-contract-version": VERSION},
    )
    evaluation_create["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationRegistrationCreate"
    }
    evaluation_create["responses"]["201"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/Receipt"
    }
    existing_evaluation_item = deepcopy(paths.get(prefix + "evaluations/{object_id}", {}))
    evaluation_list = deepcopy(anomaly_list)
    evaluation_list.update(
        operationId="list_evaluation_registrations",
        summary="List controlled evaluation registrations",
        **{"x-capability": "evaluations.read"},
    )
    evaluation_list["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationRegistrationList"
    }
    evaluation_list.setdefault("parameters", []).append(
        {"name": "programme_id", "in": "query", "required": False, "schema": deepcopy(UUID)}
    )
    paths[prefix + "evaluations"] = {"post": evaluation_create, "get": evaluation_list}
    evaluation_read = deepcopy(anomaly_read)
    evaluation_read.update(
        operationId="get_evaluations",
        summary="Read a controlled evaluation registration",
        **{"x-capability": "evaluations.read"},
    )
    evaluation_read["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationRegistrationResource"
    }
    paths[prefix + "evaluations/{object_id}"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": evaluation_read,
        **({"patch": existing_evaluation_item["patch"]} if "patch" in existing_evaluation_item else {}),
    }
    evaluation_history = deepcopy(evaluation_read)
    evaluation_history.update(
        operationId="list_evaluation_stage_gates",
        summary="List immutable evaluation gate decisions",
        **{"x-capability": "evaluations.read"},
    )
    evaluation_history["parameters"] = [
        p for p in deepcopy(evaluation_list.get("parameters", [])) if p["name"] != "programme_id"
    ]
    evaluation_history["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationStageGateHistory"
    }
    paths[prefix + "evaluations/{object_id}/stage-gates"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": evaluation_history,
    }
    evaluation_gate = deepcopy(anomaly_review)
    evaluation_gate.update(
        operationId="evaluate_evaluation_stage_gate",
        summary="Check pinned method and policy documents before an evaluation stage",
        **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
    )
    evaluation_gate["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationStageGate"
    }
    evaluation_gate["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationStageGateOutcome"
    }
    paths[prefix + "evaluations/{object_id}/actions/stage-gate"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": evaluation_gate,
    }
    methodology_create = deepcopy(evaluation_create)
    methodology_create.update(
        operationId="create_evaluation_methodology",
        summary="Create a reviewed versioned evaluation methodology",
        **{"x-capability": "dashboards.draft.create", "x-contract-version": VERSION},
    )
    methodology_create["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationMethodologyCreate"
    }
    methodology_list = deepcopy(evaluation_list)
    methodology_list.update(
        operationId="list_evaluation_methodologies", summary="List methodologies for an evaluation"
    )
    methodology_list["parameters"] = [
        p for p in methodology_list.get("parameters", []) if p["name"] != "programme_id"
    ]
    methodology_list["parameters"].append(
        {"name": "evaluation_id", "in": "query", "required": True, "schema": deepcopy(UUID)}
    )
    methodology_list["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationMethodologyList"
    }
    paths[prefix + "evaluation-methodologies"] = {"post": methodology_create, "get": methodology_list}
    methodology_read = deepcopy(evaluation_read)
    methodology_read.update(
        operationId="read_evaluation_methodology", summary="Read a current evaluation methodology"
    )
    methodology_read["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationMethodologyResource"
    }
    paths[prefix + "evaluation-methodologies/{object_id}"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": methodology_read,
    }
    methodology_history = deepcopy(methodology_read)
    methodology_history.update(
        operationId="list_evaluation_methodology_history", summary="List immutable methodology revisions"
    )
    methodology_history["parameters"] = [
        p for p in deepcopy(evaluation_list.get("parameters", [])) if p["name"] != "programme_id"
    ]
    methodology_history["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationMethodologyHistory"
    }
    paths[prefix + "evaluation-methodologies/{object_id}/history"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": methodology_history,
    }
    for action, schema, operation, summary in [
        (
            "amend",
            "EvaluationMethodologyAmend",
            "amend_evaluation_methodology",
            "Amend methodology with inspection-relative timing",
        ),
        (
            "review",
            "EvaluationMethodologyReview",
            "review_evaluation_methodology",
            "Review a pending methodology amendment",
        ),
    ]:
        entry = deepcopy(anomaly_review)
        entry.update(
            operationId=operation,
            summary=summary,
            **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
        )
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + schema
        }
        entry["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/Receipt"
        }
        paths[prefix + "evaluation-methodologies/{object_id}/actions/" + action] = {
            "parameters": deepcopy(dashboard_item["parameters"]),
            "post": entry,
        }
    sample_export_entry = deepcopy(anomaly_review)
    sample_export_entry.update(
        operationId="export_evaluation_sample",
        summary="Export a reviewed sample without silently inventing weights",
        **{"x-capability": "evaluations.read", "x-contract-version": VERSION},
    )
    sample_export_entry["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationSampleExportRequest"
    }
    sample_export_entry["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/EvaluationSampleExport"
    }
    paths[prefix + "evaluation-methodologies/{object_id}/sample-export"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": sample_export_entry,
    }
    analysis_create = deepcopy(methodology_create)
    analysis_create.update(
        operationId="create_analysis_package",
        summary="Freeze exact approved analysis sources and integrity metadata",
        **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
    )
    analysis_create["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnalysisPackageCreate"
    }
    paths[prefix + "analysis-packages"] = {"post": analysis_create}
    analysis_export = deepcopy(preview)
    analysis_export.update(
        operationId="export_analysis_package",
        summary="Export a frozen analysis package under separate export authority",
        **{"x-capability": "report.export", "x-contract-version": VERSION},
    )
    analysis_export["parameters"] = []
    analysis_export["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnalysisPackageExport"
    }
    paths[prefix + "analysis-packages/{object_id}/export"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": analysis_export,
    }
    analysis_result = deepcopy(analysis_create)
    analysis_result.update(
        operationId="register_analysis_result",
        summary="Register a result against an exact package and methodology revision",
        **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
    )
    analysis_result["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AnalysisResultRegister"
    }
    paths[prefix + "analysis-packages/{object_id}/results"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "post": analysis_result,
    }
    learning_create = deepcopy(analysis_create)
    learning_create.update(
        operationId="create_learning_question",
        summary="Create a contextual versioned learning question",
        **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
    )
    learning_create["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/LearningQuestionCreate"
    }
    paths[prefix + "learning-questions"] = {"post": learning_create}
    for action, schema_name, operation in [
        ("close", "LearningQuestionClose", "close_learning_question"),
        ("reopen", "LearningQuestionReopen", "reopen_learning_question"),
        ("consider-context", "LearningContextConsider", "consider_learning_context"),
    ]:
        entry = deepcopy(analysis_result)
        entry.update(
            operationId=operation,
            summary=operation.replace("_", " ").title(),
            **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
        )
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": f"#/components/schemas/{schema_name}"
        }
        paths[prefix + f"learning-questions/{{object_id}}/actions/{action}"] = {
            "parameters": deepcopy(dashboard_item["parameters"]),
            "post": entry,
        }
    learning_summary = deepcopy(preview)
    learning_summary.update(
        operationId="get_learning_question_summary",
        summary="Read a disclosure-reviewed learning summary",
        **{"x-capability": "evaluations.read", "x-contract-version": VERSION},
    )
    learning_summary["parameters"] = [
        {"name": "disclosure_id", "in": "query", "required": False, "schema": UUID}
    ]
    learning_summary["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/LearningQuestionSummary"
    }
    paths[prefix + "learning-questions/{object_id}/summary"] = {
        "parameters": deepcopy(dashboard_item["parameters"]),
        "get": learning_summary,
    }
    for route, schema_name, operation in [
        (
            "evaluation-recommendations/{object_id}/response",
            "ManagementResponseCreate",
            "respond_to_evaluation_recommendation",
        ),
        (
            "management-actions/{object_id}/actions/complete",
            "ManagementActionComplete",
            "complete_management_action",
        ),
        (
            "management-actions/{object_id}/actions/escalate-overdue",
            "ManagementActionEscalate",
            "escalate_overdue_management_action",
        ),
    ]:
        entry = deepcopy(analysis_result)
        entry.update(
            operationId=operation,
            summary=operation.replace("_", " ").title(),
            **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
        )
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": f"#/components/schemas/{schema_name}"
        }
        paths[prefix + route] = {"parameters": deepcopy(dashboard_item["parameters"]), "post": entry}
    for route, schema_name, operation in [
        ("qualitative-codebooks", "QualitativeCodebookCreate", "create_qualitative_codebook"),
        ("qualitative-assignments", "QualitativeAssignmentCreate", "assign_qualitative_codes"),
        ("qualitative-adjudications", "QualitativeAdjudicationCreate", "adjudicate_qualitative_coding"),
        ("qualitative-agreements", "QualitativeAgreementCreate", "calculate_qualitative_agreement"),
    ]:
        entry = deepcopy(analysis_create)
        entry.update(
            operationId=operation,
            summary=operation.replace("_", " ").title(),
            **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
        )
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": f"#/components/schemas/{schema_name}"
        }
        paths[prefix + route] = {"post": entry}
    for route, schema_name, operation in [
        ("transcription-requests", "TranscriptionRequest", "request_transcription"),
        ("transcript-corrections", "TranscriptCorrection", "correct_transcript_segment"),
        ("quotation-references", "QuotationReferenceCreate", "create_reviewed_quotation"),
    ]:
        entry = deepcopy(analysis_create)
        entry.update(
            operationId=operation,
            summary=operation.replace("_", " ").title(),
            **{"x-capability": "evaluations.draft.edit", "x-contract-version": VERSION},
        )
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": f"#/components/schemas/{schema_name}"
        }
        paths[prefix + route] = {"post": entry}
    for route, schema_name, operation in [
        ("findings", "FindingCreate", "create_triangulated_finding"),
        ("finding-revisions", "FindingRevise", "revise_finding_interpretation"),
        ("finding-publications", "FindingPublish", "publish_triangulated_finding"),
    ]:
        entry = deepcopy(analysis_create)
        entry.update(
            operationId=operation,
            summary=operation.replace("_", " ").title(),
            **{"x-capability": "budget-lines.draft.edit", "x-contract-version": VERSION},
        )
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": f"#/components/schemas/{schema_name}"
        }
        paths[prefix + route] = {"post": entry}
    for route, schema_name, operation in [
        ("budgets", "BudgetCreate", "create_budget_version"),
        ("budget-revisions", "BudgetRevise", "revise_budget_version"),
        ("budget-approvals", "BudgetApprove", "approve_budget_version"),
    ]:
        entry = deepcopy(analysis_create)
        entry.update(
            operationId=operation,
            summary=operation.replace("_", " ").title(),
            **{"x-contract-version": VERSION},
        )
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": f"#/components/schemas/{schema_name}"
        }
        paths[prefix + route] = {"post": entry}
    expenditure_entry = deepcopy(analysis_create)
    expenditure_entry.update(
        operationId="import_expenditure",
        summary="Import and reconcile expenditure",
        **{"x-capability": "finance-transactions.draft.create", "x-contract-version": VERSION},
    )
    expenditure_entry["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ExpenditureImport"
    }
    paths[prefix + "expenditure-imports"] = {"post": expenditure_entry}
    variance_entry = deepcopy(analysis_create)
    variance_entry.update(
        operationId="save_finance_variance",
        summary="Save separated actual and forecast variance",
        **{"x-capability": "finance-transactions.read", "x-contract-version": VERSION},
    )
    variance_entry["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/FinanceVarianceSave"
    }
    paths[prefix + "finance-variance-views"] = {"post": variance_entry}
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
            "preview_dashboard_sharing",
            "GET",
            prefix + "dashboards/{object_id}/sharing-preview",
            "dashboards.read",
            False,
        ),
        (
            "action_dashboards_publish",
            "POST",
            prefix + "dashboards/{object_id}/actions/publish",
            "dashboards.draft.edit",
            True,
        ),
        (
            "read_dashboard_publication",
            "GET",
            prefix + "dashboards/{object_id}/publications/{publication_id}",
            "dashboards.read",
            False,
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
        (
            "create_dashboard_alert_rule",
            "POST",
            prefix + "dashboard-alert-rules",
            "dashboards.draft.create",
            True,
        ),
        (
            "list_dashboard_alert_rules",
            "GET",
            prefix + "dashboard-alert-rules",
            "dashboards.read",
            False,
        ),
        (
            "read_dashboard_alert_rule",
            "GET",
            prefix + "dashboard-alert-rules/{object_id}",
            "dashboards.read",
            False,
        ),
        (
            "list_dashboard_alert_incidents",
            "GET",
            prefix + "dashboard-alert-rules/{object_id}/incidents",
            "dashboards.read",
            False,
        ),
        (
            "evaluate_dashboard_alert_rule",
            "POST",
            prefix + "dashboard-alert-rules/{object_id}/actions/evaluate",
            "dashboards.draft.edit",
            True,
        ),
        (
            "create_external_analytics_connection",
            "POST",
            prefix + "external-analytics-connections",
            "dashboards.draft.create",
            True,
        ),
        (
            "list_external_analytics_connections",
            "GET",
            prefix + "external-analytics-connections",
            "dashboards.read",
            False,
        ),
        (
            "read_external_analytics_connection",
            "GET",
            prefix + "external-analytics-connections/{object_id}",
            "dashboards.read",
            False,
        ),
        (
            "list_external_analytics_extracts",
            "GET",
            prefix + "external-analytics-connections/{object_id}/extracts",
            "dashboards.read",
            False,
        ),
        (
            "refresh_external_analytics_connection",
            "POST",
            prefix + "external-analytics-connections/{object_id}/actions/refresh",
            "dashboards.draft.edit",
            True,
        ),
        (
            "revoke_external_analytics_connection",
            "POST",
            prefix + "external-analytics-connections/{object_id}/actions/revoke",
            "dashboards.draft.edit",
            True,
        ),
        ("create_anomaly_run", "POST", prefix + "anomaly-runs", "dashboards.draft.create", True),
        ("list_anomaly_runs", "GET", prefix + "anomaly-runs", "dashboards.read", False),
        ("read_anomaly_run", "GET", prefix + "anomaly-runs/{object_id}", "dashboards.read", False),
        ("list_anomaly_findings", "GET", prefix + "anomaly-findings", "dashboards.read", False),
        ("read_anomaly_finding", "GET", prefix + "anomaly-findings/{object_id}", "dashboards.read", False),
        (
            "review_anomaly_finding",
            "POST",
            prefix + "anomaly-findings/{object_id}/actions/review",
            "dashboards.draft.edit",
            True,
        ),
        ("create_evaluation_registration", "POST", prefix + "evaluations", "evaluations.draft.edit", True),
        ("list_evaluation_registrations", "GET", prefix + "evaluations", "evaluations.read", False),
        ("get_evaluations", "GET", prefix + "evaluations/{object_id}", "evaluations.read", False),
        (
            "list_evaluation_stage_gates",
            "GET",
            prefix + "evaluations/{object_id}/stage-gates",
            "evaluations.read",
            False,
        ),
        (
            "evaluate_evaluation_stage_gate",
            "POST",
            prefix + "evaluations/{object_id}/actions/stage-gate",
            "evaluations.draft.edit",
            True,
        ),
        (
            "create_evaluation_methodology",
            "POST",
            prefix + "evaluation-methodologies",
            "evaluations.draft.edit",
            True,
        ),
        (
            "list_evaluation_methodologies",
            "GET",
            prefix + "evaluation-methodologies",
            "evaluations.read",
            False,
        ),
        (
            "read_evaluation_methodology",
            "GET",
            prefix + "evaluation-methodologies/{object_id}",
            "evaluations.read",
            False,
        ),
        (
            "list_evaluation_methodology_history",
            "GET",
            prefix + "evaluation-methodologies/{object_id}/history",
            "evaluations.read",
            False,
        ),
        (
            "amend_evaluation_methodology",
            "POST",
            prefix + "evaluation-methodologies/{object_id}/actions/amend",
            "evaluations.draft.edit",
            True,
        ),
        (
            "review_evaluation_methodology",
            "POST",
            prefix + "evaluation-methodologies/{object_id}/actions/review",
            "evaluations.draft.edit",
            True,
        ),
        (
            "export_evaluation_sample",
            "POST",
            prefix + "evaluation-methodologies/{object_id}/sample-export",
            "evaluations.read",
            False,
        ),
        (
            "create_analysis_package",
            "POST",
            prefix + "analysis-packages",
            "evaluations.draft.edit",
            True,
        ),
        (
            "export_analysis_package",
            "GET",
            prefix + "analysis-packages/{object_id}/export",
            "report.export",
            False,
        ),
        (
            "register_analysis_result",
            "POST",
            prefix + "analysis-packages/{object_id}/results",
            "evaluations.draft.edit",
            True,
        ),
        (
            "create_learning_question",
            "POST",
            prefix + "learning-questions",
            "evaluations.draft.edit",
            True,
        ),
        (
            "close_learning_question",
            "POST",
            prefix + "learning-questions/{object_id}/actions/close",
            "evaluations.draft.edit",
            True,
        ),
        (
            "reopen_learning_question",
            "POST",
            prefix + "learning-questions/{object_id}/actions/reopen",
            "evaluations.draft.edit",
            True,
        ),
        (
            "consider_learning_context",
            "POST",
            prefix + "learning-questions/{object_id}/actions/consider-context",
            "evaluations.draft.edit",
            True,
        ),
        (
            "get_learning_question_summary",
            "GET",
            prefix + "learning-questions/{object_id}/summary",
            "evaluations.read",
            False,
        ),
        (
            "create_qualitative_codebook",
            "POST",
            prefix + "qualitative-codebooks",
            "evaluations.draft.edit",
            True,
        ),
        (
            "assign_qualitative_codes",
            "POST",
            prefix + "qualitative-assignments",
            "evaluations.draft.edit",
            True,
        ),
        (
            "adjudicate_qualitative_coding",
            "POST",
            prefix + "qualitative-adjudications",
            "evaluations.draft.edit",
            True,
        ),
        (
            "calculate_qualitative_agreement",
            "POST",
            prefix + "qualitative-agreements",
            "evaluations.draft.edit",
            True,
        ),
        (
            "request_transcription",
            "POST",
            prefix + "transcription-requests",
            "evaluations.draft.edit",
            True,
        ),
        (
            "correct_transcript_segment",
            "POST",
            prefix + "transcript-corrections",
            "evaluations.draft.edit",
            True,
        ),
        (
            "create_reviewed_quotation",
            "POST",
            prefix + "quotation-references",
            "evaluations.draft.edit",
            True,
        ),
        ("create_triangulated_finding", "POST", prefix + "findings", "evaluations.draft.edit", True),
        (
            "revise_finding_interpretation",
            "POST",
            prefix + "finding-revisions",
            "evaluations.draft.edit",
            True,
        ),
        (
            "publish_triangulated_finding",
            "POST",
            prefix + "finding-publications",
            "evaluations.draft.edit",
            True,
        ),
        ("create_budget_version", "POST", prefix + "budgets", "budget-lines.draft.create", True),
        ("revise_budget_version", "POST", prefix + "budget-revisions", "budget-lines.draft.edit", True),
        ("approve_budget_version", "POST", prefix + "budget-approvals", "budget-lines.draft.edit", True),
        (
            "import_expenditure",
            "POST",
            prefix + "expenditure-imports",
            "finance-transactions.draft.create",
            True,
        ),
        (
            "save_finance_variance",
            "POST",
            prefix + "finance-variance-views",
            "finance-transactions.read",
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
                "role_templates": (
                    ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "ANALYST"]
                    if op
                    in {
                        "create_analysis_package",
                        "register_analysis_result",
                        "create_learning_question",
                        "reopen_learning_question",
                        "consider_learning_context",
                    }
                    else ["MEL_ADMIN", "PROGRAMME_MANAGER", "REVIEWER"]
                    if op == "close_learning_question"
                    else ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST"]
                    if op == "export_analysis_package"
                    else ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST"]
                    if op
                    in {
                        "create_qualitative_codebook",
                        "assign_qualitative_codes",
                        "adjudicate_qualitative_coding",
                        "close_learning_question",
                        "calculate_qualitative_agreement",
                        "request_transcription",
                        "correct_transcript_segment",
                        "create_reviewed_quotation",
                        "create_triangulated_finding",
                        "revise_finding_interpretation",
                        "publish_triangulated_finding",
                    }
                    else ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "ANALYST"]
                    if op
                    in {
                        "create_evaluation_registration",
                        "evaluate_evaluation_stage_gate",
                        "create_evaluation_methodology",
                        "amend_evaluation_methodology",
                        "create_budget_version",
                        "revise_budget_version",
                        "import_expenditure",
                        "save_finance_variance",
                    }
                    else ["MEL_ADMIN", "PROGRAMME_MANAGER", "REVIEWER"]
                    if op in {"review_evaluation_methodology", "approve_budget_version"}
                    else ROLES
                ),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": audit_event,
                **(
                    {"independence_required": True}
                    if op
                    in {
                        "evaluate_evaluation_stage_gate",
                        "review_evaluation_methodology",
                        "adjudicate_qualitative_coding",
                        "publish_triangulated_finding",
                        "approve_budget_version",
                    }
                    else {}
                ),
            }
        )
