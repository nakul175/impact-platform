"""Real API/database guidance history checks; synthetic facts and no external provider.

PGlite proves these sequential transactions only. Provisioned-login RLS negatives
are explicitly native-only and must not be presented as native evidence when skipped.
"""

from copy import deepcopy
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg.types.json import Jsonb
from starlette.requests import Request

import impact_api.ai_content_archives as archives
import impact_api.ai_adoption_plans as plans
from impact_api.ai_adoption_plans import AIAdoptionPlans, KIND
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.contracts import validate
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database, audit, authorize, context, hash_data, write
from test_ai_adoption_plans import plan
from test_ai_adoption_plans_live import management_disabled, save
from test_ai_content_archives import V1_SOLUTIONS_SHA256, under_guidance_v1
from test_ai_planning_inputs import planning_plan
from test_ai_planning_live import read_disabled
from test_live_application import cmd, expect

TABLES = (
    "object_registry",
    "object_revision",
    "audit_event_current",
    "outbox_event",
    "operation_receipt",
    "ai_content_snapshot",
    "ai_plan_content_binding",
    "ai_advisory_request",
    "ai_advisory_result",
)


def path(live, receipt, suffix="guidance"):
    base = live.path("ai-enablement/plans", receipt["object_id"])
    return base + "/revisions" + ("/" + receipt["revision_id"] + "/guidance" if suffix == "guidance" else "")


def counts(live):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return {
            table: c.execute(
                "SELECT count(*) AS n FROM impact." + table + " WHERE tenant_id=%s", (tenant,)
            ).fetchone()["n"]
            for table in TABLES
        }


def local_engine(live):
    settings = Settings(**live.config)
    db = Database(settings)
    identity = Auth(settings, db).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token("admin")).encode())],
            }
        )
    )
    return AIAdoptionPlans(Service(settings, db)), db, identity


def legacy_revision(live, old_practice=False):
    """A fixture representing a pre-archive build, through the ordinary governed store.

    No archive is fabricated, no immutable row is changed and no RLS/trigger is disabled.
    It is synthetic historical setup, not an exposed command or approval shortcut.
    """
    _, db, identity = local_engine(live)
    tenant = live.fixture["tenant_a"]
    data = planning_plan() if old_practice else plan()
    data["content_versions"] = {
        "catalog": "synthetic-before-archive",
        "solutions": "synthetic-before-archive",
    }
    if old_practice:
        data["content_versions"]["practice"] = "synthetic-unavailable-practice"
    with db.transaction(tenant) as c:
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        ctx = context(c, identity, tenant, write=True)
        authorize(c, ctx, "create_ai_adoption_plan", hidden=True)
        authorize(c, ctx, "get_ai_adoption_plan", hidden=True)
        receipt = write(c, ctx, KIND, deepcopy(data), "Draft")
        audit(c, ctx, "create_ai_adoption_plan", receipt, str(uuid4()))
    return receipt, data


