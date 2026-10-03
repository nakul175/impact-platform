"""Qualification of the programme dashboard and the indicator series (v0.24).

Values are built end to end through the existing review, calculation and period-close flow; the
dashboard is a read model only. Golden pooled ratios: 50/100 + 1/10 -> 51/110 = 46.36 and, with
an approved 8/10, 59/120 = 49.17 (display rounded once from the stored 12-place value).
"""
# ruff: noqa: F811

import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from impact_api.contracts import validate
from impact_api.dashboards import STALE_RULE, summarize, value_block
from impact_api.measurement import coverage
from test_calculation_methods import observation_data
from test_live_application import expect
from test_measurement import action, approve, create, get, submit
from test_measurement_unit import definition
from test_period_governance import request_close

RATIO = dict(
    measurement_type="PERCENTAGE",
    combination_rule="POOLED_RATIO",
    unit="percent",
    numerator_meaning="Households with safe water",
    denominator_meaning="Households visited",
    display_decimals=2,
)


# ------------------------------------------------------------------------------------- pure rules


def test_coverage_with_no_required_obligation_is_not_applicable():
    """Zero expected is not applicable: no percentage, never 100 % and never 0 %."""
    plan = {
        "head_revision": str(uuid.uuid4()),
        "payload": {
            "obligations": [
                {
                    "label": "Excepted partner",
                    "source_namespace": "MANUAL",
                    "source_key": "p1",
                    "due_at": "2026-09-01T00:00:00Z",
                    "eligibility": "EXCEPTED",
                }
            ]
        },
    }
    measured, _ = coverage(plan, [], definition(), datetime(2026, 9, 29, tzinfo=timezone.utc))
    block = summarize(measured, "COLLECTION_PLAN")
    assert block["applicability"] == "NOT_APPLICABLE" and block["approval_percent"] is None
    assert block["required_count"] == 0 and block["expected_count"] == 1 and not block["complete"]
    none = summarize(None, "COLLECTION_PLAN")
    assert (none["applicability"], none["expected_count"], none["approval_percent"]) == (
        "NOT_APPLICABLE",
        0,
        None,
    )
    withheld = summarize(None, "COLLECTION_PLAN", "SOURCE_ACCESS_REQUIRED")
    assert withheld["applicability"] == "UNAVAILABLE" and withheld["expected_count"] is None


def test_value_block_displays_once_from_stored_value_and_never_zero_for_blank():
    row = {
        "result_id": str(uuid.uuid4()),
        "result_revision": str(uuid.uuid4()),
        "payload": {
            "mode": "OFFICIAL",
            "value_state": "PRESENT",
            "value": "46.363636363636",
            # A stale or forged display in the payload is never reused: the display is derived.
            "displayed_value": "46.37",
            "numerator": "51",
            "denominator": "110",
            "disaggregation": [
                {"category": "F", "value_state": "PRESENT", "value": "0.125", "contributor_count": 1},
                {"category": "M", "value_state": "UNDEFINED", "value": None, "contributor_count": 0},
            ],
        },
    }
    block = value_block(row, 2)
    assert (block["value"], block["displayed_value"]) == ("46.363636363636", "46.36")
    assert [(e["category"], e["displayed_value"]) for e in block["disaggregation"]] == [
        ("F", "0.13"),
        ("M", None),
    ]
    undefined = value_block(
        {**row, "payload": {"value_state": "UNDEFINED", "value": None, "reason_code": "ZERO_DENOMINATOR"}}, 2
    )
    assert undefined["value"] is None and undefined["displayed_value"] is None
    assert undefined["value_state"] == "UNDEFINED" and undefined["reason_code"] == "ZERO_DENOMINATOR"


# ------------------------------------------------------------------------------------------- live


