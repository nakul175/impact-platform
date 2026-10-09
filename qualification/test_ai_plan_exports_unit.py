"""Pure frozen projection and exact-byte internal-export security qualification."""

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest

from impact_api import ai_plan_export_contracts as contracts, ai_plan_exports as exports, store
from impact_api.ai_content_archives import DISCLAIMER as GUIDANCE_DISCLAIMER, SCHEMA_VERSION
from impact_api.ai_enablement_catalog import catalog
from impact_api.ai_solutions_catalog import solutions_catalog
from impact_api.ai_task_practice import task_templates
from impact_api.domain import DomainError

AT = datetime(2026, 10, 5, 11, 0, tzinfo=timezone.utc)
TENANT, PLAN, REVISION, ISSUANCE, PRINCIPAL, MEMBER = [str(uuid4()) for _ in range(6)]


def plan():
    return {
        "title": "Café e\u0301 — 内部の計画",
        "profile": {
            "sector": "GENERAL",
            "team_size": 4,
            "goal": "Preserve exact saved wording",
            "data_readiness": "BASIC",
            "ai_experience": "EXPERIMENTING",
            "sensitive_data": True,
        },
        "solution_ids": ["retired-solution"],
        "learning_completed": ["legacy-intro", "unknown-but-saved"],
        "procurement": {
            "requirements": "=Not a spreadsheet formula",
            "data_boundary": "Synthetic only",
            "budget_notes": "Unapproved estimate",
            "vendor_questions": "Can we leave?",
        },
        "pilot": {"success_measure": "Manual trial", "completed_actions": ["DEFINE_GOAL"]},
        "planning": {
            "cost_comparison": {
                "currency": "USD",
                "period_months": 3,
                "offers": [
                    {
                        "id": "first",
                        "name": "Saved offer",
                        "lines": [
                            {
                                "id": "line",
                                "category": "OTHER",
                                "label": "Recorded input",
                                "quantity": "1.00",
                                "unit_amount": "2.500",
                                "cadence": "MONTHLY",
                            }
                        ],
                    }
                ],
            },
            "pilot_evaluation": {
                "task_label": "Saved pilot",
                "baseline": {
                    "sample_size": 2,
                    "total_drafting_minutes": "10.00",
                    "total_review_minutes": "3.000",
                    "factual_corrections": 1,
                },
                "pilot": {
                    "sample_size": 2,
                    "total_drafting_minutes": "4.00",
                    "total_review_minutes": "3.500",
                    "factual_corrections": 2,
                },
                "comparable": False,
                "notes": "Not official impact",
            },
            "task_practice": {
                "template_id": "old-template",
                "brief": "Old manual prompt",
                "draft": "+saved draft",
                "review_notes": "Reviewed manually",
                "checked_steps": ["legacy-check"],
            },
        },
        "content_versions": {
            "catalog": "old-catalog",
            "solutions": "old-solutions",
            "practice": "old-practice",
        },
    }


def source(data=None):
    payload = data if data is not None else plan()
    return {
        "payload": payload,
        "payload_sha256": store.hash_data(payload),
        "schema_version": "1.2",
        "created_at": AT - timedelta(days=30),
    }


def guidance(status="UNAVAILABLE"):
    components = {"catalog": catalog(), "solutions": solutions_catalog(), "practice": task_templates()}
    complete = status == "COMPLETE"
    available = status != "UNAVAILABLE"
    bundle = {
        "schema_version": SCHEMA_VERSION,
        **{name: value if name != "practice" or complete else None for name, value in components.items()},
    }
    return {
        "object_id": PLAN,
        "revision_id": REVISION,
        "status": status,
        "snapshot_schema_version": SCHEMA_VERSION if available else None,
        "captured_at": exports.stamp(AT - timedelta(days=30)) if available else None,
        "snapshot_sha256": store.hash_data(bundle).hex() if available else None,
        **{
            name: {"status": "AVAILABLE", "content_version": value["content_version"], "payload": value}
            if available and (name != "practice" or complete)
            else {"status": "UNAVAILABLE", "content_version": "saved-old-edition", "payload": None}
            for name, value in components.items()
        },
        "disclaimer": GUIDANCE_DISCLAIMER,
    }


