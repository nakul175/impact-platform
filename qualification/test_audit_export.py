"""Audit export (v0.25 part A, VF-AUD-001): capability-gated, purpose-required, fresh-assurance
export of the tenant's audit events as JSON Lines with a hash chain, a SHA-256 manifest and a
platform seal; bounded, paginated and itself audited."""

import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from impact_api.audit_export import FIELDS, genesis, link, seal, verify_content, verify_seal
from impact_api.audit_export_contracts import PURPOSES
from impact_api.contracts import OPERATIONS, validate
from test_administration import command, expect

ROUTE = "audit-exports"


def window(days=365, end_offset_seconds=0):
    end = datetime.now(timezone.utc) - timedelta(seconds=end_offset_seconds)
    return (end - timedelta(days=days)).isoformat(), end.isoformat()


def body(purpose="SECURITY_REVIEW", limit=5, cursor=None, start=None, end=None, operation=None):
    if start is None:
        start, end = window()
    data = {
        "window_start": start,
        "window_end": end,
        "purpose": purpose,
        "reason": "Quarterly access review of the qualification tenant",
        "limit": limit,
    }
    if cursor:
        data["cursor"] = cursor
    return command(data, operation=operation)


def export(live, payload, actor="admin", tenant=None, **kwargs):
    return live.request(live.path(ROUTE, tenant=tenant), actor=actor, method="POST", body=payload, **kwargs)


# ------------------------------------------------------------------------------------- pure rules


def test_policy_row_is_purpose_required_fresh_and_audited():
    row = OPERATIONS["create_audit_export"]
    assert row["capability"] == "audit.export" and row["method"] == "POST"
    assert row["purpose_required"] is True and row["fresh_assurance_seconds"] == 300 and row["audit"] is True
    assert set(row["role_templates"]) == {"OWNER", "TENANT_ADMIN"}


def test_chain_digest_and_seal_verify_and_detect_tampering():
    settings = SimpleNamespace(cookie_secret="c" * 64, cookie_secret_previous="")
    start, end = "2026-01-01T00:00:00Z", "2026-02-01T00:00:00Z"
    chain = genesis("t", start, end)
    lines = []
    for n in range(3):
        record = {k: None for k in FIELDS if k != "chain"} | {"sequence": n + 1, "action_type": "x" + str(n)}
        chain = link(chain, record)
        lines.append(json.dumps({**record, "chain": chain}, sort_keys=True, separators=(",", ":")))
    content = "".join(line + "\n" for line in lines)
    manifest = {
        "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
        "content_bytes": len(content.encode()),
        "event_count": 3,
        "chain_start": genesis("t", start, end),
        "chain_end": chain,
    }
    manifest["seal"] = seal(settings, manifest)
    assert verify_content(manifest, content) == [] and verify_seal(settings, manifest)
    # A changed line breaks the digest and the chain; a changed manifest breaks the seal.
    assert {"CONTENT_DIGEST", "CHAIN"} <= set(verify_content(manifest, content.replace("x1", "x9")))
    assert not verify_seal(settings, {**manifest, "event_count": 2})
    # The seal survives a cookie-secret rotation during grace and fails after retirement.
    rotated = SimpleNamespace(cookie_secret="d" * 64, cookie_secret_previous="c" * 64)
    assert verify_seal(rotated, manifest)
    assert not verify_seal(SimpleNamespace(cookie_secret="d" * 64, cookie_secret_previous=""), manifest)


# ------------------------------------------------------------------------------------------- live


