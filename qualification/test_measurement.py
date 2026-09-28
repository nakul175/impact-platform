"""API, database and security qualification of manual measurement configuration."""

import uuid
import pytest
from impact_api.contracts import validate
from test_live_application import cmd, expect
from test_measurement_unit import definition


def test_approved_plan_reserves_source_key_across_indicators(setup, live):
    _, _, first, _ = setup()
    _, _, second, _ = setup(False)
    entry = {**second["data"]["obligations"][0], "source_key": first["data"]["obligations"][0]["source_key"]}
    expect(
        live.request(
            live.path("collection-plans", second["object_id"]),
            method="PATCH",
            body=cmd({"obligations": [entry]}, second["revision_id"]),
        ),
        200,
    )
    second = get(live, "collection-plans", second["object_id"])
    template = get(live, "workflow-templates")["items"][0]
    denied = action(
        live, "collection-plans", second, "submit", {"workflow_version": template["revision_id"]}, status=422
    )
    assert denied["reason_code"] == "SOURCE_KEY_UNAVAILABLE"


def test_plan_approval_detects_indicator_change_after_submission(setup, live):
    _, indicator, plan, _ = setup(False)
    workflow = submit(live, "collection-plans", plan)
    expect(
        live.request(
            live.path("indicator-instances", indicator["object_id"]),
            method="PATCH",
            body=cmd({"local_applicability": "Materially changed population"}, indicator["revision_id"]),
        ),
        200,
    )
    denied = action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Stale configuration"},
        actor="reviewer",
        status=409,
    )
    assert denied["reason_code"] == "PLAN_INDICATOR_CHANGED"
    assert get(live, "workflows", workflow["object_id"])["revision_id"] == workflow["revision_id"]


def test_indicator_change_after_plan_approval_blocks_activation(setup, live):
    _, indicator, plan, _ = setup(False)
    approve(live, submit(live, "collection-plans", plan))
    expect(
        live.request(
            live.path("indicator-instances", indicator["object_id"]),
            method="PATCH",
            body=cmd({"local_applicability": "Changed population"}, indicator["revision_id"]),
        ),
        200,
    )
    denied = action(
        live,
        "indicator-instances",
        get(live, "indicator-instances", indicator["object_id"]),
        "activate",
        status=409,
    )
    assert denied["reason_code"] == "PLAN_INDICATOR_CHANGED"


def test_plan_server_pin_and_same_tenant_scope_denials(setup, live):
    programme, _, plan, _ = setup(False)
    expect(
        live.request(
            live.path("collection-plans", plan["object_id"]),
            method="PATCH",
            body=cmd({"indicator_revision": str(uuid.uuid4())}, plan["revision_id"]),
        ),
        422,
    )
    expect(live.request(live.path("collection-plans", plan["object_id"]), actor="partner"), 404)
    expect(
        live.request(
            live.path("collection-plans"), actor="partner", method="POST", body=cmd({"title": "Escalation"})
        ),
        403,
    )
    action(live, "programmes", programme, "ready", actor="partner", status=404)


def test_readiness_rechecks_assignment_suspension(setup, live):
    programme, indicator, plan, _ = setup(False)
    approve(live, submit(live, "collection-plans", plan))
    action(live, "indicator-instances", indicator, "activate")
    reviewer = live.fixture["actors"]["reviewer"]
    with live.db() as c:
        c.execute(
            "UPDATE impact.tenant_principal SET active=false WHERE tenant_id=%s AND principal_id=%s",
            (reviewer["tenant_id"], reviewer["principal_id"]),
        )
    try:
        readiness = get(live, "programmes", programme["object_id"] + "/readiness")
        assert not readiness["ready"]
        action(live, "programmes", programme, "ready", status=422)
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.tenant_principal SET active=true WHERE tenant_id=%s AND principal_id=%s",
                (reviewer["tenant_id"], reviewer["principal_id"]),
            )


def get(live, route, obj=None, actor="author"):
    return expect(live.request(live.path(route, obj), actor=actor), 200)


def create(live, route, data):
    receipt = expect(live.request(live.path(route), method="POST", body=cmd(data)), 201)
    return get(live, route, receipt["object_id"])


def action(live, route, row, verb, data=None, actor="author", status=200, body=None):
    return expect(
        live.request(
            live.path(route, row["object_id"]) + "/actions/" + verb,
            actor=actor,
            method="POST",
            body=body or cmd(data or {}, row["revision_id"]),
        ),
        status,
    )


