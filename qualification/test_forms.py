"""Qualification of web forms (v0.20): form versions with independent approval and publication,
server-side response validation, and submissions that become observations with explicit value
states through the existing observation review and calculation path."""
# ruff: noqa: F811

import os
import uuid

import pytest
from impact_api.contracts import validate
from test_live_application import cmd, expect
from test_measurement import get, create, action, submit, approve  # noqa: F401
from test_calculation_methods import SEX, build
from test_measurement_unit import definition
from test_native_roles import connect, denied, query  # noqa: F401
from test_planning import db_counts, failure, post

WHEN = {"event_at": "2026-08-15T12:00:00Z", "captured_at": "2026-08-15T13:00:00Z", "capture_zone": "UTC"}


def fields(indicator, households_required=False):
    """Consent gate, a sex code feeding the indicator's pinned disaggregation, and a household
    count bound to the indicator that applies only when consent is given."""
    return [
        {
            "field_id": str(uuid.uuid4()),
            "stable_code": "consent",
            "position": 0,
            "field_type": "BOOLEAN",
            "label": "Consent given",
            "required": True,
        },
        {
            "field_id": str(uuid.uuid4()),
            "stable_code": "sex",
            "position": 1,
            "field_type": "SINGLE_CHOICE",
            "label": "Sex of respondent",
            "required": True,
            "choices": [
                {"code": "F", "label": "Female", "active": True},
                {"code": "M", "label": "Male", "active": True},
            ],
            "dimension_code": "sex",
        },
        {
            "field_id": str(uuid.uuid4()),
            "stable_code": "households",
            "position": 2,
            "field_type": "INTEGER",
            "label": "Households reached",
            "required": households_required,
            "minimum": "0",
            "maximum": "1000",
            "indicator_id": indicator["object_id"],
            "value_role": "VALUE",
            "relevant_when": {"field_code": "consent", "equals": "true"},
        },
        {
            "field_id": str(uuid.uuid4()),
            "stable_code": "note",
            "position": 3,
            "field_type": "TEXT",
            "label": "Note",
            "required": False,
            "max_length": 20,
        },
    ]


def form_data(indicator, **extra):
    return {
        "code": "HH-" + str(uuid.uuid4())[:6],
        "title": "Household visit",
        "programme_id": indicator["data"]["programme_id"],
        "fields": fields(indicator),
        "logic": [],
        "translation_versions": [],
        "compatibility_policy": "LOCK_PUBLISHED",
        **extra,
    }


def publish(live, form):
    workflow = submit(live, "forms", form)
    approve(live, workflow)
    form = get(live, "forms", form["object_id"])
    assert form["lifecycle_state"] == "Approved"
    action(
        live, "forms", form, "publish", {"approved_candidate_revision": form["revision_id"]}, actor="reviewer"
    )
    return get(live, "forms", form["object_id"] + "/published")


def planned(live, **changes):
    """A sex-disaggregated household count (or the definition `changes` describe) whose approved
    collection plan expects three units to report through the form: FORM/"<unit>/<indicator id>"."""
    calendar = get(live, "reporting-calendars")["items"][0]
    programme = create(
        live,
        "programmes",
        {
            "code": "FRM",
            "title": "Forms " + str(uuid.uuid4())[:8],
            "programme_type": "Health",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2027-01-01T00:00:00Z",
            "reporting_calendar_id": calendar["object_id"],
            "geography_id": get(live, "geographies")["items"][0]["object_id"],
        },
    )
    d = create(live, "indicator-definitions", definition(**(changes or {"disaggregation": SEX})))
    approve(live, submit(live, "indicator-definitions", d))
    d = get(live, "indicator-definitions", d["object_id"])
    indicator = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": d["revision_id"],
            "local_applicability": "Household visits",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    period = get(live, "periods", live.records["period"]["object_id"])
    units = ["unit-" + str(uuid.uuid4())[:8] for _ in range(3)]
    plan = create(
        live,
        "collection-plans",
        {
            "title": "Household visits",
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "obligations": [
                {
                    "label": unit,
                    "source_namespace": "FORM",
                    "source_key": unit + "/" + indicator["object_id"],
                    "due_at": "2026-09-01T00:00:00Z",
                }
                for unit in units
            ],
        },
    )
    approve(live, submit(live, "collection-plans", plan))
    action(live, "indicator-instances", indicator, "activate")
    indicator = get(live, "indicator-instances", indicator["object_id"])
    action(live, "programmes", programme, "ready")
    action(live, "programmes", get(live, "programmes", programme["object_id"]), "activate")
    return indicator, period, units


