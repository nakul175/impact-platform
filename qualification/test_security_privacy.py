"""Security and privacy (v0.27): denial auditing with flood collapsing and its place in the audit
export, the durable audit-export register, tenant retention policies approved independently and
honoured by the sweep inside their bounds (the audit floor never crossed), and the retention-hold
API (placed at once, released only by another natural person, blocking erasure meanwhile)."""
# ruff: noqa: F811

import json
import time
import uuid
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from impact_api.audit_export import FIELDS, verify_content
from impact_api.contracts import OPERATIONS, validate
from impact_api.retention import AUDIT_DEFAULT_DAYS, AUDIT_FLOOR_DAYS, CLASSES, POLICY_BOUNDS, check_policy
from impact_api.security_events import CAP_PER_WINDOW, WINDOW_SECONDS, route_of
from test_administration import command, expect
from test_audit_export import body as export_body, export
from test_live_application import cmd, draft
from test_privacy_requests import create_case, grant, member, member_evidence, plan, revoke
from test_native_roles import connect, denied, query  # noqa: F401
from test_retention import make_due, proofs, receipt_of, sweep_jobs
from test_worker import empty_summary, make_worker

CSV = b"household,visited\nH1,yes\n"


def tenant(live):
    return live.fixture["tenant_a"]


def principal(live, actor):
    return live.fixture["actors"][actor]["principal_id"]


def denials(live, actor=None, **where):
    with live.db() as c:
        query, params = "SELECT * FROM impact.access_denial WHERE tenant_id=%s", [tenant(live)]
        if actor:
            query += " AND principal_id=%s"
            params.append(principal(live, actor))
        for column, value in where.items():
            query += " AND " + column + "=%s"
            params.append(value)
        return c.execute(query + " ORDER BY first_at,denial_id", params).fetchall()


def policy_body(data_class="OPERATION_RECEIPT", days=30, action=None, **extra):
    return command(
        {
            "data_class": data_class,
            "duration_days": days,
            "expiry_action": action or CLASSES[data_class]["action"],
            "reason": "Synthetic retention policy proposed for qualification",
            **extra,
        }
    )


def propose(live, actor="owner", status=201, **kwargs):
    return expect(
        live.request(live.path("retention-policies"), actor=actor, method="POST", body=policy_body(**kwargs)),
        status,
    )


def approve_policy(live, obj, actor="admin", status=200):
    current = expect(live.request(live.path("retention-policies", obj), actor="admin"), 200)
    return expect(
        live.request(
            live.path("retention-policies", obj) + "/actions/approve",
            actor=actor,
            method="POST",
            body=command({"reason": "Reviewed against the records schedule"}, current["revision_id"]),
        ),
        status,
    )


def place_hold(live, object_id, actor="privacy", status=201, days=30):
    return expect(
        live.request(
            live.path("retention-holds"),
            actor=actor,
            method="POST",
            body=command(
                {
                    "object_id": object_id,
                    "authority_reference": "Synthetic legal hold LH-" + uuid.uuid4().hex[:6],
                    "reason": "Litigation hold placed for qualification",
                    "review_at": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(),
                }
            ),
        ),
        status,
    )


def release_hold(live, hold_id, actor="admin", status=200):
    return expect(
        live.request(
            live.path("retention-holds", hold_id) + "/actions/release",
            actor=actor,
            method="POST",
            body=command({"reason": "Matter closed"}),
        ),
        status,
    )


# ------------------------------------------------------------------------------------- pure rules


def test_policy_rows_roles_assurance_and_independence():
    approve = OPERATIONS["action_retention_policies_approve"]
    assert approve["capability"] == "retention-policy.approve" and approve["fresh_assurance_seconds"] == 300
    assert approve["independence_required"] is True and approve["audit"] is True
    assert set(approve["role_templates"]) == {"TENANT_ADMIN", "PRIVACY"}
    release = OPERATIONS["action_retention_holds_release"]
    assert release["independence_required"] is True and release["fresh_assurance_seconds"] == 300
    assert OPERATIONS["create_retention_holds"]["fresh_assurance_seconds"] == 300
    assert set(OPERATIONS["list_access_denials"]["role_templates"]) == {"OWNER", "TENANT_ADMIN"}
    assert OPERATIONS["list_access_denials"]["audit"] is False
    assert set(OPERATIONS["create_retention_policies"]["role_templates"]) == {
        "OWNER",
        "TENANT_ADMIN",
        "PRIVACY",
    }
    assert "occurrences" in FIELDS


