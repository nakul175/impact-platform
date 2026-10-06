"""Current authority must control frozen blocks without rewriting snapshot arithmetic.

Prepared for the bounded shared-core fix. Classification is restored; current-head restriction
uses two valid appended synthetic revisions, never an edit to an immutable old revision. These
fixtures keep RLS, immutable triggers and historical result/target/close payloads enabled/intact.
"""

from contextlib import contextmanager
from uuid import uuid4

import pytest

from prepared_dashboard_visibility_repro import synthetic_current_classification
from test_dashboards import calculate, card, close, measure, ratio_source, series, target
from test_live_application import expect
from test_planning import tva


def append_head(live, obj, original_revision, predecessor, restriction):
    """Append a fixture revision with identical canonical payload/hash and explicit visibility."""
    tenant, new = live.fixture["tenant_a"], str(uuid4())
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        c.execute(
            "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,"
            "predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,"
            "restriction_state,revision_number) "
            "SELECT tenant_id,object_id,%s,object_type,%s,schema_version,payload,payload_sha256,"
            "author_id,now(),%s,(SELECT max(n.revision_number)+1 FROM impact.object_revision n "
            "WHERE n.tenant_id=v.tenant_id AND n.object_id=v.object_id) "
            "FROM impact.object_revision v WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
            (new, predecessor, restriction, tenant, obj, original_revision),
        )
        c.execute(
            "UPDATE impact.object_registry SET head_revision=%s,updated_at=now() "
            "WHERE tenant_id=%s AND object_id=%s",
            (new, tenant, obj),
        )
    return new


@contextmanager
def synthetic_current_head_restriction(live, obj):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        original = c.execute(
            "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
            (tenant, obj),
        ).fetchone()["head_revision"]
    restricted = append_head(live, obj, original, original, "RESTRICTED")
    try:
        yield
    finally:
        # Restore visibility through another immutable revision; do not rewind the head/history.
        append_head(live, obj, original, restricted, "AVAILABLE")


def historical_state(live, programme, period):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        binding = c.execute(
            "SELECT snapshot_id,snapshot_revision,close_revision FROM impact.period_snapshot_binding "
            "WHERE tenant_id=%s AND programme_id=%s AND period_id=%s ORDER BY snapshot_version DESC LIMIT 1",
            (tenant, programme["object_id"], period["object_id"]),
        ).fetchone()
        revisions = c.execute(
            "SELECT revision_id,payload,payload_sha256,restriction_state FROM impact.object_revision "
            "WHERE tenant_id=%s AND revision_id IN ("
            "SELECT result_revision FROM impact.official_result_snapshot WHERE tenant_id=%s AND snapshot_id=%s "
            "UNION SELECT target_revision FROM impact.target_binding WHERE tenant_id=%s AND period_id=%s "
            "UNION SELECT %s::uuid UNION SELECT %s::uuid) ORDER BY revision_id",
            (
                tenant,
                tenant,
                binding["snapshot_id"],
                tenant,
                period["object_id"],
                binding["snapshot_revision"],
                binding["close_revision"],
            ),
        ).fetchall()
    return binding, revisions


@pytest.fixture
def frozen_visibility(live):
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "50", "100")
    ratio_source(live, indicator, keys[1], "1", "10")
    calculate(live, indicator, period)
    goal = target(live, indicator, period, "50")
    close(live, programme, period)
    dashboard, row = card(live, programme, indicator, period, actor="reviewer")
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        plan = c.execute(
            "SELECT object_id FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (live.fixture["tenant_a"], row["coverage"]["plan_revision"]),
        ).fetchone()
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        pinned_result = c.execute(
            "SELECT result_id FROM impact.official_result_snapshot "
            "WHERE tenant_id=%s AND snapshot_id=%s AND indicator_id=%s",
            (live.fixture["tenant_a"], dashboard["snapshot"]["snapshot_id"], indicator["object_id"]),
        ).fetchone()
        assert str(pinned_result["result_id"]) == row["official"]["result_id"]
    return (
        programme,
        indicator,
        period,
        {
            "Target": goal["object_id"],
            "CollectionPlan": str(plan["object_id"]),
            "CalculatedResult": row["official"]["result_id"],
        },
    )


def visible_views(live, programme, indicator, period):
    dashboard, row = card(live, programme, indicator, period, actor="reviewer")
    point = next(
        p
        for p in series(live, indicator, actor="reviewer")["points"]
        if p["period_id"] == period["object_id"]
    )
    planning = next(
        r
        for r in tva(live, programme["object_id"], actor="reviewer", period_id=period["object_id"])["rows"]
        if r["indicator_id"] == indicator["object_id"]
    )
    return dashboard, row, point, planning


@pytest.mark.parametrize("visibility", ["CLASSIFICATION", "HEAD_REVISION"])
@pytest.mark.parametrize(
    "kind,route",
    [
        ("Target", "targets"),
        ("CollectionPlan", "collection-plans"),
        ("CalculatedResult", "calculated-results"),
    ],
)
def test_current_restriction_withholds_frozen_blocks_and_never_recomputes_historical_values(
    live, frozen_visibility, kind, route, visibility
):
    programme, indicator, period, objects = frozen_visibility
    obj = objects[kind]
    original = historical_state(live, programme, period)
    _, initial, _, _ = visible_views(live, programme, indicator, period)
    assert initial["official"]["value"] == "46.363636363636"
    assert initial["target"]["value"] == "50" and initial["coverage"]["approved_count"] == 2
    boundary = (
        synthetic_current_classification(live, obj)
        if visibility == "CLASSIFICATION"
        else synthetic_current_head_restriction(live, obj)
    )
    with boundary:
        expect(live.request(live.path(route, obj), actor="reviewer"), 404)
        dashboard, row, point, planning = visible_views(live, programme, indicator, period)
        assert dashboard["snapshot"]["snapshot_id"] == str(original[0]["snapshot_id"])
        if kind == "Target":
            assert row["target"] is None and point["target"] is None and planning["target"] is None
            assert row["status"] is None and point["status"] is None
            assert (
                row["official"]["value"]
                == point["official"]["value"]
                == planning["actual"]["value"]
                == "46.363636363636"
            )
        elif kind == "CollectionPlan":
            coverage = row["coverage"]
            assert coverage["applicability"] == "UNAVAILABLE"
            assert coverage["expected_count"] is None and coverage["approved_count"] is None
            assert coverage["approval_percent"] is None and coverage["plan_revision"] is None
            assert row["official"]["value"] == "46.363636363636"
        else:
            assert row["official"] is None and point["official"] is None
            assert planning["actual"]["mode"] == "NONE" and planning["actual"]["value"] is None
        assert historical_state(live, programme, period) == original
    expect(live.request(live.path(route, obj), actor="reviewer"), 200)
    _, restored, _, _ = visible_views(live, programme, indicator, period)
    assert restored["official"]["value"] == "46.363636363636"
    assert restored["target"]["value"] == "50" and restored["coverage"]["approved_count"] == 2
    assert historical_state(live, programme, period) == original
