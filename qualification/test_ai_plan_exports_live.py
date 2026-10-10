"""Exact internal-copy API checks with a reviewed tenant and ordinary manager assignment.

Authority is created through the real owner/second-admin/operator bootstrap and
independent role-request review. Storage-only legacy fixtures are labelled and
retain immutable guards; they do not stand in for the reviewed upgrade proof.
"""

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from uuid import uuid4

import psycopg
import pytest
from starlette.requests import Request

from impact_api import ai_content_archives as archives
from impact_api import ai_plan_exports as exports
from impact_api.ai_adoption_plans import KIND
from impact_api.ai_plan_exports import AIPlanExports
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.contracts import validate
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database, audit, authorize, context, write
from test_access_bootstrap import action as bootstrap_action, propose as bootstrap_propose
from test_administration import command, expect, expiry
from test_ai_adoption_plans import plan
from test_ai_planning_inputs import planning_plan

TABLES = (
    "object_registry",
    "object_revision",
    "audit_event_current",
    "outbox_event",
    "outbox_delivery",
    "operation_receipt",
    "ai_plan_export_issuance",
    "ai_plan_export_bytes",
    "ai_content_snapshot",
    "ai_plan_content_binding",
    "ai_advisory_request",
    "ai_advisory_result",
)


@pytest.fixture(scope="module", autouse=True)
def export_migration_ledger(live):
    root = Path(__file__).resolve().parents[1]
    with live.db() as c:
        rows = c.execute("SELECT version,sha256 FROM impact.schema_migration ORDER BY version").fetchall()
    applied = []
    for row in rows:
        source = next((root / "infrastructure/migrations").glob(f"{row['version']:04d}_*.sql"))
        applied.append(
            {
                "version": row["version"],
                "file": source.name,
                "applied_sha256": row["sha256"],
                "current_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        )
    native = os.environ.get("IMPACT_NATIVE_TEST") == "1"
    environment = "native" if native else "pglite"
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "environment": "NATIVE_POSTGRESQL" if native else "PGLITE",
        "scope": "Actual applied migration ledger for focused internal-copy API checks; not acceptance",
        "migrations": applied,
    }
    path = root / f"docs/evidence/sprint-0.34-ai-plan-export-{environment}-applied-migrations.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    assert len(applied) == 43
    assert all(row["applied_sha256"] == row["current_source_sha256"] for row in applied)


def base(live, tenant, route="ai-enablement/plans"):
    return live.path(route, tenant=tenant["tenant_id"])


@pytest.fixture(scope="module")
def export_tenant(live):
    requested, tenant, _, _ = bootstrap_propose(live, role_names=["PROGRAMME_MANAGER", "ANALYST"])
    accepted = bootstrap_action(live, requested, "accept", "reviewer")
    approved = bootstrap_action(live, accepted, "approve", "admin")
    roles = expect(live.request(base(live, tenant, "role-templates"), actor="reviewer"), 200)["items"]
    manager = next(row for row in roles if row["name"] == "PROGRAMME_MANAGER")
    members = expect(live.request(base(live, tenant, "membership-directory"), actor="reviewer"), 200)["items"]
    member = next(row for row in members if row["object_id"] == approved["second_membership_id"])
    request = expect(
        live.request(
            base(live, tenant, "access-requests"),
            actor="reviewer",
            method="POST",
            body=command(
                {
                    "membership_id": member["object_id"],
                    "expected_membership_revision": member["revision_id"],
                    "role_template_id": manager["object_id"],
                    "scope_ids": [approved["scope_id"]],
                    "expires_at": expiry(20),
                    "reason": "Deliberate internal planning-copy qualification role",
                }
            ),
        ),
        200,
    )
    path = base(live, tenant, "access-requests") + "/" + request["object_id"] + "/actions/approve"
    expect(
        live.request(
            path,
            actor="reviewer",
            method="POST",
            body=command({"reason": "Self approval remains refused"}, request["revision_id"]),
        ),
        403,
    )
    expect(
        live.request(
            path,
            actor="author",
            method="POST",
            body=command({"reason": "Independent review of manager scope"}, request["revision_id"]),
        ),
        200,
    )
    capabilities = expect(live.request(base(live, tenant, "me/access"), actor="reviewer"), 200)[
        "capabilities"
    ]
    assert {"ai.enablement.read", "ai.enablement.manage", "ai.enablement.export"} <= set(capabilities)
    return {**tenant, "bootstrap": approved}


def saved(live, tenant, data=None, actor="reviewer"):
    return expect(
        live.request(base(live, tenant), actor=actor, method="POST", body=command(data or plan())), 201
    )


def export_path(live, tenant, row):
    return base(live, tenant) + "/" + row["object_id"] + "/revisions/" + row["revision_id"] + "/exports"


def request_body():
    return command({"format": "JSON", "restriction": "INTERNAL_SELF", "acknowledged": True})


def issue(live, tenant, row, body=None, actor="reviewer", status=200, **kwargs):
    response = live.request(
        export_path(live, tenant, row), actor=actor, method="POST", body=body or request_body(), **kwargs
    )
    result = expect(response, status)
    if status == 200:
        validate("AIPlanExport", result)
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        raw = result["content"].encode("utf-8")
        assert len(raw) == result["manifest"]["size_bytes"] == result["receipt"]["byte_count"]
        assert (
            hashlib.sha256(raw).hexdigest()
            == result["manifest"]["content_sha256"]
            == result["receipt"]["content_sha256"]
        )
        assert result["receipt"]["saved_at"] == result["manifest"]["generated_at"]
        assert result["receipt"]["replay_until"] == result["manifest"]["replay_expires_at"]
        assert result["manifest"]["plan_id"] == row["object_id"]
        assert result["manifest"]["revision_id"] == row["revision_id"]
    return result


def counts(live, tenant):
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant["tenant_id"],))
        return {
            name: c.execute(
                "SELECT count(*) AS n FROM impact." + name + " WHERE tenant_id=%s", (tenant["tenant_id"],)
            ).fetchone()["n"]
            for name in TABLES
        }


