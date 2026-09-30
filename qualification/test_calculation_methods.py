"""v0.19 calculation methods and disaggregation: refusal of unsupported configurations at definition
submission, observation dimension validation, value-state handling, and the persisted breakdown.
Correct arithmetic for every method is qualified by the golden corpus (test_golden.py)."""

import uuid
from datetime import datetime, timezone

import pytest
from impact_api.domain import DomainError, calculate, disaggregate, validate_dimensions, validate_scheme
from impact_api.measurement import coverage, definition_ready
from test_live_application import cmd, expect
from test_measurement import action, approve, create, get, submit
from test_measurement_unit import definition

SEX = {
    "dimensions": [
        {
            "code": "sex",
            "label": "Sex",
            "version": "2026-1",
            "multiselect": False,
            "exhaustive": True,
            "categories": [{"code": "F", "label": "Female"}, {"code": "M", "label": "Male"}],
        }
    ]
}
SERVICE = {
    "dimensions": [
        {
            "code": "service",
            "label": "Service type",
            "version": "1",
            "multiselect": True,
            "exhaustive": False,
            "categories": [{"code": "A", "label": "Advice"}, {"code": "B", "label": "Benefit"}],
        }
    ]
}


def row(value="1", state="PRESENT", approval="APPROVED", dims=None, **kw):
    return {
        "value_state": state,
        "value": value if state == "PRESENT" else None,
        "approval_state": approval,
        "event_at": "2026-08-15T00:00:00Z",
        "dimension_values": dims or {},
        **kw,
    }


# ------------------------------------------------------------------------------------------------ unit


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"combination_rule": "WEIGHTED_INDEX"}, "CONFIGURATION_NOT_IMPLEMENTED"),
        ({"combination_rule": "UNIQUE_COUNT"}, "CONFIGURATION_NOT_IMPLEMENTED"),
        ({"combination_rule": "NONE"}, "CONFIGURATION_NOT_IMPLEMENTED"),
        ({"time_semantic": "CUMULATIVE"}, "CONFIGURATION_NOT_IMPLEMENTED"),  # never sum cumulative totals
        ({"time_semantic": "STOCK"}, "CONFIGURATION_NOT_IMPLEMENTED"),
        ({"combination_rule": "COUNT"}, "CONFIGURATION_NOT_IMPLEMENTED"),  # COUNT needs EVENT
        ({"measurement_type": "QUALITATIVE", "combination_rule": "MEDIAN"}, "CONFIGURATION_NOT_IMPLEMENTED"),
        ({"measurement_type": "SCORE", "combination_rule": "MEAN"}, "CONFIGURATION_NOT_IMPLEMENTED"),
        (
            {"measurement_type": "PERCENTAGE", "combination_rule": "MEDIAN", "numerator_meaning": "n"}
            | {"denominator_meaning": "d"},
            "CONFIGURATION_NOT_IMPLEMENTED",
        ),
        ({"measurement_type": "PERCENTAGE", "combination_rule": "MEAN"}, "COMPONENT_MEANINGS_REQUIRED"),
    ],
)
def test_unsupported_method_combinations_refused(changes, reason):
    with pytest.raises(DomainError) as exc:
        definition_ready(definition(**changes))
    assert exc.value.reason == reason


@pytest.mark.parametrize(
    "changes",
    [
        {"combination_rule": "COUNT", "time_semantic": "EVENT"},
        {"combination_rule": "LAST_VALID", "time_semantic": "STOCK"},
        {"combination_rule": "LAST_VALID", "time_semantic": "CUMULATIVE"},
        {"combination_rule": "MEAN"},
        {"combination_rule": "MEDIAN", "time_semantic": "STOCK"},
        {"combination_rule": "MIN"},
        {"combination_rule": "MAX", "measurement_type": "DECIMAL"},
    ],
)
def test_supported_method_combinations_accepted(changes):
    definition_ready(definition(**changes, disaggregation=SEX))