def test_policy_bounds_keep_the_audit_floor_and_the_fixed_actions():
    assert POLICY_BOUNDS["SECURITY_EVENT"][0] == AUDIT_FLOOR_DAYS == 365
    assert CLASSES["SECURITY_EVENT"]["retention_days"] == AUDIT_DEFAULT_DAYS >= AUDIT_FLOOR_DAYS
    assert check_policy("SECURITY_EVENT", AUDIT_FLOOR_DAYS - 1, "DELETE") == "RETENTION_OUT_OF_BOUNDS"
    assert check_policy("SECURITY_EVENT", AUDIT_FLOOR_DAYS, "DELETE") is None
    assert check_policy("UPLOAD_SESSION", 5, "EXPIRE") == "DATA_CLASS_NOT_POLICY_ABLE"
    assert check_policy("OPERATION_RECEIPT", 6, "DELETE") == "RETENTION_OUT_OF_BOUNDS"
    assert check_policy("OPERATION_RECEIPT", 30, "REDACT") == "RETENTION_ACTION_FIXED"
    assert check_policy("OUTBOX_RECIPIENT", 365, "REDACT") is None
    assert check_policy("NOT_A_CLASS", 1, "DELETE") == "DATA_CLASS_NOT_POLICY_ABLE"
    for data_class, (low, high) in POLICY_BOUNDS.items():
        assert low <= CLASSES[data_class]["retention_days"] <= high, data_class


def test_route_template_strips_identifiers():
    t = str(uuid.uuid4())
    assert route_of("/v1/tenants/" + t + "/reports/" + str(uuid.uuid4()) + "/actions/publish", t) == (
        "/v1/tenants/{tenant_id}/reports/{id}/actions/publish"
    )
    assert len(route_of("/v1/tenants/" + t + "/" + "x" * 400, t)) == 256


# ------------------------------------------------------------------------------- denial auditing


