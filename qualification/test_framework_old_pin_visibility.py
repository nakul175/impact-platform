"""A storage-valid unavailable historical Framework pin must not expose frozen wording.

The append-only synthetic register is a negative storage fixture, not a supported privacy or
approval API workflow. It does not overwrite immutable payloads or frozen snapshot bindings.
"""
# ruff: noqa: F811

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from impact_api.store import context, write
from prepared_retained_label_visibility_repro import frozen_labels, old_state  # noqa: F401
from test_ai_impact_references_live import local_engine
from test_dashboard_current_visibility import append_head, historical_state
from test_live_application import expect
from test_planning import tva


def storage_guards(live):
    with live.db() as c:
        triggers = c.execute(
            "SELECT tgname,tgenabled FROM pg_trigger WHERE tgrelid='impact.object_revision'::regclass "
            "AND NOT tgisinternal ORDER BY tgname"
        ).fetchall()
        foreign_keys = c.execute(
            "SELECT conname,convalidated FROM pg_constraint WHERE conrelid='impact.framework_baseline'::regclass "
            "AND contype='f' ORDER BY conname"
        ).fetchall()
    assert triggers and all(r["tgenabled"] != "D" for r in triggers)
    assert foreign_keys and all(r["convalidated"] for r in foreign_keys)
    return triggers, foreign_keys


def test_exact_unavailable_framework_pin_is_hidden_despite_readable_current_head(live, frozen_labels):
    programme, indicator, period, definition, baseline = frozen_labels
    tenant = live.fixture["tenant_a"]
    guarded_before = storage_guards(live)
    old_revisions = [indicator["data"]["definition_version"], baseline["revision_id"]]
    old_wording = old_state(live, old_revisions)
    old_official = historical_state(live, programme, period)
    restricted = append_head(
        live, baseline["object_id"], baseline["revision_id"], baseline["revision_id"], "RESTRICTED"
    )
    available = append_head(live, baseline["object_id"], baseline["revision_id"], restricted, "AVAILABLE")
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        c.execute(
            "INSERT INTO impact.framework_baseline(tenant_id,programme_id,baseline_version,framework_id,"
            "framework_revision,supersedes_revision,effective_from,workflow_id,approved_by,approved_at) "
            "SELECT tenant_id,programme_id,baseline_version+1,framework_id,%s,framework_revision,"
            "effective_from,workflow_id,approved_by,now() FROM impact.framework_baseline "
            "WHERE tenant_id=%s AND programme_id=%s AND framework_revision=%s",
            (restricted, tenant, programme["object_id"], baseline["revision_id"]),
        )
        pins = c.execute(
            "SELECT revision_id,payload,payload_sha256,restriction_state FROM impact.object_revision "
            "WHERE tenant_id=%s AND revision_id=ANY(%s::uuid[]) ORDER BY revision_id",
            (tenant, [restricted, available]),
        ).fetchall()
        applied_migrations = c.execute(
            "SELECT version,sha256 FROM impact.schema_migration ORDER BY version"
        ).fetchall()
    assert {r["restriction_state"] for r in pins} == {"RESTRICTED", "AVAILABLE"}
    assert all(r["payload"] == baseline["data"] for r in pins)
    # A separate valid Period makes an open governing row; the real locked snapshot stays intact.
    _, db, identity = local_engine(live)
    with db.transaction(tenant) as c:
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        ctx = context(c, identity, tenant)
        data = deepcopy(period["data"])
        data.update(
            code="OLD-PIN-" + str(uuid4())[:8],
            starts_at="2026-11-01T00:00:00Z",
            ends_at="2026-12-01T00:00:00Z",
        )
        opened = write(c, ctx, "Period", data, "Draft")
    direct = expect(live.request(live.path("frameworks", baseline["object_id"]), actor="reviewer"), 200)
    assert direct["revision_id"] == available
    open_view = tva(live, programme["object_id"], actor="reviewer", period_id=opened["object_id"])
    open_row = next(r for r in open_view["rows"] if r["indicator_id"] == indicator["object_id"])
    assert open_row["period_state"] == "Open"
    locked_view = tva(live, programme["object_id"], actor="reviewer", period_id=period["object_id"])
    locked_row = next(r for r in locked_view["rows"] if r["indicator_id"] == indicator["object_id"])
    root = Path(__file__).resolve().parents[1]
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Storage-valid append-only unavailable historical pin negative; not an API privacy or approval workflow and not hosted/native qualification",
        "source_sha256": {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in ("apps/api/impact_api/planning.py", "apps/api/impact_api/store.py")
        },
        "applied_migrations": applied_migrations,
        "current_framework_status": 200,
        "current_head_restriction": "AVAILABLE",
        "historical_pin_restriction": "RESTRICTED",
        "top_level_framework": open_view["framework"],
        "open_governing_revision": open_row["framework_revision"],
        "open_node_ids": open_row["node_ids"],
        "locked_governing_revision": locked_row["framework_revision"],
        "locked_actual_value": locked_row["actual"]["value"],
        "immutable_old_payloads_and_snapshot_unchanged": old_state(live, old_revisions) == old_wording
        and historical_state(live, programme, period) == old_official,
        "immutable_and_fk_guards_unchanged": storage_guards(live) == guarded_before,
    }
    (root / "docs/evidence/nonprofit-ai-framework-old-pin-visibility-observation.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n"
    )
    assert open_view["framework"] is None
    assert open_row["framework_revision"] is None and open_row["node_ids"] == []
    assert locked_view["framework"] is None
    assert locked_row["framework_revision"] == baseline["revision_id"]
    assert locked_row["node_ids"] == [
        n["node_id"]
        for n in baseline["data"]["nodes"]
        if indicator["object_id"] in n.get("indicator_ids", [])
    ]
    assert locked_row["actual"]["value"] == "46.363636363636"
    assert old_state(live, old_revisions) == old_wording
    assert historical_state(live, programme, period) == old_official
    assert storage_guards(live) == guarded_before
