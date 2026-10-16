"""Positive user journey for FR-EVA-001 / APL-625 controlled evaluation registration."""

from uuid import uuid4

import pytest

from impact_api.contracts import validate
from test_forms import temporary_grants
from test_live_application import cmd, expect


@pytest.fixture(autouse=True)
def evaluation_journey_grants(live):
    """Own the exact evidence and gate grants even after earlier revocation scenarios."""
    revokes = [
        temporary_grants(live, "author", ["evidence.draft.create", "evidence.read"]),
        temporary_grants(live, "reviewer", ["evaluations.draft.edit", "evidence.read"]),
        temporary_grants(live, "partner", ["evaluations.draft.edit", "evidence.read"]),
    ]
    try:
        yield
    finally:
        for revoke in reversed(revokes):
            revoke()


def _evidence(live, kind):
    receipt = expect(
        live.request(
            live.path("evidence"),
            method="POST",
            body=cmd(
                {
                    "evidence_type": kind,
                    "external_reference": f"https://example.test/evaluation/{kind.lower()}",
                    "source": "Synthetic evaluation qualification fixture",
                    "evidence_date": "2026-09-30",
                }
            ),
        ),
        201,
    )
    return expect(live.request(live.path("evidence", receipt["object_id"])), 200)


def test_evaluation_moves_through_independently_decided_stage_gates(live):
    """An evaluator registers a study and another natural person advances both gates.

    The journey verifies the user-visible resource, immutable gate history and exact evidence
    pins. It deliberately uses non-sensitive synthetic material: this registration flow never
    grants approval for sensitive processing.
    """

    programme = live.records["programme_a"]
    period = live.records["period"]
    created = expect(
        live.request(
            live.path("evaluations"),
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "title": "Synthetic endline evaluation",
                    "study_type": "ENDLINE",
                    "programme_id": programme["object_id"],
                    "period_id": period["object_id"],
                    "questions": ["Did the programme improve safe-water access?"],
                    "study_design": "Synthetic mixed-method endline design.",
                    "evaluator": "Independent synthetic evaluation team",
                    "independence": {"claimed": False},
                    "ethics_requirements": [],
                    "budget": {"amount": "25000", "currency": "USD"},
                    "deliverables": ["Endline report", "Disclosure-reviewed public summary"],
                    "required_documents": {
                        "FIELD_COLLECTION": ["ANALYSIS_PLAN"],
                        "PUBLICATION": ["ANALYSIS_PLAN"],
                    },
                    "sensitive_processing": False,
                },
            },
        ),
        201,
    )
    evaluation_id = created["object_id"]
    current = expect(live.request(live.path("evaluations", evaluation_id)), 200)
    validate("EvaluationRegistrationResource", current)
    assert current["data"]["stage"] == "REGISTERED"
    assert current["data"]["programme_revision_id"] == programme["revision_id"]
    assert current["data"]["period_revision_id"] == period["revision_id"]
    assert current["data"]["sensitive_processing_approved"] is False

    methodology = _evidence(live, "METHODOLOGY")
    analysis_plan = _evidence(live, "ANALYSIS_PLAN")
    disclosure = _evidence(live, "DISCLOSURE_REVIEW")
    documents = {
        row["data"]["evidence_type"]: {
            "kind": row["data"]["evidence_type"],
            "object_id": row["object_id"],
            "revision_id": row["revision_id"],
        }
        for row in (methodology, analysis_plan, disclosure)
    }

    revoke_reviewer = temporary_grants(live, "reviewer", ["evaluations.draft.edit"])
    revoke_publisher = temporary_grants(live, "partner", ["evaluations.draft.edit"])
    try:
        field_gate = expect(
            live.request(
                live.path("evaluations", evaluation_id) + "/actions/stage-gate",
                actor="partner",
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "expected_revision": current["revision_id"],
                    "data": {
                        "stage": "FIELD_COLLECTION",
                        "documents": [documents["METHODOLOGY"], documents["ANALYSIS_PLAN"]],
                    },
                },
            ),
            200,
        )
        validate("EvaluationStageGateOutcome", field_gate)
        assert field_gate["status"] == "PASSED" and field_gate["missing_document_kinds"] == []
        assert field_gate["sensitive_processing_approved"] is False

        field_current = expect(live.request(live.path("evaluations", evaluation_id)), 200)
        assert field_current["data"]["stage"] == "FIELD_COLLECTION"
        publication_gate = expect(
            live.request(
                live.path("evaluations", evaluation_id) + "/actions/stage-gate",
                actor="reviewer",
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "expected_revision": field_current["revision_id"],
                    "data": {
                        "stage": "PUBLICATION",
                        "documents": [
                            documents["METHODOLOGY"],
                            documents["ANALYSIS_PLAN"],
                            documents["DISCLOSURE_REVIEW"],
                        ],
                    },
                },
            ),
            200,
        )
    finally:
        revoke_publisher()
        revoke_reviewer()

    validate("EvaluationStageGateOutcome", publication_gate)
    assert publication_gate["status"] == "PASSED"
    published = expect(live.request(live.path("evaluations", evaluation_id)), 200)
    assert published["data"]["stage"] == "PUBLICATION"
    assert published["data"]["sensitive_processing_approved"] is False

    history = expect(live.request(live.path("evaluations", evaluation_id) + "/stage-gates"), 200)
    validate("EvaluationStageGateHistory", history)
    assert [item["gate"]["stage"] for item in history["items"]] == [
        "PUBLICATION",
        "FIELD_COLLECTION",
    ]
    assert all(item["gate"]["status"] == "PASSED" for item in history["items"])
