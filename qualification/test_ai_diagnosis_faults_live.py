"""Supplemental US-DX-01a rollback and receipt boundaries.

Execution outcomes are recorded separately; source code is not a run claim.

Uses the existing live synthetic DB/auth harness. Failure injection stays in the
test process and adds no runtime bypass, fault flag or permissions. The algorithm
and real transaction execute in-process; these checks are not HTTP fault, restart,
native RLS, concurrency, human acceptance or production evidence.
"""

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from starlette.requests import Request

import impact_api.ai_diagnoses as module
from impact_api.ai_diagnoses import AIDiagnoses
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database
from test_ai_diagnosis_live import action, action_body, diagnosis, domain_counts, get, narrowed, save
from test_live_application import cmd


class InjectedFault(Exception):
    pass


def fixture_service(live):
    settings = Settings(**live.config)
    database = Database(settings)
    identity = Auth(settings, database).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token("admin")).encode())],
            }
        )
    )
    return settings, database, identity


class ReceiptFaultDatabase:
    """Delegate the real transaction, raising after its receipt insert before commit."""

    def __init__(self, database):
        self.database = database
        self.enabled = True
        self.triggered = False

    def __getattr__(self, name):
        return getattr(self.database, name)

    @contextmanager
    def transaction(self, *args, **kwargs):
        wrapper = self

        class Cursor:
            def __init__(self, cursor):
                self.cursor = cursor

            def __getattr__(self, name):
                return getattr(self.cursor, name)

            def execute(self, statement, *params, **options):
                result = self.cursor.execute(statement, *params, **options)
                if wrapper.enabled and "INSERT INTO impact.operation_receipt" in str(statement):
                    wrapper.triggered = True
                    raise InjectedFault("Synthetic failure after receipt insertion before commit")
                return result

        with self.database.transaction(*args, **kwargs) as cursor:
            yield Cursor(cursor)


@pytest.mark.parametrize("point", ["head", "audit_outbox", "receipt"])
def test_each_failure_rolls_back_revision_head_audit_outbox_receipt_and_retry_writes_once(
    live, monkeypatch, point
):
    settings, database, identity = fixture_service(live)
    fault_database = ReceiptFaultDatabase(database)
    fault_database.enabled = point == "receipt"
    api = AIDiagnoses(Service(settings, fault_database))
    tenant = live.fixture["tenant_a"]
    body = cmd(diagnosis())
    original_write, original_audit = module.write, module.audit
    triggered = []

    def fail_after_write(*args, **kwargs):
        original_write(*args, **kwargs)
        triggered.append("head")
        raise InjectedFault("Synthetic failure after revision and registry head")

    def fail_after_audit(*args, **kwargs):
        original_audit(*args, **kwargs)
        triggered.append("audit_outbox")
        raise InjectedFault("Synthetic failure after audit and outbox intent")

    before = domain_counts(live)
    with monkeypatch.context() as patch:
        if point == "head":
            patch.setattr(module, "write", fail_after_write)
        elif point == "audit_outbox":
            patch.setattr(module, "audit", fail_after_audit)
        with pytest.raises(InjectedFault):
            api.command(identity, tenant, body, str(uuid4()))
    assert triggered == [point] if point != "receipt" else fault_database.triggered
    assert domain_counts(live) == before
    fault_database.enabled = False
    first = api.command(identity, tenant, body, str(uuid4()))
    after = domain_counts(live)
    # The governed audit event is itself a registry object and immutable revision.
    # Exactly one diagnosis + one audit, one outbox intent and one receipt.
    for table, increment in {
        "object_registry": 2,
        "object_revision": 2,
        "audit_event_current": 1,
        "outbox_event": 1,
        "operation_receipt": 1,
    }.items():
        assert after[table] == before[table] + increment
    for table in ("ai_advisory_request", "ai_advisory_result"):
        assert after[table] == before[table]
    assert api.command(identity, tenant, body, str(uuid4())) == first
    assert domain_counts(live) == after
    assert get(live, first)["business_state"] == "Draft"


@pytest.mark.parametrize("capability", ["ai.diagnosis.read", "ai.diagnosis.manage"])
def test_completed_receipt_replay_loses_access_when_current_read_or_manage_is_removed(live, capability):
    row = save(live)
    body = action_body(row)
    completed = action(live, row, "complete", body)
    before = domain_counts(live)
    with narrowed(live, capability):
        action(live, row, "complete", body, status=404)
    assert domain_counts(live) == before
    assert action(live, row, "complete", body) == completed
    assert domain_counts(live) == before


def test_revise_receipt_exact_replay_is_single_revision_and_changed_reason_conflicts(live):
    row = action(live, save(live), "complete")
    body = action_body(row, reason="Synthetic first recorded correction")
    revised = action(live, row, "revise", body)
    before = domain_counts(live)
    assert action(live, row, "revise", body) == revised
    denied = action(live, row, "revise", {**body, "reason": "Changed correction intent"}, status=409)
    assert denied["code"] == "CONFLICT_OPERATION"
    assert domain_counts(live) == before
    assert get(live, revised)["data"]["correction_reason"] == body["reason"]


def test_expired_receipt_refuses_operation_reuse_without_modifying_saved_receipts(live, monkeypatch):
    settings, database, identity = fixture_service(live)
    api = AIDiagnoses(Service(settings, database))
    tenant = live.fixture["tenant_a"]
    body = cmd(diagnosis())
    saved = api.command(identity, tenant, body, str(uuid4()))
    original = get(live, saved)
    before = domain_counts(live)

    class AfterReceiptExpiry(datetime):
        @classmethod
        def now(cls, tz=None):
            instant = datetime.now(timezone.utc) + timedelta(days=8)
            return instant.astimezone(tz) if tz is not None else instant.replace(tzinfo=None)

    # Advance only the command's expiry comparison in the test process; never age,
    # update, delete or rewrite the immutable operation receipt stored in the DB.
    with monkeypatch.context() as patch:
        patch.setattr(module, "datetime", AfterReceiptExpiry)
        with pytest.raises(DomainError) as refused:
            api.command(identity, tenant, body, str(uuid4()))
    assert refused.value.code == "IDEMPOTENCY_EXPIRED" and refused.value.status == 409
    assert domain_counts(live) == before and get(live, saved) == original
