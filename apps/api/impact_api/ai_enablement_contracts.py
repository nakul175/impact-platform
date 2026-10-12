"""Nonprofit AI enablement: editorial assessment and separately permitted advisory drafts."""

from copy import deepcopy

from .ai_solutions_catalog import catalog_schema
from .measurement_contracts import closed

VERSION = "1.41.0"
# FR-AI-001 (build 0.37.0): the tenant AI policy routes and the advisory request's policy pin.
POLICY_VERSION = "1.80.0"
# US-MP-03 (build 0.38.0): the organisation's ranking weights and the weighted opportunity ranking.
RANKING_VERSION = "1.27.0"
IMPLEMENTED = [
    ("get", "ai-enablement/catalog"),
    ("post", "ai-enablement/assessment"),
    ("post", "ai-enablement/advisory"),
    ("post", "ai-enablement/advisory-jobs"),
    ("get", "ai-enablement/advisory-jobs/{job_id}"),
    ("post", "ai-enablement/advisory-jobs/{job_id}/actions/cancel"),
    ("post", "ai-enablement/forecasts"),
    ("get", "ai-enablement/forecasts/{scenario_id}"),
    ("get", "ai-enablement/forecasts/{scenario_id}/export"),
    ("post", "ai-enablement/forecasts/{scenario_id}/versions/{version}/actions/request-adoption"),
    ("post", "ai-enablement/safety-feedback"),
    ("get", "ai-enablement/safety-shutdowns"),
    ("post", "ai-enablement/safety-shutdowns"),
    ("post", "ai-enablement/safety-shutdowns/{event_id}/actions/approve-recovery"),
    ("post", "ai-enablement/extractions"),
    ("post", "ai-enablement/extractions/{draft_id}/actions/apply"),
    ("post", "ai-enablement/indicator-design/proposals"),
    ("post", "ai-enablement/indicator-design/drafts"),
    ("post", "ai-enablement/import-assistance/{batch_id}/revisions/{revision_id}/proposals"),
    ("post", "ai-enablement/import-assistance/{batch_id}/revisions/{revision_id}/actions/apply"),
    ("post", "ai-enablement/evidence-questions"),
    ("post", "ai-enablement/numeric-analysis"),
    ("get", "ai-enablement/solutions"),
    ("get", "ai-enablement/policy"),
    ("put", "ai-enablement/policy"),
    ("get", "ai-enablement/policy/revisions"),
    ("get", "ai-enablement/ranking-weights"),
    ("put", "ai-enablement/ranking-weights"),
    ("post", "ai-enablement/ranking"),
]
# Every reader of AI enablement. FINANCE (the Operations Head persona) reads only: the owner decided on
# 9 October 2026 (US-MP-03 review) that it holds ai.enablement.read and never ai.enablement.manage.
ROLES = [
    "TENANT_ADMIN",
    "MEL_ADMIN",
    "PROGRAMME_MANAGER",
    "AUTHOR",
    "REVIEWER",
    "ANALYST",
    "DATA_STEWARD",
    "FINANCE",
]
# Changing the policy is an administrative, sensitive action: TENANT_ADMIN only, with authentication
# within the previous 300 seconds plus the configured assurance (store.authorize), always audited.
POLICY_MANAGERS = ["TENANT_ADMIN"]
POLICY_CAPABILITY = "ai.policy.manage"
# Ranking weights are a preference, not an approval: the existing ai.enablement.manage holders change
# them with expected_revision, no independent review and no fresh sign-in (US-MP-03).
RANKING_MANAGERS = ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"]
# The four criteria: each has a weight and, per ranked opportunity, a score.
WEIGHT_FIELDS = ["impact", "effort", "cost", "readiness"]
USE_CASES = [
    "ADVISORY_DRAFT",
    "EXTRACTION",
    "REPORT_DRAFT",
    "CHAT",
    "INDICATOR_DESIGN",
    "IMPORT_CLEANING",
    "EVIDENCE_QUESTION",
    "NUMERIC_ANALYSIS",
]
DATA_CLASSES = ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"]
# The closed provider-and-region list. Adding a destination is a reviewed change to this list and to
# the CHECK constraint of migration 0041; a tenant policy starts with no destination selected.
DESTINATIONS = ["openai-us"]
REVIEW_MODES = ["HUMAN_REVIEW"]
LANGUAGE_PATTERN = "^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8}){0,3}$"
TOOL_PATTERN = "^[a-z][a-z0-9_.-]{0,63}$"
MAX_BUDGET_UNITS = 1000000
MAX_POLICY_VERSION = 2147483647


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    schemas["AIEnablementProfile"] = closed(
        {
            "sector": {"enum": ["GENERAL", "EDUCATION", "HEALTH", "LIVELIHOODS", "ENVIRONMENT"]},
            "team_size": {"type": "integer", "minimum": 1, "maximum": 100000},
            "goal": {"type": "string", "minLength": 1, "maxLength": 1000},
            "data_readiness": {"enum": ["NONE", "BASIC", "STRUCTURED"]},
            "ai_experience": {"enum": ["NONE", "EXPERIMENTING", "REGULAR"]},
            "sensitive_data": {"type": "boolean"},
        },
        ["sector", "team_size", "goal", "data_readiness", "ai_experience", "sensitive_data"],
    )
    schemas["AIAssessmentRequest"] = closed(
        {"profile": {"$ref": "#/components/schemas/AIEnablementProfile"}}, ["profile"]
    )
    schemas["AIAdvisoryRequest"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "profile": {"$ref": "#/components/schemas/AIEnablementProfile"},
            "consent": {"const": True},
            "purpose": {"const": "AI_ADOPTION_ADVISORY"},
            "source_dependencies": {
                "type": "array",
                "maxItems": 20,
                "uniqueItems": True,
                "items": closed(
                    {
                        "object_id": {"type": "string", "format": "uuid"},
                        "revision_id": {"type": "string", "format": "uuid"},
                        "object_type": {"type": "string", "pattern": "^[A-Z][A-Za-z0-9]{0,99}$"},
                        "capability": {"type": "string", "pattern": "^[a-z][a-z0-9.-]{0,99}$"},
                    },
                    ["object_id", "revision_id", "object_type", "capability"],
                ),
            },
            # The policy version shown to the requester ("Policy in force"); a request made against
            # any other version is refused with 409 AI_POLICY_CHANGED before any reservation.
            "policy_version": {"type": "integer", "minimum": 0, "maximum": MAX_POLICY_VERSION},
            # Tools are never implicit: policy must list each tool and the concrete runtime must
            # independently expose it from a server-owned catalogue with scoped arguments.
            "tools": {
                "type": "array",
                "maxItems": 10,
                "uniqueItems": True,
                "items": {"type": "string", "pattern": TOOL_PATTERN},
            },
        },
        ["operation_id", "profile", "consent", "policy_version", "purpose"],
    )
    policy_schemas(schemas)
    ranking_schemas(schemas)
    # This increment publishes versioned editorial content, not an authored domain object.
    schemas["AIEnablementCatalog"] = {
        "type": "object",
        "required": [
            "schema_version",
            "content_version",
            "provenance",
            "journey",
            "use_cases",
            "learning_paths",
            "procurement_criteria",
            "marketplace_status",
            "advisory_available",
        ],
    }
    assessment_schemas(schemas)
    # US-DC-04 (build 0.39.0): closed, and every listing carries a valid commercial disclosure
    # (NONE_KNOWN with no relationship type, or DISCLOSED with at least one and a statement).
    schemas["AISolutionsCatalog"] = catalog_schema()
    schemas["AIAdvisoryDraft"] = closed(
        {
            "status": {"const": "DRAFT"},
            "text": {"type": "string", "maxLength": 12000},
            "assessment": {"type": "object"},
            "model": {"type": "string"},
            "disclaimer": {"type": "string"},
            "trace": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "requester_principal_id",
                    "scope",
                    "source_versions",
                    "use_case_configuration",
                    "model_identifier",
                    "tool_receipts",
                    "proposed_changes",
                    "review_decisions",
                    "applied_domain_receipts",
                    "output_version",
                    "retention_until",
                ],
                "properties": {
                    "requester_principal_id": {"type": "string", "format": "uuid"},
                    "scope": {"type": "object"},
                    "source_versions": {"type": "array", "maxItems": 20},
                    "use_case_configuration": {"type": "object"},
                    "model_identifier": {"type": "string", "maxLength": 200},
                    "tool_receipts": {"type": "array", "maxItems": 20},
                    "proposed_changes": {"type": "array", "maxItems": 100},
                    "review_decisions": {"type": "array", "maxItems": 100},
                    "applied_domain_receipts": {"type": "array", "maxItems": 100},
                    "output_version": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "retention_until": {"type": "string", "format": "date-time"},
                },
            },
        },
        ["status", "text", "assessment", "model", "disclaimer", "trace"],
    )
    schemas["AIAdvisoryJob"] = closed(
        {
            "job_id": {"type": "string", "format": "uuid"},
            "operation_id": {"type": "string", "format": "uuid"},
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
            "estimated_units": {"type": "integer", "minimum": 1},
            "requested_at": {"type": "string", "format": "date-time"},
            "cancellation_requested": {"type": "boolean"},
            "progress": {"type": "integer", "minimum": 0, "maximum": 100},
            "can_cancel": {"type": "boolean"},
            "outcome": {
                "type": ["string", "null"],
                "enum": ["SUCCEEDED", "TIMED_OUT", "CANCELLED", "FAILED", None],
            },
            "complete": {"type": ["boolean", "null"]},
            "label": {"type": ["string", "null"], "enum": ["Advisory draft", "Incomplete draft", None]},
            "can_publish_final": {"type": "boolean"},
        },
        [
            "job_id",
            "operation_id",
            "state",
            "estimated_units",
            "requested_at",
            "cancellation_requested",
            "progress",
            "can_cancel",
            "outcome",
            "complete",
            "label",
            "can_publish_final",
        ],
    )
    forecast_input = closed(
        {
            "ordinal": {"type": "integer", "minimum": 1},
            "object_id": {"type": "string", "format": "uuid"},
            "revision_id": {"type": "string", "format": "uuid"},
            "value": {"type": "string"},
        }
    )
    forecast_point = closed(
        {
            "step": {"type": "integer", "minimum": 1, "maximum": 24},
            "value": {"type": "string"},
            "lower": {"type": "string"},
            "upper": {"type": "string"},
        }
    )
    schemas["AIForecastRequest"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "scenario_id": {"type": ["string", "null"], "format": "uuid"},
            "label": {"type": "string", "minLength": 1, "maxLength": 220, "pattern": r"\S"},
            "horizon": {"type": "integer", "minimum": 1, "maximum": 24},
            "method": {"const": "LINEAR_TREND_V1"},
            "assumptions": {
                "type": "array",
                "maxItems": 20,
                "uniqueItems": True,
                "items": {"type": "string", "minLength": 1, "maxLength": 500},
            },
            "input_result_revisions": {
                "type": "array",
                "minItems": 1,
                "maxItems": 24,
                "uniqueItems": True,
                "items": {"type": "string", "format": "uuid"},
            },
        }
    )
    schemas["AIForecast"] = closed(
        {
            "scenario_id": {"type": "string", "format": "uuid"},
            "version": {"type": "integer", "minimum": 1},
            "label": {"type": "string"},
            "status": {"enum": ["EXPLORATORY", "PROJECTION"]},
            "horizon": {"type": "integer"},
            "method": {"const": "LINEAR_TREND_V1"},
            "assumptions": {"type": "array"},
            "validation_history": {"type": "object"},
            "unit": {"type": "string"},
            "inputs": {"type": "array", "items": forecast_input},
            "projections": {"type": "array", "items": forecast_point},
            "can_request_adoption": {"type": "boolean"},
            "targets_changed": {"const": False},
            "created_at": {"type": "string", "format": "date-time"},
        }
    )
    schemas["AIForecastExport"] = closed(
        {
            "scenario_id": {"type": "string", "format": "uuid"},
            "version": {"type": "integer"},
            "series": {"type": "array", "minItems": 2, "maxItems": 2},
            "approved_targets_changed": {"const": False},
        }
    )
    schemas["AIForecastAdoptionReview"] = closed(
        {
            "review_id": {"type": "string", "format": "uuid"},
            "state": {"const": "PENDING"},
            "targets_changed": {"const": False},
        }
    )
    category = {
        "enum": [
            "SENSITIVE_CITATION",
            "HARMFUL_CONTENT",
            "UNSUPPORTED_CLAIM",
            "UNAUTHORISED_ACTION",
            "OTHER",
        ]
    }
    schemas["AISafetyFeedbackRequest"] = closed(
        {
            "output_kind": {"enum": ["ADVISORY", "ADVISORY_JOB", "FORECAST"]},
            "output_id": {"type": "string", "format": "uuid"},
            "category": category,
            "safe_detail": {"type": "string", "minLength": 1, "maxLength": 1000, "pattern": r"\S"},
            "reviewer_id": {"type": "string", "format": "uuid"},
        }
    )
    schemas["AISafetyFeedback"] = closed(
        {
            "feedback_id": {"type": "string", "format": "uuid"},
            "output_kind": {"enum": ["ADVISORY", "ADVISORY_JOB", "FORECAST"]},
            "output_id": {"type": "string", "format": "uuid"},
            "category": category,
            "reviewer_id": {"type": "string", "format": "uuid"},
            "submitted_at": {"type": "string", "format": "date-time"},
            "source_payload_retained": {"const": False},
        }
    )
    schemas["AIShutdownRequest"] = closed(
        {
            "scope_kind": {"enum": ["USE_CASE", "CONFIGURATION", "DESTINATION"]},
            "scope_value": {"type": "string", "minLength": 1, "maxLength": 300},
            "action": {"enum": ["DISABLE", "REENABLE"]},
            "reason_category": category,
            "disabled_event_id": {"type": ["string", "null"], "format": "uuid"},
        }
    )
    schemas["AIShutdownResult"] = closed(
        {
            "event_id": {"type": "string", "format": "uuid"},
            "scope_kind": {"enum": ["USE_CASE", "CONFIGURATION", "DESTINATION"]},
            "scope_value": {"type": "string"},
            "state": {"enum": ["DISABLED", "ENABLED"]},
            "queued_jobs_stopped": {"type": "array", "items": {"type": "string", "format": "uuid"}},
            "running_jobs_cancellation_requested": {
                "type": "array",
                "items": {"type": "string", "format": "uuid"},
            },
            "affected_artifacts": {"type": "array"},
            "manual_workflows_enabled": {"const": True},
            "source_payload_retained": {"const": False},
            "occurred_at": {"type": "string", "format": "date-time"},
        }
    )
    schemas["AIShutdownStatus"] = closed(
        {
            "shutdowns": {"type": "array"},
            "affected_artifacts": {"type": "array"},
            "manual_workflows_enabled": {"const": True},
        }
    )
    schemas["AIRecoveryApprovalRequest"] = closed(
        {
            "fix_evidence_object_id": {"type": "string", "format": "uuid"},
            "fix_evidence_revision_id": {"type": "string", "format": "uuid"},
        }
    )
    schemas["AIRecoveryApproval"] = closed(
        {
            "shutdown_event_id": {"type": "string", "format": "uuid"},
            "fix_evidence_object_id": {"type": "string", "format": "uuid"},
            "fix_evidence_revision_id": {"type": "string", "format": "uuid"},
            "approved_by": {"type": "string", "format": "uuid"},
            "state": {"const": "REGRESSION_APPROVED"},
        }
    )
    extraction_location = closed(
        {
            "line": {"type": "integer", "minimum": 1},
            "section": {"type": ["string", "null"], "maxLength": 200},
        }
    )
    schemas["AIExtractionRequest"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "source_object_id": {"type": "string", "format": "uuid"},
            "source_revision_id": {"type": "string", "format": "uuid"},
            "policy_version": {"type": "integer", "minimum": 1},
            "language": {"type": "string", "pattern": LANGUAGE_PATTERN},
        }
    )
    schemas["AIExtractionDraft"] = closed(
        {
            "draft_id": {"type": "string", "format": "uuid"},
            "source_object_id": {"type": "string", "format": "uuid"},
            "source_revision_id": {"type": "string", "format": "uuid"},
            "proposals": {
                "type": "array",
                "maxItems": 500,
                "items": closed(
                    {
                        "proposal_id": {"type": "string", "format": "uuid"},
                        "field_key": {"type": "string"},
                        "proposed_value": {"type": "string"},
                        "classification": {"enum": ["EXTRACTED", "INFERRED", "SUGGESTED"]},
                        "location": extraction_location,
                        "evidence_span": {"type": "string"},
                        "conflict": {"type": "boolean"},
                    }
                ),
            },
            "missing_fields": {"type": "array", "items": {"type": "string"}},
            "activation_blocked": {"type": "boolean"},
            "domain_objects_changed": {"const": False},
        }
    )
    schemas["AIExtractionApplyRequest"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "selected_proposal_ids": {
                "type": "array",
                "maxItems": 100,
                "uniqueItems": True,
                "items": {"type": "string", "format": "uuid"},
            },
            "human_additions": {
                "type": "array",
                "maxItems": 20,
                "items": closed(
                    {
                        "field_key": {"type": "string", "minLength": 1, "maxLength": 100},
                        "value": {"type": "string", "minLength": 1, "maxLength": 2000},
                        "rationale": {"type": "string", "minLength": 1, "maxLength": 1000},
                    }
                ),
            },
        }
    )
    schemas["AIExtractionReview"] = closed(
        {
            "draft_id": {"type": "string", "format": "uuid"},
            "state": {"enum": ["BLOCKED", "READY_FOR_DOMAIN_DRAFT"]},
            "accepted_fields": {"type": "object"},
            "unresolved_fields": {"type": "array", "items": {"type": "string"}},
            "domain_objects_changed": {"const": False},
        }
    )
    indicator_source = {
        "operation_id": {"type": "string", "format": "uuid"},
        "library_definition_id": {"type": "string", "format": "uuid"},
        "library_definition_revision_id": {"type": "string", "format": "uuid"},
        "programme_id": {"type": "string", "format": "uuid"},
        "programme_revision_id": {"type": "string", "format": "uuid"},
        "policy_version": {"type": "integer", "minimum": 1},
        "language": {"type": "string", "pattern": LANGUAGE_PATTERN},
        "proxy_basis": {"enum": ["DIRECT", "PROXY"]},
    }
    schemas["AIIndicatorProposalRequest"] = closed(
        {key: value for key, value in indicator_source.items() if key != "operation_id"},
        [key for key in indicator_source if key != "operation_id"],
    )
    schemas["AIIndicatorProposal"] = closed(
        {
            "library_definition_id": {"type": "string", "format": "uuid"},
            "library_definition_revision_id": {"type": "string", "format": "uuid"},
            "proposed_fields": {"type": "object"},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "programme_context": {"type": "object"},
            "model_confidence": {"type": "null"},
            "can_approve": {"const": False},
            "standard_mapping_created": {"const": False},
        }
    )
    schemas["AIIndicatorDraftRequest"] = closed(
        {
            **indicator_source,
            "selected_fields": {
                "type": "array",
                "minItems": 1,
                "maxItems": 20,
                "uniqueItems": True,
                "items": {"type": "string", "minLength": 1, "maxLength": 100},
            },
        },
        [*indicator_source, "selected_fields"],
    )
    schemas["AIIndicatorDraftReceipt"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "object_id": {"type": "string", "format": "uuid"},
            "revision_id": {"type": "string", "format": "uuid"},
            "business_state": {"const": "Draft"},
            "saved_at": {"type": "string", "format": "date-time"},
            "correlation_id": {"type": "string"},
            "source_definition_revision_id": {"type": "string", "format": "uuid"},
            "programme_revision_id": {"type": "string", "format": "uuid"},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "submit_ready": {"type": "boolean"},
            "standard_mapping_created": {"const": False},
        }
    )
    schemas["AIImportProposalRequest"] = closed(
        {
            "policy_version": {"type": "integer", "minimum": 1},
            "language": {"type": "string", "pattern": LANGUAGE_PATTERN},
        },
        ["policy_version", "language"],
    )
    schemas["AIImportProposals"] = closed(
        {
            "batch_id": {"type": "string", "format": "uuid"},
            "batch_revision_id": {"type": "string", "format": "uuid"},
            "raw_sha256": {"type": ["string", "null"]},
            "current_mapping": {"type": ["object", "null"]},
            "proposals": {"type": "array", "maxItems": 200},
            "destructive_actions_available": {"const": False},
        }
    )
    schemas["AIImportApplyRequest"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "policy_version": {"type": "integer", "minimum": 1},
            "language": {"type": "string", "pattern": LANGUAGE_PATTERN},
            "selected_proposal_ids": {
                "type": "array",
                "maxItems": 200,
                "uniqueItems": True,
                "items": {"type": "string", "format": "uuid"},
            },
        },
        ["operation_id", "policy_version", "language", "selected_proposal_ids"],
    )
    schemas["AIImportApplyReceipt"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "object_id": {"type": "string", "format": "uuid"},
            "revision_id": {"type": "string", "format": "uuid"},
            "business_state": {"const": "Draft"},
            "saved_at": {"type": "string", "format": "date-time"},
            "correlation_id": {"type": "string"},
            "raw_sha256": {"type": ["string", "null"]},
            "mapping_diff": {"type": "object"},
            "applied_proposal_ids": {"type": "array"},
            "raw_rows_changed": {"const": False},
            "identities_merged": {"const": False},
            "approved_actuals_changed": {"const": False},
        }
    )
    schemas["AIEvidenceQuestionRequest"] = closed(
        {
            "question": {"type": "string", "minLength": 1, "maxLength": 2000, "pattern": r"\S"},
            "programme_id": {"type": ["string", "null"], "format": "uuid"},
            "programme_revision_id": {"type": ["string", "null"], "format": "uuid"},
            "period_id": {"type": ["string", "null"], "format": "uuid"},
            "period_revision_id": {"type": ["string", "null"], "format": "uuid"},
            "source_mode": {"type": ["string", "null"], "enum": ["SELECTED_GOVERNED_RESULTS", None]},
            "sources": {
                "type": "array",
                "maxItems": 20,
                "uniqueItems": True,
                "items": closed(
                    {
                        "object_id": {"type": "string", "format": "uuid"},
                        "revision_id": {"type": "string", "format": "uuid"},
                    },
                    ["object_id", "revision_id"],
                ),
            },
            "policy_version": {"type": "integer", "minimum": 1},
            "language": {"type": "string", "pattern": LANGUAGE_PATTERN},
        },
        [
            "question",
            "programme_id",
            "programme_revision_id",
            "period_id",
            "period_revision_id",
            "source_mode",
            "sources",
            "policy_version",
            "language",
        ],
    )
    evidence_claim = closed(
        {
            "text": {"type": "string", "maxLength": 500},
            "citation_numbers": {
                "type": "array",
                "minItems": 1,
                "maxItems": 20,
                "uniqueItems": True,
                "items": {"type": "integer", "minimum": 1},
            },
            "material": {"const": True},
        },
        ["text", "citation_numbers", "material"],
    )
    evidence_citation = closed(
        {
            "number": {"type": "integer", "minimum": 1},
            "object_id": {"type": "string", "format": "uuid"},
            "revision_id": {"type": "string", "format": "uuid"},
            "object_type": {"const": "CalculatedResult"},
            "location": {"type": "string", "pattern": "^/"},
        },
        ["number", "object_id", "revision_id", "object_type", "location"],
    )
    evidence_contradiction = closed(
        {
            "field": {"type": "string", "maxLength": 100},
            "indicator_id": {"type": "string", "format": "uuid"},
            "values": {
                "type": "array",
                "minItems": 2,
                "maxItems": 20,
                "uniqueItems": True,
                "items": {"type": "string", "maxLength": 500},
            },
        },
        ["field", "indicator_id", "values"],
    )
    schemas["AIEvidenceQuestionAnswer"] = closed(
        {
            "state": {"enum": ["ANSWERED", "CLARIFICATION_REQUIRED", "ABSTAINED"]},
            "answer": {"type": ["string", "null"], "maxLength": 12000},
            "clarification_fields": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
            "claims": {"type": "array", "maxItems": 160, "items": evidence_claim},
            "citations": {"type": "array", "maxItems": 160, "items": evidence_citation},
            "missing_evidence": {"type": "array", "maxItems": 20, "items": {"type": "string"}},
            "contradictions": {
                "type": "array",
                "maxItems": 80,
                "items": evidence_contradiction,
            },
            "official_number_guessed": {"const": False},
            "protected_resource_confirmed": {"const": False},
            "fabricated_citations": {"const": False},
        },
        [
            "state",
            "answer",
            "clarification_fields",
            "claims",
            "citations",
            "missing_evidence",
            "contradictions",
            "official_number_guessed",
            "protected_resource_confirmed",
            "fabricated_citations",
        ],
    )
    analysis_source = closed(
        {
            "object_id": {"type": "string", "format": "uuid"},
            "revision_id": {"type": "string", "format": "uuid"},
        },
        ["object_id", "revision_id"],
    )
    analysis_plan = closed(
        {
            "measure": {"const": "POOLED_PERCENTAGE"},
            "sources": {
                "type": "array",
                "minItems": 2,
                "maxItems": 20,
                "uniqueItems": True,
                "items": analysis_source,
            },
            "filters": closed({}),
            "period_id": {"type": "string", "format": "uuid"},
            "period_revision_id": {"type": "string", "format": "uuid"},
            "dimensions": {
                "type": "array",
                "maxItems": 0,
                "uniqueItems": True,
                "items": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]{0,63}$"},
            },
            "source_mode": {"enum": ["OFFICIAL", "PROVISIONAL"]},
            "permitted_operation": {"const": "POOL_RATIO"},
        },
        [
            "measure",
            "sources",
            "filters",
            "period_id",
            "period_revision_id",
            "dimensions",
            "source_mode",
            "permitted_operation",
        ],
    )
    schemas["AINumericAnalysisRequest"] = closed(
        {
            "question": {"type": "string", "minLength": 1, "maxLength": 2000, "pattern": r"\S"},
            "plan": analysis_plan,
            "drafted_claim": {"type": ["string", "null"], "maxLength": 500},
            "policy_version": {"type": "integer", "minimum": 1},
            "language": {"type": "string", "pattern": LANGUAGE_PATTERN},
        },
        ["question", "plan", "drafted_claim", "policy_version", "language"],
    )
    schemas["AINumericAnalysisResult"] = closed(
        {
            "state": {"const": "ANSWERED"},
            "plan": analysis_plan,
            "answer": {"type": "string", "maxLength": 500},
            "value": {"type": "string", "pattern": "^-?[0-9]+\\.[0-9]{2}$"},
            "unit": {"const": "percent"},
            "numerator": {"type": "string"},
            "denominator": {"type": "string"},
            "result_references": {
                "type": "array",
                "minItems": 2,
                "maxItems": 20,
                "items": closed(
                    {
                        "object_id": {"type": "string", "format": "uuid"},
                        "revision_id": {"type": "string", "format": "uuid"},
                        "numerator": {"type": "string", "pattern": "^[0-9]+(?:\\.[0-9]+)?$"},
                        "denominator": {"type": "string", "pattern": "^[0-9]+(?:\\.[0-9]+)?$"},
                    },
                    ["object_id", "revision_id", "numerator", "denominator"],
                ),
            },
            "calculation_receipt": closed(
                {
                    "receipt_id": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "tool": {"const": "governed.pool_ratio.v1"},
                    "precision_digits": {"const": 100},
                    "rounding_rule": {"const": "HALF_UP"},
                    "operation": {"const": "POOL_RATIO"},
                },
                ["receipt_id", "tool", "precision_digits", "rounding_rule", "operation"],
            ),
            "model_recomputed": {"const": False},
            "arbitrary_query_executed": {"const": False},
            "official_claim_matches_tool": {"const": True},
        },
        [
            "state",
            "plan",
            "answer",
            "value",
            "unit",
            "numerator",
            "denominator",
            "result_references",
            "calculation_receipt",
            "model_recomputed",
            "arbitrary_query_executed",
            "official_claim_matches_tool",
        ],
    )
    safety_base = "/v1/tenants/{tenant_id}/ai-enablement"
    safety_ops = [
        (
            "post",
            safety_base + "/safety-feedback",
            "create_ai_safety_feedback",
            "ai.advisory.request",
            "AISafetyFeedbackRequest",
            "AISafetyFeedback",
            ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
        ),
        (
            "get",
            safety_base + "/safety-shutdowns",
            "get_ai_safety_shutdowns",
            "ai.policy.manage",
            None,
            "AIShutdownStatus",
            ["TENANT_ADMIN"],
        ),
        (
            "post",
            safety_base + "/safety-shutdowns",
            "manage_ai_safety_shutdown",
            "ai.policy.manage",
            "AIShutdownRequest",
            "AIShutdownResult",
            ["TENANT_ADMIN"],
        ),
        (
            "post",
            safety_base + "/safety-shutdowns/{event_id}/actions/approve-recovery",
            "approve_ai_safety_recovery",
            "ai.policy.manage",
            "AIRecoveryApprovalRequest",
            "AIRecoveryApproval",
            ["TENANT_ADMIN"],
        ),
    ]
    for method, path, operation, capability, request, response, roles in safety_ops:
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "AI safety containment record",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ["400", "401", "403", "404", "409", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        parameters = [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
        if "{event_id}" in path:
            parameters.append(
                {
                    "name": "event_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            )
        node = spec["paths"].setdefault(path, {"parameters": parameters})
        node[method] = entry
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": capability,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": 300
                if operation in {"manage_ai_safety_shutdown", "approve_ai_safety_recovery"}
                else None,
                "audit": False,
            }
        )
    extraction_base = "/v1/tenants/{tenant_id}/ai-enablement/extractions"
    extraction_ops = [
        (
            "post",
            extraction_base,
            "create_ai_extraction",
            "AIExtractionRequest",
            "AIExtractionDraft",
        ),
        (
            "post",
            extraction_base + "/{draft_id}/actions/apply",
            "review_ai_extraction",
            "AIExtractionApplyRequest",
            "AIExtractionReview",
        ),
    ]
    for method, path, operation, request, response in extraction_ops:
        parameters = [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
        if "{draft_id}" in path:
            parameters.append(
                {
                    "name": "draft_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            )
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": "ai.advisory.request",
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            },
            "responses": {
                "200": {
                    "description": "Traceable review-only extraction",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        for status in ["400", "401", "403", "404", "409", "422", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"][path] = {"parameters": parameters, method: entry}
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": "ai.advisory.request",
                "role_templates": ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )
    indicator_base = "/v1/tenants/{tenant_id}/ai-enablement/indicator-design"
    for path, operation, request, response, capability in [
        (
            indicator_base + "/proposals",
            "create_ai_indicator_proposal",
            "AIIndicatorProposalRequest",
            "AIIndicatorProposal",
            "ai.advisory.request",
        ),
        (
            indicator_base + "/drafts",
            "create_ai_indicator_draft",
            "AIIndicatorDraftRequest",
            "AIIndicatorDraftReceipt",
            "indicator-definitions.draft.create",
        ),
    ]:
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            },
            "responses": {
                "200": {
                    "description": "Governed indicator design result",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        for status in ["400", "401", "403", "404", "409", "422", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"][path] = {
            "parameters": [
                {
                    "name": "tenant_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            "post": entry,
        }
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": "POST",
                "path": path,
                "capability": capability,
                "role_templates": ["MEL_ADMIN"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": operation == "create_ai_indicator_draft",
            }
        )
    import_base = "/v1/tenants/{tenant_id}/ai-enablement/import-assistance/{batch_id}/revisions/{revision_id}"
    for suffix, operation, request, response, capability in [
        (
            "/proposals",
            "create_ai_import_proposals",
            "AIImportProposalRequest",
            "AIImportProposals",
            "imports.read",
        ),
        (
            "/actions/apply",
            "apply_ai_import_proposals",
            "AIImportApplyRequest",
            "AIImportApplyReceipt",
            "imports.draft.edit",
        ),
    ]:
        path = import_base + suffix
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            },
            "responses": {
                "200": {
                    "description": "Non-destructive import assistance result",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        for status in ["400", "401", "403", "404", "409", "422", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"][path] = {
            "parameters": [
                {
                    "name": name,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
                for name in ["tenant_id", "batch_id", "revision_id"]
            ],
            "post": entry,
        }
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": "POST",
                "path": path,
                "capability": capability,
                "role_templates": ["DATA_STEWARD", "MEL_ADMIN"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": operation == "apply_ai_import_proposals",
            }
        )
    question_path = "/v1/tenants/{tenant_id}/ai-enablement/evidence-questions"
    spec["paths"][question_path] = {
        "parameters": [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ],
        "post": {
            "operationId": "answer_ai_evidence_question",
            "summary": "answer evidence question",
            "x-capability": "ai.advisory.request",
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIEvidenceQuestionRequest"}}
                },
            },
            "responses": {
                "200": {
                    "description": "Cited answer, clarification or bounded abstention",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AIEvidenceQuestionAnswer"}
                        }
                    },
                },
                **{
                    status: {
                        "description": "Request refused",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
                    }
                    for status in ["400", "401", "403", "409", "422", "503"]
                },
            },
        },
    }
    policy["operations"].append(
        {
            "operation_id": "answer_ai_evidence_question",
            "method": "POST",
            "path": question_path,
            "capability": "ai.advisory.request",
            "role_templates": ["PROGRAMME_MANAGER", "MEL_ADMIN"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
    analysis_path = "/v1/tenants/{tenant_id}/ai-enablement/numeric-analysis"
    spec["paths"][analysis_path] = {
        "parameters": [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ],
        "post": {
            "operationId": "execute_ai_numeric_analysis",
            "summary": "execute governed numeric analysis",
            "x-capability": "calculated-results.read",
            "x-contract-version": VERSION,
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AINumericAnalysisRequest"}}
                },
            },
            "responses": {
                "200": {
                    "description": "Deterministic typed analysis result",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AINumericAnalysisResult"}
                        }
                    },
                },
                **{
                    status: {
                        "description": "Request refused",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
                    }
                    for status in ["400", "401", "403", "404", "409", "422", "503"]
                },
            },
        },
    }
    policy["operations"].append(
        {
            "operation_id": "execute_ai_numeric_analysis",
            "method": "POST",
            "path": analysis_path,
            "capability": "calculated-results.read",
            "role_templates": ["ANALYST", "MEL_ADMIN"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": False,
        }
    )
    forecast_base = "/v1/tenants/{tenant_id}/ai-enablement/forecasts"
    forecast_ops = [
        ("post", forecast_base, "create_ai_forecast", "AIForecastRequest", "AIForecast"),
        ("get", forecast_base + "/{scenario_id}", "get_ai_forecast", None, "AIForecast"),
        ("get", forecast_base + "/{scenario_id}/export", "export_ai_forecast", None, "AIForecastExport"),
        (
            "post",
            forecast_base + "/{scenario_id}/versions/{version}/actions/request-adoption",
            "request_ai_forecast_adoption",
            None,
            "AIForecastAdoptionReview",
        ),
    ]
    for method, path, operation, request, response in forecast_ops:
        parameters = [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
        if "{scenario_id}" in path:
            parameters.append(
                {
                    "name": "scenario_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            )
        if "{version}" in path:
            parameters.append(
                {
                    "name": "version",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer", "minimum": 1},
                }
            )
        elif method == "get":
            parameters.append(
                {
                    "name": "version",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer", "minimum": 1},
                }
            )
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": "ai.advisory.request",
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "Versioned forecast planning artifact",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ["400", "401", "403", "404", "409"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"][path] = {"parameters": parameters, method: entry}
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": "ai.advisory.request",
                "role_templates": ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )
    for method, route, op, cap, request, response, roles in [
        (
            "get",
            "ai-enablement/catalog",
            "get_ai_enablement_catalog",
            "ai.enablement.read",
            None,
            "AIEnablementCatalog",
            ROLES,
        ),
        (
            "post",
            "ai-enablement/assessment",
            "assess_ai_enablement",
            "ai.enablement.read",
            "AIAssessmentRequest",
            "AIEnablementAssessment",
            ROLES,
        ),
        (
            "get",
            "ai-enablement/solutions",
            "get_ai_solutions",
            "ai.enablement.read",
            None,
            "AISolutionsCatalog",
            ROLES,
        ),
        (
            "post",
            "ai-enablement/advisory",
            "create_ai_advisory",
            "ai.advisory.request",
            "AIAdvisoryRequest",
            "AIAdvisoryDraft",
            ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
        ),
    ]:
        path = "/v1/tenants/{tenant_id}/" + route
        node = {
            "parameters": [
                {
                    "name": "tenant_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            ]
        }
        entry = {
            "operationId": op,
            "summary": op.replace("_", " "),
            "x-capability": cap,
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "Editorial content or unapproved draft",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ["400", "401", "403", "404", "409", "429", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        node[method] = entry
        spec["paths"][path] = node
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": path,
                "capability": cap,
                "role_templates": deepcopy(roles),
                "purpose_required": op == "create_ai_advisory",
                "fresh_assurance_seconds": None,
                "audit": op == "create_ai_advisory",
            }
        )
    job_base = "/v1/tenants/{tenant_id}/ai-enablement/advisory-jobs"
    for method, path, operation in [
        ("post", job_base, "create_ai_advisory_job"),
        ("get", job_base + "/{job_id}", "get_ai_advisory_job"),
        ("post", job_base + "/{job_id}/actions/cancel", "cancel_ai_advisory_job"),
    ]:
        parameters = [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
        if "{job_id}" in path:
            parameters.append(
                {
                    "name": "job_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            )
        success = "202" if operation == "create_ai_advisory_job" else "200"
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": "ai.advisory.request",
            "x-contract-version": VERSION,
            "responses": {
                success: {
                    "description": "Durable AI job",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/AIAdvisoryJob"}}
                    },
                }
            },
        }
        if operation == "create_ai_advisory_job":
            entry["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/AIAdvisoryRequest"}}
                },
            }
        for status in ["400", "401", "403", "404", "409", "429", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"][path] = {"parameters": parameters, method: entry}
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": "ai.advisory.request",
                "role_templates": ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )
    policy_paths(spec, policy)
    ranking_paths(spec, policy)


def assessment_schemas(schemas):
    strings = {"type": "array", "maxItems": 100, "items": {"type": "string", "maxLength": 1000}}
    score = {
        "dimension_id": {
            "enum": [
                "DATA_FOUNDATION",
                "PEOPLE_AND_SKILLS",
                "GOVERNANCE_AND_SAFETY",
                "WORKFLOW_FIT",
                "DELIVERY_CAPACITY",
            ]
        },
        "score": {"type": "integer", "minimum": 1, "maximum": 5},
        "level": {"enum": ["FOUNDATION_NEEDED", "EARLY", "DEVELOPING", "PREPARED", "ESTABLISHED"]},
        "scale_min": {"const": 1},
        "scale_max": {"const": 5},
        "explanation": {"type": "string", "minLength": 1, "maxLength": 1000},
        "rule_id": {"type": "string", "pattern": "^DR-[A-Z]+-[0-9]{2}$"},
        "input_fields": {
            "type": "array",
            "minItems": 1,
            "maxItems": 6,
            "uniqueItems": True,
            "items": {
                "enum": [
                    "sector",
                    "team_size",
                    "goal",
                    "data_readiness",
                    "ai_experience",
                    "sensitive_data",
                ]
            },
        },
        "self_reported": {"const": True},
    }
    schemas["AIMaturityScore"] = closed(score, list(score))
    framework = {
        "framework_id": {"const": "IMPRANA_DIGITAL_READINESS"},
        "framework_version": {"const": "2026-10-v1-editorial-draft"},
        "framework_status": {"const": "EDITORIAL_DRAFT"},
        "method": {"const": "DETERMINISTIC_SELF_REPORT_RULES"},
        "scores": {
            "type": "array",
            "minItems": 5,
            "maxItems": 5,
            "items": {"$ref": "#/components/schemas/AIMaturityScore"},
        },
        "limitations": deepcopy(strings),
    }
    schemas["AIMaturityFrameworkResult"] = closed(framework, list(framework))
    recommendation = {
        "use_case_id": {"type": "string", "maxLength": 100},
        "priority": {"type": "integer", "minimum": 1},
        "status": {"type": "string", "maxLength": 100},
        "reasons": deepcopy(strings),
        "capacity_gaps": deepcopy(strings),
        "human_approval_needs": deepcopy(strings),
    }
    schemas["AIEnablementRecommendation"] = closed(recommendation, list(recommendation))
    payload = {
        "schema_version": {"type": "string"},
        "content_version": {"type": "string"},
        "method": {"const": "DETERMINISTIC_RULES"},
        "maturity_framework": {"$ref": "#/components/schemas/AIMaturityFrameworkResult"},
        "readiness": closed(
            {"stage": {"type": "string"}, "reasons": deepcopy(strings)},
            ["stage", "reasons"],
        ),
        "recommendations": {
            "type": "array",
            "maxItems": 100,
            "items": {"$ref": "#/components/schemas/AIEnablementRecommendation"},
        },
        "capacity_gaps": deepcopy(strings),
        "learning_path_ids": deepcopy(strings),
        "next_steps": deepcopy(strings),
        "human_approval_needs": deepcopy(strings),
        "limitations": deepcopy(strings),
    }
    schemas["AIEnablementAssessmentPayload"] = closed(payload, list(payload))
    schemas["AIEnablementAssessment"] = closed(
        {"assessment": {"$ref": "#/components/schemas/AIEnablementAssessmentPayload"}},
        ["assessment"],
    )


def _strings(enum=None, pattern=None, maximum=10, length=None):
    items = {"type": "string"}
    if enum is not None:
        items = {"enum": list(enum)}
    if pattern:
        items["pattern"] = pattern
    if length:
        items.update(minLength=1, maxLength=length)
    return {"type": "array", "maxItems": maximum, "uniqueItems": True, "items": items}


def policy_schemas(schemas):
    """Closed schemas of the versioned tenant AI policy (FR-AI-001, migration 0041)."""
    rule = {
        "use_case": {"enum": list(USE_CASES)},
        "enabled": {"type": "boolean"},
        "data_classes": _strings(DATA_CLASSES, maximum=len(DATA_CLASSES)),
        "destinations": _strings(DESTINATIONS, maximum=10),
        "purposes": _strings(maximum=10, length=200),
        "languages": _strings(pattern=LANGUAGE_PATTERN, maximum=20),
        "review_mode": {"enum": list(REVIEW_MODES)},
        "budget_units": {"type": "integer", "minimum": 0, "maximum": MAX_BUDGET_UNITS},
        # Use-case enablement never implies a tool. Each reviewed tool identifier is named separately,
        # and require() refuses any requested tool absent from this exact rule.
        "tools": {
            "type": "array",
            "maxItems": 20,
            "uniqueItems": True,
            "items": {"type": "string", "pattern": TOOL_PATTERN},
        },
    }
    schemas["AIUseCasePolicy"] = closed(rule, list(rule))
    schemas["AIPolicyData"] = closed(
        {
            "use_cases": {
                "type": "array",
                "maxItems": len(USE_CASES),
                "items": {"$ref": "#/components/schemas/AIUseCasePolicy"},
            }
        },
        ["use_cases"],
    )
    command = {
        "operation_id": {"type": "string", "format": "uuid"},
        # 0 when the tenant has no policy yet; otherwise the version the editor was opened on.
        "expected_version": {"type": "integer", "minimum": 0, "maximum": MAX_POLICY_VERSION},
        "data": {"$ref": "#/components/schemas/AIPolicyData"},
    }
    schemas["AIPolicyCommand"] = closed(command, list(command))
    destination = {
        "id": {"enum": list(DESTINATIONS)},
        "provider": {"type": "string"},
        "region": {"type": "string"},
    }
    schemas["AIPolicyDestination"] = closed(destination, list(destination))
    nullable_uuid = {"type": ["string", "null"], "format": "uuid"}
    version = {
        "policy_version": {"type": "integer", "minimum": 0, "maximum": MAX_POLICY_VERSION},
        "policy_version_id": deepcopy(nullable_uuid),
        "created_at": {"type": ["string", "null"], "format": "date-time"},
        "created_by": deepcopy(nullable_uuid),
        "use_cases": {
            "type": "array",
            "maxItems": len(USE_CASES),
            "items": {"$ref": "#/components/schemas/AIUseCasePolicy"},
        },
    }
    schemas["AIPolicyRevision"] = closed(version, list(version))
    view = {
        **deepcopy(version),
        "server_enabled": {"type": "boolean"},
        "advisory_available": {"type": "boolean"},
        "destinations": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/AIPolicyDestination"},
        },
        "reserved_use_cases": {"type": "array", "items": {"enum": list(USE_CASES)}},
    }
    schemas["AIPolicy"] = closed(view, list(view))
    schemas["AIPolicyRevisionList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIPolicyRevision"},
            },
            "next_cursor": {"type": ["string", "null"]},
        },
        ["items", "next_cursor"],
    )
    receipt = {
        "object_id": {"type": "string", "format": "uuid"},
        "revision_id": {"type": "string", "format": "uuid"},
        "policy_version": {"type": "integer", "minimum": 1, "maximum": MAX_POLICY_VERSION},
        "policy_version_id": {"type": "string", "format": "uuid"},
        "business_state": {"const": "Active"},
        "saved_at": {"type": "string", "format": "date-time"},
        "operation_id": {"type": "string", "format": "uuid"},
        "correlation_id": {"type": "string", "format": "uuid"},
    }
    schemas["AIPolicyReceipt"] = closed(receipt, list(receipt))


def policy_paths(spec, policy):
    """GET and PUT .../ai-enablement/policy and GET .../policy/revisions."""
    for method, suffix, op, cap, request, response, roles, fresh in [
        ("get", "", "get_ai_policy", "ai.enablement.read", None, "AIPolicy", ROLES, None),
        (
            "put",
            "",
            "update_ai_policy",
            POLICY_CAPABILITY,
            "AIPolicyCommand",
            "AIPolicyReceipt",
            POLICY_MANAGERS,
            300,
        ),
        (
            "get",
            "/revisions",
            "list_ai_policy_revisions",
            "ai.enablement.read",
            None,
            "AIPolicyRevisionList",
            ROLES,
            None,
        ),
    ]:
        path = "/v1/tenants/{tenant_id}/ai-enablement/policy" + suffix
        parameters = [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
        if op == "list_ai_policy_revisions":
            parameters += [
                {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100}},
                {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
            ]
        entry = {
            "operationId": op,
            "summary": op.replace("_", " "),
            "x-capability": cap,
            "x-contract-version": POLICY_VERSION,
            "parameters": parameters,
            "responses": {
                "200": {
                    "description": "The policy in force, its history or the new version's receipt",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ["400", "401", "403", "404", "409", "422", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": path,
                "capability": cap,
                "role_templates": deepcopy(roles),
                "purpose_required": False,
                "fresh_assurance_seconds": fresh,
                "audit": op == "update_ai_policy",
            }
        )


def ranking_schemas(schemas):
    """Closed schemas of the ranking weights and the weighted opportunity ranking (US-MP-03).

    The total of 100 cannot be expressed in JSON Schema; the server refuses any other total with
    422 AI_RANKING_WEIGHTS_TOTAL and keeps the weights in force."""
    weight = {"type": "integer", "minimum": 0, "maximum": 100}
    schemas["AIRankingWeightsData"] = closed({field: dict(weight) for field in WEIGHT_FIELDS}, WEIGHT_FIELDS)
    nullable_uuid = {"type": ["string", "null"], "format": "uuid"}
    command = {
        "operation_id": {"type": "string", "format": "uuid"},
        # null while the organisation has never saved weights; otherwise the revision the editor showed.
        "expected_revision": deepcopy(nullable_uuid),
        "data": {"$ref": "#/components/schemas/AIRankingWeightsData"},
    }
    schemas["AIRankingWeightsCommand"] = closed(command, list(command))
    view = {
        # UNREADABLE: saved weights that do not read back exactly; revision_id names them so that a
        # manager can replace them, weights is null and every ranking answers 503 until then.
        "source": {"enum": ["DEFAULT", "SAVED", "UNREADABLE"]},
        "revision_id": deepcopy(nullable_uuid),
        "weights": {"anyOf": [{"$ref": "#/components/schemas/AIRankingWeightsData"}, {"type": "null"}]},
        "saved_at": {"type": ["string", "null"], "format": "date-time"},
        "saved_by": deepcopy(nullable_uuid),
    }
    schemas["AIRankingWeights"] = closed(view, list(view))
    receipt = {
        "object_id": {"type": "string", "format": "uuid"},
        "revision_id": {"type": "string", "format": "uuid"},
        "business_state": {"const": "Active"},
        "saved_at": {"type": "string", "format": "date-time"},
        "operation_id": {"type": "string", "format": "uuid"},
        "correlation_id": {"type": "string", "format": "uuid"},
    }
    schemas["AIRankingWeightsReceipt"] = closed(receipt, list(receipt))
    schemas["AIRankingRequest"] = closed(
        {"profile": {"$ref": "#/components/schemas/AIEnablementProfile"}}, ["profile"]
    )
    score = {"type": "integer", "minimum": 1, "maximum": 5}
    schemas["AIOpportunityScores"] = closed({field: dict(score) for field in WEIGHT_FIELDS}, WEIGHT_FIELDS)
    item = {
        "rank": {"type": "integer", "minimum": 1},
        "use_case_id": {"type": "string"},
        "scores": {"$ref": "#/components/schemas/AIOpportunityScores"},
        # Exact decimal string, 0.00 to 100.00.
        "weighted_total": {"type": "string", "pattern": "^(100\\.00|[0-9]{1,2}\\.[0-9]{2})$"},
        "readiness_gaps": {"type": "array", "items": {"type": "string"}},
    }
    schemas["AIRankedOpportunity"] = closed(item, list(item))
    unranked = {
        "use_case_id": {"type": "string"},
        "missing_scores": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {"enum": ["impact", "effort", "cost"]},
        },
    }
    schemas["AIUnrankedOpportunity"] = closed(unranked, list(unranked))
    ranking = {
        "method": {"const": "WEIGHTED_EDITORIAL_SCORES"},
        "content_version": {"type": "string"},
        "score_version": {"type": "string"},
        "score_status": {"type": "string"},
        "weights": {"$ref": "#/components/schemas/AIRankingWeightsData"},
        "weights_source": {"enum": ["DEFAULT", "SAVED"]},
        "weights_revision_id": deepcopy(nullable_uuid),
        "items": {"type": "array", "items": {"$ref": "#/components/schemas/AIRankedOpportunity"}},
        "unranked": {"type": "array", "items": {"$ref": "#/components/schemas/AIUnrankedOpportunity"}},
    }
    schemas["AIOpportunityRanking"] = closed(ranking, list(ranking))


def ranking_paths(spec, policy):
    """GET and PUT .../ai-enablement/ranking-weights and POST .../ai-enablement/ranking."""
    for method, route, op, cap, request, response, roles, audited in [
        (
            "get",
            "ai-enablement/ranking-weights",
            "get_ai_ranking_weights",
            "ai.enablement.read",
            None,
            "AIRankingWeights",
            ROLES,
            False,
        ),
        (
            "put",
            "ai-enablement/ranking-weights",
            "update_ai_ranking_weights",
            "ai.enablement.manage",
            "AIRankingWeightsCommand",
            "AIRankingWeightsReceipt",
            RANKING_MANAGERS,
            True,
        ),
        (
            "post",
            "ai-enablement/ranking",
            "rank_ai_opportunities",
            "ai.enablement.read",
            "AIRankingRequest",
            "AIOpportunityRanking",
            ROLES,
            False,
        ),
    ]:
        path = "/v1/tenants/{tenant_id}/" + route
        entry = {
            "operationId": op,
            "summary": op.replace("_", " "),
            "x-capability": cap,
            "x-contract-version": RANKING_VERSION,
            "parameters": [
                {
                    "name": "tenant_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            ],
            "responses": {
                "200": {
                    "description": "The weights in force, the new revision's receipt or the ranking",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ["400", "401", "403", "404", "409", "422", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": path,
                "capability": cap,
                "role_templates": deepcopy(roles),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": audited,
            }
        )
