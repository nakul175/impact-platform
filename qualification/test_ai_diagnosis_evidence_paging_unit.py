"""Deterministic visibility pagination regression, separate from native authority evidence."""

import pytest

from impact_api.ai_diagnoses import AIDiagnoses
from impact_api.domain import DomainError


def test_hidden_rows_do_not_underfill_a_visible_page_when_batch_has_visible_rows(monkeypatch):
    feature = AIDiagnoses(None)
    rows = [{"payload": {"hidden": i < 3}, "id": i} for i in range(6)]

    def check(c, identity, tenant, payload):
        if payload["hidden"]:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)

    monkeypatch.setattr(feature, "check_evidence", check)
    page, scanned = feature.visible_page(None, None, None, rows, 2)
    assert [row["id"] for row in page] == [3, 4]
    assert scanned == 5 and len(rows) > scanned


def test_empty_hidden_batch_is_bounded_and_advances_to_a_continuation(monkeypatch):
    feature = AIDiagnoses(None)
    rows = [{"payload": {}, "id": i} for i in range(101)]
    calls = []

    def check(c, identity, tenant, payload):
        calls.append(payload)
        raise DomainError("RESOURCE_UNAVAILABLE", 404)

    monkeypatch.setattr(feature, "check_evidence", check)
    assert feature.visible_page(None, None, None, rows, 50) == ([], 100)
    assert len(calls) == 100 and len(rows) > 100


def test_non_visibility_errors_are_not_silently_filtered(monkeypatch):
    feature = AIDiagnoses(None)

    def check(c, identity, tenant, payload):
        raise DomainError("AUTH_REQUIRED", 401)

    monkeypatch.setattr(feature, "check_evidence", check)
    with pytest.raises(DomainError) as error:
        feature.visible_page(None, None, None, [{"payload": {}}], 1)
    assert error.value.code == "AUTH_REQUIRED"
