"""Offline draft validation, receipt replay and current-authority checks."""

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

import impact_api.ai_adoption_plans as module
import impact_api.ai_learning_content as learning_module
from impact_api.ai_adoption_plans import AIAdoptionPlans, learning_keys, validate_plan
from impact_api.ai_solutions_catalog import SOLUTION_IDS
from impact_api.domain import DomainError


def plan():
    return {
        "title": "Synthetic public newsletter pilot",
        "profile": {
            "sector": "GENERAL",
            "team_size": 8,
            "goal": "Draft a public newsletter",
            "data_readiness": "BASIC",
            "ai_experience": "EXPERIMENTING",
            "sensitive_data": False,
        },
        "solution_ids": [sorted(SOLUTION_IDS)[0]],
        "learning_completed": ["foundations:0"],
        "procurement": {
            "requirements": "Human review and source links",
            "data_boundary": "Synthetic examples only",
            "budget_notes": "Ask for a written offer",
            "vendor_questions": "How do we export and delete our data?",
        },
        "pilot": {"success_measure": "Every sampled claim verified", "completed_actions": ["DEFINE_GOAL"]},
    }


@pytest.mark.parametrize(
    "edit",
    [
        lambda p: p.update(approved=True),
        lambda p: p.update(content_versions={"catalog": "forged"}),
        lambda p: p.update(title=" "),
        lambda p: p.update(title="x" * 151),
        lambda p: p["profile"].update(team_size=True),
        lambda p: p.update(solution_ids=["unknown"]),
        lambda p: p.update(solution_ids=[sorted(SOLUTION_IDS)[0]] * 2),
        lambda p: p.update(solution_ids=sorted(SOLUTION_IDS)[:5]),
        lambda p: p.update(learning_completed=["foundations:99"]),
        lambda p: p.update(learning_completed=["foundations:0"] * 2),
        lambda p: p.update(learning_completed=["foundations:0", "foundations:safe-practice-task"]),
        lambda p: p["procurement"].update(budget_notes="x" * 501),
        lambda p: p["procurement"].update(award=True),
        lambda p: p["pilot"].update(completed_actions=["AUTOMATIC_DEPLOY"]),
        lambda p: p["pilot"].update(completed_actions=["DEFINE_GOAL"] * 2),
        lambda p: p["pilot"].update(success_measure="x" * 1001),
        lambda p: p["pilot"].update(approved=True),
    ],
)
def test_closed_draft_refuses_unknown_ids_duplicate_actions_and_unbounded_notes(edit):
    data = plan()
    edit(data)
    with pytest.raises(DomainError) as denied:
        validate_plan(data)
    assert denied.value.status == 422


def test_valid_early_draft_allows_an_empty_shortlist_without_certifying_completion():
    data = plan()
    data["solution_ids"] = []
    data["learning_completed"] = []
    data["pilot"]["completed_actions"] = []
    before = deepcopy(data)
    validate_plan(data)
    assert data == before and len(learning_keys()) == 12


class Rows:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.row


class Database:
    def __init__(self):
        self.receipts, self.objects, self.revisions, self.events = {}, {}, [], []
        self.principal = "synthetic-principal"
        self.allow_read = self.allow_write = True
        self.locked = False

    @contextmanager
    def transaction(self, tenant):
        self.locked = False
        yield self

    def execute(self, sql, values):
        if "pg_advisory_xact_lock" in sql:
            self.locked = True
            return Rows(None)
        if sql.startswith("SELECT * FROM impact.operation_receipt"):
            return Rows(self.receipts.get(tuple(values)))
        if sql.startswith("SELECT count(*)"):
            return Rows({"n": len(self.objects)})
        if sql.startswith("SELECT r.*,v.payload"):
            tenant, kind, limit = values
            rows = sorted(
                [
                    row
                    for (scope, _), row in self.objects.items()
                    if scope == tenant and row["object_type"] == kind
                ],
                key=lambda row: row["object_id"],
            )
            return Rows(rows[:limit])
        if sql.startswith("INSERT INTO impact.operation_receipt"):
            tenant, actor, command, operation, fingerprint, receipt, expiry = values
            key = (tenant, actor, command, operation)
            assert key not in self.receipts
            self.receipts[key] = {
                "payload_hash": fingerprint,
                "outcome": deepcopy(receipt.obj),
                "expires_at": expiry,
            }
            return Rows(None)
        raise AssertionError(sql)


