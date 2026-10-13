"""Bounded diagnosis plan-query/digest checks; fake SQL is not native evidence."""

from types import SimpleNamespace

import pytest

from impact_api import privacy
from impact_api.domain import DomainError
from impact_api.store import hash_data


class Plan(privacy.Privacy):
    def __init__(self):
        pass

    def subject(self, c, ctx, selector):
        return {"object_id": "membership", "principal_id": "principal"}

    def invitations(self, c, ctx, membership):
        return []

    def owned_objects(self, c, ctx, kind, ids, principal):
        return [{"object_id": obj} for obj in ids or []]

    def holds(self, c, ctx, ids):
        return {}


class Query:
    def __init__(self, revisions):
        self.revisions, self.calls, self.result = revisions, [], []

    def execute(self, sql, args):
        self.calls.append((sql, args))
        if "SELECT revision_id,payload_sha256,restriction_state" in sql:
            self.result = self.revisions[args[1]][: args[2]]
        else:
            self.result = []
        return self

    def fetchone(self):
        return None

    def fetchall(self):
        return self.result


def case(ids=None):
    data = {"request_type": "ERASURE", "subject_membership_id": "membership"}
    if ids is not None:
        data["diagnosis_ids"] = ids
    return {"object_id": "case", "payload": data}


def revision(index, state="AVAILABLE"):
    return {
        "revision_id": str(index),
        "payload_sha256": bytes([index % 256]) * 32,
        "restriction_state": state,
    }


def test_diagnosis_plan_budget_is_global_and_overflow_prevents_digest(monkeypatch):
    query = Query({"first": [revision(n) for n in range(privacy.PLAN_LIMIT)], "second": [revision(1)]})
    digests = []
    monkeypatch.setattr(privacy, "hash_data", lambda value: digests.append(value))
    with pytest.raises(DomainError) as error:
        Plan().plan(query, SimpleNamespace(tenant_id="tenant"), case(["first", "second"]))
    assert (error.value.code, error.value.status, error.value.reason) == (
        "LIMIT_EXCEEDED",
        422,
        "PRIVACY_PLAN_TOO_LARGE",
    )
    pins = [
        (sql, args)
        for sql, args in query.calls
        if "SELECT revision_id,payload_sha256,restriction_state" in sql
    ]
    assert [args for _, args in pins] == [
        ("tenant", "first", privacy.PLAN_LIMIT + 1),
        ("tenant", "second", 1),
    ]
    assert all(
        "ORDER BY revision_id LIMIT %s" in sql and "restriction_state<>'REMOVED'" in sql for sql, _ in pins
    )
    assert digests == []


def test_legacy_privacy_plan_hash_unchanged_without_diagnosis_scope():
    expected = hash_data(
        {
            "case_id": "case",
            "request_type": "ERASURE",
            "subject": ["membership", "principal"],
            "sections": None,
            "entries": [],
        }
    ).hex()
    for selected in [None, []]:
        entries, digest, extras = Plan().plan(Query({}), SimpleNamespace(tenant_id="tenant"), case(selected))
        assert entries == [] and digest == expected
        assert extras["object_store"] == {}


def test_restricted_revision_state_is_pinned_into_diagnosis_plan_digest():
    first = Query({"selected": [revision(1)]})
    second = Query({"selected": [revision(1, "RESTRICTED")]})
    plan = Plan()
    ordinary = plan.plan(first, SimpleNamespace(tenant_id="tenant"), case(["selected"]))
    restricted = plan.plan(second, SimpleNamespace(tenant_id="tenant"), case(["selected"]))
    assert ordinary[0] == restricted[0]
    assert ordinary[1] != restricted[1]
