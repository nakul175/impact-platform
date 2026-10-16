# ruff: noqa: F811
"""External HTTP journeys with real reviewed local activation, tenant policy and safety gates.

The component packs are retained separately. This pack uses no monkeypatches.
"""

import hashlib
from types import SimpleNamespace
from uuid import UUID, uuid4
import pytest
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.store import Database
from reviewed_ai_runtime_fixture import runtime, rules, save_policy
from test_ai_assistance_journeys_live import assistance_grants, ratio_sources, _object_count  # noqa: F401
from test_ai_governed_actions_live import (
    governed_ai_grants,  # noqa: F401
    _seed,
    _identity,
    _count,
    _assert_app_cannot_update,
    _programme,
    _text_evidence,
)  # noqa: F401
from test_forms import planned, temporary_grants
from test_import import HOUSEHOLDS, batch_data
from test_live_application import expect
from test_measurement import create, get


@pytest.fixture
def live(live, tmp_path):
    with runtime(live, tmp_path / "reviewed") as activated:
        previous = expect(activated.request(activated.path("ai-enablement/policy"), actor="admin"), 200)
        activated.default_runtime = live
        activated.policy_version = save_policy(activated, rules())
        try:
            yield activated
        finally:
            save_policy(activated, previous["use_cases"])


@pytest.fixture(autouse=True)
def verify_actual_policy_and_shutdown_gates(live, assistance_grants, governed_ai_grants, request):
    yield
    if request.node.name.startswith("test_apl_"):
        _assert_real_gates(live, live.default_runtime)


ROUTE_CASES = {
    "indicator-design/proposals": "INDICATOR_DESIGN",
    "import-assistance/": "IMPORT_CLEANING",
    "evidence-questions": "EVIDENCE_QUESTION",
    "numeric-analysis": "NUMERIC_ANALYSIS",
    "qualitative-runs": "QUALITATIVE_ASSISTANCE",
    "detection-tasks": "PROACTIVE_FINDINGS",
    "action-proposals": "ACTION_PROPOSAL",
}


def _assert_real_gates(activated, default_runtime):
    from copy import deepcopy
    from test_story_error_recovery_analytics_live import _durable_counts

    records = []
    for route, actor, method, body, status in activated.requests:
        if method == "POST" and status == 200 and isinstance(body, dict) and "policy_version" in body:
            for prefix, case in ROUTE_CASES.items():
                suffix = route.split("/ai-enablement/", 1)[-1]
                if suffix.startswith(prefix) and "/actions/" not in suffix:
                    records.append((route, actor, deepcopy(body), case))
    assert records, "A qualifying external runtime journey must have a successful policy-bound route"
    route, actor, body, case = records[-1]
    if case == "ACTION_PROPOSAL":
        route, actor, body, case = records[0]
    if case == "IMPORT_CLEANING":
        batch = route.split("/import-assistance/", 1)[1].split("/")[0]
        current = get(activated, "imports", batch)
        route = (
            activated.path("ai-enablement")
            + f"/import-assistance/{batch}/revisions/{current['revision_id']}/proposals"
        )
        body = {"policy_version": activated.policy_version, "language": "en"}

    def refused(client, reason):
        request = deepcopy(body)
        request["policy_version"] = activated.policy_version
        if "operation_id" in request:
            request["operation_id"] = str(uuid4())
        before = _durable_counts(activated)
        denied = expect(client.request(route, actor=actor, method="POST", body=request), 503)
        assert denied["reason_code"] == reason
        assert _durable_counts(activated) == before

    # A previously enabled persisted policy cannot bypass a process without reviewed activation.
    refused(default_runtime, "AI_USE_CASE_DISABLED")
    activated.policy_version = save_policy(
        activated, [dict(row, enabled=False) if row["use_case"] == case else row for row in rules()]
    )
    refused(activated, "AI_USE_CASE_DISABLED")
    activated.policy_version = save_policy(activated, rules())
    shutdown = expect(
        activated.request(
            activated.path("ai-enablement/safety-shutdowns"),
            actor="admin",
            method="POST",
            body={
                "scope_kind": "USE_CASE",
                "scope_value": case,
                "action": "DISABLE",
                "reason_category": "UNSUPPORTED_CLAIM",
                "disabled_event_id": None,
            },
        ),
        200,
    )
    assert shutdown["manual_workflows_enabled"] is True
    refused(activated, "AI_SAFETY_SHUTDOWN")
    # Ordinary manual programme reading remains available under the same real API.
    expect(activated.request(activated.path("programmes", _programme(activated)["object_id"])), 200)