@pytest.fixture
def published(live):
    indicator, period, units = planned(live)
    form = create(live, "forms", form_data(indicator))
    return indicator, period, form, publish(live, form), units


def response(live, version, answers, actor="author", unit=None):
    data = {"form_version": version["form_version"], **WHEN, "answers": answers}
    return create_as(live, "submissions", {**data, **({"unit_key": unit} if unit else {})}, actor)


def create_as(live, route, data, actor):
    receipt = expect(live.request(live.path(route), actor=actor, method="POST", body=cmd(data)), 201)
    return get(live, route, receipt["object_id"], actor=actor)


def workflow_version(live):
    return get(live, "workflow-templates")["items"][0]["revision_id"]


def send(live, row, actor="author", operation=None, status=200, wf=None):
    return expect(
        live.request(
            live.path("submissions", row["object_id"]) + "/actions/submit",
            actor=actor,
            method="POST",
            body=cmd({"workflow_version": wf or workflow_version(live)}, row["revision_id"], operation),
        ),
        status,
    )


def observations(live, submission):
    return [get(live, "observations", o) for o in submission["data"]["observation_ids"]]


def workflow_of(live, observation_id):
    with live.db() as c:
        row = c.execute(
            "SELECT r.object_id FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.object_type='Workflow' AND v.payload->>'candidate_id'=%s",
            (observation_id,),
        ).fetchone()
    return get(live, "workflows", str(row["object_id"]))


ANSWERED = {
    "consent": {"kind": "BOOLEAN", "value": True},
    "sex": {"kind": "SINGLE_CHOICE", "value": "F"},
    "households": {"kind": "INTEGER", "value": 7},
}


