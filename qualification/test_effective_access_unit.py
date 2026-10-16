"""Focused pure checks for FR-ACC-003 effective-access explanation semantics."""

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from impact_api.domain import DomainError
from impact_api.effective_access import EffectiveAccess
from impact_api.store import scopes, visible_sql


class Result:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row


class Cursor:
    def __init__(self, available=True, scope_members=None):
        self.available = available
        self.scope_members = set(scope_members or [])

    def execute(self, query, params):
        if "object_registry" in query:
            return Result({"exists": True} if self.available else None)
        if "scope_member" in query:
            return Result({"exists": True} if str(params[-1]) in self.scope_members else None)
        raise AssertionError(query)


def grant(capability, *, source="DIRECT", records=None, purpose=None, fields=None):
    return {
        "source": source,
        "capability": capability,
        "scope_id": str(uuid4()),
        "scope_type": "TENANT",
        "purpose": purpose,
        "record_object_ids": records,
        "readable_field_categories": fields,
        "writable_field_categories": fields,
    }


def identity():
    return SimpleNamespace(
        auth_time=datetime.now(timezone.utc),
        assurance_verified=True,
    )


def test_explicit_record_restriction_wins_over_a_broad_conflicting_role():
    allowed, outside = str(uuid4()), str(uuid4())
    grants = [
        grant("programmes.read", records=[allowed]),
        grant("programmes.read", source="GROUP"),
    ]
    denied = EffectiveAccess._explain(Cursor(), str(uuid4()), "get_programmes", outside, grants, identity())
    assert denied["decision"] == "DENIED"
    assert "RECORD_CONDITION" in denied["restrictions"]
    assert {path["source"] for path in denied["grant_paths"]} == {"DIRECT", "GROUP"}
    assert all("scope_id" not in path for path in denied["grant_paths"])

    ctx = SimpleNamespace(grants=grants, tenant_id=str(uuid4()))
    assert not scopes(Cursor(), ctx, "programmes.read", outside)
    assert scopes(Cursor(), ctx, "programmes.read", allowed)
    expression, params = visible_sql(ctx, "programmes.read")
    assert " AND " in expression and any(allowed in values for values in params)


def test_field_restriction_and_unknown_record_are_sanitized():
    obj = str(uuid4())
    result = EffectiveAccess._explain(
        Cursor(available=False),
        str(uuid4()),
        "get_programmes",
        obj,
        [grant("programmes.read", fields=["PUBLIC"])],
        identity(),
        field_category="SENSITIVE",
        field_access="READ",
    )
    assert result["decision"] == "DENIED"
    assert result["restrictions"] == ["FIELD_CATEGORY", "RESOURCE_UNAVAILABLE"]
    assert obj not in str(result)


def test_purpose_required_operation_explains_missing_and_matching_purpose():
    obj = str(uuid4())
    missing = EffectiveAccess._explain(
        Cursor(),
        str(uuid4()),
        "list_participants",
        obj,
        [grant("participants.read", purpose="SERVICE_DELIVERY")],
        identity(),
    )
    assert missing["decision"] == "DENIED"
    assert "PURPOSE_REQUIRED" in missing["missing_assurance"]
    matched = EffectiveAccess._explain(
        Cursor(),
        str(uuid4()),
        "list_participants",
        obj,
        [grant("participants.read", purpose="SERVICE_DELIVERY")],
        identity(),
        purpose="SERVICE_DELIVERY",
    )
    assert matched["decision"] == "PERMITTED"


def test_request_is_closed_and_field_context_is_paired():
    base = {"operation_id": "get_programmes", "object_id": None}
    assert EffectiveAccess._request(base)[0] == "get_programmes"
    with pytest.raises(DomainError):
        EffectiveAccess._request({**base, "subject_principal_id": str(uuid4())})
    with pytest.raises(DomainError):
        EffectiveAccess._request({**base, "field_category": "SENSITIVE"})
    with pytest.raises(DomainError):
        EffectiveAccess._request({**base, "purpose": 7})
