"""Immutable guidance and preservation regressions; synthetic transaction model, no provider."""

from copy import deepcopy
from uuid import uuid4

import pytest

import impact_api.ai_adoption_plans as plans
import impact_api.ai_content_archives as archives
import impact_api.ai_task_practice as practice
from impact_api.domain import DomainError
from impact_api.store import hash_data
from test_ai_adoption_plans import engine as engine
from test_ai_adoption_plans import plan, request
from test_ai_planning_inputs import planning_plan


def guidance(api, receipt, tenant="synthetic-tenant"):
    return api.guidance(None, tenant, receipt["object_id"], receipt["revision_id"])


def test_new_revision_captures_exact_server_guidance_and_learning_with_no_private_plan_inputs(engine):
    api, db = engine
    data = plan()
    data["profile"]["goal"] = "synthetic-private-marker-123"
    first = api.save(None, "synthetic-tenant", request(data), str(uuid4()))
    result = guidance(api, first)
    assert result["status"] == "COMPLETE"
    assert result["catalog"]["payload"] == archives.catalog()
    assert result["solutions"]["payload"] == archives.solutions_catalog()
    assert result["practice"]["payload"] == archives.task_templates()
    assert sum(len(path["lessons"]) for path in result["catalog"]["payload"]["learning_paths"]) == 12
    row = next(iter(db.content_snapshots.values()))
    assert result["snapshot_sha256"] == hash_data(row["payload"]).hex()
    assert b"synthetic-private-marker-123" not in archives.canonical(row["payload"])
    assert len(db.content_bindings) == len(db.content_snapshots) == 1
    assert api.get(None, "synthetic-tenant", first["object_id"])["content_compatibility"][
        "historical_snapshots_available"
    ]


def test_current_guide_change_creates_a_distinct_archive_without_rewriting_saved_wording(engine, monkeypatch):
    api, db = engine
    first = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    original = guidance(api, first)
    later = archives.catalog()
    later["content_version"] = "synthetic-catalog-v-next"
    later["learning_paths"][0]["lessons"][0]["title"] = "Changed synthetic wording"
    monkeypatch.setattr(archives, "catalog", lambda: deepcopy(later))
    monkeypatch.setattr(plans, "CATALOG_VERSION", later["content_version"])
    second = api.save(
        None, "synthetic-tenant", request(plan(), first["revision_id"]), str(uuid4()), first["object_id"]
    )
    assert guidance(api, first) == original
    current = guidance(api, second)
    assert current["catalog"]["payload"] == later
    assert current["snapshot_sha256"] != original["snapshot_sha256"]
    assert len(db.content_snapshots) == len(db.content_bindings) == len(db.revisions) == 2
    current["catalog"]["payload"]["learning_paths"].clear()
    assert guidance(api, first) == original and guidance(api, second)["catalog"]["payload"] == later


def test_exact_receipt_retry_precedes_any_new_archive_generation(engine, monkeypatch):
    api, db = engine
    body = request()
    first = api.save(None, "synthetic-tenant", body, str(uuid4()))

    def trap(*args):
        raise AssertionError("An exact retry must not capture current guides")

    monkeypatch.setattr(archives, "capture", trap)
    monkeypatch.setattr(archives, "catalog", trap)
    assert api.save(None, "synthetic-tenant", body, str(uuid4())) == first
    assert len(db.content_snapshots) == len(db.content_bindings) == len(db.revisions) == 1


def test_identical_server_content_is_deduplicated_only_inside_the_same_tenant(engine):
    api, db = engine
    one = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    two = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    foreign = api.save(None, "different-tenant", request(), str(uuid4()))
    assert one["object_id"] != two["object_id"]
    assert (
        guidance(api, one)["snapshot_sha256"] == guidance(api, foreign, "different-tenant")["snapshot_sha256"]
    )
    assert (
        db.content_bindings["synthetic-tenant", one["object_id"], one["revision_id"]]
        == db.content_bindings["synthetic-tenant", two["object_id"], two["revision_id"]]
    )
    assert len(db.content_snapshots) == 2 and len(db.content_bindings) == 3


def test_pre_upgrade_revision_without_binding_is_explicitly_unavailable_and_never_backfilled(engine):
    api, db = engine
    receipt = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    db.content_bindings.clear()
    before = deepcopy(db.revisions)
    result = guidance(api, receipt)
    assert result["status"] == "UNAVAILABLE"
    assert result["snapshot_schema_version"] is result["captured_at"] is result["snapshot_sha256"] is None
    assert all(
        result[name]["status"] == "UNAVAILABLE" and result[name]["payload"] is None
        for name in archives.COMPONENTS
    )
    assert not api.get(None, "synthetic-tenant", receipt["object_id"])["content_compatibility"][
        "historical_snapshots_available"
    ]
    assert db.revisions == before and not db.content_bindings


def test_legacy_omitted_practice_with_unknown_old_edition_preserves_source_without_false_archive(engine):
    api, db = engine
    receipt = api.save(None, "synthetic-tenant", request(planning_plan()), str(uuid4()))
    current = db.objects["synthetic-tenant", receipt["object_id"]]
    current["payload"]["content_versions"]["practice"] = "unknown-before-upgrade"
    db.content_bindings.clear()
    retained = deepcopy(current["payload"]["planning"])
    second = api.save(
        None, "synthetic-tenant", request(plan(), receipt["revision_id"]), str(uuid4()), receipt["object_id"]
    )
    result = guidance(api, second)
    assert result["status"] == "PARTIAL"
    assert result["practice"] == {
        "status": "UNAVAILABLE",
        "content_version": "unknown-before-upgrade",
        "payload": None,
    }
    saved = api.get(None, "synthetic-tenant", receipt["object_id"])
    assert saved["data"]["planning"] == retained
    assert saved["data"]["content_versions"]["practice"] == "unknown-before-upgrade"
    assert not saved["content_compatibility"]["historical_snapshots_available"]