def retained(status="UNAVAILABLE", data=None):
    guide = guidance(status)
    raw = exports.render_document(TENANT, ISSUANCE, AT, PLAN, REVISION, source(data), guide)
    metadata = {
        "tenant_id": TENANT,
        "issuance_id": ISSUANCE,
        "audit_revision_id": str(uuid4()),
        "plan_object_id": PLAN,
        "plan_revision_id": REVISION,
        "principal_id": PRINCIPAL,
        "membership_id": MEMBER,
        "command_type": contracts.OPERATION,
        "operation_id": str(uuid4()),
        "request_sha256": b"x" * 32,
        "format": "JSON",
        "restriction": "INTERNAL_SELF",
        "package_schema_version": contracts.PACKAGE_VERSION,
        "renderer_version": contracts.RENDERER_VERSION,
        "guidance_status": status,
        "guidance_snapshot_id": str(uuid4()) if status != "UNAVAILABLE" else None,
        "guidance_schema_version": guide["snapshot_schema_version"],
        "guidance_sha256": bytes.fromhex(guide["snapshot_sha256"]) if status != "UNAVAILABLE" else None,
        "generated_at": AT,
        "replay_until": AT + timedelta(hours=168),
        "content_sha256": hashlib.sha256(raw).digest(),
        "byte_count": len(raw),
        "correlation_id": str(uuid4()),
        "outbox_event_id": str(uuid4()),
    }
    return metadata, raw


def test_projection_recursive_allowlist_preserves_exact_strings_and_decimal_lexemes():
    data = plan()
    data["impact_reference"] = {"secret_core_id": "private"}
    data["provider_config"] = {"secret": "private"}
    data["profile"]["identity_proof"] = "private"
    data["procurement"]["private_quote"] = "private"
    data["planning"]["cost_comparison"]["offers"][0]["vendor_secret"] = "private"
    data["planning"]["cost_comparison"]["offers"][0]["lines"][0]["credential"] = "private"
    data["planning"]["pilot_evaluation"]["baseline"]["natural_identity_id"] = "private"
    data["planning"]["task_practice"]["future_unknown"] = "private"
    data["content_versions"]["source_internal"] = "private"
    before = deepcopy(data)
    projected = exports.public_plan(data)
    assert projected == plan()
    assert data == before
    assert "private" not in store.canonical(projected).decode()
    assert projected["title"] == "Café e\u0301 — 内部の計画"
    line = projected["planning"]["cost_comparison"]["offers"][0]["lines"][0]
    assert (line["quantity"], line["unit_amount"]) == ("1.00", "2.500")


@pytest.mark.parametrize("field", ["cost_comparison", "pilot_evaluation", "task_practice"])
def test_projection_preserves_nullable_and_optional_presence(field):
    data = plan()
    data["planning"][field] = None
    assert exports.public_plan(data) == data
    data.pop("planning")
    assert "planning" not in exports.public_plan(data)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.pop("title"),
        lambda d: d.update(title=12),
        lambda d: d["profile"].update(team_size=True),
        lambda d: d["profile"].update(sensitive_data="yes"),
        lambda d: d["profile"].update(sector="FUTURE"),
        lambda d: d["planning"].update(task_practice=[]),
        lambda d: d["planning"]["cost_comparison"]["offers"][0]["lines"][0].update(quantity=1.00),
        lambda d: d["planning"]["cost_comparison"]["offers"][0]["lines"][0].update(quantity="01.00"),
        lambda d: d["planning"]["pilot_evaluation"]["baseline"].update(sample_size=0),
        lambda d: d.update(title="\ud800"),
    ],
)
def test_unrepresentable_known_source_refuses_without_coercion(mutate):
    data = plan()
    mutate(data)
    with pytest.raises(DomainError) as caught:
        exports.public_plan(data)
    assert (caught.value.status, caught.value.reason) == (503, "AI_PLAN_EXPORT_SOURCE_UNREADABLE")