def test_scheme_rejects_duplicates_and_reserved_category():
    duplicate = {"dimensions": [SEX["dimensions"][0], SEX["dimensions"][0]]}
    reserved = {
        "dimensions": [
            {**SEX["dimensions"][0], "categories": [{"code": "UNSPECIFIED", "label": "Not given"}]}
        ]
    }
    repeated = {"dimensions": [{**SEX["dimensions"][0], "categories": [{"code": "F", "label": "a"}] * 2}]}
    for scheme in [duplicate, reserved, repeated]:
        with pytest.raises(DomainError) as exc:
            validate_scheme({"disaggregation": scheme})
        assert exc.value.reason == "INVALID_DISAGGREGATION"


@pytest.mark.parametrize(
    "scheme,dims,state,complete",
    [
        (SEX, {"age": "0-4"}, "PRESENT", True),  # undeclared dimension
        (SEX, {"sex": "X"}, "PRESENT", True),  # undeclared category
        (SEX, {"sex": "F|M"}, "PRESENT", True),  # several codes on a single-select dimension
        (SEX, {}, "PRESENT", True),  # exhaustive dimension without a code
        (SERVICE, {"service": "A|A"}, "PRESENT", True),  # repeated code
        (None, {"sex": "F"}, "PRESENT", False),  # no scheme at all
    ],
)
def test_observation_codes_must_match_the_pinned_scheme(scheme, dims, state, complete):
    d = definition(**({"disaggregation": scheme} if scheme else {}))
    with pytest.raises(DomainError) as exc:
        validate_dimensions(d, row(dims=dims, state=state), complete=complete)
    assert exc.value.reason == "INVALID_DIMENSION_VALUES"


def test_exhaustive_code_optional_for_draft_and_non_present_values():
    d = definition(disaggregation=SEX)
    validate_dimensions(d, row(dims={}), complete=False)
    validate_dimensions(d, row(state="MISSING", dims={}))


@pytest.mark.parametrize("state", ["MISSING", "NOT_COLLECTED", "NOT_APPLICABLE", "INVALID", "UNDEFINED"])
@pytest.mark.parametrize(
    "rule,semantic", [("SUM", "FLOW"), ("MEAN", "FLOW"), ("MIN", "FLOW"), ("LAST_VALID", "STOCK")]
)
def test_absent_value_states_never_become_zero(state, rule, semantic):
    d = definition(measurement_type="DECIMAL", combination_rule=rule, time_semantic=semantic)
    only_absent = calculate(d, [row(state=state)])
    assert only_absent["value_state"] == "UNDEFINED" and only_absent["value"] is None
    assert only_absent["displayed_value"] == "Undefined"
    mixed = calculate(d, [row("4"), row(state=state)])
    assert mixed["value"] == "4"  # a zero would halve a mean, lower a minimum or pull a latest value


def test_pending_and_returned_rows_are_excluded():
    d = definition(combination_rule="MAX")
    result = calculate(d, [row("3"), row("9", approval="SUBMITTED"), row("8", approval="RETURNED")])
    assert result["value"] == "3"


def test_breakdown_total_is_computed_from_sources_not_from_categories():
    d = definition(measurement_type="DECIMAL", display_decimals=0, disaggregation=SEX)
    rows = [row("0.4", dims={"sex": "F"}), row("0.4", dims={"sex": "M"})]
    total = calculate(d, rows)
    entries = disaggregate(d, rows)
    assert [e["displayed_value"] for e in entries] == ["0", "0"]
    assert total["displayed_value"] == "1" and total["value"] == "0.8"


def test_multiselect_categories_are_nonadditive_and_unique_total_stays_one():
    """FT-IND-006: one participant selects two service types."""
    d = definition(combination_rule="COUNT", time_semantic="EVENT", disaggregation=SERVICE)
    rows = [row("1", dims={"service": "A|B"})]
    entries = {e["category"]: e for e in disaggregate(d, rows)}
    assert entries["A"]["value"] == entries["B"]["value"] == "1"
    assert {e["additivity"] for e in entries.values()} == {"NONADDITIVE"}
    assert entries["UNSPECIFIED"]["value_state"] == "UNDEFINED"
    assert calculate(d, rows)["value"] == "1"


def test_coverage_without_required_obligations_is_not_applicable():
    """CAL08: zero required submissions give no percentage, never 100 and never a division by zero."""
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
    measured, included = coverage(plan, [], definition(), datetime(2026, 9, 29, tzinfo=timezone.utc))
    assert measured["required_count"] == 0 and measured["complete"] is False
    assert "approval_percent" not in measured and included == set()