def current(live, tenant, row, actor="reviewer"):
    return expect(live.request(base(live, tenant) + "/" + row["object_id"], actor=actor), 200)


def principal(live, tenant, actor):
    with live.db() as c:
        return str(
            c.execute(
                "SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
                (tenant["tenant_id"], live.fixture["actors"][actor]["identity_id"]),
            ).fetchone()["principal_id"]
        )


@contextmanager
def narrowed(live, tenant, capability, actor="reviewer", object_id=None):
    """Only narrow already reviewed synthetic grants; no capability is added by a fixture."""
    subject, scope = principal(live, tenant, actor), str(uuid4())
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant["tenant_id"],))
        grants = c.execute(
            "SELECT * FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability=%s AND purpose IS NULL",
            (tenant["tenant_id"], subject, capability),
        ).fetchall()
        assert grants
        if object_id:
            version = c.execute(
                "SELECT predicate_version FROM impact.scope_definition WHERE tenant_id=%s AND scope_id=%s",
                (tenant["tenant_id"], grants[0]["scope_id"]),
            ).fetchone()["predicate_version"]
            c.execute(
                "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) VALUES(%s,%s,'OBJECT_SET',%s)",
                (tenant["tenant_id"], scope, version),
            )
            c.execute(
                "INSERT INTO impact.scope_member VALUES(%s,%s,%s)", (tenant["tenant_id"], scope, object_id)
            )
            c.execute(
                "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
                (scope, tenant["tenant_id"], [str(g["object_id"]) for g in grants]),
            )
        else:
            c.execute(
                "UPDATE impact.grant_current SET purpose='QUALIFICATION_ONLY' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
                (tenant["tenant_id"], [str(g["object_id"]) for g in grants]),
            )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant["tenant_id"],))
            for grant in grants:
                c.execute(
                    "UPDATE impact.grant_current SET scope_id=%s,purpose=%s WHERE tenant_id=%s AND object_id=%s",
                    (grant["scope_id"], grant["purpose"], tenant["tenant_id"], grant["object_id"]),
                )


def engine(live, actor="reviewer"):
    settings = Settings(**live.config)
    db = Database(settings)
    identity = Auth(settings, db).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token(actor)).encode())],
            }
        )
    )
    return AIPlanExports(Service(settings, db)), db, identity


