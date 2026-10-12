"""Separate the implemented domain API from the larger design contract."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api"))
from impact_api.contracts import SPEC  # noqa: E402
from impact_api.ai_enablement_contracts import IMPLEMENTED as AI_ENABLEMENT_ROUTES  # noqa: E402
from impact_api.ai_adoption_contracts import IMPLEMENTED as AI_ADOPTION_ROUTES  # noqa: E402
from impact_api.ai_diagnosis_contracts import IMPLEMENTED as AI_DIAGNOSIS_ROUTES  # noqa: E402
from impact_api.ai_diagnosis_contribution_contracts import (  # noqa: E402
    IMPLEMENTED as AI_DIAGNOSIS_CONTRIBUTION_ROUTES,
)
from impact_api.ai_diagnosis_review_contracts import (  # noqa: E402
    IMPLEMENTED as AI_DIAGNOSIS_REVIEW_ROUTES,
)
from impact_api.ai_solution_shortlist_contracts import IMPLEMENTED as AI_SOLUTION_SHORTLIST_ROUTES  # noqa: E402
from impact_api.ai_solution_fit_score_contracts import IMPLEMENTED as AI_SOLUTION_FIT_SCORE_ROUTES  # noqa: E402
from impact_api.ai_vetting_contracts import IMPLEMENTED as AI_VETTING_ROUTES  # noqa: E402
from impact_api.ai_problem_baseline_contracts import (  # noqa: E402
    IMPLEMENTED as AI_PROBLEM_BASELINE_ROUTES,
)
from impact_api.ai_outcome_observation_contracts import IMPLEMENTED as AI_OUTCOME_OBSERVATION_ROUTES  # noqa: E402
from impact_api.ai_sponsor_value_report_contracts import IMPLEMENTED as AI_SPONSOR_VALUE_REPORT_ROUTES  # noqa: E402
from impact_api.ai_quarterly_value_review_contracts import IMPLEMENTED as AI_QUARTERLY_VALUE_REVIEW_ROUTES  # noqa: E402
from impact_api.ai_next_opportunity_contracts import IMPLEMENTED as AI_NEXT_OPPORTUNITY_ROUTES  # noqa: E402
from impact_api.ai_outcome_evidence_contracts import (  # noqa: E402
    TENANT_IMPLEMENTED as AI_OUTCOME_EVIDENCE_TENANT_ROUTES,
    PLATFORM_IMPLEMENTED as AI_OUTCOME_EVIDENCE_PLATFORM_ROUTES,
)
from impact_api.discoverability_contracts import IMPLEMENTED as DISCOVERABILITY_ROUTES  # noqa: E402
from impact_api.population_overlap_contracts import IMPLEMENTED as POPULATION_OVERLAP_ROUTES  # noqa: E402
from impact_api.hierarchical_aggregation_contracts import IMPLEMENTED as HIERARCHICAL_AGGREGATION_ROUTES  # noqa: E402
from impact_api.dimension_crosswalk_contracts import IMPLEMENTED as DIMENSION_CROSSWALK_ROUTES  # noqa: E402
from impact_api.formula_authoring_contracts import IMPLEMENTED as FORMULA_AUTHORING_ROUTES  # noqa: E402
from impact_api.portfolio_attribution_contracts import IMPLEMENTED as PORTFOLIO_ATTRIBUTION_ROUTES  # noqa: E402
from impact_api.sponsored_access_contracts import IMPLEMENTED as SPONSORED_ACCESS_ROUTES  # noqa: E402
from impact_api.entitlement_view_contracts import IMPLEMENTED as ENTITLEMENT_VIEW_ROUTES  # noqa: E402
from impact_api.service_package_contracts import IMPLEMENTED as SERVICE_PACKAGE_ROUTES  # noqa: E402
from impact_api.tax_invoicing_contracts import IMPLEMENTED as TAX_INVOICING_ROUTES  # noqa: E402
from impact_api.agreement_coverage_contracts import IMPLEMENTED as AGREEMENT_COVERAGE_ROUTES  # noqa: E402
from impact_api.ai_opportunity_mapping_contracts import (  # noqa: E402
    IMPLEMENTED as AI_OPPORTUNITY_MAPPING_ROUTES,
)
from impact_api.ai_value_case_contracts import IMPLEMENTED as AI_VALUE_CASE_ROUTES  # noqa: E402
from impact_api.ai_value_case_export_contracts import (  # noqa: E402
    IMPLEMENTED as AI_VALUE_CASE_EXPORT_ROUTES,
)
from impact_api.ai_value_case_version_contracts import (  # noqa: E402
    IMPLEMENTED as AI_VALUE_CASE_VERSION_ROUTES,
)
from impact_api.ai_content_contracts import IMPLEMENTED as AI_CONTENT_ROUTES  # noqa: E402
from impact_api.ai_impact_reference_contracts import IMPLEMENTED as AI_IMPACT_ROUTES  # noqa: E402
from impact_api.human_advice_contracts import IMPLEMENTED as HUMAN_ADVICE_ROUTES  # noqa: E402
from impact_api.ai_plan_export_contracts import IMPLEMENTED as AI_PLAN_EXPORT_ROUTES  # noqa: E402
from impact_api.ai_planning_contracts import IMPLEMENTED as AI_PLANNING_ROUTES  # noqa: E402
from impact_api.service import READ_ROUTES, WRITE_ROUTES, ACTIONS  # noqa: E402
from impact_api.administration_contracts import COMMANDS, ADMIN_READS  # noqa: E402
from impact_api.measurement_contracts import SPECIAL_READS  # noqa: E402
from impact_api.reporting_contracts import SPECIAL_READS as REPORTING_READS  # noqa: E402
from impact_api.planning_contracts import SPECIAL_READS as PLANNING_READS  # noqa: E402
from impact_api.planning_contracts import LOGFRAME_READS  # noqa: E402
from impact_api.calculation_contracts import SPECIAL_READS as CALCULATION_READS  # noqa: E402
from impact_api.calculation_compatibility_contracts import (  # noqa: E402
    IMPLEMENTED as CALCULATION_COMPATIBILITY_ROUTES,
)
from impact_api.forms_contracts import SPECIAL_READS as FORMS_READS  # noqa: E402
from impact_api.evidence_contracts import (  # noqa: E402
    SPECIAL_READS as EVIDENCE_READS,
    IMPLEMENTED as EVIDENCE_ROUTES,
)
from impact_api.export_contracts import SPECIAL_READS as EXPORT_READS  # noqa: E402
from impact_api.dashboard_contracts import SPECIAL_READS as DASHBOARD_READS  # noqa: E402
from impact_api.audit_export_contracts import IMPLEMENTED as AUDIT_EXPORT_ROUTES  # noqa: E402
from impact_api.privacy_contracts import IMPLEMENTED as PRIVACY_ROUTES  # noqa: E402
from impact_api.retention_contracts import IMPLEMENTED as RETENTION_ROUTES  # noqa: E402
from impact_api.publication_contracts import (  # noqa: E402
    SPECIAL_READS as PUBLICATION_READS,
    DIRECTORY_READS as PUBLICATION_DIRECTORIES,
)

allowed = set()
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in SPECIAL_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in REPORTING_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in PLANNING_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in LOGFRAME_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in CALCULATION_READS)
allowed.update(
    (method, "/v1/tenants/{tenant_id}/" + route) for method, route in CALCULATION_COMPATIBILITY_ROUTES
)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in FORMS_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in EXPORT_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in DASHBOARD_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in PUBLICATION_READS)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in PUBLICATION_DIRECTORIES)
allowed.update(("get", "/v1/tenants/{tenant_id}/" + route) for route in EVIDENCE_READS)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in EVIDENCE_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in PRIVACY_ROUTES)
allowed.update(
    (method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_OUTCOME_OBSERVATION_ROUTES
)
allowed.update(
    (method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_SPONSOR_VALUE_REPORT_ROUTES
)
allowed.update(
    (method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_QUARTERLY_VALUE_REVIEW_ROUTES
)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_NEXT_OPPORTUNITY_ROUTES)
allowed.update(
    (method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_OUTCOME_EVIDENCE_TENANT_ROUTES
)
allowed.update(AI_OUTCOME_EVIDENCE_PLATFORM_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in DISCOVERABILITY_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in POPULATION_OVERLAP_ROUTES)
allowed.update(
    (method, "/v1/tenants/{tenant_id}/" + route) for method, route in HIERARCHICAL_AGGREGATION_ROUTES
)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in DIMENSION_CROSSWALK_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in FORMULA_AUTHORING_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in PORTFOLIO_ATTRIBUTION_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in SPONSORED_ACCESS_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in ENTITLEMENT_VIEW_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in SERVICE_PACKAGE_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in TAX_INVOICING_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AGREEMENT_COVERAGE_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in RETENTION_ROUTES)
allowed.add(("post", "/v1/tenants/{tenant_id}/disclosure-requests"))
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AUDIT_EXPORT_ROUTES)
for route in READ_ROUTES:
    allowed.update(
        {
            ("get", "/v1/tenants/{tenant_id}/" + route),
            ("get", "/v1/tenants/{tenant_id}/" + route + "/{object_id}"),
        }
    )
for route in WRITE_ROUTES:
    allowed.update(
        {
            ("post", "/v1/tenants/{tenant_id}/" + route),
            ("patch", "/v1/tenants/{tenant_id}/" + route + "/{object_id}"),
        }
    )
for route, actions in ACTIONS.items():
    for action in actions:
        allowed.add(("post", "/v1/tenants/{tenant_id}/" + route + "/{object_id}/actions/" + action))
for route in ADMIN_READS:
    allowed.add(("get", "/v1/tenants/{tenant_id}/" + route))
for route, action in COMMANDS:
    allowed.add(
        ("post", "/v1/tenants/{tenant_id}/" + route + ("/{object_id}/actions/" + action if action else ""))
    )
spec = json.loads(json.dumps(SPEC))
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_ENABLEMENT_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_ADOPTION_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_DIAGNOSIS_ROUTES)
allowed.update(
    (method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_DIAGNOSIS_CONTRIBUTION_ROUTES
)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_SOLUTION_SHORTLIST_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_SOLUTION_FIT_SCORE_ROUTES)
allowed.update(AI_VETTING_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_DIAGNOSIS_REVIEW_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_PROBLEM_BASELINE_ROUTES)
allowed.update(
    (method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_OPPORTUNITY_MAPPING_ROUTES
)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_VALUE_CASE_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_VALUE_CASE_EXPORT_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_VALUE_CASE_VERSION_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_CONTENT_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_IMPACT_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in HUMAN_ADVICE_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_PLAN_EXPORT_ROUTES)
allowed.update((method, "/v1/tenants/{tenant_id}/" + route) for method, route in AI_PLANNING_ROUTES)
spec["info"]["title"] = "Impact Platform — implemented domain API"
spec["info"]["description"] = (
    "Implemented domain subset only. Support, authentication and health routes are documented in docs/IMPLEMENTATION.md."
)
spec["paths"] = {
    path: {k: v for k, v in node.items() if (k, path) in allowed or k == "parameters"}
    for path, node in spec["paths"].items()
    if any(p == path for _, p in allowed)
}
(ROOT / "packages/contracts/openapi-implemented.json").write_text(json.dumps(spec, indent=2) + "\n")
lines = ["# Implemented domain operations", "", "| Method | Path | Capability |", "|---|---|---|"]
for method, path in sorted(allowed, key=lambda x: (x[1], x[0])):
    entry = spec["paths"][path][method]
    lines.append("| " + method.upper() + " | `" + path + "` | `" + entry["x-capability"] + "` |")
(ROOT / "docs/API-INVENTORY.md").write_text("\n".join(lines) + "\n")
print("Exported", len(allowed), "domain operations")