def measure(live, keys=3, **changes):
    """An active programme with one approved definition, one instance and an approved plan of
    `keys` obligations on the fixture period."""
    programme = create(
        live,
        "programmes",
        {
            "code": "DSH",
            "title": "Dashboard " + str(uuid.uuid4())[:8],
            "programme_type": "Health",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2027-01-01T00:00:00Z",
            "reporting_calendar_id": get(live, "reporting-calendars")["items"][0]["object_id"],
            "geography_id": get(live, "geographies")["items"][0]["object_id"],
        },
    )
    d = create(live, "indicator-definitions", definition(**{**RATIO, **changes}))
    approve(live, submit(live, "indicator-definitions", d))
    d = get(live, "indicator-definitions", d["object_id"])
    indicator = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": d["revision_id"],
            "local_applicability": "Dashboard households",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    period = get(live, "periods", live.records["period"]["object_id"])
    sources = [str(uuid.uuid4()) for _ in range(keys)]
    plan = create(
        live,
        "collection-plans",
        {
            "title": "Dashboard collection",
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "obligations": [
                {
                    "label": f"Site {i + 1}",
                    "source_namespace": "MANUAL",
                    "source_key": k,
                    "due_at": "2026-09-01T00:00:00Z",
                }
                for i, k in enumerate(sources)
            ],
        },
    )
    approve(live, submit(live, "collection-plans", plan))
    action(live, "indicator-instances", indicator, "activate")
    indicator = get(live, "indicator-instances", indicator["object_id"])
    action(live, "programmes", programme, "ready")
    action(live, "programmes", get(live, "programmes", programme["object_id"]), "activate")
    return programme, indicator, period, sources


def ratio_source(live, indicator, key, n, d):
    row = create(
        live,
        "observations",
        observation_data(indicator, key, "0", {}) | {"numerator": n, "denominator": d},
    )
    approve(live, submit(live, "observations", row))
    return get(live, "observations", row["object_id"])


def calculate(live, indicator, period):
    receipt = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    return get(live, "calculated-results", receipt["object_id"])


def close(live, programme, period):
    workflow = request_close(live, programme, period)
    approve(live, workflow)


def dashboard(live, programme_id, period_id, actor="author", **params):
    query = "&".join(["period_id=" + period_id] + [k + "=" + str(v) for k, v in params.items()])
    body = get(live, "programmes", programme_id + "/dashboard?" + query, actor=actor)
    validate("ProgrammeDashboard", body)
    return body


def card(live, programme, indicator, period, actor="author"):
    body = dashboard(live, programme["object_id"], period["object_id"], actor=actor)
    assert body["stale_rule"] == STALE_RULE
    return body, next(c for c in body["indicators"] if c["indicator_id"] == indicator["object_id"])


def series(live, indicator, actor="author", **params):
    query = "&".join(k + "=" + str(v) for k, v in params.items())
    body = get(
        live,
        "indicator-instances",
        indicator["object_id"] + "/dashboard-series" + ("?" + query if query else ""),
        actor=actor,
    )
    validate("IndicatorDashboardSeries", body)
    return body


def target(live, indicator, period, value):
    row = create(
        live,
        "targets",
        {
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "target_kind": "VALUE",
            "value_state": "PRESENT",
            "value": value,
            "direction": "HIGHER",
            "target_basis": "ORIGINAL",
        },
    )
    approve(live, submit(live, "targets", row))
    return get(live, "targets", row["object_id"])


def test_official_pooled_ratio_from_the_programme_snapshot(live):
    """51/110 closed through the existing flow: OFFICIAL 46.36 from this programme's snapshot, with
    the pinned target, coverage from the close's obligation snapshot and a fresh flag."""
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "50", "100")
    ratio_source(live, indicator, keys[1], "1", "10")
    provisional = calculate(live, indicator, period)
    assert provisional["data"]["value"] == "46.363636363636"
    goal = target(live, indicator, period, "50")
    close(live, programme, period)

    body, row = card(live, programme, indicator, period)
    assert body["period"]["period_state"] == "Locked" and body["snapshot"]["snapshot_version"] == 1
    assert row["provisional"] is None
    official = row["official"]
    assert official["mode"] == "OFFICIAL"
    assert (official["value"], official["displayed_value"]) == ("46.363636363636", "46.36")
    assert (official["numerator"], official["denominator"]) == ("51", "110")
    assert row["unit"] == "percent" and row["display_decimals"] == 2
    assert row["target"]["revision_id"] == goal["revision_id"] and row["target"]["displayed_value"] == "50.00"
    assert row["status"]["compared_with"] == "OFFICIAL" and row["status"]["status"] == "BELOW_TARGET"
    assert row["status"]["attainment_percent"] == "92.73" and row["status"]["deviation"] == "-3.636363636364"
    assert row["coverage"]["source"] == "CLOSE_SNAPSHOT"
    assert [row["coverage"][k] for k in ["expected_count", "approved_count", "missing_count"]] == [2, 2, 0]
    assert (
        row["coverage"]["approval_percent"] == "100.00" and row["coverage"]["applicability"] == "APPLICABLE"
    )
    fresh = row["freshness"]
    assert fresh["stale"] is False and fresh["stale_reasons"] == [] and fresh["source_check"] == "CHECKED"
    assert fresh["snapshot_id"] == body["snapshot"]["snapshot_id"] and fresh["locked_at"]
    assert fresh["official_calculated_at"] == provisional["data"]["freshness"]["calculated_at"]

    points = series(live, indicator)["points"]
    assert [(p["period_id"], p["official"]["displayed_value"], p["snapshot_version"]) for p in points] == [
        (period["object_id"], "46.36", 1)
    ]
    assert points[0]["provisional"] is None and "coverage" not in points[0]