def test_denials_are_recorded_collapsed_listed_and_exported(live):
    before = len(denials(live, "author", operation_id="create_audit_export"))
    window_start = (datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat()
    # The author holds no audit.export: the same refusal five times collapses into one row.
    correlations = []
    for _ in range(5):
        refused = export(live, export_body(), actor="author")
        assert refused.status_code == 403 and refused.json()["code"] == "POLICY_DENIED"
        correlations.append(refused.json()["correlation_id"])
    time.sleep(0.2)
    rows = denials(live, "author", operation_id="create_audit_export")
    assert len(rows) == before + 1
    row = rows[-1]
    assert row["occurrences"] >= 5 and row["status"] == 403 and row["reason_code"] == "POLICY_DENIED"
    assert row["capability"] == "audit.export" and row["route"] == "/v1/tenants/{tenant_id}/audit-exports"
    assert str(row["last_correlation_id"]) == correlations[-1]
    assert str(row["first_correlation_id"]) in correlations or row["occurrences"] > 5
    # A hidden refusal (404 for an object the caller may not read) records the selector and 404.
    selector = str(uuid.uuid4())
    hidden = live.request(live.path("retention-policies", selector), actor="partner")
    assert hidden.status_code == 404, hidden.text
    time.sleep(0.2)
    hidden_rows = denials(live, "partner", operation_id="get_retention_policies")
    assert hidden_rows and hidden_rows[-1]["status"] == 404 and str(hidden_rows[-1]["object_id"]) == selector
    assert hidden_rows[-1]["reason_code"] == "RESOURCE_UNAVAILABLE"
    # A fresh-assurance refusal is recorded with its reason.
    stale = live.signed(live.fixture["actors"]["admin"]["identity_id"], auth_time=time.time() - 400)
    refused = expect(
        export(live, export_body(), actor=None, headers={"Authorization": "Bearer " + stale}), 403
    )
    assert refused["reason_code"] == "FRESH_AUTHENTICATION_REQUIRED"
    time.sleep(0.2)
    assert denials(live, "admin", reason_code="FRESH_AUTHENTICATION_REQUIRED")
    # Nothing but identifiers and codes is stored.
    with live.db() as c:
        columns = {
            r["column_name"]
            for r in c.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_schema='impact' AND table_name='access_denial'"
            ).fetchall()
        }
    assert not columns & {"payload", "body", "token", "email", "recipient"}

    # Visible to administrators and owners, refused to others (that refusal is itself recorded),
    # unavailable from another tenant.
    listed = expect(live.request(live.path("access-denials"), actor="admin", params={"limit": 200}), 200)
    validate("AccessDenialList", listed)
    ids = {item["denial_id"] for item in listed["items"]}
    assert str(row["denial_id"]) in ids and str(hidden_rows[-1]["denial_id"]) in ids
    expect(live.request(live.path("access-denials"), actor="owner"), 200)
    expect(live.request(live.path("access-denials"), actor="author"), 403)
    expect(live.request(live.path("access-denials"), actor="other_tenant"), 404)
    time.sleep(0.2)
    assert denials(live, "author", operation_id="list_access_denials")

    # The audit export carries the denials of the window as DENIED lines and registers the page.
    time.sleep(0.3)
    window_end = datetime.now(timezone.utc).isoformat()
    page = expect(export(live, export_body(limit=1000, start=window_start, end=window_end)), 200)
    manifest = page["manifest"]
    assert verify_content(manifest, page["content"]) == []
    assert manifest["format"] == "impact-audit-export-v2" and manifest["fields"] == FIELDS
    lines = [json.loads(line) for line in page["content"].split("\n") if line]
    denied = [line for line in lines if line["outcome"] == "DENIED"]
    assert manifest["denial_count"] == len(denied) >= 1
    mine = [line for line in denied if line["event_id"] == str(row["denial_id"])]
    assert mine and mine[0]["action_type"] == "create_audit_export" and mine[0]["occurrences"] >= 5
    assert mine[0]["revision_id"] is None and mine[0]["specification_ref"] == "FR-SEC-007/POLICY_DENIED"
    assert mine[0]["real_actor_id"] == principal(live, "author")
    assert all(line["occurrences"] is None for line in lines if line["outcome"] != "DENIED")
    with live.db() as c:
        register = c.execute(
            "SELECT * FROM impact.audit_export_register WHERE export_id=%s", (manifest["export_id"],)
        ).fetchone()
    assert register and bytes(register["content_sha256"]).hex() == manifest["content_sha256"]
    assert bytes(register["chain_end"]).hex() == manifest["chain_end"]
    assert register["seal_key_id"] == manifest["seal"]["key_id"] and register["purpose"] == "SECURITY_REVIEW"
    assert register["event_count"] == manifest["event_count"] and register["denial_count"] == len(denied)
    assert register["page"] == 1 and str(register["principal_id"]) == principal(live, "admin")


def test_a_scan_cannot_flood_the_denial_table(live):
    """Through the definer the application calls: distinct operations beyond the per-window cap
    collapse into one overflow row, and repeats never add rows."""
    t, actor = tenant(live), principal(live, "enumerator")
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (t,))
        c.execute("DELETE FROM impact.access_denial WHERE tenant_id=%s AND principal_id=%s", (t, actor))
        ids = set()
        for n in range(CAP_PER_WINDOW + 25):
            for _ in range(3):
                ids.add(
                    c.execute(
                        "SELECT impact.record_access_denial(%s,%s,%s,%s,403,'POLICY_DENIED','POLICY_DENIED',NULL,%s,%s,%s) AS d",
                        (
                            actor,
                            "scan_operation_" + str(n),
                            "cap",
                            "/route",
                            str(uuid.uuid4()),
                            WINDOW_SECONDS,
                            CAP_PER_WINDOW,
                        ),
                    ).fetchone()["d"]
                )
        rows = c.execute(
            "SELECT operation_id,reason_code,occurrences FROM impact.access_denial WHERE tenant_id=%s AND principal_id=%s "
            "ORDER BY first_at,denial_id",
            (t, actor),
        ).fetchall()
    assert len(rows) == CAP_PER_WINDOW + 1 == len(ids)
    overflow = [r for r in rows if r["operation_id"] == "*"]
    assert len(overflow) == 1 and overflow[0]["reason_code"] == "DENIAL_LIMIT"
    assert overflow[0]["occurrences"] == 25 * 3
    assert all(r["occurrences"] == 3 for r in rows if r["operation_id"] != "*")
    # The application itself can only read the table and never rewrite a row's identity.
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (t,))
        for statement in [
            "INSERT INTO impact.access_denial SELECT * FROM impact.access_denial LIMIT 1",
            "UPDATE impact.access_denial SET occurrences=1",
            "DELETE FROM impact.access_denial",
            "UPDATE impact.audit_export_register SET purpose='INTERNAL_AUDIT'",
            "DELETE FROM impact.audit_export_register",
            "UPDATE impact.retention_policy_binding SET duration_days=0",
            "DELETE FROM impact.retention_policy_binding",
        ]:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                with c.transaction():
                    c.execute(statement)
    with live.db() as c:
        with pytest.raises(psycopg.errors.CheckViolation):
            with c.transaction():
                c.execute(
                    "UPDATE impact.access_denial SET operation_id='rewritten' WHERE tenant_id=%s AND principal_id=%s",
                    (t, actor),
                )


