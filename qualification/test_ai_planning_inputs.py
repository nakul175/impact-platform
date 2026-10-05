"""Pure input-snapshot and replay checks; no database or provider qualification."""

from copy import deepcopy
import json
from uuid import uuid4

import pytest

import impact_api.ai_adoption_plans as module
import impact_api.ai_task_practice as practice_module
from impact_api.ai_adoption_plans import validate_plan
from impact_api.domain import DomainError
from test_ai_adoption_plans import engine as engine
from test_ai_adoption_plans import plan, request


def cost_inputs():
    return {
        "currency": "INR",
        "period_months": 12,
        "offers": [
            {
                "id": "synthetic-a",
                "name": "Synthetic supplied offer A",
                "lines": [
                    {
                        "id": "subscription",
                        "category": "SUBSCRIPTION",
                        "label": "Supplied monthly amount",
                        "quantity": "2.5",
                        "unit_amount": "0.004",
                        "cadence": "MONTHLY",
                    },
                    {
                        "id": "exit",
                        "category": "EXIT",
                        "label": "Exit cost not supplied",
                        "quantity": "0",
                        "unit_amount": None,
                        "cadence": "ONE_OFF",
                    },
                ],
            }
        ],
    }


def pilot_inputs():
    return {
        "task_label": "Draft a synthetic public newsletter",
        "baseline": {
            "sample_size": 10,
            "total_drafting_minutes": "100",
            "total_review_minutes": "20",
            "factual_corrections": 2,
        },
        "pilot": {
            "sample_size": 20,
            "total_drafting_minutes": "80",
            "total_review_minutes": "40",
            "factual_corrections": 4,
        },
        "comparable": True,
        "notes": "Synthetic observations only; no causal or accepted-impact claim.",
    }


def task_inputs():
    return {
        "template_id": "invitation",
        "brief": "Synthetic workshop; invented event facts only.",
        "draft": "Draft for human review. Venue and registration not supplied.",
        "review_notes": "The communications role must check the missing event details.",
        "checked_steps": ["source_facts", "privacy"],
    }


def planning_plan():
    return {
        **plan(),
        "planning": {
            "cost_comparison": cost_inputs(),
            "pilot_evaluation": pilot_inputs(),
            "task_practice": task_inputs(),
        },
    }


@pytest.mark.parametrize("fields", [(), ("cost_comparison",), ("pilot_evaluation",), ("task_practice",)])
def test_optional_planning_inputs_accept_empty_or_partial_work_without_certifying_it(fields):
    data = planning_plan()
    data["planning"] = {key: value if key in fields else None for key, value in data["planning"].items()}
    before = deepcopy(data)
    validate_plan(data)
    assert data == before
    assert not {"approved", "official_result", "certified", "award"}.intersection(data)


def test_original_six_field_plan_remains_valid_without_a_planning_snapshot():
    data = plan()
    assert len(data) == 6 and "planning" not in data
    before = deepcopy(data)
    validate_plan(data)
    assert data == before


@pytest.mark.parametrize(
    "edit",
    [
        pytest.param(lambda p: p.update(planning=None), id="planning-null"),
        pytest.param(lambda p: p.update(planning=[]), id="planning-array"),
        pytest.param(lambda p: p["planning"].pop("task_practice"), id="missing-planning-key"),
        pytest.param(lambda p: p["planning"].update(approved=True), id="unknown-planning-key"),
        pytest.param(
            lambda p: p["planning"]["cost_comparison"].update(cheapest_offer_ids=["synthetic-a"]),
            id="cost-result-instead-of-input",
        ),
        pytest.param(lambda p: p["planning"]["cost_comparison"].update(period_months=True), id="bool-months"),
        pytest.param(
            lambda p: p["planning"]["cost_comparison"]["offers"][0]["lines"][0].update(unit_amount=0.004),
            id="float-amount",
        ),
        pytest.param(
            lambda p: p["planning"]["cost_comparison"]["offers"][0]["lines"][0].update(currency="USD"),
            id="mixed-currency-line",
        ),
        pytest.param(
            lambda p: p["planning"]["pilot_evaluation"].update(status="APPROVED"),
            id="pilot-approval-forgery",
        ),
        pytest.param(
            lambda p: p["planning"]["pilot_evaluation"]["baseline"].update(sample_size=True),
            id="bool-sample-size",
        ),
        pytest.param(
            lambda p: p["planning"]["pilot_evaluation"].update(comparable="true"),
            id="string-comparability",
        ),
        pytest.param(lambda p: p["planning"].update(task_practice="completed"), id="task-string"),
        pytest.param(
            lambda p: p["planning"]["task_practice"].update(template_id="unavailable-template"),
            id="unavailable-template",
        ),
        pytest.param(
            lambda p: p["planning"]["task_practice"].update(checked_steps=["source_facts", "source_facts"]),
            id="duplicate-task-check",
        ),
        pytest.param(
            lambda p: p["planning"]["task_practice"].update(checked_steps=["claim_scope"]),
            id="another-template-check",
        ),
        pytest.param(
            lambda p: p["planning"]["task_practice"].update(approved=True), id="task-approval-forgery"
        ),
        pytest.param(
            lambda p: p["planning"]["task_practice"].update(draft="x" * 2501), id="oversize-task-draft"
        ),
        pytest.param(
            lambda p: p.update(content_versions={"practice": "forged-version"}), id="client-version-forgery"
        ),
    ],
)
def test_invalid_nested_snapshot_is_refused_before_any_save_or_receipt(engine, edit):
    api, db = engine
    data = planning_plan()
    edit(data)
    with pytest.raises(DomainError) as invalid:
        api.save(None, "synthetic-tenant", request(data), str(uuid4()))
    assert invalid.value.status == 422
    assert not db.objects and not db.revisions and not db.events and not db.receipts