def test_provisional_to_official_and_freshness_transitions(live):
    """59/120: PROVISIONAL 46.36 -> sources change (stale) -> PROVISIONAL 49.17 (fresh) -> close
    OFFICIAL 49.17 -> restatement changes a source (official stale) -> a newer provisional stays
    separate from the official value and marks it stale."""
    programme, indicator, period, keys = measure(live, keys=3)
    rows = [
        ratio_source(live, indicator, keys[0], "50", "100"),
        ratio_source(live, indicator, keys[1], "1", "10"),
    ]
    calculate(live, indicator, period)
    body, row = card(live, programme, indicator, period)
    assert body["snapshot"] is None and body["period"]["period_state"] == "Open"
    assert row["official"] is None and row["provisional"]["mode"] == "PROVISIONAL"
    assert row["provisional"]["displayed_value"] == "46.36"
    assert row["status"] is None  # no target, no status
    cover = row["coverage"]
    assert cover["source"] == "COLLECTION_PLAN"
    assert [cover[k] for k in ["expected_count", "required_count", "approved_count", "missing_count"]] == [
        3,
        3,
        2,
        1,
    ]
    assert cover["approval_percent"] == "66.67" and not cover["complete"]
    assert row["freshness"]["stale"] is False and row["freshness"]["stale_reasons"] == []

    rows.append(ratio_source(live, indicator, keys[2], "8", "10"))
    _, row = card(live, programme, indicator, period)
    assert row["freshness"]["stale"] is True
    # The approval also records a durable invalidation of the calculation (pending recalculation).
    assert row["freshness"]["stale_reasons"] == [
        "RECALCULATION_PENDING",
        "SOURCES_CHANGED_SINCE_CALCULATION",
    ]
    assert row["provisional"]["displayed_value"] == "46.36"  # the stale value is still labelled, not replaced
    assert row["coverage"]["approved_count"] == 3 and row["coverage"]["approval_percent"] == "100.00"

    calculate(live, indicator, period)
    _, row = card(live, programme, indicator, period)
    assert (row["provisional"]["value"], row["provisional"]["displayed_value"]) == (
        "49.166666666667",
        "49.17",
    )
    assert row["freshness"]["stale"] is False

    close(live, programme, period)
    body, row = card(live, programme, indicator, period)
    assert row["provisional"] is None and row["official"]["displayed_value"] == "49.17"
    assert (row["official"]["numerator"], row["official"]["denominator"]) == ("59", "120")
    assert row["freshness"]["stale"] is False and row["coverage"]["source"] == "CLOSE_SNAPSHOT"

    # A restatement window opens and an approved correction changes one source after the lock.
    template = get(live, "workflow-templates")["items"][0]
    receipt = action(
        live,
        "periods",
        get(live, "periods", period["object_id"]),
        "restate",
        {
            "workflow_version": template["revision_id"],
            "programme_id": programme["object_id"],
            "reason": "Correct a verified transcription error.",
            "source_ids": [rows[0]["object_id"]],
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        },
    )
    approve(live, get(live, "workflows", receipt["object_id"]))
    proposal = create(
        live,
        "measurement-changes",
        {
            "target_kind": "Observation",
            "target_id": rows[0]["object_id"],
            "target_revision": rows[0]["revision_id"],
            "reason": "Verified transcription correction.",
            "proposed_data": {"numerator": "60", "source_version": "2"},
        },
    )
    approve(live, submit(live, "measurement-changes", proposal))
    body, row = card(live, programme, indicator, period)
    assert body["period"]["period_state"] == "RestatementOpen"
    assert row["official"]["displayed_value"] == "49.17" and row["provisional"] is None
    assert row["freshness"]["stale"] is True
    assert row["freshness"]["stale_reasons"] == ["SOURCES_CHANGED_SINCE_CLOSE"]

    calculate(live, indicator, period)
    _, row = card(live, programme, indicator, period)
    assert row["official"]["displayed_value"] == "49.17"
    assert row["provisional"]["mode"] == "PROVISIONAL" and row["provisional"]["displayed_value"] == "57.50"
    assert row["freshness"]["stale"] is True
    assert row["freshness"]["stale_reasons"] == [
        "PROVISIONAL_NEWER_THAN_OFFICIAL",
        "SOURCES_CHANGED_SINCE_CLOSE",
    ]
    point = series(live, indicator)["points"][0]
    assert (
        point["official"]["displayed_value"] == "49.17" and point["provisional"]["displayed_value"] == "57.50"
    )
    assert point["period_state"] == "RestatementOpen"


