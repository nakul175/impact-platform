"""Positive user journey for FR-EVA-006 / APL-634 versioned learning agendas."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from impact_api.store import Context, write
from test_evaluation_registry_live import _evidence
from test_forms import temporary_grants
from test_live_application import expect


@pytest.fixture(autouse=True)
def learning_journey_grants(live):
    revokes = [
        temporary_grants(live, "author", ["evidence.draft.create", "evidence.read"]),
        temporary_grants(
            live,
            "reviewer",
            ["evaluations.draft.edit", "evaluations.read", "evidence.read"],
        ),
    ]
    try:
        yield
    finally:
        for revoke in reversed(revokes):
            revoke()


def _decision(live):
    actor = live.fixture["actors"]["author"]
    ctx = Context(
        actor["tenant_id"],
        actor["principal_id"],
        actor["membership_id"],
        SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
        0,
        0,
        [],
    )
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (actor["tenant_id"],))
        return write(
            c,
            ctx,
            "Decision",
            {
                "action": "SYNTHETIC_LEARNING_REVIEW",
                "reason": "Qualification precondition.",
                "evidence_revisions": [],
            },
            "Approved",
        )


def _stored(live, object_id):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return c.execute(
            "SELECT r.lifecycle_state,v.revision_id::text,v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
            (tenant, object_id),
        ).fetchone()


def test_team_closes_reopens_and_context_checks_a_versioned_learning_question(live):
    decision = _decision(live)
    evidence = [_evidence(live, kind) for kind in ["ANALYSIS_PLAN", "FIELD_NOTE", "INTERVIEW_TRANSCRIPT"]]
    created = expect(
        live.request(
            live.path("learning-questions"),
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "decision_id": decision["object_id"],
                    "question": "Which outreach approach should be retained?",
                    "context": "Synthetic district programme",
                    "evidence_gaps": ["Seasonal effects remain unknown."],
                    "planned_inquiry": "Repeat the comparison in the next reporting period.",
                    "owner_id": live.fixture["actors"]["author"]["principal_id"],
                    "review_date": "2026-12-31",
                    "evidence": [
                        {"object_id": row["object_id"], "revision_id": row["revision_id"]} for row in evidence
                    ],
                    "unresolved_assumptions": [
                        {
                            "assumption": "The effect persists across seasons.",
                            "follow_up_study_required": True,
                        }
                    ],
                },
            },
        ),
        201,
    )
    revoke = temporary_grants(
        live, "reviewer", ["evaluations.draft.edit", "evaluations.read", "evidence.read"]
    )
    try:
        closed = expect(
            live.request(
                live.path("learning-questions", created["object_id"]) + "/actions/close",
                actor="reviewer",
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "expected_revision": created["revision_id"],
                    "data": {
                        "conclusion": "Retain the assisted outreach approach in this context.",
                        "remaining_uncertainty": "Seasonality is unresolved.",
                    },
                },
            ),
            200,
        )
    finally:
        revoke()
    summary = expect(live.request(live.path("learning-questions", created["object_id"]) + "/summary"), 200)
    assert summary["question_revision"] == closed["revision_id"]
    assert len(summary["evidence"]) == 3
    reopened = expect(
        live.request(
            live.path("learning-questions", created["object_id"]) + "/actions/reopen",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "expected_revision": closed["revision_id"],
                "data": {"reason": "New seasonal evidence is planned."},
            },
        ),
        200,
    )
    current = _stored(live, created["object_id"])
    assert current["lifecycle_state"] == "Open"
    assert current["payload"]["prior_reasoning"][0]["revision_id"] == closed["revision_id"]
    review = expect(
        live.request(
            live.path("learning-questions", created["object_id"]) + "/actions/consider-context",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "expected_revision": reopened["revision_id"],
                "data": {"target_context": "A second synthetic district"},
            },
        ),
        201,
    )
    applicability = _stored(live, review["object_id"])
    assert applicability["lifecycle_state"] == "Pending"
    assert applicability["payload"]["question_revision"] == reopened["revision_id"]
    assert applicability["payload"]["transferred_conclusion"] is None
