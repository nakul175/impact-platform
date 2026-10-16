"""Component-only qualification for the three reserved governed-action AI candidates.

The production policy deliberately keeps these use cases reserved-disabled.  These tests replace
only the policy and safety gates with an in-process synthetic qualification gate; they do not
change the stored tenant policy, runtime configuration, or production activation rules.  The
tests exercise service authorization, storage, the ordinary command dispatcher and
transaction boundaries behind those gates.
"""

from types import SimpleNamespace
from uuid import UUID, uuid4
import hashlib

import psycopg
import pytest
from starlette.requests import Request

from impact_api import ai_action_proposals, ai_proactive_findings, ai_qualitative_assistance
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.service import Service
from impact_api.store import Context, Database, write
from test_evidence import evidence, unique, uploaded
from test_forms import temporary_grants
from test_live_application import expect


@pytest.fixture
def component_services(live, monkeypatch):
    """Build component-only services behind an isolated synthetic policy/safety boundary.

    This does not prove a runtime-authorized positive journey.  The external API process and its
    persisted reserved-disabled policy remain untouched; this fixture qualifies service behavior
    that will sit behind a future reviewed activation.
    """

    synthetic_policy = {"version": 1, "use_cases": {}}
    policy_calls = []

    def synthetic_require(policy, use_case, version, classification, *rest):
        policy_calls.append((use_case, version, classification))

    monkeypatch.setattr(ai_qualitative_assistance.ai_policy, "in_force", lambda *_: synthetic_policy)
    monkeypatch.setattr(ai_qualitative_assistance.ai_policy, "require", synthetic_require)
    for module in (ai_qualitative_assistance, ai_proactive_findings, ai_action_proposals):
        monkeypatch.setattr(module, "require_available", lambda *_: None)
    settings = Settings(**live.config)
    database = Database(settings)
    service = Service(settings, database)
    return SimpleNamespace(
        database=database,
        policy_calls=policy_calls,
        qualitative=ai_qualitative_assistance.AIQualitativeAssistance(
            service, "openai-us", {"qualification": "component-only"}
        ),
        findings=ai_proactive_findings.AIProactiveFindings(
            service, "openai-us", {"qualification": "component-only"}
        ),
        actions=ai_action_proposals.AIActionProposals(
            service, "openai-us", {"qualification": "component-only"}
        ),
    )


@pytest.fixture
def governed_ai_grants(live):
    revoke = temporary_grants(
        live,
        "author",
        [
            "qualitative-extracts.draft.create",
            "qualitative-extracts.read",
            "evidence.read",
            "ai.enablement.manage",
            "calculated-results.read",
            "programmes.read",
            "work-items.draft.create",
            "work-items.read",
        ],
    )
    try:
        yield
    finally:
        revoke()


def _identity(live, database, actor="author"):
    return Auth(Settings(**live.config), database).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token(actor)).encode())],
            }
        )
    )


def _count(live, table, object_type=None):
    tenant = live.fixture["tenant_a"]
    with live.db() as connection:
        if object_type is not None:
            return connection.execute(
                f"SELECT count(*) AS n FROM impact.{table} WHERE tenant_id=%s AND object_type=%s",
                (tenant, object_type),
            ).fetchone()["n"]
        return connection.execute(
            f"SELECT count(*) AS n FROM impact.{table} WHERE tenant_id=%s", (tenant,)
        ).fetchone()["n"]


def _assert_app_cannot_update(database, tenant, table):
    with database.transaction(tenant) as connection:
        privilege = connection.execute(
            "SELECT has_table_privilege(current_user, %s, 'UPDATE') AS allowed",
            (f"impact.{table}",),
        ).fetchone()
        assert privilege["allowed"] is False
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with database.transaction(tenant) as connection:
            connection.execute(f"UPDATE impact.{table} SET tenant_id=tenant_id")


def _seed(live, kind, payload, state="Draft"):
    actor = live.fixture["actors"]["author"]
    ctx = Context(
        actor["tenant_id"],
        actor["principal_id"],
        actor["membership_id"],
        SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
        0,
        0,
        [],
    )
    with live.db() as connection:
        connection.execute("SELECT set_config('impact.tenant_id',%s,true)", (actor["tenant_id"],))
        return write(connection, ctx, kind, payload, state)


def _text_evidence(live, text):
    body = unique(text.encode())
    upload = uploaded(live, body, "text/plain", "synthetic-interview.txt")
    return expect(
        evidence(
            live,
            upload["upload_id"],
            evidence_type="INTERVIEW_TRANSCRIPT",
            source="Synthetic qualification interview",
        ),
        201,
    ), body.decode()


def _programme(live):
    return live.records["programme_a"]


