"""Real API and database qualification, always using synthetic provider output."""

from uuid import uuid4

import pytest
from starlette.requests import Request

from impact_api.ai_enablement import AIEnablement
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database
from test_live_application import expect


def profile():
    return {
        "sector": "GENERAL",
        "team_size": 8,
        "goal": "Draft a public donor newsletter",
        "data_readiness": "BASIC",
        "ai_experience": "EXPERIMENTING",
        "sensitive_data": False,
    }


def test_readiness_api_and_separate_advisory_authority(live):
    path = live.path("ai-enablement")
    data = expect(live.request(path + "/catalog"), 200)
    assert data["marketplace_status"]["vendors"] == []
    assert data["advisory_available"] is False
    result = expect(live.request(path + "/assessment", method="POST", body={"profile": profile()}), 200)
    assert result["assessment"]["recommendations"]
    expect(live.request(path + "/catalog", actor="other_tenant"), 404)
    expect(live.request(path + "/catalog", actor="revoked"), 404)
    expect(
        live.request(
            path + "/assessment", method="POST", body={"profile": {**profile(), "official_value": "10"}}
        ),
        422,
    )
    request = {"operation_id": str(uuid4()), "profile": profile(), "consent": True}
    # This fixture author is also a programme manager. Narrow the synthetic advisory grant
    # temporarily to prove that ordinary read access does not authorize provider requests.
    grant = None
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        grant = c.execute(
            "SELECT g.object_id FROM impact.grant_current g JOIN impact.tenant_principal p ON p.tenant_id=g.tenant_id AND p.principal_id=g.subject_id WHERE g.tenant_id=%s AND p.identity_id=%s AND g.capability='ai.advisory.request' AND g.purpose IS NULL",
            (live.fixture["tenant_a"], live.fixture["actors"]["author"]["identity_id"]),
        ).fetchone()["object_id"]
        c.execute(
            "UPDATE impact.grant_current SET purpose='QUALIFICATION' WHERE tenant_id=%s AND object_id=%s",
            (live.fixture["tenant_a"], grant),
        )
    try:
        expect(live.request(path + "/catalog"), 200)
        expect(live.request(path + "/advisory", method="POST", body=request), 404)
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            c.execute(
                "UPDATE impact.grant_current SET purpose=NULL WHERE tenant_id=%s AND object_id=%s",
                (live.fixture["tenant_a"], grant),
            )
    unavailable = expect(live.request(path + "/advisory", actor="admin", method="POST", body=request), 503)
    assert unavailable["reason_code"] == "AI_NOT_CONFIGURED"
    expect(
        live.request(path + "/advisory", actor="admin", method="POST", body={**request, "consent": False}),
        422,
    )


def test_durable_sealed_replay_and_daily_budget_on_real_database(live):
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
        calls = 0

        def generate(self, supplied, assessment):
            self.calls += 1
            return {
                "text": "SYNTHETIC: test a public newsletter with a staff reviewer.",
                "model": "synthetic-test",
            }

    provider = Provider()
    api = AIEnablement(Service(settings, db), provider, enabled=True)
    request = {"operation_id": str(uuid4()), "profile": profile(), "consent": True}
    correlation = str(uuid4())
    first = api.advisory(identity, tenant, request, correlation)
    assert first == api.advisory(identity, tenant, request, str(uuid4()))
    assert first["status"] == "DRAFT" and provider.calls == 1
    with pytest.raises(DomainError) as changed:
        api.advisory(identity, tenant, {**request, "profile": {**profile(), "team_size": 9}}, str(uuid4()))
    assert changed.value.status == 409 and provider.calls == 1
    with db.transaction(tenant) as c:
        row = c.execute(
            "SELECT sealed_output FROM impact.ai_advisory_result WHERE tenant_id=%s AND request_id=%s",
            (tenant, request["operation_id"]),
        ).fetchone()
        assert b"SYNTHETIC" not in bytes(row["sealed_output"])
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current a JOIN impact.ai_advisory_request r ON r.tenant_id=a.tenant_id AND r.object_id=a.object_reference WHERE r.tenant_id=%s AND r.request_id=%s AND a.action_type='ai_advisory_completed'",
                (tenant, request["operation_id"]),
            ).fetchone()["n"]
            == 1
        )
    for _ in range(2):
        api.advisory(identity, tenant, {**request, "operation_id": str(uuid4())}, str(uuid4()))
    with pytest.raises(DomainError) as limited:
        api.advisory(identity, tenant, {**request, "operation_id": str(uuid4())}, str(uuid4()))
    assert limited.value.status == 429 and provider.calls == 3
    assert api.advisory(identity, tenant, request, str(uuid4())) == first