def legacy_saved(live, tenant, data=None):
    """Storage-valid historical payload, through the governed actual application writer.

    This models old saved inputs without manufacturing an archive, using the
    current reviewed read/manage authority. It is not an exposed legacy command.
    """
    api, db, identity = engine(live)
    data = deepcopy(data or planning_plan())
    data["learning_completed"] = ["saved-legacy-alias", "saved-retired-key"]
    data["solution_ids"] = ["saved-retired-solution"]
    data["content_versions"] = {
        "catalog": "saved-legacy-catalog",
        "solutions": "saved-legacy-solutions",
        "practice": "saved-unavailable-practice",
    }
    data["impact_reference"] = {"private_core_identifier": str(uuid4())}
    data["profile"]["future_proof"] = "PRIVATE_PROOF_MARKER"
    data["planning"]["task_practice"]["private_provider"] = "PRIVATE_PROOF_MARKER"
    with db.transaction(tenant["tenant_id"]) as c:
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant["tenant_id"],))
        ctx = context(c, identity, tenant["tenant_id"], write=True)
        authorize(c, ctx, "create_ai_adoption_plan", hidden=True)
        authorize(c, ctx, "get_ai_adoption_plan", hidden=True)
        row = write(c, ctx, KIND, data, "Draft")
        audit(c, ctx, "create_ai_adoption_plan", row, str(uuid4()))
    return row, data


def test_one_issuance_binds_original_bytes_audit_receipt_and_nondelivery_intent(live, export_tenant):
    tenant, row = export_tenant, saved(live, export_tenant, planning_plan())
    before, old = counts(live, tenant), current(live, tenant, row)
    body = request_body()
    result = issue(live, tenant, row, body)
    after = counts(live, tenant)
    additions = {
        "object_registry",
        "object_revision",
        "audit_event_current",
        "outbox_event",
        "outbox_delivery",
        "operation_receipt",
        "ai_plan_export_issuance",
        "ai_plan_export_bytes",
    }
    assert after == {name: count + int(name in additions) for name, count in before.items()}
    assert current(live, tenant, row) == old
    document = json.loads(result["content"])
    assert document["plan"]["data"] == old["data"]
    assert document["record_status"] == "Draft" and document["restriction"] == "INTERNAL_SELF"
    assert document["guidance"]["status"] == result["manifest"]["guidance_status"] == "COMPLETE"
    assert document["guidance"]["catalog"]["payload"] == archives.catalog()
    assert "impact_reference" not in document["plan"]["data"]
    assert document["declared_components"] == ["PUBLIC_PLAN", "ARCHIVED_GUIDANCE"]
    assert set(result["receipt"]) == {
        "object_id",
        "revision_id",
        "business_state",
        "operation_id",
        "correlation_id",
        "saved_at",
        "content_sha256",
        "byte_count",
        "replay_until",
    }
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant["tenant_id"],))
        metadata = c.execute(
            "SELECT * FROM impact.ai_plan_export_issuance WHERE tenant_id=%s AND issuance_id=%s",
            (tenant["tenant_id"], result["receipt"]["object_id"]),
        ).fetchone()
        assert metadata["issuer_slot"] >= 1 and metadata["operation_id"] == uuid_from(body["operation_id"])
        original = c.execute(
            "SELECT body FROM impact.ai_plan_export_bytes WHERE tenant_id=%s AND issuance_id=%s",
            (tenant["tenant_id"], metadata["issuance_id"]),
        ).fetchone()
        assert bytes(original["body"]) == result["content"].encode()
        audit_row = c.execute(
            "SELECT * FROM impact.audit_event_current WHERE tenant_id=%s AND object_id=%s",
            (tenant["tenant_id"], metadata["issuance_id"]),
        ).fetchone()
        assert audit_row["action_type"] == "issue_ai_plan_export" and audit_row["outcome"] == "SUCCEEDED"
        assert str(audit_row["object_reference"]) == row["object_id"]
        assert str(audit_row["revision_id"]) == result["receipt"]["revision_id"]
        outbox = c.execute(
            "SELECT payload FROM impact.outbox_event WHERE tenant_id=%s AND event_id=%s",
            (tenant["tenant_id"], metadata["outbox_event_id"]),
        ).fetchone()["payload"]
        assert (
            outbox["aggregate_type"] == "AuditEvent"
            and outbox["aggregate_id"] == result["receipt"]["object_id"]
        )
        assert (
            outbox["aggregate_revision"] == result["receipt"]["revision_id"]
            and outbox["aggregate_sequence"] == 1
        )
        delivery = c.execute(
            "SELECT * FROM impact.outbox_delivery WHERE tenant_id=%s AND event_id=%s",
            (tenant["tenant_id"], metadata["outbox_event_id"]),
        ).fetchone()
        assert delivery["channel"] is None and delivery["state"] == "PENDING" and delivery["sent_at"] is None
    assert issue(live, tenant, row, body) == result
    assert counts(live, tenant) == after


