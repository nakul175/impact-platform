"""The ordinary draft command used by explicit APL-541 confirmation remains scoped."""

from uuid import uuid4

from test_forms import temporary_grants
from test_live_application import expect
from test_story_error_recovery_analytics_live import _durable_counts


def test_ordinary_work_item_draft_checks_authority_references_and_exact_retries(live):
    revoke = temporary_grants(live, "author", ["work-items.draft.create", "work-items.read"])
    try:
        body = {
            "operation_id": str(uuid4()),
            "data": {
                "programme_id": live.records["programme_a"]["object_id"],
                "work_type": "ACTION",
                "title": "Synthetic accountable follow-up",
                "dependency_ids": [],
                "assignee_id": live.fixture["actors"]["author"]["principal_id"],
            },
        }
        path = live.path("work-items")
        before = _durable_counts(live, body["operation_id"])
        expect(live.request(path, actor="revoked", method="POST", body=body), 404)
        expect(live.request(path, actor="partner", method="POST", body=body), 403)
        invalid = {**body, "data": {**body["data"], "programme_id": str(uuid4())}}
        expect(live.request(path, method="POST", body=invalid), 404)
        assert _durable_counts(live, body["operation_id"]) == before
        created = expect(live.request(path, method="POST", body=body), 201)
        assert created["business_state"] == "Draft"
        after = _durable_counts(live, body["operation_id"])
        assert expect(live.request(path, method="POST", body=body), 201) == created
        expect(
            live.request(path, method="POST", body={**body, "data": {**body["data"], "title": "Changed"}}),
            409,
        )
        assert _durable_counts(live, body["operation_id"]) == after
        saved = expect(live.request(live.path("work-items", created["object_id"])), 200)
        assert saved["revision_id"] == created["revision_id"]
        expect(live.request(live.path("work-items", created["object_id"]), actor="other_tenant"), 404)
    finally:
        revoke()
