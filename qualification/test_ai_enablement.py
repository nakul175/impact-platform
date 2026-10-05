"""Offline advisory claim/replay/authority qualification; provider is always synthetic."""

from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from cryptography.exceptions import InvalidTag

import impact_api.ai_enablement as module
from impact_api.ai_enablement import AIEnablement, _binding, _key
from impact_api.domain import DomainError
from impact_api.keyring import Keyring


def body():
    return {
        "operation_id": str(uuid4()),
        "consent": True,
        "profile": {
            "sector": "GENERAL",
            "team_size": 8,
            "goal": "Draft donor newsletter",
            "data_readiness": "BASIC",
            "ai_experience": "EXPERIMENTING",
            "sensitive_data": False,
        },
    }


class Cursor:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row


class Database:
    def __init__(self):
        self.requests, self.results, self.active = {}, {}, False
        self.principal = "principal-one"
        self.registry_queries = 0
        self.authority = True

    @contextmanager
    def transaction(self, tenant):
        assert not self.active
        self.active = True
        try:
            yield self
        finally:
            self.active = False

    def execute(self, sql, values):
        if sql.startswith("SELECT pg_advisory"):
            return Cursor(None)
        if "SELECT count" in sql:
            return Cursor({"n": sum(t == values[0] for t, _ in self.requests)})
        if "SELECT object_id FROM impact.object_registry" in sql:
            self.registry_queries += 1
            raise AssertionError("Client operation IDs must never select registry objects")
        if "FROM impact.ai_advisory_request r JOIN" in sql:
            stored = self.requests[tuple(values)]
            return Cursor(
                {
                    "object_id": stored["object_id"],
                    "revision_id": "synthetic-revision",
                    "business_state": "Recorded",
                }
            )
        if "SELECT * FROM impact.ai_advisory_request" in sql:
            return Cursor(self.requests.get(tuple(values)))
        if "SELECT * FROM impact.ai_advisory_result" in sql:
            return Cursor(self.results.get(tuple(values)))
        if "INSERT INTO impact.ai_advisory_request" in sql:
            tenant, request, object_id, principal, fingerprint = values
            self.requests[tenant, request] = {
                "principal_id": principal,
                "object_id": object_id,
                "fingerprint": fingerprint,
            }
            return Cursor(None)
        if "INSERT INTO impact.ai_advisory_result" in sql:
            tenant, request, output, failure = values
            assert (tenant, request) not in self.results
            self.results[tenant, request] = {"sealed_output": output, "failure_reason": failure}
            return Cursor(None)
        raise AssertionError(sql)


class Provider:
    configured = True

    def __init__(self, db):
        self.db, self.calls, self.fail, self.revoke = db, 0, False, False

    def generate(self, profile, assessment):
        assert not self.db.active, "Provider call must occur outside every transaction"
        self.calls += 1
        if self.revoke:
            self.db.authority = False
        if self.fail:
            raise RuntimeError("synthetic-sensitive-error")
        return {"text": "Synthetic advisory draft", "model": "synthetic-test", "usage": {"total_tokens": 10}}


