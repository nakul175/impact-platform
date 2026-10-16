"""Whole positive containment journey for FR-AI-018 / APL-347."""

from uuid import uuid4

import pytest

from impact_api.ai_safety import configuration_id, require_available
from impact_api.contracts import validate
from impact_api.domain import DomainError
from test_ai_forecast_scenarios_live import _official_result
from test_forms import temporary_grants
from test_live_application import expect


def test_minimal_feedback_and_scoped_shutdown_contain_ai_without_stopping_manual_work(live):
    result = _official_result(live, 10)
    revoke = temporary_grants(live, "admin", ["calculated-results.read"])
    forecast_path = live.path("ai-enablement/forecasts")
    forecast = expect(
        live.request(
            forecast_path,
            actor="admin",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "scenario_id": None,
                "label": "Safety feedback fixture",
                "horizon": 1,
                "method": "LINEAR_TREND_V1",
                "assumptions": ["Synthetic containment qualification"],
                "input_result_revisions": [result["revision_id"]],
            },
        ),
        200,
    )

    feedback_path = live.path("ai-enablement/safety-feedback")
    feedback = expect(
        live.request(
            feedback_path,
            actor="admin",
            method="POST",
            body={
                "output_kind": "FORECAST",
                "output_id": forecast["scenario_id"],
                "category": "UNSUPPORTED_CLAIM",
                "safe_detail": "Projection needs an additional source review.",
                "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
            },
        ),
        200,
    )
    validate("AISafetyFeedback", feedback)
    assert feedback["output_id"] == forecast["scenario_id"]
    assert feedback["reviewer_id"] == live.fixture["actors"]["reviewer"]["principal_id"]
    assert feedback["source_payload_retained"] is False

    prohibited = expect(
        live.request(
            feedback_path,
            actor="admin",
            method="POST",
            body={
                "output_kind": "FORECAST",
                "output_id": forecast["scenario_id"],
                "category": "OTHER",
                "safe_detail": "Contact reviewer@example.org and use password=synthetic-secret",
                "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
            },
        ),
        400,
    )
    assert prohibited["reason_code"] == "AI_FEEDBACK_DETAIL_PROHIBITED"

    tenant = live.fixture["tenant_a"]
    queued_job = str(uuid4())
    # Keep this containment exercise scoped to its own synthetic configuration. Shutdown events
    # are deliberately append-only and recovery needs a second tenant administrator, which this
    # fixture does not invent. A unique selector proves containment without changing the shared
    # ADVISORY_DRAFT state consumed by later whole-journey tests.
    configuration = {"qualification_run_id": str(uuid4())}
    shutdown_value = configuration_id(configuration)
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        scope = c.execute(
            "SELECT scope_id FROM impact.scope_definition WHERE tenant_id=%s AND scope_type='TENANT' LIMIT 1",
            (tenant,),
        ).fetchone()["scope_id"]
        c.execute(
            "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest) "
            "VALUES(%s,%s,'AI_ADVISORY',%s,%s,'Queued',%s)",
            (
                tenant,
                queued_job,
                live.fixture["actors"]["admin"]["principal_id"],
                scope,
                '{"use_case":"ADVISORY_DRAFT","destination":"openai-us",'
                f'"configuration_id":"{shutdown_value}"}}',
            ),
        )

    shutdown_path = live.path("ai-enablement/safety-shutdowns")
    disabled = expect(
        live.request(
            shutdown_path,
            actor="admin",
            method="POST",
            body={
                "scope_kind": "CONFIGURATION",
                "scope_value": shutdown_value,
                "action": "DISABLE",
                "reason_category": "UNSUPPORTED_CLAIM",
                "disabled_event_id": None,
            },
        ),
        200,
    )
    validate("AIShutdownResult", disabled)
    assert disabled["queued_jobs_stopped"] == [queued_job]
    assert disabled["manual_workflows_enabled"] is True
    assert disabled["source_payload_retained"] is False
    assert isinstance(disabled["affected_artifacts"], list)

    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        job = c.execute(
            "SELECT state,output_manifest FROM impact.job WHERE tenant_id=%s AND job_id=%s",
            (tenant, queued_job),
        ).fetchone()
        assert job["state"] == "Cancelled"
        assert job["output_manifest"] == {
            "outcome": "CANCELLED",
            "reason": "AI_SAFETY_SHUTDOWN",
        }
        with pytest.raises(DomainError) as stopped:
            require_available(c, tenant, "ADVISORY_DRAFT", "openai-us", configuration)
    assert (stopped.value.status, stopped.value.reason) == (503, "AI_SAFETY_SHUTDOWN")

    status = expect(live.request(shutdown_path, actor="admin"), 200)
    validate("AIShutdownStatus", status)
    assert any(
        item["scope_kind"] == "CONFIGURATION"
        and item["scope_value"] == shutdown_value
        and item["state"] == "DISABLED"
        for item in status["shutdowns"]
    )
    assert status["manual_workflows_enabled"] is True

    refused = expect(
        live.request(
            shutdown_path,
            actor="admin",
            method="POST",
            body={
                "scope_kind": "CONFIGURATION",
                "scope_value": shutdown_value,
                "action": "REENABLE",
                "reason_category": "OTHER",
                "disabled_event_id": disabled["event_id"],
            },
        ),
        409,
    )
    assert refused["reason_code"] == "AI_REENABLE_APPROVAL_INVALID"

    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        stored = c.execute(
            "SELECT category,safe_detail,submitted_by::text,reviewer_id::text "
            "FROM impact.ai_safety_feedback WHERE tenant_id=%s AND feedback_id=%s",
            (tenant, feedback["feedback_id"]),
        ).fetchone()
        assert stored["category"] == "UNSUPPORTED_CLAIM"
        assert stored["safe_detail"] == "Projection needs an additional source review."
        assert stored["submitted_by"] == live.fixture["actors"]["admin"]["principal_id"]
        assert stored["reviewer_id"] == live.fixture["actors"]["reviewer"]["principal_id"]
        columns = {
            item["column_name"]
            for item in c.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='impact' AND table_name='ai_safety_feedback'"
            ).fetchall()
        }
        assert not {"source_payload", "prompt", "provider_response", "credentials"} & columns
    revoke()