def test_planning_snapshot_round_trip_retains_raw_inputs_nulls_checks_and_server_practice_version(engine):
    api, db = engine
    body = request(planning_plan())
    before = deepcopy(body)
    receipt = api.save(None, "synthetic-tenant", body, str(uuid4()))
    saved = api.get(None, "synthetic-tenant", receipt["object_id"])
    assert body == before
    assert json.loads(json.dumps(saved["data"]["planning"])) == before["data"]["planning"]
    assert saved["data"]["planning"]["cost_comparison"]["offers"][0]["lines"][1]["unit_amount"] is None
    assert saved["data"]["content_versions"] == {
        "catalog": module.CATALOG_VERSION,
        "solutions": module.SOLUTIONS_VERSION,
        "practice": practice_module.CONTENT_VERSION,
    }
    assert saved["data"]["learning_completed"] == ["foundations:safe-practice-task"]
    assert saved["business_state"] == "Draft"
    saved["data"]["planning"]["task_practice"]["checked_steps"].clear()
    assert (
        api.get(None, "synthetic-tenant", receipt["object_id"])["data"]["planning"]
        == before["data"]["planning"]
    )
    assert len(db.revisions) == len(db.events) == len(db.receipts) == 1


def test_only_a_nonnull_task_snapshot_stamps_the_server_practice_version(engine):
    api, _ = engine
    data = planning_plan()
    data["planning"]["task_practice"] = None
    receipt = api.save(None, "synthetic-tenant", request(data), str(uuid4()))
    stored = api.get(None, "synthetic-tenant", receipt["object_id"])["data"]
    assert stored["planning"] == data["planning"]
    assert set(stored["content_versions"]) == {"catalog", "solutions"}


def test_legacy_update_retains_optional_snapshots_and_their_original_practice_edition(engine, monkeypatch):
    api, db = engine
    created = api.save(None, "synthetic-tenant", request(planning_plan()), str(uuid4()))
    original = deepcopy(api.get(None, "synthetic-tenant", created["object_id"])["data"])
    monkeypatch.setattr(practice_module, "CONTENT_VERSION", "later-practice-version")
    legacy = {**plan(), "title": "Edited by a six-field client"}
    command = request(legacy, created["revision_id"])
    updated = api.save(None, "synthetic-tenant", command, str(uuid4()), created["object_id"])
    assert api.save(None, "synthetic-tenant", command, str(uuid4()), created["object_id"]) == updated
    stored = api.get(None, "synthetic-tenant", created["object_id"])["data"]
    assert stored["title"] == legacy["title"]
    assert stored["planning"] == original["planning"]
    assert stored["content_versions"]["practice"] == original["content_versions"]["practice"]
    assert db.revisions[0]["payload"] == original
    assert len(db.revisions) == len(db.events) == len(db.receipts) == 2