def submit(live, route, row):
    template = get(live, "workflow-templates")["items"][0]
    receipt = action(live, route, row, "submit", {"workflow_version": template["revision_id"]})
    return get(live, "workflows", receipt["object_id"])


def approve(live, workflow):
    return action(
        live,
        "workflows",
        workflow,
        "approve",
        {
            "candidate_revision": workflow["data"]["candidate_revision"],
            "reason": "Verified the exact configuration and eligibility.",
        },
        actor="reviewer",
    )


def measurement_builder(live):
    """What the `setup` fixture hands to a test: a builder of one configured measurement (programme,
    approved definition pinned by an indicator instance, five-obligation collection plan on the
    fixture period), activated end to end unless `activate` is false. A plain function so that a
    module can build a measurement without importing the fixture under a name it then shadows."""

    def build(activate=True):
        calendar = get(live, "reporting-calendars")["items"][0]
        geography = get(live, "geographies")["items"][0]
        programme = create(
            live,
            "programmes",
            {
                "code": "CFG",
                "title": "Configuration " + str(uuid.uuid4())[:8],
                "programme_type": "Health",
                "starts_at": "2026-01-01T00:00:00Z",
                "ends_at": "2027-01-01T00:00:00Z",
                "reporting_calendar_id": calendar["object_id"],
                "geography_id": geography["object_id"],
            },
        )
        d = create(live, "indicator-definitions", definition())
        approve(live, submit(live, "indicator-definitions", d))
        d = get(live, "indicator-definitions", d["object_id"])
        indicator = create(
            live,
            "indicator-instances",
            {
                "programme_id": programme["object_id"],
                "definition_version": d["revision_id"],
                "local_applicability": "Registered households",
                "collector_id": live.fixture["actors"]["author"]["principal_id"],
                "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
            },
        )
        period = get(live, "periods", live.records["period"]["object_id"])
        key = str(uuid.uuid4())
        plan = create(
            live,
            "collection-plans",
            {
                "title": "Quarterly collection",
                "indicator_id": indicator["object_id"],
                "period_id": period["object_id"],
                "obligations": [
                    {
                        "label": f"Partner {i + 1}",
                        "source_namespace": "MANUAL",
                        "source_key": key + "-" + str(i),
                        "due_at": "2026-09-01T00:00:00Z",
                    }
                    for i in range(5)
                ],
            },
        )
        if activate:
            approve(live, submit(live, "collection-plans", plan))
            plan = get(live, "collection-plans", plan["object_id"])
            action(live, "indicator-instances", indicator, "activate")
            indicator = get(live, "indicator-instances", indicator["object_id"])
            action(live, "programmes", programme, "ready")
            programme = get(live, "programmes", programme["object_id"])
            action(live, "programmes", programme, "activate")
            programme = get(live, "programmes", programme["object_id"])
        return programme, indicator, plan, period

    return build


@pytest.fixture
def setup(live):
    return measurement_builder(live)


def observation(live, indicator, source):
    return create(
        live,
        "observations",
        {
            "source_namespace": "MANUAL",
            "source_key": source,
            "indicator_id": indicator["object_id"],
            "event_at": "2026-08-15T12:00:00Z",
            "captured_at": "2026-08-15T13:00:00Z",
            "capture_zone": "UTC",
            "value_state": "PRESENT",
            "value": "10",
            "source_version": "1",
            "dimension_values": {},
        },
    )


def result(live, indicator, period):
    receipt = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    return get(live, "calculated-results", receipt["object_id"])


def test_end_to_end_activation_and_fsd_coverage(setup, live):
    programme, indicator, plan, period = setup()
    assert programme["lifecycle_state"] == indicator["lifecycle_state"] == "Active"
    for i in range(4):
        row = observation(live, indicator, plan["data"]["obligations"][i]["source_key"])
        workflow = submit(live, "observations", row)
        assert workflow["data"]["stages"][0]["candidate_membership_ids"] == [
            live.fixture["actors"]["reviewer"]["membership_id"]
        ]
        if i < 3:
            approve(live, workflow)
    extra = observation(live, indicator, "unplanned-" + str(uuid.uuid4()))
    approve(live, submit(live, "observations", extra))
    r = result(live, indicator, period)
    validate("CalculatedResult", r)
    d = r["data"]
    cov = d["coverage"]
    assert d["value"] == "30" and d["mode"] == "PROVISIONAL"
    assert [
        cov[k]
        for k in [
            "expected_count",
            "received_count",
            "valid_count",
            "approved_count",
            "pending_count",
            "missing_count",
            "unplanned_count",
        ]
    ] == [5, 4, 4, 3, 1, 1, 1]
    assert cov["approval_percent"] == "60.00" and cov["plan_revision"] == plan["revision_id"]
    manifest = get(live, "lineage-manifests", d["lineage_manifest_id"])
    assert (
        manifest["data"]["plan_revision"] == plan["revision_id"]
        and len(manifest["data"]["source_revisions"]) == 5
    )
    before = r
    approve(live, get(live, "workflows", workflow["object_id"]))
    assert get(live, "calculated-results", before["object_id"])["data"]["freshness"]["stale"]