def test_export_pages_verify_and_each_export_is_audited(live):
    start, end = window()
    first = body(start=start, end=end, limit=3)
    response = export(live, first)
    page = expect(response, 200)
    validate("AuditExport", page)
    manifest = page["manifest"]
    assert manifest["tenant_id"] == live.fixture["tenant_a"] and manifest["purpose"] == "SECURITY_REVIEW"
    assert manifest["page"] == 1 and manifest["first_sequence"] == 1 and manifest["event_count"] == 3
    assert manifest["complete"] is False and page["next_cursor"]
    assert manifest["chain_start"] == genesis(
        live.fixture["tenant_a"], manifest["window_start"], manifest["window_end"]
    )
    assert verify_content(manifest, page["content"]) == []
    assert verify_seal(SimpleNamespace(**live.config), manifest)
    records = [json.loads(line) for line in page["content"].splitlines()]
    assert all(sorted(r) == sorted(FIELDS) for r in records)
    assert [r["sequence"] for r in records] == [1, 2, 3]
    assert [(r["occurred_at"], r["event_id"]) for r in records] == sorted(
        (r["occurred_at"], r["event_id"]) for r in records
    )
    # Page two continues the sequence and the chain where page one ended.
    second = expect(export(live, body(start=start, end=end, limit=3, cursor=page["next_cursor"])), 200)
    m2 = second["manifest"]
    assert m2["page"] == 2 and m2["first_sequence"] == 4 and m2["chain_start"] == manifest["chain_end"]
    assert verify_content(m2, second["content"]) == []
    assert not {r["event_id"] for r in records} & {
        json.loads(line)["event_id"] for line in second["content"].splitlines()
    }
    # Each page is recorded: one audit event (the export id) with the purpose, the request
    # correlation and the exporting principal, and one operation receipt.
    with live.db() as c:
        for exported, correlation in [(manifest, response.headers["x-correlation-id"]), (m2, None)]:
            row = c.execute(
                "SELECT * FROM impact.audit_event_current WHERE tenant_id=%s AND object_id=%s",
                (live.fixture["tenant_a"], exported["export_id"]),
            ).fetchone()
            assert row["action_type"] == "create_audit_export" and row["outcome"] == "SUCCEEDED"
            assert row["specification_ref"] == "VF-AUD-001/SECURITY_REVIEW"
            assert str(row["real_actor_id"]) == live.fixture["actors"]["admin"]["principal_id"]
            assert str(row["correlation_id"]) == exported["correlation_id"]
            if correlation:
                assert exported["correlation_id"] == correlation
            # The export's own event lies outside the window it read.
            assert row["occurred_at"] >= datetime.fromisoformat(end)
        receipt = c.execute(
            "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='create_audit_export' AND operation_id=%s",
            (live.fixture["tenant_a"], first["operation_id"]),
        ).fetchone()
        assert receipt["outcome"]["manifest"]["content_sha256"] == manifest["content_sha256"]


def test_exact_retry_is_identical_and_a_changed_payload_conflicts(live):
    payload = body(limit=2)
    original = expect(export(live, payload), 200)
    assert expect(export(live, payload), 200) == original
    changed = {**payload, "data": {**payload["data"], "limit": 3}}
    assert expect(export(live, changed), 409)["code"] == "CONFLICT_OPERATION"


def test_owner_may_export_and_the_content_holds_no_secret(live):
    page = expect(export(live, body(purpose="INTERNAL_AUDIT", limit=50), actor="owner"), 200)
    text = json.dumps(page)
    for name, value in live.config.items():
        if name.endswith("secret") or name.endswith("dsn") or name.endswith("_previous"):
            for part in str(value).split(","):
                assert len(part) < 16 or part not in text, name


def test_refusals_tenant_capability_assurance_and_revocation(live):
    # Another tenant's member, and a member addressing another tenant: both unavailable.
    expect(export(live, body(), actor="other_tenant"), 404)
    expect(export(live, body(), actor="admin", tenant=live.fixture["tenant_b"]), 404)
    # A member without audit.export.
    for actor in ["author", "reviewer", "partner"]:
        assert expect(export(live, body(), actor=actor), 403)["code"] == "POLICY_DENIED"
    # Authentication older than 300 seconds.
    stale = live.signed(live.fixture["actors"]["admin"]["identity_id"], auth_time=time.time() - 400)
    refused = expect(export(live, body(), actor=None, headers={"Authorization": "Bearer " + stale}), 403)
    assert (refused["code"], refused["reason_code"]) == (
        "ASSURANCE_REQUIRED",
        "FRESH_AUTHENTICATION_REQUIRED",
    )
    # A revoked member and an anonymous caller.
    assert export(live, body(), actor="revoked").status_code in {401, 404}
    expect(export(live, body(), actor=None), 401)