@contextmanager
def scoped_reader(live, object_id):
    """Narrow an actual synthetic reader's existing grant, restoring it afterwards."""
    tenant, scope = live.fixture["tenant_a"], str(uuid4())
    principal = live.fixture["actors"]["reviewer"]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grant = c.execute(
            "SELECT * FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s "
            "AND capability='ai.enablement.read' AND purpose IS NULL LIMIT 1",
            (tenant, principal),
        ).fetchone()
        assert grant
        version = c.execute(
            "SELECT predicate_version FROM impact.scope_definition WHERE tenant_id=%s AND scope_id=%s",
            (tenant, grant["scope_id"]),
        ).fetchone()["predicate_version"]
        c.execute(
            "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) VALUES(%s,%s,'OBJECT_SET',%s)",
            (tenant, scope, version),
        )
        c.execute("INSERT INTO impact.scope_member VALUES(%s,%s,%s)", (tenant, scope, object_id))
        c.execute(
            "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
            (scope, tenant, grant["object_id"]),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(
                "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
                (grant["scope_id"], tenant, grant["object_id"]),
            )


def test_new_archive_is_exact_versioned_closed_and_contains_learning_without_private_plan_text(live):
    data = planning_plan()
    data["profile"]["goal"] = "Synthetic private marker 8d0a3765"
    first = save(live, data)
    before = counts(live)
    result = expect(live.request(path(live, first), actor="reviewer"), 200)
    validate("AIAdoptionPlanGuidance", result)
    assert result["status"] == "COMPLETE"
    assert result["catalog"]["payload"] == archives.catalog()
    assert result["solutions"]["payload"] == archives.solutions_catalog()
    assert result["practice"]["payload"] == archives.task_templates()
    assert len(result["catalog"]["payload"]["learning_paths"]) == 3
    assert all(len(item["lessons"]) == 4 for item in result["catalog"]["payload"]["learning_paths"])
    assert b"Synthetic private marker 8d0a3765" not in archives.canonical(result)
    assert counts(live) == before, "Historical reads must not write archives, receipts or provider work"
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        row = c.execute(
            "SELECT s.payload,s.payload_sha256 FROM impact.ai_plan_content_binding b "
            "JOIN impact.ai_content_snapshot s USING(tenant_id,snapshot_id) "
            "WHERE b.tenant_id=%s AND b.object_id=%s AND b.revision_id=%s",
            (tenant, first["object_id"], first["revision_id"]),
        ).fetchone()
        assert bytes(row["payload_sha256"]) == hash_data(row["payload"])
        assert result["snapshot_sha256"] == bytes(row["payload_sha256"]).hex()
    current = expect(
        live.request(live.path("ai-enablement/plans", first["object_id"]), actor="reviewer"), 200
    )
    validate("AIAdoptionPlan", current)
    assert current["content_compatibility"]["historical_snapshots_available"] is True


def test_save_retry_and_update_bind_exact_revisions_with_atomic_audit_outbox_receipts(live):
    tenant = live.fixture["tenant_a"]
    base = live.path("ai-enablement/plans")
    command = cmd(plan())
    first = expect(live.request(base, actor="admin", method="POST", body=command), 201)
    before_retry = counts(live)
    original = expect(live.request(path(live, first), actor="admin"), 200)
    assert expect(live.request(base, actor="admin", method="POST", body=command), 201) == first
    assert counts(live) == before_retry
    update = cmd({**plan(), "title": "Synthetic second scope"}, first["revision_id"])
    second = expect(
        live.request(base + "/" + first["object_id"], actor="admin", method="PUT", body=update), 200
    )
    assert expect(live.request(path(live, first), actor="admin"), 200) == original
    assert (
        expect(live.request(path(live, second), actor="admin"), 200)["snapshot_sha256"]
        == original["snapshot_sha256"]
    )
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        bindings = c.execute(
            "SELECT revision_id,snapshot_id FROM impact.ai_plan_content_binding WHERE tenant_id=%s AND object_id=%s",
            (tenant, first["object_id"]),
        ).fetchall()
        assert {str(row["revision_id"]) for row in bindings} == {first["revision_id"], second["revision_id"]}
        assert len({str(row["snapshot_id"]) for row in bindings}) == 1
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s "
                "AND action_type IN ('create_ai_adoption_plan','update_ai_adoption_plan')",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_id'=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=ANY(%s::uuid[])",
                (tenant, [command["operation_id"], update["operation_id"]]),
            ).fetchone()["n"]
            == 2
        )


def test_real_prior_words_remain_immutable_when_current_content_changes_in_a_new_save(live, monkeypatch):
    first = save(live)
    original = expect(live.request(path(live, first), actor="admin"), 200)
    api, _, identity = local_engine(live)
    current = archives.catalog()
    current["content_version"] = "synthetic-next-guidance-edition"
    current["learning_paths"][0]["lessons"][0]["title"] = "Later synthetic wording"
    # A genuinely new edition preserves the immutable older wording.
    monkeypatch.setattr(archives, "catalog", lambda: deepcopy(current))
    monkeypatch.setattr(plans, "CATALOG_VERSION", current["content_version"])
    second = api.save(
        identity,
        live.fixture["tenant_a"],
        cmd(plan(), first["revision_id"]),
        str(uuid4()),
        first["object_id"],
    )
    result = expect(live.request(path(live, second), actor="admin"), 200)
    assert result["catalog"]["payload"] == current
    assert result["snapshot_sha256"] != original["snapshot_sha256"]
    assert expect(live.request(path(live, first), actor="admin"), 200) == original


