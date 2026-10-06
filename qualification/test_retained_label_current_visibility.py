"""Strict regressions prepared for the reproduced retained-wording current visibility fix.

Do not register these as passing until the shared core fix is implemented and qualified.
"""
# ruff: noqa: F811

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import pytest

from prepared_dashboard_visibility_repro import synthetic_current_classification
from prepared_retained_label_visibility_repro import frozen_labels, old_state, shown  # noqa: F401
from test_ai_impact_references_live import disabled
from test_dashboard_current_visibility import historical_state, synthetic_current_head_restriction
from test_live_application import expect


@pytest.fixture(scope="module", autouse=True)
def retained_visibility_migration_ledger(live):
    root = Path(__file__).resolve().parents[1]
    with live.db() as c:
        rows = c.execute("SELECT version,sha256 FROM impact.schema_migration ORDER BY version").fetchall()
    migrations = []
    for row in rows:
        path = next((root / "infrastructure/migrations").glob(f"{row['version']:04d}_*.sql"))
        migrations.append(
            {
                "version": row["version"],
                "file": path.name,
                "applied_sha256": row["sha256"],
                "current_source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    native = os.environ.get("IMPACT_NATIVE_TEST") == "1"
    environment = "native" if native else "pglite"
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "environment": "NATIVE_POSTGRESQL" if native else "PGLITE",
        "scope": "Actually applied migration checksums for retained-wording qualification; outcome and acceptance evidence are separate",
        "migrations": migrations,
    }
    (
        root / f"docs/evidence/sprint-0.33-retained-visibility-{environment}-applied-migrations.json"
    ).write_text(json.dumps(report, indent=2) + "\n")
    assert all(r["applied_sha256"] == r["current_source_sha256"] for r in migrations)


def assert_wording_withheld(kind, value, original_definition_name):
    if kind == "IndicatorDefinition":
        for surface in ("dashboard", "series", "planning"):
            assert value[surface + "_unit"] is None
            assert original_definition_name not in value[surface + "_label"]
    else:
        assert value["planning_framework"] is None
        assert value["planning_framework_revision"] is None
        assert value["planning_node_ids"] == []


@pytest.mark.parametrize("visibility", ["CLASSIFICATION", "HEAD_REVISION"])
@pytest.mark.parametrize(
    "kind,route,capability",
    [
        ("IndicatorDefinition", "indicator-definitions", "indicator-definitions.read"),
        ("Framework", "frameworks", "frameworks.read"),
    ],
)
def test_current_authority_withholds_frozen_wording_without_changing_original_numbers(
    live, frozen_labels, kind, route, capability, visibility
):
    programme, indicator, period, definition, baseline = frozen_labels
    obj = str(definition["object_id"]) if kind == "IndicatorDefinition" else baseline["object_id"]
    ids = [indicator["data"]["definition_version"], baseline["revision_id"]]
    before = shown(live, programme, indicator, period)
    assert before["official_value"] == "46.363636363636"
    assert before["planning_framework"]["revision_id"] == baseline["revision_id"]
    assert before["dashboard_unit"] == before["series_unit"] == before["planning_unit"] == "percent"
    immutable_wording = old_state(live, ids)
    immutable_results = historical_state(live, programme, period)
    name = definition["payload"]["name"]
    expect(live.request(live.path(route, obj), actor="reviewer"), 200)
    with disabled(live, "reviewer", capability):
        expect(live.request(live.path(route, obj), actor="reviewer"), 404)
        assert_wording_withheld(kind, shown(live, programme, indicator, period), name)
    guard = (
        synthetic_current_classification
        if visibility == "CLASSIFICATION"
        else synthetic_current_head_restriction
    )
    with guard(live, obj):
        expect(live.request(live.path(route, obj), actor="reviewer"), 404)
        current = shown(live, programme, indicator, period)
        assert_wording_withheld(kind, current, name)
        assert current["snapshot_id"] == before["snapshot_id"]
        assert current["official_value"] == before["official_value"]
        assert old_state(live, ids) == immutable_wording
        assert historical_state(live, programme, period) == immutable_results
    expect(live.request(live.path(route, obj), actor="reviewer"), 200)
    restored = shown(live, programme, indicator, period)
    assert restored == before
    assert old_state(live, ids) == immutable_wording
    assert historical_state(live, programme, period) == immutable_results