# ---------------------------------------------------------------------------- retention policies


def test_retention_policies_need_independent_approval_and_the_sweep_honours_them(live):
    # Out-of-bounds or fixed-class proposals are refused; the audit floor is a bound.
    assert propose(live, status=422, data_class="SECURITY_EVENT", days=AUDIT_FLOOR_DAYS - 1)[
        "reason_code"
    ] == ("RETENTION_OUT_OF_BOUNDS")
    assert propose(live, status=422, days=200)["reason_code"] == "RETENTION_OUT_OF_BOUNDS"
    assert propose(live, status=422, action="REDACT")["reason_code"] == "RETENTION_ACTION_FIXED"
    assert (
        live.request(
            live.path("retention-policies"),
            actor="owner",
            method="POST",
            body=policy_body(data_class="UPLOAD_SESSION", days=1),
        ).status_code
        == 422
    )
    # The administrator proposes 30 days for receipts and cannot approve their own proposal.
    created = propose(live, actor="admin", days=30)
    assert created["business_state"] == "Draft"
    policy = created["object_id"]
    refused = approve_policy(live, policy, actor="admin", status=403)
    assert refused["reason_code"] == "INDEPENDENCE_REQUIRED"
    approve_policy(live, policy, actor="owner", status=404)  # no approval capability: hidden
    expect(live.request(live.path("retention-policies", policy), actor="author"), 404)  # hidden
    expect(live.request(live.path("retention-policies"), actor="author"), 403)
    expect(live.request(live.path("retention-policies", policy), actor="other_tenant"), 404)
    # A patch keeps it a Draft; a stale revision conflicts.
    patched = expect(
        live.request(
            live.path("retention-policies", policy),
            actor="owner",
            method="PATCH",
            body=command({"duration_days": 45}, created["revision_id"]),
        ),
        200,
    )
    expect(
        live.request(
            live.path("retention-policies", policy),
            actor="owner",
            method="PATCH",
            body=command({"duration_days": 60}, created["revision_id"]),
        ),
        409,
    )
    approved = approve_policy(live, policy, actor="privacy")
    assert approved["business_state"] == "Approved"
    expect(
        live.request(
            live.path("retention-policies", policy),
            actor="owner",
            method="PATCH",
            body=command({"duration_days": 60}, approved["revision_id"]),
        ),
        409,
    )
    current = expect(live.request(live.path("retention-policies", policy), actor="privacy"), 200)
    assert current["data"]["approved_by"] == principal(live, "privacy")
    assert current["data"]["duration_days"] == 45
    listed = expect(live.request(live.path("retention-policies"), actor="admin"), 200)
    assert policy in {item["object_id"] for item in listed["items"]}
    with live.db() as c:
        binding = c.execute(
            "SELECT * FROM impact.retention_policy_binding WHERE policy_id=%s", (policy,)
        ).fetchone()
    assert binding["duration_days"] == 45 and str(binding["policy_revision"]) == approved["revision_id"]
    assert str(binding["approved_by"]) == principal(live, "privacy")
    assert str(binding["proposed_by"]) == principal(live, "admin")
    _ = patched
    # The schedule read shows the effective value and its source.
    schedule = expect(live.request(live.path("retention-schedule"), actor="admin"), 200)
    validate("RetentionSchedule", schedule)
    receipts = next(i for i in schedule["items"] if i["data_class"] == "OPERATION_RECEIPT")
    assert (
        receipts["retention_days"] == 45
        and receipts["source"] == "APPROVED_POLICY"
        and receipts["policy_id"] == policy
    )
    uploads = next(i for i in schedule["items"] if i["data_class"] == "UPLOAD_SESSION")
    assert uploads["source"] == "DEFAULT" and uploads["policy_id"] is None

    # The sweep keeps a receipt that is expired by the API's 7 days but inside the 45-day policy,
    # and deletes one beyond it; the proof carries the applied duration.
    kept = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    gone = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    with live.db() as c:
        c.execute(
            "UPDATE impact.operation_receipt SET expires_at=now()-interval '1 day' WHERE operation_id=%s",
            (kept["operation_id"],),
        )
        c.execute(
            "UPDATE impact.operation_receipt SET expires_at=now()-interval '40 days' WHERE operation_id=%s",
            (gone["operation_id"],),
        )
    make_due(live)
    worker = make_worker(live)
    summary = empty_summary()
    worker.run_retention(tenant(live), summary)
    assert summary["retention_swept"] == 1
    job = sweep_jobs(live)[-1]
    proof = proofs(live, job["job_id"])
    assert proof["OPERATION_RECEIPT"]["retention_days"] == 45
    assert proof["SECURITY_EVENT"]["retention_days"] == AUDIT_DEFAULT_DAYS
    assert receipt_of(live, kept["operation_id"]) is not None
    assert receipt_of(live, gone["operation_id"]) is None
    # A later proposal supersedes the approved one only by naming its current revision.
    assert (
        propose(live, status=422, days=30, supersedes_revision=created["revision_id"])["reason_code"]
        == "SUPERSEDES_NOT_CURRENT"
    )
    successor = propose(live, days=30, supersedes_revision=approved["revision_id"])
    second = approve_policy(live, successor["object_id"], actor="admin")
    schedule = expect(live.request(live.path("retention-schedule"), actor="admin"), 200)
    assert (
        next(i for i in schedule["items"] if i["data_class"] == "OPERATION_RECEIPT")["retention_days"] == 30
    )
    # Leave the tenant on the build default (a 7-day policy), so the other suites' expectations hold
    # whatever the file order.
    restored = propose(live, days=7, supersedes_revision=second["revision_id"])
    approve_policy(live, restored["object_id"], actor="admin")


