"""Positive live journey for FR-AI-014 / APL-343 immutable AI task trace."""

import hashlib
from datetime import datetime, timezone
from uuid import uuid4

from advisory_tenant_fixture import isolated_advisory_tenant

import pytest

from impact_api import ai_enablement as enablement_module
from impact_api.ai_enablement import AIEnablement
from impact_api.ai_policy import AIPolicy
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database
from test_ai_answer_provenance_live import _identity
from test_ai_enablement_live import profile


@pytest.fixture(autouse=True)
def passed_advisory_evaluation(monkeypatch):
    monkeypatch.setattr(enablement_module, "require_exposure", lambda use_case, configuration: {})


def test_successful_ai_task_preserves_a_closed_reproducible_trace_without_hidden_reasoning(live):
    settings = Settings(**live.config)
    db, tenant = Database(settings), isolated_advisory_tenant(live)
    admin = _identity(live, db, "admin")

    class Provider:
        configured = True
        destination = "openai-us"
        evaluation_configuration = {}
        calls = 0

        def generate(self, supplied, assessment):
            self.calls += 1
            return {
                "text": "SYNTHETIC: retain a human reviewer for the pilot.",
                "model": "synthetic-trace-v1",
                "hidden_reasoning": "must never be accepted or stored",
                "tool_receipts": [{"forged": True}],
            }

    provider = Provider()
    service = Service(settings, db)
    api = AIEnablement(service, provider, enabled=True)
    policies = AIPolicy(service, api.server_ready)
    enabled = policies.save(
        admin,
        tenant,
        {
            "operation_id": str(uuid4()),
            "expected_version": policies.get(admin, tenant)["policy_version"],
            "data": {
                "use_cases": [
                    {
                        "use_case": "ADVISORY_DRAFT",
                        "enabled": True,
                        "data_classes": ["INTERNAL"],
                        "destinations": ["openai-us"],
                        "purposes": ["AI_ADOPTION_ADVISORY"],
                        "languages": ["en"],
                        "review_mode": "HUMAN_REVIEW",
                        "budget_units": 100,
                        "tools": [],
                    }
                ]
            },
        },
        str(uuid4()),
    )
    request = {
        "operation_id": str(uuid4()),
        "profile": profile(),
        "consent": True,
        "policy_version": enabled["policy_version"],
        "purpose": "AI_ADOPTION_ADVISORY",
        "source_dependencies": [],
    }
    revoked = _identity(live, db, "revoked")
    with pytest.raises(DomainError) as denied:
        api.advisory(revoked, tenant, request, str(uuid4()))
    assert (denied.value.status, denied.value.code) == (404, "RESOURCE_UNAVAILABLE")
    assert provider.calls == 0
    with db.transaction(tenant) as c:
        assert not c.execute(
            "SELECT 1 FROM impact.ai_advisory_request WHERE tenant_id=%s AND request_id=%s",
            (tenant, request["operation_id"]),
        ).fetchone()
    result = api.advisory(admin, tenant, request, str(uuid4()))
    assert set(result) == {"status", "text", "assessment", "model", "disclaimer", "trace"}
    trace = result["trace"]
    assert set(trace) == {
        "requester_principal_id",
        "scope",
        "source_versions",
        "use_case_configuration",
        "model_identifier",
        "tool_receipts",
        "proposed_changes",
        "review_decisions",
        "applied_domain_receipts",
        "output_version",
        "retention_until",
    }
    assert trace["requester_principal_id"] == live.fixture["actors"]["admin"]["principal_id"]
    assert trace["scope"] == {
        "use_case": "ADVISORY_DRAFT",
        "purpose": "AI_ADOPTION_ADVISORY",
    }
    assert trace["source_versions"] == []
    assert trace["use_case_configuration"] == {
        "policy_version": enabled["policy_version"],
        "policy_version_id": enabled["policy_version_id"],
        "use_case": "ADVISORY_DRAFT",
        "purpose": "AI_ADOPTION_ADVISORY",
        "data_classes": ["INTERNAL"],
        "destinations": ["openai-us"],
        "review_mode": "HUMAN_REVIEW",
        "tools": [],
    }
    assert trace["model_identifier"] == "synthetic-trace-v1"
    assert trace["tool_receipts"] == []
    assert trace["proposed_changes"] == []
    assert trace["review_decisions"] == []
    assert trace["applied_domain_receipts"] == []
    assert trace["output_version"] == hashlib.sha256(result["text"].encode()).hexdigest()
    retention = datetime.fromisoformat(trace["retention_until"])
    assert 29.99 < (retention - datetime.now(timezone.utc)).total_seconds() / 86400 <= 30
    assert "reasoning" not in str(result).lower()

    assert api.advisory(admin, tenant, request, str(uuid4())) == result
    assert provider.calls == 1
    with db.transaction(tenant) as c:
        stored = c.execute(
            "SELECT sealed_output,failure_reason FROM impact.ai_advisory_result "
            "WHERE tenant_id=%s AND request_id=%s",
            (tenant, request["operation_id"]),
        ).fetchone()
        completed = c.execute(
            "SELECT count(*) AS n FROM impact.audit_event_current a "
            "JOIN impact.ai_advisory_request q ON q.tenant_id=a.tenant_id "
            "AND q.object_id=a.object_reference WHERE q.tenant_id=%s AND q.request_id=%s "
            "AND a.action_type='ai_advisory_completed'",
            (tenant, request["operation_id"]),
        ).fetchone()["n"]
    assert stored["failure_reason"] is None and stored["sealed_output"]
    assert b"hidden_reasoning" not in bytes(stored["sealed_output"])
    assert completed == 1
    # A conflicting uncertain retry must neither replace the trace nor call the provider.
    with pytest.raises(DomainError) as conflict:
        api.advisory(admin, tenant, {**request, "profile": {**profile(), "team_size": 42}}, str(uuid4()))
    assert conflict.value.status == 409
    assert api.advisory(admin, tenant, request, str(uuid4())) == result
    assert provider.calls == 1
