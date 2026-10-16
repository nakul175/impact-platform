"""Positive user journey for FR-EVD-008 / APL-646 triangulated findings."""

from uuid import uuid4

import pytest

from test_evaluation_registry_live import _evidence
from test_forms import temporary_grants
from test_live_application import expect


@pytest.fixture(autouse=True)
def finding_journey_grants(live):
    revokes = [
        temporary_grants(
            live,
            "author",
            ["evaluations.draft.edit", "evidence.draft.create", "evidence.read"],
        ),
        temporary_grants(
            live,
            "reviewer",
            ["evaluations.draft.edit", "evidence.read"],
        ),
    ]
    try:
        yield
    finally:
        for revoke in reversed(revokes):
            revoke()


def post(live, route, data, actor="author"):
    return expect(
        live.request(
            live.path(route), actor=actor, method="POST", body={"operation_id": str(uuid4()), "data": data}
        ),
        201,
    )


def stored(live, object_id):
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        return c.execute(
            "SELECT r.object_type,r.lifecycle_state,v.revision_id::text,v.predecessor_revision::text,v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
            (live.fixture["tenant_a"], object_id),
        ).fetchone()


def test_finding_preserves_evidence_history_and_publishes_the_reviewed_revision(live):
    ra = temporary_grants(live, "author", ["evaluations.draft.edit"])
    rr = temporary_grants(live, "reviewer", ["evaluations.draft.edit"])
    try:
        support, contrary = _evidence(live, "FIELD_NOTE"), _evidence(live, "INTERVIEW_TRANSCRIPT")

        def pin(row):
            return {
                "object_type": "Evidence",
                "object_id": row["object_id"],
                "revision_id": row["revision_id"],
            }

        created = post(
            live,
            "findings",
            {
                "statement": "Assisted outreach improved synthetic attendance.",
                "method": "Triangulation.",
                "observation": "Attendance rose.",
                "interpretation": "Outreach may have contributed.",
                "supporting_evidence": [pin(support)],
                "contradictory_evidence": [pin(contrary)],
                "confidence_rationale": "Sources agree on attendance but disagree on cause.",
                "limitations": ["No causal inference."],
                "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
                "ai_confidence": None,
            },
        )
        revised = post(
            live,
            "finding-revisions",
            {
                "finding_id": created["object_id"],
                "expected_revision": created["revision_id"],
                "interpretation": "Outreach is one plausible contributor.",
                "supporting_evidence": [pin(support)],
                "contradictory_evidence": [pin(contrary)],
            },
        )
        row = stored(live, created["object_id"])
        assert (
            row["revision_id"] == revised["revision_id"]
            and row["predecessor_revision"] == created["revision_id"]
        )
        assert row["payload"]["prior_evidence_set"] == {
            "revision": created["revision_id"],
            "supporting": [pin(support)],
            "contradictory": [pin(contrary)],
        }
        refused = expect(
            live.request(
                live.path("finding-publications"),
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "data": {
                        "finding_id": created["object_id"],
                        "expected_revision": revised["revision_id"],
                        "preserve_contradictory_evidence": True,
                        "disclosed_limitation": None,
                    },
                },
            ),
            409,
        )
        assert refused["code"] == "INDEPENDENCE_REQUIRED"
        publication = post(
            live,
            "finding-publications",
            {
                "finding_id": created["object_id"],
                "expected_revision": revised["revision_id"],
                "preserve_contradictory_evidence": True,
                "disclosed_limitation": None,
            },
            actor="reviewer",
        )
        saved = stored(live, publication["object_id"])
        assert (saved["object_type"], saved["lifecycle_state"], saved["payload"]["finding_revision"]) == (
            "FindingPublication",
            "Published",
            revised["revision_id"],
        )
    finally:
        rr()
        ra()
