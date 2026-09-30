"""Qualification of results frameworks, targets, baselines, milestones and targets versus actuals."""
# ruff: noqa: F811

from decimal import Decimal
import json
import os
import uuid
from urllib.parse import quote

import psycopg
import pytest
from psycopg.types.json import Jsonb
from test_live_application import cmd, expect
from test_measurement import setup, get, create, action, submit, approve, observation, result  # noqa: F401
from test_period_governance import complete_period, request_close
from test_native_roles import connect, denied, query  # noqa: F401

TODAY = "2026-12-31"


def nodes(owner, indicator=None):
    """Impact -> outcome -> output (measured by `indicator`) -> activity, stable identities."""
    ids = [str(uuid.uuid4()) for _ in range(4)]
    levels = ["IMPACT", "OUTCOME", "OUTPUT", "ACTIVITY"]
    return [
        {
            "node_id": ids[i],
            "node_type": level,
            "title": level.title() + " statement",
            "definition": "The intended " + level.lower() + " of the programme.",
            "parent_node_id": ids[i - 1] if i else None,
            "owner_id": owner,
            "indicator_ids": [indicator] if indicator and level == "OUTPUT" else [],
        }
        for i, level in enumerate(levels)
    ]


def content(data):
    """A stored framework payload as a draft command may carry it: exception authorship is
    server-owned and never sent."""
    return {
        **data,
        "exceptions": [
            {k: e[k] for k in ["object_id", "rule", "reason", "review_date"]}
            for e in data.get("exceptions", [])
        ],
    }


def exceptions(items, *rules):
    return [
        {
            "object_id": n["node_id"],
            "rule": "UNMEASURED_RESULT",
            "reason": "Measured at the end-line evaluation, outside routine monitoring.",
            "review_date": TODAY,
        }
        for n in items
        if n["node_type"] in rules
    ]


def framework(live, programme, indicator, **extra):
    owner = live.fixture["actors"]["author"]["principal_id"]
    items = nodes(owner, indicator["object_id"])
    data = {
        "programme_id": programme["object_id"],
        "version_label": "Baseline 2026",
        "nodes": items,
        "relationships": [],
        "effective_from": "2026-01-01T00:00:00Z",
        "exceptions": exceptions(items, "IMPACT", "OUTCOME"),
        **extra,
    }
    return create(live, "frameworks", data)


def approved(live, route, row):
    workflow = submit(live, route, row)
    approve(live, workflow)
    return get(live, route, row["object_id"]), workflow


def target(live, indicator, period, **data):
    return create(
        live,
        "targets",
        {
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "target_kind": "VALUE",
            "value_state": "PRESENT",
            "value": "40",
            "direction": "HIGHER",
            "target_basis": "ORIGINAL",
            **data,
        },
    )


def failure(response, status, reason=None):
    body = expect(response, status)
    if reason:
        assert body.get("reason_code") == reason, body
    return body


def post(live, route, data, actor="author", operation=None, revision=None, obj=None, verb=None):
    path = live.path(route, obj) + ("/actions/" + verb if verb else "")
    method = "PATCH" if obj and not verb else "POST"
    return live.request(path, actor=actor, method=method, body=cmd(data, revision, operation))


def db_counts(live, object_id, op):
    with live.db() as c:
        return {
            "revisions": c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s", (object_id,)
            ).fetchone()["n"],
            "audit": c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE object_reference=%s AND action_type=%s",
                (object_id, op),
            ).fetchone()["n"],
            "outbox": c.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE payload->>'aggregate_id'=%s",
                (object_id,),
            ).fetchone()["n"],
            "receipts": c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE command_type=%s AND outcome->>'object_id'=%s",
                (op, object_id),
            ).fetchone()["n"],
        }


def test_framework_draft_review_baseline_and_child_version(live, setup):
    programme, indicator, _, _ = setup(False)
    draft = framework(live, programme, indicator)
    assert draft["lifecycle_state"] == "Draft"
    assert db_counts(live, draft["object_id"], "create_frameworks") == {
        "revisions": 1,
        "audit": 1,
        "outbox": 1,
        "receipts": 1,
    }
    # FT-PLN-001: renaming an output in the draft keeps its identity and its indicator placement.
    items = draft["data"]["nodes"]
    output = next(n for n in items if n["node_type"] == "OUTPUT")
    renamed = [{**n, "title": "Households registered"} if n is output else n for n in items]
    expect(
        post(live, "frameworks", {"nodes": renamed}, revision=draft["revision_id"], obj=draft["object_id"]),
        200,
    )
    draft = get(live, "frameworks", draft["object_id"])
    assert [n["node_id"] for n in draft["data"]["nodes"]] == [n["node_id"] for n in items]
    moved = next(n for n in draft["data"]["nodes"] if n["node_id"] == output["node_id"])
    assert moved["title"] == "Households registered" and moved["indicator_ids"] == [indicator["object_id"]]
    report = get(live, "frameworks", draft["object_id"] + "/completeness")
    assert report["ready"] and report["comparison"] is None
    assert {(i["rule"], i["excepted"]) for i in report["issues"]} == {("UNMEASURED_RESULT", True)}

    workflow = submit(live, "frameworks", draft)
    own = action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Own work"},
        status=403,
    )
    assert own["reason_code"] == "INDEPENDENCE_REQUIRED"
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    assert candidate["kind"] == "Framework" and candidate["completeness"]["ready"]
    approve(live, workflow)
    first = get(live, "frameworks", draft["object_id"])
    assert first["lifecycle_state"] == "Approved"
    with live.db() as c:
        baseline = c.execute(
            "SELECT * FROM impact.framework_baseline WHERE programme_id=%s", (programme["object_id"],)
        ).fetchall()
    assert [(b["baseline_version"], str(b["framework_revision"])) for b in baseline] == [
        (1, first["revision_id"])
    ]
    # An approved framework is immutable; a second root baseline is refused.
    failure(
        post(
            live, "frameworks", {"version_label": "x"}, revision=first["revision_id"], obj=first["object_id"]
        ),
        409,
    )
    failure(
        post(
            live,
            "frameworks",
            {"programme_id": programme["object_id"], "version_label": "Second root", "nodes": items},
        ),
        409,
        "FRAMEWORK_BASELINE_EXISTS",
    )

    # FT-PLN-003: a child draft revises one outcome from an effective date; the approved baseline stays.
    outcome = next(n for n in first["data"]["nodes"] if n["node_type"] == "OUTCOME")
    revised_nodes = [
        {**n, "title": "Revised outcome statement"} if n["node_id"] == outcome["node_id"] else n
        for n in first["data"]["nodes"]
    ]
    child = create(
        live,
        "frameworks",
        {
            **content(first["data"]),
            "version_label": "July revision",
            "nodes": revised_nodes,
            "supersedes_revision": first["revision_id"],
            "effective_from": "2026-07-01T00:00:00Z",
        },
    )
    comparison = get(live, "frameworks", child["object_id"] + "/completeness")["comparison"]
    assert comparison["base_revision"] == first["revision_id"] and comparison["changed"] == [
        outcome["node_id"]
    ]
    assert comparison["added"] == comparison["removed"] == []
    early = post(
        live,
        "frameworks",
        {"effective_from": "2025-12-01T00:00:00Z"},
        revision=child["revision_id"],
        obj=child["object_id"],
    )
    failure(early, 422, "EFFECTIVE_DATE_ORDER")
    workflow = submit(live, "frameworks", child)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    assert candidate["superseded"]["revision_id"] == first["revision_id"]
    approve(live, workflow)
    assert get(live, "frameworks", first["object_id"])["lifecycle_state"] == "Superseded"
    assert get(live, "frameworks", child["object_id"])["lifecycle_state"] == "Approved"
    with live.db() as c:
        rows = c.execute(
            "SELECT baseline_version,framework_revision,supersedes_revision FROM impact.framework_baseline WHERE programme_id=%s ORDER BY baseline_version",
            (programme["object_id"],),
        ).fetchall()
        original = c.execute(
            "SELECT payload FROM impact.object_revision WHERE revision_id=%s", (first["revision_id"],)
        ).fetchone()["payload"]
    assert [r["baseline_version"] for r in rows] == [1, 2]
    assert str(rows[0]["framework_revision"]) == first["revision_id"]
    assert str(rows[1]["supersedes_revision"]) == first["revision_id"]
    # The first baseline keeps its approved language.
    assert (
        next(n for n in original["nodes"] if n["node_id"] == outcome["node_id"])["title"]
        == "Outcome statement"
    )
    view = get(live, "programmes", programme["object_id"] + "/targets-vs-actuals")
    assert view["framework"]["baseline_version"] == 2


