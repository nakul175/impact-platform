"""Bounded listing filters dependent 404s without leaking candidate cursor positions."""

from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest

import impact_api.service as module
from impact_api.domain import DomainError
from impact_api.service import LIST_SCAN_BUDGET, Service


class Rows:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


def candidate(number, hidden=False):
    return {
        "object_id": str(UUID(int=number)),
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=number),
        "hidden": hidden,
    }


def listing(monkeypatch, rows, error=None):
    queries, decorated = [], []

    class Connection:
        def execute(self, query, params):
            queries.append((query, list(params)))
            assert "TEST_SCOPE" in query and "TEST_PERSONAL" in query
            assert params[:4] == ["tenant", "Programme", "scope", "personal"]
            after = params[4:6] if "(r.created_at,r.object_id)>" in query else None
            remaining = rows
            if after:
                timestamp = after[0]
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                remaining = [
                    row for row in rows if (row["created_at"], row["object_id"]) > (timestamp, after[1])
                ]
            if query.startswith("SELECT 1 "):
                return Rows([{"exists": 1}] if remaining else [])
            return Rows(remaining[: params[-1]])

    service = Service.__new__(Service)
    connection = Connection()
    service.db = SimpleNamespace(transaction=lambda tenant: nullcontext(connection))
    service.work = SimpleNamespace(listing_filter=lambda route, ctx: ("TEST_PERSONAL", ["personal"]))
    ctx = SimpleNamespace(grants=[{"capability": "programmes.read", "purpose": None}])
    monkeypatch.setattr(module, "context", lambda *args: ctx)
    monkeypatch.setattr(module, "visible_sql", lambda *args: ("TEST_SCOPE", ["scope"]))
    service.cursor_binding = lambda *args: "current-visibility-binding"
    service.cursor_key = lambda binding, cursor: cursor["key"] if cursor else None
    service.cursor = lambda payload: payload

    def result(c, ctx, row):
        decorated.append(row["object_id"])
        if row["hidden"]:
            raise error or DomainError("RESOURCE_UNAVAILABLE", 404)
        return {"object_id": row["object_id"], "value": "46.363636363636"}

    service.result = result
    return service, queries, decorated


def test_hidden_dependencies_are_omitted_and_cursor_names_last_returned_visible_row(monkeypatch):
    rows = [candidate(1, True), candidate(2), candidate(3, True), candidate(4)]
    service, _, _ = listing(monkeypatch, rows)
    first = service.listing(None, "tenant", "programmes", limit=1)
    assert first["items"] == [{"object_id": rows[1]["object_id"], "value": "46.363636363636"}]
    assert first["next_cursor"]["key"] == [rows[1]["created_at"].isoformat(), rows[1]["object_id"]]
    assert first["next_cursor"]["binding"] == "current-visibility-binding"
    assert all(row["object_id"] not in str(first) for row in (rows[0], rows[2]))
    second = service.listing(None, "tenant", "programmes", limit=1, cursor=first["next_cursor"])
    assert [item["object_id"] for item in second["items"]] == [rows[3]["object_id"]]
    assert second["next_cursor"] is None


def test_hidden_runs_cross_multiple_batches_without_empty_pages_or_skipped_visible_rows(monkeypatch):
    rows = [candidate(number, number not in {202, 405, 406}) for number in range(1, 407)]
    service, queries, _ = listing(monkeypatch, rows)
    first = service.listing(None, "tenant", "programmes", limit=1)
    second = service.listing(None, "tenant", "programmes", limit=1, cursor=first["next_cursor"])
    third = service.listing(None, "tenant", "programmes", limit=1, cursor=second["next_cursor"])
    assert [page["items"][0]["object_id"] for page in (first, second, third)] == [
        rows[index - 1]["object_id"] for index in (202, 405, 406)
    ]
    assert third["next_cursor"] is None
    assert len(queries) > 3
    assert all(params[-1] <= 100 for query, params in queries if not query.startswith("SELECT 1 "))


def test_all_hidden_candidates_produce_no_items_no_cursor_and_no_hidden_count(monkeypatch):
    service, _, _ = listing(monkeypatch, [candidate(n, True) for n in range(1, 201)])
    assert service.listing(None, "tenant", "programmes") == {
        "items": [],
        "next_cursor": None,
        "scope_label": "Records permitted by your current access",
    }


def test_exact_budget_can_complete_without_a_false_continuation(monkeypatch):
    rows = [candidate(n, n < LIST_SCAN_BUDGET) for n in range(1, LIST_SCAN_BUDGET + 1)]
    service, queries, decorated = listing(monkeypatch, rows)
    page = service.listing(None, "tenant", "programmes", limit=1)
    assert page["items"][0]["object_id"] == rows[-1]["object_id"]
    assert page["next_cursor"] is None and len(decorated) == LIST_SCAN_BUDGET
    assert queries[-1][0].startswith("SELECT 1 ")


def test_budget_exhaustion_refuses_instead_of_returning_partial_or_hidden_scan_cursor(monkeypatch):
    rows = [candidate(n, True) for n in range(1, LIST_SCAN_BUDGET + 1)] + [candidate(LIST_SCAN_BUDGET + 1)]
    service, _, decorated = listing(monkeypatch, rows)
    with pytest.raises(DomainError) as caught:
        service.listing(None, "tenant", "programmes")
    assert (caught.value.code, caught.value.status, caught.value.reason) == (
        "LIMIT_EXCEEDED",
        422,
        "LISTING_SCAN_LIMIT",
    )
    assert len(decorated) == LIST_SCAN_BUDGET


@pytest.mark.parametrize("status", [400, 401, 403, 409, 422, 503])
def test_non_404_domain_errors_propagate(monkeypatch, status):
    error = DomainError("SERVICE_UNAVAILABLE", status)
    service, _, _ = listing(monkeypatch, [candidate(1, True)], error)
    with pytest.raises(DomainError) as caught:
        service.listing(None, "tenant", "programmes")
    assert caught.value is error


def test_non_domain_errors_propagate(monkeypatch):
    error = RuntimeError("synthetic renderer failure")
    service, _, _ = listing(monkeypatch, [candidate(1, True)], error)
    with pytest.raises(RuntimeError) as caught:
        service.listing(None, "tenant", "programmes")
    assert caught.value is error


@pytest.mark.parametrize("limit", [0, 101, -1])
def test_invalid_page_bounds_are_rejected(monkeypatch, limit):
    service, queries, _ = listing(monkeypatch, [])
    with pytest.raises(DomainError) as caught:
        service.listing(None, "tenant", "programmes", limit=limit)
    assert caught.value.code == "VALIDATION_FAILED" and not queries