@pytest.fixture
def engine(monkeypatch):
    db = Database()

    def ctx(c, identity, tenant, write=False):
        if write:
            assert c.locked, "Tenant write lock precedes authority resolution"
        return SimpleNamespace(
            tenant_id=tenant,
            principal_id=db.principal,
            grants=[{"capability": module.READ_CAP, "purpose": None}],
        )

    def permission(c, context, operation, object_id=None, hidden=False):
        if not db.allow_read or (operation.startswith(("create_", "update_")) and not db.allow_write):
            raise DomainError("RESOURCE_UNAVAILABLE", 404)

    def get(c, context, obj, kind=None, capability=None, lock=False):
        row = db.objects.get((context.tenant_id, obj))
        if not row or (kind and row["object_type"] != kind):
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return row

    def save(c, context, kind, payload, state, previous=None):
        obj, revision = str(previous["object_id"]) if previous else str(uuid4()), str(uuid4())
        db.objects[context.tenant_id, obj] = {
            "object_id": obj,
            "head_revision": revision,
            "object_type": kind,
            "payload": deepcopy(payload),
            "lifecycle_state": state,
        }
        db.revisions.append(deepcopy(db.objects[context.tenant_id, obj]))
        return {
            "object_id": obj,
            "revision_id": revision,
            "business_state": state,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

    monkeypatch.setattr(module, "context", ctx)
    monkeypatch.setattr(module, "authorize", permission)
    monkeypatch.setattr(module, "load", get)
    monkeypatch.setattr(module, "write", save)
    monkeypatch.setattr(module, "audit", lambda c, context, op, receipt, correlation: db.events.append(op))
    monkeypatch.setattr(module, "visible_sql", lambda context, capability: ("TRUE", []))
    service = SimpleNamespace(
        db=db,
        cursor_binding=lambda context, route: (context.tenant_id, route),
        cursor_key=lambda bound, cursor: None,
        next_cursor=lambda bound, key: "synthetic-cursor",
    )
    return AIAdoptionPlans(service), db


def request(data=None, expected=None):
    return {
        "operation_id": str(uuid4()),
        "data": data or plan(),
        **({"expected_revision": expected} if expected else {}),
    }


def test_exact_replay_retains_server_versions_and_writes_once_after_catalogue_update(engine, monkeypatch):
    api, db = engine
    body = request()
    original = api.save(None, "synthetic-tenant", body, str(uuid4()))
    pinned = api.get(None, "synthetic-tenant", original["object_id"])["data"]["content_versions"]
    monkeypatch.setattr(module, "CATALOG_VERSION", "later-catalogue")
    monkeypatch.setattr(module, "SOLUTION_IDS", frozenset())
    assert api.save(None, "synthetic-tenant", body, str(uuid4())) == original
    assert len(db.revisions) == len(db.events) == len(db.receipts) == 1
    assert pinned["catalog"] != "later-catalogue"


def test_changed_payload_conflicts_without_an_extra_revision(engine):
    api, db = engine
    body = request()
    api.save(None, "synthetic-tenant", body, str(uuid4()))
    changed = {**body, "data": {**body["data"], "title": "Changed intent"}}
    with pytest.raises(DomainError) as conflict:
        api.save(None, "synthetic-tenant", changed, str(uuid4()))
    assert conflict.value.code == "CONFLICT_OPERATION" and len(db.revisions) == 1


def test_stale_update_refused_old_revision_retained_and_exact_update_replays(engine):
    api, db = engine
    original = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    body = request({**plan(), "title": "Reviewed pilot scope"}, original["revision_id"])
    updated = api.save(None, "synthetic-tenant", body, str(uuid4()), original["object_id"])
    assert api.save(None, "synthetic-tenant", body, str(uuid4()), original["object_id"]) == updated
    with pytest.raises(DomainError) as stale:
        api.save(
            None,
            "synthetic-tenant",
            request(plan(), original["revision_id"]),
            str(uuid4()),
            original["object_id"],
        )
    assert stale.value.code == "CONFLICT_VERSION"
    assert len(db.revisions) == 2 and db.revisions[0]["payload"]["title"] == plan()["title"]
    assert api.get(None, "synthetic-tenant", original["object_id"])["business_state"] == "Draft"


@pytest.mark.parametrize("permission", ["allow_read", "allow_write"])
def test_receipt_never_bypasses_current_authority(engine, permission):
    api, db = engine
    body = request()
    api.save(None, "synthetic-tenant", body, str(uuid4()))
    setattr(db, permission, False)
    with pytest.raises(DomainError) as denied:
        api.save(None, "synthetic-tenant", body, str(uuid4()))
    assert denied.value.status == 404 and len(db.revisions) == 1


def test_expired_receipt_is_not_a_new_save(engine):
    api, db = engine
    body = request()
    api.save(None, "synthetic-tenant", body, str(uuid4()))
    next(iter(db.receipts.values()))["expires_at"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    with pytest.raises(DomainError) as conflict:
        api.save(None, "synthetic-tenant", body, str(uuid4()))
    assert conflict.value.code == "IDEMPOTENCY_EXPIRED" and len(db.revisions) == 1


def test_tenant_selector_and_wrong_kind_are_hidden(engine):
    api, db = engine
    original = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    with pytest.raises(DomainError) as hidden:
        api.get(None, "another-tenant", original["object_id"])
    assert hidden.value.status == 404
    db.objects["synthetic-tenant", original["object_id"]]["object_type"] = "Programme"
    with pytest.raises(DomainError) as wrong_kind:
        api.save(
            None,
            "synthetic-tenant",
            request(plan(), original["revision_id"]),
            str(uuid4()),
            original["object_id"],
        )
    assert wrong_kind.value.status == 404 and len(db.revisions) == 1


def test_receipts_are_scoped_to_current_principal(engine):
    api, db = engine
    body = request()
    first = api.save(None, "synthetic-tenant", body, str(uuid4()))
    db.principal = "different-synthetic-principal"
    second = api.save(None, "synthetic-tenant", body, str(uuid4()))
    assert first["object_id"] != second["object_id"] and len(db.receipts) == 2


@pytest.mark.parametrize("limit", [0, 101, True, "10"])
def test_list_page_bound_is_enforced_before_database_access(engine, limit):
    api, _ = engine
    with pytest.raises(DomainError) as invalid:
        api.listing(None, "synthetic-tenant", limit)
    assert invalid.value.status == 422


def test_new_save_canonicalizes_known_aliases_without_changing_the_submitted_command(engine):
    api, db = engine
    body = request()
    body["data"]["learning_completed"] = ["foundations:0", "procurement:whole-cost-and-exit"]
    before = deepcopy(body)
    receipt = api.save(None, "synthetic-tenant", body, str(uuid4()))
    saved = api.get(None, "synthetic-tenant", receipt["object_id"])
    assert body == before
    assert saved["data"]["learning_completed"] == [
        "foundations:safe-practice-task",
        "procurement:whole-cost-and-exit",
    ]
    assert saved["content_compatibility"] == {
        "current_versions": {"catalog": module.CATALOG_VERSION, "solutions": module.SOLUTIONS_VERSION},
        "catalog_version_status": "CURRENT",
        "solutions_version_status": "CURRENT",
        "learning_completed": saved["data"]["learning_completed"],
        "legacy_learning_keys": [],
        "unavailable_learning_keys": [],
        "historical_snapshots_available": False,
    }
    assert len(db.revisions) == 1


def test_alias_and_stable_key_are_distinct_retry_payloads_even_for_the_same_lesson(engine):
    api, db = engine
    body = request()
    api.save(None, "synthetic-tenant", body, str(uuid4()))
    changed = deepcopy(body)
    changed["data"]["learning_completed"] = ["foundations:safe-practice-task"]
    with pytest.raises(DomainError) as conflict:
        api.save(None, "synthetic-tenant", changed, str(uuid4()))
    assert conflict.value.code == "CONFLICT_OPERATION" and len(db.revisions) == 1


def test_legacy_revision_reads_and_lists_interpret_progress_without_rewriting_history(engine):
    api, db = engine
    receipt = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    row = db.objects["synthetic-tenant", receipt["object_id"]]
    # A synthetic pre-upgrade saved revision, including an identifier no longer available.
    row["payload"]["learning_completed"] = ["foundations:0", "retired:unavailable-lesson"]
    row["payload"]["content_versions"] = {"catalog": "previous-catalog", "solutions": "previous-solutions"}
    before = deepcopy(row)
    result = api.get(None, "synthetic-tenant", receipt["object_id"])
    assert api.listing(None, "synthetic-tenant")["items"] == [result]
    assert result["data"] == before["payload"] and row == before
    assert result["content_compatibility"] == {
        "current_versions": {"catalog": module.CATALOG_VERSION, "solutions": module.SOLUTIONS_VERSION},
        "catalog_version_status": "STALE",
        "solutions_version_status": "STALE",
        "learning_completed": ["foundations:safe-practice-task"],
        "legacy_learning_keys": ["foundations:0"],
        "unavailable_learning_keys": ["retired:unavailable-lesson"],
        "historical_snapshots_available": False,
    }
    result["data"]["learning_completed"].clear()
    result["content_compatibility"]["learning_completed"].clear()
    assert row == before and len(db.revisions) == 1


@pytest.mark.parametrize("saved_versions", [None, {}, {"catalog": "", "solutions": 12}])
def test_unknown_saved_versions_are_explicit_without_claiming_a_historical_snapshot(engine, saved_versions):
    api, db = engine
    receipt = api.save(None, "synthetic-tenant", request(), str(uuid4()))
    row = db.objects["synthetic-tenant", receipt["object_id"]]
    row["payload"]["content_versions"] = saved_versions
    compatibility = api.get(None, "synthetic-tenant", receipt["object_id"])["content_compatibility"]
    assert compatibility["catalog_version_status"] == compatibility["solutions_version_status"] == "UNKNOWN"
    assert compatibility["historical_snapshots_available"] is False


def test_exact_legacy_receipt_replays_before_any_learning_interpretation(engine, monkeypatch):
    api, db = engine
    body = request()
    original = api.save(None, "synthetic-tenant", body, str(uuid4()))
    row = db.objects["synthetic-tenant", original["object_id"]]
    row["payload"]["learning_completed"] = ["foundations:0"]
    row["payload"]["content_versions"]["catalog"] = "pre-upgrade-catalog"
    before = deepcopy(row)

    def cannot_interpret(key):
        raise AssertionError("A receipt retry must not reinterpret progress")

    monkeypatch.setattr(module, "canonical_lesson_key", cannot_interpret)
    assert api.save(None, "synthetic-tenant", body, str(uuid4())) == original
    assert row == before and len(db.revisions) == len(db.events) == len(db.receipts) == 1


def test_new_save_refuses_unavailable_legacy_content_without_reassigning_its_meaning(engine, monkeypatch):
    api, db = engine
    lessons = deepcopy(learning_module._LESSONS)
    lessons["foundations"].pop(0)
    monkeypatch.setattr(learning_module, "_LESSONS", lessons)
    with pytest.raises(DomainError) as denied:
        api.save(None, "synthetic-tenant", request(), str(uuid4()))
    assert denied.value.status == 422
    assert not db.revisions and not db.receipts and not db.events
