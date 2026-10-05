"""Learning and persisted progress share stable lesson keys; checks remain self-assessment."""

from copy import deepcopy

import pytest

import impact_api.ai_learning_content as module
from impact_api.ai_enablement_catalog import catalog
from impact_api.ai_learning_content import LEGACY_LESSON_ALIASES, canonical_lesson_key, enrich_learning_paths


def test_practical_lessons_cover_every_saved_learning_step():
    paths = catalog()["learning_paths"]
    keys = []
    for path in paths:
        assert len(path["lessons"]) == len(path["steps"])
        for index, lesson in enumerate(path["lessons"]):
            assert lesson["key"] == LEGACY_LESSON_ALIASES[f"{path['id']}:{index}"]
            keys.append(lesson["key"])
            assert lesson["lesson"] and lesson["exercise"] and lesson["title"]
            check = lesson["check"]
            assert check["question"] and check["explanation"]
            assert len(check["options"]) >= 2
            assert 0 <= check["answer"] < len(check["options"])
    assert len(keys) == len(set(keys)) == 12


def test_a_clients_lesson_edits_do_not_change_future_catalogues():
    original = deepcopy(catalog())
    changed = catalog()
    changed["learning_paths"][0]["lessons"][0]["check"]["options"].clear()
    assert catalog() == original


def test_legacy_aliases_keep_the_original_published_lesson_meaning():
    expected = {
        "foundations:0": ("foundations:safe-practice-task", "Start with a safe practice task"),
        "foundations:1": ("foundations:verify-claims", "Check claims before using a draft"),
        "foundations:2": ("foundations:choose-useful-method", "Choose the simplest useful method"),
        "foundations:3": ("foundations:data-boundary", "Write a data boundary"),
        "pilot_design:0": ("pilot_design:problem-and-owner", "Name one problem and an owner"),
        "pilot_design:1": ("pilot_design:measure-baseline", "Measure the current process"),
        "pilot_design:2": ("pilot_design:test-difficult-cases", "Test ordinary and difficult cases"),
        "pilot_design:3": ("pilot_design:review-and-stop-rule", "Agree a review and stop rule"),
        "procurement:0": ("procurement:testable-requirements", "Turn a goal into testable requirements"),
        "procurement:1": ("procurement:comparable-offers", "Ask for comparable written offers"),
        "procurement:2": ("procurement:whole-cost-and-exit", "Compare the whole cost and exit"),
        "procurement:3": (
            "procurement:data-and-delivery-terms",
            "Review data terms and delivery responsibilities",
        ),
    }
    titles = {
        lesson["key"]: lesson["title"] for path in catalog()["learning_paths"] for lesson in path["lessons"]
    }
    assert set(LEGACY_LESSON_ALIASES) == set(expected)
    for alias, (key, title) in expected.items():
        assert canonical_lesson_key(alias) == key and titles[key] == title


def test_reordering_paths_and_lessons_preserves_keys_and_legacy_meaning(monkeypatch):
    original = catalog()["learning_paths"]
    lessons = deepcopy(module._LESSONS)
    lessons["foundations"].reverse()
    monkeypatch.setattr(module, "_LESSONS", lessons)
    reordered = enrich_learning_paths(list(reversed(original)))
    original_by_key = {lesson["key"]: lesson for path in original for lesson in path["lessons"]}
    reordered_by_key = {lesson["key"]: lesson for path in reordered for lesson in path["lessons"]}
    assert original_by_key == reordered_by_key
    foundations = next(path for path in reordered if path["id"] == "foundations")
    assert foundations["lessons"][0]["key"] == "foundations:data-boundary"
    assert canonical_lesson_key("foundations:0") == "foundations:safe-practice-task"


def test_inserting_a_lesson_cannot_reassign_existing_positional_aliases(monkeypatch):
    lessons = deepcopy(module._LESSONS)
    synthetic = ("foundations:synthetic-addition", "Synthetic new lesson", *lessons["foundations"][0][2:])
    lessons["foundations"].insert(0, synthetic)
    monkeypatch.setattr(module, "_LESSONS", lessons)
    assert catalog()["learning_paths"][0]["lessons"][0]["key"] == "foundations:synthetic-addition"
    assert canonical_lesson_key("foundations:0") == "foundations:safe-practice-task"
    assert canonical_lesson_key("foundations:4") is None


def test_removed_content_is_unavailable_instead_of_reinterpreting_its_alias(monkeypatch):
    lessons = deepcopy(module._LESSONS)
    lessons["foundations"].pop(0)
    monkeypatch.setattr(module, "_LESSONS", lessons)
    assert canonical_lesson_key("foundations:0") is None
    assert canonical_lesson_key("foundations:safe-practice-task") is None
    assert canonical_lesson_key("foundations:1") == "foundations:verify-claims"


def test_legacy_alias_registry_cannot_be_changed_by_a_caller():
    with pytest.raises(TypeError):
        LEGACY_LESSON_ALIASES["foundations:0"] = "foundations:data-boundary"