def test_form_version_review_publication_and_submission_to_calculation(live, published):
    indicator, period, form, version, units = published
    validate("PublishedForm", version)
    assert version["version_number"] == 1 and version["data"]["fields"] == form["data"]["fields"]
    assert get(live, "forms", form["object_id"])["lifecycle_state"] == "Published"
    draft = response(live, version, ANSWERED, unit=units[0])
    assert draft["lifecycle_state"] == "Draft" and draft["data"]["review_state"] == "DRAFT"
    operation = str(uuid.uuid4())
    wf = workflow_version(live)
    receipt = send(live, draft, operation=operation, wf=wf)
    # Exact retry resolves to the original receipt; the same identifier with another payload conflicts.
    assert send(live, draft, operation=operation, wf=wf) == receipt
    other = str(uuid.uuid4())
    failure(
        live.request(
            live.path("submissions", draft["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": other}, draft["revision_id"], operation),
        ),
        409,
    )["code"] == "CONFLICT_OPERATION"
    submission = get(live, "submissions", draft["object_id"])
    validate("Submission", submission)
    assert submission["lifecycle_state"] == "Submitted" and submission["data"]["review_state"] == "SUBMITTED"
    assert submission["data"]["form_version"] == version["form_version"]
    assert submission["data"]["authenticated_uploader_id"] == live.fixture["actors"]["author"]["principal_id"]
    [obs] = observations(live, submission)
    assert obs["lifecycle_state"] == "Submitted"
    assert obs["data"]["source_namespace"] == "FORM"
    assert obs["data"]["source_key"] == units[0] + "/" + indicator["object_id"]
    assert obs["data"]["source_version"] == version["form_version"]
    assert obs["data"]["value_state"] == "PRESENT" and obs["data"]["value"] == "7"
    assert obs["data"]["dimension_values"] == {"sex": "F"}
    assert db_counts(live, draft["object_id"], "action_submissions_submit") == {
        "revisions": 2,
        "audit": 1,
        "outbox": 2,
        "receipts": 1,
    }
    # The observation and its review workflow carry their own audit and outbox events.
    obs_counts = db_counts(live, obs["object_id"], "action_submissions_submit")
    assert (obs_counts["revisions"], obs_counts["audit"], obs_counts["outbox"]) == (2, 1, 1)
    # The observation is reviewed like any other source: the collector cannot approve it.
    workflow = workflow_of(live, obs["object_id"])
    body = cmd(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Mine"},
        workflow["revision_id"],
    )
    failure(
        live.request(
            live.path("workflows", workflow["object_id"]) + "/actions/approve", method="POST", body=body
        ),
        403,
        "INDEPENDENCE_REQUIRED",
    )
    approve(live, workflow)
    # A second unit reports through the form; the third obligation stays missing.
    second = response(
        live,
        version,
        {
            **ANSWERED,
            "sex": {"kind": "SINGLE_CHOICE", "value": "M"},
            "households": {"kind": "INTEGER", "value": 3},
        },
        unit=units[1],
    )
    send(live, second)
    [other_obs] = observations(live, get(live, "submissions", second["object_id"]))
    approve(live, workflow_of(live, other_obs["object_id"]))
    result = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    value = get(live, "calculated-results", result["object_id"])["data"]
    assert value["value"] == "10" and value["mode"] == "PROVISIONAL"
    assert [(e["category"], e["value"]) for e in value["disaggregation"]] == [("F", "7"), ("M", "3")]
    cov = value["coverage"]
    assert [
        cov[k]
        for k in ["expected_count", "received_count", "approved_count", "missing_count", "unplanned_count"]
    ] == [3, 2, 2, 1, 0]
    # The same unit cannot report twice for the same indicator.
    duplicate = response(live, version, ANSWERED, unit=units[0])
    assert failure(send_raw(live, duplicate), 409)["code"] == "SOURCE_KEY_CONFLICT"
    # A submitted response cannot be submitted again: it is no longer a draft.
    assert (
        failure(send_raw(live, get(live, "submissions", draft["object_id"])), 409)["code"] == "INVALID_STATE"
    )
    # FORM is reserved for observations produced from a response; a direct observation cannot use it.
    direct = {
        "source_namespace": "FORM",
        "source_key": units[2] + "/" + indicator["object_id"],
        "indicator_id": indicator["object_id"],
        **WHEN,
        "value_state": "PRESENT",
        "value": "1",
        "source_version": "1",
        "dimension_values": {"sex": "F"},
    }
    failure(
        live.request(live.path("observations"), method="POST", body=cmd(direct)),
        422,
        "SOURCE_NAMESPACE_RESERVED",
    )
    manual = create(live, "observations", {**direct, "source_namespace": "MANUAL"})
    failure(
        post(
            live,
            "observations",
            {"source_namespace": "FORM"},
            revision=manual["revision_id"],
            obj=manual["object_id"],
        ),
        422,
        "SOURCE_NAMESPACE_RESERVED",
    )


def send_raw(live, row):
    return live.request(
        live.path("submissions", row["object_id"]) + "/actions/submit",
        method="POST",
        body=cmd({"workflow_version": workflow_version(live)}, row["revision_id"]),
    )


def test_form_review_requires_independence_and_publish_requires_approval(live):
    _, indicator, _, _ = build(live)
    form = create(live, "forms", form_data(indicator))
    assert db_counts(live, form["object_id"], "create_forms") == {
        "revisions": 1,
        "audit": 1,
        "outbox": 1,
        "receipts": 1,
    }
    failure(
        live.request(
            live.path("forms", form["object_id"]) + "/actions/publish",
            actor="reviewer",
            method="POST",
            body=cmd({"approved_candidate_revision": form["revision_id"]}, form["revision_id"]),
        ),
        409,
    )
    workflow = submit(live, "forms", form)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate")
    assert candidate["kind"] == "Form"
    body = cmd(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Self"},
        workflow["revision_id"],
    )
    failure(
        live.request(
            live.path("workflows", workflow["object_id"]) + "/actions/approve", method="POST", body=body
        ),
        403,
        "INDEPENDENCE_REQUIRED",
    )
    # Submitted for review, the schema is locked.
    failure(
        post(
            live,
            "forms",
            {"title": "Changed"},
            revision=workflow["data"]["candidate_revision"],
            obj=form["object_id"],
        ),
        409,
    )
    expect(live.request(live.path("forms", form["object_id"] + "/published")), 404)


