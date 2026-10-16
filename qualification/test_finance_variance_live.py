"""APL-652 / FR-FIN-005 live actual-versus-forecast variance journey."""

from uuid import uuid4

from test_forms import temporary_grants
from test_live_application import expect


def _post(live, route, data, actor="author"):
    return expect(
        live.request(
            live.path(route),
            actor=actor,
            method="POST",
            body={"operation_id": str(uuid4()), "data": data},
        ),
        201,
    )


def _stored(live, object_id):
    with live.db() as connection:
        return connection.execute(
            "SELECT r.lifecycle_state,v.revision_id::text,v.payload "
            "FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_id=%s",
            (live.fixture["tenant_a"], object_id),
        ).fetchone()


def _approved_budget(live):
    created = _post(
        live,
        "budgets",
        {
            "title": "Synthetic variance budget",
            "approval_route": [live.fixture["actors"]["reviewer"]["principal_id"]],
            "rate_assumptions": [{"pair": "USD/USD", "rate": "1.0000"}],
            "lines": [
                {
                    "activity_id": str(uuid4()),
                    "category_id": str(uuid4()),
                    "partner_id": str(uuid4()),
                    "period_id": live.records["period"]["object_id"],
                    "currency": "USD",
                    "amount": "100.00",
                }
            ],
        },
    )
    approved = _post(
        live,
        "budget-approvals",
        {"budget_id": created["object_id"], "expected_revision": created["revision_id"]},
        actor="reviewer",
    )
    return created["object_id"], approved["revision_id"]


def _actual(live):
    imported = _post(
        live,
        "expenditure-imports",
        {
            "source_system": "SYNTHETIC_LEDGER",
            "file_sha256": "5" * 64,
            "control_total": "60.00",
            "permitted_exception": None,
            "transactions": [
                {
                    "source_transaction_key": "ACTUAL-60",
                    "posting_date": "2026-08-18",
                    "event_date": "2026-08-15",
                    "amount": "60.00",
                    "currency": "USD",
                    "category_id": str(uuid4()),
                    "funding_allocation_id": str(uuid4()),
                    "adjustment_semantic": "ORIGINAL",
                }
            ],
        },
    )
    batch = _stored(live, imported["object_id"])
    transaction_id = batch["payload"]["imported_transaction_ids"][0]
    transaction = _stored(live, transaction_id)
    return transaction_id, transaction["revision_id"]


def _variance_data(live, budget_id, budget_revision, actuals, state):
    return {
        "budget_id": budget_id,
        "budget_revision": budget_revision,
        "actual_cutoff": "2026-08-31",
        "actual_data_state": state,
        "actual_transactions": actuals,
        "commitments": "20.00",
        "forecast_total": "110.00",
        "forecast_method": "Reviewed run-rate forecast",
        "forecast_method_version": "2026.1",
        "forecast_assumptions": ["Known commitments remain payable"],
        "author_id": live.fixture["actors"]["author"]["principal_id"],
    }


def test_variance_separates_current_unspent_budget_from_forecast_overrun(live):
    author_revoke = temporary_grants(
        live,
        "author",
        [
            "budget-lines.draft.create",
            "finance-transactions.draft.create",
            "finance-transactions.read",
        ],
    )
    reviewer_revoke = temporary_grants(live, "reviewer", ["budget-lines.draft.edit"])
    try:
        _complete_variance(live)
    finally:
        reviewer_revoke()
        author_revoke()


def _complete_variance(live):
    budget_id, budget_revision = _approved_budget(live)
    transaction_id, transaction_revision = _actual(live)
    saved = _post(
        live,
        "finance-variance-views",
        _variance_data(
            live,
            budget_id,
            budget_revision,
            [{"object_id": transaction_id, "revision_id": transaction_revision}],
            "COMPLETE",
        ),
    )
    view = _stored(live, saved["object_id"])
    assert view["revision_id"] == saved["revision_id"]
    assert view["payload"]["budget_revision"] == budget_revision
    assert view["payload"]["actual_transactions"] == [
        {"object_id": transaction_id, "revision_id": transaction_revision}
    ]
    assert view["payload"]["budget_total"] == "100.00"
    assert view["payload"]["actual_total"] == "60.00"
    assert view["payload"]["remaining_budget"] == "40.00"
    assert view["payload"]["remaining_sign_convention"] == "POSITIVE_MEANS_UNSPENT"
    assert view["payload"]["forecast_overrun"] == "10.00"
    assert view["payload"]["forecast"] == {
        "total": "110.00",
        "commitments": "20.00",
        "method": "Reviewed run-rate forecast",
        "method_version": "2026.1",
        "assumptions": ["Known commitments remain payable"],
    }
    assert view["payload"]["actual_series_includes_forecast"] is False
    assert view["payload"]["impact_success_inference"] == "PROHIBITED"


def test_missing_actual_data_never_becomes_apparent_underspend(live):
    author_revoke = temporary_grants(
        live,
        "author",
        ["budget-lines.draft.create", "finance-transactions.read"],
    )
    reviewer_revoke = temporary_grants(live, "reviewer", ["budget-lines.draft.edit"])
    try:
        budget_id, budget_revision = _approved_budget(live)
        saved = _post(
            live,
            "finance-variance-views",
            _variance_data(live, budget_id, budget_revision, [], "MISSING"),
        )
        payload = _stored(live, saved["object_id"])["payload"]
        assert payload["actual_data_state"] == "MISSING"
        assert payload["actual_total"] is None
        assert payload["remaining_budget"] is None
        assert payload["forecast_overrun"] == "10.00"
        assert payload["actual_series_includes_forecast"] is False
    finally:
        reviewer_revoke()
        author_revoke()
