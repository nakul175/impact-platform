"""Real transaction qualification: proposal approval, preservation and isolation."""
# ruff: noqa: F811

import uuid
import pytest
from impact_api.contracts import validate
from impact_api.domain import DomainError
from test_live_application import cmd, expect
from test_measurement import setup, get, create, action, submit, approve, observation, result  # noqa: F401


def propose(live, target, kind, changes):
    return create(
        live,
        "measurement-changes",
        {
            "target_kind": kind,
            "target_id": target["object_id"],
            "target_revision": target["revision_id"],
            "reason": "Verified source correction against collection records",
            "proposed_data": changes,
        },
    )


def approved_observation(live, setup):
    _, indicator, plan, period = setup()
    row = observation(live, indicator, plan["data"]["obligations"][0]["source_key"])
    approve(live, submit(live, "observations", row))
    return indicator, plan, period, get(live, "observations", row["object_id"])


def test_correction_keeps_effective_source_until_approval_and_stales_result(live, setup):
    indicator, _, period, row = approved_observation(live, setup)
    calculated = result(live, indicator, period)
    proposal = propose(live, row, "Observation", {"value": "25", "source_version": "2"})
    workflow = submit(live, "measurement-changes", proposal)
    assert get(live, "observations", row["object_id"]) == row
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    validate("ReviewCandidate", candidate)
    assert candidate["current_target"]["data"]["value"] == "10"
    assert not get(live, "calculated-results", calculated["object_id"])["data"]["freshness"]["stale"]
    approve(live, workflow)
    changed = get(live, "observations", row["object_id"])
    assert changed["lifecycle_state"] == "Approved" and changed["data"]["value"] == "25"
    assert changed["revision_id"] != row["revision_id"]
    assert get(live, "calculated-results", calculated["object_id"])["data"]["freshness"]["stale"]
    with live.db() as c:
        old = c.execute(
            "SELECT payload FROM impact.object_revision WHERE revision_id=%s", (row["revision_id"],)
        ).fetchone()
        assert old["payload"]["value"] == "10"
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.measurement_change_effect WHERE change_id=%s",
                (proposal["object_id"],),
            ).fetchone()["n"]
            == 1
        )


def test_correction_author_cannot_approve_and_rejection_preserves_source(live, setup):
    _, _, _, row = approved_observation(live, setup)
    proposal = propose(live, row, "Observation", {"value": "20"})
    workflow = submit(live, "measurement-changes", proposal)
    data = {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Review"}
    assert (
        action(live, "workflows", workflow, "approve", data, status=403)["reason_code"]
        == "INDEPENDENCE_REQUIRED"
    )
    action(live, "workflows", workflow, "reject", data, actor="reviewer")
    assert get(live, "observations", row["object_id"]) == row


def test_competing_corrections_recheck_target_atomically(live, setup):
    _, _, _, row = approved_observation(live, setup)
    a = submit(live, "measurement-changes", propose(live, row, "Observation", {"value": "20"}))
    b = submit(live, "measurement-changes", propose(live, row, "Observation", {"value": "30"}))
    approve(live, a)
    denied = action(
        live,
        "workflows",
        b,
        "approve",
        {"candidate_revision": b["data"]["candidate_revision"], "reason": "Review"},
        actor="reviewer",
        status=409,
    )
    assert denied["reason_code"] == "AMENDMENT_TARGET_CHANGED"
    assert get(live, "workflows", b["object_id"]) == b
    assert get(live, "observations", row["object_id"])["data"]["value"] == "20"


def test_plan_amendment_preserves_history_and_changes_binding(live, setup):
    _, indicator, plan, period = setup()
    calculated = result(live, indicator, period)
    obligations = plan["data"]["obligations"] + [
        {**plan["data"]["obligations"][0], "source_key": str(uuid.uuid4()), "label": "Additional partner"}
    ]
    proposal = propose(live, plan, "CollectionPlan", {"obligations": obligations})
    workflow = submit(live, "measurement-changes", proposal)
    assert get(live, "collection-plans", plan["object_id"]) == plan
    approve(live, workflow)
    changed = get(live, "collection-plans", plan["object_id"])
    assert changed["revision_id"] != plan["revision_id"]
    assert get(live, "calculated-results", calculated["object_id"])["data"]["freshness"]["stale"]
    assert result(live, indicator, period)["data"]["coverage"]["expected_count"] == 6


def test_plan_cannot_remove_obligations_to_inflate_coverage(live, setup):
    _, _, plan, _ = setup()
    denied = expect(
        live.request(
            live.path("measurement-changes"),
            method="POST",
            body=cmd(
                {
                    "target_kind": "CollectionPlan",
                    "target_id": plan["object_id"],
                    "target_revision": plan["revision_id"],
                    "reason": "Remove missing contributors",
                    "proposed_data": {"obligations": plan["data"]["obligations"][:1]},
                }
            ),
        ),
        422,
    )
    assert denied["reason_code"] == "OBLIGATION_REMOVAL_REQUIRES_EXCLUSION"


@pytest.mark.parametrize("field", ["indicator_id", "source_key", "event_at", "approval_state", "tenant_id"])
def test_correction_contract_rejects_identity_and_authority_changes(field):
    with pytest.raises(DomainError):
        validate(
            "MeasurementChangeData",
            {
                "target_kind": "Observation",
                "target_id": str(uuid.uuid4()),
                "target_revision": str(uuid.uuid4()),
                "reason": "Correction",
                "proposed_data": {field: str(uuid.uuid4())},
            },
        )


def test_change_cross_tenant_and_scope_hidden_and_effect_rls(live, setup):
    _, _, _, row = approved_observation(live, setup)
    proposal = propose(live, row, "Observation", {"value": "20"})
    expect(live.request(live.path("measurement-changes", proposal["object_id"]), actor="partner"), 404)
    expect(
        live.request(
            live.path("measurement-changes", proposal["object_id"], tenant=live.fixture["tenant_b"])
        ),
        404,
    )
    approve(live, submit(live, "measurement-changes", proposal))
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.measurement_change_effect WHERE tenant_id=%s",
                (live.fixture["tenant_a"],),
            ).fetchone()["n"]
            == 0
        )