def test_undefined_result_is_never_zero(live):
    programme, indicator, period, keys = measure(live, keys=1)
    ratio_source(live, indicator, keys[0], "0", "0")
    target(live, indicator, period, "40")
    calculate(live, indicator, period)
    _, row = card(live, programme, indicator, period)
    value = row["provisional"]
    assert value["value_state"] == "UNDEFINED" and value["reason_code"] == "ZERO_DENOMINATOR"
    assert value["value"] is None and value["displayed_value"] is None
    assert row["status"]["status"] == "NO_ACTUAL" and row["status"]["attainment_percent"] is None
    assert row["status"]["deviation"] is None


def test_without_a_plan_coverage_is_not_applicable_and_blank_stays_blank(live):
    programme, indicator, period, _ = measure(live, keys=1)
    extra = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": indicator["data"]["definition_version"],
            "local_applicability": "Unplanned sites",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    _, row = card(live, programme, extra, period)
    assert row["official"] is None and row["provisional"] is None and row["status"] is None
    cover = row["coverage"]
    assert cover["applicability"] == "NOT_APPLICABLE" and cover["approval_percent"] is None
    assert cover["expected_count"] == 0 and cover["reason_code"] == "NO_COLLECTION_PLAN"
    assert row["freshness"]["stale"] is None and row["freshness"]["source_check"] == "NO_VALUE"


def test_seeded_fixture_official_is_never_surfaced(live):
    """The seeded OFFICIAL 46.36 sits in a fixture snapshot bound to no programme."""
    body = dashboard(live, live.records["programme_a"]["object_id"], live.records["period"]["object_id"])
    assert body["snapshot"] is None
    assert all(c["official"] is None for c in body["indicators"])
    assert "46.363636363636" not in json.dumps(body)
    points = series(live, {"object_id": live.records["indicator_a"]["object_id"]})["points"]
    assert all(p["official"] is None for p in points)


def test_access_boundaries(live):
    programme, indicator, period, _ = measure(live, keys=1)
    pid, period_id = programme["object_id"], period["object_id"]
    path = live.path("programmes", pid) + "/dashboard?period_id=" + period_id
    series_path = live.path("indicator-instances", indicator["object_id"]) + "/dashboard-series"
    for p in [path, series_path]:
        assert expect(live.request(p, actor="other_tenant"), 404)["code"] == "RESOURCE_UNAVAILABLE"
        response = live.request(p, actor="revoked")
        assert response.status_code in {401, 404}, response.text
        # ENUMERATOR holds no dashboards.read at all.
        assert expect(live.request(p, actor="enumerator"), 403)["code"] == "POLICY_DENIED"
    other = live.fixture["tenant_b"]
    expect(
        live.request(
            live.path("programmes", pid, tenant=other) + "/dashboard?period_id=" + period_id,
            actor="other_tenant",
        ),
        404,
    )
    expect(
        live.request(live.path("programmes", str(uuid.uuid4())) + "/dashboard?period_id=" + period_id), 404
    )
    expect(live.request(live.path("programmes", pid) + "/dashboard?period_id=" + str(uuid.uuid4())), 404)
    expect(live.request(live.path("indicator-instances", str(uuid.uuid4())) + "/dashboard-series"), 404)
    expect(live.request(live.path("programmes", pid) + "/dashboard"), 422)
    expect(live.request(path + "&limit=101"), 422)
    expect(live.request(path + "&limit=0"), 422)
    # An indicator instance identifier is not a programme: kinds are never confused.
    expect(
        live.request(live.path("programmes", indicator["object_id"]) + "/dashboard?period_id=" + period_id),
        404,
    )