def test_the_audit_window_is_never_crossed_and_audit_events_are_never_swept(live):
    t, actor = tenant(live), principal(live, "enumerator")
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (t,))
        c.execute("DELETE FROM impact.access_denial WHERE tenant_id=%s AND principal_id=%s", (t, actor))
        old, recent = [
            c.execute(
                "SELECT impact.record_access_denial(%s,%s,'cap','/route',403,'POLICY_DENIED','POLICY_DENIED',NULL,%s,%s,%s) AS d",
                (actor, name, str(uuid.uuid4()), WINDOW_SECONDS, CAP_PER_WINDOW),
            ).fetchone()["d"]
            for name in ["window_old", "window_recent"]
        ]
        c.execute(
            "UPDATE impact.access_denial SET last_at=now()-interval '3000 days' WHERE denial_id=%s", (old,)
        )
        c.execute(
            "UPDATE impact.access_denial SET last_at=now()-interval '400 days' WHERE denial_id=%s", (recent,)
        )
        audit_events = c.execute(
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s", (t,)
        ).fetchone()["n"]
        # An audit event far beyond any window: it must survive every sweep of this build.
        ancient = c.execute(
            "UPDATE impact.audit_event_current SET occurred_at=now()-interval '4000 days' WHERE tenant_id=%s AND object_id=("
            "SELECT object_id FROM impact.audit_event_current WHERE tenant_id=%s ORDER BY occurred_at LIMIT 1) RETURNING object_id",
            (t, t),
        ).fetchone()["object_id"]
    # Default window (seven years): the 3000-day row goes, the 400-day row stays.
    make_due(live)
    worker = make_worker(live)
    worker.run_retention(t, empty_summary())
    proof = proofs(live, sweep_jobs(live)[-1]["job_id"])["SECURITY_EVENT"]
    assert proof["retention_days"] == AUDIT_DEFAULT_DAYS and proof["action"] == "DELETE"
    assert proof["affected_count"] >= 1
    remaining = {str(r["denial_id"]) for r in denials(live, "enumerator")}
    assert str(old) not in remaining and str(recent) in remaining
    # The definer refuses to go below the floor even when asked to.
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (t,))
        c.execute(
            "UPDATE impact.access_denial SET last_at=now()-interval '200 days' WHERE denial_id=%s", (recent,)
        )
        purged = c.execute("SELECT * FROM impact.retention_purge_security_events(5000,1)").fetchall()
    assert not any(item["item"].startswith(str(recent)) for item in purged)
    # A policy at the floor is accepted; one below it is refused; approved, it removes the 400-day row.
    with live.db() as c:
        c.execute(
            "UPDATE impact.access_denial SET last_at=now()-interval '400 days' WHERE denial_id=%s", (recent,)
        )
    created = propose(live, data_class="SECURITY_EVENT", days=AUDIT_FLOOR_DAYS)
    approve_policy(live, created["object_id"], actor="admin")
    make_due(live)
    worker.run_retention(t, empty_summary())
    proof = proofs(live, sweep_jobs(live)[-1]["job_id"])["SECURITY_EVENT"]
    assert proof["retention_days"] == AUDIT_FLOOR_DAYS
    assert str(recent) not in {str(r["denial_id"]) for r in denials(live, "enumerator")}
    with live.db() as c:
        after = c.execute(
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s", (t,)
        ).fetchone()["n"]
        assert c.execute(
            "SELECT 1 FROM impact.audit_event_current WHERE tenant_id=%s AND object_id=%s", (t, ancient)
        ).fetchone()
    assert after >= audit_events
    # Back to the seven-year default for the suites that follow.
    floor_policy = expect(
        live.request(live.path("retention-policies", created["object_id"]), actor="admin"), 200
    )
    restored = propose(
        live,
        data_class="SECURITY_EVENT",
        days=AUDIT_DEFAULT_DAYS,
        supersedes_revision=floor_policy["revision_id"],
    )
    approve_policy(live, restored["object_id"], actor="privacy")