def test_draft_readiness_explains_blockers_and_denies_activation(live):
    row = create(live, "programmes", {"title": "Incomplete"})
    readiness = get(live, "programmes", row["object_id"] + "/readiness")
    validate("ProgrammeReadiness", readiness)
    assert not readiness["ready"] and any(not c["passed"] for c in readiness["checks"])
    action(live, "programmes", row, "ready", status=422)
    action(live, "programmes", row, "activate", status=409)
    assert get(live, "programmes", row["object_id"])["revision_id"] == row["revision_id"]


def test_plan_independence_typed_review_and_immutable_approval(setup, live):
    _, _, plan, _ = setup(False)
    workflow = submit(live, "collection-plans", plan)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate")
    validate("ReviewCandidate", candidate)
    assert candidate["kind"] == "CollectionPlan"
    action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Self approval"},
        status=403,
    )
    approve(live, workflow)
    approved = get(live, "collection-plans", plan["object_id"])
    expect(
        live.request(
            live.path("collection-plans", plan["object_id"]),
            method="PATCH",
            body=cmd({"title": "Changed"}, approved["revision_id"]),
        ),
        409,
    )


def test_duplicate_plan_competes_at_approval_and_rolls_back(setup, live):
    _, _, plan, _ = setup(False)
    duplicate = create(live, "collection-plans", plan["data"])
    w1 = submit(live, "collection-plans", plan)
    w2 = submit(live, "collection-plans", duplicate)
    approve(live, w1)
    action(
        live,
        "workflows",
        w2,
        "approve",
        {"candidate_revision": w2["data"]["candidate_revision"], "reason": "Second plan"},
        actor="reviewer",
        status=409,
    )
    assert get(live, "workflows", w2["object_id"])["revision_id"] == w2["revision_id"]
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.review_decision WHERE tenant_id=%s AND workflow_id=%s",
                (live.fixture["tenant_a"], w2["object_id"]),
            ).fetchone()["n"]
            == 0
        )


def test_return_edit_and_resubmit_creates_new_candidate(setup, live):
    _, _, plan, _ = setup(False)
    w = submit(live, "collection-plans", plan)
    action(
        live,
        "workflows",
        w,
        "return",
        {"candidate_revision": w["data"]["candidate_revision"], "reason": "Clarify labels"},
        actor="reviewer",
    )
    returned = get(live, "collection-plans", plan["object_id"])
    expect(
        live.request(
            live.path("collection-plans", plan["object_id"]),
            method="PATCH",
            body=cmd({"title": "Clarified plan"}, returned["revision_id"]),
        ),
        200,
    )
    new = submit(live, "collection-plans", get(live, "collection-plans", plan["object_id"]))
    assert new["data"]["candidate_revision"] != w["data"]["candidate_revision"]
    approve(live, new)


@pytest.mark.parametrize(
    "change", [{"obligations": []}, {"lifecycle_state": "Approved"}, {"indicator_id": str(uuid.uuid4())}]
)
def test_invalid_plan_inputs_rejected(live, change):
    response = live.request(live.path("collection-plans"), method="POST", body=cmd(change))
    assert response.status_code in {404, 422}


def test_plan_duplicate_source_and_period_bounds(setup, live):
    _, _, plan, _ = setup(False)
    for entries in [
        [plan["data"]["obligations"][0]] * 2,
        [{**plan["data"]["obligations"][0], "due_at": "2025-01-01T00:00:00Z"}],
    ]:
        expect(
            live.request(
                live.path("collection-plans", plan["object_id"]),
                method="PATCH",
                body=cmd({"obligations": entries}, plan["revision_id"]),
            ),
            422,
        )