def test_explicit_null_members_clear_optional_inputs_without_changing_the_old_revision(engine):
    api, db = engine
    created = api.save(None, "synthetic-tenant", request(planning_plan()), str(uuid4()))
    original = deepcopy(db.revisions[0])
    cleared = {
        **plan(),
        "planning": {"cost_comparison": None, "pilot_evaluation": None, "task_practice": None},
    }
    api.save(
        None, "synthetic-tenant", request(cleared, created["revision_id"]), str(uuid4()), created["object_id"]
    )
    stored = api.get(None, "synthetic-tenant", created["object_id"])["data"]
    assert stored["planning"] == cleared["planning"]
    assert "practice" not in stored["content_versions"]
    assert db.revisions[0] == original
    assert len(db.revisions) == len(db.events) == len(db.receipts) == 2


def test_exact_snapshot_replay_precedes_new_content_validation_and_never_restamps_versions(
    engine, monkeypatch
):
    api, db = engine
    body = request(planning_plan())
    first = api.save(None, "synthetic-tenant", body, str(uuid4()))
    original = deepcopy(db.revisions)
    monkeypatch.setattr(practice_module, "CONTENT_VERSION", "later-practice-version")

    def changed_validator(_):
        raise AssertionError("An exact receipt replay must not revalidate a historical task snapshot")

    monkeypatch.setattr(practice_module, "validate_task_practice", changed_validator)
    assert api.save(None, "synthetic-tenant", body, str(uuid4())) == first
    assert db.revisions == original and len(db.revisions) == len(db.events) == len(db.receipts) == 1


@pytest.mark.parametrize("field", ["cost_comparison", "pilot_evaluation", "task_practice"])
def test_changed_nested_input_under_the_same_operation_conflicts_without_rewriting_the_original(
    engine, field
):
    api, db = engine
    body = request(planning_plan())
    api.save(None, "synthetic-tenant", body, str(uuid4()))
    original = deepcopy(db.revisions)
    changed = deepcopy(body)
    edits = {
        "cost_comparison": lambda value: value["offers"][0]["lines"][0].update(unit_amount="0.0040"),
        "pilot_evaluation": lambda value: value["baseline"].update(total_drafting_minutes="100.0"),
        "task_practice": lambda value: value.update(review_notes="Changed synthetic reviewer intent"),
    }
    edits[field](changed["data"]["planning"][field])
    with pytest.raises(DomainError) as conflict:
        api.save(None, "synthetic-tenant", changed, str(uuid4()))
    assert conflict.value.code == "CONFLICT_OPERATION"
    assert db.revisions == original and len(db.revisions) == len(db.events) == len(db.receipts) == 1


@pytest.mark.parametrize("permission", ["allow_read", "allow_write"])
def test_nested_snapshot_receipt_still_requires_current_read_and_management_authority(engine, permission):
    api, db = engine
    body = request(planning_plan())
    api.save(None, "synthetic-tenant", body, str(uuid4()))
    setattr(db, permission, False)
    with pytest.raises(DomainError) as refused:
        api.save(None, "synthetic-tenant", body, str(uuid4()))
    assert refused.value.status == 404
    assert len(db.revisions) == len(db.events) == len(db.receipts) == 1


def test_planning_edits_create_a_revision_and_stale_changes_do_not_alter_history(engine):
    api, db = engine
    original_data = planning_plan()
    first = api.save(None, "synthetic-tenant", request(original_data), str(uuid4()))
    update_data = deepcopy(original_data)
    update_data["planning"]["cost_comparison"]["offers"][0]["lines"][1]["unit_amount"] = "40"
    update_data["planning"]["task_practice"]["checked_steps"].append("missing_information")
    update = request(update_data, first["revision_id"])
    second = api.save(None, "synthetic-tenant", update, str(uuid4()), first["object_id"])
    assert api.save(None, "synthetic-tenant", update, str(uuid4()), first["object_id"]) == second
    with pytest.raises(DomainError) as stale:
        api.save(
            None,
            "synthetic-tenant",
            request(original_data, first["revision_id"]),
            str(uuid4()),
            first["object_id"],
        )
    assert stale.value.code == "CONFLICT_VERSION"
    assert db.revisions[0]["payload"]["planning"] == original_data["planning"]
    assert db.revisions[1]["payload"]["planning"] == update_data["planning"]
    assert len(db.revisions) == len(db.events) == len(db.receipts) == 2


def test_reading_an_old_plan_does_not_backfill_inputs_or_mutate_its_revision(engine):
    api, db = engine
    first = api.save(None, "synthetic-tenant", request(plan()), str(uuid4()))
    before = deepcopy(db.revisions)
    saved = api.get(None, "synthetic-tenant", first["object_id"])
    assert "planning" not in saved["data"] and "practice" not in saved["data"]["content_versions"]
    assert db.revisions == before and len(db.revisions) == len(db.events) == len(db.receipts) == 1
