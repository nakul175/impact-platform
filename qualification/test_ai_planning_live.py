"""API/database security checks for unapproved planning drafts and saved source inputs.

These use the provisioned live harness. A PGlite pass is not native/concurrency or
hosted acceptance evidence. All input facts, supplier offers and task text are synthetic.
"""

from contextlib import contextmanager
from copy import deepcopy
import json
from uuid import uuid4

import pytest
from starlette.requests import Request

from impact_api.ai_enablement import AIEnablement
from impact_api.ai_task_practice import CONTENT_VERSION as PRACTICE_VERSION
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.contracts import validate
from impact_api.service import Service
from impact_api.store import Database
from test_ai_adoption_plans import plan
from test_ai_adoption_plans_live import management_disabled
from test_ai_planning_inputs import cost_inputs, pilot_inputs, planning_plan
from test_live_application import cmd, expect

PLANNING_ROUTES = [
    pytest.param("cost-comparison", "POST", cost_inputs, "AICostComparisonResult", id="cost-comparison"),
    pytest.param("pilot-evaluation", "POST", pilot_inputs, "AIPilotEvaluationResult", id="pilot-evaluation"),
    pytest.param("task-templates", "GET", lambda: None, "AITaskPracticeTemplates", id="task-templates"),
]


def domain_counts(live):
    """Denied reads may add a separate security-denial row, never domain/audit/provider work."""
    tenant = live.fixture["tenant_a"]
    tables = [
        "object_registry",
        "object_revision",
        "audit_event_current",
        "outbox_event",
        "operation_receipt",
        "ai_advisory_request",
        "ai_advisory_result",
    ]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return {
            table: c.execute(
                "SELECT count(*) AS n FROM impact." + table + " WHERE tenant_id=%s", (tenant,)
            ).fetchone()["n"]
            for table in tables
        }


