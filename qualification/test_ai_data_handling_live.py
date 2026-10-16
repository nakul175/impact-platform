"""Positive data-handling journey for FR-AI-012 / APL-341 on a real disposable database."""

from uuid import uuid4

import pytest
from starlette.requests import Request

from impact_api import ai_enablement as enablement_module
from impact_api.ai_enablement import AIEnablement
from impact_api.ai_enablement_catalog import assess
from impact_api.ai_policy import AIPolicy
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database


def _profile(**changes):
    return {
        "sector": "GENERAL",
        "team_size": 8,
        "goal": (
            "Draft a public update for person@example.org or +1 (202) 555-0198; password=synthetic-secret"
        ),
        "data_readiness": "BASIC",
        "ai_experience": "EXPERIMENTING",
        "sensitive_data": False,
        **changes,
    }


def _request(policy_version, **changes):
    return {
        "operation_id": str(uuid4()),
        "profile": _profile(),
        "consent": True,
        "policy_version": policy_version,
        "purpose": "AI_ADOPTION_ADVISORY",
        **changes,
    }


def test_advisory_records_exact_handling_and_sends_only_minimized_data(live, monkeypatch):
    monkeypatch.setattr(enablement_module, "require_exposure", lambda use_case, configuration: {})
    settings = Settings(**live.config)
    db = Database(settings)
    auth = Auth(settings, db)
    identity = auth.resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token("admin")).encode())],
            }
        )
    )
    tenant = live.fixture["tenant_a"]

    class Provider:
        configured = True
        destination = "openai-us"
        evaluation_configuration = {
            "destination": "openai-us",
            "model": "synthetic-test",
            "prompt_version": "synthetic-test-v1",
            "policy_gate_version": "synthetic-policy-gate-v1",
            "retrieval": "NONE",
            "tools": [],
        }

        def __init__(self):
            self.calls = []

        def generate(self, profile, assessment):
            self.calls.append((profile, assessment))
            return {"text": "Synthetic review-only advisory.", "model": "synthetic-test"}

    provider = Provider()
    service = Service(settings, db)
    api = AIEnablement(service, provider, enabled=True)
    policies = AIPolicy(service, api.server_ready)
    current = policies.get(identity, tenant)
    enabled = policies.save(
        identity,
        tenant,
        {
            "operation_id": str(uuid4()),
            "expected_version": current["policy_version"],
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

    request = _request(enabled["policy_version"])
    result = api.advisory(identity, tenant, request, str(uuid4()))
    assert result["status"] == "DRAFT"
    assert len(provider.calls) == 1
    sent, recomputed = provider.calls[0]
    assert sent == {
        "sector": "GENERAL",
        "team_size": 10,
        "goal": "Draft a public update for [REDACTED] or [REDACTED]; [REDACTED]",
        "data_readiness": "BASIC",
        "ai_experience": "EXPERIMENTING",
        "sensitive_data": False,
    }
    assert recomputed == assess(sent)
    assert "person@example.org" not in repr(provider.calls)
    assert "555-0198" not in repr(provider.calls)
    assert "synthetic-secret" not in repr(provider.calls)

    with db.transaction(tenant) as c:
        reserved = c.execute(
            "SELECT v.payload FROM impact.ai_advisory_request r "
            "JOIN impact.object_registry o ON o.tenant_id=r.tenant_id AND o.object_id=r.object_id "
            "JOIN impact.object_revision v ON v.tenant_id=o.tenant_id AND v.revision_id=o.head_revision "
            "WHERE r.tenant_id=%s AND r.request_id=%s",
            (tenant, request["operation_id"]),
        ).fetchone()["payload"]
    assert reserved["data_handling"] == {
        "purpose": "AI_ADOPTION_ADVISORY",
        "destination": "openai-us",
        "destination_version": "openai-us-responses-no-store-2026-10-13.1",
        "region": "United States",
        "provider_retention": "NO_STORE",
        "training_reuse_opt_in": False,
        "fallback_destination": None,
        "minimisation_profile_version": "advisory-minimisation-2026-10-13.1",
        "transmitted_fields": [
            "ai_experience",
            "data_readiness",
            "goal",
            "sector",
            "sensitive_data",
            "team_size",
        ],
        "excluded_fields": ["exact_team_size"],
        "redaction_categories": ["EMAIL", "PHONE", "CREDENTIAL"],
        "evaluation_dataset_eligible": False,
    }

    blocked = _request(enabled["policy_version"], profile=_profile(sensitive_data=True))
    with pytest.raises(DomainError) as refused:
        api.advisory(identity, tenant, blocked, str(uuid4()))
    assert (refused.value.status, refused.value.reason) == (422, "AI_POLICY_BLOCKED")
    assert len(provider.calls) == 1
    with db.transaction(tenant) as c:
        assert not c.execute(
            "SELECT 1 FROM impact.ai_advisory_request WHERE tenant_id=%s AND request_id=%s",
            (tenant, blocked["operation_id"]),
        ).fetchone()