@pytest.fixture
def engine(monkeypatch):
    db = Database()
    provider = Provider(db)
    service = SimpleNamespace(db=db, s=SimpleNamespace(delivery_secret="s" * 48))
    events = []

    def context(c, identity, tenant, write=False):
        if not db.authority:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return SimpleNamespace(principal_id=db.principal)

    def authorize(c, ctx, operation, hidden=False):
        events.append(operation)

    monkeypatch.setattr(module, "context", context)
    monkeypatch.setattr(module, "authorize", authorize)
    monkeypatch.setattr(
        module,
        "write",
        lambda c, ctx, kind, data, state: {
            "object_id": str(uuid4()),
            "data": data,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    monkeypatch.setattr(
        module, "audit", lambda c, ctx, operation, receipt, correlation: events.append((operation, receipt))
    )
    return AIEnablement(service, provider, True), db, provider, events


def test_claim_commits_before_provider_and_exact_replay_does_not_call_again(engine):
    api, db, provider, events = engine
    request = body()
    result = api.advisory(None, "tenant", request, "correlation")
    assert result["status"] == "DRAFT"
    assert "usage" not in result
    assert api.advisory(None, "tenant", request, "different-correlation") == result
    assert provider.calls == 1
    assert len(db.requests) == len(db.results) == 1
    assert events.count("create_ai_advisory") == 3
    assert events.count("get_ai_enablement_catalog") == 3
    receipt = next(event[1] for event in events if isinstance(event, tuple))
    assert "goal" not in receipt["data"]
    assert request["profile"]["goal"].encode() not in next(iter(db.results.values()))["sealed_output"]


def test_changed_payload_or_principal_conflicts_without_provider_call(engine):
    api, db, provider, _ = engine
    request = body()
    api.advisory(None, "tenant", request, "c")
    request["profile"]["goal"] = "Different goal"
    with pytest.raises(DomainError) as exc:
        api.advisory(None, "tenant", request, "c")
    assert exc.value.reason == "AI_OPERATION_CHANGED"
    request["profile"]["goal"] = "Draft donor newsletter"
    db.principal = "another-principal"
    with pytest.raises(DomainError):
        api.advisory(None, "tenant", request, "c")
    assert provider.calls == 1


def test_failed_attempt_is_durable_and_never_regenerated(engine):
    api, db, provider, _ = engine
    provider.fail = True
    request = body()
    for _ in range(2):
        with pytest.raises(DomainError) as exc:
            api.advisory(None, "tenant", request, "c")
        assert exc.value.reason == "AI_PROVIDER_UNAVAILABLE"
        assert "synthetic-sensitive-error" not in str(exc.value)
    assert provider.calls == 1
    assert next(iter(db.results.values()))["sealed_output"] is None


def test_budget_counts_failed_reserved_attempts_and_is_per_tenant(engine):
    api, db, provider, _ = engine
    provider.fail = True
    for _ in range(3):
        with pytest.raises(DomainError):
            api.advisory(None, "tenant", body(), "c")
    with pytest.raises(DomainError) as exc:
        api.advisory(None, "tenant", body(), "c")
    assert exc.value.reason == "AI_DAILY_LIMIT"
    assert exc.value.status == 429
    provider.fail = False
    assert api.advisory(None, "other", body(), "c")["status"] == "DRAFT"
    assert provider.calls == 4


def test_revoked_authority_after_call_never_returns_draft_or_regenerates(engine):
    api, db, provider, _ = engine
    provider.revoke = True
    request = body()
    with pytest.raises(DomainError) as exc:
        api.advisory(None, "tenant", request, "c")
    assert exc.value.status == 404
    assert len(db.requests) == 1 and not db.results
    db.authority = True
    with pytest.raises(DomainError) as exc:
        api.advisory(None, "tenant", request, "c")
    assert exc.value.reason == "AI_REQUEST_IN_FLIGHT"
    assert provider.calls == 1


def test_replay_requires_current_authority(engine):
    api, db, provider, _ = engine
    request = body()
    api.advisory(None, "tenant", request, "c")
    db.authority = False
    with pytest.raises(DomainError) as exc:
        api.advisory(None, "tenant", request, "c")
    assert exc.value.status == 404
    assert provider.calls == 1


@pytest.mark.parametrize("disabled", ["enabled", "provider", "secret"])
def test_unconfigured_never_reserves_or_spends(engine, disabled):
    api, db, provider, _ = engine
    if disabled == "enabled":
        api.enabled = False
    elif disabled == "provider":
        provider.configured = False
    else:
        api.service.s.delivery_secret = ""
    with pytest.raises(DomainError) as exc:
        api.advisory(None, "tenant", body(), "c")
    assert exc.value.reason == "AI_NOT_CONFIGURED"
    assert not db.requests and provider.calls == 0
    assert api.catalog(None, "tenant")["advisory_available"] is False


def test_consent_closed_body_and_profile_are_independently_validated(engine):
    api, db, provider, _ = engine
    for request in [
        None,
        {**body(), "consent": False},
        {**body(), "extra": "x"},
        {**body(), "operation_id": "invalid"},
        {**body(), "profile": {}},
    ]:
        with pytest.raises(DomainError) as exc:
            api.advisory(None, "tenant", request, "c")
        assert exc.value.status == 422
    assert not db.requests and provider.calls == 0


def test_sealed_output_tenant_binding_rotation_and_retirement():
    original = Keyring("delivery", "a" * 48)
    sealed = original.seal(_key, b"synthetic-draft", _binding("tenant", "request"))
    rotated = Keyring("delivery", "b" * 48, ["a" * 48])
    assert rotated.unseal(_key, sealed, _binding("tenant", "request")) == b"synthetic-draft"
    for ring, binding in [
        (rotated, _binding("other", "request")),
        (rotated, _binding("tenant", "other")),
        (Keyring("delivery", "b" * 48), _binding("tenant", "request")),
    ]:
        with pytest.raises(InvalidTag):
            ring.unseal(_key, sealed, binding)


def test_unreadable_replay_fails_closed_without_provider_call(engine):
    api, db, provider, _ = engine
    request = body()
    api.advisory(None, "tenant", request, "c")
    api.service.s.delivery_secret = "r" * 48
    with pytest.raises(DomainError) as exc:
        api.advisory(None, "tenant", request, "c")
    assert exc.value.reason == "AI_RESULT_UNREADABLE"
    assert provider.calls == 1


@pytest.mark.skipif(
    __import__("os").environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Real login-role boundaries require native PostgreSQL",
)
def test_native_advisory_tables_force_rls_and_narrow_application_grants(live):
    import os

    import psycopg
    from psycopg.errors import InsufficientPrivilege

    dsn = os.environ.get("IMPACT_LOGIN_DSN_APP")
    if not dsn:
        pytest.skip("Provisioned application login is required")
    with psycopg.connect(dsn, autocommit=True) as c:
        for table in ("ai_advisory_request", "ai_advisory_result"):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                assert c.execute(f"SELECT * FROM impact.{table}").fetchall() == []
                fenced = c.execute(
                    "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=%s::regclass",
                    ("impact." + table,),
                ).fetchone()
                assert fenced == (True, True)
            for verb in ("UPDATE", "DELETE"):
                with pytest.raises(InsufficientPrivilege):
                    with c.transaction():
                        c.execute("SET LOCAL ROLE impact_app")
                        c.execute(
                            "SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],)
                        )
                        statement = (
                            f"UPDATE impact.{table} SET tenant_id=tenant_id"
                            if verb == "UPDATE"
                            else f"DELETE FROM impact.{table}"
                        )
                        c.execute(statement)
        for role in ("PLATFORM", "IDENTITY"):
            role_dsn = os.environ.get("IMPACT_LOGIN_DSN_" + role)
            assert role_dsn, "Native qualification must provision all login roles"
            with psycopg.connect(role_dsn, autocommit=True) as other:
                for table in ("ai_advisory_request", "ai_advisory_result"):
                    with pytest.raises(InsufficientPrivilege):
                        with other.transaction():
                            other.execute(
                                "SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],)
                            )
                            other.execute(f"SELECT * FROM impact.{table}")


def test_catalogue_update_preserves_exact_replay_of_original_draft(engine, monkeypatch):
    api, db, provider, _ = engine
    request = body()
    original = api.advisory(None, "tenant", request, "c")
    prior_assess = module.assess

    def updated_assess(profile):
        return {**prior_assess(profile), "content_version": "later-editorial-version"}

    monkeypatch.setattr(module, "assess", updated_assess)
    replay = api.advisory(None, "tenant", request, "c")
    assert replay == original
    assert replay["assessment"]["content_version"] != "later-editorial-version"
    assert provider.calls == 1


def test_client_operation_id_is_never_used_as_a_registry_selector(engine):
    api, db, provider, events = engine
    request = body()
    result = api.advisory(None, "tenant", request, "c")
    stored = db.requests["tenant", request["operation_id"]]
    assert stored["object_id"] != request["operation_id"]
    assert db.registry_queries == 0
    assert provider.calls == 1 and result["status"] == "DRAFT"
    receipts = [event[1] for event in events if isinstance(event, tuple)]
    assert all(receipt["object_id"] == stored["object_id"] for receipt in receipts)