@pytest.mark.parametrize("status", ["COMPLETE", "PARTIAL", "UNAVAILABLE"])
def test_original_document_manifest_receipt_are_bound_and_truthful(status):
    metadata, raw = retained(status)
    response = exports.original_response(metadata, raw, AT + timedelta(hours=1))
    document = json.loads(response["content"])
    assert contracts.DOCUMENT_VALIDATOR.is_valid(document)
    assert contracts.MANIFEST_VALIDATOR.is_valid(response["manifest"])
    assert contracts.RECEIPT_VALIDATOR.is_valid(response["receipt"])
    assert set(response["manifest"]) == set(contracts.MANIFEST_SCHEMA["required"])
    assert len(response["manifest"]) == 13
    assert len(response["receipt"]) == 9
    assert document["record_status"] == "Draft"
    assert document["declared_components"] == ["PUBLIC_PLAN", "ARCHIVED_GUIDANCE"]
    assert response["manifest"]["guidance_status"] == status
    assert response["manifest"]["saved_at"] != response["receipt"]["saved_at"]
    assert response["manifest"]["generated_at"] == response["receipt"]["saved_at"]
    assert response["manifest"]["replay_expires_at"] == response["receipt"]["replay_until"]
    assert response["manifest"]["size_bytes"] == response["receipt"]["byte_count"] == len(raw)
    assert response["receipt"]["object_id"] == ISSUANCE
    assert response["receipt"]["revision_id"] != REVISION
    assert response["manifest"]["plan_id"] == PLAN
    assert response["manifest"]["revision_id"] == REVISION
    assert response["content"].encode() == raw
    assert "competency certification" in document["disclaimer"]
    assert "impact_reference" not in document["plan"]["data"]
    if status == "UNAVAILABLE":
        assert all(document["guidance"][n]["payload"] is None for n in ("catalog", "solutions", "practice"))
    elif status == "PARTIAL":
        assert document["guidance"]["practice"]["payload"] is None
        assert document["guidance"]["catalog"]["payload"] == catalog()


def test_replay_never_renders_or_uses_current_catalog(monkeypatch):
    metadata, raw = retained("COMPLETE")
    expected = exports.original_response(metadata, raw, AT)
    monkeypatch.setattr(exports, "render_document", lambda *a: pytest.fail("rerendered original"))
    monkeypatch.setattr(exports, "public_plan", lambda *a: pytest.fail("reinterpreted saved source"))
    monkeypatch.setattr(exports.ai_content_archives, "result", lambda *a: pytest.fail("read current content"))
    assert exports.original_response(metadata, raw, AT + timedelta(days=6)) == expected


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", str(uuid4())),
        ("issuance_id", str(uuid4())),
        ("plan_object_id", str(uuid4())),
        ("plan_revision_id", str(uuid4())),
        ("package_schema_version", "future-v2"),
        ("renderer_version", "future-v2"),
        ("generated_at", AT + timedelta(seconds=1)),
        ("guidance_status", "COMPLETE"),
        ("guidance_schema_version", SCHEMA_VERSION),
        ("guidance_sha256", b"x" * 32),
        ("replay_until", AT + timedelta(hours=169)),
        ("content_sha256", b"x" * 32),
        ("byte_count", 4),
    ],
)
def test_retained_metadata_mismatch_never_returns_body(field, value):
    metadata, raw = retained()
    metadata[field] = value
    with pytest.raises(DomainError) as caught:
        exports.original_response(metadata, raw, AT)
    assert caught.value.status == 503


@pytest.mark.parametrize("delta", [timedelta(hours=168), timedelta(days=8)])
def test_expired_original_metadata_cannot_authorize_bytes(delta):
    metadata, raw = retained()
    with pytest.raises(DomainError) as caught:
        exports.original_response(metadata, raw, AT + delta)
    assert (caught.value.status, caught.value.code) == (409, "IDEMPOTENCY_EXPIRED")


@pytest.mark.parametrize(
    "transform",
    [
        lambda b: b + b"\n",
        lambda b: b[:-1] + b"?",
        lambda b: b"\xff\xfe",
        lambda b: json.dumps(json.loads(b), ensure_ascii=False, indent=2).encode(),
    ],
)
def test_corrupt_or_noncanonical_retained_bytes_refused_even_with_matching_digest(transform):
    metadata, raw = retained()
    raw = transform(raw)
    metadata.update(byte_count=len(raw), content_sha256=hashlib.sha256(raw).digest())
    with pytest.raises(DomainError) as caught:
        exports.original_response(metadata, raw, AT)
    assert caught.value.status == 503


def test_unknown_retained_public_field_is_not_silently_removed_on_replay():
    metadata, raw = retained()
    document = json.loads(raw)
    document["plan"]["data"]["unknown"] = "Do not reinterpret an already issued artifact"
    raw = store.canonical(document)
    metadata.update(byte_count=len(raw), content_sha256=hashlib.sha256(raw).digest())
    with pytest.raises(DomainError) as caught:
        exports.original_response(metadata, raw, AT)
    assert caught.value.status == 503