def _post(live, suffix, body, *, actor="author", status=200):
    return expect(
        live.request(live.path("ai-enablement") + "/" + suffix, method="POST", actor=actor, body=body), status
    )


class HTTPService:
    """Translate the shared test scenario's service-shaped calls into actual HTTP requests."""

    def __init__(self, live, routes):
        self.live, self.routes = live, routes

    def __getattr__(self, method):
        def invoke(identity, tenant, *args):
            actor = next(
                name
                for name, row in self.live.fixture["actors"].items()
                if row["identity_id"] == str(identity.identity_id)
            )
            suffix = self.routes[method]
            if method in {"review", "confirm"}:
                suffix, body = suffix.format(id=args[0]), args[1]
            else:
                body = args[0]
            response = self.live.request(
                self.live.path("ai-enablement", tenant=str(tenant)) + "/" + suffix,
                actor=actor,
                method="POST",
                body=body,
            )
            data = response.json()
            if response.status_code >= 400:
                raise DomainError(data["code"], response.status_code, reason=data.get("reason_code"))
            return data

        return invoke


@pytest.fixture
def component_services(live):
    # Despite the shared scenario's fixture name, every story operation below is external HTTP.
    return SimpleNamespace(
        database=Database(Settings(**live.config)),
        qualitative=HTTPService(
            live, {"create": "qualitative-runs", "review": "qualitative-suggestions/{id}/actions/review"}
        ),
        findings=HTTPService(
            live,
            {
                "configure": "detection-tasks",
                "suggest": "suggested-findings",
                "review": "suggested-findings/{id}/actions/review",
            },
        ),
        actions=HTTPService(
            live, {"create": "action-proposals", "confirm": "action-proposals/{id}/actions/confirm"}
        ),
    )


def test_apl_533_indicator_proposal_refusal_is_atomic_then_valid_draft_recovers(
    live, assistance_grants, ratio_sources
):
    definition, programme, _, _ = ratio_sources
    source = {
        "library_definition_id": definition["object_id"],
        "library_definition_revision_id": definition["revision_id"],
        "programme_id": programme["object_id"],
        "programme_revision_id": programme["revision_id"],
        "policy_version": live.policy_version,
        "language": "en",
        "proxy_basis": "DIRECT",
    }
    denied = _post(live, "indicator-design/proposals", source, actor="partner", status=404)
    assert denied["code"] == "RESOURCE_UNAVAILABLE"

    proposal = _post(live, "indicator-design/proposals", source)
    assert proposal["can_approve"] is False
    assert proposal["model_confidence"] is None
    assert proposal["standard_mapping_created"] is False
    assert "DENOMINATOR_ELIGIBILITY_REQUIRES_HUMAN_REVIEW" in proposal["warnings"]

    before = _object_count(live, "IndicatorDefinition")
    invalid = _post(
        live,
        "indicator-design/drafts",
        {**source, "operation_id": str(uuid4()), "selected_fields": ["unsupported_field"]},
        status=400,
    )
    assert invalid["reason_code"] == "INDICATOR_FIELD_SELECTION_INVALID"
    assert _object_count(live, "IndicatorDefinition") == before

    fields = sorted(proposal["proposed_fields"])
    operation = str(uuid4())
    request = {**source, "operation_id": operation, "selected_fields": fields}
    created = _post(live, "indicator-design/drafts", request)
    assert created["business_state"] == "Draft"
    assert created["submit_ready"] is True
    assert created["standard_mapping_created"] is False
    assert _post(live, "indicator-design/drafts", request) == created
    from test_story_error_recovery_analytics_live import _durable_counts

    before_retry = _durable_counts(live)
    path = live.path("ai-enablement") + "/indicator-design/drafts"
    assert expect(live.default_runtime.request(path, method="POST", body=request), 200) == created
    expect(
        live.default_runtime.request(path, method="POST", body={**request, "selected_fields": fields[:-1]}),
        409,
    )
    fresh = expect(
        live.default_runtime.request(path, method="POST", body={**request, "operation_id": str(uuid4())}), 503
    )
    assert fresh["reason_code"] == "AI_USE_CASE_DISABLED"
    assert _durable_counts(live) == before_retry


