"""US-MP-03 opportunity ranking: database-free checks of the scoring maths, the weights rule, the
editorial score table, the contract and migration 0042 (part of `make unit`).

The real API and database qualification of every acceptance scenario is test_ai_ranking.py.
"""

from copy import deepcopy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import re

import pytest

from impact_api import ai_enablement_contracts as contracts
from impact_api import ai_opportunity_scores as editorial
from impact_api import ai_ranking as module
from impact_api.access_bootstrap import PROFILE_HASH
from impact_api.ai_enablement_catalog import (
    AI_PRACTICE_GAP,
    DATA_FOUNDATION_GAP,
    SENSITIVE_DATA_GAP,
    SMALL_TEAM_GAP,
    assess,
    catalog,
)
from impact_api.ai_ranking import points, rank, readiness, validate_weights, weighted_total
from impact_api.domain import DomainError

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "infrastructure/migrations/0042_ai_ranking_weights.sql"
DEFAULT = {"impact": 25, "effort": 25, "cost": 25, "readiness": 25}
IMPACT_FIRST = {"impact": 70, "effort": 10, "cost": 10, "readiness": 10}


def profile(**changes):
    return {
        "sector": "GENERAL",
        "team_size": 8,
        "goal": "Improve impact reporting",
        "data_readiness": "STRUCTURED",
        "ai_experience": "EXPERIMENTING",
        "sensitive_data": False,
        **changes,
    }


def order(result):
    return [(item["use_case_id"], item["weighted_total"]) for item in result["items"]]


def reference_total(score_set, weights):
    """Independent reference: rational arithmetic straight from the documented rule."""
    oriented = {
        "impact": score_set["impact"] - 1,
        "readiness": score_set["readiness"] - 1,
        "effort": 5 - score_set["effort"],
        "cost": 5 - score_set["cost"],
    }
    return sum(Fraction(weights[k] * oriented[k] * 25, 100) for k in oriented)


# Scenario: Ranked list with scores (default weights 25/25/25/25)


def test_default_weights_rank_by_descending_total_with_four_scores_each():
    result = rank(profile(), DEFAULT)
    # Hand-computed: communications 50+100+100+100 points, data_foundation 75+50+100+100, ...
    assert order(result) == [
        ("communications", "87.50"),
        ("data_foundation", "81.25"),
        ("mel_narratives", "75.00"),
        ("knowledge_search", "56.25"),
    ]
    assert [item["rank"] for item in result["items"]] == [1, 2, 3, 4]
    for item in result["items"]:
        assert set(item) == {"rank", "use_case_id", "scores", "weighted_total", "readiness_gaps"}
        assert set(item["scores"]) == {"impact", "effort", "cost", "readiness"}
        assert all(type(value) is int and 1 <= value <= 5 for value in item["scores"].values())
    assert result["unranked"] == []


# Scenario: Changing weights reorders the ranking


def test_impact_first_weights_reorder_the_same_opportunities():
    assert order(rank(profile(), IMPACT_FIRST)) == [
        ("data_foundation", "77.50"),
        ("mel_narratives", "75.00"),
        ("communications", "65.00"),
        ("knowledge_search", "52.50"),
    ]


# Scenario: Reject weights that do not total 100


@pytest.mark.parametrize(
    "weights,total",
    [((50, 30, 30, 10), 120), ((0, 0, 0, 0), 0), ((25, 25, 25, 24), 99), ((100, 0, 0, 1), 101)],
)
def test_weights_must_total_exactly_100(weights, total):
    with pytest.raises(DomainError) as caught:
        validate_weights(dict(zip(module.WEIGHT_FIELDS, weights)))
    error = caught.value
    assert (error.status, error.code, error.reason) == (422, "VALIDATION_FAILED", "AI_RANKING_WEIGHTS_TOTAL")
    assert "add up to " + str(total) in error.message


@pytest.mark.parametrize(
    "data",
    [
        {**DEFAULT, "impact": 25.0},  # JSON Schema accepts 25.0 as an integer; the server does not
        {**DEFAULT, "impact": True},
        {**DEFAULT, "impact": "25"},
        {**DEFAULT, "impact": None},
        {"impact": 125, "effort": -25, "cost": 0, "readiness": 0},
        {"impact": 101, "effort": 0, "cost": 0, "readiness": -1},
        {"impact": 50, "effort": 25, "cost": 25},
        {**DEFAULT, "approved": True},
        [25, 25, 25, 25],
        None,
    ],
)
def test_weights_are_closed_whole_numbers_from_0_to_100(data):
    with pytest.raises(DomainError) as caught:
        validate_weights(data)
    assert (caught.value.status, caught.value.reason) == (422, "AI_RANKING_WEIGHTS_INVALID")