def test_purpose_is_required_and_a_purpose_bound_grant_authorises_only_its_purpose(live):
    payload = body()
    del payload["data"]["purpose"]
    expect(export(live, payload), 422)
    principal = live.fixture["actors"]["owner"]["principal_id"]
    with live.db() as c:
        c.execute(
            "UPDATE impact.grant_current SET purpose='INTERNAL_AUDIT' WHERE subject_id=%s AND capability='audit.export'",
            (principal,),
        )
    try:
        assert (
            expect(export(live, body(purpose="SECURITY_REVIEW"), actor="owner"), 403)["code"]
            == "POLICY_DENIED"
        )
        expect(export(live, body(purpose="INTERNAL_AUDIT", limit=1), actor="owner"), 200)
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.grant_current SET purpose=NULL WHERE subject_id=%s AND capability='audit.export'",
                (principal,),
            )


@pytest.mark.parametrize(
    "case,reason",
    [
        ("future", "WINDOW_IN_FUTURE"),
        ("too-long", "WINDOW_TOO_LONG"),
        ("reversed", "WINDOW_INVALID"),
        ("limit", None),
        ("purpose", None),
        ("unknown-field", None),
    ],
)
def test_window_and_body_are_bounded(live, case, reason):
    payload = body()
    at = datetime.now(timezone.utc)
    data = payload["data"]
    if case == "future":
        data.update(
            window_start=(at - timedelta(days=1)).isoformat(), window_end=(at + timedelta(days=1)).isoformat()
        )
    elif case == "too-long":
        data["window_start"] = (at - timedelta(days=400)).isoformat()
    elif case == "reversed":
        data.update(
            window_start=(at - timedelta(hours=1)).isoformat(),
            window_end=(at - timedelta(hours=2)).isoformat(),
        )
    elif case == "limit":
        data["limit"] = 1001
    elif case == "purpose":
        data["purpose"] = "CURIOSITY"
    else:
        data["secret"] = "x"
    refused = expect(export(live, payload), 422)
    if reason:
        assert refused["reason_code"] == reason


def test_cursor_is_signed_and_bound_to_window_and_purpose(live):
    start, end = window()
    page = expect(export(live, body(start=start, end=end, limit=1)), 200)
    cursor = page["next_cursor"]
    tampered = cursor[:-1] + ("0" if cursor[-1] != "0" else "1")
    assert expect(export(live, body(start=start, end=end, cursor=tampered)), 400)["code"] == "INVALID_CURSOR"
    other = body(purpose="REGULATORY_REQUEST", start=start, end=end, cursor=cursor)
    assert expect(export(live, other), 400)["code"] == "INVALID_CURSOR"
    shifted = body(
        start=start, end=(datetime.fromisoformat(end) - timedelta(seconds=1)).isoformat(), cursor=cursor
    )
    assert expect(export(live, shifted), 400)["code"] == "INVALID_CURSOR"
    # Another actor cannot continue an export someone else started.
    assert expect(export(live, body(start=start, end=end, cursor=cursor), actor="owner"), 400)["code"] == (
        "INVALID_CURSOR"
    )


def test_empty_window_is_a_complete_page_with_the_genesis_chain(live):
    start = "2001-01-01T00:00:00+00:00"
    end = "2001-01-02T00:00:00+00:00"
    page = expect(export(live, body(start=start, end=end)), 200)
    manifest = page["manifest"]
    assert (manifest["event_count"], manifest["complete"], page["content"], page["next_cursor"]) == (
        0,
        True,
        "",
        None,
    )
    assert (
        manifest["chain_start"]
        == manifest["chain_end"]
        == genesis(live.fixture["tenant_a"], manifest["window_start"], manifest["window_end"])
    )
    assert manifest["first_sequence"] is None and verify_content(manifest, "") == []
    assert set(PURPOSES) >= {manifest["purpose"]}
    uuid.UUID(manifest["export_id"])
