"""Published discovery content and shortlist boundaries, without vendor service calls."""

from copy import deepcopy
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker
import pytest

import impact_api.ai_solutions_catalog as module
from impact_api.ai_enablement_catalog import catalog
from impact_api.ai_solutions_catalog import (
    CATEGORIES,
    CHECKED_ON,
    CONTENT_VERSION,
    DISCLOSURES_DECLARED_ON,
    RELATIONSHIP_TYPES,
    SOLUTION_IDS,
    SolutionsCatalogInvalid,
    catalog_schema,
    solutions_catalog,
    validate_catalog,
    validate_disclosure,
    validate_solution_ids,
)

ROOT = Path(__file__).resolve().parents[1]


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
    # commercial_disclosure (an object, US-DC-04) is checked field by field below.
    assert all(
        type(value) is str and value
        for key, value in solution.items()
        if key
        not in {
            "use_case_ids",
            "source_urls",
            "verification_notes",
            "data_review_questions",
            "commercial_disclosure",
        }
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


# US-DC-04: every listing discloses commercial relationships, or the catalogue is not served


def disclosed(**changes):
    return {
        "status": "DISCLOSED",
        "relationship_types": ["referral_fee", "sponsorship"],
        "statement": "Synthetic example: Imprana receives a referral fee and sponsorship from this provider.",
        "declared_on": "2026-10-09",
        **changes,
    }


def contract_validator():
    contract = json.loads((ROOT / "packages/contracts/openapi-implemented.json").read_text())
    return Draft202012Validator(
        contract["components"]["schemas"]["AISolutionsCatalog"], format_checker=FormatChecker()
    )


@pytest.mark.parametrize("solution", solutions_catalog()["solutions"], ids=lambda item: item["id"])
def test_every_listing_carries_a_valid_commercial_disclosure(solution):
    disclosure = solution["commercial_disclosure"]
    assert set(disclosure) == {"status", "relationship_types", "statement", "declared_on"}
    # Today no commercial relationship is known for any listing; nothing is invented.
    assert disclosure["status"] == "NONE_KNOWN"
    assert disclosure["relationship_types"] == []
    assert disclosure["declared_on"] == DISCLOSURES_DECLARED_ON == "2026-10-09"
    assert date.fromisoformat(disclosure["declared_on"]) >= date.fromisoformat(CHECKED_ON)
    statement = disclosure["statement"]
    assert statement.startswith("Imprana editorial declaration, pending advisor review:")
    assert solution["provider"] in statement and "is known" in statement
    assert all(kind.replace("_", " ") in statement for kind in ("referral_fee", "revenue_share", "reseller"))
    assert 1 <= len(statement) <= 1000
    validate_disclosure(disclosure)


def test_no_relationship_is_invented_while_no_vendor_is_registered():
    assert catalog()["marketplace_status"]["vendors"] == []
    listings = solutions_catalog()["solutions"]
    assert {item["commercial_disclosure"]["status"] for item in listings} == {"NONE_KNOWN"}
    # "None known" is what editorial knows, never a claim that no relationship can exist.
    assert not any(
        "no relationship exists" in item["commercial_disclosure"]["statement"] for item in listings
    )
    assert "commercial relationship" in solutions_catalog()["explanation"]


def test_relationship_types_are_the_closed_list_of_the_story():
    assert RELATIONSHIP_TYPES == ("referral_fee", "revenue_share", "reseller", "sponsorship", "ownership")
    disclosure = catalog_schema()["properties"]["solutions"]["items"]["properties"]["commercial_disclosure"]
    statuses = [variant["properties"]["status"]["const"] for variant in disclosure["oneOf"]]
    assert statuses == ["NONE_KNOWN", "DISCLOSED"]
    assert disclosure["oneOf"][1]["properties"]["relationship_types"]["items"]["enum"] == list(
        RELATIONSHIP_TYPES
    )


def test_published_catalogue_satisfies_its_closed_regenerated_contract():
    schema = catalog_schema()
    contract = json.loads((ROOT / "packages/contracts/openapi-implemented.json").read_text())
    assert contract["components"]["schemas"]["AISolutionsCatalog"] == schema
    listing = schema["properties"]["solutions"]["items"]
    assert schema["additionalProperties"] is False and listing["additionalProperties"] is False
    assert "commercial_disclosure" in listing["required"]
    assert all(
        variant["additionalProperties"] is False
        for variant in listing["properties"]["commercial_disclosure"]["oneOf"]
    )
    assert not list(contract_validator().iter_errors(solutions_catalog()))
    assert validate_catalog(solutions_catalog()) == solutions_catalog()


def test_a_disclosed_relationship_with_types_and_a_statement_is_valid():
    validate_disclosure(disclosed())
    validate_disclosure(disclosed(relationship_types=list(RELATIONSHIP_TYPES)))
    published = solutions_catalog()
    published["solutions"][2]["commercial_disclosure"] = disclosed()
    assert validate_catalog(published) is published
    assert not list(contract_validator().iter_errors(published))


INVALID_DISCLOSURES = {
    "missing": None,
    "not_an_object": "NONE_KNOWN",
    "unknown_status": {**disclosed(), "status": "PARTNER"},
    "disclosed_without_statement": {k: v for k, v in disclosed().items() if k != "statement"},
    "disclosed_with_empty_statement": disclosed(statement=""),
    "disclosed_with_blank_statement": disclosed(statement="   \n"),
    "disclosed_without_a_type": disclosed(relationship_types=[]),
    "none_known_naming_a_type": disclosed(status="NONE_KNOWN"),
    "unknown_relationship_type": disclosed(relationship_types=["affiliate"]),
    "repeated_relationship_type": disclosed(relationship_types=["reseller", "reseller"]),
    "types_not_a_list": disclosed(relationship_types="reseller"),
    "statement_too_long": disclosed(statement="x" * 1001),
    "statement_not_text": disclosed(statement=7),
    "undated": {k: v for k, v in disclosed().items() if k != "declared_on"},
    "impossible_date": disclosed(declared_on="2026-02-30"),
    "not_a_calendar_date": disclosed(declared_on="9 October 2026"),
    "extra_field": disclosed(verified=True),
}


@pytest.mark.parametrize("case", sorted(INVALID_DISCLOSURES))
def test_a_listing_without_a_valid_disclosure_fails_validation_and_the_catalogue_is_not_served(
    monkeypatch, case
):
    listings = deepcopy(module._SOLUTIONS)
    value = INVALID_DISCLOSURES[case]
    if case == "missing":
        del listings[3]["commercial_disclosure"]
    else:
        listings[3]["commercial_disclosure"] = deepcopy(value)
    monkeypatch.setattr(module, "_SOLUTIONS", listings)
    with pytest.raises(SolutionsCatalogInvalid) as refused:
        solutions_catalog()
    assert repr(listings[3]["id"]) in str(refused.value)
    with pytest.raises(SolutionsCatalogInvalid):
        validate_disclosure(listings[3].get("commercial_disclosure"))
    # The published contract refuses the same catalogue independently of the Python rules.
    candidate = {
        "content_version": CONTENT_VERSION,
        "checked_on": CHECKED_ON,
        "explanation": "Synthetic",
        "solutions": listings,
        "comparison_criteria": [],
    }
    assert list(contract_validator().iter_errors(candidate))


@pytest.mark.parametrize("statement", [None, "", " "])
def test_disclosed_without_a_statement_fails_validation(monkeypatch, statement):
    disclosure = disclosed()
    if statement is None:
        del disclosure["statement"]
    else:
        disclosure["statement"] = statement
    with pytest.raises(SolutionsCatalogInvalid, match="statement|four fields"):
        validate_disclosure(disclosure)
    listings = deepcopy(module._SOLUTIONS)
    listings[0]["commercial_disclosure"] = disclosure
    monkeypatch.setattr(module, "_SOLUTIONS", listings)
    with pytest.raises(SolutionsCatalogInvalid):
        solutions_catalog()


def test_a_new_listing_built_without_a_disclosure_is_never_given_one_by_default(monkeypatch):
    added = module._solution(
        "synthetic_tool",
        "Synthetic tool",
        "Synthetic provider",
        "DESIGN",
        ["communications"],
        "Synthetic",
        "Synthetic",
        "Synthetic, not verified",
        "Synthetic, not verified",
        "Synthetic",
        [("Synthetic", "https://example.org/synthetic")],
        ["One", "Two", "Three"],
    )
    assert "commercial_disclosure" not in added
    monkeypatch.setattr(module, "_SOLUTIONS", [*deepcopy(module._SOLUTIONS), added])
    with pytest.raises(SolutionsCatalogInvalid, match="synthetic_tool"):
        solutions_catalog()


def test_duplicate_listing_ids_fail_validation(monkeypatch):
    listings = deepcopy(module._SOLUTIONS)
    listings[1]["id"] = listings[0]["id"]
    monkeypatch.setattr(module, "_SOLUTIONS", listings)
    with pytest.raises(SolutionsCatalogInvalid, match="unique"):
        solutions_catalog()