@pytest.mark.parametrize(
    "mutate",
    [
        lambda b: b.update(extra="private"),
        lambda b: b["data"].update(format="PDF"),
        lambda b: b["data"].update(restriction="EXTERNAL"),
        lambda b: b["data"].update(acknowledged=False),
        lambda b: b["data"].update(recipient_id=str(uuid4())),
        lambda b: b.update(operation_id="not-uuid"),
    ],
)
def test_closed_request_refuses_before_database(mutate):
    service = SimpleNamespace(db=SimpleNamespace(transaction=lambda *a: pytest.fail("opened database")))
    body = {
        "operation_id": str(uuid4()),
        "data": {"format": "JSON", "restriction": "INTERNAL_SELF", "acknowledged": True},
    }
    mutate(body)
    with pytest.raises(DomainError) as caught:
        exports.AIPlanExports(service).create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert caught.value.status == 422


class FakeConnection:
    def __init__(self, source_row=None, existing=None, saved=None, fail_at=None):
        self.source, self.existing, self.saved = source_row or source(), existing, saved
        self.queries, self.fail_at, self.result = [], fail_at, None

    def execute(self, query, args=()):
        self.queries.append((query, args))
        if self.fail_at and self.fail_at in query:
            raise RuntimeError("injected transaction failure")
        self.result = None
        if query.startswith("SELECT statement_timestamp()"):
            self.result = {"generated_at": exports.now()}
        elif query.startswith("SELECT payload,payload_sha256"):
            self.result = self.source
        elif query.startswith("SELECT * FROM impact.ai_plan_export_issuance"):
            self.result = self.existing
        elif query.startswith("SELECT body FROM impact.ai_plan_export_bytes"):
            self.result = {"body": self.saved} if self.saved is not None else None
        return self

    def fetchone(self):
        return self.result


class FakeDB:
    def __init__(self, connection):
        self.connection, self.committed, self.rolled_back = connection, False, False

    @contextmanager
    def transaction(self, tenant):
        assert tenant == TENANT
        try:
            yield self.connection
        except Exception:
            self.rolled_back = True
            raise
        self.committed = True


def command_fixture(monkeypatch, existing=None, saved=None, fail_at=None):
    c = FakeConnection(existing=existing, saved=saved, fail_at=fail_at)
    db = FakeDB(c)
    ctx = SimpleNamespace(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        membership_id=MEMBER,
        identity=SimpleNamespace(auth_time=AT, assurance_verified=True),
    )
    checks, audits = [], []
    monkeypatch.setattr(exports, "now", lambda: AT)
    monkeypatch.setattr(exports, "context", lambda *a, **k: checks.append("context") or ctx)
    monkeypatch.setattr(exports, "authorize", lambda *a, **k: checks.append(a[2]))
    monkeypatch.setattr(exports, "load", lambda *a, **k: checks.append("current_read"))
    monkeypatch.setattr(exports.ai_content_archives, "result", lambda *a: guidance())
    monkeypatch.setattr(exports.ai_content_archives, "_bound", lambda *a: None)

    def audit_write(*args, **kwargs):
        audits.append((args, kwargs))
        return {"object_id": kwargs["object_id"], "revision_id": str(uuid4())}

    monkeypatch.setattr(exports, "write", audit_write)
    body = {
        "operation_id": str(uuid4()),
        "data": {"format": "JSON", "restriction": "INTERNAL_SELF", "acknowledged": True},
    }
    return exports.AIPlanExports(SimpleNamespace(db=db)), c, db, checks, audits, body


def test_new_issuance_one_audit_one_outbox_pointer_receipt_no_plan_write(monkeypatch):
    service, c, db, checks, audits, body = command_fixture(monkeypatch)
    response = service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert db.committed and not db.rolled_back
    assert checks == ["context", contracts.OPERATION, "get_ai_adoption_plan", "current_read"]
    assert c.queries[0][0].startswith("SELECT pg_advisory_xact_lock")
    assert len(audits) == 1
    assert audits[0][0][2] == "AuditEvent" and audits[0][1]["track_author"] is False
    assert audits[0][0][3]["object_reference"] == PLAN
    inserts = [(q, a) for q, a in c.queries if q.startswith("INSERT")]
    assert len(inserts) == 5
    assert [q.split("(")[0].split()[2] for q, a in inserts] == [
        "impact.ai_plan_export_issuance",
        "impact.ai_plan_export_bytes",
        "impact.outbox_event",
        "impact.outbox_delivery",
        "impact.operation_receipt",
    ]
    assert "issuer_slot" not in inserts[0][0]
    event = inserts[2][1][-1].obj
    assert event["aggregate_type"] == "AuditEvent"
    assert event["aggregate_id"] == response["receipt"]["object_id"]
    assert event["aggregate_revision"] == response["receipt"]["revision_id"]
    assert event["aggregate_sequence"] == 1
    assert event["payload"]["state"] == "Recorded"
    assert inserts[3][0] == "INSERT INTO impact.outbox_delivery(tenant_id,event_id) VALUES(%s,%s)"
    stored_receipt = inserts[4][1][-2].obj
    assert stored_receipt == response["receipt"]
    assert set(stored_receipt) == set(contracts.RECEIPT_SCHEMA["required"])
    assert "content" not in stored_receipt and "title" not in stored_receipt