def test_apl_535_import_diff_applies_only_selected_change_and_recovers_atomically(live, assistance_grants):
    indicator, period, _ = planned(live, **HOUSEHOLDS)
    content = "district,IMP,event_at\nNorth,12,2026-08-01\nSouth,7,2026-08-02\n"
    batch = create(
        live,
        "imports",
        batch_data(
            indicator,
            period,
            content,
            mapping={
                "unit_column": "district",
                "columns": [
                    {
                        "column": "IMP",
                        "indicator_id": indicator["object_id"],
                        "value_role": "VALUE",
                        "unit": "households",
                    }
                ],
                "event_at_column": "event_at",
            },
            date_pattern="DD/MM/YYYY",
        ),
    )
    suffix = f"import-assistance/{batch['object_id']}/revisions/{batch['revision_id']}"
    denied = _post(
        live,
        suffix + "/proposals",
        {"policy_version": live.policy_version, "language": "en"},
        actor="revoked",
        status=404,
    )
    assert denied["code"] == "RESOURCE_UNAVAILABLE"

    proposals = _post(live, suffix + "/proposals", {"policy_version": live.policy_version, "language": "en"})
    assert proposals["destructive_actions_available"] is False
    assert proposals["proposals"] and all(item["selected"] is False for item in proposals["proposals"])
    map_item = next(item for item in proposals["proposals"] if item["kind"] == "MAP_COLUMN")
    date_item = next(item for item in proposals["proposals"] if item["kind"] == "SET_DATE_PATTERN")
    raw_digest = proposals["raw_sha256"]

    before = get(live, "imports", batch["object_id"])
    invalid = _post(
        live,
        suffix + "/actions/apply",
        {
            "operation_id": str(uuid4()),
            "policy_version": live.policy_version,
            "language": "en",
            "selected_proposal_ids": [str(uuid4())],
        },
        status=400,
    )
    assert invalid["reason_code"] == "IMPORT_PROPOSAL_SELECTION_INVALID"
    assert get(live, "imports", batch["object_id"])["revision_id"] == before["revision_id"]

    operation = str(uuid4())
    request = {
        "operation_id": operation,
        "policy_version": live.policy_version,
        "language": "en",
        "selected_proposal_ids": [map_item["proposal_id"], date_item["proposal_id"]],
    }
    applied = _post(live, suffix + "/actions/apply", request)
    assert applied["raw_sha256"] == raw_digest
    assert applied["raw_rows_changed"] is False
    assert applied["identities_merged"] is False
    assert applied["approved_actuals_changed"] is False
    assert applied["mapping_diff"]["after"]["columns"] == [{"column": "IMP", **map_item["destination"]}]
    assert get(live, "imports", batch["object_id"])["data"]["date_pattern"] == "YYYY-MM-DD"
    assert _post(live, suffix + "/actions/apply", request) == applied


def test_apl_537_supported_question_cites_exact_results_and_hidden_selector_abstains(
    live, assistance_grants, ratio_sources
):
    _, programme, period, results = ratio_sources
    body = {
        "question": "What result value and coverage complete status are recorded?",
        "programme_id": programme["object_id"],
        "programme_revision_id": programme["revision_id"],
        "period_id": period["object_id"],
        "period_revision_id": period["revision_id"],
        "source_mode": "SELECTED_GOVERNED_RESULTS",
        "sources": [{"object_id": item["object_id"], "revision_id": item["revision_id"]} for item in results],
        "policy_version": live.policy_version,
        "language": "en",
    }
    denied = _post(live, "evidence-questions", body, actor="partner", status=404)
    assert denied["code"] == "RESOURCE_UNAVAILABLE"

    hidden = _post(
        live,
        "evidence-questions",
        {**body, "sources": [{"object_id": str(uuid4()), "revision_id": str(uuid4())}]},
    )
    assert hidden["state"] == "ABSTAINED"
    assert hidden["protected_resource_confirmed"] is False
    assert hidden["claims"] == hidden["citations"] == []

    answered = _post(live, "evidence-questions", body)
    assert answered["state"] == "ANSWERED"
    assert answered["claims"] and answered["citations"]
    assert all(claim["citation_numbers"] for claim in answered["claims"])
    assert {citation["revision_id"] for citation in answered["citations"]} == {
        item["revision_id"] for item in results
    }
    assert answered["official_number_guessed"] is False
    assert answered["fabricated_citations"] is False