def uuid_from(value):
    from uuid import UUID

    return UUID(value)


def test_saved_revision_is_deliberate_and_replay_does_not_follow_a_new_head(live, export_tenant):
    tenant, row = export_tenant, saved(live, export_tenant)
    body, old = request_body(), current(live, tenant, row)
    original = issue(live, tenant, row, body)
    newer = expect(
        live.request(
            base(live, tenant) + "/" + row["object_id"],
            actor="reviewer",
            method="PUT",
            body=command({**plan(), "title": "New saved title"}, row["revision_id"]),
        ),
        200,
    )
    before = counts(live, tenant)
    assert issue(live, tenant, row, body) == original
    assert counts(live, tenant) == before
    assert json.loads(original["content"])["plan"]["data"] == old["data"]
    second = issue(live, tenant, newer)
    assert second["manifest"]["revision_id"] == newer["revision_id"]
    assert second["manifest"]["title"] == "New saved title"
    assert second["manifest"]["content_sha256"] != original["manifest"]["content_sha256"]
    issue(live, tenant, newer, body, status=409)


def test_legacy_unknown_fields_are_excluded_and_saved_strings_preserved_without_reconstruction(
    live, export_tenant
):
    row, source = legacy_saved(live, export_tenant)
    before = counts(live, export_tenant)
    result = issue(live, export_tenant, row)
    document = json.loads(result["content"])
    public = document["plan"]["data"]
    assert public["learning_completed"] == source["learning_completed"]
    assert public["solution_ids"] == source["solution_ids"]
    assert public["content_versions"] == source["content_versions"]
    assert public["planning"]["task_practice"]["brief"] == source["planning"]["task_practice"]["brief"]
    assert (
        "PRIVATE_PROOF_MARKER" not in result["content"] and "private_core_identifier" not in result["content"]
    )
    assert result["manifest"]["guidance_status"] == document["guidance"]["status"] == "UNAVAILABLE"
    assert document["guidance"]["snapshot_sha256"] is document["guidance"]["captured_at"] is None
    assert all(document["guidance"][name]["payload"] is None for name in ("catalog", "solutions", "practice"))
    assert counts(live, export_tenant)["ai_plan_content_binding"] == before["ai_plan_content_binding"]


def test_partial_archive_preserves_known_catalog_and_truthful_unavailable_practice(live, export_tenant):
    old, _ = legacy_saved(live, export_tenant)
    updated = expect(
        live.request(
            base(live, export_tenant) + "/" + old["object_id"],
            actor="reviewer",
            method="PUT",
            body=command(plan(), old["revision_id"]),
        ),
        200,
    )
    guide = expect(
        live.request(
            base(live, export_tenant)
            + "/"
            + updated["object_id"]
            + "/revisions/"
            + updated["revision_id"]
            + "/guidance",
            actor="reviewer",
        ),
        200,
    )
    result = issue(live, export_tenant, updated)
    document = json.loads(result["content"])
    assert result["manifest"]["guidance_status"] == guide["status"] == "PARTIAL"
    assert document["guidance"] == guide
    assert guide["catalog"]["payload"] == archives.catalog()
    assert guide["solutions"]["payload"] == archives.solutions_catalog()
    assert guide["practice"] == {
        "status": "UNAVAILABLE",
        "content_version": "saved-unavailable-practice",
        "payload": None,
    }


def test_storage_valid_saved_decimal_lexemes_survive_without_current_recalculation(live, export_tenant):
    data = planning_plan()
    line = data["planning"]["cost_comparison"]["offers"][0]["lines"][0]
    line.update(quantity="1.00", unit_amount="2.500")
    row, _ = legacy_saved(live, export_tenant, data)
    result = issue(live, export_tenant, row)
    retained = json.loads(result["content"])["plan"]["data"]["planning"]["cost_comparison"]
    assert retained["offers"][0]["lines"][0]["quantity"] == "1.00"
    assert retained["offers"][0]["lines"][0]["unit_amount"] == "2.500"