def test_hierarchy_structure_is_refused(live, setup):
    programme, indicator, _, _ = setup(False)
    owner = live.fixture["actors"]["author"]["principal_id"]
    items = nodes(owner, indicator["object_id"])
    base = {"programme_id": programme["object_id"], "version_label": "Structure", "relationships": []}
    cycle = [dict(n) for n in items]
    cycle[0]["parent_node_id"] = cycle[1]["node_id"]
    cycle[1]["node_type"] = "IMPACT"
    failure(post(live, "frameworks", {**base, "nodes": cycle}), 422, "CONTAINMENT_CYCLE")
    orphan = [dict(n) for n in items]
    orphan[2]["parent_node_id"] = str(uuid.uuid4())
    failure(post(live, "frameworks", {**base, "nodes": orphan}), 422, "ORPHAN_PARENT")
    inverted = [dict(n) for n in items]
    inverted[1]["node_type"] = "ACTIVITY"
    failure(post(live, "frameworks", {**base, "nodes": inverted}), 422, "LEVEL_ORDER")
    twice = [dict(n) for n in items]
    twice[1]["indicator_ids"] = [indicator["object_id"]]
    failure(post(live, "frameworks", {**base, "nodes": twice}), 422, "INDICATOR_LINKED_TWICE")
    # A seeded indicator of another programme cannot be placed on this programme's framework.
    foreign = [dict(n) for n in items]
    foreign[2]["indicator_ids"] = [live.records["indicator_a"]["object_id"]]
    failure(post(live, "frameworks", {**base, "nodes": foreign}), 422, "INDICATOR_PROGRAMME_MISMATCH")
    # Unknown indicator identifiers are selectors, never proof: not found.
    unknown = [dict(n) for n in items]
    unknown[2]["indicator_ids"] = [str(uuid.uuid4())]
    failure(post(live, "frameworks", {**base, "nodes": unknown}), 404)
    # Theory-of-change relationships and assumption nodes are not implemented.
    link = {
        "relationship_id": str(uuid.uuid4()),
        "from_node_id": items[1]["node_id"],
        "to_node_id": items[0]["node_id"],
        "relationship_type": "CONTRIBUTES_TO",
        "rationale": "Hypothesis",
    }
    failure(post(live, "frameworks", {**base, "nodes": items, "relationships": [link]}), 422)
    assumption = [dict(n) for n in items]
    assumption[3]["node_type"] = "ASSUMPTION"
    failure(post(live, "frameworks", {**base, "nodes": assumption}), 422)
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.framework_current WHERE programme_id=%s", (programme["object_id"],)
        ).fetchone()


