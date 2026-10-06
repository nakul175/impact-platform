"""Dependent visibility omits unavailable rows while governed results remain readable."""

import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import pytest

from prepared_dashboard_visibility_repro import synthetic_current_classification
from test_ai_impact_references_live import scoped_programme
from test_dashboard_current_visibility import historical_state, synthetic_current_head_restriction
from test_dashboards import calculate, card, close, measure, ratio_source
from test_live_application import expect


@pytest.fixture(scope="module", autouse=True)
def listing_migration_ledger(live):
    root = Path(__file__).resolve().parents[1]
    with live.db() as c:
        rows = c.execute("SELECT version,sha256 FROM impact.schema_migration ORDER BY version").fetchall()
    applied = []
    for row in rows:
        path = next((root / "infrastructure/migrations").glob(f"{row['version']:04d}_*.sql"))
        applied.append(
            {
                "version": row["version"],
                "file": path.name,
                "applied_sha256": row["sha256"],
                "current_source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    native = os.environ.get("IMPACT_NATIVE_TEST") == "1"
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "environment": "NATIVE_POSTGRESQL" if native else "PGLITE",
        "scope": "Actually applied migration checksums for dependent listing visibility; not formal acceptance",
        "migrations": applied,
    }
    environment = "native" if native else "pglite"
    (root / f"docs/evidence/sprint-0.33-listing-visibility-{environment}-applied-migrations.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    assert all(row["applied_sha256"] == row["current_source_sha256"] for row in applied)


def governed_result(live):
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "50", "100")
    ratio_source(live, indicator, keys[1], "1", "10")
    provisional = calculate(live, indicator, period)
    close(live, programme, period)
    _, row = card(live, programme, indicator, period, actor="reviewer")
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        binding = c.execute(
            "SELECT plan_id FROM impact.collection_plan_binding "
            "WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s",
            (live.fixture["tenant_a"], indicator["object_id"], period["object_id"]),
        ).fetchone()
    return {
        "programme": programme,
        "period": period,
        "plan_id": str(binding["plan_id"]),
        "results": [provisional["object_id"], row["official"]["result_id"]],
    }


def listed_results(live, forbidden):
    items, cursor, seen = [], None, set()
    # Small pages exercise signed keyset continuity, including unavailable candidates
    # between the returned rows. A signed cursor names the last returned visible row.
    for _ in range(1000):
        response = live.request(
            live.path("calculated-results"),
            actor="reviewer",
            params={"limit": 7, **({"cursor": cursor} if cursor else {})},
        )
        page = expect(response, 200)
        assert set(page) == {"items", "next_cursor", "scope_label"}
        assert all(value not in response.text for value in forbidden)
        for item in page["items"]:
            assert item["object_id"] not in seen
            seen.add(item["object_id"])
            items.append(item)
        cursor = page["next_cursor"]
        if not cursor:
            return items
        assert page["items"]
        payload = cursor.split(".")[0]
        decoded = json.loads(base64.urlsafe_b64decode(payload + "=" * ((-len(payload)) % 4)))
        last = page["items"][-1]
        assert decoded["key"] == [last["created_at"], last["object_id"]]
        assert all(value not in json.dumps(decoded) for value in forbidden)
    raise AssertionError("Bounded synthetic listing did not finish")


@pytest.mark.parametrize("boundary", ["CLASSIFICATION", "HEAD_REVISION", "SCOPED_READ"])
def test_unavailable_dependent_result_does_not_fail_the_page_or_change_official_values(live, boundary):
    hidden, visible = governed_result(live), governed_result(live)
    original = {
        item["plan_id"]: historical_state(live, item["programme"], item["period"])
        for item in (hidden, visible)
    }
    for item in (hidden, visible):
        for result_id in item["results"]:
            row = expect(live.request(live.path("calculated-results", result_id), actor="reviewer"), 200)
            assert row["data"]["value"] == "46.363636363636"
    guard = (
        synthetic_current_classification(live, hidden["plan_id"])
        if boundary == "CLASSIFICATION"
        else synthetic_current_head_restriction(live, hidden["plan_id"])
        if boundary == "HEAD_REVISION"
        else scoped_programme(live, "reviewer", visible["plan_id"], "collection-plans.read")
    )
    with guard:
        for result_id in hidden["results"]:
            expect(live.request(live.path("calculated-results", result_id), actor="reviewer"), 404)
        items = {item["object_id"]: item for item in listed_results(live, hidden["results"])}
        assert not set(hidden["results"]) & set(items)
        for result_id in visible["results"]:
            assert items[result_id]["data"]["value"] == "46.363636363636"
            row = expect(live.request(live.path("calculated-results", result_id), actor="reviewer"), 200)
            assert row["data"]["value"] == items[result_id]["data"]["value"]
        assert items[visible["results"][1]]["data"]["mode"] == "OFFICIAL"
        for item in (hidden, visible):
            assert historical_state(live, item["programme"], item["period"]) == original[item["plan_id"]]
    for item in (hidden, visible):
        assert historical_state(live, item["programme"], item["period"]) == original[item["plan_id"]]


def test_existing_signed_cursor_rejects_tampering_and_changed_current_authority(live):
    visible = governed_result(live)
    first = expect(live.request(live.path("calculated-results"), actor="reviewer", params={"limit": 1}), 200)
    cursor = first["next_cursor"]
    assert cursor
    forged = cursor[:-1] + ("0" if cursor[-1] != "0" else "1")
    invalid = expect(
        live.request(
            live.path("calculated-results"), actor="reviewer", params={"limit": 1, "cursor": forged}
        ),
        400,
    )
    assert invalid["code"] == "INVALID_CURSOR"
    with scoped_programme(live, "reviewer", visible["plan_id"], "collection-plans.read"):
        changed = expect(
            live.request(
                live.path("calculated-results"),
                actor="reviewer",
                params={"limit": 1, "cursor": cursor},
            ),
            400,
        )
        assert changed["code"] == "INVALID_CURSOR"