@pytest.mark.parametrize("restriction", ["RESTRICTED", "REMOVED"])
def test_exact_unavailable_old_pin_is_opaque_despite_a_readable_appended_head(
    live, export_tenant, restriction
):
    row = saved(live, export_tenant)
    original = issue(live, export_tenant, row)
    tenant, predecessor = export_tenant["tenant_id"], row["revision_id"]
    revisions = []
    # Append-only storage negative, not an operated privacy removal. No old
    # payload changes, trigger disabling, head rewind, or invented archive.
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        for state in (restriction, "AVAILABLE"):
            new = str(uuid4())
            c.execute(
                "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,"
                "predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,"
                "restriction_state,revision_number) "
                "SELECT tenant_id,object_id,%s,object_type,%s,schema_version,"
                "CASE WHEN %s='REMOVED' THEN NULL ELSE payload END,payload_sha256,"
                "author_id,statement_timestamp(),%s,(SELECT max(n.revision_number)+1 "
                "FROM impact.object_revision n WHERE n.tenant_id=v.tenant_id AND n.object_id=v.object_id) "
                "FROM impact.object_revision v WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
                (new, predecessor, state, state, tenant, row["object_id"], row["revision_id"]),
            )
            c.execute(
                "UPDATE impact.object_registry SET head_revision=%s,updated_at=statement_timestamp() "
                "WHERE tenant_id=%s AND object_id=%s",
                (new, tenant, row["object_id"]),
            )
            predecessor = new
            revisions.append(new)
    assert current(live, export_tenant, row)["revision_id"] == revisions[1]
    before = counts(live, export_tenant)
    hidden = issue(live, export_tenant, {**row, "revision_id": revisions[0]}, status=404)
    missing = issue(live, export_tenant, {**row, "revision_id": str(uuid4())}, status=404)
    assert hidden["code"] == missing["code"] == "RESOURCE_UNAVAILABLE"
    assert counts(live, export_tenant) == before
    assert (
        json.loads(issue(live, export_tenant, row)["content"])["plan"]["data"]
        == json.loads(original["content"])["plan"]["data"]
    )


def test_expired_owner_only_storage_fixture_retains_dedup_but_deadline_hides_bytes(
    live, export_tenant, monkeypatch
):
    row, body = saved(live, export_tenant), request_body()
    api, db, identity = engine(live)
    tenant = export_tenant["tenant_id"]
    past = datetime.now(timezone.utc) - timedelta(days=8)
    # A trusted owner fixture constructs a complete, storage-valid expired
    # issuance. Ordinary HTTP issuance always uses the current DB clock.
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        ctx = context(c, identity, tenant, write=True)
        authorize(c, ctx, "issue_ai_plan_export", row["object_id"], hidden=True)
        authorize(c, ctx, "get_ai_adoption_plan", row["object_id"], hidden=True)
        c.execute("SELECT set_config('impact.ai_plan_export_principal',%s,true)", (ctx.principal_id,))
        source = c.execute(
            "SELECT payload,payload_sha256,schema_version,created_at FROM impact.object_revision "
            "WHERE tenant_id=%s AND revision_id=%s",
            (tenant, row["revision_id"]),
        ).fetchone()
        with monkeypatch.context() as patch:
            patch.setattr(exports, "observed", lambda connection: past)
            original = api._issue(
                c,
                ctx,
                row["object_id"],
                row["revision_id"],
                source,
                body,
                exports.hash_data(
                    [
                        "issue_ai_plan_export",
                        tenant,
                        ctx.principal_id,
                        row["object_id"],
                        row["revision_id"],
                        body,
                    ]
                ),
                str(uuid4()),
            )
    before = counts(live, export_tenant)
    expired = issue(live, export_tenant, row, body, status=409)
    assert expired["code"] == "IDEMPOTENCY_EXPIRED"
    assert counts(live, export_tenant) == before
    with db.transaction(tenant) as c:
        ctx = context(c, identity, tenant)
        c.execute("SELECT set_config('impact.ai_plan_export_principal',%s,true)", (ctx.principal_id,))
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.ai_plan_export_issuance WHERE tenant_id=%s AND issuance_id=%s",
                (tenant, original["receipt"]["object_id"]),
            ).fetchone()["n"]
            == 1
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.ai_plan_export_bytes WHERE tenant_id=%s AND issuance_id=%s",
                (tenant, original["receipt"]["object_id"]),
            ).fetchone()["n"]
            == 0
        )
    issue(live, export_tenant, row)  # A new deliberate operation can issue a new current copy.