def test_unmeasured_output_blocks_submission_until_documented_exception(live, setup):
    programme, indicator, _, _ = setup(False)
    owner = live.fixture["actors"]["author"]["principal_id"]
    items = nodes(owner)  # no indicator placed anywhere
    items[3]["owner_id"] = None
    draft = create(
        live,
        "frameworks",
        {
            "programme_id": programme["object_id"],
            "version_label": "Incomplete",
            "nodes": items,
            "effective_from": "2026-01-01T00:00:00Z",
        },
    )
    report = get(live, "frameworks", draft["object_id"] + "/completeness")
    assert not report["ready"]
    rules = {(i["rule"], i["object_id"]): i for i in report["issues"]}
    output = items[2]["node_id"]
    unmeasured = rules[("UNMEASURED_RESULT", output)]
    assert unmeasured["severity"] == "WARNING" and unmeasured["resolver_id"] == owner
    assert unmeasured["exceptable"] and not unmeasured["excepted"]
    assert rules[("NODE_INCOMPLETE", items[3]["node_id"])]["severity"] == "ERROR"
    assert rules[("ORPHAN_INDICATOR", indicator["object_id"])]["severity"] == "WARNING"
    template = get(live, "workflow-templates")["items"][0]
    denied = action(
        live, "frameworks", draft, "submit", {"workflow_version": template["revision_id"]}, status=422
    )
    assert denied["reason_code"] == "FRAMEWORK_INCOMPLETE"
    # A structural error cannot be excepted; a warning can, with a reason and review date.
    items[3]["owner_id"] = owner
    documented = exceptions(items, "IMPACT", "OUTCOME", "OUTPUT") + [
        {
            "object_id": indicator["object_id"],
            "rule": "ORPHAN_INDICATOR",
            "reason": "Placed after the partner mapping workshop.",
            "review_date": TODAY,
        }
    ]
    expect(
        post(
            live,
            "frameworks",
            {"nodes": items, "exceptions": documented},
            revision=draft["revision_id"],
            obj=draft["object_id"],
        ),
        200,
    )
    draft = get(live, "frameworks", draft["object_id"])
    assert get(live, "frameworks", draft["object_id"] + "/completeness")["ready"]
    stale = [{**documented[0], "object_id": str(uuid.uuid4())}]
    expect(
        post(
            live,
            "frameworks",
            {"exceptions": documented + stale},
            revision=draft["revision_id"],
            obj=draft["object_id"],
        ),
        200,
    )
    draft = get(live, "frameworks", draft["object_id"])
    denied = action(
        live, "frameworks", draft, "submit", {"workflow_version": template["revision_id"]}, status=422
    )
    assert denied["reason_code"] == "FRAMEWORK_INCOMPLETE"
    expect(
        post(
            live,
            "frameworks",
            {"exceptions": documented},
            revision=draft["revision_id"],
            obj=draft["object_id"],
        ),
        200,
    )
    approved_row, _ = approved(live, "frameworks", get(live, "frameworks", draft["object_id"]))
    # The accepted exception remains visible in the approved baseline evidence.
    assert approved_row["lifecycle_state"] == "Approved"
    assert {e["rule"] for e in approved_row["data"]["exceptions"]} == {
        "UNMEASURED_RESULT",
        "ORPHAN_INDICATOR",
    }

    # A child draft cannot delete a node that places indicators in the approved baseline.
    placed = [dict(n) for n in approved_row["data"]["nodes"]]
    placed[2]["indicator_ids"] = [indicator["object_id"]]
    documented = [
        e for e in documented if e["rule"] == "UNMEASURED_RESULT" and e["object_id"] != placed[2]["node_id"]
    ]
    child = create(
        live,
        "frameworks",
        {
            **content(approved_row["data"]),
            "nodes": placed,
            "exceptions": documented,
            "supersedes_revision": approved_row["revision_id"],
            "effective_from": "2026-04-01T00:00:00Z",
        },
    )
    second, _ = approved(live, "frameworks", child)
    grandchild = {
        **content(second["data"]),
        "nodes": [
            {**n, "parent_node_id": placed[1]["node_id"]} if n["node_id"] == placed[3]["node_id"] else n
            for n in second["data"]["nodes"]
            if n["node_id"] != placed[2]["node_id"]
        ],
        "supersedes_revision": second["revision_id"],
        "effective_from": "2026-05-01T00:00:00Z",
    }
    failure(post(live, "frameworks", grandchild), 422, "NODE_REFERENCED")
    # A draft built on a superseded baseline is stale.
    stale_child = {
        **content(approved_row["data"]),
        "supersedes_revision": approved_row["revision_id"],
        "effective_from": "2026-06-01T00:00:00Z",
    }
    failure(post(live, "frameworks", stale_child), 409, "FRAMEWORK_BASELINE_CHANGED")


def test_framework_access_boundaries(live, setup):
    programme, indicator, _, _ = setup(False)
    draft = framework(live, programme, indicator)
    other = live.fixture["tenant_b"] if "tenant_b" in live.fixture else None
    expect(live.request(live.path("frameworks", draft["object_id"]), actor="other_tenant"), 404)
    if other:
        expect(
            live.request(live.path("frameworks", draft["object_id"], tenant=other), actor="other_tenant"), 404
        )
    response = live.request(live.path("frameworks", draft["object_id"]), actor="revoked")
    assert response.status_code in {401, 404}, response.text
    # EXTERNAL may read frameworks but never create or submit them.
    failure(post(live, "frameworks", {"programme_id": programme["object_id"]}, actor="partner"), 403)
    template = get(live, "workflow-templates")["items"][0]
    response = post(
        live,
        "frameworks",
        {"workflow_version": template["revision_id"]},
        actor="partner",
        revision=draft["revision_id"],
        obj=draft["object_id"],
        verb="submit",
    )
    assert response.status_code in {403, 404}, response.text
    expect(live.request(live.path("frameworks"), actor="enumerator"), 403)
    expect(
        live.request(
            live.path("programmes", programme["object_id"]) + "/targets-vs-actuals", actor="other_tenant"
        ),
        404,
    )
    expect(live.request(live.path("frameworks", str(uuid.uuid4())) + "/completeness"), 404)


def test_exact_retry_conflicting_reuse_and_stale_revision(live, setup):
    programme, indicator, _, _ = setup(False)
    operation = str(uuid.uuid4())
    owner = live.fixture["actors"]["author"]["principal_id"]
    items = nodes(owner, indicator["object_id"])
    data = {
        "programme_id": programme["object_id"],
        "version_label": "Retry",
        "nodes": items,
        "exceptions": exceptions(items, "IMPACT", "OUTCOME"),
    }
    first = expect(post(live, "frameworks", data, operation=operation), 201)
    again = expect(post(live, "frameworks", data, operation=operation), 201)
    assert again == first
    changed = failure(post(live, "frameworks", {**data, "version_label": "Other"}, operation=operation), 409)
    assert changed["code"] == "CONFLICT_OPERATION"
    assert db_counts(live, first["object_id"], "create_frameworks")["revisions"] == 1
    row = get(live, "frameworks", first["object_id"])
    expect(
        post(
            live, "frameworks", {"version_label": "Second"}, revision=row["revision_id"], obj=row["object_id"]
        ),
        200,
    )
    stale = failure(
        post(
            live, "frameworks", {"version_label": "Third"}, revision=row["revision_id"], obj=row["object_id"]
        ),
        409,
    )
    assert stale["code"] == "CONFLICT_VERSION"