@pytest.mark.parametrize(
    "fail_at",
    [
        "INSERT INTO impact.ai_plan_export_issuance",
        "INSERT INTO impact.ai_plan_export_bytes",
        "INSERT INTO impact.outbox_event",
        "INSERT INTO impact.outbox_delivery",
        "INSERT INTO impact.operation_receipt",
    ],
)
def test_each_insert_failure_keeps_the_command_in_a_single_rollback(monkeypatch, fail_at):
    service, c, db, checks, audits, body = command_fixture(monkeypatch, fail_at=fail_at)
    with pytest.raises(RuntimeError):
        service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert db.rolled_back and not db.committed
    assert len(audits) == 1


def test_command_replay_current_authority_precedes_retained_lookup_and_never_write(monkeypatch):
    metadata, raw = retained()
    service, c, db, checks, audits, body = command_fixture(monkeypatch, existing=metadata, saved=raw)
    body["operation_id"] = metadata["operation_id"]
    metadata["request_sha256"] = store.hash_data(
        [contracts.OPERATION, TENANT, PRINCIPAL, PLAN, REVISION, body]
    )
    c.source["payload"] = {"current_source_now_unrepresentable": True}
    monkeypatch.setattr(exports, "render_document", lambda *a: pytest.fail("re-rendered replay"))
    response = service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert checks == ["context", contracts.OPERATION, "get_ai_adoption_plan", "current_read"]
    assert response == exports.original_response(metadata, raw, AT)
    assert not audits and not any(q.startswith("INSERT") for q, a in c.queries)
    assert db.committed


@pytest.mark.parametrize(
    "gate", ["context", contracts.OPERATION, "get_ai_adoption_plan", "current_read", "exact_source"]
)
def test_revoked_current_authority_or_unavailable_exact_pin_never_queries_retained_bytes(monkeypatch, gate):
    metadata, raw = retained()
    service, c, db, checks, audits, body = command_fixture(monkeypatch, existing=metadata, saved=raw)

    def refuse(*a, **k):
        raise DomainError("RESOURCE_UNAVAILABLE", 404)

    if gate == "context":
        monkeypatch.setattr(exports, "context", refuse)
    elif gate in (contracts.OPERATION, "get_ai_adoption_plan"):
        monkeypatch.setattr(exports, "authorize", lambda *a, **k: refuse() if a[2] == gate else None)
    elif gate == "current_read":
        monkeypatch.setattr(exports, "load", refuse)
    else:
        c.source = None
    with pytest.raises(DomainError) as caught:
        service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert caught.value.status == 404
    assert not audits and not any("SELECT body" in q for q, a in c.queries)
    assert not any("SELECT * FROM impact.ai_plan_export_issuance" in q for q, a in c.queries)
    assert db.rolled_back


@pytest.mark.parametrize(
    "verified,age,reason",
    [(False, 0, "MFA_ASSURANCE_REQUIRED"), (True, 301, "FRESH_AUTHENTICATION_REQUIRED")],
)
def test_real_authorizer_requires_verified_fresh_assurance_for_export(monkeypatch, verified, age, reason):
    monkeypatch.setitem(store.OPERATIONS, contracts.OPERATION, contracts.POLICY)
    identity = SimpleNamespace(
        assurance_verified=verified, auth_time=datetime.now(timezone.utc) - timedelta(seconds=age)
    )
    ctx = SimpleNamespace(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        identity=identity,
        grants=[{"capability": contracts.CAPABILITY, "purpose": None, "scope_type": "TENANT"}],
    )
    with pytest.raises(DomainError) as caught:
        store.authorize(None, ctx, contracts.OPERATION, PLAN, hidden=True)
    assert (caught.value.status, caught.value.reason) == (403, reason)


