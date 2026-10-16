"""APL-435/437/612: comparisons and freshness through governed live read models."""

from decimal import Decimal

from test_dashboards import (
    calculate,
    card,
    close,
    definition_of,
    measure,
    portfolio_of,
    ratio_source,
)
from test_live_application import expect
from test_measurement import approve, create, submit


def test_apl435_lower_is_better_retains_overachievement_and_exact_target_context(live):
    programme, indicator, period, keys = measure(live, keys=1)
    ratio_source(live, indicator, keys[0], "25", "100")
    calculate(live, indicator, period)
    target = create(
        live,
        "targets",
        {
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "target_kind": "VALUE",
            "value_state": "PRESENT",
            "value": "50",
            "direction": "LOWER",
            "target_basis": "ORIGINAL",
        },
    )
    approve(live, submit(live, "targets", target))
    _, row = card(live, programme, indicator, period)
    status = row["status"]
    assert status["attainment_percent"] == "200.00"
    assert Decimal(status["deviation"]) == Decimal("-25")
    assert status["attainment_formula"] == "target / actual × 100"
    assert status["time_semantic_compatibility"] == "COMPATIBLE"
    assert row["target"]["version_label"] == "Original target"
    assert row["target"]["applicable_period"]["period_id"] == period["object_id"]
    route = live.path("programmes", programme["object_id"]) + "/dashboard?period_id="
    expect(live.request(route + period["object_id"], actor="other_tenant"), 404)
    expect(live.request(route + period["object_id"], actor="revoked"), 404)
    assert expect(live.request(route + "invalid-period"), 404)["code"] == "RESOURCE_UNAVAILABLE"
    _, recovered = card(live, programme, indicator, period)
    assert recovered["status"] == status


def test_apl437_source_change_remains_stale_across_fetch_then_recalculation_recovers(live):
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "1", "10")
    calculate(live, indicator, period)
    _, first = card(live, programme, indicator, period)
    fresh = first["freshness"]
    assert fresh["data_state"] == "PROVISIONAL" and fresh["stale"] is False
    assert fresh["freshness_basis"] == "SOURCE_AND_CALCULATION_STATE"
    assert fresh["last_source_success_at"] and fresh["calculation_at"]
    assert fresh["approval_cutoff_at"] is None
    assert first["coverage"]["approved_count"] == 1
    ratio_source(live, indicator, keys[1], "8", "10")
    _, stale = card(live, programme, indicator, period)
    _, fetched_again = card(live, programme, indicator, period)
    assert stale["freshness"]["stale"] is True
    assert fetched_again["freshness"]["stale"] is True
    assert fetched_again["freshness"]["last_valid_data_at"] == fresh["last_valid_data_at"]
    assert fetched_again["freshness"]["data_state"] == "PROVISIONAL"
    assert fetched_again["provisional"]["displayed_value"] == "10.00"
    route = live.path("programmes", programme["object_id"]) + "/dashboard?period_id=" + period["object_id"]
    expect(live.request(route, actor="revoked"), 404)
    calculate(live, indicator, period)
    _, recovered = card(live, programme, indicator, period)
    assert recovered["freshness"]["stale"] is False
    assert recovered["provisional"]["displayed_value"] == "45.00"
    close(live, programme, period)
    _, locked = card(live, programme, indicator, period)
    assert locked["freshness"]["data_state"] == "SNAPSHOT"
    assert locked["freshness"]["approval_cutoff_at"]
    assert locked["official"]["displayed_value"] == "45.00"


def test_apl612_portfolio_ranks_qualified_exact_version_and_recovers_from_invalid_selector(live):
    programme, indicator, period, keys = measure(live, keys=1)
    ratio_source(live, indicator, keys[0], "8", "10")
    calculate(live, indicator, period)
    close(live, programme, period)
    definition = definition_of(live, indicator)
    body = portfolio_of(live, definition, period, coverage_threshold=100)
    comparison = body["comparison"]
    assert comparison["coverage_threshold"] == "100"
    assert comparison["hidden_members_disclosed"] is False
    assert comparison["raw_cross_group_ranking"] == "REFUSED"
    (group,) = comparison["groups"]
    assert group["compatibility_key"]["definition_revision"] == indicator["data"]["definition_version"]
    assert group["ranking"]["status"] == "QUALIFIED"
    assert group["ranking"]["unqualified_league_table"] is False
    (ranked,) = group["ranking"]["items"]
    assert ranked["programme_id"] == programme["object_id"]
    assert Decimal(ranked["denominator"]) == Decimal("10")
    path = live.path("indicator-definitions", definition) + "/portfolio?period_id=" + period["object_id"]
    expect(live.request(path, actor="other_tenant"), 404)
    expect(live.request(path, actor="revoked"), 404)
    expect(live.request(path + "&cursor=corrupt"), 400)
    assert portfolio_of(live, definition, period, coverage_threshold=100)["comparison"] == comparison