# ------------------------------------------------------------------------------------------------ live


def build(live, scheme=SEX, **changes):
    calendar = get(live, "reporting-calendars")["items"][0]
    geography = get(live, "geographies")["items"][0]
    programme = create(
        live,
        "programmes",
        {
            "code": "CAL",
            "title": "Calculation " + str(uuid.uuid4())[:8],
            "programme_type": "Health",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2027-01-01T00:00:00Z",
            "reporting_calendar_id": calendar["object_id"],
            "geography_id": geography["object_id"],
        },
    )
    d = create(
        live, "indicator-definitions", definition(**changes, **({"disaggregation": scheme} if scheme else {}))
    )
    approve(live, submit(live, "indicator-definitions", d))
    d = get(live, "indicator-definitions", d["object_id"])
    indicator = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": d["revision_id"],
            "local_applicability": "Calculation checks",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    period = get(live, "periods", live.records["period"]["object_id"])
    keys = [str(uuid.uuid4()) for _ in range(3)]
    plan = create(
        live,
        "collection-plans",
        {
            "title": "Calculation collection",
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "obligations": [
                {
                    "label": f"P{i}",
                    "source_namespace": "MANUAL",
                    "source_key": k,
                    "due_at": "2026-09-01T00:00:00Z",
                }
                for i, k in enumerate(keys)
            ],
        },
    )
    approve(live, submit(live, "collection-plans", plan))
    action(live, "indicator-instances", indicator, "activate")
    indicator = get(live, "indicator-instances", indicator["object_id"])
    action(live, "programmes", programme, "ready")
    action(live, "programmes", get(live, "programmes", programme["object_id"]), "activate")
    return d, indicator, period, keys


def observation_data(indicator, key, value="4", dims=None, **kw):
    return {
        "source_namespace": "MANUAL",
        "source_key": key,
        "indicator_id": indicator["object_id"],
        "event_at": "2026-08-15T12:00:00Z",
        "captured_at": "2026-08-15T13:00:00Z",
        "capture_zone": "UTC",
        "value_state": "PRESENT",
        "value": value,
        "source_version": "1",
        "dimension_values": dims if dims is not None else {"sex": "F"},
        **kw,
    }


def test_definition_submission_refuses_unsupported_method(live):
    for changes, reason in [
        ({"combination_rule": "WEIGHTED_INDEX"}, "CONFIGURATION_NOT_IMPLEMENTED"),
        ({"time_semantic": "CUMULATIVE"}, "CONFIGURATION_NOT_IMPLEMENTED"),
        ({"disaggregation": {"dimensions": [SEX["dimensions"][0]] * 2}}, "INVALID_DISAGGREGATION"),
    ]:
        d = create(live, "indicator-definitions", definition(**changes))
        template = get(live, "workflow-templates")["items"][0]
        body = expect(
            live.request(
                live.path("indicator-definitions", d["object_id"]) + "/actions/submit",
                method="POST",
                body=cmd({"workflow_version": template["revision_id"]}, d["revision_id"]),
            ),
            422,
        )
        assert body["reason_code"] == reason
        assert get(live, "indicator-definitions", d["object_id"])["lifecycle_state"] == "Draft"


def test_contract_rejects_unknown_method_and_open_scheme(live):
    for data in [
        definition(combination_rule="AVERAGE_OF_AVERAGES"),
        definition(disaggregation={"dimensions": [{**SEX["dimensions"][0], "weights": [1]}]}),
        definition(disaggregation={"dimensions": [{**SEX["dimensions"][0], "code": "1bad"}]}),
    ]:
        body = expect(live.request(live.path("indicator-definitions"), method="POST", body=cmd(data)), 422)
        assert body["code"] == "VALIDATION_FAILED"


