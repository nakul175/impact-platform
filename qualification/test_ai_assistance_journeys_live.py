"""Component-only journeys for the four reserved AI assistance candidates.

Production deliberately keeps these use cases reserved-disabled.  The fixture below replaces
only the in-process policy and safety gates.  Stored tenant policy and production activation
rules remain unchanged while the in-process HTTP contracts, authorization, revisions and transaction
boundaries are exercised. This is not whole-story external runtime qualification.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from impact_api.config import Settings
from impact_api.main import create_app

from impact_api import (
    ai_evidence_questions,
    ai_import_assistance,
    ai_indicator_design,
    ai_numeric_analysis,
)
from test_calculation_methods import build, observation_data
from test_forms import planned, temporary_grants
from test_import import HOUSEHOLDS, batch_data
from test_live_application import expect
from test_measurement import action, approve, create, get, submit


@pytest.fixture(autouse=True)
def isolated_reserved_assistance_gate(live, monkeypatch):
    """Enable only this test process; never alter persisted policy or runtime defaults."""

    synthetic_policy = {"version": 1, "use_cases": {}}
    modules = (
        ai_indicator_design,
        ai_import_assistance,
        ai_evidence_questions,
        ai_numeric_analysis,
    )
    monkeypatch.setattr(ai_indicator_design.ai_policy, "in_force", lambda *_: synthetic_policy)
    monkeypatch.setattr(ai_indicator_design.ai_policy, "require", lambda *_, **kwargs: None)
    for module in modules:
        monkeypatch.setattr(module, "require_available", lambda *_: None)
    monkeypatch.setattr(
        Settings,
        "load",
        classmethod(
            lambda cls: Settings(
                **{
                    **live.config,
                    "ai_reviewed_use_cases": "INDICATOR_DESIGN,IMPORT_CLEANING,EVIDENCE_QUESTION,NUMERIC_ANALYSIS",
                }
            )
        ),
    )
    with TestClient(create_app()) as client:
        live.assistance_component_client = client
        try:
            yield
        finally:
            del live.assistance_component_client


@pytest.fixture
def assistance_grants(live):
    revoke = temporary_grants(
        live,
        "author",
        [
            "ai.advisory.request",
            "indicator-definitions.draft.create",
            "indicator-definitions.read",
            "imports.read",
            "imports.draft.edit",
            "calculated-results.read",
            "programmes.read",
            "periods.read",
        ],
    )
    try:
        yield
    finally:
        revoke()


def _post(live, suffix, body, *, actor="author", status=200):
    return expect(
        live.assistance_component_client.request(
            method="POST",
            url=live.path("ai-enablement") + "/" + suffix,
            headers={"Authorization": "Bearer " + live.token(actor)},
            json=body,
        ),
        status,
    )


def _object_count(live, kind):
    with live.db() as connection:
        return connection.execute(
            "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s AND object_type=%s",
            (live.fixture["tenant_a"], kind),
        ).fetchone()["n"]


@pytest.fixture
def ratio_sources(live):
    definition, indicator, period, keys = build(
        live,
        scheme=None,
        measurement_type="PERCENTAGE",
        combination_rule="POOLED_RATIO",
        numerator_meaning="Households with safe water",
        denominator_meaning="Households visited",
        display_decimals=2,
        population="Households in the programme area",
    )
    first = create(
        live,
        "observations",
        observation_data(indicator, keys[0], "0", {}) | {"numerator": "50", "denominator": "100"},
    )
    approve(live, submit(live, "observations", first))
    receipt = action(
        live,
        "indicator-instances",
        indicator,
        "calculate",
        {"period_id": period["object_id"]},
    )
    result_one = get(live, "calculated-results", receipt["object_id"])
    second = create(
        live,
        "observations",
        observation_data(indicator, keys[1], "0", {}) | {"numerator": "1", "denominator": "10"},
    )
    approve(live, submit(live, "observations", second))
    receipt = action(
        live,
        "indicator-instances",
        get(live, "indicator-instances", indicator["object_id"]),
        "calculate",
        {"period_id": period["object_id"]},
    )
    result_two = get(live, "calculated-results", receipt["object_id"])
    programme = get(live, "programmes", indicator["data"]["programme_id"])
    return definition, programme, period, [result_one, result_two]


def test_apl_533_indicator_proposal_refusal_is_atomic_then_valid_draft_recovers(
    live, assistance_grants, ratio_sources
):
    definition, programme, _, _ = ratio_sources
    source = {
        "library_definition_id": definition["object_id"],
        "library_definition_revision_id": definition["revision_id"],
        "programme_id": programme["object_id"],
        "programme_revision_id": programme["revision_id"],
        "policy_version": 1,
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
        {"policy_version": 1, "language": "en"},
        actor="revoked",
        status=404,
    )
    assert denied["code"] == "RESOURCE_UNAVAILABLE"

    proposals = _post(live, suffix + "/proposals", {"policy_version": 1, "language": "en"})
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
            "policy_version": 1,
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
        "policy_version": 1,
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
        "policy_version": 1,
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
        "policy_version": 1,
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