def test_changed_words_without_a_new_edition_are_refused_with_atomic_rollback(live, monkeypatch):
    first = save(live)
    original = expect(live.request(path(live, first), actor="admin"), 200)
    api, _, identity = local_engine(live)
    changed = archives.catalog()
    changed["learning_paths"][0]["lessons"][0]["title"] = "Synthetic forbidden edition drift"
    monkeypatch.setattr(archives, "catalog", lambda: deepcopy(changed))
    before = counts(live)
    with pytest.raises(DomainError) as refused:
        api.save(
            identity,
            live.fixture["tenant_a"],
            cmd(plan(), first["revision_id"]),
            str(uuid4()),
            first["object_id"],
        )
    assert refused.value.reason == "AI_GUIDANCE_VERSION_CHANGED"
    assert counts(live) == before
    assert expect(live.request(path(live, first), actor="admin"), 200) == original


def test_applied_migration_ledger_is_recorded_as_actual_database_evidence(live):
    # This runner can overlap source integration; report what its database actually
    # applied, not what a later working tree happens to contain.
    with live.db() as c:
        rows = c.execute("SELECT version,sha256 FROM impact.schema_migration ORDER BY version").fetchall()
    root = Path(__file__).resolve().parents[1]
    migrations = []
    for row in rows:
        file = next((root / "infrastructure/migrations").glob(f"{row['version']:04d}_*.sql"))
        migrations.append(
            {
                "version": row["version"],
                "file": file.name,
                "applied_sha256": row["sha256"],
                "current_source_sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
            }
        )
    result = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "environment": "NATIVE_POSTGRESQL" if os.environ.get("IMPACT_NATIVE_TEST") == "1" else "PGLITE",
        "scope": "Applied migration ledger observed by this qualification process; other qualification outcomes are separate",
        "migrations": migrations,
    }
    (root / "docs/evidence/nonprofit-ai-content-applied-migrations.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    archive_migration = next(row for row in migrations if row["version"] == 37)
    assert archive_migration["applied_sha256"] == archive_migration["current_source_sha256"]


def test_history_lists_actual_available_revisions_in_order_with_plan_principal_bound_cursors(live):
    first = save(live)
    current = first
    base = live.path("ai-enablement/plans", first["object_id"])
    for number in (2, 3, 4):
        current = expect(
            live.request(
                base,
                actor="admin",
                method="PUT",
                body=cmd({**plan(), "title": f"Synthetic history revision {number}"}, current["revision_id"]),
            ),
            200,
        )
    history_path = path(live, first, "history")
    before = counts(live)
    page = expect(live.request(history_path, actor="admin", params={"limit": 2}), 200)
    validate("AIAdoptionRevisionList", page)
    assert [item["revision_number"] for item in page["items"]] == [4, 3]
    assert page["next_cursor"] and "total_rows" not in page
    next_page = expect(
        live.request(history_path, actor="admin", params={"limit": 2, "cursor": page["next_cursor"]}), 200
    )
    assert [item["revision_number"] for item in next_page["items"]] == [2, 1]
    assert next_page["next_cursor"] is None
    assert counts(live) == before
    other = save(live)
    expect(
        live.request(path(live, other, "history"), actor="admin", params={"cursor": page["next_cursor"]}), 400
    )
    expect(live.request(history_path, actor="reviewer", params={"cursor": page["next_cursor"]}), 400)
    expect(live.request(history_path, actor="admin", params={"cursor": page["next_cursor"] + "forged"}), 400)


@pytest.mark.parametrize("actor", ["other_tenant", "revoked", "partner", None])
@pytest.mark.parametrize("suffix", ["guidance", "history"])
def test_current_authority_hides_guidance_and_history_from_unauthorized_callers(live, actor, suffix):
    first = save(live)
    before = counts(live)
    denied = expect(live.request(path(live, first, suffix), actor=actor), 401 if actor is None else 404)
    assert denied["code"] in {"RESOURCE_UNAVAILABLE", "AUTH_REQUIRED"}
    assert counts(live) == before


def test_read_only_can_read_both_routes_but_revocation_is_rechecked_and_history_does_not_export(live):
    first = save(live)
    with management_disabled(live, "reviewer"):
        assert expect(live.request(path(live, first), actor="reviewer"), 200)["status"] == "COMPLETE"
        assert len(expect(live.request(path(live, first, "history"), actor="reviewer"), 200)["items"]) == 1
    with read_disabled(live, "reviewer"):
        expect(live.request(path(live, first), actor="reviewer"), 404)
        expect(live.request(path(live, first, "history"), actor="reviewer"), 404)


def test_current_object_scope_fences_guidance_and_history_even_for_a_valid_tenant_reader(live):
    allowed, hidden = save(live), save(live)
    with scoped_reader(live, allowed["object_id"]):
        expect(live.request(path(live, allowed), actor="reviewer"), 200)
        expect(live.request(path(live, allowed, "history"), actor="reviewer"), 200)
        expect(live.request(path(live, hidden), actor="reviewer"), 404)
        expect(live.request(path(live, hidden, "history"), actor="reviewer"), 404)


def test_unrelated_revision_wrong_kind_and_missing_revision_are_the_same_opaque_refusal(live):
    first, second = save(live), save(live)
    base = live.path("ai-enablement/plans", first["object_id"]) + "/revisions/"
    wrong = expect(live.request(base + second["revision_id"] + "/guidance", actor="admin"), 404)
    missing = expect(live.request(base + str(uuid4()) + "/guidance", actor="admin"), 404)
    kind = expect(
        live.request(
            live.path("ai-enablement/plans", live.fixture["programme_a"])
            + "/revisions/"
            + first["revision_id"]
            + "/guidance",
            actor="admin",
        ),
        404,
    )
    assert wrong["code"] == missing["code"] == kind["code"] == "RESOURCE_UNAVAILABLE"


def test_pre_archive_revision_is_unavailable_without_inventing_wording_or_backfilling(live):
    receipt, source = legacy_revision(live)
    before = counts(live)
    result = expect(live.request(path(live, receipt), actor="admin"), 200)
    validate("AIAdoptionPlanGuidance", result)
    assert result["status"] == "UNAVAILABLE"
    assert all(
        result[name]["status"] == "UNAVAILABLE" and result[name]["payload"] is None
        for name in archives.COMPONENTS
    )
    assert result["catalog"]["content_version"] == source["content_versions"]["catalog"]
    assert result["snapshot_sha256"] is result["captured_at"] is None
    current = expect(live.request(live.path("ai-enablement/plans", receipt["object_id"]), actor="admin"), 200)
    assert current["content_compatibility"]["historical_snapshots_available"] is False
    assert counts(live) == before


def test_legacy_omission_keeps_unavailable_practice_edition_and_new_archive_is_explicitly_partial(live):
    old, source = legacy_revision(live, old_practice=True)
    base = live.path("ai-enablement/plans", old["object_id"])
    command = cmd(plan(), old["revision_id"])
    new = expect(live.request(base, actor="admin", method="PUT", body=command), 200)
    before_retry = counts(live)
    assert expect(live.request(base, actor="admin", method="PUT", body=command), 200) == new
    assert counts(live) == before_retry
    current = expect(live.request(base, actor="admin"), 200)
    assert current["data"]["planning"] == source["planning"]
    assert current["data"]["content_versions"]["practice"] == "synthetic-unavailable-practice"
    assert current["content_compatibility"]["historical_snapshots_available"] is False
    result = expect(live.request(path(live, new), actor="admin"), 200)
    validate("AIAdoptionPlanGuidance", result)
    assert result["status"] == "PARTIAL"
    assert result["practice"] == {
        "status": "UNAVAILABLE",
        "content_version": "synthetic-unavailable-practice",
        "payload": None,
    }
    assert result["catalog"]["status"] == result["solutions"]["status"] == "AVAILABLE"
    assert expect(live.request(path(live, old), actor="admin"), 200)["status"] == "UNAVAILABLE"


@pytest.mark.parametrize("update", [False, True])
def test_failure_after_archive_and_binding_rolls_back_head_revision_events_and_receipt(
    live, monkeypatch, update
):
    api, _, identity = local_engine(live)
    first = save(live) if update else None
    before = counts(live)
    original = archives.capture

    def abort_after_capture(*args, **kwargs):
        original(*args, **kwargs)
        raise DomainError("SERVICE_UNAVAILABLE", 503, reason="SYNTHETIC_ABORT_AFTER_ARCHIVE")

    monkeypatch.setattr(archives, "capture", abort_after_capture)
    with pytest.raises(DomainError) as refused:
        api.save(
            identity,
            live.fixture["tenant_a"],
            cmd(plan(), first["revision_id"] if first else None),
            str(uuid4()),
            first["object_id"] if first else None,
        )
    assert refused.value.reason == "SYNTHETIC_ABORT_AFTER_ARCHIVE"
    assert counts(live) == before
    if first:
        current = expect(
            live.request(live.path("ai-enablement/plans", first["object_id"]), actor="admin"), 200
        )
        assert current["revision_id"] == first["revision_id"]


@pytest.mark.parametrize("limit", [0, 101, "invalid"])
def test_history_query_bound_refuses_without_new_domain_work(live, limit):
    first = save(live)
    before = counts(live)
    expect(live.request(path(live, first, "history"), actor="admin", params={"limit": limit}), 422)
    assert counts(live) == before


def test_archive_sql_guards_are_insert_only_and_tenant_foreign_keys_are_enforced(live):
    first = save(live)
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        binding = c.execute(
            "SELECT * FROM impact.ai_plan_content_binding WHERE tenant_id=%s AND object_id=%s",
            (tenant, first["object_id"]),
        ).fetchone()
        for table in ("ai_content_snapshot", "ai_plan_content_binding"):
            row = c.execute(
                "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=%s::regclass",
                ("impact." + table,),
            ).fetchone()
            assert row["relrowsecurity"] and row["relforcerowsecurity"]
    for table, action in (
        ("ai_content_snapshot", "UPDATE"),
        ("ai_content_snapshot", "DELETE"),
        ("ai_plan_content_binding", "UPDATE"),
        ("ai_plan_content_binding", "DELETE"),
    ):
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with live.db() as c:
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                sql = (
                    "UPDATE impact." + table + " SET tenant_id=tenant_id"
                    if action == "UPDATE"
                    else "DELETE FROM impact." + table
                ) + " WHERE tenant_id=%s"
                c.execute(sql, (tenant,))
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
            c.execute(
                "INSERT INTO impact.ai_plan_content_binding(tenant_id,object_id,revision_id,snapshot_id) VALUES(%s,%s,%s,%s)",
                (live.fixture["tenant_b"], first["object_id"], first["revision_id"], binding["snapshot_id"]),
            )
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            programme = c.execute(
                "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                (tenant, live.fixture["programme_a"]),
            ).fetchone()
            c.execute(
                "INSERT INTO impact.ai_plan_content_binding(tenant_id,object_id,revision_id,snapshot_id) VALUES(%s,%s,%s,%s)",
                (tenant, live.fixture["programme_a"], programme["head_revision"], binding["snapshot_id"]),
            )


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Provisioned login-role boundaries require native PostgreSQL",
)
def test_native_archive_fences_and_role_grants_do_not_broaden_private_plan_access(live):
    first = save(live)
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        snapshot = c.execute(
            "SELECT snapshot_id FROM impact.ai_plan_content_binding WHERE tenant_id=%s AND object_id=%s",
            (live.fixture["tenant_a"], first["object_id"]),
        ).fetchone()["snapshot_id"]
    app_dsn = os.environ.get("IMPACT_LOGIN_DSN_APP")
    assert app_dsn, "Native qualification must provision the application login"
    with psycopg.connect(app_dsn, autocommit=True) as c:
        for table in ("ai_content_snapshot", "ai_plan_content_binding"):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                privileges = [
                    c.execute(
                        "SELECT has_table_privilege('impact_app',%s,%s)", ("impact." + table, privilege)
                    ).fetchone()[0]
                    for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE")
                ]
                assert privileges == [True, True, False, False, False]
        for tenant in (None, live.fixture["tenant_b"]):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                if tenant:
                    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                for table, key, value in (
                    ("ai_content_snapshot", "snapshot_id", snapshot),
                    ("ai_plan_content_binding", "object_id", first["object_id"]),
                ):
                    assert (
                        c.execute(
                            "SELECT count(*) FROM impact." + table + " WHERE " + key + "=%s", (value,)
                        ).fetchone()[0]
                        == 0
                    )
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            assert (
                c.execute(
                    "SELECT count(*) FROM impact.ai_plan_content_binding WHERE object_id=%s",
                    (first["object_id"],),
                ).fetchone()[0]
                == 1
            )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
                probe = {"synthetic_fence_probe": str(uuid4())}
                c.execute(
                    "INSERT INTO impact.ai_content_snapshot(tenant_id,snapshot_id,schema_version,payload,payload_sha256,captured_at) VALUES(%s,%s,%s,%s,%s,statement_timestamp())",
                    (
                        live.fixture["tenant_a"],
                        str(uuid4()),
                        archives.SCHEMA_VERSION,
                        Jsonb(probe),
                        hash_data(probe),
                    ),
                )
    for name, role in (
        ("PLATFORM", "impact_platform"),
        ("IDENTITY", "impact_identity"),
        ("WORKER", "impact_worker"),
    ):
        dsn = os.environ.get("IMPACT_LOGIN_DSN_" + name)
        assert dsn, "Native qualification must provision the " + name.lower() + " login"
        with psycopg.connect(dsn, autocommit=True) as c:
            for table in ("ai_content_snapshot", "ai_plan_content_binding"):
                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    with c.transaction():
                        c.execute("SET LOCAL ROLE " + role)
                        c.execute(
                            "SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],)
                        )
                        c.execute("SELECT count(*) FROM impact." + table)


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Parallel transaction contention requires native PostgreSQL, not serialized PGlite",
)
def test_native_competing_exact_saves_create_one_revision_binding_and_receipt(live):
    tenant, command = live.fixture["tenant_a"], cmd(plan())
    target = live.path("ai-enablement/plans")
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = [
            pool.submit(live.request, target, actor="admin", method="POST", body=command) for _ in range(2)
        ]
        receipts = [expect(response.result(), 201) for response in responses]
    assert receipts[0] == receipts[1]
    first = receipts[0]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        for table in ("object_revision", "ai_plan_content_binding"):
            assert (
                c.execute(
                    "SELECT count(*) AS n FROM impact." + table + " WHERE tenant_id=%s AND object_id=%s",
                    (tenant, first["object_id"]),
                ).fetchone()["n"]
                == 1
            )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=%s",
                (tenant, command["operation_id"]),
            ).fetchone()["n"]
            == 1
        )
    assert expect(live.request(path(live, first), actor="admin"), 200)["status"] == "COMPLETE"


