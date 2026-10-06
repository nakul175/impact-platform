"""Bounded diagnostics of retained definition/framework wording versus current authority.

These observations are not passing security qualification. Each independent fixture changes
only one synthetic object's current visibility and preserves old immutable revisions and values.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest

from prepared_dashboard_visibility_repro import synthetic_current_classification
from test_ai_impact_references_live import disabled
from test_dashboard_current_visibility import synthetic_current_head_restriction
from test_dashboards import calculate, card, close, measure, ratio_source, series
from test_live_application import expect
from test_planning import approved, framework, tva


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/evidence/nonprofit-ai-retained-label-visibility-reproduction.json"


@pytest.fixture(scope="module", autouse=True)
def diagnostic_report(live):
    with live.db() as c:
        applied = c.execute("SELECT version,sha256 FROM impact.schema_migration ORDER BY version").fetchall()
    REPORT.write_text(
        json.dumps(
            {
                "scope": "Isolated real local API diagnostic; observations are not passing security, native, hosted or requirement acceptance evidence",
                "policy_basis": "Existing current object reads conceal restricted classification/head; revoked source capability already withholds historical wording. Frozen snapshots preserve arithmetic and revision selection, not current source authority.",
                "source_sha256": {
                    name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                    for name in (
                        "apps/api/impact_api/store.py",
                        "apps/api/impact_api/dashboards.py",
                        "apps/api/impact_api/planning.py",
                        "qualification/prepared_retained_label_visibility_repro.py",
                    )
                },
                "applied_migrations": applied,
                "observations": [],
            },
            indent=2,
            default=str,
        )
        + "\n"
    )


@pytest.fixture
def frozen_labels(live):
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "50", "100")
    ratio_source(live, indicator, keys[1], "1", "10")
    calculate(live, indicator, period)
    baseline, _ = approved(live, "frameworks", framework(live, programme, indicator))
    close(live, programme, period)
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        definition = c.execute(
            "SELECT object_id,payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (live.fixture["tenant_a"], indicator["data"]["definition_version"]),
        ).fetchone()
    return programme, indicator, period, definition, baseline


def shown(live, programme, indicator, period):
    dashboard, row = card(live, programme, indicator, period, actor="reviewer")
    line = series(live, indicator, actor="reviewer")
    planning = tva(live, programme["object_id"], actor="reviewer", period_id=period["object_id"])
    planned = next(r for r in planning["rows"] if r["indicator_id"] == indicator["object_id"])
    return {
        "dashboard_label": row["indicator_label"],
        "dashboard_unit": row["unit"],
        "series_label": line["indicator_label"],
        "series_unit": line["unit"],
        "planning_label": planned["indicator_label"],
        "planning_unit": planned["unit"],
        "planning_framework": planning["framework"],
        "planning_framework_revision": planned["framework_revision"],
        "planning_node_ids": planned["node_ids"],
        "snapshot_id": dashboard["snapshot"]["snapshot_id"],
        "official_value": row["official"]["value"] if row["official"] else None,
    }


def old_state(live, ids):
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        return c.execute(
            "SELECT revision_id,payload,payload_sha256,restriction_state FROM impact.object_revision "
            "WHERE tenant_id=%s AND revision_id=ANY(%s::uuid[]) ORDER BY revision_id",
            (live.fixture["tenant_a"], ids),
        ).fetchall()


@pytest.mark.parametrize("visibility", ["CLASSIFICATION", "HEAD_REVISION"])
@pytest.mark.parametrize(
    "kind,route,capability",
    [
        ("IndicatorDefinition", "indicator-definitions", "indicator-definitions.read"),
        ("Framework", "frameworks", "frameworks.read"),
    ],
)
def test_observe_current_definition_and_framework_visibility(
    live, frozen_labels, kind, route, capability, visibility
):
    programme, indicator, period, definition, baseline = frozen_labels
    obj = str(definition["object_id"]) if kind == "IndicatorDefinition" else baseline["object_id"]
    ids = [indicator["data"]["definition_version"], baseline["revision_id"]]
    before = shown(live, programme, indicator, period)
    assert before["official_value"] == "46.363636363636"
    assert before["planning_framework"]["revision_id"] == baseline["revision_id"]
    immutable_before = old_state(live, ids)
    expect(live.request(live.path(route, obj), actor="reviewer"), 200)
    with disabled(live, "reviewer", capability):
        direct_scope = live.request(live.path(route, obj), actor="reviewer")
        expect(direct_scope, 404)
        scope = shown(live, programme, indicator, period)
        if kind == "IndicatorDefinition":
            assert all(scope[k] is None for k in ("dashboard_unit", "series_unit", "planning_unit"))
        else:
            assert scope["planning_framework"] is None and not scope["planning_node_ids"]
    guard = (
        synthetic_current_classification
        if visibility == "CLASSIFICATION"
        else synthetic_current_head_restriction
    )
    with guard(live, obj):
        direct = live.request(live.path(route, obj), actor="reviewer")
        expect(direct, 404)
        current = shown(live, programme, indicator, period)
        assert old_state(live, ids) == immutable_before
        assert current["snapshot_id"] == before["snapshot_id"]
        assert current["official_value"] == before["official_value"]
        leak = (
            any(current[k] is not None for k in ("dashboard_unit", "series_unit", "planning_unit"))
            if kind == "IndicatorDefinition"
            else current["planning_framework"] is not None or bool(current["planning_node_ids"])
        )
        observation = {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "visibility": visibility,
            "direct_route_status": direct.status_code,
            "scope_control": scope,
            "current_restriction_view": current,
            "immutable_old_payloads_unchanged": True,
            "official_value_unchanged": before["official_value"],
            "outcome": "RETAINED_WORDING_BYPASS_REPRODUCED" if leak else "RETAINED_WORDING_WITHHELD",
        }
        report = json.loads(REPORT.read_text())
        report["observations"].append(observation)
        REPORT.write_text(json.dumps(report, indent=2, default=str) + "\n")
    expect(live.request(live.path(route, obj), actor="reviewer"), 200)