def test_apl_597_source_bound_suggestions_refuse_fabrication_and_recover(
    live, governed_ai_grants, component_services
):
    """APL-597 component: traceable views, individual review and atomic output refusal."""

    positive, positive_text = _text_evidence(live, "The service was easy to reach.\n")
    opposing, opposing_text = _text_evidence(live, "El servicio fue difícil de alcanzar.\n")
    codebook = _seed(
        live,
        "Codebook",
        {"codes": [{"code": "ACCESS_POSITIVE"}, {"code": "ACCESS_BARRIER"}]},
        "Approved",
    )

    def candidate(source, text, viewpoint, code, translation=None):
        excerpt = text.splitlines()[0]
        return {
            "source_revision_id": source["revision_id"],
            "viewpoint": viewpoint,
            "start_character": 0,
            "end_character": len(excerpt),
            "excerpt": excerpt,
            "excerpt_sha256": hashlib.sha256(excerpt.encode()).hexdigest(),
            "speaker_reference": None,
            "suggested_codes": [code],
            "theme": "Service access",
            "translation_language": "en" if translation else None,
            "translation_text": translation,
        }

    sources = [
        {"object_id": positive["object_id"], "revision_id": positive["revision_id"], "language": "en"},
        {"object_id": opposing["object_id"], "revision_id": opposing["revision_id"], "language": "es"},
    ]
    candidates = [
        candidate(positive, positive_text, "Service was accessible", "ACCESS_POSITIVE"),
        candidate(
            opposing,
            opposing_text,
            "Service was difficult to access",
            "ACCESS_BARRIER",
            "The service was difficult to reach.",
        ),
    ]
    operation_id = str(uuid4())
    request = {
        "operation_id": operation_id,
        "codebook_id": codebook["object_id"],
        "codebook_revision_id": codebook["revision_id"],
        "sources": sources,
        "candidates": candidates,
        "policy_version": 1,
        "language": "en",
    }

    before = _count(live, "ai_qualitative_run")
    fabricated = {**request, "candidates": [{**candidates[0], "excerpt": "Invented quotation"}]}
    actor = _identity(live, component_services.database)
    tenant = live.fixture["tenant_a"]
    with pytest.raises(DomainError) as refused:
        component_services.qualitative.create(actor, tenant, fabricated, str(uuid4()))
    assert (refused.value.status, refused.value.reason) == (
        422,
        "QUALITATIVE_QUOTATION_FABRICATED",
    )
    assert _count(live, "ai_qualitative_run") == before

    partner = _identity(live, component_services.database, "partner")
    with pytest.raises(DomainError) as denied:
        component_services.qualitative.create(partner, tenant, request, str(uuid4()))
    assert (denied.value.status, denied.value.code) in {
        (403, "POLICY_DENIED"),
        (404, "RESOURCE_UNAVAILABLE"),
    }
    assert _count(live, "ai_qualitative_run") == before

    run = component_services.qualitative.create(actor, tenant, request, str(uuid4()))
    _assert_app_cannot_update(component_services.database, tenant, "ai_qualitative_suggestion")
    assert run["individual_review_required"] is True and run["consensus_inferred"] is False
    assert {item["viewpoint"] for item in run["suggestions"]} == {
        "Service was accessible",
        "Service was difficult to access",
    }
    translated = next(item for item in run["suggestions"] if item["translation_text"])
    assert translated["translation_status"] == "MACHINE_UNREVIEWED"

    review_operation = str(uuid4())
    unreviewed = {
        "operation_id": review_operation,
        "disposition": "ACCEPTED",
        "final_codes": ["ACCESS_BARRIER"],
        "final_theme": "Service access barrier",
        "final_translation": "Human changed translation.",
        "translation_reviewed": False,
    }
    before_reviews = _count(live, "ai_qualitative_review")
    before_extracts = _count(live, "object_registry")
    with pytest.raises(DomainError) as refused:
        component_services.qualitative.review(
            actor, tenant, UUID(translated["suggestion_id"]), unreviewed, str(uuid4())
        )
    assert (refused.value.status, refused.value.reason) == (
        422,
        "QUALITATIVE_TRANSLATION_REVIEW_REQUIRED",
    )
    assert _count(live, "ai_qualitative_review") == before_reviews
    assert _count(live, "object_registry") == before_extracts

    accepted = component_services.qualitative.review(
        actor,
        tenant,
        UUID(translated["suggestion_id"]),
        {**unreviewed, "translation_reviewed": True},
        str(uuid4()),
    )
    assert accepted["disposition"] == "ACCEPTED"
    assert accepted["translation_status"] == "HUMAN_REVIEWED"
    assert accepted["qualitative_extract_id"] and accepted["source_classification_inherited"]

    first = next(item for item in run["suggestions"] if item["suggestion_id"] != translated["suggestion_id"])
    rejected = component_services.qualitative.review(
        actor,
        tenant,
        UUID(first["suggestion_id"]),
        {
            "operation_id": str(uuid4()),
            "disposition": "REJECTED",
            "final_codes": [],
            "final_theme": None,
            "final_translation": None,
            "translation_reviewed": False,
        },
        str(uuid4()),
    )
    assert rejected["disposition"] == "REJECTED" and rejected["qualitative_extract_id"] is None