def test_targets_baselines_milestones_and_provisional_progress(live, setup):
    programme, indicator, plan, period = setup()
    goal = target(live, indicator, period)
    assert goal["data"]["value"] == "40" and "indicator_version" not in goal["data"]
    baseline = target(live, indicator, period, value="10", target_basis="BASELINE")
    milestone = target(
        live,
        indicator,
        period,
        target_kind="MILESTONE",
        direction="MILESTONE",
        value="20",
        milestone_label="Half of villages reporting",
        due_at="2026-08-31T00:00:00Z",
    )
    # A draft can never carry the definition pin; submission sets it.
    failure(
        post(
            live,
            "targets",
            {"indicator_version": indicator["data"]["definition_version"]},
            revision=goal["revision_id"],
            obj=goal["object_id"],
        ),
        422,
    )
    workflow = submit(live, "targets", goal)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    assert candidate["record"]["data"]["indicator_version"] == indicator["data"]["definition_version"]
    own = action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Own"},
        status=403,
    )
    assert own["reason_code"] == "INDEPENDENCE_REQUIRED"
    approve(live, workflow)
    goal = get(live, "targets", goal["object_id"])
    baseline, _ = approved(live, "targets", baseline)
    milestone, _ = approved(live, "targets", milestone)
    assert (
        goal["lifecycle_state"] == baseline["lifecycle_state"] == milestone["lifecycle_state"] == "Approved"
    )
    failure(post(live, "targets", {**goal["data"]} | {"indicator_version": None}), 422)
    duplicate = {k: v for k, v in goal["data"].items() if k != "indicator_version"}
    failure(post(live, "targets", duplicate), 409, "TARGET_ALREADY_APPROVED")

    view = get(live, "programmes", programme["object_id"] + "/targets-vs-actuals")
    row = next(r for r in view["rows"] if r["indicator_id"] == indicator["object_id"])
    assert row["target"]["value"] == "40" and row["baseline"]["value"] == "10"
    assert row["milestones"][0]["milestone_label"] == "Half of villages reporting"
    assert row["actual"]["mode"] == "NONE" and row["progress"]["status"] == "NO_ACTUAL"

    for obligation in plan["data"]["obligations"][:3]:
        source = observation(live, indicator, obligation["source_key"])
        approve(live, submit(live, "observations", source))
    provisional = result(live, indicator, period)
    assert provisional["data"]["value"] == "30"
    row = next(
        r
        for r in get(live, "programmes", programme["object_id"] + "/targets-vs-actuals")["rows"]
        if r["indicator_id"] == indicator["object_id"]
    )
    assert row["actual"]["mode"] == "PROVISIONAL" and row["actual"]["source"] == "CALCULATION"
    assert row["actual"]["result_revision"] == provisional["revision_id"]
    assert row["progress"] == {
        "status": "BELOW_TARGET",
        "attainment_percent": "75.00",
        "deviation": "-10",
        "displayed_deviation": "-10",
        "change_from_baseline": "20",
        "change_from_baseline_percent": "200.00",
        "change_from_baseline_reason": None,
        "reason_code": None,
    }

    # A revised target supersedes the approved one; the original revision is retained.
    revised = target(
        live,
        indicator,
        period,
        value="25",
        target_basis="REVISED",
        supersedes_revision=goal["revision_id"],
        reason="Two partners withdrew from the programme.",
    )
    revised, _ = approved(live, "targets", revised)
    assert get(live, "targets", goal["object_id"])["lifecycle_state"] == "Superseded"
    row = next(
        r
        for r in get(live, "programmes", programme["object_id"] + "/targets-vs-actuals")["rows"]
        if r["indicator_id"] == indicator["object_id"]
    )
    assert row["target"]["target_basis"] == "REVISED" and row["target"]["binding_version"] == 2
    assert row["progress"]["status"] == "ACHIEVED" and row["progress"]["attainment_percent"] == "120.00"
    with live.db() as c:
        chain = c.execute(
            "SELECT binding_version,target_revision,supersedes_revision FROM impact.target_binding WHERE indicator_id=%s AND slot='TARGET' ORDER BY binding_version",
            (indicator["object_id"],),
        ).fetchall()
    assert [str(r["target_revision"]) for r in chain] == [goal["revision_id"], revised["revision_id"]]
    assert str(chain[1]["supersedes_revision"]) == goal["revision_id"]


def test_blank_target_stays_blank_and_decimals_round_trip(live, setup):
    programme, indicator, _, period = setup(False)
    blank = target(live, indicator, period, value_state="MISSING", value=None)
    failure(
        post(
            live,
            "targets",
            {"value_state": "MISSING", "value": "0"},
            revision=blank["revision_id"],
            obj=blank["object_id"],
        ),
        422,
    )
    # A value alone merged into a blank target is refused (merged-record schema), never stored as zero.
    refused = failure(
        post(live, "targets", {"value": "0"}, revision=blank["revision_id"], obj=blank["object_id"]),
        422,
    )
    assert refused["field_errors"][0]["path"] == "value"
    blank, _ = approved(live, "targets", blank)
    assert blank["data"]["value"] is None and blank["data"]["value_state"] == "MISSING"
    with live.db() as c:
        stored = c.execute(
            "SELECT value,value_state FROM impact.target_current WHERE object_id=%s", (blank["object_id"],)
        ).fetchone()
    assert stored["value"] is None and stored["value_state"] == "MISSING"
    row = next(
        r
        for r in get(live, "programmes", programme["object_id"] + "/targets-vs-actuals")["rows"]
        if r["indicator_id"] == indicator["object_id"]
    )
    assert row["target"]["value"] is None and row["target"]["value_state"] == "MISSING"

    for value in ["12345678901234567890123456.123456789012", "0.000000000001", "-7.5"]:
        row = target(live, indicator, period, target_basis="BASELINE", value=value)
        assert get(live, "targets", row["object_id"])["data"]["value"] == value
        with live.db() as c:
            assert c.execute(
                "SELECT value FROM impact.target_current WHERE object_id=%s", (row["object_id"],)
            ).fetchone()["value"] == Decimal(value)
    for bad in ["1e3", "1.0000000000001", "01", " 4"]:
        failure(
            post(
                live,
                "targets",
                {"indicator_id": indicator["object_id"], "value_state": "PRESENT", "value": bad},
            ),
            422,
        )