def test_apl_538_typed_pooling_refuses_mismatched_claim_then_recovers_without_writes(
    live, assistance_grants, ratio_sources
):
    _, _, period, results = ratio_sources
    plan = {
        "measure": "POOLED_PERCENTAGE",
        "sources": [{"object_id": item["object_id"], "revision_id": item["revision_id"]} for item in results],
        "filters": {},
        "period_id": period["object_id"],
        "period_revision_id": period["revision_id"],
        "dimensions": [],
        "source_mode": "PROVISIONAL",
        "permitted_operation": "POOL_RATIO",
    }
    body = {
        "question": "Pool the approved ratio components.",
        "plan": plan,
        "drafted_claim": "99.99 percent (invented)",
        "policy_version": live.policy_version,
        "language": "en",
    }
    denied = _post(live, "numeric-analysis", body, actor="revoked", status=404)
    assert denied["code"] == "RESOURCE_UNAVAILABLE"

    with live.db() as connection:
        before = connection.execute(
            "SELECT count(*) AS revisions FROM impact.object_revision WHERE tenant_id=%s",
            (live.fixture["tenant_a"],),
        ).fetchone()["revisions"]
    mismatch = _post(live, "numeric-analysis", body, status=422)
    assert mismatch["reason_code"] == "AI_NUMERIC_CLAIM_MISMATCH"
    with live.db() as connection:
        after = connection.execute(
            "SELECT count(*) AS revisions FROM impact.object_revision WHERE tenant_id=%s",
            (live.fixture["tenant_a"],),
        ).fetchone()["revisions"]
    assert after == before

    result = _post(live, "numeric-analysis", {**body, "drafted_claim": None})
    assert result["state"] == "ANSWERED"
    assert result["model_recomputed"] is False
    assert result["arbitrary_query_executed"] is False
    assert result["official_claim_matches_tool"] is True
    assert result["calculation_receipt"] == {
        **result["calculation_receipt"],
        "tool": "governed.pool_ratio.v1",
        "precision_digits": 100,
        "rounding_rule": "HALF_UP",
        "operation": "POOL_RATIO",
    }
    assert result["answer"] == f"{result['value']} percent ({result['numerator']}/{result['denominator']})"


def test_apl_597_source_bound_suggestions_refuse_fabrication_and_recover(
    live, governed_ai_grants, component_services
):
    """APL-597 external HTTP: traceable views, individual review and atomic output refusal."""

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
        "policy_version": live.policy_version,
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
    """APL-601 external HTTP: a suggestion can be dismissed without mutating its sources."""

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
                "policy_version": live.policy_version,
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
    """APL-541 external HTTP: inspectable proposal, protected refusal and authority recheck."""

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
        "policy_version": live.policy_version,
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
    assert protected.value.status == 422 and protected.value.code == "VALIDATION_FAILED"
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
    assert proposal["command_type"] == "CREATE_WORK_ITEM_DRAFT"
    assert proposal["scope_object_id"] == programme["object_id"]
    assert proposal["before_values"] is None and proposal["after_values"] == request["after_values"]
    assert proposal["affected_versions"] == request["affected_versions"]
    assert (
        proposal["policy_version"] == live.policy_version
        and proposal["consequences"] == request["consequences"]
    )
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


def test_policy_save_exact_retry_survives_runtime_rollback_and_does_not_leak_activation(live):
    from test_story_error_recovery_analytics_live import _durable_counts

    path = live.path("ai-enablement/policy")
    current = expect(live.request(path, actor="admin"), 200)
    body = {
        "operation_id": str(uuid4()),
        "expected_version": current["policy_version"],
        "data": {"use_cases": rules()},
    }
    saved = expect(live.request(path, actor="admin", method="PUT", body=body), 200)
    before = _durable_counts(live)
    assert expect(live.default_runtime.request(path, actor="admin", method="PUT", body=body), 200) == saved
    changed = {**body, "data": {"use_cases": []}}
    expect(live.default_runtime.request(path, actor="admin", method="PUT", body=changed), 409)
    fresh = {**body, "operation_id": str(uuid4()), "expected_version": saved["policy_version"]}
    refused = expect(live.default_runtime.request(path, actor="admin", method="PUT", body=fresh), 422)
    assert refused["reason_code"] == "AI_USE_CASE_RESERVED"
    assert _durable_counts(live) == before
    # Both a reviewed process and the default process must authorize before exposing activation.
    for client in (live, live.default_runtime):
        for use_case in ("INDICATOR_DESIGN", "IMPORT_CLEANING"):
            rule = next(row for row in rules() if row["use_case"] == use_case)
            response = client.request(
                path,
                actor="partner",
                method="PUT",
                body={**fresh, "operation_id": str(uuid4()), "data": {"use_cases": [rule]}},
            )
            assert response.status_code in {403, 404}
            assert response.json().get("reason_code") != "AI_USE_CASE_RESERVED"
