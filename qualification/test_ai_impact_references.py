"""Synthetic relationship transactions; core arithmetic is reused without pilot attribution."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from jsonschema import Draft202012Validator
import pytest

import impact_api.ai_content_archives as archives
import impact_api.ai_impact_references as module
from impact_api.ai_impact_reference_contracts import augment
from impact_api.ai_impact_references import AIImpactReferences, validate_input
from impact_api.dashboards import Dashboards, summarize
from impact_api.domain import DomainError
from test_ai_adoption_plans import Rows, engine as engine, request


TENANT = "synthetic-tenant"


def body(receipt, data):
    return {"operation_id": str(uuid4()), "expected_revision": receipt["revision_id"], "data": data}


@pytest.fixture
def linked_engine(engine, monkeypatch):
    plans, db = engine
    db.denied_caps, db.denied_objects = set(), set()
    db.allow_dashboard = True
    db.period_snapshots, db.official_values, db.provisional_values = [], {}, {}

    def add(kind, payload):
        obj, rev = str(uuid4()), str(uuid4())
        row = {
            "object_id": obj,
            "head_revision": rev,
            "revision_id": rev,
            "object_type": kind,
            "payload": deepcopy(payload),
            "lifecycle_state": "Approved",
            "revision_number": 1,
            "tenant_id": TENANT,
            "created_at": datetime.now(timezone.utc),
        }
        db.objects[TENANT, obj] = row
        db.revisions.append(deepcopy(row))
        return row

    calendar = add("ReportingCalendar", {"name": "Synthetic calendar"})
    programme = add(
        "Programme",
        {
            "title": "Synthetic governed programme",
            "reporting_calendar_id": calendar["object_id"],
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2027-01-01T00:00:00Z",
        },
    )
    definition = add(
        "IndicatorDefinition",
        {
            "name": "Verified approved deliveries",
            "unit": "deliveries",
            "measurement_type": "COUNT",
            "combination_rule": "SUM",
            "display_decimals": 2,
        },
    )
    indicator = add(
        "IndicatorInstance",
        {
            "programme_id": programme["object_id"],
            "definition_version": definition["revision_id"],
            "local_applicability": "Synthetic site",
        },
    )
    period = add(
        "Period",
        {
            "code": "2026-Q1",
            "calendar_version": calendar["revision_id"],
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2026-04-01T00:00:00Z",
        },
    )
    fixture = {
        "programme": programme,
        "indicator": indicator,
        "definition": definition,
        "period": period,
        "calendar": calendar,
    }
    data = {name + "_id": fixture[name]["object_id"] for name in ("programme", "indicator", "period")}
    data["interpretation_note"] = "Synthetic evidence for human review; no causal inference."

    def ctx(c, identity, tenant, write=False):
        if write:
            assert c.locked
        return SimpleNamespace(
            tenant_id=tenant,
            principal_id=db.principal,
            grants=[{"capability": "dashboards.read", "purpose": None}] if db.allow_dashboard else [],
        )

    def permission(c, context, operation, obj=None, hidden=False):
        if (
            not db.allow_read
            or (operation == module.SAVE_OPERATION and not db.allow_write)
            or (operation == "programme_dashboard" and not db.allow_dashboard)
        ):
            raise DomainError("RESOURCE_UNAVAILABLE", 404)

    def get(c, context, obj, kind=None, capability=None, lock=False):
        row = db.objects.get((context.tenant_id, str(obj)))
        if (
            not row
            or row["object_type"] != kind
            or capability in db.denied_caps
            or str(obj) in db.denied_objects
        ):
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return row

    def pinned(c, context, rev, kind, capability):
        row = next(
            (
                row
                for row in db.revisions
                if row["tenant_id"] == context.tenant_id
                and row["object_type"] == kind
                and str(row.get("revision_id", row.get("head_revision"))) == str(rev)
            ),
            None,
        )
        if not row:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        get(c, context, row["object_id"], kind, capability)
        return row

    execute = db.execute

    def queries(sql, values):
        if sql.startswith("SELECT b.snapshot_id,b.snapshot_revision"):
            tenant, programme_id, period_id = values[:3]
            rows = [
                row
                for row in db.period_snapshots
                if row["tenant_id"] == tenant
                and row["programme_id"] == programme_id
                and row["period_id"] == period_id
            ]
            if len(values) == 6:
                rows = [
                    row
                    for row in rows
                    if (row["snapshot_id"], row["snapshot_revision"], row["snapshot_version"])
                    == tuple(values[3:])
                ]
            return Rows(max(rows, key=lambda row: row["snapshot_version"], default=None))
        return execute(sql, values)

    monkeypatch.setattr(db, "execute", queries)
    monkeypatch.setattr(module, "context", ctx)
    monkeypatch.setattr(module, "authorize", permission)
    monkeypatch.setattr(module, "load", get)
    monkeypatch.setattr(module, "revision", pinned)
    # Reuse the existing transaction/revision fixture; aliases remain request-bound there.
    import impact_api.ai_adoption_plans as plan_module

    monkeypatch.setattr(module, "write", plan_module.write)
    monkeypatch.setattr(module, "audit", plan_module.audit)
    dashboards = Dashboards(plans.service)

    def official(c, context, snapshot, indicator_id, pin):
        row = db.official_values.get(snapshot["snapshot_id"]) if snapshot else None
        return row if row and row["payload"]["indicator_version"] == pin else None

    dashboards.official = official
    dashboards.provisional = lambda c, context, indicator_id, period_id, pin: (
        db.provisional_values.get((indicator_id, period_id))
        if db.provisional_values.get((indicator_id, period_id), {})
        .get("payload", {})
        .get("indicator_version")
        == pin
        else None
    )
    dashboards.targets = lambda *args: (None, None)
    dashboards.coverage = lambda *args: summarize(None, "CLOSE_SNAPSHOT")
    dashboards.freshness = lambda *args: {
        "stale": False,
        "stale_reasons": [],
        "source_check": "CHECKED",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    plans.service.dashboards = dashboards
    plans.service.periods = SimpleNamespace(state=lambda *args: {"lifecycle_state": "Locked"})

    def snapshot(value="12.345", mode="OFFICIAL"):
        result = add(
            "CalculatedResult",
            {
                "mode": mode,
                "value_state": "PRESENT",
                "value": value,
                "numerator": None,
                "denominator": None,
                "reason_code": None,
                "disaggregation": [],
                "freshness": {"calculated_at": datetime.now(timezone.utc).isoformat()},
                "indicator_version": definition["revision_id"],
            },
        )
        result_row = {
            "result_id": result["object_id"],
            "result_revision": result["revision_id"],
            "payload": result["payload"],
            "created_at": datetime.now(timezone.utc) + timedelta(seconds=1),
        }
        if mode == "PROVISIONAL":
            db.provisional_values[indicator["object_id"], period["object_id"]] = result_row
            return result_row
        snap = add("Snapshot", {"target_versions": []})
        row = {
            "tenant_id": TENANT,
            "programme_id": programme["object_id"],
            "period_id": period["object_id"],
            "snapshot_id": snap["object_id"],
            "snapshot_revision": snap["revision_id"],
            "snapshot_version": len(db.period_snapshots) + 1,
            "close_revision": str(uuid4()),
            "payload": snap["payload"],
            "created_at": datetime.now(timezone.utc),
        }
        db.period_snapshots.append(row)
        db.official_values[snap["object_id"]] = result_row
        return row

    return plans, AIImpactReferences(plans.service, dashboards), db, data, fixture, snapshot


def save_link(fixture):
    plans, api, db, data, core, snapshot = fixture
    original = plans.save(None, TENANT, request(), str(uuid4()))
    linked = api.save(None, TENANT, original["object_id"], body(original, data), str(uuid4()))
    return original, linked


@pytest.mark.parametrize(
    "edit",
    [
        lambda p: p.update(snapshot_id=str(uuid4())),
        lambda p: p.update(official_value="100"),
        lambda p: p.update(indicator_id=True),
        lambda p: p.update(period_id="not-a-uuid"),
        lambda p: p.update(interpretation_note="x" * 1001),
        lambda p: p.pop("programme_id"),
    ],
)
def test_input_is_closed_and_cannot_supply_server_pins_or_numbers(linked_engine, edit):
    data = deepcopy(linked_engine[3])
    edit(data)
    with pytest.raises(DomainError) as error:
        validate_input(data)
    assert error.value.status == 422


def test_link_is_new_immutable_plan_revision_inheriting_exact_actual_guidance(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    selected = snapshot()
    original, linked = save_link(linked_engine)
    saved = db.objects[TENANT, original["object_id"]]["payload"]
    reference = saved["impact_reference"]
    assert reference["snapshot_id"] == selected["snapshot_id"]
    assert reference["snapshot_revision"] == selected["snapshot_revision"]
    assert reference["definition_revision"] == core["definition"]["revision_id"]
    assert saved["content_versions"] == db.revisions[-2]["payload"]["content_versions"]
    assert (
        plans.guidance(None, TENANT, linked["object_id"], linked["revision_id"])["snapshot_sha256"]
        == plans.guidance(None, TENANT, original["object_id"], original["revision_id"])["snapshot_sha256"]
    )
    assert "impact_reference" not in db.revisions[-2]["payload"]
    assert not any("value" in key for key in reference)


def test_plan_only_get_and_list_hide_private_core_selectors_without_rewriting_saved_pins(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    before = deepcopy(db.objects[TENANT, original["object_id"]]["payload"])
    db.denied_caps.update(capability for _, _, capability in module.CORE_PINS)
    db.allow_dashboard = False
    public = plans.get(None, TENANT, original["object_id"])
    listed = plans.listing(None, TENANT)["items"]
    assert "impact_reference" not in public["data"]
    assert all("impact_reference" not in item["data"] for item in listed)
    assert public["content_compatibility"]["historical_snapshots_available"]
    assert db.objects[TENANT, original["object_id"]]["payload"] == before
    with pytest.raises(DomainError) as error:
        api.result(None, TENANT, original["object_id"])
    assert error.value.status == 404


@pytest.mark.parametrize("cleared", [False, True])
def test_generic_plan_edit_retains_server_reference_even_when_client_cannot_read_core(linked_engine, cleared):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    if cleared:
        linked = api.save(None, TENANT, original["object_id"], body(linked, None), str(uuid4()))
    before = deepcopy(db.objects[TENANT, original["object_id"]]["payload"]["impact_reference"])
    db.denied_caps.update(capability for _, _, capability in module.CORE_PINS)
    public = plans.get(None, TENANT, original["object_id"])["data"]
    public.pop("content_versions")
    public["title"] = "Changed AI plan title; same private reference"
    edited = plans.save(
        None, TENANT, request(public, linked["revision_id"]), str(uuid4()), original["object_id"]
    )
    assert edited["revision_id"] != linked["revision_id"]
    saved = db.objects[TENANT, original["object_id"]]["payload"]
    assert "impact_reference" in saved and saved["impact_reference"] == before
    assert "impact_reference" not in plans.get(None, TENANT, original["object_id"])["data"]


def test_generic_plan_client_cannot_forge_or_clear_private_reference(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    before = deepcopy(db.objects[TENANT, original["object_id"]])
    public = plans.get(None, TENANT, original["object_id"])["data"]
    public.pop("content_versions")
    public["impact_reference"] = None
    with pytest.raises(DomainError) as error:
        plans.save(None, TENANT, request(public, linked["revision_id"]), str(uuid4()), original["object_id"])
    assert error.value.status == 422
    assert db.objects[TENANT, original["object_id"]] == before


def test_official_and_newer_provisional_values_are_separate_and_keep_stored_precision(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    snapshot("12.345")
    original, linked = save_link(linked_engine)
    snapshot("17.999", "PROVISIONAL")
    result = api.result(None, TENANT, original["object_id"])
    assert result["indicator"]["official"]["value"] == "12.345"
    assert result["indicator"]["official"]["displayed_value"] == "12.35"
    assert result["indicator"]["provisional"]["value"] == "17.999"
    assert result["indicator"]["provisional"]["displayed_value"] == "18.00"
    assert result["indicator"]["official"]["mode"] == "OFFICIAL"
    assert result["indicator"]["provisional"]["mode"] == "PROVISIONAL"
    assert "do not establish that AI caused" in result["disclaimer"]


def test_new_locked_snapshot_does_not_silently_refresh_a_saved_reference(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    first = snapshot("12")
    original, linked = save_link(linked_engine)
    later = snapshot("20")
    result = api.result(None, TENANT, original["object_id"])
    assert result["reference"]["snapshot_id"] == first["snapshot_id"]
    assert result["reference_status"]["snapshot"] == "CHANGED"
    assert result["indicator"]["official"]["value"] == "12"
    refreshed = api.save(None, TENANT, original["object_id"], body(linked, data), str(uuid4()))
    result = api.result(None, TENANT, original["object_id"])
    assert refreshed["revision_id"] != linked["revision_id"]
    assert result["reference"]["snapshot_id"] == later["snapshot_id"]
    assert result["indicator"]["official"]["value"] == "20"


def test_no_snapshot_at_link_time_remains_no_official_until_explicit_refresh(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    result = api.result(None, TENANT, original["object_id"])
    assert result["indicator"]["official"] is None
    assert result["reference_status"]["snapshot"] == "ABSENT"
    snapshot("20")
    result = api.result(None, TENANT, original["object_id"])
    assert result["indicator"]["official"] is None
    assert result["reference"]["snapshot_id"] is None
    assert result["reference_status"]["snapshot"] == "CHANGED"


def test_exact_replay_precedes_current_core_semantic_validation(linked_engine, monkeypatch):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    command = body(original, data)
    linked = api.save(None, TENANT, original["object_id"], command, str(uuid4()))
    monkeypatch.setattr(
        api, "_current_pins", lambda *args: (_ for _ in ()).throw(AssertionError("must not refresh replay"))
    )
    assert api.save(None, TENANT, original["object_id"], command, str(uuid4())) == linked
    assert len(db.receipts) == 2 and len(db.content_bindings) == 2


@pytest.mark.parametrize("permission", ["allow_read", "allow_write"])
def test_replay_never_bypasses_current_plan_authority(linked_engine, permission):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    command = body(original, data)
    api.save(None, TENANT, original["object_id"], command, str(uuid4()))
    setattr(db, permission, False)
    with pytest.raises(DomainError) as denied:
        api.save(None, TENANT, original["object_id"], command, str(uuid4()))
    assert denied.value.status == 404


@pytest.mark.parametrize(
    "capability", [cap for _, _, cap in module.CORE_PINS] + ["snapshots.read", "calculated-results.read"]
)
def test_result_requires_current_authority_on_each_linked_core_object(linked_engine, capability):
    plans, api, db, data, core, snapshot = linked_engine
    snapshot()
    original, linked = save_link(linked_engine)
    db.denied_caps.add(capability)
    with pytest.raises(DomainError) as denied:
        api.result(None, TENANT, original["object_id"])
    assert denied.value.status == 404


def test_dashboard_scope_is_required_on_the_actual_linked_programme(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    db.allow_dashboard = False
    with pytest.raises(DomainError) as denied:
        api.result(None, TENANT, original["object_id"])
    assert denied.value.status == 404


def test_plan_only_actor_cannot_distinguish_unlinked_from_hidden_linked_lookup(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    unlinked = plans.save(None, TENANT, request(), str(uuid4()))
    linked, _ = save_link(linked_engine)
    corrupt = plans.save(None, TENANT, request(), str(uuid4()))
    db.objects[TENANT, corrupt["object_id"]]["payload"]["impact_reference"] = {}
    db.allow_dashboard = False
    for receipt in (unlinked, linked, corrupt):
        with pytest.raises(DomainError) as denied:
            api.result(None, TENANT, receipt["object_id"])
        assert denied.value.status == 404


def test_unrelated_dashboard_scope_cannot_distinguish_absent_from_hidden_link(linked_engine, monkeypatch):
    plans, api, db, data, core, snapshot = linked_engine
    unlinked = plans.save(None, TENANT, request(), str(uuid4()))
    linked, _ = save_link(linked_engine)
    corrupt = plans.save(None, TENANT, request(), str(uuid4()))
    db.objects[TENANT, corrupt["object_id"]]["payload"]["impact_reference"] = {}
    original = module.authorize

    def another_programme(c, ctx, operation, obj=None, hidden=False):
        if operation == "programme_dashboard":
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return original(c, ctx, operation, obj, hidden=hidden)

    monkeypatch.setattr(module, "authorize", another_programme)
    errors = []
    for receipt in (unlinked, linked, corrupt):
        with pytest.raises(DomainError) as denied:
            api.result(None, TENANT, receipt["object_id"])
        errors.append((denied.value.code, denied.value.status, denied.value.reason, denied.value.message))
    assert (
        errors[0]
        == errors[1]
        == errors[2]
        == ("RESOURCE_UNAVAILABLE", 404, None, "The resource is unavailable.")
    )


def test_clear_is_explicit_new_revision_and_possible_after_core_read_revocation(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    db.denied_caps.add("programmes.read")
    cleared = api.save(None, TENANT, original["object_id"], body(linked, None), str(uuid4()))
    assert cleared["revision_id"] != linked["revision_id"]
    assert db.objects[TENANT, original["object_id"]]["payload"]["impact_reference"] is None
    with pytest.raises(DomainError) as absent:
        api.result(None, TENANT, original["object_id"])
    assert absent.value.status == 404
    assert (
        next(row for row in db.revisions if row["head_revision"] == linked["revision_id"])["payload"][
            "impact_reference"
        ]
        is not None
    )


def test_failure_after_relationship_write_rolls_back_head_guidance_audit_and_receipt(
    linked_engine, monkeypatch
):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    before = deepcopy((db.objects, db.revisions, db.events, db.receipts, db.content_bindings))
    monkeypatch.setattr(
        module, "audit", lambda *args: (_ for _ in ()).throw(DomainError("RESOURCE_UNAVAILABLE", 503))
    )
    with pytest.raises(DomainError):
        api.save(None, TENANT, original["object_id"], body(original, data), str(uuid4()))
    assert (db.objects, db.revisions, db.events, db.receipts, db.content_bindings) == before


def test_absent_historical_guidance_is_not_captured_during_a_relationship_only_edit(
    linked_engine, monkeypatch
):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    db.content_bindings.clear()
    monkeypatch.setattr(
        archives, "catalog", lambda: (_ for _ in ()).throw(AssertionError("must not invent old guides"))
    )
    linked = api.save(None, TENANT, original["object_id"], body(original, data), str(uuid4()))
    assert not db.content_bindings
    assert plans.guidance(None, TENANT, linked["object_id"], linked["revision_id"])["status"] == "UNAVAILABLE"


def test_corrupt_guidance_refuses_relationship_write_atomically(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    next(iter(db.content_snapshots.values()))["payload_sha256"] = b"\x00" * 32
    before = deepcopy((db.objects, db.revisions, db.receipts, db.content_bindings))
    with pytest.raises(DomainError) as denied:
        api.save(None, TENANT, original["object_id"], body(original, data), str(uuid4()))
    assert denied.value.status == 503
    assert (db.objects, db.revisions, db.receipts, db.content_bindings) == before


@pytest.mark.parametrize(
    "alter,reason",
    [
        (
            lambda rows: rows["indicator"]["payload"].update(programme_id=str(uuid4())),
            "INDICATOR_NOT_IN_PROGRAMME",
        ),
        (
            lambda rows: rows["programme"]["payload"].update(reporting_calendar_id=str(uuid4())),
            "PERIOD_NOT_IN_PROGRAMME_CALENDAR",
        ),
        (
            lambda rows: rows["period"]["payload"].update(ends_at="2028-01-01T00:00:00Z"),
            "PERIOD_OUTSIDE_PROGRAMME",
        ),
    ],
)
def test_mismatched_governed_relationships_are_refused_without_a_revision(linked_engine, alter, reason):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    alter(core)
    before = len(db.revisions)
    with pytest.raises(DomainError) as denied:
        api.save(None, TENANT, original["object_id"], body(original, data), str(uuid4()))
    assert denied.value.reason == reason and len(db.revisions) == before


def test_wrong_tenant_and_wrong_plan_kind_remain_opaque(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    for tenant, obj in (("other-tenant", original["object_id"]), (TENANT, core["programme"]["object_id"])):
        with pytest.raises(DomainError) as denied:
            api.result(None, tenant, obj)
        assert denied.value.status == 404


def test_stale_or_changed_operation_conflicts_do_not_refresh_evidence(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    command = body(original, data)
    linked = api.save(None, TENANT, original["object_id"], command, str(uuid4()))
    with pytest.raises(DomainError) as stale:
        api.save(None, TENANT, original["object_id"], body(original, data), str(uuid4()))
    assert stale.value.code == "CONFLICT_VERSION"
    changed = deepcopy(command)
    changed["data"]["interpretation_note"] = "Changed synthetic interpretation"
    with pytest.raises(DomainError) as reused:
        api.save(None, TENANT, original["object_id"], changed, str(uuid4()))
    assert reused.value.code == "CONFLICT_OPERATION"
    assert str(db.objects[TENANT, original["object_id"]]["head_revision"]) == linked["revision_id"]


def test_expired_receipt_does_not_become_a_new_relationship_command(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    command = body(original, data)
    api.save(None, TENANT, original["object_id"], command, str(uuid4()))
    receipt = next(row for key, row in db.receipts.items() if key[2] == module.SAVE_OPERATION)
    receipt["expires_at"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    before = deepcopy((db.objects, db.revisions, db.receipts, db.content_bindings))
    with pytest.raises(DomainError) as expired:
        api.save(None, TENANT, original["object_id"], command, str(uuid4()))
    assert expired.value.code == "IDEMPOTENCY_EXPIRED"
    assert (db.objects, db.revisions, db.receipts, db.content_bindings) == before


@pytest.mark.parametrize("name", [name for name, _, _ in module.CORE_PINS])
def test_core_head_changes_are_reported_while_exact_pinned_wording_is_preserved(linked_engine, name):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    row = db.objects[TENANT, core[name]["object_id"]]
    row["head_revision"] = str(uuid4())
    row["payload"]["title"] = "Changed core title today"
    row["payload"]["name"] = "Changed core name today"
    result = api.result(None, TENANT, original["object_id"])
    assert result["reference_status"][name] == "CHANGED"
    assert result["reference"][name + "_revision"] != row["head_revision"]
    assert result["programme_title"] == "Synthetic governed programme"
    assert result["indicator"]["indicator_label"] == "Verified approved deliveries · Synthetic site"


def test_linked_result_read_has_no_domain_mutations_or_archive_generation(linked_engine, monkeypatch):
    plans, api, db, data, core, snapshot = linked_engine
    snapshot()
    original, linked = save_link(linked_engine)
    before = deepcopy(
        (db.objects, db.revisions, db.events, db.receipts, db.content_bindings, db.content_snapshots)
    )
    monkeypatch.setattr(
        archives, "capture", lambda *args: (_ for _ in ()).throw(AssertionError("read cannot capture"))
    )
    assert api.result(None, TENANT, original["object_id"])["status"] == "LINKED"
    assert (
        db.objects,
        db.revisions,
        db.events,
        db.receipts,
        db.content_bindings,
        db.content_snapshots,
    ) == before


@pytest.mark.parametrize(
    "kind,capability", [("Target", "targets.read"), ("CollectionPlan", "collection-plans.read")]
)
def test_returned_target_and_locked_coverage_require_current_core_visibility(
    linked_engine, monkeypatch, kind, capability
):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    obj, rev = str(uuid4()), str(uuid4())
    row = {
        "tenant_id": TENANT,
        "object_id": obj,
        "object_type": kind,
        "head_revision": rev,
        "revision_id": rev,
        "payload": {},
        "lifecycle_state": "Approved",
    }
    db.objects[TENANT, obj] = row
    db.revisions.append(deepcopy(row))
    if kind == "Target":
        target = {
            "target_id": obj,
            "revision_id": rev,
            "target_kind": "VALUE",
            "target_basis": "ORIGINAL",
            "direction": "HIGHER",
            "value_state": "PRESENT",
            "value": "50",
            "low": None,
            "high": None,
            "binding_version": 1,
        }
        monkeypatch.setattr(plans.service.dashboards, "targets", lambda *args: (target, None))
    else:
        coverage = summarize(
            {
                "plan_revision": rev,
                "required_count": 2,
                "approved_count": 2,
                "approval_percent": "100.00",
                "complete": True,
            },
            "CLOSE_SNAPSHOT",
        )
        monkeypatch.setattr(plans.service.dashboards, "coverage", lambda *args: coverage)
    db.denied_objects.add(obj)
    with pytest.raises(DomainError) as denied:
        api.result(None, TENANT, original["object_id"])
    assert denied.value.status == 404


def test_incomplete_programme_dates_are_validation_failure_instead_of_server_error(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original = plans.save(None, TENANT, request(), str(uuid4()))
    core["programme"]["payload"].pop("starts_at")
    with pytest.raises(DomainError) as denied:
        api.save(None, TENANT, original["object_id"], body(original, data), str(uuid4()))
    assert denied.value.status == 422


@pytest.mark.parametrize("value", [None, "0", "-0.004"])
def test_blank_zero_and_negative_near_zero_keep_core_value_semantics(linked_engine, value):
    plans, api, db, data, core, snapshot = linked_engine
    snap = snapshot(value)
    if value is None:
        db.official_values[snap["snapshot_id"]]["payload"]["value_state"] = "UNDEFINED"
        db.official_values[snap["snapshot_id"]]["payload"]["reason_code"] = "ZERO_DENOMINATOR"
    original, linked = save_link(linked_engine)
    result = api.result(None, TENANT, original["object_id"])["indicator"]["official"]
    assert result["value"] == value
    assert result["displayed_value"] == (None if value is None else "0.00")
    if value is None:
        assert result["value_state"] == "UNDEFINED" and result["reason_code"] == "ZERO_DENOMINATOR"


def test_malformed_server_pin_is_unreadable_and_never_treated_as_current(linked_engine):
    plans, api, db, data, core, snapshot = linked_engine
    original, linked = save_link(linked_engine)
    db.objects[TENANT, original["object_id"]]["payload"]["impact_reference"]["snapshot_version"] = True
    with pytest.raises(DomainError) as denied:
        api.result(None, TENANT, original["object_id"])
    assert denied.value.reason is None and denied.value.status == 404


def test_isolated_contracts_do_not_accept_server_pins_in_generic_plan_writes():
    import json
    from pathlib import Path

    spec = json.loads(Path("packages/contracts/openapi.json").read_text())
    policy = {"operations": []}
    augment(spec, policy)
    schemas = spec["components"]["schemas"]
    assert "impact_reference" not in schemas["AIAdoptionPlanStoredData"]["properties"]
    assert "impact_reference" not in schemas["AIAdoptionPlanData"]["properties"]
    assert schemas["AIImpactReferenceInput"]["additionalProperties"] is False
    assert {row["capability"] for row in policy["operations"]} == {
        "ai.enablement.read",
        "ai.enablement.manage",
    }
    Draft202012Validator.check_schema(schemas["AIImpactReferenceResult"])