# ----------------------------------------------------------------------------------------- holds


def test_holds_are_placed_through_the_api_block_erasure_and_release_independently(live):
    subject = member(live)
    grant(live, subject, "upload.create", "upload.write", "uploads.read")
    evidence_id, _, _ = member_evidence(live, subject, CSV + b"#hold-" + uuid.uuid4().hex.encode() + b"\n")
    revoke(live, subject)
    # Place: future review date required; the hold is effective at once and listed.
    assert place_hold(live, evidence_id, status=422, days=-1)["reason_code"] == "REVIEW_DATE_PAST"
    expect(live.request(live.path("retention-holds"), actor="author", method="POST", body=command({})), 422)
    place_hold(live, evidence_id, actor="author", status=403)
    place_hold(live, evidence_id, actor="other_tenant", status=404)
    placed = place_hold(live, evidence_id)
    hold_id = placed["hold_id"]
    assert placed["business_state"] == "Held" and placed["object_id"] == evidence_id
    listed = expect(live.request(live.path("retention-holds"), actor="admin"), 200)
    validate("RetentionHoldList", listed)
    mine = next(h for h in listed["items"] if h["hold_id"] == hold_id)
    assert mine["object_id"] == evidence_id and mine["placed_by"] == principal(live, "privacy")
    assert mine["released_at"] is None and mine["object_type"] == "Evidence"
    # The erasure plan reports the evidence as HELD with the review date.
    created = create_case(live, subject, "ERASURE", evidence_ids=[evidence_id])
    held = [e for e in plan(live, created["object_id"])["entries"] if e["object_id"] == evidence_id]
    assert held and all(e["state"] == "HELD" and e["reason"] == "RETENTION_HOLD" for e in held)
    # Release: never by the person who placed it; by another natural person once; then final.
    assert release_hold(live, hold_id, actor="privacy", status=403)["reason_code"] == "INDEPENDENCE_REQUIRED"
    release_hold(live, str(uuid.uuid4()), status=404)
    released = release_hold(live, hold_id)
    assert released["business_state"] == "Released"
    assert release_hold(live, hold_id, status=409)["reason_code"] == "HOLD_ALREADY_RELEASED"
    after = next(
        h
        for h in expect(live.request(live.path("retention-holds"), actor="privacy"), 200)["items"]
        if h["hold_id"] == hold_id
    )
    assert after["released_by"] == principal(live, "admin") and after["release_reason"] == "Matter closed"
    assert all(
        e["state"] != "HELD"
        for e in plan(live, created["object_id"])["entries"]
        if e["object_id"] == evidence_id
    )
    # A released hold cannot be reopened or rewritten, by anyone.
    with live.db() as c:
        for statement in [
            "UPDATE impact.retention_hold SET released_at=NULL,released_by=NULL,release_reason=NULL WHERE hold_id=%s",
            "UPDATE impact.retention_hold SET authority_reference='changed' WHERE hold_id=%s",
        ]:
            with pytest.raises(psycopg.errors.CheckViolation):
                with c.transaction():
                    c.execute(statement, (hold_id,))
    # Both commands are audited against the held object.
    with live.db() as c:
        audited = {
            r["action_type"]
            for r in c.execute(
                "SELECT action_type FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s",
                (tenant(live), evidence_id),
            ).fetchall()
        }
    assert {"create_retention_holds", "action_retention_holds_release"} <= audited