def test_target_rules_and_calendar(live, setup):
    programme, indicator, _, period = setup(False)
    base = {
        "indicator_id": indicator["object_id"],
        "period_id": period["object_id"],
        "value_state": "PRESENT",
        "target_basis": "ORIGINAL",
    }
    cases = [
        ({"target_kind": "RANGE", "direction": "RANGE", "low": "9", "high": "3"}, "RANGE_ORDER"),
        ({"target_kind": "RANGE", "direction": "RANGE", "value": "5"}, "RANGE_USES_BOUNDS"),
        ({"target_kind": "VALUE", "direction": "RANGE", "value": "5"}, "DIRECTION_KIND_MISMATCH"),
        ({"target_kind": "VALUE", "direction": "HIGHER", "value": "5", "low": "1"}, "BOUNDS_ONLY_FOR_RANGE"),
        (
            {
                "target_kind": "RANGE",
                "direction": "RANGE",
                "low": "1",
                "high": "2",
                "target_basis": "BASELINE",
            },
            "BASELINE_REQUIRES_VALUE",
        ),
        (
            {"target_kind": "VALUE", "direction": "HIGHER", "value": "5", "target_basis": "REVISED"},
            "REVISION_BASIS_MISMATCH",
        ),
        (
            {
                "target_kind": "MILESTONE",
                "direction": "MILESTONE",
                "value": "1",
                "milestone_label": "Launch",
                "due_at": "2027-01-15T00:00:00Z",
            },
            "MILESTONE_OUTSIDE_PERIOD",
        ),
        (
            {"target_kind": "VALUE", "direction": "HIGHER", "value": "5", "milestone_label": "x"},
            "MILESTONE_FIELDS_NOT_ALLOWED",
        ),
    ]
    for data, reason in cases:
        failure(post(live, "targets", {**base, **data}), 422, reason)
    # The seeded programme has no reporting calendar, so no period belongs to its calendar.
    seeded = {
        **base,
        "indicator_id": live.records["indicator_a"]["object_id"],
        "target_kind": "VALUE",
        "direction": "HIGHER",
        "value": "50",
    }
    failure(post(live, "targets", seeded), 422, "PERIOD_NOT_IN_PROGRAMME_CALENDAR")
    # An inclusive range compares against both bounds.
    ranged = create(
        live, "targets", {**base, "target_kind": "RANGE", "direction": "RANGE", "low": "3", "high": "9"}
    )
    template = get(live, "workflow-templates")["items"][0]
    incomplete = create(
        live, "targets", {"indicator_id": indicator["object_id"], "period_id": period["object_id"]}
    )
    denied = action(
        live, "targets", incomplete, "submit", {"workflow_version": template["revision_id"]}, status=422
    )
    assert denied["reason_code"] == "SUBMISSION_INCOMPLETE"
    assert ranged["data"]["low"] == "3"
    expect(live.request(live.path("targets", ranged["object_id"]), actor="other_tenant"), 404)
    failure(
        post(
            live,
            "targets",
            {**base, "target_kind": "VALUE", "direction": "HIGHER", "value": "5"},
            actor="partner",
        ),
        403,
    )


def test_period_close_pins_targets_and_uses_official_result(live, setup):
    programme, indicator, _, period, _, provisional = complete_period(live, setup)
    goal, _ = approved(live, "targets", target(live, indicator, period, value="60"))
    workflow = request_close(live, programme, period)
    approve(live, workflow)
    snapshot = next(
        s
        for s in get(live, "snapshots")["items"]
        if s["data"]["period_id"] == period["object_id"]
        and s["data"].get("programme_id") == programme["object_id"]
    )
    assert snapshot["data"]["target_versions"] == [goal["revision_id"]]
    row = next(
        r
        for r in get(live, "programmes", programme["object_id"] + "/targets-vs-actuals")["rows"]
        if r["indicator_id"] == indicator["object_id"]
    )
    assert row["period_state"] == "Locked"
    assert row["actual"]["mode"] == "OFFICIAL" and row["actual"]["source"] == "PROGRAMME_SNAPSHOT"
    assert row["actual"]["snapshot_id"] == snapshot["object_id"]
    assert row["actual"]["value"] == provisional["data"]["value"] == "50"
    assert row["target"]["revision_id"] == goal["revision_id"]
    assert row["progress"]["attainment_percent"] == "83.33" and row["progress"]["status"] == "BELOW_TARGET"
    # A locked period's targets are frozen: no new or revised target.
    failure(
        post(
            live,
            "targets",
            {
                "indicator_id": indicator["object_id"],
                "period_id": period["object_id"],
                "target_kind": "VALUE",
                "value_state": "PRESENT",
                "value": "45",
                "direction": "HIGHER",
                "target_basis": "REVISED",
                "supersedes_revision": goal["revision_id"],
                "reason": "After lock",
            },
        ),
        409,
        "PERIOD_LOCKED",
    )


def tva(live, programme_id, actor="author", **params):
    query = "&".join(k + "=" + str(v) for k, v in params.items())
    return get(
        live, "programmes", programme_id + "/targets-vs-actuals" + ("?" + query if query else ""), actor=actor
    )


def test_seeded_fixture_official_is_never_attributed(live):
    """The seeded OFFICIAL 46.36 sits in a fixture snapshot bound to no programme: it is not this
    programme's snapshot, so the seeded indicator's row reads no official actual."""
    programme = live.records["programme_a"]["object_id"]
    view = tva(live, programme, period_id=live.records["period"]["object_id"])
    assert view["framework"] is None and view["next_cursor"] is None
    row = next(r for r in view["rows"] if r["indicator_id"] == live.records["indicator_a"]["object_id"])
    assert row["actual"]["mode"] != "OFFICIAL" and row["actual"]["source"] in {"NONE", "CALCULATION"}
    if row["actual"]["mode"] == "NONE":
        assert row["actual"]["value"] is None and row["progress"]["status"] == "NO_ACTUAL"
    assert all(r["actual"]["value"] != "46.363636363636" for r in view["rows"])


