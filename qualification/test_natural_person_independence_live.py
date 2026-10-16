"""Positive live journey for FR-ACC-004 / APL-351 natural-person independence."""

from test_administration import action, expect, join, member, request_as, role_request


def test_alias_cannot_approve_but_distinct_natural_person_can(live):
    """A second account cannot create independence; a distinct reviewer completes the decision."""

    identity, receipt = join(live, natural=live.fixture["actors"]["owner"]["natural_identity_id"])
    proposal = role_request(live, receipt, actor="owner")

    alias_denial = expect(
        action(
            live,
            "access-requests",
            proposal["object_id"],
            "approve",
            proposal["revision_id"],
            actor="owner",
        ),
        403,
    )
    assert alias_denial["reason_code"] == "INDEPENDENCE_REQUIRED"

    approved = expect(
        action(
            live,
            "access-requests",
            proposal["object_id"],
            "approve",
            proposal["revision_id"],
            actor="admin",
        ),
        200,
    )
    assert approved["object_id"] == proposal["object_id"]
    assert member(live, receipt["object_id"])["revision_id"] != receipt["revision_id"]
    access = expect(request_as(live, identity, live.path("me/access")), 200)
    assert "workflow.approve" in access["capabilities"]