def test_openapi_projection_components_are_separate_and_closed():
    spec = {"components": {"schemas": {"Error": {}}}, "paths": {}}
    policy = {"operations": []}
    contracts.augment(spec, policy)
    assert len([k for k in spec["components"]["schemas"] if k.startswith("AIPlanExportV1")]) == 11
    assert policy["operations"] == [contracts.POLICY]
    assert policy["operations"][0]["role_templates"] == ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"]
    assert policy["operations"][0]["fresh_assurance_seconds"] == 300
    assert policy["operations"][0]["capability"] == "ai.enablement.export"
    assert set(spec["paths"]) == {contracts.POLICY["path"]}
    assert "get" not in spec["paths"][contracts.POLICY["path"]]
    assert "#/$defs/" not in json.dumps(spec)


@pytest.mark.parametrize(
    "field,value",
    [
        ("format", "PDF"),
        ("restriction", "EXTERNAL"),
        ("guidance_snapshot_id", str(uuid4())),
    ],
)
def test_metadata_cannot_relabel_export_restriction_or_unavailable_guidance(field, value):
    metadata, raw = retained()
    metadata[field] = value
    with pytest.raises(DomainError) as caught:
        exports.original_response(metadata, raw, AT)
    assert caught.value.status == 503


@pytest.mark.parametrize(
    "mutate",
    [
        lambda g: g.update(object_id=str(uuid4())),
        lambda g: g.update(revision_id=str(uuid4())),
        lambda g: g.update(status="PARTIAL"),
        lambda g: g.update(snapshot_sha256="00" * 32),
        lambda g: g["catalog"].update(content_version="incorrect-edition"),
        lambda g: g["catalog"]["payload"].update(content_version="edited-without-new-binding"),
    ],
)
def test_guidance_ids_status_edition_and_archived_bundle_hash_are_verified(mutate):
    guide = guidance("COMPLETE")
    mutate(guide)
    with pytest.raises(DomainError) as caught:
        exports.render_document(TENANT, ISSUANCE, AT, PLAN, REVISION, source(), guide)
    assert caught.value.status == 503


def test_unavailable_guidance_cannot_claim_archive_provenance():
    guide = guidance()
    guide["captured_at"] = exports.stamp(AT)
    with pytest.raises(DomainError) as caught:
        exports.render_document(TENANT, ISSUANCE, AT, PLAN, REVISION, source(), guide)
    assert caught.value.status == 503


def test_utf8_byte_count_measures_original_bytes_and_filename_excludes_authored_title():
    metadata, raw = retained()
    response = exports.original_response(metadata, raw, AT)
    assert response["manifest"]["size_bytes"] > len(response["content"])
    assert response["manifest"]["filename"] == f"impact-ai-plan-{PLAN}-{REVISION}.json"
    assert "Café" not in response["manifest"]["filename"]
    assert response["content"] == raw.decode("utf-8")


def test_valid_source_over_copy_byte_limit_is_refused_before_any_issuance(monkeypatch):
    monkeypatch.setattr(exports, "MAX_COPY_BYTES", 100)
    with pytest.raises(DomainError) as caught:
        exports.render_document(TENANT, ISSUANCE, AT, PLAN, REVISION, source(), guidance())
    assert (caught.value.status, caught.value.reason) == (422, "AI_PLAN_EXPORT_SIZE_LIMIT")


def test_operation_uuid_is_canonical_for_sql_and_receipt_without_changing_request_fingerprint(monkeypatch):
    service, c, db, checks, audits, body = command_fixture(monkeypatch)
    body["operation_id"] = body["operation_id"].upper()
    response = service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert response["receipt"]["operation_id"] == body["operation_id"].lower()
    insert = next(
        args for query, args in c.queries if query.startswith("INSERT INTO impact.operation_receipt")
    )
    assert insert[3] == body["operation_id"].lower()
    assert insert[4] == store.hash_data([contracts.OPERATION, TENANT, PRINCIPAL, PLAN, REVISION, body])


def test_new_issue_rejects_corrupt_saved_source_hash_before_audit(monkeypatch):
    service, c, db, checks, audits, body = command_fixture(monkeypatch)
    c.source["payload_sha256"] = b"x" * 32
    with pytest.raises(DomainError) as caught:
        service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert caught.value.status == 503
    assert not audits and not any(query.startswith("INSERT") for query, args in c.queries)
    assert db.rolled_back