def programme_with_calendar(live, title):
    return create(
        live,
        "programmes",
        {
            "code": "PRB",
            "title": title + " " + str(uuid.uuid4())[:8],
            "programme_type": "Health",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2027-01-01T00:00:00Z",
            "reporting_calendar_id": get(live, "reporting-calendars")["items"][0]["object_id"],
            "geography_id": get(live, "geographies")["items"][0]["object_id"],
        },
    )


def test_shared_definition_does_not_borrow_another_programmes_official(live):
    """Reviewer probe (H1): a new programme whose instance pins the seeded definition's current
    head, with an approved target of 40 in the open period and no data, has no actual."""
    programme = programme_with_calendar(live, "Probe")
    definition = get(live, "indicator-definitions", live.records["definition"]["object_id"])
    assert definition["lifecycle_state"] == "Approved"
    instance = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": definition["revision_id"],
            "local_applicability": "Probe households",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    period = get(live, "periods", live.records["period"]["object_id"])
    approved(live, "targets", target(live, instance, period, value="40"))
    row = next(
        r for r in tva(live, programme["object_id"])["rows"] if r["indicator_id"] == instance["object_id"]
    )
    assert row["target"]["value"] == "40"
    assert row["actual"] == {
        "mode": "NONE",
        "source": "NONE",
        "value_state": "MISSING",
        "value": None,
        "displayed_value": None,
        "result_id": None,
        "result_revision": None,
        "snapshot_id": None,
        "stale": False,
    }
    assert row["progress"]["status"] == "NO_ACTUAL" and row["progress"]["attainment_percent"] is None


def expire_grant(live, actor, capability):
    """Take one capability from a fixture actor for the duration of a check (restored after)."""
    principal = live.fixture["actors"][actor]["principal_id"]
    with live.db() as c:
        rows = c.execute(
            "UPDATE impact.grant_current SET expires_at=now()-interval '1 second' WHERE subject_id=%s AND capability=%s RETURNING object_id,expires_at",
            (principal, capability),
        ).fetchall()
    assert rows, (actor, capability)
    return principal, capability


def restore_grant(live, principal, capability):
    with live.db() as c:
        c.execute(
            "UPDATE impact.grant_current g SET expires_at=(v.payload->>'expires_at')::timestamptz FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE g.subject_id=%s AND g.capability=%s AND r.tenant_id=g.tenant_id AND r.object_id=g.object_id",
            (principal, capability),
        )


def test_actual_withheld_without_result_access(live, setup):
    programme, indicator, _, period = setup(False)
    approved(live, "targets", target(live, indicator, period))
    held = expire_grant(live, "partner", "calculated-results.read")
    try:
        row = next(
            r
            for r in tva(live, programme["object_id"], actor="partner")["rows"]
            if r["indicator_id"] == indicator["object_id"]
        )
    finally:
        restore_grant(live, *held)
    assert row["actual"]["mode"] == "NONE" and row["actual"]["value"] is None
    assert row["progress"]["reason_code"] == "RESULT_ACCESS_REQUIRED"


def test_targets_vs_actuals_pages_by_indicator(live, setup):
    """M1: more than 500 potential rows arrive in signed pages of indicators; no total is given."""
    programme, indicator, _, period = setup(False)
    author = live.fixture["actors"]["author"]["principal_id"]
    tenant = live.fixture["tenant_a"]
    payload = {
        "programme_id": programme["object_id"],
        "definition_version": indicator["data"]["definition_version"],
        "local_applicability": "Bulk village",
    }
    with live.db() as c:
        c.execute(
            "CREATE TEMP TABLE bulk AS SELECT gen_random_uuid() AS object_id,gen_random_uuid() AS revision_id FROM generate_series(1,501)"
        )
        c.execute(
            "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,lifecycle_state,classification,owner_id,created_at,created_by,updated_at) SELECT %s,object_id,'IndicatorInstance',revision_id,'Draft','INTERNAL',%s,now(),%s,now() FROM bulk",
            (tenant, author, author),
        )
        c.execute(
            "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,schema_version,payload,payload_sha256,author_id,created_at) SELECT %s,object_id,revision_id,'IndicatorInstance','1.2',%s,sha256(convert_to(%s::text,'UTF8')),%s,now() FROM bulk",
            (tenant, Jsonb(payload), json.dumps(payload), author),
        )
        c.execute(
            "INSERT INTO impact.indicator_instance_current(tenant_id,object_id,revision_id,programme_id,definition_version,local_applicability) SELECT %s,object_id,revision_id,%s,%s,'Bulk village' FROM bulk",
            (tenant, programme["object_id"], indicator["data"]["definition_version"]),
        )
    seen, cursor, pages = [], None, 0
    while True:
        params = {"period_id": period["object_id"], "limit": 100}
        if cursor:
            params["cursor"] = quote(cursor, safe="")
        page = tva(live, programme["object_id"], **params)
        pages += 1
        assert len(page["rows"]) <= 100 and "total_rows" not in page
        seen += [r["indicator_id"] for r in page["rows"]]
        cursor = page["next_cursor"]
        if not cursor:
            break
    assert pages == 6 and len(seen) == len(set(seen)) == 502 and seen == sorted(seen)
    assert all(r["actual"]["mode"] == "NONE" for r in page["rows"])
    first = tva(live, programme["object_id"], period_id=period["object_id"], limit=100)
    token = quote(first["next_cursor"], safe="")
    other = setup(False)[0]
    for path in [
        programme["object_id"] + "/targets-vs-actuals?cursor=" + token,  # bound to the period filter
        other["object_id"] + "/targets-vs-actuals?period_id=" + period["object_id"] + "&cursor=" + token,
        programme["object_id"] + "/targets-vs-actuals?period_id=" + period["object_id"] + "&cursor=x" + token,
    ]:
        assert expect(live.request(live.path("programmes", path)), 400)["code"] == "INVALID_CURSOR"
    response = live.request(
        live.path("programmes", programme["object_id"])
        + "/targets-vs-actuals?period_id="
        + period["object_id"]
        + "&cursor="
        + token,
        actor="reviewer",
    )
    assert response.status_code == 400, response.text
    expect(
        live.request(live.path("programmes", programme["object_id"]) + "/targets-vs-actuals?limit=101"), 422
    )