def test_blank_answers_keep_explicit_value_states(live, published):
    indicator, _, _, version, _ = published
    cases = [
        (
            {"consent": {"kind": "BOOLEAN", "value": True}, "sex": {"kind": "SINGLE_CHOICE", "value": "M"}},
            "MISSING",
        ),
        (
            {**ANSWERED, "households": {"kind": "MISSING", "reason": "NOT_COLLECTED"}},
            "NOT_COLLECTED",
        ),
        ({**ANSWERED, "households": {"kind": "MISSING", "reason": "DECLINED"}}, "MISSING"),
        (
            {"consent": {"kind": "BOOLEAN", "value": False}, "sex": {"kind": "SINGLE_CHOICE", "value": "F"}},
            "NOT_APPLICABLE",
        ),
        ({**ANSWERED, "households": {"kind": "INTEGER", "value": 0}}, "PRESENT"),
    ]
    for answers, state in cases:
        row = response(live, version, answers)
        send(live, row)
        [obs] = observations(live, get(live, "submissions", row["object_id"]))
        assert obs["data"]["value_state"] == state, (answers, obs["data"])
        assert (obs["data"]["value"] is None) == (state != "PRESENT")
    assert obs["data"]["value"] == "0"


@pytest.mark.parametrize(
    "answers,reason",
    [
        ({**ANSWERED, "households": {"kind": "INTEGER", "value": 1001}}, "ANSWER_OUT_OF_RANGE"),
        ({**ANSWERED, "households": {"kind": "INTEGER", "value": -1}}, "ANSWER_OUT_OF_RANGE"),
        ({**ANSWERED, "households": {"kind": "DECIMAL", "value": "7"}}, "ANSWER_TYPE_MISMATCH"),
        ({**ANSWERED, "sex": {"kind": "SINGLE_CHOICE", "value": "X"}}, "ANSWER_CODE_NOT_ALLOWED"),
        ({**ANSWERED, "extra": {"kind": "TEXT", "value": "x"}}, "ANSWER_FIELD_UNKNOWN"),
        ({**ANSWERED, "note": {"kind": "TEXT", "value": "x" * 21}}, "ANSWER_OUT_OF_RANGE"),
    ],
)
def test_draft_answers_are_validated_against_the_version(live, published, answers, reason):
    _, _, _, version, _ = published
    body = cmd({"form_version": version["form_version"], **WHEN, "answers": answers})
    failure(live.request(live.path("submissions"), method="POST", body=body), 422, reason)


@pytest.mark.parametrize(
    "answers,reason",
    [
        ({"consent": {"kind": "BOOLEAN", "value": True}}, "REQUIRED_ANSWER_MISSING"),
        # A tampered payload cannot carry an answer to a field its relevance rule hides.
        (
            {**ANSWERED, "consent": {"kind": "BOOLEAN", "value": False}},
            "ANSWER_NOT_RELEVANT",
        ),
    ],
)
def test_submission_refuses_incomplete_and_hidden_answers(live, published, answers, reason):
    _, _, _, version, _ = published
    row = response(live, version, answers)
    failure(send_raw(live, row), 422, reason)
    after = get(live, "submissions", row["object_id"])
    assert after["revision_id"] == row["revision_id"] and after["lifecycle_state"] == "Draft"


