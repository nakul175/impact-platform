"""Positive user journey for FR-EVA-002 / APL-630 sampling methodology."""

from uuid import uuid4

from impact_api.contracts import validate
from test_forms import temporary_grants
from test_live_application import expect


def _evaluation(live):
    return expect(
        live.request(
            live.path("evaluations"),
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "title": "Synthetic sampling evaluation",
                    "study_type": "MIDLINE",
                    "programme_id": live.records["programme_a"]["object_id"],
                    "period_id": live.records["period"]["object_id"],
                    "questions": ["What is the representative programme outcome?"],
                    "study_design": "Synthetic stratified probability sample.",
                    "evaluator": "Independent synthetic sampling team",
                    "independence": {"claimed": False},
                    "ethics_requirements": [],
                    "budget": {"amount": "12000", "currency": "USD"},
                    "deliverables": ["Reviewed sample specification"],
                    "required_documents": {"FIELD_COLLECTION": [], "PUBLICATION": []},
                    "sensitive_processing": False,
                },
            },
        ),
        201,
    )


def test_methodology_is_independently_reviewed_and_exports_reproducible_sample_counts(live):
    """An analyst records the sample, an independent reviewer approves it, and export preserves
    the eligible denominator while labelling the sample count separately from population output.
    """

    evaluation = _evaluation(live)
    created = expect(
        live.request(
            live.path("evaluation-methodologies"),
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "evaluation_id": evaluation["object_id"],
                    "sampling_frame": "Synthetic register of 150 eligible programme households.",
                    "eligibility_rules": "Household was enrolled before the midline cutoff.",
                    "assignment_method": "Stratified deterministic random selection using the frozen frame.",
                    "strata": [
                        {
                            "code": "RURAL",
                            "eligible_count": 100,
                            "sampled_count": 10,
                            "weight": "10",
                            "nonresponse_count": 2,
                        },
                        {
                            "code": "URBAN",
                            "eligible_count": 50,
                            "sampled_count": 5,
                            "weight": "10",
                            "nonresponse_count": 1,
                        },
                    ],
                    "nonresponse_rules": "Keep nonresponse explicit; do not impute outcomes.",
                    "analysis_plan": "Report sample counts and weighted population estimates separately.",
                    "expansion_method": "POST_STRATIFIED_WEIGHTED_SUM",
                },
            },
        ),
        201,
    )
    methodology_id = created["object_id"]
    pending = expect(live.request(live.path("evaluation-methodologies", methodology_id)), 200)
    validate("EvaluationMethodologyResource", pending)
    assert pending["data"]["review_state"] == "PENDING"
    assert pending["data"]["evaluation_revision"] == evaluation["revision_id"]

    revoke = temporary_grants(live, "reviewer", ["evaluations.draft.edit"])
    try:
        reviewed = expect(
            live.request(
                live.path("evaluation-methodologies", methodology_id) + "/actions/review",
                actor="reviewer",
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "expected_revision": pending["revision_id"],
                    "data": {
                        "decision": "APPROVE",
                        "reason": "Frame, weights and nonresponse treatment are reproducible.",
                    },
                },
            ),
            200,
        )
    finally:
        revoke()

    approved = expect(live.request(live.path("evaluation-methodologies", methodology_id)), 200)
    validate("EvaluationMethodologyResource", approved)
    assert reviewed["revision_id"] == approved["revision_id"]
    assert approved["data"]["review_state"] == "REVIEWED"
    assert approved["data"]["review"]["reviewed_by"] == live.fixture["actors"]["reviewer"]["principal_id"]

    exported = expect(
        live.request(
            live.path("evaluation-methodologies", methodology_id) + "/sample-export",
            method="POST",
            body={"weighted": True, "population_estimate": True},
        ),
        200,
    )
    validate("EvaluationSampleExport", exported)
    assert exported["eligible_denominator"] == 150
    assert exported["sample_count"] == 15
    assert exported["sample_count_label"] == "SAMPLE_COUNT_NOT_ALL_BENEFICIARIES"
    assert exported["population_estimate"] == "150"
    assert exported["missing_weight_strata"] == []

    history = expect(
        live.request(live.path("evaluation-methodologies", methodology_id) + "/history"),
        200,
    )
    validate("EvaluationMethodologyHistory", history)
    assert [item["data"]["review_state"] for item in history["items"]] == ["REVIEWED", "PENDING"]