def test_legacy_omission_reuses_only_a_real_matching_archived_practice_edition(engine, monkeypatch):
    api, db = engine
    first = api.save(None, "synthetic-tenant", request(planning_plan()), str(uuid4()))
    original = guidance(api, first)
    later = archives.task_templates()
    later["content_version"] = "synthetic-practice-v-next"
    later["templates"][0]["title"] = "Changed synthetic task wording"
    monkeypatch.setattr(archives, "task_templates", lambda: deepcopy(later))
    monkeypatch.setattr(practice, "CONTENT_VERSION", later["content_version"])
    second = api.save(
        None, "synthetic-tenant", request(plan(), first["revision_id"]), str(uuid4()), first["object_id"]
    )
    result = guidance(api, second)
    assert result["status"] == "COMPLETE"
    assert result["practice"] == original["practice"]
    assert result["snapshot_sha256"] == original["snapshot_sha256"]
    assert len(db.content_snapshots) == 1 and len(db.content_bindings) == 2
    third = api.save(
        None,
        "synthetic-tenant",
        request(planning_plan(), second["revision_id"]),
        str(uuid4()),
        first["object_id"],
    )
    assert guidance(api, third)["practice"]["payload"] == later
    assert guidance(api, first) == original


def test_guidance_read_requires_current_read_scope_and_the_revision_belongs_to_that_plan(engine):
    api, _ = engine
    first = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    second = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    with pytest.raises(DomainError) as wrong:
        api.guidance(None, "synthetic-tenant", first["object_id"], second["revision_id"])
    assert wrong.value.status == 404
    with pytest.raises(DomainError) as foreign:
        guidance(api, first, "different-tenant")
    assert foreign.value.status == 404


def test_read_only_can_inspect_guidance_but_revocation_hides_saved_words(engine):
    api, db = engine
    receipt = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    db.allow_write = False
    assert guidance(api, receipt)["status"] == "COMPLETE"
    db.allow_read = False
    with pytest.raises(DomainError) as denied:
        guidance(api, receipt)
    assert denied.value.status == 404


@pytest.mark.parametrize("change", ["hash", "payload", "schema"])
def test_corrupt_or_unknown_archive_fails_closed_without_reconstructing_current_content(engine, change):
    api, db = engine
    receipt = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    row = next(iter(db.content_snapshots.values()))
    if change == "hash":
        row["payload_sha256"] = b"x" * 32
    elif change == "schema":
        row["schema_version"] = "unknown-format"
    else:
        row["payload"]["catalog"]["learning_paths"][0]["lessons"][0]["title"] = "Tampered wording"
    with pytest.raises(DomainError) as denied:
        guidance(api, receipt)
    assert denied.value.status == 503 and denied.value.reason == "AI_GUIDANCE_UNREADABLE"
    with pytest.raises(DomainError) as history_denied:
        api.history(None, "synthetic-tenant", receipt["object_id"])
    assert history_denied.value.status == 503 and history_denied.value.reason == "AI_GUIDANCE_UNREADABLE"
    with pytest.raises(DomainError) as listing_denied:
        api.listing(None, "synthetic-tenant")
    assert listing_denied.value.status == 503 and listing_denied.value.reason == "AI_GUIDANCE_UNREADABLE"


def test_archive_capture_failure_rolls_back_the_whole_new_revision(engine, monkeypatch):
    api, db = engine
    malformed = archives.catalog()
    malformed["forged_approval"] = True
    monkeypatch.setattr(archives, "catalog", lambda: malformed)
    with pytest.raises(DomainError) as denied:
        api.save(None, "synthetic-tenant", request(), str(uuid4()))
    assert denied.value.status == 503
    assert not db.objects and not db.revisions and not db.events and not db.receipts
    assert not db.content_snapshots and not db.content_bindings


@pytest.mark.parametrize("name", ["catalog", "solutions", "practice"])
def test_changed_wording_under_an_existing_edition_is_refused_atomically(engine, monkeypatch, name):
    api, db = engine
    first = api.save(None, "synthetic-tenant", request(planning_plan()), str(uuid4()))
    original = guidance(api, first)
    getter = {"catalog": "catalog", "solutions": "solutions_catalog", "practice": "task_templates"}[name]
    changed = deepcopy(getattr(archives, getter)())
    if name == "catalog":
        changed["learning_paths"][0]["lessons"][0]["title"] = "Changed without a new edition"
    elif name == "solutions":
        changed["explanation"] = "Changed without a new edition"
    else:
        changed["templates"][0]["title"] = "Changed without a new edition"
    monkeypatch.setattr(archives, getter, lambda: deepcopy(changed))
    before = deepcopy(
        (db.objects, db.revisions, db.events, db.receipts, db.content_snapshots, db.content_bindings)
    )
    with pytest.raises(DomainError) as refused:
        api.save(
            None,
            "synthetic-tenant",
            request(planning_plan(), first["revision_id"]),
            str(uuid4()),
            first["object_id"],
        )
    assert refused.value.status == 503 and refused.value.reason == "AI_GUIDANCE_VERSION_CHANGED"
    assert (
        db.objects,
        db.revisions,
        db.events,
        db.receipts,
        db.content_snapshots,
        db.content_bindings,
    ) == before
    assert guidance(api, first) == original


@pytest.mark.parametrize("limit", [0, 101, True, "10"])
def test_revision_history_bounds_fail_before_database_read(engine, limit):
    api, db = engine
    with pytest.raises(DomainError) as denied:
        api.history(None, "synthetic-tenant", str(uuid4()), limit)
    assert denied.value.status == 422 and not db.objects