def test_disaggregated_calculation_persists_breakdown_and_denies_other_tenant(live):
    d, indicator, period, keys = build(live)
    for key, value, sex in zip(keys, ["10", "5", "2"], ["F", "M", "F"]):
        approve(
            live,
            submit(
                live,
                "observations",
                create(live, "observations", observation_data(indicator, key, value, {"sex": sex})),
            ),
        )
    receipt = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    result = get(live, "calculated-results", receipt["object_id"])["data"]
    assert result["value"] == "17" and result["dimensions"] == {}
    assert [
        (e["category"], e["value"], e["contributor_count"], e["additivity"]) for e in result["disaggregation"]
    ] == [
        ("F", "12", 2, "ADDITIVE"),
        ("M", "5", 1, "ADDITIVE"),
    ]
    assert all(e["dimension_version"] == "2026-1" for e in result["disaggregation"])
    with live.db() as db:
        stored = db.execute(
            "SELECT disaggregation FROM impact.calculated_result_current WHERE object_id=%s",
            (receipt["object_id"],),
        ).fetchone()["disaggregation"]
        pinned = db.execute(
            "SELECT disaggregation FROM impact.indicator_definition_current WHERE object_id=%s",
            (d["object_id"],),
        ).fetchone()["disaggregation"]
    assert stored == result["disaggregation"] and pinned == SEX
    expect(
        live.request(
            live.path("calculated-results", receipt["object_id"], tenant=live.fixture["tenant_b"]),
            actor="other_tenant",
        ),
        404,
    )


def test_observation_codes_refused_at_draft_and_submission(live):
    _, indicator, _, keys = build(live)
    for dims in [{"age": "0-4"}, {"sex": "X"}, {"sex": "F|M"}]:
        body = expect(
            live.request(
                live.path("observations"),
                method="POST",
                body=cmd(observation_data(indicator, keys[0], dims=dims)),
            ),
            422,
        )
        assert body["reason_code"] == "INVALID_DIMENSION_VALUES"
    draft = create(live, "observations", observation_data(indicator, keys[0], dims={}))
    template = get(live, "workflow-templates")["items"][0]
    body = expect(
        live.request(
            live.path("observations", draft["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": template["revision_id"]}, draft["revision_id"]),
        ),
        422,
    )
    assert body["reason_code"] == "INVALID_DIMENSION_VALUES"


def test_codes_refused_for_definition_without_scheme(live):
    _, indicator, _, keys = build(live, scheme=None)
    body = expect(
        live.request(
            live.path("observations"), method="POST", body=cmd(observation_data(indicator, keys[0]))
        ),
        422,
    )
    assert body["reason_code"] == "INVALID_DIMENSION_VALUES"


def test_event_count_requires_single_events_and_ratio_mean_requires_components(live):
    _, indicator, _, keys = build(live, scheme=None, combination_rule="COUNT", time_semantic="EVENT")
    row = create(live, "observations", observation_data(indicator, keys[0], "2", {}))
    template = get(live, "workflow-templates")["items"][0]
    body = expect(
        live.request(
            live.path("observations", row["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": template["revision_id"]}, row["revision_id"]),
        ),
        422,
    )
    assert body["reason_code"] == "INVALID_MEASUREMENT_VALUE"
    _, indicator, _, keys = build(
        live,
        scheme=None,
        measurement_type="PERCENTAGE",
        combination_rule="MEAN",
        numerator_meaning="Eligible reached",
        denominator_meaning="Eligible population",
    )
    row = create(live, "observations", observation_data(indicator, keys[0], "50", {}))
    body = expect(
        live.request(
            live.path("observations", row["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd({"workflow_version": template["revision_id"]}, row["revision_id"]),
        ),
        422,
    )
    assert body["reason_code"] == "INVALID_MEASUREMENT_VALUE"


def test_mean_result_is_labelled_unweighted(live):
    _, indicator, period, keys = build(
        live, scheme=None, measurement_type="DECIMAL", combination_rule="MEAN", display_decimals=2
    )
    for key, value in zip(keys, ["1", "2", "2"]):
        approve(
            live,
            submit(
                live,
                "observations",
                create(live, "observations", observation_data(indicator, key, value, {})),
            ),
        )
    receipt = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    result = get(live, "calculated-results", receipt["object_id"])["data"]
    assert (result["value"], result["displayed_value"]) == ("1.666666666667", "1.67")
    assert "UNWEIGHTED_MEAN" in [x["code"] for x in result["limitations"]]
    assert "disaggregation" not in result