@pytest.mark.parametrize("capability", ["ai.enablement.export", "ai.enablement.read"])
def test_separate_capability_revocation_blocks_issue_and_exact_replay(live, export_tenant, capability):
    row, body = saved(live, export_tenant), request_body()
    original = issue(live, export_tenant, row, body)
    before = counts(live, export_tenant)
    with narrowed(live, export_tenant, capability):
        issue(live, export_tenant, row, body, status=404)
        issue(live, export_tenant, row, status=404)
        if capability == "ai.enablement.export":
            assert current(live, export_tenant, row)["revision_id"] == row["revision_id"]
    assert counts(live, export_tenant) == before
    assert issue(live, export_tenant, row, body) == original


@pytest.mark.parametrize("capability", ["ai.enablement.read", "ai.enablement.export"])
def test_object_scope_is_current_and_both_read_and_export_must_cover_exact_plan(
    live, export_tenant, capability
):
    allowed, hidden = saved(live, export_tenant), saved(live, export_tenant)
    hidden_body = request_body()
    issue(live, export_tenant, hidden, hidden_body)
    with narrowed(live, export_tenant, capability, object_id=allowed["object_id"]):
        issue(live, export_tenant, allowed)
        denied = issue(live, export_tenant, hidden, hidden_body, status=404)
        missing = issue(
            live, export_tenant, {"object_id": str(uuid4()), "revision_id": str(uuid4())}, status=404
        )
        assert denied["code"] == missing["code"] == "RESOURCE_UNAVAILABLE"


@pytest.mark.parametrize("actor", ["other_tenant", "revoked", "partner", "admin", None])
def test_other_tenant_removed_member_and_uninvolved_operator_cannot_issue(live, export_tenant, actor):
    row = saved(live, export_tenant)
    before = counts(live, export_tenant)
    result = issue(live, export_tenant, row, actor=actor, status=401 if actor is None else 404)
    assert result["code"] in {"RESOURCE_UNAVAILABLE", "AUTH_REQUIRED"}
    assert counts(live, export_tenant) == before


@pytest.mark.parametrize(
    "mutation",
    [
        lambda b: b.update(expected_revision=str(uuid4())),
        lambda b: b.update(format="JSON"),
        lambda b: b["data"].update(format="PDF"),
        lambda b: b["data"].update(restriction="EXTERNAL"),
        lambda b: b["data"].update(acknowledged=False),
        lambda b: b["data"].update(recipient=str(uuid4())),
        lambda b: b["data"].update(provider_secret="synthetic private marker"),
    ],
)
def test_closed_internal_only_request_refuses_without_domain_writes(live, export_tenant, mutation):
    row, body = saved(live, export_tenant), request_body()
    mutation(body)
    before = counts(live, export_tenant)
    issue(live, export_tenant, row, body, status=422)
    assert counts(live, export_tenant) == before


def test_fresh_signed_authentication_is_checked_again_on_replay(live, export_tenant):
    import time

    row, body = saved(live, export_tenant), request_body()
    issue(live, export_tenant, row, body)
    token = live.signed(live.fixture["actors"]["reviewer"]["identity_id"], auth_time=time.time() - 301)
    before = counts(live, export_tenant)
    response = live.request(
        export_path(live, export_tenant, row),
        actor=None,
        method="POST",
        body=body,
        headers={"Authorization": "Bearer " + token},
    )
    result = expect(response, 403)
    assert result["reason_code"] == "FRESH_AUTHENTICATION_REQUIRED"
    assert counts(live, export_tenant) == before