@contextmanager
def read_disabled(live, actor):
    """Narrow only existing synthetic grants; do not manufacture authority or identities."""
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"][actor]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grants = c.execute(
            "SELECT object_id,purpose FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s "
            "AND capability='ai.enablement.read' AND purpose IS NULL",
            (tenant, principal),
        ).fetchall()
        assert grants, "The fixture actor must begin with an actual read grant"
        c.execute(
            "UPDATE impact.grant_current SET purpose='QUALIFICATION' WHERE tenant_id=%s "
            "AND object_id=ANY(%s::uuid[])",
            (tenant, [str(grant["object_id"]) for grant in grants]),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            for grant in grants:
                c.execute(
                    "UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s",
                    (grant["purpose"], tenant, grant["object_id"]),
                )


def checked_tool(live, route, method, body, schema, actor="author"):
    before = domain_counts(live)
    result = expect(
        live.request(live.path("ai-enablement/" + route), actor=actor, method=method, body=body), 200
    )
    validate(schema, result)
    assert domain_counts(live) == before, "An unapproved planning read must not persist or queue anything"
    return result


def test_cost_api_preserves_unknown_exit_cost_even_with_zero_quantity_and_does_not_pick_a_winner(live):
    result = checked_tool(live, "cost-comparison", "POST", cost_inputs(), "AICostComparisonResult")
    assert result["currency"] == "INR" and result["period_months"] == 12
    assert result["status"] == "INCOMPLETE" and result["cheapest_offer_ids"] == []
    assert result["offers"] == [
        {
            "id": "synthetic-a",
            "name": "Synthetic supplied offer A",
            "known_subtotal": "0.12",
            "complete_total": None,
            "missing_line_ids": ["exit"],
        }
    ]
    assert "unknown, not zero" in result["disclaimer"]
    assert not {"approved", "supplier_verified", "award", "official_result"}.intersection(result)


def test_cost_api_uses_exact_decimal_products_and_preserves_equal_total_ties(live):
    body = cost_inputs()
    body["offers"][0]["lines"][1].update(quantity="1", unit_amount="40")
    other = deepcopy(body["offers"][0])
    other.update(id="synthetic-b", name="Synthetic supplied offer B")
    body["offers"].append(other)
    result = checked_tool(live, "cost-comparison", "POST", body, "AICostComparisonResult")
    assert result["status"] == "COMPLETE"
    assert [offer["complete_total"] for offer in result["offers"]] == ["40.12", "40.12"]
    assert result["cheapest_offer_ids"] == ["synthetic-a", "synthetic-b"]
    assert all(offer["missing_line_ids"] == [] for offer in result["offers"])


@pytest.mark.parametrize(
    "comparison,baseline_minutes,pilot_review,expected",
    [
        pytest.param(
            True,
            "100",
            "40",
            {"status": "DEFINED", "percent": "50", "reason": "COMPARABLE_SAMPLES"},
            id="normalized-review-time",
        ),
        pytest.param(
            True,
            "0",
            "40",
            {"status": "UNDEFINED", "percent": None, "reason": "ZERO_BASELINE"},
            id="zero-baseline",
        ),
        pytest.param(
            False,
            "100",
            "40",
            {"status": "UNDEFINED", "percent": None, "reason": "SAMPLES_NOT_COMPARABLE"},
            id="incomparable",
        ),
        pytest.param(
            True,
            "100",
            "400",
            {"status": "DEFINED", "percent": "-100", "reason": "COMPARABLE_SAMPLES"},
            id="review-effort-worsens-time",
        ),
    ],
)
def test_pilot_api_retains_source_counts_and_marks_comparability_without_official_outcomes(
    live, comparison, baseline_minutes, pilot_review, expected
):
    body = pilot_inputs()
    body["comparable"] = comparison
    body["baseline"]["total_drafting_minutes"] = baseline_minutes
    if baseline_minutes == "0":
        body["baseline"]["total_review_minutes"] = "0"
    body["pilot"]["total_review_minutes"] = pilot_review
    result = checked_tool(live, "pilot-evaluation", "POST", body, "AIPilotEvaluationResult")
    assert result["status"] == "SELF_REPORTED_DRAFT"
    assert result["improvement"] == expected
    assert result["source"] == {"baseline": body["baseline"], "pilot": body["pilot"]}
    assert result["comparable"] is comparison
    assert result["notes"] == body["notes"]
    assert result["baseline"]["factual_corrections_per_item"] == "0.2"
    assert result["pilot"]["factual_corrections_per_item"] == "0.2"
    assert not {"approved", "quality_score", "roi", "official_result", "certified"}.intersection(result)


def test_task_templates_api_returns_four_versioned_manual_exercises_without_execution_or_approval(live):
    result = checked_tool(live, "task-templates", "GET", None, "AITaskPracticeTemplates")
    assert result["content_version"] == PRACTICE_VERSION
    assert [template["id"] for template in result["templates"]] == [
        "invitation",
        "grant_summary",
        "meeting_actions",
        "supplier_questions",
    ]
    assert "not an AI-generated result" in result["disclaimer"]
    for template in result["templates"]:
        assert template["example_brief"].startswith("Synthetic exercise:")
        assert template["allowed_inputs"] and template["prohibited_inputs"]
        assert len(template["review_steps"]) == 5
        assert not {"approved", "generated_output", "certificate", "operation_id"}.intersection(template)


@pytest.mark.parametrize("route,method,factory,schema", PLANNING_ROUTES)
@pytest.mark.parametrize(
    "actor,status",
    [
        pytest.param("other_tenant", 404, id="other-tenant"),
        pytest.param("revoked", 404, id="revoked-member"),
        pytest.param(None, 401, id="unsigned"),
        pytest.param("partner", 404, id="no-read-capability"),
    ],
)
def test_planning_routes_deny_tenant_selector_revoked_missing_identity_and_missing_capability(
    live, route, method, factory, schema, actor, status
):
    before = domain_counts(live)
    denied = expect(
        live.request(live.path("ai-enablement/" + route), actor=actor, method=method, body=factory()), status
    )
    validate("Error", denied)
    assert domain_counts(live) == before


@pytest.mark.parametrize("route,method,factory,schema", PLANNING_ROUTES)
def test_planning_tools_recheck_current_read_authority_for_every_request(
    live, route, method, factory, schema
):
    checked_tool(live, route, method, factory(), schema, actor="reviewer")
    before = domain_counts(live)
    with read_disabled(live, "reviewer"):
        expect(
            live.request(
                live.path("ai-enablement/" + route), actor="reviewer", method=method, body=factory()
            ),
            404,
        )
    assert domain_counts(live) == before
    checked_tool(live, route, method, factory(), schema, actor="reviewer")


def test_read_only_actor_can_compute_and_practise_but_cannot_save_or_update_inputs(live):
    path = live.path("ai-enablement/plans")
    created = expect(live.request(path, actor="admin", method="POST", body=cmd(planning_plan())), 201)
    before = domain_counts(live)
    with management_disabled(live, "reviewer"):
        for route, method, body, schema in [
            ("cost-comparison", "POST", cost_inputs(), "AICostComparisonResult"),
            ("pilot-evaluation", "POST", pilot_inputs(), "AIPilotEvaluationResult"),
            ("task-templates", "GET", None, "AITaskPracticeTemplates"),
        ]:
            checked_tool(live, route, method, body, schema, actor="reviewer")
        saved = expect(live.request(path + "/" + created["object_id"], actor="reviewer"), 200)
        assert saved["data"]["planning"] == planning_plan()["planning"]
        expect(live.request(path, actor="reviewer", method="POST", body=cmd(planning_plan())), 404)
        expect(
            live.request(
                path + "/" + created["object_id"],
                actor="reviewer",
                method="PUT",
                body=cmd(planning_plan(), created["revision_id"]),
            ),
            404,
        )
    assert domain_counts(live) == before


@pytest.mark.parametrize(
    "route,factory,edit",
    [
        pytest.param(
            "cost-comparison", cost_inputs, lambda b: b.update(approved=True), id="cost-unknown-root"
        ),
        pytest.param(
            "cost-comparison",
            cost_inputs,
            lambda b: b["offers"][0].update(currency="USD"),
            id="unlike-offer-currency",
        ),
        pytest.param(
            "cost-comparison",
            cost_inputs,
            lambda b: b["offers"][0]["lines"][0].update(unit_amount=0.004),
            id="float-money",
        ),
        pytest.param(
            "cost-comparison", cost_inputs, lambda b: b.update(period_months=True), id="bool-months"
        ),
        pytest.param(
            "cost-comparison",
            cost_inputs,
            lambda b: b["offers"][0]["lines"][0].update(quantity="1e2"),
            id="exponent-money",
        ),
        pytest.param(
            "cost-comparison", cost_inputs, lambda b: b["offers"][0].update(name=" "), id="empty-offer-name"
        ),
        pytest.param(
            "pilot-evaluation",
            pilot_inputs,
            lambda b: b.update(official_result="50"),
            id="pilot-result-forgery",
        ),
        pytest.param(
            "pilot-evaluation",
            pilot_inputs,
            lambda b: b["baseline"].update(approved=True),
            id="sample-unknown-key",
        ),
        pytest.param(
            "pilot-evaluation",
            pilot_inputs,
            lambda b: b["pilot"].update(sample_size=True),
            id="bool-sample-size",
        ),
        pytest.param(
            "pilot-evaluation",
            pilot_inputs,
            lambda b: b["pilot"].update(total_review_minutes=-1),
            id="negative-numeric-time",
        ),
        pytest.param(
            "pilot-evaluation", pilot_inputs, lambda b: b.update(comparable="true"), id="string-comparability"
        ),
        pytest.param(
            "pilot-evaluation", pilot_inputs, lambda b: b.update(task_label=" "), id="empty-task-label"
        ),
    ],
)
def test_closed_api_inputs_reject_forged_decisions_types_and_unsupported_fields_without_work(
    live, route, factory, edit
):
    body = factory()
    edit(body)
    before = domain_counts(live)
    denied = expect(live.request(live.path("ai-enablement/" + route), method="POST", body=body), 422)
    assert denied["code"] == "VALIDATION_FAILED"
    assert domain_counts(live) == before


@pytest.mark.parametrize(
    "route,raw",
    [
        pytest.param(
            "cost-comparison",
            json.dumps(cost_inputs()).replace('"currency": "INR"', '"currency": "INR", "currency": "USD"'),
            id="duplicate-currency",
        ),
        pytest.param(
            "cost-comparison",
            json.dumps(cost_inputs()).replace(
                '"unit_amount": "0.004"', '"unit_amount": "0.004", "unit_amount": "0"'
            ),
            id="duplicate-nested-amount",
        ),
        pytest.param(
            "pilot-evaluation",
            json.dumps(pilot_inputs()).replace(
                '"total_review_minutes": "40"', '"total_review_minutes": "40", "total_review_minutes": "0"'
            ),
            id="duplicate-nested-review",
        ),
    ],
)
def test_duplicate_json_keys_are_refused_before_planning_or_persistence(live, route, raw):
    before = domain_counts(live)
    expect(
        live.request(
            live.path("ai-enablement/" + route),
            method="POST",
            headers={"Content-Type": "application/json"},
            content=raw,
        ),
        400,
    )
    assert domain_counts(live) == before


def test_authorized_planning_never_inspects_or_calls_an_enabled_provider(live):
    settings = Settings(**live.config)
    db = Database(settings)
    identity = Auth(settings, db).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token("admin")).encode())],
            }
        )
    )

    class ForbiddenProvider:
        @property
        def configured(self):
            raise AssertionError("Deterministic planning must not inspect provider availability")

        def generate(self, *args, **kwargs):
            raise AssertionError("Deterministic planning must not make any provider request")

    api = AIEnablement(Service(settings, db), ForbiddenProvider(), enabled=True)
    before = domain_counts(live)
    tenant = live.fixture["tenant_a"]
    assert api.cost_comparison(identity, tenant, cost_inputs())["status"] == "INCOMPLETE"
    assert api.pilot_evaluation(identity, tenant, pilot_inputs())["status"] == "SELF_REPORTED_DRAFT"
    assert len(api.task_templates(identity, tenant)["templates"]) == 4
    assert domain_counts(live) == before