@pytest.mark.parametrize("expired", [False, True])
def test_permanent_operation_metadata_blocks_changed_request_and_expired_reissue(monkeypatch, expired):
    metadata, raw = retained()
    service, c, db, checks, audits, body = command_fixture(monkeypatch, existing=metadata, saved=raw)
    body["operation_id"] = metadata["operation_id"]
    if expired:
        metadata["request_sha256"] = store.hash_data(
            [contracts.OPERATION, TENANT, PRINCIPAL, PLAN, REVISION, body]
        )
        monkeypatch.setattr(exports, "now", lambda: AT + timedelta(days=8))
    with pytest.raises(DomainError) as caught:
        service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert (caught.value.status, caught.value.code) == (
        409,
        "IDEMPOTENCY_EXPIRED" if expired else "CONFLICT_OPERATION",
    )
    assert not audits and not any(
        query.startswith("INSERT") or query.startswith("SELECT body") for query, args in c.queries
    )


@pytest.mark.parametrize("matching", [True, False])
def test_storage_limit_translation_is_narrow_and_contains_no_count_or_hidden_details(monkeypatch, matching):
    service, c, db, checks, audits, body = command_fixture(monkeypatch)

    class CapacityError(Exception):
        diag = SimpleNamespace(
            message_primary="AI_PLAN_EXPORT_STORAGE_LIMIT" if matching else "OTHER_FAILURE"
        )

    monkeypatch.setattr(exports, "ProgramLimitExceeded", CapacityError)
    original = c.execute

    def execute(query, args=()):
        if query.startswith("INSERT INTO impact.ai_plan_export_issuance"):
            raise CapacityError()
        return original(query, args)

    c.execute = execute
    with pytest.raises(DomainError if matching else CapacityError) as caught:
        service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert db.rolled_back
    if matching:
        assert (caught.value.status, caught.value.reason) == (429, "AI_PLAN_EXPORT_STORAGE_LIMIT")
        assert caught.value.fields == []


@pytest.mark.parametrize("table", ["ai_plan_export_issuance", "unrelated_table"])
def test_unique_conflict_does_not_disclose_hidden_operation_and_other_errors_propagate(monkeypatch, table):
    service, c, db, checks, audits, body = command_fixture(monkeypatch)

    class ConflictError(Exception):
        diag = SimpleNamespace(table_name=table)

    monkeypatch.setattr(exports, "UniqueViolation", ConflictError)
    original = c.execute

    def execute(query, args=()):
        if query.startswith("INSERT INTO impact.ai_plan_export_issuance"):
            raise ConflictError()
        return original(query, args)

    c.execute = execute
    with pytest.raises(DomainError if table == "ai_plan_export_issuance" else ConflictError) as caught:
        service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert db.rolled_back
    if table == "ai_plan_export_issuance":
        assert (caught.value.status, caught.value.code) == (409, "CONFLICT_OPERATION")
        assert caught.value.fields == []


def test_issue_generation_uses_observed_database_clock_for_every_original_binding(monkeypatch):
    service, c, db, checks, audits, body = command_fixture(monkeypatch)
    database_time = AT + timedelta(minutes=2)
    original = c.execute

    def execute(query, args=()):
        result = original(query, args)
        if query.startswith("SELECT statement_timestamp()"):
            c.result = {"generated_at": database_time}
        return result

    c.execute = execute
    response = service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert response["manifest"]["generated_at"] == exports.stamp(database_time)
    assert response["receipt"]["saved_at"] == exports.stamp(database_time)
    assert response["receipt"]["replay_until"] == exports.stamp(database_time + timedelta(hours=168))
    assert audits[0][0][3]["occurred_at"] == exports.stamp(database_time)
    outbox = next(
        values[-1].obj for query, values in c.queries if query.startswith("INSERT INTO impact.outbox_event")
    )
    assert outbox["occurred_at"] == exports.stamp(database_time)
    assert db.committed


def test_replay_database_deadline_refuses_even_when_application_clock_is_earlier(monkeypatch):
    metadata, raw = retained()
    service, c, db, checks, audits, body = command_fixture(monkeypatch, existing=metadata, saved=raw)
    body["operation_id"] = metadata["operation_id"]
    metadata["request_sha256"] = store.hash_data(
        [contracts.OPERATION, TENANT, PRINCIPAL, PLAN, REVISION, body]
    )
    original = c.execute

    def execute(query, args=()):
        result = original(query, args)
        if query.startswith("SELECT statement_timestamp()"):
            c.result = {"generated_at": metadata["replay_until"]}
        return result

    c.execute = execute
    with pytest.raises(DomainError) as caught:
        service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert (caught.value.status, caught.value.code) == (409, "IDEMPOTENCY_EXPIRED")
    assert not audits and not any(query.startswith("SELECT body") for query, args in c.queries)


