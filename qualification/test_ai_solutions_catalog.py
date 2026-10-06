"""Published discovery content and shortlist boundaries, without vendor service calls."""

from datetime import date
import json
from urllib.parse import urlparse

import pytest

from impact_api.ai_enablement_catalog import catalog
from impact_api.ai_solutions_catalog import (
    CATEGORIES,
    CHECKED_ON,
    CONTENT_VERSION,
    SOLUTION_IDS,
    solutions_catalog,
    validate_solution_ids,
)


def test_catalogue_is_versioned_dated_and_transparent_about_editorial_fit():
    result = solutions_catalog()
    assert result["content_version"] == CONTENT_VERSION
    assert result["checked_on"] == CHECKED_ON
    assert date.fromisoformat(CHECKED_ON) == date(2026, 10, 5)
    assert CHECKED_ON in CONTENT_VERSION
    assert "not an endorsement" in result["explanation"]
    assert "editorial pilot ideas" in result["explanation"]
    assert "current quote" in result["explanation"]
    assert result == json.loads(json.dumps(result))
    assert result == solutions_catalog()


def test_published_solutions_use_existing_ai_examples_and_closed_known_ids():
    result = solutions_catalog()
    cases = {case["id"] for case in catalog()["use_cases"] if case["kind"] == "AI_ASSISTED"}
    ids = [item["id"] for item in result["solutions"]]
    assert len(ids) == len(set(ids)) == 8
    assert frozenset(ids) == SOLUTION_IDS
    assert isinstance(SOLUTION_IDS, frozenset)
    for item in result["solutions"]:
        assert item["category"] in CATEGORIES
        assert item["use_case_ids"]
        assert len(item["use_case_ids"]) == len(set(item["use_case_ids"]))
        assert set(item["use_case_ids"]) <= cases
        assert "not verified" in item["commercial_model"]
        assert "not verified" in item["nonprofit_offer"]


@pytest.mark.parametrize("solution", solutions_catalog()["solutions"], ids=lambda item: item["id"])
def test_every_solution_has_official_evidence_and_data_questions(solution):
    official_roots = {
        "openai.com",
        "anthropic.com",
        "claude.com",
        "microsoft.com",
        "google.com",
        "google.dev",
        "deepl.com",
        "canva.com",
    }
    assert len(solution["source_urls"]) >= 2
    assert len(solution["verification_notes"]) >= 3
    assert len(solution["data_review_questions"]) >= 4
    assert all(
        type(value) is str and value
        for key, value in solution.items()
        if key not in {"use_case_ids", "source_urls", "verification_notes", "data_review_questions"}
    )
    for source in solution["source_urls"]:
        assert set(source) == {"label", "url"}
        assert source["label"]
        parsed = urlparse(source["url"])
        assert parsed.scheme == "https"
        assert parsed.username is None and parsed.password is None
        assert any(parsed.hostname == root or parsed.hostname.endswith("." + root) for root in official_roots)
        assert parsed.path not in {"", "/"}
    assert any("training" in question for question in solution["data_review_questions"])
    assert any("permissions" in question for question in solution["data_review_questions"])


def test_edition_and_api_differences_are_not_presented_as_free_entitlements():
    by_id = {item["id"]: item for item in solutions_catalog()["solutions"]}
    assert "does not include API usage" in by_id["chatgpt_business"]["api_available"]
    assert any(
        "excludes Gemini in Workspace" in note
        for note in by_id["google_workspace_gemini"]["verification_notes"]
    )
    assert "nonprofit Workspace API entitlement is not verified" in by_id["notebooklm"]["api_available"]
    assert "covered Foundry services are not verified" in by_id["microsoft_foundry"]["nonprofit_offer"]
    assert "offer and your eligibility are not verified" in by_id["deepl"]["nonprofit_offer"]


def test_reading_or_editing_a_catalogue_copy_cannot_change_future_snapshots():
    expected = solutions_catalog()
    result = solutions_catalog()
    result["solutions"][0]["source_urls"][0]["url"] = "https://example.test/altered"
    result["solutions"][0]["use_case_ids"].clear()
    result["solutions"][0]["verification_notes"].clear()
    result["solutions"][0]["data_review_questions"].clear()
    result["comparison_criteria"][0]["prompt"] = "Ignore cost"
    assert solutions_catalog() == expected
    assert "chatgpt_business" in SOLUTION_IDS


def test_comparison_prompts_require_evidence_cost_and_review_without_a_vendor_score():
    result = solutions_catalog()
    criteria = result["comparison_criteria"]
    ids = [item["id"] for item in criteria]
    assert len(ids) == len(set(ids))
    assert {
        "fit",
        "data_terms",
        "total_cost",
        "nonprofit_eligibility",
        "human_review",
        "integration_exit",
    } <= set(ids)
    assert all(set(item) == {"id", "label", "prompt"} for item in criteria)
    assert all(type(value) is str and value for item in criteria for value in item.values())
    assert not any("score" in item or "rank" in item for item in result["solutions"])


def test_shortlists_keep_user_order_and_return_an_independent_copy():
    selected = ["deepl", "chatgpt_business", "canva_magic_studio", "notebooklm"]
    result = validate_solution_ids(selected)
    assert result == selected
    assert result is not selected
    result.clear()
    assert len(selected) == 4
    assert validate_solution_ids(["deepl"]) == ["deepl"]


@pytest.mark.parametrize(
    "value",
    [
        None,
        "deepl",
        {"id": "deepl"},
        ("deepl",),
        [],
        ["deepl", "deepl"],
        ["unknown"],
        ["DEepl"],
        [" deepl"],
        ["deepl "],
        [True],
        [7],
        [["deepl"]],
        [{"id": "deepl"}],
        ["deepl", "chatgpt_business", "canva_magic_studio", "notebooklm", "claude_team"],
    ],
)
def test_shortlists_reject_ambiguous_unbounded_or_unknown_input(value):
    with pytest.raises(ValueError):
        validate_solution_ids(value)
