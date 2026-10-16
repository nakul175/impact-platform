"""Positive live journey for FR-AI-013 / APL-342 AI answer provenance."""

from uuid import uuid4

import pytest
from starlette.requests import Request

from impact_api import ai_enablement as enablement_module
from impact_api.ai_enablement import AIEnablement
from impact_api.ai_policy import AIPolicy
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Database
from test_administration import action
from test_ai_enablement_live import profile
from test_live_application import expect


@pytest.fixture(autouse=True)
def passed_advisory_evaluation(monkeypatch):
    monkeypatch.setattr(enablement_module, "require_exposure", lambda use_case, configuration: {})


def _identity(live, db, actor):
    return Auth(Settings(**live.config), db).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token(actor)).encode())],
            }
        )
    )


def test_saved_answer_pins_exact_sources_and_rechecks_current_access_on_replay(live):
    settings = Settings(**live.config)
    db, tenant = Database(settings), live.fixture["tenant_a"]
    admin, author = _identity(live, db, "admin"), _identity(live, db, "author")

    class Provider:
        configured = True
        destination = "openai-us"
        evaluation_configuration = {}
        calls = 0

        def generate(self, supplied, assessment):
            self.calls += 1
            return {"text": "SYNTHETIC: review the cited evidence.", "model": "synthetic-provenance"}

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
    evidence = expect(live.request(live.path("evidence", live.records["evidence_a"]["object_id"])), 200)
    dependency = {
        "object_id": evidence["object_id"],
        "revision_id": evidence["revision_id"],
        "object_type": "Evidence",
        "capability": "evidence.read",
    }
    request = {
        "operation_id": str(uuid4()),
        "profile": profile(),
        "consent": True,
        "policy_version": enabled["policy_version"],
        "purpose": "AI_ADOPTION_ADVISORY",
        "source_dependencies": [dependency],
    }
    first = api.advisory(author, tenant, request, str(uuid4()))
    assert first["trace"]["source_versions"] == [
        {key: dependency[key] for key in ("object_id", "revision_id", "object_type")}
    ]
    assert api.advisory(author, tenant, request, str(uuid4())) == first
    assert provider.calls == 1
    with db.transaction(tenant) as c:
        saved = c.execute(
            "SELECT v.payload FROM impact.ai_advisory_request q "
            "JOIN impact.object_registry r ON r.tenant_id=q.tenant_id AND r.object_id=q.object_id "
            "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE q.tenant_id=%s AND q.request_id=%s",
            (tenant, request["operation_id"]),
        ).fetchone()["payload"]
        linked = c.execute(
            "SELECT source_object_id::text,source_revision_id::text,source_object_type,required_capability "
            "FROM impact.ai_advisory_source WHERE tenant_id=%s AND request_id=%s",
            (tenant, request["operation_id"]),
        ).fetchone()
    assert saved["source_dependencies"] == [dependency]
    assert saved["permitted_audience"] == [live.fixture["actors"]["author"]["principal_id"]]
    assert dict(linked) == {
        "source_object_id": dependency["object_id"],
        "source_revision_id": dependency["revision_id"],
        "source_object_type": "Evidence",
        "required_capability": "evidence.read",
    }

    grant = live.records["grant:author:evidence.read"]
    with db.transaction(tenant) as c:
        current_grant_revision = str(
            c.execute(
                "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                (tenant, grant["object_id"]),
            ).fetchone()["head_revision"]
        )
    expect(
        action(
            live,
            "grants",
            grant["object_id"],
            "revoke",
            current_grant_revision,
            actor="admin",
        ),
        200,
    )
    with pytest.raises(DomainError) as revoked:
        api.advisory(author, tenant, request, str(uuid4()))
    assert (revoked.value.status, revoked.value.code) == (404, "RESOURCE_UNAVAILABLE")
    assert provider.calls == 1

    partner = _identity(live, db, "partner")
    with pytest.raises(DomainError) as copied:
        api.advisory(partner, tenant, request, str(uuid4()))
    assert copied.value.status == 404
