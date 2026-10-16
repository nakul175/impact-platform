"""Positive user journey for FR-EVA-003 / APL-632 frozen analysis packages."""

from uuid import uuid4

from impact_api.contracts import validate
from test_dashboards import measure, ratio_source
from test_forms import temporary_grants
from test_live_application import expect


def _evaluation(live, programme):
    return expect(
        live.request(
            live.path("evaluations"),
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "title": "Synthetic frozen analysis evaluation",
                    "study_type": "MIDLINE",
                    "programme_id": programme["object_id"],
                    "period_id": live.records["period"]["object_id"],
                    "questions": ["What proportion reached the outcome?"],
                    "study_design": "Synthetic reproducible quantitative analysis.",
                    "evaluator": "Independent synthetic analysis team",
                    "independence": {"claimed": False},
                    "ethics_requirements": [],
                    "budget": {"amount": "1000", "currency": "USD"},
                    "deliverables": ["Frozen analysis export"],
                    "required_documents": {"FIELD_COLLECTION": [], "PUBLICATION": []},
                    "sensitive_processing": False,
                },
            },
        ),
        201,
    )


def _reviewed_methodology(live, evaluation):
    created = expect(
        live.request(
            live.path("evaluation-methodologies"),
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "evaluation_id": evaluation["object_id"],
                    "sampling_frame": "One synthetic approved observation.",
                    "eligibility_rules": "Approved observations only.",
                    "assignment_method": "Deterministic inclusion of the frozen source.",
                    "strata": [
                        {
                            "code": "ALL",
                            "eligible_count": 1,
                            "sampled_count": 1,
                            "weight": "1",
                            "nonresponse_count": 0,
                        }
                    ],
                    "nonresponse_rules": "No imputation.",
                    "analysis_plan": "Preserve exact revisions and source digests.",
                    "expansion_method": "POST_STRATIFIED_WEIGHTED_SUM",
                },
            },
        ),
        201,
    )
    current = expect(live.request(live.path("evaluation-methodologies", created["object_id"])), 200)
    revoke = temporary_grants(live, "reviewer", ["evaluations.draft.edit"])
    try:
        expect(
            live.request(
                live.path("evaluation-methodologies", created["object_id"]) + "/actions/review",
                actor="reviewer",
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "expected_revision": current["revision_id"],
                    "data": {"decision": "APPROVE", "reason": "The frozen plan is reproducible."},
                },
            ),
            200,
        )
    finally:
        revoke()
    return expect(live.request(live.path("evaluation-methodologies", created["object_id"])), 200)


def test_analyst_freezes_an_approved_source_and_registers_a_pinned_result(live):
    programme, indicator, _, keys = measure(live, keys=1)
    observation = ratio_source(live, indicator, keys[0], "3", "4")
    evaluation = _evaluation(live, programme)
    methodology = _reviewed_methodology(live, evaluation)
    variables = ["approval_state", "numerator", "denominator", "indicator_id"]
    package = expect(
        live.request(
            live.path("analysis-packages"),
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "evaluation_id": evaluation["object_id"],
                    "methodology_id": methodology["object_id"],
                    "methodology_revision": methodology["revision_id"],
                    "sources": [
                        {
                            "kind": "Observation",
                            "object_id": observation["object_id"],
                            "revision_id": observation["revision_id"],
                        }
                    ],
                    "variables": variables,
                    "filters": [{"field": "approval_state", "operator": "EQ", "values": ["APPROVED"]}],
                    "dictionary": [
                        {"variable": item, "definition": f"Frozen {item} field.", "unit": None}
                        for item in variables
                    ],
                    "reviewed_code_evidence": [],
                },
            },
        ),
        201,
    )
    exported = expect(live.request(live.path("analysis-packages", package["object_id"]) + "/export"), 200)
    validate("AnalysisPackageExport", exported)
    assert exported["content"]["rows"][0]["revision_id"] == observation["revision_id"]
    assert exported["content"]["code_execution"] == "PROHIBITED"
    result = expect(
        live.request(
            live.path("analysis-packages", package["object_id"]) + "/results",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {"title": "Synthetic ratio", "result": {"ratio": "0.75"}},
            },
        ),
        201,
    )
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        stored = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (tenant, result["revision_id"]),
        ).fetchone()["payload"]
    assert stored["package_revision"] == package["revision_id"]
    assert stored["package_integrity_sha256"] == exported["integrity_sha256"]
    assert stored["methodology_revision"] == methodology["revision_id"]