def test_apl_601_suggestions_remain_unconfirmed_and_disabled_tasks_recover(
    live, governed_ai_grants, component_services
):
    """APL-601 component: a suggestion can be dismissed without mutating its sources."""

    programme = _programme(live)
    source, _ = _text_evidence(live, "A seasonal performance spike was observed.\n")
    result = _seed(live, "CalculatedResult", {"value_state": "PRESENT", "value": "25"}, "Approved")
    owner = live.fixture["actors"]["author"]["principal_id"]
    actor = _identity(live, component_services.database)
    partner = _identity(live, component_services.database, "partner")
    tenant = live.fixture["tenant_a"]

    def configure(enabled, code, identity=actor):
        return component_services.findings.configure(
            identity,
            tenant,
            {
                "operation_id": str(uuid4()),
                "task_code": code,
                "scope_object_id": programme["object_id"],
                "scope_revision_id": programme["revision_id"],
                "owner_principal_id": owner,
                "cooldown_seconds": 60,
                "noise_limit": 2,
                "enabled": enabled,
                "policy_version": 1,
                "language": "en",
            },
        )

    disabled = configure(False, "SEASONAL_DISABLED")
    _assert_app_cannot_update(component_services.database, tenant, "ai_detection_task")
    finding = {
        "operation_id": str(uuid4()),
        "task_id": disabled["task_id"],
        "detection_event_key": "seasonal-spike-01",
        "affected_results": [{"object_id": result["object_id"], "revision_id": result["revision_id"]}],
        "evidence": [{"object_id": source["object_id"], "revision_id": source["revision_id"]}],
        "summary": "A performance spike needs human review.",
        "limitation": "One synthetic period cannot establish impact or fraud.",
        "proposed_follow_up": "Compare against the prior seasonal period.",
        "language": "en",
    }
    before = _count(live, "ai_suggested_finding")
    with pytest.raises(DomainError) as refused:
        component_services.findings.suggest(actor, tenant, finding)
    assert (refused.value.status, refused.value.reason) == (404, "DETECTION_TASK_NOT_ENABLED")
    assert _count(live, "ai_suggested_finding") == before

    with pytest.raises(DomainError) as denied:
        configure(True, "SEASONAL_PARTNER", partner)
    assert (denied.value.status, denied.value.code) in {
        (403, "POLICY_DENIED"),
        (404, "RESOURCE_UNAVAILABLE"),
    }

    enabled = configure(True, "SEASONAL_ENABLED")
    finding = {**finding, "task_id": enabled["task_id"]}
    assert _count(live, "ai_suggested_finding") == before

    suggested = component_services.findings.suggest(actor, tenant, finding)
    assert suggested["status"] == "SUGGESTED" and suggested["confirmed_finding"] is False
    assert suggested["affected_results"] == finding["affected_results"]
    assert suggested["evidence"] == finding["evidence"]
    assert suggested["limitation"] == finding["limitation"]
    assert suggested["proposed_follow_up"] == finding["proposed_follow_up"]

    with live.db() as connection:
        tenant = live.fixture["tenant_a"]
        source_before = connection.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (tenant, result["revision_id"]),
        ).fetchone()["payload"]
    feedback = component_services.findings.review(
        actor,
        tenant,
        UUID(suggested["suggestion_id"]),
        {
            "operation_id": str(uuid4()),
            "decision": "DISMISSED",
            "reason": "The reviewed spike is seasonal.",
            "assigned_to": None,
        },
    )
    assert feedback["decision"] == "DISMISSED" and feedback["source_values_changed"] is False
    with live.db() as connection:
        source_after = connection.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (live.fixture["tenant_a"], result["revision_id"]),
        ).fetchone()["payload"]
    assert source_after == source_before

    with pytest.raises(DomainError) as cooldown:
        component_services.findings.suggest(
            actor,
            tenant,
            {**finding, "operation_id": str(uuid4()), "detection_event_key": "seasonal-spike-02"},
        )
    assert (cooldown.value.status, cooldown.value.reason) == (409, "DETECTION_COOLDOWN_ACTIVE")
    assert _count(live, "ai_suggested_finding") == before + 1