def test_boundary_weights_are_accepted_in_canonical_order():
    assert list(validate_weights({"readiness": 0, "cost": 0, "effort": 0, "impact": 100})) == [
        "impact",
        "effort",
        "cost",
        "readiness",
    ]
    assert validate_weights(DEFAULT) == DEFAULT


# Scenario: Reject ranking an opportunity without all four scores


def test_opportunity_missing_its_cost_score_is_only_listed_as_not_ranked():
    table = editorial.scores()
    del table["communications"]["cost"]
    result = rank(profile(), DEFAULT, table)
    assert "communications" not in [item["use_case_id"] for item in result["items"]]
    assert result["unranked"] == [{"use_case_id": "communications", "missing_scores": ["cost"]}]
    assert [item["rank"] for item in result["items"]] == [1, 2, 3]
    assert order(result) == [
        ("data_foundation", "81.25"),
        ("mel_narratives", "75.00"),
        ("knowledge_search", "56.25"),
    ]


def test_an_unscored_use_case_lists_every_missing_score():
    table = editorial.scores()
    del table["knowledge_search"]
    table["mel_narratives"] = {"impact": 4}
    result = rank(profile(), DEFAULT, table)
    assert result["unranked"] == [
        {"use_case_id": "knowledge_search", "missing_scores": ["impact", "effort", "cost"]},
        {"use_case_id": "mel_narratives", "missing_scores": ["effort", "cost"]},
    ]


def test_every_editorial_use_case_is_scored_on_the_documented_scale():
    table = editorial.scores()
    assert set(table) == {case["id"] for case in catalog()["use_cases"]}
    for scores in table.values():
        assert set(scores) == set(editorial.CRITERIA)
        assert all(type(value) is int and 1 <= value <= 5 for value in scores.values())
    assert editorial.STATUS == "EDITORIAL_DRAFT_PENDING_ADVISOR_REVIEW"
    assert editorial.SCORE_VERSION


@pytest.mark.parametrize(
    "table",
    [
        {"communications": {"cost": 0}},
        {"communications": {"cost": 6}},
        {"communications": {"cost": 2.0}},
        {"communications": {"cost": True}},
        {"communications": {"readiness": 3}},  # readiness is computed, never editorial
        {"communications": None},
        [],
    ],
)
def test_score_tables_outside_the_scale_are_refused(table):
    with pytest.raises(ValueError):
        rank(profile(), DEFAULT, table)


# Readiness from the gaps assess() finds


def test_readiness_counts_case_gaps_small_team_and_sensitive_data_review():
    result = rank(
        profile(
            sector="HEALTH", team_size=3, data_readiness="NONE", ai_experience="NONE", sensitive_data=True
        ),
        DEFAULT,
    )
    readiness_by_case = {item["use_case_id"]: item["scores"]["readiness"] for item in result["items"]}
    # data_foundation: small team only (it is not an AI example and needs no data organisation).
    # communications: no AI practice, small team, sensitive data review.
    # the others also need more data organisation: four gaps, the floor of 1.
    assert readiness_by_case == {
        "data_foundation": 4,
        "communications": 2,
        "knowledge_search": 1,
        "health_communications": 1,
        "mel_narratives": 1,
    }
    gaps = {item["use_case_id"]: item["readiness_gaps"] for item in result["items"]}
    assert gaps["data_foundation"] == [SMALL_TEAM_GAP]
    assert SENSITIVE_DATA_GAP in gaps["communications"] and SMALL_TEAM_GAP in gaps["communications"]
    assert len(gaps["mel_narratives"]) == 4
    # Equal totals are ordered by use-case ID: health_communications before mel_narratives.
    assert order(result) == [
        ("data_foundation", "75.00"),
        ("communications", "68.75"),
        ("health_communications", "50.00"),
        ("mel_narratives", "50.00"),
        ("knowledge_search", "31.25"),
    ]
    assert [item["rank"] for item in result["items"]] == [1, 2, 3, 4, 5]


def test_readiness_is_full_without_gaps_and_never_below_one():
    assert readiness({"capacity_gaps": []}, "AI_ASSISTED", []) == (5, [])
    gaps = [SMALL_TEAM_GAP, SENSITIVE_DATA_GAP]
    assert readiness({"capacity_gaps": ["a", "b"]}, "AI_ASSISTED", gaps)[0] == 1
    assert readiness({"capacity_gaps": []}, "NON_AI", gaps) == (4, [SMALL_TEAM_GAP])
    with pytest.raises(ValueError):
        readiness({"capacity_gaps": ["a", "b", "c"]}, "AI_ASSISTED", gaps)


def test_ties_are_broken_by_use_case_id_whatever_the_table_order():
    same = {"impact": 3, "effort": 3, "cost": 3}
    table = {case["id"]: dict(same) for case in reversed(catalog()["use_cases"])}
    result = rank(profile(), DEFAULT, table)
    ids = [item["use_case_id"] for item in result["items"]]
    assert ids == sorted(ids)
    assert len({item["weighted_total"] for item in result["items"]}) == 1