def test_form_definition_validation(live):
    _, indicator, _, _ = build(live)
    base = form_data(indicator)

    def refused(change, reason):
        data = {**base, "fields": [dict(f) for f in base["fields"]]}
        change(data["fields"])
        failure(live.request(live.path("forms"), method="POST", body=cmd(data)), 422, reason)

    refused(
        lambda f: f[1].update(choices=[{"code": "X", "label": "Other", "active": True}]),
        "ANSWER_CODE_NOT_ALLOWED",
    )
    refused(
        lambda f: f[0].update(relevant_when={"field_code": "note", "equals": "x"}), "FORM_RELEVANCE_INVALID"
    )
    refused(
        lambda f: f[2].update(relevant_when={"field_code": "consent", "equals": "maybe"}),
        "FORM_RELEVANCE_INVALID",
    )
    refused(
        lambda f: f[3].update(indicator_id=indicator["object_id"], value_role="VALUE"), "FORM_BINDING_INVALID"
    )
    refused(lambda f: f[2].update(value_role=None), "FORM_BINDING_INVALID")
    refused(lambda f: f[3].update(stable_code="consent"), "FORM_FIELD_DUPLICATE")
    refused(lambda f: f[2].update(minimum="10", maximum="1"), "FORM_FIELD_INVALID")
    refused(lambda f: f[1].update(dimension_code="region"), "FORM_BINDING_INVALID")
    # Unknown properties and logic rules are refused by the closed contract.
    data = {**base, "fields": [{**base["fields"][0], "colour": "red"}]}
    expect(live.request(live.path("forms"), method="POST", body=cmd(data)), 422)
    data = {**base, "logic": [{"rule_id": str(uuid.uuid4())}]}
    expect(live.request(live.path("forms"), method="POST", body=cmd(data)), 422)
    # A draft may be incomplete; submission for review requires a complete version.
    draft = create(live, "forms", {"code": "PART", "title": "Partial"})
    template = get(live, "workflow-templates")["items"][0]
    failure(
        live.request(
            live.path("forms", draft["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": template["revision_id"]}, draft["revision_id"]),
        ),
        422,
        "SUBMISSION_INCOMPLETE",
    )


def test_superseded_version_quarantines_rather_than_inventing_answers(live, published):
    indicator, _, form, v1, _ = published
    offline = response(live, v1, ANSWERED)
    # A new version adds a mandatory question while the v1 response is still unsent.
    head = get(live, "forms", form["object_id"])
    extra = {
        "field_id": str(uuid.uuid4()),
        "stable_code": "water",
        "position": 4,
        "field_type": "SINGLE_CHOICE",
        "label": "Safe water",
        "required": True,
        "choices": [
            {"code": "yes", "label": "Yes", "active": True},
            {"code": "no", "label": "No", "active": True},
        ],
    }
    expect(
        post(
            live,
            "forms",
            {"fields": head["data"]["fields"] + [extra]},
            revision=head["revision_id"],
            obj=form["object_id"],
        ),
        200,
    )
    revised = get(live, "forms", form["object_id"])
    assert revised["lifecycle_state"] == "Draft"
    # Still collecting on v1 until v2 publishes.
    assert get(live, "forms", form["object_id"] + "/published")["form_version"] == v1["form_version"]
    v2 = publish(live, revised)
    assert v2["version_number"] == 2 and v2["supersedes_revision"] == v1["form_version"]
    assert [v["form_version"] for v in v2["versions"]] == [v1["form_version"], v2["form_version"]]
    receipt = send(live, offline)
    assert receipt["business_state"] == "Quarantined"
    kept = get(live, "submissions", offline["object_id"])
    assert kept["data"]["review_state"] == "QUARANTINED"
    assert kept["data"]["quarantine_reason"] == "FORM_VERSION_SUPERSEDED"
    assert kept["data"]["answers"] == ANSWERED and "water" not in kept["data"]["answers"]
    assert kept["data"]["observation_ids"] == [] and kept["data"]["form_version"] == v1["form_version"]
    # The current version requires the new answer.
    row = response(live, v2, ANSWERED)
    failure(send_raw(live, row), 422, "REQUIRED_ANSWER_MISSING")
    # A draft cannot silently move to another version.
    failure(
        post(
            live,
            "submissions",
            {"form_version": v2["form_version"]},
            revision=offline["revision_id"],
            obj=offline["object_id"],
        ),
        409,
    )
    with live.db() as c:
        rows = c.execute(
            "SELECT version_number,supersedes_revision FROM impact.form_publication WHERE form_id=%s ORDER BY 1",
            (form["object_id"],),
        ).fetchall()
    assert [
        (r["version_number"], str(r["supersedes_revision"]) if r["supersedes_revision"] else None)
        for r in rows
    ] == [
        (1, None),
        (2, v1["form_version"]),
    ]