def test_activation_requires_approved_plan_and_independent_assignments(setup, live):
    _, indicator, plan, _ = setup(False)
    action(live, "indicator-instances", indicator, "activate", status=422)
    approve(live, submit(live, "collection-plans", plan))
    expect(
        live.request(
            live.path("indicator-instances", indicator["object_id"]),
            method="PATCH",
            body=cmd(
                {"reviewer_id": live.fixture["actors"]["author"]["principal_id"]}, indicator["revision_id"]
            ),
        ),
        200,
    )
    action(
        live,
        "indicator-instances",
        get(live, "indicator-instances", indicator["object_id"]),
        "activate",
        status=422,
    )


def test_not_active_measurement_cannot_submit_or_calculate(setup, live):
    _, indicator, _, period = setup(False)
    row = observation(live, indicator, str(uuid.uuid4()))
    template = get(live, "workflow-templates")["items"][0]
    action(live, "observations", row, "submit", {"workflow_version": template["revision_id"]}, status=409)
    action(
        live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]}, status=409
    )


def test_ready_revision_recheck_and_idempotency(setup, live):
    programme, indicator, plan, _ = setup(False)
    approve(live, submit(live, "collection-plans", plan))
    action(live, "indicator-instances", indicator, "activate")
    body = cmd({}, programme["revision_id"])
    first = action(live, "programmes", programme, "ready", body=body)
    assert action(live, "programmes", programme, "ready", body=body) == first
    action(live, "programmes", programme, "activate", status=409)
    ready = get(live, "programmes", programme["object_id"])
    expect(
        live.request(
            live.path("programmes", ready["object_id"]),
            method="PATCH",
            body=cmd({"title": "Forbidden"}, ready["revision_id"]),
        ),
        409,
    )
    action(live, "programmes", ready, "revise", {"reason": "Correct calendar"})
    assert get(live, "programmes", ready["object_id"])["lifecycle_state"] == "Draft"


def test_new_plan_invalidates_pre_plan_result(live):
    indicator = get(live, "indicator-instances", live.records["indicator_a"]["object_id"])
    period = get(live, "periods", live.records["period"]["object_id"])
    before = result(live, indicator, period)
    # Trusted test fixture insertion isolates freshness from the legacy programme's missing configuration.
    with live.db() as c:
        from types import SimpleNamespace
        from impact_api.store import Context, write

        actor = live.fixture["actors"]["author"]
        tenant = actor["tenant_id"]
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        ctx = Context(
            tenant,
            actor["principal_id"],
            actor["membership_id"],
            SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
            0,
            0,
            [],
        )
        plan = write(
            c,
            ctx,
            "CollectionPlan",
            {
                "title": "Freshness qualification",
                "indicator_id": indicator["object_id"],
                "period_id": period["object_id"],
                "obligations": [
                    {
                        "label": "Expected",
                        "source_namespace": "MANUAL",
                        "source_key": "qualification-only",
                        "due_at": "2026-09-30T00:00:00Z",
                    }
                ],
            },
            "Approved",
        )
        c.execute(
            "INSERT INTO impact.collection_plan_binding VALUES(%s,%s,%s,%s,%s)",
            (tenant, indicator["object_id"], period["object_id"], plan["object_id"], plan["revision_id"]),
        )
    try:
        assert get(live, "calculated-results", before["object_id"])["data"]["freshness"]["stale"]
    finally:
        with live.db() as c:
            c.execute(
                "DELETE FROM impact.collection_plan_binding WHERE tenant_id=%s AND plan_id=%s",
                (live.fixture["tenant_a"], plan["object_id"]),
            )


def test_members_directory_minimal_fields_and_capability_gate(live):
    directory = get(live, "measurement-members")
    validate("MeasurementMembers", directory)
    assert directory["items"] and all("email" not in str(item).lower() for item in directory["items"])
    expect(live.request(live.path("measurement-members"), actor="partner"), 403)


def test_cross_tenant_plan_and_readiness_hidden(setup, live):
    programme, _, plan, _ = setup(False)
    for route, obj in [
        ("collection-plans", plan["object_id"]),
        ("programmes", programme["object_id"] + "/readiness"),
    ]:
        expect(live.request(live.path(route, obj, tenant=live.fixture["tenant_b"])), 404)


def test_collection_binding_forced_rls(live):
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.collection_plan_binding WHERE tenant_id=%s",
                (live.fixture["tenant_a"],),
            ).fetchone()["n"]
            == 0
        )