# Exact decimal arithmetic (rule 6 style)


def test_points_are_oriented_so_higher_is_better_and_effort_and_cost_reverse():
    assert [points("impact", s) for s in range(1, 6)] == [0, 25, 50, 75, 100]
    assert [points("readiness", s) for s in range(1, 6)] == [0, 25, 50, 75, 100]
    assert [points("effort", s) for s in range(1, 6)] == [100, 75, 50, 25, 0]
    assert [points("cost", s) for s in range(1, 6)] == [100, 75, 50, 25, 0]
    for bad in (0, 6, 2.0, True, "3"):
        with pytest.raises(ValueError):
            points("impact", bad)


def test_weighted_totals_equal_a_rational_reference_for_every_score_combination():
    weight_sets = [DEFAULT, IMPACT_FIRST, {"impact": 33, "effort": 33, "cost": 33, "readiness": 1}]
    weight_sets += [
        dict(zip(module.WEIGHT_FIELDS, w)) for w in [(100, 0, 0, 0), (1, 2, 3, 94), (0, 0, 0, 100)]
    ]
    for weights in weight_sets:
        for combination in itertools.product(range(1, 6), repeat=4):
            score_set = dict(zip(module.WEIGHT_FIELDS, combination))
            numerator, shown = weighted_total(score_set, weights)
            expected = reference_total(score_set, weights)
            assert Fraction(numerator, 100) == expected
            assert Fraction(shown) == expected, (score_set, weights, shown)
            assert re.fullmatch(r"(100\.00|[0-9]{1,2}\.[0-9]{2})", shown)


def test_extreme_totals_and_no_floating_point_in_the_ranking_code():
    best = {"impact": 5, "effort": 1, "cost": 1, "readiness": 5}
    worst = {"impact": 1, "effort": 5, "cost": 5, "readiness": 1}
    assert weighted_total(best, DEFAULT) == (10000, "100.00")
    assert weighted_total(worst, DEFAULT) == (0, "0.00")
    for name in ("ai_ranking.py", "ai_opportunity_scores.py"):
        source = (ROOT / "apps/api/impact_api" / name).read_text()
        assert "float(" not in source and "round(" not in source, name


# The existing assessment is untouched


def test_assessment_order_and_gap_texts_are_unchanged_and_never_mutated():
    assert DATA_FOUNDATION_GAP == "Agree data definitions, ownership and a basic quality routine"
    assert AI_PRACTICE_GAP == "Practise verification and safe prompting before live use"
    assert SMALL_TEAM_GAP == "Reserve staff time and name a backup reviewer for a small team"
    assert SENSITIVE_DATA_GAP == "Complete a data-handling review before any real data enters an AI service"
    source = profile()
    before = deepcopy(source)
    expected = assess(source)
    table = editorial.scores()
    snapshot = deepcopy(table)
    for weights in (DEFAULT, IMPACT_FIRST):
        rank(source, weights, table)
    assert source == before and table == snapshot
    assert assess(source) == expected
    # The assessment keeps its keyword-relevance order (test_ai_enablement_catalog.py pins it).
    assert expected["recommendations"][0]["use_case_id"] == "mel_narratives"
    # The editorial scores stay outside the archived catalogue.
    assert not {"impact", "effort", "cost"} & {key for case in catalog()["use_cases"] for key in case}


def test_invalid_profiles_are_refused_before_ranking():
    with pytest.raises(ValueError):
        rank(profile(sector="OTHER"), DEFAULT)
    with pytest.raises(ValueError):
        rank({**profile(), "extra": 1}, DEFAULT)


# Contract, policy rows and access profile


def generated():
    spec = {"components": {"schemas": {"Error": {}}}, "paths": {}}
    access = {"operations": []}
    contracts.augment(spec, access)
    return spec, {row["operation_id"]: row for row in access["operations"]}


def test_weights_change_is_a_manage_preference_without_fresh_sign_in_and_audited():
    spec, rows = generated()
    update = rows["update_ai_ranking_weights"]
    assert (update["method"], update["capability"]) == ("PUT", "ai.enablement.manage")
    assert update["role_templates"] == ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"]
    assert update["fresh_assurance_seconds"] is None and update["audit"] is True
    # The same holders as every other ai.enablement.manage operation (saved adoption plans).
    published = {
        row["operation_id"]: row
        for row in json.loads((ROOT / "packages/contracts/access-policy.json").read_text())["operations"]
    }
    assert update["role_templates"] == published["create_ai_adoption_plan"]["role_templates"]
    for read in ("get_ai_ranking_weights", "rank_ai_opportunities"):
        assert rows[read]["capability"] == "ai.enablement.read"
        assert rows[read]["role_templates"] == rows["get_ai_enablement_catalog"]["role_templates"]
        assert rows[read]["audit"] is False and rows[read]["fresh_assurance_seconds"] is None
    weights = "/v1/tenants/{tenant_id}/ai-enablement/ranking-weights"
    assert set(spec["paths"][weights]) == {"get", "put"}
    assert set(spec["paths"]["/v1/tenants/{tenant_id}/ai-enablement/ranking"]) == {"post"}