def test_form_and_submission_access_boundaries(live, published):
    _, _, form, version, _ = published
    for route, obj in [("forms", form["object_id"]), ("forms", form["object_id"] + "/published")]:
        expect(live.request(live.path(route, obj), actor="other_tenant"), 404)
        response_ = live.request(live.path(route, obj), actor="revoked")
        assert response_.status_code in {401, 404}, response_.text
    row = response(live, version, ANSWERED)
    expect(live.request(live.path("submissions", row["object_id"]), actor="other_tenant"), 404)
    # Enumerators collect but never design forms; partners do neither.
    failure(live.request(live.path("forms"), actor="enumerator", method="POST", body=cmd({"code": "E"})), 403)
    failure(live.request(live.path("submissions"), actor="partner", method="POST", body=cmd({**WHEN})), 403)
    # An unpublished revision cannot collect.
    draft = create(live, "forms", {"code": "DRAFT", "title": "Draft only"})
    body = cmd({"form_version": draft["revision_id"], **WHEN, "answers": {}})
    failure(
        live.request(live.path("submissions"), method="POST", body=body), 409, "FORM_VERSION_NOT_PUBLISHED"
    )
    # Stale revision.
    expect(
        post(
            live,
            "submissions",
            {"capture_zone": "Africa/Kigali"},
            revision=row["revision_id"],
            obj=row["object_id"],
        ),
        200,
    )
    failure(
        post(live, "submissions", {"capture_zone": "UTC"}, revision=row["revision_id"], obj=row["object_id"]),
        409,
    )
    # Server-owned fields cannot be supplied.
    for field, value in [("review_state", "SUBMITTED"), ("observation_ids", [])]:
        body = cmd({"form_version": version["form_version"], **WHEN, "answers": {}, field: value})
        expect(live.request(live.path("submissions"), method="POST", body=body), 422)


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="native PostgreSQL only: PGlite serves one superuser session and has no login-role "
    "topology to test (run scripts/run.py test --native)",
)
def test_native_form_publication_register_is_fenced_and_insert_only(connect, live, published):
    _, _, form, version, _ = published
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    c = connect("APP")
    assert query(c, "SELECT count(*) FROM impact.form_publication", role="impact_app") == [(0,)]
    for statement in [
        "UPDATE impact.form_publication SET published_at=now()",
        "DELETE FROM impact.form_publication",
    ]:
        assert "permission denied" in denied(c, statement, role="impact_app", tenant=tenant_a)
    count = "SELECT count(*) FROM impact.form_publication WHERE form_revision=%s"
    assert query(c, count, (version["form_version"],), role="impact_app", tenant=tenant_a) == [(1,)]
    assert query(c, count, (version["form_version"],), role="impact_app", tenant=tenant_b) == [(0,)]
    for login, role in [("PLATFORM", "impact_platform"), ("IDENTITY", "impact_identity")]:
        other = connect(login)
        assert "permission denied" in denied(
            other, "SELECT count(*) FROM impact.form_publication", role=role, tenant=tenant_a
        )


def test_submitter_without_indicator_read_access_fails_closed(live, published):
    """Known limit of this build: turning a response into observations reuses the observation
    submission path, which reads the bound indicator instance and definition with the submitter's
    own capabilities. ENUMERATOR can save a draft but its submit fails closed (404) and writes
    nothing; AUTHOR and PROGRAMME_MANAGER submit."""
    _, _, _, version, units = published
    row = response(live, version, ANSWERED, actor="enumerator", unit=units[2])
    r = live.request(
        live.path("submissions", row["object_id"]) + "/actions/submit",
        actor="enumerator",
        method="POST",
        body=cmd({"workflow_version": workflow_version(live)}, row["revision_id"]),
    )
    failure(r, 404)
    after = get(live, "submissions", row["object_id"], actor="enumerator")
    assert after["revision_id"] == row["revision_id"] and after["lifecycle_state"] == "Draft"