@pytest.mark.parametrize("point", ["metadata", "bytes", "intent", "receipt"])
def test_real_transaction_rolls_back_every_written_component_on_late_failure(
    live, export_tenant, monkeypatch, point
):
    row, body = saved(live, export_tenant), request_body()
    api, db, identity = engine(live)
    original_transaction = db.transaction
    before = counts(live, export_tenant)
    trigger = {
        "metadata": "INSERT INTO impact.ai_plan_export_issuance",
        "bytes": "INSERT INTO impact.ai_plan_export_bytes",
        "intent": "INSERT INTO impact.outbox_delivery",
        "receipt": "INSERT INTO impact.operation_receipt",
    }[point]

    @contextmanager
    def failed_transaction(*args, **kwargs):
        with original_transaction(*args, **kwargs) as c:

            class Connection:
                def execute(self, query, values=()):
                    result = c.execute(query, values)
                    if isinstance(query, str) and query.startswith(trigger):
                        raise DomainError("SERVICE_UNAVAILABLE", 503, reason="SYNTHETIC_EXPORT_ABORT")
                    return result

            yield Connection()

    monkeypatch.setattr(db, "transaction", failed_transaction)
    with pytest.raises(DomainError) as caught:
        api.create(
            identity, export_tenant["tenant_id"], row["object_id"], row["revision_id"], body, str(uuid4())
        )
    assert caught.value.reason == "SYNTHETIC_EXPORT_ABORT"
    assert counts(live, export_tenant) == before
    monkeypatch.setattr(db, "transaction", original_transaction)
    issue(live, export_tenant, row, body)


def test_registry_classification_hides_original_and_replay_without_erasing_retained_bytes(
    live, export_tenant
):
    row, body = saved(live, export_tenant), request_body()
    original = issue(live, export_tenant, row, body)
    with live.db() as c:
        c.execute(
            "UPDATE impact.object_registry SET classification='RESTRICTED' WHERE tenant_id=%s AND object_id=%s",
            (export_tenant["tenant_id"], row["object_id"]),
        )
    try:
        issue(live, export_tenant, row, body, status=404)
        issue(live, export_tenant, row, status=404)
        with live.db() as c:
            assert (
                c.execute(
                    "SELECT count(*) AS n FROM impact.ai_plan_export_bytes WHERE tenant_id=%s AND issuance_id=%s",
                    (export_tenant["tenant_id"], original["receipt"]["object_id"]),
                ).fetchone()["n"]
                == 1
            )
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.object_registry SET classification='INTERNAL' WHERE tenant_id=%s AND object_id=%s",
                (export_tenant["tenant_id"], row["object_id"]),
            )
    assert issue(live, export_tenant, row, body) == original


def test_original_receipt_deletion_does_not_allow_operation_reuse_or_recreation(live, export_tenant):
    row, body = saved(live, export_tenant), request_body()
    original = issue(live, export_tenant, row, body)
    with live.db() as c:
        c.execute(
            "DELETE FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='issue_ai_plan_export' AND operation_id=%s",
            (export_tenant["tenant_id"], body["operation_id"]),
        )
    # Trusted fixture-only receipt removal proves durable dedup; no operated purge claim.
    before = counts(live, export_tenant)
    assert issue(live, export_tenant, row, body) == original
    assert counts(live, export_tenant) == before
    other = saved(live, export_tenant)
    issue(live, export_tenant, other, body, status=409)


def test_storage_sql_forces_tenant_fences_insert_only_and_original_retention(live, export_tenant):
    row = saved(live, export_tenant)
    result = issue(live, export_tenant, row)
    for table in ("ai_plan_export_issuance", "ai_plan_export_bytes"):
        with live.db() as c:
            flags = c.execute(
                "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=%s::regclass",
                ("impact." + table,),
            ).fetchone()
            assert flags["relrowsecurity"] and flags["relforcerowsecurity"]
        for verb in ("UPDATE", "DELETE"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with live.db() as c:
                    suffix = " SET issuance_id=issuance_id" if verb == "UPDATE" else ""
                    c.execute(
                        verb
                        + (" impact." if verb == "UPDATE" else " FROM impact.")
                        + table
                        + suffix
                        + " WHERE tenant_id=%s AND issuance_id=%s",
                        (export_tenant["tenant_id"], result["receipt"]["object_id"]),
                    )
    assert issue(live, export_tenant, row, actor="reviewer")["manifest"]["content_sha256"]


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Actual isolated login RLS proof requires native PostgreSQL",
)
def test_actual_app_login_cannot_read_private_pointers_without_current_export_context(live, export_tenant):
    row = saved(live, export_tenant)
    result = issue(live, export_tenant, row)
    dsn = os.environ.get("IMPACT_LOGIN_DSN_APP")
    assert dsn, "No fallback owner DSN may qualify an actual login boundary"
    with psycopg.connect(dsn, prepare_threshold=None) as c:
        assert c.execute("SELECT current_user").fetchone()[0] == "impact_app_login"
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (export_tenant["tenant_id"],))
        for table in ("ai_plan_export_issuance", "ai_plan_export_bytes"):
            assert (
                c.execute(
                    "SELECT count(*) FROM impact." + table + " WHERE tenant_id=%s AND issuance_id=%s",
                    (export_tenant["tenant_id"], result["receipt"]["object_id"]),
                ).fetchone()[0]
                == 0
            )
        for table, column, value in (
            ("object_registry", "object_id", result["receipt"]["object_id"]),
            ("object_revision", "revision_id", result["receipt"]["revision_id"]),
            ("audit_event_current", "object_id", result["receipt"]["object_id"]),
            ("operation_receipt", "operation_id", result["receipt"]["operation_id"]),
        ):
            assert (
                c.execute(
                    "SELECT count(*) FROM impact." + table + " WHERE tenant_id=%s AND " + column + "=%s",
                    (export_tenant["tenant_id"], value),
                ).fetchone()[0]
                == 0
            )