def test_planning_snapshot_save_reload_exact_retry_changed_input_and_stale_edit_are_atomic(live):
    path = live.path("ai-enablement/plans")
    body = cmd(planning_plan())
    first = expect(live.request(path, actor="admin", method="POST", body=body), 201)
    validate("AIAdoptionPlanReceipt", first)
    assert expect(live.request(path, actor="admin", method="POST", body=body), 201) == first
    current = expect(live.request(path + "/" + first["object_id"], actor="reviewer"), 200)
    validate("AIAdoptionPlan", current)
    assert current["business_state"] == "Draft"
    assert current["data"]["planning"] == body["data"]["planning"]
    assert current["data"]["content_versions"]["practice"] == PRACTICE_VERSION
    assert current["data"]["learning_completed"] == ["foundations:safe-practice-task"]
    changed = deepcopy(body)
    changed["data"]["planning"]["cost_comparison"]["offers"][0]["lines"][0]["unit_amount"] = "0.0040"
    denied = expect(live.request(path, actor="admin", method="POST", body=changed), 409)
    assert denied["code"] == "CONFLICT_OPERATION"
    next_data = deepcopy(body["data"])
    next_data["planning"]["cost_comparison"]["offers"][0]["lines"][1].update(quantity="1", unit_amount="40")
    next_data["planning"]["task_practice"]["checked_steps"].append("missing_information")
    update = cmd(next_data, first["revision_id"])
    second = expect(
        live.request(path + "/" + first["object_id"], actor="admin", method="PUT", body=update), 200
    )
    assert (
        expect(live.request(path + "/" + first["object_id"], actor="admin", method="PUT", body=update), 200)
        == second
    )
    stale = cmd(body["data"], first["revision_id"])
    denied = expect(
        live.request(path + "/" + first["object_id"], actor="admin", method="PUT", body=stale), 409
    )
    assert denied["code"] == "CONFLICT_VERSION"
    reread = expect(live.request(path + "/" + first["object_id"], actor="reviewer"), 200)
    assert reread["data"]["planning"] == next_data["planning"]
    before_replay = domain_counts(live)
    with management_disabled(live, "admin"):
        expect(live.request(path, actor="admin", method="POST", body=body), 404)
        expect(live.request(path + "/" + first["object_id"], actor="admin", method="PUT", body=update), 404)
    with read_disabled(live, "admin"):
        expect(live.request(path, actor="admin", method="POST", body=body), 404)
    assert domain_counts(live) == before_replay
    for actor in ["other_tenant", "revoked"]:
        expect(live.request(path + "/" + first["object_id"], actor=actor), 404)
        expect(live.request(path, actor=actor, method="POST", body=cmd(planning_plan())), 404)
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        rows = c.execute(
            "SELECT revision_id,payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s ORDER BY revision_number",
            (tenant, first["object_id"]),
        ).fetchall()
        assert len(rows) == 2
        assert rows[0]["payload"]["planning"] == body["data"]["planning"]
        assert rows[1]["payload"]["planning"] == next_data["planning"]
        assert str(rows[0]["revision_id"]) == first["revision_id"]
        assert str(rows[1]["revision_id"]) == second["revision_id"]
        assert (
            c.execute(
                "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                (tenant, first["object_id"]),
            ).fetchone()["head_revision"]
            == rows[1]["revision_id"]
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s AND action_type IN ('create_ai_adoption_plan','update_ai_adoption_plan')",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_id'=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=ANY(%s::uuid[])",
                (tenant, [body["operation_id"], update["operation_id"], stale["operation_id"]]),
            ).fetchone()["n"]
            == 2
        )