def test_reassignment_independent_approval_preserves_pending_candidate_and_decisions(live, setup):
    from test_administration import join, role_request, request_as

    _, indicator, plan, _ = setup()
    row = observation(live, indicator, plan["data"]["obligations"][0]["source_key"])
    pending = submit(live, "observations", row)
    identity, member = join(live)
    role = role_request(live, member)
    expect(
        live.request(
            live.path("access-requests", role["object_id"]) + "/actions/approve",
            actor="owner",
            method="POST",
            body=cmd({"reason": "Qualified new reviewer"}, role["revision_id"]),
        ),
        200,
    )
    principal = expect(request_as(live, identity, live.path("me/access")), 200)["principal_id"]
    change = propose(live, indicator, "IndicatorInstance", {"reviewer_id": principal})
    workflow = submit(live, "measurement-changes", change)
    data = {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Responsibility review"}
    denied = expect(
        request_as(
            live,
            identity,
            live.path("workflows", workflow["object_id"]) + "/actions/approve",
            method="POST",
            body=cmd(data, workflow["revision_id"]),
        ),
        403,
    )
    assert denied["reason_code"] == "ASSIGNMENT_RECIPIENT_CANNOT_APPROVE"
    authored = {k: v for k, v in row["data"].items() if k != "approval_state"}
    authored["source_key"] = str(uuid.uuid4())
    own = expect(
        request_as(live, identity, live.path("observations"), method="POST", body=cmd(authored)), 201
    )
    own_workflow = expect(
        request_as(
            live,
            identity,
            live.path("observations", own["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd(
                {"workflow_version": get(live, "workflow-templates")["items"][0]["revision_id"]},
                own["revision_id"],
            ),
        ),
        200,
    )
    blocked = action(live, "workflows", workflow, "approve", data, actor="reviewer", status=422)
    assert blocked["reason_code"] == "REASSIGNMENT_INDEPENDENCE_CONFLICT"
    assert get(live, "workflows", pending["object_id"]) == pending
    assert get(live, "indicator-instances", indicator["object_id"])["revision_id"] == indicator["revision_id"]
    approve(live, get(live, "workflows", own_workflow["object_id"]))
    approve(live, workflow)
    reassigned = get(live, "workflows", pending["object_id"])
    assert reassigned["revision_id"] != pending["revision_id"]
    assert reassigned["lifecycle_state"] == "InReview"
    assert reassigned["data"]["candidate_revision"] == pending["data"]["candidate_revision"]
    assert reassigned["data"]["stages"][0]["candidate_membership_ids"] == [member["object_id"]]
    decision = {"candidate_revision": reassigned["data"]["candidate_revision"], "reason": "Checked source"}
    action(live, "workflows", reassigned, "approve", decision, actor="reviewer", status=403)
    expect(
        request_as(
            live,
            identity,
            live.path("workflows", reassigned["object_id"]) + "/actions/approve",
            method="POST",
            body=cmd(decision, reassigned["revision_id"]),
        ),
        200,
    )
    assert get(live, "observations", row["object_id"])["lifecycle_state"] == "Approved"


def test_approved_amendment_retry_has_one_effect_and_target_event(live, setup):
    _, _, _, row = approved_observation(live, setup)
    change = propose(live, row, "Observation", {"value": "24"})
    workflow = submit(live, "measurement-changes", change)
    body = cmd(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Correction verified"},
        workflow["revision_id"],
    )
    first = action(live, "workflows", workflow, "approve", actor="reviewer", body=body)
    assert action(live, "workflows", workflow, "approve", actor="reviewer", body=body) == first
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.measurement_change_effect WHERE change_id=%s",
                (change["object_id"],),
            ).fetchone()["n"]
            == 1
        )

        effect = c.execute(
            "SELECT after_revision FROM impact.measurement_change_effect WHERE change_id=%s",
            (change["object_id"],),
        ).fetchone()
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE payload->>'aggregate_revision'=%s",
                (str(effect["after_revision"]),),
            ).fetchone()["n"]
            == 1
        )