def test_approved_baseline_is_corrected_by_a_superseding_baseline(live, setup):
    """M2: an approved BASELINE is corrected by a BASELINE that supersedes it, with a reason."""
    _, indicator, _, period = setup(False)
    first, _ = approved(live, "targets", target(live, indicator, period, value="10", target_basis="BASELINE"))
    correction = {
        "target_basis": "BASELINE",
        "value": "12",
        "supersedes_revision": first["revision_id"],
    }
    unreasoned = target(live, indicator, period, **correction)
    template = get(live, "workflow-templates")["items"][0]
    denied = action(
        live, "targets", unreasoned, "submit", {"workflow_version": template["revision_id"]}, status=422
    )
    assert denied["reason_code"] == "REVISION_REASON_REQUIRED"
    second_child = target(live, indicator, period, **correction, reason="Late census return.")
    corrected, _ = approved(
        live, "targets", target(live, indicator, period, **correction, reason="Register re-count.")
    )
    assert get(live, "targets", first["object_id"])["lifecycle_state"] == "Superseded"
    denied = action(
        live, "targets", second_child, "submit", {"workflow_version": template["revision_id"]}, status=409
    )
    assert denied["reason_code"] == "TARGET_CHANGED"
    # The chain continues from the correction; ORIGINAL can never supersede.
    failure(
        post(
            live,
            "targets",
            {
                "indicator_id": indicator["object_id"],
                "period_id": period["object_id"],
                "target_kind": "VALUE",
                "value_state": "PRESENT",
                "value": "13",
                "direction": "HIGHER",
                "target_basis": "ORIGINAL",
                "supersedes_revision": corrected["revision_id"],
            },
        ),
        422,
        "REVISION_BASIS_MISMATCH",
    )
    with live.db() as c:
        chain = c.execute(
            "SELECT binding_version,target_revision,supersedes_revision FROM impact.target_binding WHERE indicator_id=%s AND slot='BASELINE' ORDER BY binding_version",
            (indicator["object_id"],),
        ).fetchall()
    assert [str(r["target_revision"]) for r in chain] == [first["revision_id"], corrected["revision_id"]]
    assert str(chain[1]["supersedes_revision"]) == first["revision_id"]


def test_progress_overflow_is_a_row_reason_not_a_failed_read(live, setup):
    """L1: an attainment or deviation outside NUMERIC(38,12) empties that row's arithmetic only."""
    programme, indicator, plan, period = setup()
    source = create(
        live,
        "observations",
        {
            "source_namespace": "MANUAL",
            "source_key": plan["data"]["obligations"][0]["source_key"],
            "indicator_id": indicator["object_id"],
            "event_at": "2026-08-15T12:00:00Z",
            "captured_at": "2026-08-15T13:00:00Z",
            "capture_zone": "UTC",
            "value_state": "PRESENT",
            "value": "99999999999999999999999999",
            "source_version": "1",
            "dimension_values": {},
        },
    )
    approve(live, submit(live, "observations", source))
    assert result(live, indicator, period)["data"]["value"] == "99999999999999999999999999"
    approved(live, "targets", target(live, indicator, period, value="-99999999999999999999999999"))
    approved(
        live,
        "targets",
        target(live, indicator, period, value="-99999999999999999999999999", target_basis="BASELINE"),
    )
    row = next(
        r for r in tva(live, programme["object_id"])["rows"] if r["indicator_id"] == indicator["object_id"]
    )
    assert row["actual"]["mode"] == "PROVISIONAL"
    assert (
        row["progress"]["status"] == "NOT_COMPUTABLE"
        and row["progress"]["reason_code"] == "ARITHMETIC_OVERFLOW"
    )
    assert row["progress"]["deviation"] is None


def test_blank_state_row_cannot_carry_a_value(live):
    """L2: the projection refuses a value, low or high on a row without a PRESENT state, including
    a row with no state at all."""
    tenant = live.fixture["tenant_a"]
    author = live.fixture["actors"]["author"]["principal_id"]
    for state in [None, "MISSING"]:
        obj, rev = str(uuid.uuid4()), str(uuid.uuid4())
        with pytest.raises(psycopg.errors.CheckViolation):
            with live.db() as c:
                c.execute(
                    "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,lifecycle_state,classification,owner_id,created_at,created_by,updated_at) VALUES(%s,%s,'Target',%s,'Draft','INTERNAL',%s,now(),%s,now())",
                    (tenant, obj, rev, author, author),
                )
                c.execute(
                    "INSERT INTO impact.target_current(tenant_id,object_id,revision_id,value_state,value) VALUES(%s,%s,%s,%s,5)",
                    (tenant, obj, rev, state),
                )


def test_close_pins_governing_framework_revision(live, setup):
    """L3: a close pins the framework baseline that governs the period into the snapshot policy
    context, and locked rows are placed by that pinned revision."""
    programme, indicator, _, period, _, _ = complete_period(live, setup)
    baseline, _ = approved(live, "frameworks", framework(live, programme, indicator))
    approve(live, request_close(live, programme, period))
    snapshot = next(
        s
        for s in get(live, "snapshots")["items"]
        if s["data"]["period_id"] == period["object_id"]
        and s["data"].get("programme_id") == programme["object_id"]
    )
    assert snapshot["data"]["policy_context"]["framework_revision"] == baseline["revision_id"]
    row = next(
        r for r in tva(live, programme["object_id"])["rows"] if r["indicator_id"] == indicator["object_id"]
    )
    output = next(n for n in baseline["data"]["nodes"] if n["node_type"] == "OUTPUT")
    assert row["framework_revision"] == baseline["revision_id"] and row["node_ids"] == [output["node_id"]]
    # A later revision effective after the locked period does not re-place it.
    child = create(
        live,
        "frameworks",
        {
            **content(baseline["data"]),
            "supersedes_revision": baseline["revision_id"],
            "effective_from": "2026-12-01T00:00:00Z",
        },
    )
    approved(live, "frameworks", child)
    row = next(
        r for r in tva(live, programme["object_id"])["rows"] if r["indicator_id"] == indicator["object_id"]
    )
    assert row["framework_revision"] == baseline["revision_id"]