def test_result_withheld_without_result_access(live):
    from test_planning import expire_grant, restore_grant

    programme, indicator, period, keys = measure(live, keys=1)
    ratio_source(live, indicator, keys[0], "3", "4")
    calculate(live, indicator, period)
    held = expire_grant(live, "partner", "calculated-results.read")
    try:
        _, row = card(live, programme, indicator, period, actor="partner")
    finally:
        restore_grant(live, *held)
    assert row["official"] is None and row["provisional"] is None


def forge(live, token, **changes):
    raw, _ = token.split(".")
    data = json.loads(base64.urlsafe_b64decode(raw + "=" * ((-len(raw)) % 4)))
    data.update(changes)
    body = base64.urlsafe_b64encode(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).rstrip(
        b"="
    )
    mac = hmac.new(live.config["cookie_secret"].encode(), body, hashlib.sha256).hexdigest()
    return body.decode() + "." + mac


def test_signed_cursor_pages_and_refusals(live):
    programme, indicator, period, _ = measure(live, keys=1)
    for i in range(2):
        create(
            live,
            "indicator-instances",
            {
                "programme_id": programme["object_id"],
                "definition_version": indicator["data"]["definition_version"],
                "local_applicability": "Page " + str(i),
                "collector_id": live.fixture["actors"]["author"]["principal_id"],
                "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
            },
        )
    seen, cursor, pages = [], None, 0
    while True:
        params = {"limit": 1}
        if cursor:
            params["cursor"] = quote(cursor, safe="")
        body = dashboard(live, programme["object_id"], period["object_id"], **params)
        pages += 1
        assert len(body["indicators"]) <= 1 and "total_rows" not in body
        seen += [c["indicator_id"] for c in body["indicators"]]
        cursor = body["next_cursor"]
        if not cursor:
            break
    assert pages == 3 and len(seen) == len(set(seen)) == 3 and seen == sorted(seen)

    first = dashboard(live, programme["object_id"], period["object_id"], limit=1)["next_cursor"]
    base = (
        live.path("programmes", programme["object_id"])
        + "/dashboard?limit=1&period_id="
        + period["object_id"]
    )
    other = measure(live, keys=1)[0]
    refused = [
        base + "&cursor=x" + quote(first, safe=""),  # tampered
        base + "&cursor=" + quote(forge(live, first, expires=int(time.time()) - 1), safe=""),  # expired
        base + "&cursor=" + quote(forge(live, first, binding="0" * 64), safe=""),  # rebound
        live.path("programmes", other["object_id"])
        + "/dashboard?limit=1&period_id="
        + period["object_id"]
        + "&cursor="
        + quote(first, safe=""),  # another programme
        live.path("indicator-instances", indicator["object_id"])
        + "/dashboard-series?cursor="
        + quote(first, safe=""),  # another route
    ]
    for p in refused:
        assert expect(live.request(p), 400)["code"] == "INVALID_CURSOR", p
    # Another principal cannot replay the author's cursor.
    expect(live.request(base + "&cursor=" + quote(first, safe=""), actor="reviewer"), 400)
    # A still-valid forged expiry in the future with the right binding is accepted (control).
    valid = forge(live, first, expires=int(time.time()) + 60)
    assert expect(live.request(base + "&cursor=" + quote(valid, safe="")), 200)["indicators"]


# ----------------------------------------------------------------------- v0.27: drill-down, portfolio


def sources_of(live, indicator, period, actor="author", **params):
    query = "&".join(["period_id=" + period["object_id"]] + [k + "=" + str(v) for k, v in params.items()])
    body = get(
        live, "indicator-instances", indicator["object_id"] + "/dashboard-sources?" + query, actor=actor
    )
    validate("IndicatorDashboardSources", body)
    return body


def portfolio_of(live, definition_id, period, actor="author", **params):
    query = "&".join(["period_id=" + period["object_id"]] + [k + "=" + str(v) for k, v in params.items()])
    body = get(live, "indicator-definitions", definition_id + "/portfolio?" + query, actor=actor)
    validate("IndicatorPortfolio", body)
    return body