def test_apl_541_confirmation_uses_ordinary_command_and_refusal_is_recoverable(
    live, governed_ai_grants, component_services
):
    """APL-541 component: inspectable proposal, protected refusal and authority recheck."""

    programme = _programme(live)
    source, _ = _text_evidence(live, "A reviewed follow-up action is required.\n")
    request = {
        "operation_id": str(uuid4()),
        "command_type": "CREATE_WORK_ITEM_DRAFT",
        "scope_object_id": programme["object_id"],
        "scope_revision_id": programme["revision_id"],
        "after_values": {
            "programme_id": programme["object_id"],
            "work_type": "ACTION",
            "title": "Review the synthetic programme follow-up",
            "dependency_ids": [],
        },
        "affected_versions": [
            {
                "object_type": "Evidence",
                "object_id": source["object_id"],
                "revision_id": source["revision_id"],
            }
        ],
        "policy_version": 1,
        "consequences": ["Creates one ordinary draft work item after explicit confirmation."],
        "language": "en",
    }

    before_proposals = _count(live, "ai_action_proposal")
    actor = _identity(live, component_services.database)
    partner = _identity(live, component_services.database, "partner")
    tenant = live.fixture["tenant_a"]
    with pytest.raises(DomainError) as protected:
        component_services.actions.create(
            actor,
            tenant,
            {**request, "command_type": "PRIVACY_DELETE", "operation_id": str(uuid4())},
        )
    assert (protected.value.status, protected.value.reason) == (422, "AI_PROTECTED_COMMAND_REFUSED")
    assert _count(live, "ai_action_proposal") == before_proposals

    with pytest.raises(DomainError) as denied:
        component_services.actions.create(partner, tenant, request)
    assert (denied.value.status, denied.value.code) in {
        (403, "POLICY_DENIED"),
        (404, "RESOURCE_UNAVAILABLE"),
    }
    assert _count(live, "ai_action_proposal") == before_proposals

    work_before = _count(live, "object_registry")
    proposal = component_services.actions.create(actor, tenant, request)
    _assert_app_cannot_update(component_services.database, tenant, "ai_action_proposal")
    assert ("ACTION_PROPOSAL", 1, "INTERNAL") in component_services.policy_calls
    assert proposal["command_type"] == "CREATE_WORK_ITEM_DRAFT"
    assert proposal["scope_object_id"] == programme["object_id"]
    assert proposal["before_values"] is None and proposal["after_values"] == request["after_values"]
    assert proposal["affected_versions"] == request["affected_versions"]
    assert proposal["policy_version"] == 1 and proposal["consequences"] == request["consequences"]
    assert proposal["confirmation_required"] is True and proposal["domain_side_effects_created"] is False
    assert _count(live, "object_registry") == work_before

    # A second principal receives only temporary current authority.  Revocation between proposal
    # generation and confirmation must not leave an execution receipt or WorkItem; restoring the
    # authority lets the same confirmation operation recover safely.
    reviewer_grant = temporary_grants(
        live,
        "reviewer",
        [
            "ai.enablement.manage",
            "work-items.draft.create",
            "work-items.read",
            "programmes.read",
            "evidence.read",
        ],
    )
    reviewer_request = {**request, "operation_id": str(uuid4())}
    reviewer = _identity(live, component_services.database, "reviewer")
    reviewer_proposal = component_services.actions.create(reviewer, tenant, reviewer_request)
    reviewer_grant()
    confirmation = {"operation_id": str(uuid4()), "language": "en"}
    before_confirmations = _count(live, "ai_action_confirmation")
    before_work_items = _count(live, "object_registry", "WorkItem")
    before_audits = _count(live, "object_registry", "AuditEvent")
    with pytest.raises(DomainError) as refused:
        component_services.actions.confirm(
            reviewer,
            tenant,
            UUID(reviewer_proposal["proposal_id"]),
            confirmation,
            str(uuid4()),
        )
    assert (refused.value.status, refused.value.code) == (404, "RESOURCE_UNAVAILABLE")
    assert _count(live, "ai_action_confirmation") == before_confirmations
    assert _count(live, "object_registry", "WorkItem") == before_work_items
    assert _count(live, "object_registry", "AuditEvent") == before_audits

    restored = temporary_grants(
        live,
        "reviewer",
        [
            "ai.enablement.manage",
            "work-items.draft.create",
            "work-items.read",
            "programmes.read",
            "evidence.read",
        ],
    )
    try:
        confirmed = component_services.actions.confirm(
            reviewer,
            tenant,
            UUID(reviewer_proposal["proposal_id"]),
            confirmation,
            str(uuid4()),
        )
        replay = component_services.actions.confirm(
            reviewer,
            tenant,
            UUID(reviewer_proposal["proposal_id"]),
            confirmation,
            str(uuid4()),
        )
    finally:
        restored()
    assert confirmed == replay
    assert confirmed["ordinary_command"] == "create_work_items"
    assert confirmed["protected_write"] is False
    assert _count(live, "ai_action_confirmation") == before_confirmations + 1
    assert _count(live, "object_registry", "WorkItem") == before_work_items + 1
    assert _count(live, "object_registry", "AuditEvent") == before_audits + 1