# US-DC-04: guidance edition v2 (commercial disclosures) beside plans saved under v1


def bound_edition(live, receipt):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return c.execute(
            "SELECT s.schema_version,s.payload->>'schema_version' AS payload_version "
            "FROM impact.ai_plan_content_binding b JOIN impact.ai_content_snapshot s USING(tenant_id,snapshot_id) "
            "WHERE b.tenant_id=%s AND b.object_id=%s AND b.revision_id=%s",
            (tenant, receipt["object_id"], receipt["revision_id"]),
        ).fetchone()


def test_plans_saved_under_guidance_v1_and_v2_both_load_and_v2_keeps_its_disclosures(live, monkeypatch):
    api, _, identity = local_engine(live)
    # Saved as build 0.38.0 did (guidance v1, the v1 solutions edition) by the real capture path.
    with under_guidance_v1(monkeypatch):
        old = api.save(identity, live.fixture["tenant_a"], cmd(plan()), str(uuid4()))
    new = save(live)
    assert dict(bound_edition(live, old)) == {
        "schema_version": archives.SCHEMA_V1,
        "payload_version": archives.SCHEMA_V1,
    }
    assert dict(bound_edition(live, new)) == {
        "schema_version": archives.SCHEMA_V2,
        "payload_version": archives.SCHEMA_V2,
    }
    before = counts(live)
    first = expect(live.request(path(live, old), actor="reviewer"), 200)
    second = expect(live.request(path(live, new), actor="reviewer"), 200)
    validate("AIAdoptionPlanGuidance", first)
    validate("AIAdoptionPlanGuidance", second)
    assert first["status"] == second["status"] == "COMPLETE"
    assert first["snapshot_schema_version"] == archives.SCHEMA_V1
    assert second["snapshot_schema_version"] == archives.SCHEMA_V2
    assert hash_data(first["solutions"]["payload"]).hex() == V1_SOLUTIONS_SHA256
    assert not any("commercial_disclosure" in item for item in first["solutions"]["payload"]["solutions"])
    assert second["solutions"]["payload"] == archives.solutions_catalog()
    assert [
        item["commercial_disclosure"]["status"] for item in second["solutions"]["payload"]["solutions"]
    ] == ["NONE_KNOWN"] * 8
    for receipt in (old, new):
        current = expect(
            live.request(live.path("ai-enablement/plans", receipt["object_id"]), actor="reviewer"), 200
        )
        validate("AIAdoptionPlan", current)
        assert current["content_compatibility"]["historical_snapshots_available"] is True
        history = expect(live.request(path(live, receipt, "history"), actor="reviewer"), 200)
        assert history["items"][0]["historical_snapshots_available"] is True
    old_plan = expect(live.request(live.path("ai-enablement/plans", old["object_id"]), actor="reviewer"), 200)
    assert old_plan["content_compatibility"]["solutions_version_status"] == "STALE"
    assert counts(live) == before, "Reading either edition writes nothing and relabels nothing"