def test_ranking_schemas_are_closed():
    spec, _ = generated()
    schemas = spec["components"]["schemas"]
    for name in (
        "AIRankingWeightsData",
        "AIRankingWeightsCommand",
        "AIRankingWeights",
        "AIRankingWeightsReceipt",
        "AIRankingRequest",
        "AIOpportunityScores",
        "AIRankedOpportunity",
        "AIUnrankedOpportunity",
        "AIOpportunityRanking",
    ):
        assert schemas[name]["additionalProperties"] is False, name
    data = schemas["AIRankingWeightsData"]
    assert data["required"] == ["impact", "effort", "cost", "readiness"]
    assert all(p == {"type": "integer", "minimum": 0, "maximum": 100} for p in data["properties"].values())
    command = schemas["AIRankingWeightsCommand"]
    assert set(command["required"]) == {"operation_id", "expected_revision", "data"}
    assert command["properties"]["expected_revision"]["type"] == ["string", "null"]


def test_generated_contracts_carry_the_ranking_routes_and_the_profile_is_unchanged():
    access = json.loads((ROOT / "packages/contracts/access-policy.json").read_text())
    rows = {row["operation_id"]: row for row in access["operations"]}
    _, expected = generated()
    for operation in ("get_ai_ranking_weights", "update_ai_ranking_weights", "rank_ai_opportunities"):
        assert rows[operation] == expected[operation]
    implemented = json.loads((ROOT / "packages/contracts/openapi-implemented.json").read_text())
    assert set(implemented["paths"]["/v1/tenants/{tenant_id}/ai-enablement/ranking-weights"]) == {
        "get",
        "put",
    }
    assert "/v1/tenants/{tenant_id}/ai-enablement/ranking" in implemented["paths"]
    # No capability changed: the onboarding profile is the one migration 0041 registered.
    assert PROFILE_HASH == "14997060d0b7d8a95c820674a5b1ad38c029eeed5d113e674a6ca04ec28ce133"


# Migration 0042


def test_migration_0042_only_widens_the_kind_check_and_adds_the_singleton_index():
    sql = MIGRATION.read_text()
    assert sql.startswith("BEGIN;\nSET LOCAL ROLE impact_owner;\n") and sql.rstrip().endswith("COMMIT;")
    assert "OR object_type = ''AIRankingWeights''" in sql
    assert "DROP CONSTRAINT object_registry_object_type_check" in sql
    assert re.search(
        r"CREATE UNIQUE INDEX ai_ranking_weights_one_per_tenant ON impact\.object_registry\(tenant_id\)\s+"
        r"WHERE object_type='AIRankingWeights';",
        sql,
    )
    code = "\n".join(line for line in sql.splitlines() if not line.lstrip().startswith("--"))
    for forbidden in ("GRANT", "REVOKE", "CREATE TABLE", "POLICY", "SECURITY DEFINER", "DROP TABLE"):
        assert forbidden not in code.upper(), forbidden


def test_migration_0042_is_ledgered_in_the_data_dictionary():
    digest = hashlib.sha256(MIGRATION.read_bytes()).hexdigest()
    dictionary = (ROOT / "docs/current/CURRENT-DATA-DICTIONARY.md").read_text()
    assert "| 0042_ai_ranking_weights.sql | " + digest + " |" in dictionary


# Stored weights are used only when they read back exactly as saved


@pytest.mark.parametrize(
    "row",
    [
        {"restriction_state": "AVAILABLE", "payload": {**DEFAULT, "impact": 26}},
        {"restriction_state": "AVAILABLE", "payload": {**DEFAULT, "extra": 0}},
        {"restriction_state": "REMOVED", "payload": DEFAULT},
    ],
)
def test_unreadable_saved_weights_fail_closed(row):
    with pytest.raises(DomainError) as caught:
        module.AIRanking._view({"head_revision": "r", "saved_at": None, "author_id": "a", **row})
    assert (caught.value.status, caught.value.reason) == (503, "AI_RANKING_WEIGHTS_UNREADABLE")


def test_no_saved_weights_means_the_defaults_and_no_revision():
    assert module.AIRanking._view(None) == {
        "source": "DEFAULT",
        "revision_id": None,
        "weights": DEFAULT,
        "saved_at": None,
        "saved_by": None,
    }
    assert module.DEFAULT_WEIGHTS == DEFAULT and sum(DEFAULT.values()) == 100