def test_exception_authorship_and_review_date(live, setup):
    """L4: who recorded an exception is set by the server, its review date cannot lie in the past,
    and the independent approver (the named authority) is recorded against the baseline."""
    programme, indicator, _, _ = setup(False)
    draft = framework(live, programme, indicator)
    author = live.fixture["actors"]["author"]["principal_id"]
    assert {e["recorded_by"] for e in draft["data"]["exceptions"]} == {author}
    assert all(e["recorded_at"] for e in draft["data"]["exceptions"])
    forged = [
        {**e, "recorded_by": live.fixture["actors"]["reviewer"]["principal_id"]}
        for e in draft["data"]["exceptions"]
    ]
    failure(
        post(
            live, "frameworks", {"exceptions": forged}, revision=draft["revision_id"], obj=draft["object_id"]
        ),
        422,
    )
    past = [{**e, "review_date": "2020-01-01"} for e in content(draft["data"])["exceptions"]]
    failure(
        post(live, "frameworks", {"exceptions": past}, revision=draft["revision_id"], obj=draft["object_id"]),
        422,
        "EXCEPTION_REVIEW_DATE_PASSED",
    )
    # An unrelated edit keeps each unchanged exception's original authorship.
    expect(
        post(
            live,
            "frameworks",
            {"version_label": "Relabelled"},
            revision=draft["revision_id"],
            obj=draft["object_id"],
        ),
        200,
    )
    kept = get(live, "frameworks", draft["object_id"])
    assert kept["data"]["exceptions"] == draft["data"]["exceptions"]
    row, workflow = approved(live, "frameworks", kept)
    with live.db() as c:
        register = c.execute(
            "SELECT approved_by FROM impact.framework_baseline WHERE framework_revision=%s",
            (row["revision_id"],),
        ).fetchone()
    assert str(register["approved_by"]) == live.fixture["actors"]["reviewer"]["principal_id"] != author


def test_second_framework_child_is_refused_after_the_first_is_approved(live, setup):
    programme, indicator, _, _ = setup(False)
    baseline, _ = approved(live, "frameworks", framework(live, programme, indicator))
    children = [
        create(
            live,
            "frameworks",
            {
                **content(baseline["data"]),
                "version_label": label,
                "supersedes_revision": baseline["revision_id"],
                "effective_from": "2026-07-01T00:00:00Z",
            },
        )
        for label in ["Child A", "Child B"]
    ]
    approved(live, "frameworks", children[0])
    template = get(live, "workflow-templates")["items"][0]
    denied = action(
        live, "frameworks", children[1], "submit", {"workflow_version": template["revision_id"]}, status=409
    )
    assert denied["reason_code"] == "FRAMEWORK_BASELINE_CHANGED"


def test_reviewer_who_edits_a_draft_becomes_an_author(live, setup):
    programme, indicator, _, period = setup(False)
    for route, row, change in [
        ("frameworks", framework(live, programme, indicator), {"version_label": "Reviewer wording"}),
        ("targets", target(live, indicator, period), {"value": "41"}),
    ]:
        expect(
            post(live, route, change, actor="reviewer", revision=row["revision_id"], obj=row["object_id"]),
            200,
        )
        workflow = submit(live, route, get(live, route, row["object_id"]))
        denied = action(
            live,
            "workflows",
            workflow,
            "approve",
            {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Own edit"},
            actor="reviewer",
            status=403,
        )
        assert denied["reason_code"] == "INDEPENDENCE_REQUIRED", route


def test_candidate_view_degrades_without_indicator_access(live, setup):
    """L7: a reviewer who cannot read indicator instances still sees the framework candidate and
    its completeness; placements are reported by identifier only."""
    programme, indicator, _, _ = setup(False)
    workflow = submit(live, "frameworks", framework(live, programme, indicator))
    held = expire_grant(live, "reviewer", "indicator-instances.read")
    try:
        candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    finally:
        restore_grant(live, *held)
    assert candidate["kind"] == "Framework"
    output = next(n for n in candidate["record"]["data"]["nodes"] if n["node_type"] == "OUTPUT")
    assert output["indicator_ids"] == [indicator["object_id"]]
    assert candidate["completeness"]["ready"]


@pytest.mark.parametrize("route", ["frameworks", "targets"])
def test_listing_is_permission_filtered(live, route):
    page = get(live, route)
    assert set(page) == {"items", "next_cursor", "scope_label"}
    expect(live.request(live.path(route), actor="enumerator"), 403)


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="native PostgreSQL only: PGlite serves one superuser session and has no login-role "
    "topology to test (run scripts/run.py test --native)",
)
def test_native_planning_registers_are_fenced_and_insert_only(connect, live, setup):
    """0019 grants SELECT and INSERT (no UPDATE or DELETE) on framework_baseline and target_binding
    to impact_app only, and forces the tenant fence on both."""
    programme, indicator, _, period = setup(False)
    goal, _ = approved(live, "targets", target(live, indicator, period))
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    c = connect("APP")
    for table in ["framework_baseline", "target_binding"]:
        assert query(c, "SELECT count(*) FROM impact." + table, role="impact_app") == [(0,)], table
        for statement in ["UPDATE impact." + table + " SET approved_at=now()", "DELETE FROM impact." + table]:
            assert "permission denied" in denied(c, statement, role="impact_app", tenant=tenant_a)
    assert query(
        c,
        "SELECT count(*) FROM impact.target_binding WHERE target_revision=%s",
        (goal["revision_id"],),
        role="impact_app",
        tenant=tenant_a,
    ) == [(1,)]
    assert query(
        c,
        "SELECT count(*) FROM impact.target_binding WHERE target_revision=%s",
        (goal["revision_id"],),
        role="impact_app",
        tenant=tenant_b,
    ) == [(0,)]
    message = denied(
        c,
        "INSERT INTO impact.target_binding VALUES(%s,%s,%s,'TARGET',1,%s,%s,NULL,%s,%s,now())",
        (
            tenant_b,
            indicator["object_id"],
            period["object_id"],
            goal["object_id"],
            goal["revision_id"],
            str(uuid.uuid4()),
            live.fixture["actors"]["author"]["principal_id"],
        ),
        role="impact_app",
        tenant=tenant_a,
    )
    assert "row-level security" in message
    for login, role in [("PLATFORM", "impact_platform"), ("IDENTITY", "impact_identity")]:
        other = connect(login)
        for table in ["framework_baseline", "target_binding"]:
            assert "permission denied" in denied(
                other, "SELECT count(*) FROM impact." + table, role=role, tenant=tenant_a
            )