def definition_of(live, indicator):
    with live.db() as c:
        return str(
            c.execute(
                "SELECT object_id FROM impact.object_revision WHERE revision_id=%s",
                (indicator["data"]["definition_version"],),
            ).fetchone()["object_id"]
        )


def test_drilldown_lists_the_sources_behind_the_shown_value_with_their_disposition(live):
    """59/120: the drill-down names every source row of the period with its value state, approval
    state, namespace, event time and its disposition in the calculation the card shows; a later
    approval is NOT_IN_RESULT until recalculated; after the close the official value's inputs."""
    programme, indicator, period, keys = measure(live, keys=3)
    first = ratio_source(live, indicator, keys[0], "50", "100")
    second = ratio_source(live, indicator, keys[1], "1", "10")
    calculate(live, indicator, period)
    body = sources_of(live, indicator, period)
    assert body["value"]["mode"] == "PROVISIONAL" and body["source_check"] == "COMPLETE"
    assert body["period"]["period_state"] == "Open"
    by_id = {item["observation_id"]: item for item in body["items"]}
    assert set(by_id) == {first["object_id"], second["object_id"]}
    row = by_id[first["object_id"]]
    assert (row["source_namespace"], row["source_key"], row["event_at"]) == (
        "MANUAL",
        keys[0],
        "2026-08-15T12:00:00Z",
    )
    assert (row["value_state"], row["approval_state"], row["contribution"]) == (
        "PRESENT",
        "APPROVED",
        "INCLUDED",
    )
    assert (row["numerator"], row["denominator"]) == ("50", "100") and row[
        "changed_since_calculation"
    ] is False
    # A source approved after the calculation is listed but was not an input of the shown value.
    third = ratio_source(live, indicator, keys[2], "8", "10")
    body = sources_of(live, indicator, period)
    assert {i["observation_id"]: i["contribution"] for i in body["items"]}[
        third["object_id"]
    ] == "NOT_IN_RESULT"
    calculate(live, indicator, period)
    close(live, programme, period)
    body = sources_of(live, indicator, period)
    assert body["value"]["mode"] == "OFFICIAL" and body["period"]["period_state"] == "Locked"
    assert sorted(i["contribution"] for i in body["items"]) == ["INCLUDED"] * 3
    _, shown_card = card(live, programme, indicator, period)
    assert body["value"]["result_revision"] == shown_card["official"]["result_revision"]
    # No value yet: an instance without calculations lists its rows with no disposition.
    programme2, indicator2, period2, keys2 = measure(live, keys=1)
    blank = create(
        live,
        "observations",
        observation_data(indicator2, keys2[0], "0", {}) | {"value_state": "MISSING", "value": None},
    )
    body = sources_of(live, indicator2, period2)
    assert body["value"] == {"mode": None, "result_id": None, "result_revision": None}
    assert [
        (i["observation_id"], i["value_state"], i["value"], i["contribution"]) for i in body["items"]
    ] == [(blank["object_id"], "MISSING", None, None)]


def test_drilldown_withholds_hidden_rows_and_says_so(live):
    from test_planning import expire_grant, restore_grant

    programme, indicator, period, keys = measure(live, keys=1)
    ratio_source(live, indicator, keys[0], "3", "4")
    calculate(live, indicator, period)
    # A reader without observations.read sees no rows, a PARTIAL set and never a hidden count.
    held = expire_grant(live, "partner", "observations.read")
    try:
        body = sources_of(live, indicator, period, actor="partner")
    finally:
        restore_grant(live, *held)
    assert body["items"] == [] and body["source_check"] == "PARTIAL"
    assert "total" not in json.dumps(body)
    path = (
        live.path("indicator-instances", indicator["object_id"])
        + "/dashboard-sources?period_id="
        + period["object_id"]
    )
    assert expect(live.request(path, actor="other_tenant"), 404)["code"] == "RESOURCE_UNAVAILABLE"
    assert expect(live.request(path, actor="enumerator"), 403)["code"] == "POLICY_DENIED"
    expect(live.request(live.path("indicator-instances", indicator["object_id"]) + "/dashboard-sources"), 422)
    expect(
        live.request(
            live.path("indicator-instances", str(uuid.uuid4()))
            + "/dashboard-sources?period_id="
            + period["object_id"]
        ),
        404,
    )
    # Pages of one with a signed cursor; a tampered cursor and another route's cursor are refused.
    ratio_source(live, indicator, str(uuid.uuid4()), "1", "2")
    first = sources_of(live, indicator, period, limit=1)
    assert len(first["items"]) == 1 and first["next_cursor"]
    second = sources_of(live, indicator, period, limit=1, cursor=quote(first["next_cursor"], safe=""))
    assert second["items"][0]["observation_id"] != first["items"][0]["observation_id"]
    assert not second["next_cursor"]
    tampered = path + "&cursor=x" + quote(first["next_cursor"], safe="")
    assert expect(live.request(tampered), 400)["code"] == "INVALID_CURSOR"
    other_route = (
        live.path("programmes", programme["object_id"])
        + "/dashboard?period_id="
        + period["object_id"]
        + "&cursor="
        + quote(first["next_cursor"], safe="")
    )
    assert expect(live.request(other_route), 400)["code"] == "INVALID_CURSOR"