class _Rollback(Exception):
    pass


def test_snapshot_edition_check_admits_exactly_guidance_v1_and_v2(live):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        rows = c.execute(
            "SELECT conname,pg_get_constraintdef(oid) AS definition FROM pg_constraint "
            "WHERE conrelid='impact.ai_content_snapshot'::regclass AND contype='c' "
            "AND pg_get_constraintdef(oid) LIKE '%%schema_version%%'"
        ).fetchall()
    assert [row["conname"] for row in rows] == ["ai_content_snapshot_schema_version_check"]
    assert "nonprofit-ai-guidance-v1" in rows[0]["definition"]
    assert "nonprofit-ai-guidance-v2" in rows[0]["definition"]

    def insert(c, version):
        probe = {"synthetic_edition_probe": str(uuid4())}
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute(
            "INSERT INTO impact.ai_content_snapshot(tenant_id,snapshot_id,schema_version,payload,payload_sha256,"
            "captured_at) VALUES(%s,%s,%s,%s,%s,statement_timestamp())",
            (tenant, str(uuid4()), version, Jsonb(probe), hash_data(probe)),
        )

    # Both editions are admitted (the probe rows are rolled back: snapshots are insert-only).
    with pytest.raises(_Rollback):
        with live.db() as c:
            insert(c, archives.SCHEMA_V1)
            insert(c, archives.SCHEMA_V2)
            raise _Rollback
    for refused in ("nonprofit-ai-guidance-v3", "NONPROFIT-AI-GUIDANCE-V2", ""):
        with pytest.raises(psycopg.errors.CheckViolation):
            with live.db() as c:
                insert(c, refused)
