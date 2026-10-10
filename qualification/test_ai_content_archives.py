"""Immutable guidance and preservation regressions; synthetic transaction model, no provider."""

from contextlib import contextmanager
from copy import deepcopy
import hashlib
from pathlib import Path
from uuid import uuid4

import pytest

import impact_api.ai_adoption_plans as plans
import impact_api.ai_content_archives as archives
import impact_api.ai_task_practice as practice
from impact_api.ai_solutions_catalog import (
    CATEGORIES,
    catalog_schema,
    solutions_catalog as published_solutions,
)
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


# US-DC-04: archive edition v2 (commercial disclosures) beside the retained v1 reader

V1_SCHEMA_FILE_SHA256 = "248434d7ddb31bdb76508b673ffc26c517f68a3fc46565856d556bc9f458994c"
# The solutions edition that build 0.38.0 archived under guidance v1, as recorded before US-DC-04.
V1_SOLUTIONS_EDITION = "nonprofit-solutions-2026-10-05.1"
V1_SOLUTIONS_SHA256 = "7c1b378329293735afb45d1cdf4b33df5fe8346d9545299dc5718ecdad0e38e4"
V1_SOLUTIONS_EXPLANATION = (
    "A source-backed starting list checked on the stated date, not an endorsement, live price feed "
    "or guarantee of eligibility. Use-case mappings are editorial pilot ideas. "
    "Compare evidence and obtain a current quote before choosing a solution."
)


def v1_solutions():
    """Byte-for-byte the solutions component build 0.38.0 archived: today's listings without
    disclosures under the previous edition and explanation (checked against the recorded digest)."""
    edition = published_solutions()
    edition["content_version"] = V1_SOLUTIONS_EDITION
    edition["explanation"] = V1_SOLUTIONS_EXPLANATION
    for listing in edition["solutions"]:
        del listing["commercial_disclosure"]
    assert hash_data(edition).hex() == V1_SOLUTIONS_SHA256
    return edition


@contextmanager
def under_guidance_v1(monkeypatch):
    """Save as build 0.38.0 did: the v1 edition label and the v1 solutions edition, through the real
    capture path. Nothing is fabricated: the archive is written by capture() itself."""
    with monkeypatch.context() as patch:
        patch.setattr(archives, "SCHEMA_VERSION", archives.SCHEMA_V1)
        patch.setattr(archives, "solutions_catalog", v1_solutions)
        patch.setattr(plans, "SOLUTIONS_VERSION", V1_SOLUTIONS_EDITION)
        yield


def test_v1_schema_file_is_frozen_and_v2_adds_only_the_disclosure_and_closed_categories():
    v1_file = Path(archives.__file__).with_name("ai_content_schema_v1.json")
    assert hashlib.sha256(v1_file.read_bytes()).hexdigest() == V1_SCHEMA_FILE_SHA256
    assert archives.SCHEMA_VERSION == archives.SCHEMA_V2 == "nonprofit-ai-guidance-v2"
    assert list(archives.EDITIONS) == list(archives.READERS) == [archives.SCHEMA_V1, archives.SCHEMA_V2]
    v1, v2 = archives.EDITIONS[archives.SCHEMA_V1], archives.EDITIONS[archives.SCHEMA_V2]
    assert v2["catalog"] == v1["catalog"] and v2["practice"] == v1["practice"]
    # The current published catalogue contract is exactly the archived v2 solutions component.
    assert v2["solutions"] == catalog_schema()
    listing = deepcopy(v2["solutions"]["properties"]["solutions"]["items"])
    del listing["properties"]["commercial_disclosure"]
    listing["required"].remove("commercial_disclosure")
    # v2 closes `category` to the published categories; v1 accepted any text.
    assert listing["properties"]["category"] == {"enum": sorted(CATEGORIES)}
    listing["properties"]["category"] = {"type": "string", "maxLength": 12000}
    reduced = deepcopy(v2["solutions"])
    reduced["properties"]["solutions"]["items"] = listing
    assert reduced == v1["solutions"]


def test_new_revision_is_captured_in_guidance_v2_with_every_listing_disclosure(engine):
    api, db = engine
    receipt = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    row = next(iter(db.content_snapshots.values()))
    assert row["schema_version"] == row["payload"]["schema_version"] == archives.SCHEMA_V2
    result = guidance(api, receipt)
    assert result["status"] == "COMPLETE" and result["snapshot_schema_version"] == archives.SCHEMA_V2
    archived = result["solutions"]["payload"]
    assert archived == archives.solutions_catalog()
    assert archived["content_version"] == "nonprofit-solutions-2026-10-05.2"
    assert len(archived["solutions"]) == 8
    assert all(item["commercial_disclosure"]["status"] == "NONE_KNOWN" for item in archived["solutions"])
    saved = api.get(None, "synthetic-tenant", receipt["object_id"])
    assert saved["data"]["content_versions"]["solutions"] == archived["content_version"]


