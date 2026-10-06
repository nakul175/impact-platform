"""Reproduce current-head visibility versus immutable dashboard snapshot semantics.

This is an isolated diagnostic, not a passing security qualification. It changes only synthetic
current classification inside a disposable fixture, restores it, and never disables RLS or
immutable triggers. Scope removal is the control case; old snapshot numbers must never change.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest

from test_ai_impact_references_live import disabled
from test_dashboards import calculate, card, close, measure, ratio_source, target
from test_live_application import expect


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/evidence/nonprofit-ai-dashboard-visibility-reproduction.json"


@contextmanager
def synthetic_current_classification(live, obj):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        old = c.execute(
            "SELECT classification,head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
            (tenant, obj),
        ).fetchone()
        assert old
        c.execute(
            "UPDATE impact.object_registry SET classification='RESTRICTED' WHERE tenant_id=%s AND object_id=%s",
            (tenant, obj),
        )
    try:
        yield old
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(
                "UPDATE impact.object_registry SET classification=%s WHERE tenant_id=%s AND object_id=%s",
                (old["classification"], tenant, obj),
            )


@pytest.fixture(scope="module")
def frozen_core(live):
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "50", "100")
    ratio_source(live, indicator, keys[1], "1", "10")
    calculate(live, indicator, period)
    goal = target(live, indicator, period, "50")
    close(live, programme, period)
    dashboard, row = card(live, programme, indicator, period, actor="reviewer")
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        plan = c.execute(
            "SELECT object_id FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (tenant, row["coverage"]["plan_revision"]),
        ).fetchone()
    REPORT.write_text(
        json.dumps(
            {
                "scope": "Isolated diagnostic using real local API/database and reviewed synthetic facts; not passing security or hosted qualification",
                "setup": "Current registry classification changed for one synthetic object and restored; old revisions remain AVAILABLE, RLS and immutable triggers remain enabled",
                "policy_basis": "Current store.load rejects RESTRICTED registry classification and non-AVAILABLE current revision; approved snapshots freeze arithmetic/revision selection, not current read authority",
                "source_sha256": {
                    name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                    for name in (
                        "apps/api/impact_api/store.py",
                        "apps/api/impact_api/dashboards.py",
                        "apps/api/impact_api/planning.py",
                        "apps/api/impact_api/dashboard_contracts.py",
                    )
                },
                "observations": [],
            },
            indent=2,
        )
        + "\n"
    )
    return (
        programme,
        indicator,
        period,
        goal["object_id"],
        str(plan["object_id"]),
        dashboard["snapshot"]["snapshot_id"],
        row["official"]["result_id"],
    )


@pytest.mark.parametrize(
    "kind,route,capability,index",
    [
        ("Target", "targets", "targets.read", 3),
        ("CollectionPlan", "collection-plans", "collection-plans.read", 4),
        ("CalculatedResult", "calculated-results", "calculated-results.read", 6),
    ],
)
def test_compare_current_scope_and_classification_with_returned_snapshot_blocks(
    live, frozen_core, kind, route, capability, index
):
    programme, indicator, period, target_id, plan_id, snapshot_id, result_id = frozen_core
    obj = frozen_core[index]
    expect(live.request(live.path(route, obj), actor="reviewer"), 200)

    def visible(row):
        return (
            row["target"]["value"]
            if kind == "Target" and row["target"]
            else row["coverage"]["approved_count"]
            if kind == "CollectionPlan"
            else row["official"]["value"]
            if kind == "CalculatedResult" and row["official"]
            else None
        )

    with disabled(live, "reviewer", capability):
        direct_scope = live.request(live.path(route, obj), actor="reviewer")
        expect(direct_scope, 404)
        _, scope_row = card(live, programme, indicator, period, actor="reviewer")
        assert visible(scope_row) is None, (
            "Revoked current scope must withhold the block instead of treating it as zero"
        )
    with synthetic_current_classification(live, obj) as old:
        direct_classification = live.request(live.path(route, obj), actor="reviewer")
        expect(direct_classification, 404)
        dashboard, classified_row = card(live, programme, indicator, period, actor="reviewer")
        assert dashboard["snapshot"]["snapshot_id"] == snapshot_id
        if kind != "CalculatedResult":
            assert classified_row["official"]["value"] == "46.363636363636", (
                "Classification cannot recompute the frozen official arithmetic"
            )
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            state = c.execute(
                "SELECT r.classification,r.head_revision,v.restriction_state FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
                (live.fixture["tenant_a"], obj),
            ).fetchone()
            original = c.execute(
                "SELECT v.payload FROM impact.official_result_snapshot o JOIN impact.object_revision v ON v.tenant_id=o.tenant_id AND v.revision_id=o.result_revision WHERE o.tenant_id=%s AND o.snapshot_id=%s AND o.indicator_id=%s",
                (live.fixture["tenant_a"], snapshot_id, indicator["object_id"]),
            ).fetchone()
        assert original["payload"]["value"] == "46.363636363636"
        assert state["classification"] == "RESTRICTED" and state["restriction_state"] == "AVAILABLE"
        assert state["head_revision"] == old["head_revision"]
        value = visible(classified_row)
        observed = {
            "kind": kind,
            "object_id": obj,
            "snapshot_id": snapshot_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "scope_control": {
                "direct_route_status": direct_scope.status_code,
                "dashboard_value": visible(scope_row),
            },
            "classification_case": {
                "direct_route_status": direct_classification.status_code,
                "registry_classification": state["classification"],
                "old_head_revision_still_available": True,
                "dashboard_value": value,
                "official_value_unchanged": original["payload"]["value"],
                "dashboard_official_value": classified_row["official"]["value"]
                if classified_row["official"]
                else None,
            },
            "outcome": "CURRENT_CLASSIFICATION_BYPASS_REPRODUCED"
            if value is not None
            else "CURRENT_CLASSIFICATION_BLOCK_WITHHELD",
        }
        report = json.loads(REPORT.read_text())
        report["observations"].append(observed)
        REPORT.write_text(json.dumps(report, indent=2) + "\n")
    expect(live.request(live.path(route, obj), actor="reviewer"), 200)
