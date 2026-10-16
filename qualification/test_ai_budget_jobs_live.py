"""Durable database journey for FR-AI-016a / APL-345 budgeted AI jobs."""

from uuid import uuid4

import pytest
from starlette.requests import Request

from impact_api import ai_enablement as enablement_module
from impact_api import ai_jobs as jobs_module
from impact_api.ai_enablement import AIEnablement
from impact_api.ai_jobs import AIJobs
from impact_api.ai_policy import AIPolicy
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database


def _profile():
    return {
        "sector": "GENERAL",
        "team_size": 8,
        "goal": "Draft a synthetic public donor newsletter",
        "data_readiness": "BASIC",
        "ai_experience": "EXPERIMENTING",
        "sensitive_data": False,
    }


def test_accepted_job_reserves_budget_and_queued_cancel_releases_it(live, monkeypatch):
    monkeypatch.setattr(enablement_module, "require_exposure", lambda *_: {})
    monkeypatch.setattr(jobs_module, "require_exposure", lambda *_: {})
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
        evaluation_configuration = {}

    enablement = AIEnablement(Service(settings, db), Provider(), enabled=True)
    policy = AIPolicy(enablement.service, enablement.server_ready)
    current = policy.get(identity, tenant)
    enabled = policy.save(
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
                        "budget_units": 1,
                        "tools": [],
                    }
                ]
            },
        },
        str(uuid4()),
    )
    jobs = AIJobs(enablement.service, enablement)
    body = {
        "operation_id": str(uuid4()),
        "profile": _profile(),
        "consent": True,
        "policy_version": enabled["policy_version"],
        "purpose": "AI_ADOPTION_ADVISORY",
        "source_dependencies": [],
        "tools": [],
    }
    accepted = jobs.submit(identity, tenant, body)
    assert accepted["state"] == "Queued"
    assert accepted["estimated_units"] == 1
    assert accepted["progress"] == 0 and accepted["can_cancel"] is True
    assert jobs.submit(identity, tenant, body) == accepted
    assert jobs.status(identity, tenant, accepted["job_id"]) == accepted

    revoked = auth.resolve(
        Request(
            {
                "type": "http",
                "method": "GET",
                "headers": [(b"authorization", ("Bearer " + live.token("revoked")).encode())],
            }
        )
    )
    for operation in (
        lambda: jobs.status(revoked, tenant, accepted["job_id"]),
        lambda: jobs.cancel(revoked, tenant, accepted["job_id"]),
    ):
        with pytest.raises(DomainError) as denied:
            operation()
        assert (denied.value.status, denied.value.code) == (404, "RESOURCE_UNAVAILABLE")
    assert jobs.status(identity, tenant, accepted["job_id"]) == accepted

    with db.transaction(tenant) as c:
        reservation = c.execute(
            "SELECT state,estimated_units,actual_units FROM impact.ai_budget_reservation WHERE tenant_id=%s AND job_id=%s",
            (tenant, accepted["job_id"]),
        ).fetchone()
        assert reservation["state"] == "RESERVED" and reservation["estimated_units"] == 1
        assert reservation["actual_units"] is None

    cancelled = jobs.cancel(identity, tenant, accepted["job_id"])
    assert cancelled["state"] == "Cancelled"
    assert cancelled["progress"] == 100 and cancelled["can_cancel"] is False
    assert cancelled["cancellation_requested"] is True
    with db.transaction(tenant) as c:
        released = c.execute(
            "SELECT state,estimated_units,actual_units FROM impact.ai_budget_reservation WHERE tenant_id=%s AND job_id=%s",
            (tenant, accepted["job_id"]),
        ).fetchone()
        assert released == {"state": "RELEASED", "estimated_units": 1, "actual_units": 0}