def test_revisions_saved_under_v1_and_v2_both_load_and_v1_keeps_its_original_words(engine, monkeypatch):
    api, db = engine
    with under_guidance_v1(monkeypatch):
        old = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    new = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    assert sorted(row["schema_version"] for row in db.content_snapshots.values()) == [
        archives.SCHEMA_V1,
        archives.SCHEMA_V2,
    ]
    before = deepcopy(db.content_snapshots)
    first, second = guidance(api, old), guidance(api, new)
    assert first["status"] == second["status"] == "COMPLETE"
    assert first["snapshot_schema_version"] == archives.SCHEMA_V1
    assert second["snapshot_schema_version"] == archives.SCHEMA_V2
    assert hash_data(first["solutions"]["payload"]).hex() == V1_SOLUTIONS_SHA256
    assert not any("commercial_disclosure" in item for item in first["solutions"]["payload"]["solutions"])
    assert all("commercial_disclosure" in item for item in second["solutions"]["payload"]["solutions"])
    assert first["catalog"] == second["catalog"] and first["practice"] == second["practice"]
    # Plans, history and listing read both editions; nothing is rewritten or relabelled.
    for receipt in (old, new):
        assert api.get(None, "synthetic-tenant", receipt["object_id"])["content_compatibility"][
            "historical_snapshots_available"
        ]
        assert api.history(None, "synthetic-tenant", receipt["object_id"])["items"][0][
            "historical_snapshots_available"
        ]
    assert all(
        item["content_compatibility"]["historical_snapshots_available"]
        for item in api.listing(None, "synthetic-tenant")["items"]
    )
    stale = api.get(None, "synthetic-tenant", old["object_id"])["content_compatibility"]
    assert stale["solutions_version_status"] == "STALE"
    assert db.content_snapshots == before


def test_a_saved_revision_keeps_the_disclosure_that_was_current_when_it_was_saved(engine, monkeypatch):
    api, db = engine
    first = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    original = guidance(api, first)
    later = archives.solutions_catalog()
    later["content_version"] = "synthetic-solutions-disclosed-next"
    later["solutions"][0]["commercial_disclosure"] = {
        "status": "DISCLOSED",
        "relationship_types": ["referral_fee"],
        "statement": "Synthetic later edition: a referral fee relationship.",
        "declared_on": "2026-11-01",
        "editorial_confirmation": "CONFIRMED",
    }
    monkeypatch.setattr(archives, "solutions_catalog", lambda: deepcopy(later))
    monkeypatch.setattr(plans, "SOLUTIONS_VERSION", later["content_version"])
    second = api.save(
        None, "synthetic-tenant", request(plan(), first["revision_id"]), str(uuid4()), first["object_id"]
    )
    assert guidance(api, first) == original
    kept = original["solutions"]["payload"]["solutions"][0]["commercial_disclosure"]
    assert kept["status"] == "NONE_KNOWN" and kept["relationship_types"] == []
    assert kept["editorial_confirmation"] == "PENDING"
    current = guidance(api, second)["solutions"]["payload"]["solutions"][0]["commercial_disclosure"]
    assert current == later["solutions"][0]["commercial_disclosure"]
    assert len(db.content_snapshots) == 2


@pytest.mark.parametrize("change", ["missing", "disclosed_without_statement", "disclosed_without_type"])
def test_a_listing_without_a_valid_disclosure_refuses_the_save_atomically(engine, monkeypatch, change):
    import impact_api.ai_solutions_catalog as solutions_module

    api, db = engine
    listings = deepcopy(solutions_module._SOLUTIONS)
    disclosure = listings[1]["commercial_disclosure"]
    if change == "missing":
        del listings[1]["commercial_disclosure"]
    elif change == "disclosed_without_statement":
        disclosure.update(status="DISCLOSED", relationship_types=["reseller"])
        del disclosure["statement"]
    else:
        disclosure.update(status="DISCLOSED")
    monkeypatch.setattr(solutions_module, "_SOLUTIONS", listings)
    with pytest.raises(DomainError) as refused:
        api.save(None, "synthetic-tenant", request(), str(uuid4()))
    assert (refused.value.status, refused.value.reason) == (503, "AI_SOLUTIONS_CATALOG_INVALID")
    assert not db.objects and not db.revisions and not db.events and not db.receipts
    assert not db.content_snapshots and not db.content_bindings


@pytest.mark.parametrize(
    "change",
    ["v2_without_disclosure", "row_v1_payload_v2", "row_v2_payload_v1", "unknown_edition"],
)
def test_an_edition_label_and_its_payload_shape_must_agree_or_the_archive_is_unreadable(
    engine, monkeypatch, change
):
    api, db = engine
    if change == "row_v2_payload_v1":
        with under_guidance_v1(monkeypatch):
            receipt = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    else:
        receipt = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    row = next(iter(db.content_snapshots.values()))
    payload = row["payload"]
    if change == "v2_without_disclosure":
        del payload["solutions"]["solutions"][0]["commercial_disclosure"]
    elif change == "row_v1_payload_v2":
        row["schema_version"] = archives.SCHEMA_V1
    elif change == "row_v2_payload_v1":
        row["schema_version"] = archives.SCHEMA_V2
    else:
        payload["schema_version"] = row["schema_version"] = "nonprofit-ai-guidance-v3"
    # A validly hashed payload: only the edition rules can refuse it.
    row["payload_sha256"] = hash_data(payload)
    with pytest.raises(DomainError) as denied:
        guidance(api, receipt)
    assert (denied.value.status, denied.value.reason) == (503, "AI_GUIDANCE_UNREADABLE")


def test_practice_archived_under_v1_is_reused_in_a_v2_bundle_only_when_identical(engine, monkeypatch):
    api, db = engine
    with under_guidance_v1(monkeypatch):
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
    assert result["snapshot_schema_version"] == archives.SCHEMA_V2
    assert result["status"] == "COMPLETE" and result["practice"] == original["practice"]
    assert guidance(api, first) == original
