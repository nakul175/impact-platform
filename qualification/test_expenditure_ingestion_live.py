"""APL-650 / FR-FIN-003 live expenditure reconciliation and correction journey."""

from uuid import uuid4

from test_forms import temporary_grants
from test_live_application import expect


def _post(live, data):
    return expect(
        live.request(
            live.path("expenditure-imports"),
            method="POST",
            body={"operation_id": str(uuid4()), "data": data},
        ),
        201,
    )


def _transaction(key, amount, semantic, category_id, funding_id):
    return {
        "source_transaction_key": key,
        "posting_date": "2026-08-18",
        "event_date": "2026-08-15",
        "amount": amount,
        "currency": "USD",
        "category_id": category_id,
        "funding_allocation_id": funding_id,
        "adjustment_semantic": semantic,
    }


def _batch(digest, total, transactions):
    return {
        "source_system": "SYNTHETIC_LEDGER",
        "file_sha256": digest,
        "control_total": total,
        "permitted_exception": None,
        "transactions": transactions,
    }


def _rows(live, key):
    with live.db() as connection:
        return connection.execute(
            "SELECT r.object_id::text,r.lifecycle_state,v.revision_id::text,v.payload "
            "FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_type='ExpenditureTransaction' "
            "AND v.payload->>'source_transaction_key'=%s ORDER BY v.created_at,v.revision_id",
            (live.fixture["tenant_a"], key),
        ).fetchall()


def test_repeated_and_amended_expenditure_preserves_exact_correction_semantics(live):
    revoke = temporary_grants(live, "author", ["finance-transactions.draft.create"])
    try:
        _repeated_and_amended_expenditure(live)
    finally:
        revoke()


def _repeated_and_amended_expenditure(live):
    key = "EXP-2026-0001"
    category_id, funding_id = str(uuid4()), str(uuid4())
    original_data = _batch(
        "1" * 64,
        "60.10",
        [_transaction(key, "60.10", "ORIGINAL", category_id, funding_id)],
    )
    original = _post(live, original_data)
    repeated = _post(live, original_data)
    assert repeated["object_id"] == original["object_id"]
    assert repeated["revision_id"] == original["revision_id"]
    assert repeated["business_state"] == "Reconciled"
    assert repeated["repeated_file"] is True
    rows = _rows(live, key)
    assert len(rows) == 1
    assert rows[0]["payload"]["amount"] == "60.10"
    original_revision = rows[0]["revision_id"]

    reversal = _post(
        live,
        _batch(
            "2" * 64,
            "-60.10",
            [_transaction(key, "-60.10", "REVERSAL", category_id, funding_id)],
        ),
    )
    reversal_row = _rows(live, key)[-1]
    assert reversal_row["lifecycle_state"] == "REVERSAL"
    assert reversal_row["payload"]["amount"] == "-60.10"
    assert reversal_row["payload"]["supersedes_revision"] == original_revision
    assert reversal["business_state"] == "Reconciled"

    replacement = _post(
        live,
        _batch(
            "3" * 64,
            "55.25",
            [_transaction(key, "55.25", "REPLACEMENT", category_id, funding_id)],
        ),
    )
    replacement_row = _rows(live, key)[-1]
    assert replacement_row["lifecycle_state"] == "REPLACEMENT"
    assert replacement_row["payload"]["amount"] == "55.25"
    assert replacement_row["payload"]["supersedes_revision"] == reversal_row["revision_id"]
    assert replacement["business_state"] == "Reconciled"
    assert len(_rows(live, key)) == 3

    repeat_replacement = _post(
        live,
        _batch(
            "3" * 64,
            "55.25",
            [_transaction(key, "55.25", "REPLACEMENT", category_id, funding_id)],
        ),
    )
    assert repeat_replacement["object_id"] == replacement["object_id"]
    assert repeat_replacement["revision_id"] == replacement["revision_id"]
    assert len(_rows(live, key)) == 3


def test_unbalanced_expenditure_is_refused_without_an_explicit_exception(live):
    revoke = temporary_grants(live, "author", ["finance-transactions.draft.create"])
    try:
        category_id, funding_id = str(uuid4()), str(uuid4())
        refused = expect(
            live.request(
                live.path("expenditure-imports"),
                method="POST",
                body={
                    "operation_id": str(uuid4()),
                    "data": _batch(
                        "4" * 64,
                        "100.00",
                        [_transaction("EXP-UNBALANCED", "99.99", "ORIGINAL", category_id, funding_id)],
                    ),
                },
            ),
            409,
        )
        assert refused["code"] == "CONTROL_TOTAL_UNBALANCED"
    finally:
        revoke()