def test_plans_archived_under_guidance_v1_and_v2_both_export_valid_documents(
    live, export_tenant, monkeypatch
):
    """US-DC-04: exports stay valid for a plan saved under each archive edition."""
    from impact_api.ai_adoption_plans import AIAdoptionPlans
    from impact_api.ai_plan_export_contracts import DOCUMENT_VALIDATOR
    from test_ai_content_archives import V1_SOLUTIONS_SHA256, under_guidance_v1

    settings = Settings(**live.config)
    db = Database(settings)
    identity = Auth(settings, db).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token("reviewer")).encode())],
            }
        )
    )
    with under_guidance_v1(monkeypatch):
        old = AIAdoptionPlans(Service(settings, db)).save(
            identity, export_tenant["tenant_id"], command(plan()), str(uuid4())
        )
    new = saved(live, export_tenant)
    documents = {}
    for name, row in (("v1", old), ("v2", new)):
        body = request_body()
        result = issue(live, export_tenant, row, body)
        document = json.loads(result["content"])
        assert DOCUMENT_VALIDATOR.is_valid(document)
        assert result["manifest"]["guidance_status"] == "COMPLETE"
        # Owner decision (US-DC-04 review): the package label follows the archived guidance edition,
        # and each document validates against its own published schema only.
        package = "nonprofit-ai-plan-export-" + name
        assert result["manifest"]["schema"] == document["schema_version"] == package
        validate("AIPlanExportDocument" + name.upper(), document)
        with pytest.raises(DomainError):
            validate("AIPlanExportDocument" + ("V2" if name == "v1" else "V1"), document)
        # The exact replay returns the same bytes and label.
        assert issue(live, export_tenant, row, body) == result
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (export_tenant["tenant_id"],))
            stored = c.execute(
                "SELECT package_schema_version,guidance_schema_version FROM impact.ai_plan_export_issuance "
                "WHERE tenant_id=%s AND operation_id=%s",
                (export_tenant["tenant_id"], body["operation_id"]),
            ).fetchone()
        assert dict(stored) == {
            "package_schema_version": package,
            "guidance_schema_version": "nonprofit-ai-guidance-" + name,
        }
        documents[name] = document
    with live.db() as c:
        definition = c.execute(
            "SELECT pg_get_constraintdef(oid) AS d FROM pg_constraint WHERE conrelid="
            "'impact.ai_plan_export_issuance'::regclass AND conname='ai_plan_export_issuance_package_schema_version_check'"
        ).fetchone()["d"]
    assert sorted(set(re.findall(r"'([^']*)'", definition))) == [
        "nonprofit-ai-plan-export-v1",
        "nonprofit-ai-plan-export-v2",
    ]
    assert documents["v1"]["guidance"]["snapshot_schema_version"] == archives.SCHEMA_V1
    assert documents["v2"]["guidance"]["snapshot_schema_version"] == archives.SCHEMA_V2
    v1_listings = documents["v1"]["guidance"]["solutions"]["payload"]
    assert (
        hashlib.sha256(
            json.dumps(v1_listings, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()
        == V1_SOLUTIONS_SHA256
    )
    assert not any("commercial_disclosure" in item for item in v1_listings["solutions"])
    assert documents["v2"]["guidance"]["solutions"]["payload"] == archives.solutions_catalog()
    assert all(
        item["commercial_disclosure"]["status"] == "NONE_KNOWN"
        for item in documents["v2"]["guidance"]["solutions"]["payload"]["solutions"]
    )