@pytest.mark.parametrize(
    "edit",
    [
        pytest.param(
            lambda p: p["planning"].update(content_versions={"practice": "forged"}),
            id="planning-version-forgery",
        ),
        pytest.param(
            lambda p: p["planning"]["cost_comparison"]["offers"][0]["lines"][0].update(approved=True),
            id="line-decision-forgery",
        ),
        pytest.param(
            lambda p: p["planning"]["pilot_evaluation"]["baseline"].update(official_result="1"),
            id="sample-result-forgery",
        ),
        pytest.param(
            lambda p: p["planning"]["task_practice"].update(approved_by=str(uuid4())),
            id="task-approver-forgery",
        ),
        pytest.param(
            lambda p: p["planning"]["task_practice"].update(template_id="unavailable"),
            id="unknown-practice-id",
        ),
        pytest.param(
            lambda p: p["planning"]["task_practice"].update(checked_steps=["claim_scope"]),
            id="another-template-check",
        ),
    ],
)
def test_invalid_saved_planning_inputs_leave_no_head_revision_audit_outbox_or_receipt(live, edit):
    data = planning_plan()
    edit(data)
    before = domain_counts(live)
    denied = expect(
        live.request(live.path("ai-enablement/plans"), actor="admin", method="POST", body=cmd(data)), 422
    )
    assert denied["code"] == "VALIDATION_FAILED"
    assert domain_counts(live) == before


