"""Learning and persisted progress share stable lesson keys; checks remain self-assessment."""

from copy import deepcopy

from impact_api.ai_enablement_catalog import catalog


def test_practical_lessons_cover_every_saved_learning_step():
    paths = catalog()["learning_paths"]
    keys = []
    for path in paths:
        assert len(path["lessons"]) == len(path["steps"])
        for index, lesson in enumerate(path["lessons"]):
            assert lesson["key"] == f"{path['id']}:{index}"
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