def programme_on(live, indicator, period, key):
    """A second active programme pinning the same definition revision, with one planned source."""
    programme = create(
        live,
        "programmes",
        {
            "code": "PFB",
            "title": "Portfolio B " + str(uuid.uuid4())[:8],
            "programme_type": "Health",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2027-01-01T00:00:00Z",
            "reporting_calendar_id": get(live, "reporting-calendars")["items"][0]["object_id"],
            "geography_id": get(live, "geographies")["items"][0]["object_id"],
        },
    )
    instance = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": indicator["data"]["definition_version"],
            "local_applicability": "Portfolio B sites",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    plan = create(
        live,
        "collection-plans",
        {
            "title": "Portfolio B collection",
            "indicator_id": instance["object_id"],
            "period_id": period["object_id"],
            "obligations": [
                {
                    "label": "Site B",
                    "source_namespace": "MANUAL",
                    "source_key": key,
                    "due_at": "2026-09-01T00:00:00Z",
                }
            ],
        },
    )
    approve(live, submit(live, "collection-plans", plan))
    action(live, "indicator-instances", instance, "activate")
    instance = get(live, "indicator-instances", instance["object_id"])
    action(live, "programmes", programme, "ready")
    action(live, "programmes", get(live, "programmes", programme["object_id"]), "activate")
    return programme, instance