def test_duplicate_nested_json_key_in_a_saved_planning_input_is_not_silently_overwritten(live):
    body = cmd(planning_plan())
    raw = json.dumps(body).replace(
        '"template_id": "invitation"', '"template_id": "invitation", "template_id": "grant_summary"'
    )
    before = domain_counts(live)
    expect(
        live.request(
            live.path("ai-enablement/plans"),
            actor="admin",
            method="POST",
            headers={"Content-Type": "application/json"},
            content=raw,
        ),
        400,
    )
    assert domain_counts(live) == before


def test_original_six_field_plan_stays_readable_without_backfilled_planning_input(live):
    path = live.path("ai-enablement/plans")
    saved = expect(live.request(path, actor="admin", method="POST", body=cmd(plan())), 201)
    before = domain_counts(live)
    current = expect(live.request(path + "/" + saved["object_id"], actor="reviewer"), 200)
    validate("AIAdoptionPlan", current)
    assert "planning" not in current["data"]
    assert set(current["data"]["content_versions"]) == {"catalog", "solutions"}
    assert current["data"]["learning_completed"] == ["foundations:safe-practice-task"]
    assert domain_counts(live) == before


def test_older_six_field_update_preserves_planning_and_explicit_nulls_clear_only_the_new_revision(live):
    """An older client cannot erase unknown inputs; a deliberate clearing command can."""
    path = live.path("ai-enablement/plans")
    create = cmd(planning_plan())
    first = expect(live.request(path, actor="admin", method="POST", body=create), 201)
    item_path = path + "/" + first["object_id"]
    original = expect(live.request(item_path, actor="reviewer"), 200)
    validate("AIAdoptionPlan", original)
    original_planning = deepcopy(original["data"]["planning"])
    original_practice_version = original["data"]["content_versions"]["practice"]

    legacy_data = {**plan(), "title": "Synthetic title changed by an older six-field client"}
    assert len(legacy_data) == 6 and "planning" not in legacy_data
    legacy_update = cmd(legacy_data, first["revision_id"])
    second = expect(live.request(item_path, actor="admin", method="PUT", body=legacy_update), 200)
    retained = expect(live.request(item_path, actor="reviewer"), 200)
    validate("AIAdoptionPlan", retained)
    assert retained["data"]["title"] == legacy_data["title"]
    assert retained["data"]["planning"] == original_planning
    assert retained["data"]["content_versions"]["practice"] == original_practice_version
    before_retry = domain_counts(live)
    assert expect(live.request(item_path, actor="admin", method="PUT", body=legacy_update), 200) == second
    assert domain_counts(live) == before_retry

    clear_data = {
        **legacy_data,
        "planning": {"cost_comparison": None, "pilot_evaluation": None, "task_practice": None},
    }
    clear_update = cmd(clear_data, second["revision_id"])
    third = expect(live.request(item_path, actor="admin", method="PUT", body=clear_update), 200)
    cleared = expect(live.request(item_path, actor="reviewer"), 200)
    validate("AIAdoptionPlan", cleared)
    assert cleared["revision_id"] == third["revision_id"]
    assert cleared["data"]["planning"] == clear_data["planning"]
    assert "practice" not in cleared["data"]["content_versions"]
    assert cleared["business_state"] == "Draft"
    before_final_retries = domain_counts(live)
    assert expect(live.request(item_path, actor="admin", method="PUT", body=clear_update), 200) == third
    # Replaying an older update returns its receipt, never resurrecting the former inputs/head.
    assert expect(live.request(item_path, actor="admin", method="PUT", body=legacy_update), 200) == second
    assert domain_counts(live) == before_final_retries
    assert expect(live.request(item_path, actor="reviewer"), 200) == cleared

    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        revisions = c.execute(
            "SELECT revision_id,payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
            "ORDER BY revision_number",
            (tenant, first["object_id"]),
        ).fetchall()
        assert [str(row["revision_id"]) for row in revisions] == [
            first["revision_id"],
            second["revision_id"],
            third["revision_id"],
        ]
        assert revisions[0]["payload"] == original["data"]
        assert revisions[1]["payload"] == retained["data"]
        assert revisions[2]["payload"] == cleared["data"]
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s "
                "AND action_type IN ('create_ai_adoption_plan','update_ai_adoption_plan')",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 3
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_id'=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 3
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s "
                "AND operation_id=ANY(%s::uuid[])",
                (
                    tenant,
                    [create["operation_id"], legacy_update["operation_id"], clear_update["operation_id"]],
                ),
            ).fetchone()["n"]
            == 3
        )
