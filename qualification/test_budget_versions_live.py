"""Positive user journey for FR-FIN-002 / APL-648 versioned budgets."""

from uuid import uuid4
from test_forms import temporary_grants
from test_live_application import expect


def post(live, route, data, actor="author"):
    return expect(
        live.request(
            live.path(route), actor=actor, method="POST", body={"operation_id": str(uuid4()), "data": data}
        ),
        201,
    )


def stored(live, obj):
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        return c.execute(
            "SELECT r.lifecycle_state,v.revision_id::text,v.predecessor_revision::text,v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
            (live.fixture["tenant_a"], obj),
        ).fetchone()


def line(amount, period):
    return {
        "activity_id": str(uuid4()),
        "category_id": str(uuid4()),
        "partner_id": str(uuid4()),
        "period_id": period,
        "currency": "USD",
        "amount": amount,
    }


def test_independent_reviewer_approves_exact_decimal_budget_revision(live):
    ra = temporary_grants(live, "author", ["budget-lines.draft.create", "budget-lines.draft.edit"])
    rr = temporary_grants(live, "reviewer", ["budget-lines.draft.edit"])
    try:
        period = live.records["period"]["object_id"]
        reviewer = live.fixture["actors"]["reviewer"]["principal_id"]
        created = post(
            live,
            "budgets",
            {
                "title": "Synthetic budget",
                "approval_route": [reviewer],
                "rate_assumptions": [{"pair": "USD/USD", "rate": "1.0000"}],
                "lines": [line("100.10", period), line("200.20", period)],
            },
        )
        revised = post(
            live,
            "budget-revisions",
            {
                "budget_id": created["object_id"],
                "expected_revision": created["revision_id"],
                "rate_assumptions": [{"pair": "USD/USD", "rate": "1.0000"}],
                "lines": [line("150.15", period), line("250.25", period)],
            },
        )
        draft = stored(live, created["object_id"])
        assert (
            draft["payload"]["total"] == "400.40"
            and draft["payload"]["original_baseline_revision"] == created["revision_id"]
        )
        approved = post(
            live,
            "budget-approvals",
            {"budget_id": created["object_id"], "expected_revision": revised["revision_id"]},
            actor="reviewer",
        )
        current = stored(live, created["object_id"])
        assert (
            current["revision_id"] == approved["revision_id"]
            and current["predecessor_revision"] == revised["revision_id"]
        )
        assert current["payload"]["approved_budget_revision"] == revised["revision_id"]
        assert current["payload"]["pinned_rate_assumptions"] == [{"pair": "USD/USD", "rate": "1.0000"}]
        assert (
            current["payload"]["actual_expenditure_relation"] == "INDEPENDENT_UNCHANGED"
            and current["payload"]["historical_variance_relation"] == "UNCHANGED"
        )
    finally:
        rr()
        ra()