def test_native_security_privacy_tables_are_fenced_for_the_application_login(connect, live):
    """Natively: the app login sees only its tenant's rows of the new tables, cannot write the
    denial table at all and cannot update or delete the registers; other logins see nothing."""
    tenant_a, tenant_b = tenant(live), live.fixture["tenant_b"]
    c = connect("APP")
    expect(live.request(live.path("access-denials"), actor="author"), 403)
    time.sleep(0.2)
    with live.db() as superuser:
        superuser.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_a,))
        total = superuser.execute(
            "SELECT count(*) AS n FROM impact.access_denial WHERE tenant_id=%s", (tenant_a,)
        ).fetchone()["n"]
    assert total >= 1
    count = "SELECT count(*) FROM impact.access_denial WHERE tenant_id=%s"
    assert query(c, count, (tenant_a,), role="impact_app", tenant=tenant_a) == [(total,)]
    assert query(c, count, (tenant_a,), role="impact_app", tenant=tenant_b) == [(0,)]
    for statement in [
        "INSERT INTO impact.access_denial SELECT * FROM impact.access_denial LIMIT 1",
        "UPDATE impact.access_denial SET occurrences=occurrences+1",
        "DELETE FROM impact.access_denial",
        "UPDATE impact.audit_export_register SET page=page",
        "DELETE FROM impact.audit_export_register",
        "UPDATE impact.retention_policy_binding SET duration_days=duration_days",
        "DELETE FROM impact.retention_policy_binding",
    ]:
        assert "permission denied" in denied(c, statement, role="impact_app", tenant=tenant_a)
    for table in ["audit_export_register", "retention_policy_binding"]:
        assert query(c, "SELECT count(*) FROM impact." + table, role="impact_app", tenant=tenant_b) == [(0,)]
    for login, role in [("PLATFORM", "impact_platform"), ("IDENTITY", "impact_identity")]:
        for table in ["access_denial", "audit_export_register", "retention_policy_binding"]:
            assert "permission denied" in denied(
                connect(login), "SELECT count(*) FROM impact." + table, role=role, tenant=tenant_a
            )
    worker = connect("WORKER")
    assert "permission denied" in denied(
        worker, "SELECT count(*) FROM impact.access_denial", role="impact_worker", tenant=tenant_a
    )
    assert "permission denied" in denied(
        worker,
        "INSERT INTO impact.retention_policy_binding SELECT * FROM impact.retention_policy_binding LIMIT 1",
        role="impact_worker",
        tenant=tenant_a,
    )