def test_pooled_components_can_be_corrected_without_new_source_identity(live, setup):
    from test_live_application import draft

    programme, _, plan, period = setup()
    seeded = get(live, "indicator-instances", live.records["indicator_a"]["object_id"])
    indicator = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": seeded["data"]["definition_version"],
            "local_applicability": "Isolated pooled correction",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    key = str(uuid.uuid4())
    ratio_plan = create(
        live,
        "collection-plans",
        {
            "title": "Ratio correction plan",
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "obligations": [{**plan["data"]["obligations"][0], "source_key": key}],
        },
    )
    approve(live, submit(live, "collection-plans", ratio_plan))
    action(live, "indicator-instances", indicator, "activate")
    row = create(live, "observations", draft(live, key=key, indicator_id=indicator["object_id"]))
    approve(live, submit(live, "observations", row))
    row = get(live, "observations", row["object_id"])
    request = propose(live, row, "Observation", {"value": "90", "numerator": "9", "denominator": "10"})
    approve(live, submit(live, "measurement-changes", request))
    changed = get(live, "observations", row["object_id"])
    assert changed["data"]["source_key"] == row["data"]["source_key"]
    assert changed["data"]["numerator"] == "9" and changed["data"]["denominator"] == "10"


def test_closed_period_blocks_amendment_without_restatement(live, setup):
    indicator, _, period, row = approved_observation(live, setup)
    with live.db() as c:
        c.execute(
            "INSERT INTO impact.programme_period_state VALUES(%s,%s,%s,'Locked',0,NULL,now(),%s)",
            (
                live.fixture["tenant_a"],
                indicator["data"]["programme_id"],
                period["object_id"],
                live.fixture["actors"]["author"]["principal_id"],
            ),
        )
    try:
        response = expect(
            live.request(
                live.path("measurement-changes"),
                method="POST",
                body=cmd(
                    {
                        "target_kind": "Observation",
                        "target_id": row["object_id"],
                        "target_revision": row["revision_id"],
                        "reason": "Late correction",
                        "proposed_data": {"value": "30"},
                    }
                ),
            ),
            409,
        )
        assert response["reason_code"] == "PERIOD_RESTATEMENT_REQUIRED"
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.programme_period_state SET lifecycle_state='Open',restatement_expires_at=NULL WHERE programme_id=%s AND period_id=%s",
                (indicator["data"]["programme_id"], period["object_id"]),
            )


def test_connection_handoffs_preserve_tenant_reads_and_administrative_scope(live):
    from concurrent.futures import ThreadPoolExecutor

    def read(index):
        if index % 3 == 0:
            page = get(live, "access-scopes", actor="admin")
            assert any(s["scope_type"] == "TENANT" for s in page["items"])
        elif index % 3 == 1:
            assert (
                get(live, "programmes", live.fixture["programme_a"])["object_id"]
                == live.fixture["programme_a"]
            )
        else:
            expect(live.request(live.path("programmes", live.fixture["programme_b"])), 404)

    # Mix identity and tenant connections with differently shaped wire responses.
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(read, range(90)))