def test_deadline_crossed_during_byte_query_returns_expired_instead_of_source_unreadable(monkeypatch):
    metadata, raw = retained()
    service, c, db, checks, audits, body = command_fixture(monkeypatch, existing=metadata, saved=None)
    body["operation_id"] = metadata["operation_id"]
    metadata["request_sha256"] = store.hash_data(
        [contracts.OPERATION, TENANT, PRINCIPAL, PLAN, REVISION, body]
    )
    original, times = c.execute, iter([AT, metadata["replay_until"]])

    def execute(query, args=()):
        result = original(query, args)
        if query.startswith("SELECT statement_timestamp()"):
            c.result = {"generated_at": next(times)}
        return result

    c.execute = execute
    with pytest.raises(DomainError) as caught:
        service.create(None, TENANT, PLAN, REVISION, body, str(uuid4()))
    assert (caught.value.status, caught.value.code) == (409, "IDEMPOTENCY_EXPIRED")


# US-DC-04: the export carries archived guidance of either edition, labelled by its snapshot


def edition_guidance(version, status="COMPLETE"):
    """Archived guidance as the read returns it, for a snapshot of `version`."""
    from impact_api.ai_content_archives import SCHEMA_V1
    from test_ai_content_archives import v1_solutions

    guide = guidance(status)
    if version == SCHEMA_V1:
        guide["solutions"] = {
            "status": "AVAILABLE",
            "content_version": v1_solutions()["content_version"],
            "payload": v1_solutions(),
        }
    guide["snapshot_schema_version"] = version
    bundle = {
        "schema_version": version,
        **{name: guide[name]["payload"] for name in ("catalog", "solutions", "practice")},
    }
    guide["snapshot_sha256"] = store.hash_data(bundle).hex()
    return guide


@pytest.mark.parametrize("version", ["nonprofit-ai-guidance-v1", "nonprofit-ai-guidance-v2"])
@pytest.mark.parametrize("status", ["COMPLETE", "PARTIAL"])
def test_plans_archived_under_either_edition_export_and_replay_as_valid_documents(version, status):
    guide = edition_guidance(version, status)
    raw = exports.render_document(TENANT, ISSUANCE, AT, PLAN, REVISION, source(), guide)
    document = json.loads(raw)
    assert contracts.DOCUMENT_VALIDATOR.is_valid(document)
    assert document["schema_version"] == contracts.PACKAGE_VERSION == "nonprofit-ai-plan-export-v1"
    assert document["guidance"]["snapshot_schema_version"] == version
    listings = document["guidance"]["solutions"]["payload"]["solutions"]
    disclosed = ["commercial_disclosure" in item for item in listings]
    assert disclosed == [version.endswith("v2")] * 8
    metadata, _ = retained(status)
    metadata.update(
        guidance_schema_version=version,
        guidance_sha256=bytes.fromhex(guide["snapshot_sha256"]),
        byte_count=len(raw),
        content_sha256=hashlib.sha256(raw).digest(),
    )
    response = exports.original_response(metadata, raw, AT + timedelta(hours=1))
    assert response["content"].encode() == raw


@pytest.mark.parametrize(
    "label,payload",
    [
        ("nonprofit-ai-guidance-v1", "nonprofit-ai-guidance-v2"),
        ("nonprofit-ai-guidance-v2", "nonprofit-ai-guidance-v1"),
        ("nonprofit-ai-guidance-v3", "nonprofit-ai-guidance-v2"),
    ],
)
def test_guidance_labelled_with_another_edition_than_its_shape_is_refused(label, payload):
    guide = edition_guidance(payload)
    guide["snapshot_schema_version"] = label
    bundle = {
        "schema_version": label,
        **{name: guide[name]["payload"] for name in ("catalog", "solutions", "practice")},
    }
    # Validly hashed under the wrong label: only the edition-bound document schema can refuse it.
    guide["snapshot_sha256"] = store.hash_data(bundle).hex()
    with pytest.raises(DomainError) as caught:
        exports.render_document(TENANT, ISSUANCE, AT, PLAN, REVISION, source(), guide)
    assert (caught.value.status, caught.value.reason) == (503, "AI_PLAN_EXPORT_SOURCE_UNREADABLE")