def test_portfolio_pools_official_values_per_definition_version_from_stored_components(live):
    """Two programmes pin the same definition revision: 51/110 and 8/10 closed through the real
    flow pool to 59/120 = 49.17 (never the mean of 46.36 and 80.00); until both are closed the
    total is withheld."""
    programme_a, indicator_a, period, keys_a = measure(live, keys=2)
    ratio_source(live, indicator_a, keys_a[0], "50", "100")
    ratio_source(live, indicator_a, keys_a[1], "1", "10")
    calculate(live, indicator_a, period)
    close(live, programme_a, period)
    definition_id = definition_of(live, indicator_a)
    body = portfolio_of(live, definition_id, period)
    assert body["scope"] == "COMPLETE" and body["combination_rule"] == "POOLED_RATIO"
    assert [p["programme_id"] for p in body["programmes"]] == [programme_a["object_id"]]
    (version,) = body["versions"]
    assert version["definition_revision"] == indicator_a["data"]["definition_version"]
    assert version["pooled"]["value_state"] == "PRESENT" and version["pooled"]["displayed_value"] == "46.36"
    assert (version["pooled"]["numerator"], version["pooled"]["denominator"]) == ("51", "110")
    # A second programme on the same definition revision, not yet closed: the total is withheld.
    key_b = str(uuid.uuid4())
    programme_b, indicator_b = programme_on(live, indicator_a, period, key_b)
    ratio_source(live, indicator_b, key_b, "8", "10")
    calculate(live, indicator_b, period)
    body = portfolio_of(live, definition_id, period)
    (version,) = body["versions"]
    assert version["instance_count"] == 2 and version["pooled"]["contributing_count"] == 1
    assert version["pooled"]["value_state"] == "MISSING" and version["pooled"]["value"] is None
    assert version["pooled"]["reason_code"] == "OFFICIAL_VALUES_INCOMPLETE"
    rows = {p["programme_id"]: p for p in body["programmes"]}
    assert rows[programme_b["object_id"]]["official"] is None
    assert rows[programme_b["object_id"]]["period_state"] == "Open"
    assert rows[programme_a["object_id"]]["official"]["displayed_value"] == "46.36"
    assert rows[programme_a["object_id"]]["coverage"]["source"] == "CLOSE_SNAPSHOT"
    close(live, programme_b, period)
    body = portfolio_of(live, definition_id, period)
    (version,) = body["versions"]
    assert (version["pooled"]["numerator"], version["pooled"]["denominator"]) == ("59", "120")
    assert (version["pooled"]["value"], version["pooled"]["displayed_value"]) == ("49.166666666667", "49.17")
    assert version["pooled"]["contributing_count"] == version["pooled"]["instance_count"] == 2
    assert "80.00" in json.dumps(body) and "63.18" not in json.dumps(body)  # never the mean of displays
    # Pages of one with a signed cursor bound to this definition and period.
    first = portfolio_of(live, definition_id, period, limit=1)
    assert len(first["programmes"]) == 1 and first["next_cursor"] and len(first["versions"]) == 1
    second = portfolio_of(live, definition_id, period, limit=1, cursor=quote(first["next_cursor"], safe=""))
    assert second["programmes"][0]["programme_id"] != first["programmes"][0]["programme_id"]
    assert not second["next_cursor"]
    path = live.path("indicator-definitions", definition_id) + "/portfolio?period_id=" + period["object_id"]
    tampered = path + "&cursor=x" + quote(first["next_cursor"], safe="")
    assert expect(live.request(tampered), 400)["code"] == "INVALID_CURSOR"
    assert expect(live.request(path, actor="other_tenant"), 404)["code"] == "RESOURCE_UNAVAILABLE"
    assert expect(live.request(path, actor="enumerator"), 403)["code"] == "POLICY_DENIED"
    expect(live.request(live.path("indicator-definitions", definition_id) + "/portfolio"), 422)
    expect(
        live.request(
            live.path("indicator-definitions", str(uuid.uuid4()))
            + "/portfolio?period_id="
            + period["object_id"]
        ),
        404,
    )
    # An instance identifier is not a definition: kinds are never confused.
    expect(
        live.request(
            live.path("indicator-definitions", indicator_a["object_id"])
            + "/portfolio?period_id="
            + period["object_id"]
        ),
        404,
    )


def test_portfolio_withholds_totals_for_partial_scope_non_poolable_methods_and_zero_denominators(live):
    from test_planning import expire_grant, restore_grant

    programme, indicator, period, keys = measure(live, keys=1)
    ratio_source(live, indicator, keys[0], "0", "0")
    calculate(live, indicator, period)
    close(live, programme, period)
    definition_id = definition_of(live, indicator)
    body = portfolio_of(live, definition_id, period)
    (version,) = body["versions"]
    # The only official value is UNDEFINED (zero denominator): no total, never 0.
    assert version["pooled"]["value_state"] == "MISSING" and version["pooled"]["value"] is None
    assert body["programmes"][0]["official"]["value_state"] == "UNDEFINED"
    assert body["programmes"][0]["official"]["displayed_value"] is None
    # A reader who cannot see every instance gets a PARTIAL scope and no total.
    held = expire_grant(live, "partner", "indicator-instances.read")
    try:
        partial = portfolio_of(live, definition_id, period, actor="partner")
    finally:
        restore_grant(live, *held)
    assert partial["scope"] == "PARTIAL" and partial["programmes"] == [] and partial["versions"] == []
    # A non-poolable method (MEAN) never gets a total, however complete.
    programme_m, indicator_m, period_m, keys_m = measure(
        live, keys=1, measurement_type="COUNT", combination_rule="MEAN", unit="households", display_decimals=0
    )
    row = create(live, "observations", observation_data(indicator_m, keys_m[0], "4", {}))
    approve(live, submit(live, "observations", row))
    calculate(live, indicator_m, period_m)
    close(live, programme_m, period_m)
    body = portfolio_of(live, definition_of(live, indicator_m), period_m)
    (version,) = body["versions"]
    assert version["pooled"]["value_state"] == "NOT_APPLICABLE"
    assert version["pooled"]["reason_code"] == "NOT_POOLABLE"
    assert body["programmes"][0]["official"]["displayed_value"] == "4"