def test_numerator_and_denominator_answers_pool_into_a_percentage(live):
    """Two answers feed one ratio observation; the result pools the components (never averages
    the per-response percentages); a zero denominator is UNDEFINED, never zero."""
    indicator, period, units = planned(
        live,
        measurement_type="PERCENTAGE",
        unit="percent",
        combination_rule="POOLED_RATIO",
        numerator_meaning="Households with safe water",
        denominator_meaning="Households visited",
        display_decimals=2,
    )

    def number(code, role, position):
        return {
            "field_id": str(uuid.uuid4()),
            "stable_code": code,
            "position": position,
            "field_type": "INTEGER",
            "label": code,
            "required": True,
            "minimum": "0",
            "indicator_id": indicator["object_id"],
            "value_role": role,
        }

    items = [number("safe", "NUMERATOR", 0), number("visited", "DENOMINATOR", 1)]
    # Both components are required before a ratio form can be reviewed.
    partial = create(live, "forms", {**form_data(indicator), "fields": items[:1]})
    failure(
        live.request(
            live.path("forms", partial["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": workflow_version(live)}, partial["revision_id"]),
        ),
        422,
        "FORM_BINDING_INVALID",
    )
    form = create(live, "forms", {**form_data(indicator), "fields": items})
    version = publish(live, form)

    def answer(unit, n, d):
        row = response(
            live,
            version,
            {"safe": {"kind": "INTEGER", "value": n}, "visited": {"kind": "INTEGER", "value": d}},
            unit=unit,
        )
        return row, live.request(
            live.path("submissions", row["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": workflow_version(live)}, row["revision_id"]),
        )

    values = []
    for unit, n, d in [(units[0], 50, 100), (units[1], 1, 10), (units[2], 0, 0)]:
        row, sent = answer(unit, n, d)
        expect(sent, 200)
        [obs] = observations(live, get(live, "submissions", row["object_id"]))
        values.append((obs["data"]["value_state"], obs["data"]["value"], obs["data"].get("numerator")))
        approve(live, workflow_of(live, obs["object_id"]))
    assert values == [("PRESENT", "50", "50"), ("PRESENT", "10", "1"), ("UNDEFINED", None, None)]
    for n, d in [(11, 10), (1, 0)]:
        row, sent = answer("unit-extra", n, d)
        failure(sent, 422, "INVALID_COMPONENTS")
    result = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    value = get(live, "calculated-results", result["object_id"])["data"]
    assert value["numerator"] == "51" and value["denominator"] == "110"
    assert value["displayed_value"] == "46.36"


def test_response_drafters_are_authors_of_its_observations(live, published):
    """Independence follows the response: the enumerator drafts the answers and the author submits;
    both natural persons are authors of the resulting observation and of its review candidate, so
    neither can approve it (the review decision checks exactly this `workflow_author` set)."""
    _, _, _, version, units = published
    row = response(live, version, ANSWERED, actor="enumerator", unit=units[1])
    expect(
        post(
            live,
            "submissions",
            {"answers": {**ANSWERED, "households": {"kind": "INTEGER", "value": 9}}},
            actor="enumerator",
            revision=row["revision_id"],
            obj=row["object_id"],
        ),
        200,
    )
    row = get(live, "submissions", row["object_id"])
    send(live, row, actor="author")
    [obs] = observations(live, get(live, "submissions", row["object_id"]))
    assert obs["data"]["value"] == "9"
    workflow = workflow_of(live, obs["object_id"])
    actors = live.fixture["actors"]
    with live.db() as c:
        authors = {
            str(r["natural_identity_id"])
            for r in c.execute(
                "SELECT natural_identity_id FROM impact.workflow_author WHERE workflow_id=%s AND candidate_revision=%s",
                (workflow["object_id"], workflow["data"]["candidate_revision"]),
            ).fetchall()
        }
    assert authors == {actors["enumerator"]["natural_identity_id"], actors["author"]["natural_identity_id"]}
    body = cmd(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Submitted by me"},
        workflow["revision_id"],
    )
    failure(
        live.request(
            live.path("workflows", workflow["object_id"]) + "/actions/approve", method="POST", body=body
        ),
        403,
        "INDEPENDENCE_REQUIRED",
    )
    approve(live, workflow)
