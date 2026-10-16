"""Positive live journey for FR-EVA-007 / APL-639 management responses."""

from uuid import uuid4

from test_forms import temporary_grants
from test_live_application import expect


def test_partial_response_creates_owned_action_completed_by_exact_evidence(live):
    """A recommendation becomes a dated action with durable, immutable follow-through."""

    evidence = expect(live.request(live.path("evidence", live.records["evidence_a"]["object_id"])), 200)
    owner_id = live.fixture["actors"]["author"]["principal_id"]
    revoke = temporary_grants(live, "author", ["evaluations.draft.edit", "evaluations.read", "evidence.read"])
    try:
        recommendation = expect(
            live.request(
                live.path("evaluation-recommendations"),
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "data": {
                        "title": "Strengthen evidence review",
                        "recommendation": "Record completion against the approved evidence revision.",
                        "source_object_id": evidence["object_id"],
                        "source_revision": evidence["revision_id"],
                        "rationale": "The exact synthetic evidence record supports this recommendation.",
                    },
                },
            ),
            201,
        )
        recommendation_id = recommendation["object_id"]
        issued = expect(live.request(live.path("evaluation-recommendations", recommendation_id)), 200)
        assert issued["lifecycle_state"] == "Issued"
        assert issued["data"]["source_revision"] == evidence["revision_id"]

        responded = expect(
            live.request(
                live.path("evaluation-recommendations", recommendation_id) + "/response",
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "data": {
                        "response": "PARTIALLY_ACCEPT",
                        "reason": "Adopt the bounded evidence-control portion first.",
                        "accepted_scope": "Pin completion to the current approved evidence revision.",
                        "owner_id": owner_id,
                        "due_date": "2026-12-31",
                        "required_completion_evidence": ["Exact Evidence object and revision"],
                    },
                },
            ),
            201,
        )
        action_id = responded["action"]["object_id"]
        opened = expect(live.request(live.path("management-actions", action_id)), 200)
        assert opened["lifecycle_state"] == "Open"
        assert opened["data"]["owner_id"] == owner_id
        assert opened["data"]["action_completion"] == "PENDING"

        complete_operation = str(uuid4())
        completion_body = {
            "operation_id": complete_operation,
            "data": {
                "evidence": [
                    {
                        "object_id": evidence["object_id"],
                        "revision_id": evidence["revision_id"],
                    }
                ]
            },
        }
        completed = expect(
            live.request(
                live.path("management-actions", action_id) + "/actions/complete",
                method="POST",
                body=completion_body,
            ),
            200,
        )
        retried = expect(
            live.request(
                live.path("management-actions", action_id) + "/actions/complete",
                method="POST",
                body=completion_body,
            ),
            200,
        )
        assert retried == completed

        current = expect(live.request(live.path("management-actions", action_id)), 200)
        assert current["lifecycle_state"] == "Completed"
        assert current["data"]["completion_evidence"] == completion_body["data"]["evidence"]
        assert current["data"]["action_completion"] == "COMPLETE"
        assert current["data"]["outcome_improvement"] == "PENDING_FOLLOW_UP_MEASUREMENT"

        history = expect(live.request(live.path("management-actions", action_id) + "/history"), 200)
        assert [item["revision_number"] for item in history["items"]] == [1, 2]
        assert history["items"][0]["payload"]["action_completion"] == "PENDING"
        assert history["items"][1]["predecessor_revision"] == history["items"][0]["revision_id"]
        assert history["items"][1]["payload"]["completion_evidence"] == completion_body["data"]["evidence"]
    finally:
        revoke()
