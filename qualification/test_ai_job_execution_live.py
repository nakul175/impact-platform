"""Restricted-worker positive journey for FR-AI-016b / APL-346."""

from datetime import timedelta
from uuid import uuid4

from starlette.requests import Request

from impact_api import ai_enablement as enablement_module
from impact_api import ai_jobs as jobs_module
from impact_api import keyring
from impact_api import worker as worker_module
from impact_api.ai_enablement import AIEnablement
from impact_api.ai_jobs import AIJobs
from impact_api.ai_policy import AIPolicy
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.service import Service
from impact_api.store import Database
from impact_api.worker import empty_summary
from test_worker import make_worker


def _profile():
    return {
        "sector": "GENERAL",
        "team_size": 8,
        "goal": "Draft a synthetic public donor newsletter",
        "data_readiness": "BASIC",
        "ai_experience": "EXPERIMENTING",
        "sensitive_data": False,
    }


def test_restricted_worker_completes_fenced_job_and_settles_exact_budget(live, monkeypatch):
    monkeypatch.setattr(enablement_module, "require_exposure", lambda *_: {})
    monkeypatch.setattr(jobs_module, "require_exposure", lambda *_: {})
    monkeypatch.setattr(worker_module, "require_ai_safety_available", lambda *_: None)
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

    class ApiProvider:
        configured = True
        destination = "openai-us"
        evaluation_configuration = {}

    enablement = AIEnablement(Service(settings, db), ApiProvider(), enabled=True)
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
                        "budget_units": 2,
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

    observed = {}

    class WorkerProvider:
        configured = True
        destination = "openai-us"
        evaluation_configuration = {}

        def generate(self, profile, assessment):
            observed["profile"] = profile
            observed["assessment"] = assessment
            return {"text": "Synthetic advisory draft for human review.", "model": "synthetic-v1"}

    worker = make_worker(
        live,
        probe=lambda active: observed.update(provider_outside_transaction=active.connection is None),
        ai_enabled=True,
        ai_api_key="synthetic-worker-key",
        ai_job_timeout_seconds=1200,
    )
    worker.ai_provider = WorkerProvider()
    [claimed] = worker.claim_ai_jobs(tenant)
    assert str(claimed["job_id"]) == accepted["job_id"]
    assert claimed["lease_generation"] == 1 and claimed["attempts"] == 1
    assert claimed["deadline_at"] - claimed["started_at"] == timedelta(minutes=20)

    summary = empty_summary()
    worker.process_ai_job(tenant, claimed, summary)
    assert summary["ai_succeeded"] == 1 and observed["provider_outside_transaction"] is True
    assert observed["profile"] == {**_profile(), "team_size": 10}
    assert observed["assessment"]["method"] == "DETERMINISTIC_RULES"

    status = jobs.status(identity, tenant, accepted["job_id"])
    assert status == {
        **status,
        "state": "Succeeded",
        "progress": 100,
        "can_cancel": False,
        "outcome": "SUCCEEDED",
        "complete": True,
        "label": "Advisory draft",
        "can_publish_final": True,
    }
    with db.transaction(tenant) as c:
        persisted = c.execute(
            "SELECT j.state,j.lease_generation,j.lease_expires_at,a.lease_owner,a.completed_at,"
            "o.outcome,o.complete,o.label,o.model_identifier,o.actual_units,r.state AS budget_state,"
            "r.estimated_units,r.actual_units AS budget_actual "
            "FROM impact.job j JOIN impact.ai_advisory_job a USING(tenant_id,job_id) "
            "JOIN impact.ai_advisory_job_output o USING(tenant_id,job_id) "
            "JOIN impact.ai_budget_reservation r USING(tenant_id,job_id) "
            "WHERE j.tenant_id=%s AND j.job_id=%s",
            (tenant, accepted["job_id"]),
        ).fetchone()
    assert persisted["state"] == "Succeeded"
    assert persisted["lease_generation"] == 1 and persisted["lease_expires_at"] is None
    assert persisted["lease_owner"] is None and persisted["completed_at"] is not None
    assert (persisted["outcome"], persisted["complete"], persisted["label"]) == (
        "SUCCEEDED",
        True,
        "Advisory draft",
    )
    assert persisted["model_identifier"] == "synthetic-v1" and persisted["actual_units"] == 1
    assert (persisted["budget_state"], persisted["estimated_units"], persisted["budget_actual"]) == (
        "SETTLED",
        1,
        1,
    )

    # A worker has no requester identity with which to recheck current source authority. Preserve
    # the fail-closed branch with an exact sealed source-dependent request and no provider call.
    dependent_body = {**body, "operation_id": str(uuid4())}
    dependent = jobs.submit(identity, tenant, dependent_body)
    sealed_body = {
        **dependent_body,
        "source_dependencies": [
            {
                "object_id": str(uuid4()),
                "revision_id": str(uuid4()),
                "object_type": "Evidence",
                "capability": "evidence.read",
            }
        ],
    }
    sealed = keyring.ring(worker.s, "delivery").seal(
        jobs_module._key,
        jobs_module._json(sealed_body),
        jobs_module._binding(tenant, dependent["job_id"]),
    )
    with live.db() as c:
        c.execute(
            "UPDATE impact.ai_advisory_job SET sealed_request=%s WHERE tenant_id=%s AND job_id=%s",
            (sealed, tenant, dependent["job_id"]),
        )
    [dependent_claim] = worker.claim_ai_jobs(tenant)
    refused = empty_summary()
    worker.process_ai_job(tenant, dependent_claim, refused)
    assert refused["ai_failed"] == 1
    assert jobs.status(identity, tenant, dependent["job_id"])["outcome"] == "FAILED"
    with db.transaction(tenant) as c:
        blocked = c.execute(
            "SELECT a.last_error_class,r.state,r.actual_units FROM impact.ai_advisory_job a "
            "JOIN impact.ai_budget_reservation r USING(tenant_id,job_id) "
            "WHERE a.tenant_id=%s AND a.job_id=%s",
            (tenant, dependent["job_id"]),
        ).fetchone()
    assert blocked == {
        "last_error_class": "SOURCE_AUTHORITY_RECHECK_REQUIRED",
        "state": "SETTLED",
        "actual_units": 0,
    }
