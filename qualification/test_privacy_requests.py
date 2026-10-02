"""Qualification of data-subject requests (v0.25 part B): purpose-bound privacy cases for a member of
the tenant, independent approval by natural person, a bounded access export with a SHA-256 manifest,
and erasure propagation across the member profile, invitations, delivery intents, evidence (with
object-store bytes) and import batches, through impact.privacy_remove_revisions under the
revision_removal_guard trigger, while audit and approved official numbers stay unchanged."""
# ruff: noqa: F811

import hashlib
import json
import os
import shutil
import uuid
from types import SimpleNamespace
from pathlib import Path

import psycopg
import pytest
from cryptography.exceptions import InvalidTag

from impact_api.contracts import validate
from impact_api.delivery import unseal_recipient
from impact_api.identity_profile import email_hash, masked_email
from impact_api.privacy import ERASED_MASK, ERASED_NAME, SECTIONS
from impact_api.store import Context, write
from test_administration import invitation_token, invite, provision_identity, request_as
from test_live_application import cmd, expect
from test_native_roles import connect, denied, query  # noqa: F401

PURPOSE = "DATA_SUBJECT_REQUEST"
CSV = b"household,visited\nH1,yes\n"
NATIVE = os.environ.get("IMPACT_NATIVE_TEST") == "1"


# -- helpers ---------------------------------------------------------------------------------------


def member(live):
    """A fresh member of tenant A (invited by the administrator, accepted), with its e-mail."""
    identity, email = provision_identity(live)
    _, receipt = invite(live, email)
    accepted = expect(
        request_as(
            live,
            identity,
            live.path("invitation-acceptances"),
            method="POST",
            body=cmd({"invitation_token": invitation_token(receipt)}),
        ),
        200,
    )
    with live.db() as c:
        principal = c.execute(
            "SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
            (live.fixture["tenant_a"], identity),
        ).fetchone()["principal_id"]
    return SimpleNamespace(
        identity=identity,
        email=email,
        membership=accepted["object_id"],
        principal=str(principal),
        invitation=receipt["object_id"],
    )


def revoke(live, person):
    row = next(
        m
        for m in expect(live.request(live.path("membership-directory") + "?limit=100", actor="admin"), 200)[
            "items"
        ]
        if m["object_id"] == person.membership
    )
    return expect(
        live.request(
            live.path("memberships", person.membership) + "/actions/revoke",
            actor="admin",
            method="POST",
            body=cmd({"reason": "Left the organisation"}, row["revision_id"]),
        ),
        200,
    )


def directory_item(live, membership):
    items = []
    cursor = None
    while True:
        page = expect(
            live.request(
                live.path("membership-directory") + "?limit=100" + ("&cursor=" + cursor if cursor else ""),
                actor="admin",
            ),
            200,
        )
        items += page["items"]
        cursor = page["next_cursor"]
        if not cursor:
            break
    return next(m for m in items if m["object_id"] == membership)


def case_body(person, request_type="ACCESS", **extra):
    return cmd(
        {
            "request_type": request_type,
            "subject_membership_id": person.membership,
            "reason": "Request received from the member through the privacy mailbox",
            "verification_note": "Confirmed from the member's verified workspace account",
            "purpose": PURPOSE,
            **extra,
        }
    )


def create_case(live, person, request_type="ACCESS", actor="admin", status=201, **extra):
    return expect(
        live.request(
            live.path("privacy-cases"),
            actor=actor,
            method="POST",
            body=case_body(person, request_type, **extra),
        ),
        status,
    )


def case(live, obj, actor="privacy"):
    return expect(
        live.request(live.path("privacy-cases", obj), actor=actor, params={"purpose": PURPOSE}), 200
    )


def plan(live, obj, actor="privacy"):
    return expect(
        live.request(live.path("privacy-cases", obj) + "/plan", actor=actor, params={"purpose": PURPOSE}), 200
    )


def approve(live, obj, actor="privacy", status=200, digest=None):
    current = case(live, obj)
    body = cmd(
        {"purpose": PURPOSE, "plan_sha256": digest or plan(live, obj)["plan_sha256"], "reason": "Checked"},
        current["revision_id"],
    )
    return expect(
        live.request(
            live.path("privacy-cases", obj) + "/actions/approve", actor=actor, method="POST", body=body
        ),
        status,
    )


def execute(live, obj, actor="privacy", status=200, operation=None):
    current = case(live, obj)
    body = cmd(
        {"purpose": PURPOSE, "approved_plan_hash": current["data"]["plan_sha256"]},
        current["revision_id"],
        operation,
    )
    return expect(
        live.request(
            live.path("privacy-cases", obj) + "/actions/execute", actor=actor, method="POST", body=body
        ),
        status,
    )


def export(live, obj, actor="privacy", purpose=PURPOSE, tenant=None):
    return live.request(
        live.path("privacy-cases", obj, tenant) + "/export",
        actor=actor,
        params={"purpose": purpose} if purpose else None,
    )


def grant(live, person, *capabilities):
    """Direct fixture-style grants for a provisioned member (synthetic qualification set-up only)."""
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        scope = c.execute(
            "SELECT scope_id FROM impact.scope_definition WHERE tenant_id=%s AND scope_type='TENANT' LIMIT 1",
            (tenant,),
        ).fetchone()["scope_id"]
        owner = live.fixture["actors"]["owner"]
        ctx = Context(tenant, owner["principal_id"], owner["membership_id"], SimpleNamespace(), 0, 0, [])
        for capability in capabilities:
            write(
                c,
                ctx,
                "Grant",
                {
                    "subject_id": person.principal,
                    "capability": capability,
                    "scope_id": str(scope),
                    "starts_at": "2026-09-01T00:00:00Z",
                    "expires_at": "2027-08-01T00:00:00Z",
                    "issuer_id": owner["principal_id"],
                },
                "Active",
                track_author=False,
            )


def as_member(live, person, path, method="GET", body=None, **kwargs):
    headers = {"Authorization": "Bearer " + live.signed(person.identity)}
    headers.update(kwargs.pop("headers", {}))
    return live.request(path, actor=None, method=method, body=body, headers=headers, **kwargs)


def member_evidence(live, person, content):
    """An evidence file uploaded by the member (CLEAN upload, then an evidence draft citing it)."""
    digest = hashlib.sha256(content).hexdigest()
    status = expect(
        as_member(
            live,
            person,
            live.path("uploads"),
            "POST",
            cmd(
                {
                    "purpose": "EVIDENCE_MEDIA",
                    "content_type": "text/csv",
                    "expected_bytes": len(content),
                    "content_sha256": digest,
                    "mode": "WHOLE",
                    "filename": "household-" + person.email.split("@")[0] + ".csv",
                }
            ),
        ),
        201,
    )
    received = expect(
        as_member(
            live,
            person,
            live.path("uploads", status["upload_id"]) + "/content",
            "PUT",
            content=content,
            headers={"Content-Type": "application/octet-stream"},
        ),
        200,
    )
    done = expect(
        as_member(
            live,
            person,
            live.path("uploads", status["upload_id"]) + "/actions/complete",
            "POST",
            cmd({"content_sha256": digest, "parts": []}, received["revision_id"]),
        ),
        200,
    )
    assert done["state"] == "CLEAN"
    saved = expect(
        as_member(
            live,
            person,
            live.path("evidence"),
            "POST",
            cmd({"upload_id": status["upload_id"], "evidence_type": "CONSENT_FORM", "source": "Field visit"}),
        ),
        201,
    )
    return saved["object_id"], status["upload_id"], digest


def stored(live, digest):
    return Path(live.config["object_store_dir"]) / live.fixture["tenant_a"] / digest[:2] / digest


def official_fingerprint(live):
    """Every calculated result, snapshot and observation revision of tenant A, with its payload hash
    and restriction state: erasure must leave all of them exactly as they were."""
    with live.db() as c:
        rows = c.execute(
            "SELECT revision_id,payload_sha256,restriction_state,md5(payload::text) AS body FROM impact.object_revision "
            "WHERE tenant_id=%s AND object_type IN ('CalculatedResult','Snapshot','Observation') ORDER BY revision_id",
            (live.fixture["tenant_a"],),
        ).fetchall()
    return {
        str(r["revision_id"]): (bytes(r["payload_sha256"]).hex(), r["restriction_state"], r["body"])
        for r in rows
    }


# -- access ----------------------------------------------------------------------------------------


def test_access_export_holds_only_the_subjects_data_with_a_manifest_and_is_mediated(live):
    subject, other = member(live), member(live)
    created = create_case(live, subject)
    item = case(live, created["object_id"])
    validate("PrivacyCase", item)
    assert item["lifecycle_state"] == "Draft" and item["data"]["subject_principal_id"] == subject.principal
    preview = plan(live, created["object_id"])
    validate("PrivacyCasePlan", preview)
    assert preview["entries"] == [] and preview["approved"] is False
    approved = approve(live, created["object_id"])
    assert approved["business_state"] == "Approved"
    done = execute(live, created["object_id"])
    assert done["business_state"] == "Completed"
    final = case(live, created["object_id"])
    assert final["data"]["outcome"] == "COMPLETED" and final["data"]["approved_by"] != final["created_by"]

    response = export(live, created["object_id"])
    assert response.status_code == 200, response.text
    assert response.headers["content-disposition"].startswith("attachment;")
    body = response.content
    digest = hashlib.sha256(body).hexdigest()
    assert response.headers["etag"] == '"' + digest + '"' and final["data"]["package_sha256"] == digest
    package = json.loads(body)
    assert set(package["sections"]) == set(SECTIONS) and package["case_id"] == created["object_id"]
    for name, section in package["sections"].items():
        canonical = json.dumps(section, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        assert package["manifest"][name] == {
            "count": len(section),
            "complete": True,
            "sha256": hashlib.sha256(canonical).hexdigest(),
        }
    me = package["sections"]["subject"][0]
    assert (me["membership_id"], me["principal_id"], me["identity_id"]) == (
        subject.membership,
        subject.principal,
        subject.identity,
    )
    assert me["email_mask"] == masked_email(subject.email) and me["display_name"] == "Test colleague"
    assert [i["invitation_id"] for i in package["sections"]["invitations"]] == [subject.invitation]
    assert package["sections"]["grants"] and all(g["state"] for g in package["sections"]["grants"])
    assert {e["action_type"] for e in package["sections"]["audit_events"]} >= {"accept_invitation"}
    text = body.decode()
    # Nothing of another person: not the other member, nor any fixture actor (the inviter and the
    # grant issuer are deliberately not part of the subject's package).
    for value in [
        other.membership,
        other.principal,
        other.identity,
        other.invitation,
        other.email,
    ]:
        assert value not in text
    for actor in live.fixture["actors"].values():
        for key in ["principal_id", "membership_id", "identity_id"]:
            assert actor[key] not in text
    assert subject.email not in text

    with live.db() as c:
        access = c.execute(
            "SELECT * FROM impact.privacy_export_access WHERE case_id=%s", (created["object_id"],)
        ).fetchall()
        assert len(access) == 1 and bytes(access[0]["content_sha256"]).hex() == digest
        assert access[0]["purpose"] == PURPOSE
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE object_reference=%s AND action_type=%s",
                (created["object_id"], "read_privacy_case_export"),
            ).fetchone()["n"]
            == 1
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.privacy_export_package WHERE case_id=%s",
                (created["object_id"],),
            ).fetchone()["n"]
            == 1
        )
    # Purpose, capability and tenant are each required; every refusal looks the same as absence.
    assert export(live, created["object_id"], purpose=None).status_code == 403
    assert export(live, created["object_id"], purpose="QUALIFICATION").status_code == 404
    assert export(live, created["object_id"], actor="admin").status_code == 404
    assert export(live, created["object_id"], actor="author").status_code == 404
    assert export(live, created["object_id"], actor="other_tenant").status_code == 404
    assert (
        export(live, created["object_id"], actor="other_tenant", tenant=live.fixture["tenant_b"]).status_code
        == 404
    )


def test_case_operations_are_purpose_bound_and_never_authorised_by_a_general_grant(live):
    subject = member(live)
    access = expect(live.request(live.path("me/access"), actor="privacy"), 200)
    assert ["privacy.approve", PURPOSE] in access["purpose_capabilities"]
    assert "privacy.approve" not in access["capabilities"]
    body = case_body(subject)
    body["data"].pop("purpose")
    expect(live.request(live.path("privacy-cases"), actor="admin", method="POST", body=body), 422)
    body = case_body(subject)
    body["data"]["purpose"] = "QUALIFICATION"  # a fixture label, not a privacy purpose
    expect(live.request(live.path("privacy-cases"), actor="admin", method="POST", body=body), 422)
    refused = expect(live.request(live.path("privacy-cases"), actor="privacy"), 403)
    assert refused["reason_code"] == "PURPOSE_REQUIRED"
    expect(live.request(live.path("privacy-cases"), actor="author", params={"purpose": PURPOSE}), 403)
    expect(
        live.request(live.path("privacy-cases"), actor="author", method="POST", body=case_body(subject)), 403
    )
    created = create_case(live, subject)
    listed = expect(
        live.request(live.path("privacy-cases"), actor="privacy", params={"purpose": PURPOSE}), 200
    )
    validate("PrivacyCaseList", listed)
    assert created["object_id"] in {c["object_id"] for c in listed["items"]}
    for actor in ["author", "reviewer", "other_tenant"]:
        expect(
            live.request(
                live.path("privacy-cases", created["object_id"]), actor=actor, params={"purpose": PURPOSE}
            ),
            404,
        )
    revoked = live.request(
        live.path("privacy-cases", created["object_id"]), actor="revoked", params={"purpose": PURPOSE}
    )
    assert revoked.status_code in {401, 404}
    # The general purpose-less authorisation path of every other route refuses privacy routes too.
    expect(
        live.request(
            live.path("privacy-cases", created["object_id"]) + "/actions/reject",
            actor="privacy",
            method="POST",
            body=cmd({"purpose": PURPOSE}, created["revision_id"]),
        ),
        404,
    )
    # A subject outside the tenant is refused.
    stranger = SimpleNamespace(membership=live.fixture["actors"]["other_tenant"]["membership_id"])
    refused = create_case(live, stranger, status=422)
    assert refused["reason_code"] == "SUBJECT_NOT_A_MEMBER"


def test_case_approval_requires_an_independent_natural_person(live):
    subject = member(live)
    own = create_case(live, subject, actor="privacy")
    refused = approve(live, own["object_id"], status=403)
    assert refused["reason_code"] == "INDEPENDENCE_REQUIRED"
    # The privacy officer cannot approve a request about themselves either.
    officer = SimpleNamespace(membership=live.fixture["actors"]["privacy"]["membership_id"])
    about_me = create_case(live, officer)
    assert approve(live, about_me["object_id"], status=403)["reason_code"] == "INDEPENDENCE_REQUIRED"
    # Intake roles cannot approve or execute at all.
    created = create_case(live, subject)
    assert approve(live, created["object_id"], actor="admin", status=404)
    approve(live, created["object_id"])
    execute(live, created["object_id"], actor="admin", status=404)


def test_exact_retry_changed_payload_stale_revision_and_changed_plan(live):
    subject = member(live)
    body = case_body(subject)
    first = expect(live.request(live.path("privacy-cases"), actor="admin", method="POST", body=body), 201)
    again = expect(live.request(live.path("privacy-cases"), actor="admin", method="POST", body=body), 201)
    assert again == first
    changed = {**body, "data": {**body["data"], "reason": "Another reason"}}
    expect(live.request(live.path("privacy-cases"), actor="admin", method="POST", body=changed), 409)
    patched = expect(
        live.request(
            live.path("privacy-cases", first["object_id"]),
            actor="admin",
            method="PATCH",
            body=cmd({"purpose": PURPOSE, "deadline": "2026-11-01T00:00:00Z"}, first["revision_id"]),
        ),
        200,
    )
    stale = live.request(
        live.path("privacy-cases", first["object_id"]),
        actor="admin",
        method="PATCH",
        body=cmd({"purpose": PURPOSE, "reason": "Stale"}, first["revision_id"]),
    )
    assert stale.status_code == 409 and stale.json()["code"] == "CONFLICT_VERSION"
    refused = approve(live, first["object_id"], status=409, digest="0" * 64)
    assert refused["reason_code"] == "PLAN_CHANGED"
    with live.db() as c:
        revisions = c.execute(
            "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s", (first["object_id"],)
        ).fetchone()["n"]
        receipts = c.execute(
            "SELECT count(*) AS n FROM impact.operation_receipt WHERE command_type='create_privacy_cases' "
            "AND operation_id=%s",
            (body["operation_id"],),
        ).fetchone()["n"]
        audits = c.execute(
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE object_reference=%s",
            (first["object_id"],),
        ).fetchone()["n"]
    assert (revisions, receipts, audits) == (2, 1, 2) and patched["object_id"] == first["object_id"]
    # A completed case cannot be executed or approved again.
    approve(live, first["object_id"])
    current = case(live, first["object_id"])
    body = cmd(
        {"purpose": PURPOSE, "approved_plan_hash": current["data"]["plan_sha256"]}, current["revision_id"]
    )
    path = live.path("privacy-cases", first["object_id"]) + "/actions/execute"
    done = expect(live.request(path, actor="privacy", method="POST", body=body), 200)
    assert expect(live.request(path, actor="privacy", method="POST", body=body), 200) == done
    assert execute(live, first["object_id"], status=409)["code"] == "INVALID_STATE"


# -- erasure ---------------------------------------------------------------------------------------


def test_erasure_reaches_every_store_keeps_audit_and_never_alters_official_numbers(live):
    subject = member(live)
    grant(live, subject, "upload.create", "upload.write", "uploads.read")
    content = CSV + ("#" + str(uuid.uuid4()) + "\n").encode()
    evidence_id, upload_id, digest = member_evidence(live, subject, content)
    assert stored(live, digest).is_file()
    refused = create_case(live, subject, "ERASURE", evidence_ids=[evidence_id])
    assert approve(live, refused["object_id"], status=409)["reason_code"] == "SUBJECT_STILL_ACTIVE"
    revoke(live, subject)
    created = create_case(live, subject, "ERASURE", evidence_ids=[evidence_id])
    before = official_fingerprint(live)
    preview = plan(live, created["object_id"])
    stores = {(e["store"], e["object_id"]) for e in preview["entries"]}
    assert stores == {
        ("MEMBER_PROFILE", subject.membership),
        ("INVITATION_REGISTER", subject.invitation),
        ("DATABASE", subject.invitation),
        ("OUTBOX", subject.invitation),
        ("PROJECTION", evidence_id),
        ("DATABASE", evidence_id),
        ("OBJECT_STORE", evidence_id),
    }
    assert all(e["state"] == "APPROVED" for e in preview["entries"])
    approve(live, created["object_id"])
    assert plan(live, created["object_id"])["approved"] is True
    receipt = execute(live, created["object_id"])
    final = case(live, created["object_id"])
    assert final["lifecycle_state"] == "Completed" and final["data"]["outcome"] == "COMPLETED", final
    assert receipt["object_id"] == created["object_id"]

    # Membership directory and invitation listing: the tombstone, never the person.
    item = directory_item(live, subject.membership)
    assert item["display_name"] == ERASED_NAME and item["email_mask"] is None
    invitations = expect(live.request(live.path("member-invitations") + "?limit=100", actor="admin"), 200)[
        "items"
    ]
    tombstone = next(i for i in invitations if i["object_id"] == subject.invitation)
    assert tombstone["email_mask"] == ERASED_MASK
    # Evidence: no read, no download, no bytes.
    expect(live.request(live.path("evidence", evidence_id)), 404)
    assert live.request(live.path("evidence", evidence_id) + "/content").status_code == 404
    assert not stored(live, digest).exists()
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        # No revision payload of the subject's objects still yields the mask, and no revision of the
        # tenant yields the address or the file name (masks are not unique between people).
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=ANY(%s::uuid[]) "
                "AND payload::text LIKE %s",
                (
                    tenant,
                    [subject.invitation, subject.membership, evidence_id],
                    "%" + masked_email(subject.email) + "%",
                ),
            ).fetchone()["n"]
            == 0
        )
        for needle in [subject.email, "household-" + subject.email.split("@")[0]]:
            assert (
                c.execute(
                    "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND payload::text LIKE %s",
                    (tenant, "%" + needle + "%"),
                ).fetchone()["n"]
                == 0
            ), needle
        profile = c.execute(
            "SELECT * FROM impact.member_profile WHERE tenant_id=%s AND membership_id=%s",
            (tenant, subject.membership),
        ).fetchone()
        assert (profile["display_name"], profile["email_mask"]) == (ERASED_NAME, None)
        invitation = c.execute(
            "SELECT * FROM impact.member_invitation WHERE invitation_id=%s", (subject.invitation,)
        ).fetchone()
        assert invitation["intended_subject"] is None
        assert bytes(invitation["intended_email_hash"]) != email_hash(subject.email)
        upload = c.execute("SELECT * FROM impact.upload_session WHERE upload_id=%s", (upload_id,)).fetchone()
        assert upload["filename"] is None
        blob = c.execute("SELECT * FROM impact.file_blob WHERE blob_id=%s", (upload["blob_id"],)).fetchone()
        assert blob["purged_at"] and str(blob["purge_case_id"]) == created["object_id"]
        projection = c.execute(
            "SELECT * FROM impact.evidence_current WHERE object_id=%s", (evidence_id,)
        ).fetchone()
        assert projection["filename"] is None and projection["source"] is None
        removed = c.execute(
            "SELECT object_id,count(*) FILTER (WHERE restriction_state='REMOVED') AS removed,"
            "count(*) FILTER (WHERE restriction_state='AVAILABLE') AS kept,"
            "count(*) FILTER (WHERE restriction_state='REMOVED' AND payload IS NOT NULL) AS leaked "
            "FROM impact.object_revision WHERE object_id=ANY(%s::uuid[]) GROUP BY object_id",
            ([subject.invitation, evidence_id],),
        ).fetchall()
        counts = {str(r["object_id"]): (r["removed"] >= 1, r["kept"], r["leaked"]) for r in removed}
        # The invitation keeps exactly one tombstone revision; the evidence keeps none.
        assert counts == {subject.invitation: (True, 1, 0), evidence_id: (True, 0, 0)}
        ledger = c.execute(
            "SELECT object_id,disposition FROM impact.deletion_ledger WHERE case_id=%s ORDER BY object_id",
            (created["object_id"],),
        ).fetchall()
        assert {str(r["object_id"]) for r in ledger} == {subject.invitation, evidence_id}
        actions = c.execute(
            "SELECT store,state FROM impact.privacy_store_action WHERE case_id=%s", (created["object_id"],)
        ).fetchall()
        assert len(actions) == 7 and {a["state"] for a in actions} == {"COMPLETED"}
        deliveries = c.execute(
            "SELECT * FROM impact.outbox_delivery WHERE reference_id=%s AND channel='EMAIL'",
            (subject.invitation,),
        ).fetchall()
        assert deliveries and all(d["recipient_redacted_at"] for d in deliveries)
        assert all(d["state"] in {"SENT", "DEAD", "SUPERSEDED"} for d in deliveries)
        for d in deliveries:
            with pytest.raises(InvalidTag):
                unseal_recipient(
                    live.config["delivery_secret"],
                    tenant,
                    d["template"],
                    d["reference_id"],
                    d["recipient_sealed"],
                )
        events = {
            r["action_type"]
            for r in c.execute(
                "SELECT action_type FROM impact.audit_event_current WHERE object_reference=%s",
                (created["object_id"],),
            ).fetchall()
        }
        assert {
            "create_privacy_cases",
            "action_privacy_cases_approve",
            "action_privacy_cases_execute",
            "privacy.object_store_purge",
        } <= events
        # The subject's principal and membership stay (pseudonymous keys for audit and review).
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.tenant_principal WHERE principal_id=%s",
                (subject.principal,),
            ).fetchone()["n"]
            == 1
        )
    assert official_fingerprint(live) == before
    # A second case finds nothing left to erase for this member.
    again = create_case(live, subject, "ERASURE")
    assert plan(live, again["object_id"])["entries"] == []


def test_erasure_reports_held_items_and_a_failed_object_store_deletion_until_retried(live):
    subject = member(live)
    grant(live, subject, "upload.create", "upload.write", "uploads.read")
    held_id, _, held_digest = member_evidence(
        live, subject, CSV + b"#held-" + uuid.uuid4().hex.encode() + b"\n"
    )
    failing_id, _, failing_digest = member_evidence(
        live, subject, CSV + b"#fail-" + uuid.uuid4().hex.encode() + b"\n"
    )
    revoke(live, subject)
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute(
            "INSERT INTO impact.retention_hold(tenant_id,hold_id,object_id,authority_reference,review_at) "
            "VALUES(%s,%s,%s,'Synthetic legal hold',now()+interval '30 days')",
            (tenant, str(uuid.uuid4()), held_id),
        )
    created = create_case(live, subject, "ERASURE", evidence_ids=[held_id, failing_id])
    preview = plan(live, created["object_id"])
    held = [e for e in preview["entries"] if e["object_id"] == held_id]
    assert held and all(e["state"] == "HELD" and e["reason"] == "RETENTION_HOLD" for e in held)
    assert all(e["hold_review_at"] for e in held)
    approve(live, created["object_id"])
    # The failing object: a directory where the file was, so the store cannot unlink it.
    target = stored(live, failing_digest)
    target.unlink()
    target.mkdir()
    try:
        execute(live, created["object_id"])
        partial = case(live, created["object_id"])
        assert partial["lifecycle_state"] == "PartiallyCompleted"
        assert partial["data"]["outcome"] == "PARTIALLY_COMPLETED"
        assert [h["object_id"] for h in partial["data"]["manifest"]["held"]] == [held_id] * len(held)
        result = partial["data"]["manifest"]["object_store_results"][failing_id]
        assert result["state"] == "FAILED" and result["error_class"].startswith("OBJECT_DELETE_")
    finally:
        shutil.rmtree(target)
    # The held evidence is untouched and still served; the failing one is no longer readable.
    expect(live.request(live.path("evidence", held_id)), 200)
    assert stored(live, held_digest).is_file()
    expect(live.request(live.path("evidence", failing_id)), 404)
    retried = execute(live, created["object_id"])
    assert retried["business_state"] == "PartiallyCompleted"  # the original state of this retry's receipt
    final = case(live, created["object_id"])
    assert final["lifecycle_state"] == "PartiallyCompleted"  # still partial: the hold remains
    assert final["data"]["manifest"]["object_store_results"][failing_id]["state"] == "COMPLETED"
    with live.db() as c:
        states = {
            (str(r["object_id"]), r["store"]): r["state"]
            for r in c.execute(
                "SELECT object_id,store,state FROM impact.privacy_store_action WHERE case_id=%s",
                (created["object_id"],),
            ).fetchall()
        }
    assert states[(failing_id, "OBJECT_STORE")] == "COMPLETED"
    assert states[(held_id, "DATABASE")] == "HELD"
    assert execute(live, created["object_id"], status=409)["reason_code"] == "NOTHING_TO_RETRY"


def test_erasure_of_a_named_import_batch_removes_its_raw_content(live):
    from test_import import HOUSEHOLDS, batch_data
    from test_forms import planned

    indicator, period, _ = planned(live, **HOUSEHOLDS)
    subject = member(live)
    content = "district,households\nD-" + subject.email.split("@")[0] + ",3\n"
    batch = expect(
        as_member(live, subject, live.path("imports"), "POST", cmd(batch_data(indicator, period, content))),
        201,
    )
    head = expect(as_member(live, subject, live.path("imports", batch["object_id"])), 200)
    expect(
        as_member(
            live,
            subject,
            live.path("imports", batch["object_id"]) + "/actions/cancel",
            "POST",
            cmd({"reason": "Wrong file"}, head["revision_id"]),
        ),
        200,
    )
    revoke(live, subject)
    # Only the subject's own batches can be named.
    other = expect(
        live.request(live.path("imports"), method="POST", body=cmd(batch_data(indicator, period, content))),
        201,
    )
    assert (
        create_case(live, subject, "ERASURE", import_ids=[other["object_id"]], status=422)["reason_code"]
        == "NOT_SUBJECT_DATA"
    )
    created = create_case(live, subject, "ERASURE", import_ids=[batch["object_id"]])
    approve(live, created["object_id"])
    execute(live, created["object_id"])
    assert case(live, created["object_id"])["lifecycle_state"] == "Completed"
    expect(live.request(live.path("imports", batch["object_id"])), 404)
    with live.db() as c:
        row = c.execute(
            "SELECT * FROM impact.import_job_current WHERE object_id=%s", (batch["object_id"],)
        ).fetchone()
        assert row["content"] is None and row["preview"] is None and row["file_name"] is None
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s AND (payload IS NOT NULL "
                "OR restriction_state<>'REMOVED')",
                (batch["object_id"],),
            ).fetchone()["n"]
            == 0
        )


# -- database boundaries ---------------------------------------------------------------------------


def test_revision_removal_is_reachable_only_through_an_approved_executing_plan(live):
    tenant = live.fixture["tenant_a"]
    observation = live.records["observation_1"]["object_id"]
    statements = [
        # The application has no UPDATE privilege on revisions at all.
        (
            "impact_app",
            "UPDATE impact.object_revision SET payload=NULL,restriction_state='REMOVED' WHERE object_id='"
            + observation
            + "'",
        ),
        # The definers refuse without an approved erasure case and an EXECUTING plan entry.
        (
            "impact_app",
            "SELECT impact.privacy_remove_revisions(gen_random_uuid(),'" + observation + "',NULL)",
        ),
        ("impact_app", "SELECT impact.privacy_supersede_deliveries(gen_random_uuid(),gen_random_uuid())"),
        ("impact_app", "SELECT impact.privacy_redact_uploads(gen_random_uuid(),gen_random_uuid())"),
        # Retention definers are the worker's; privacy definers the application's.
        ("impact_app", "SELECT * FROM impact.retention_purge_receipts(1)"),
        ("impact_app", "SELECT impact.worker_schedule_retention(gen_random_uuid(),3600)"),
        ("impact_worker", "SELECT impact.privacy_remove_revisions(gen_random_uuid(),gen_random_uuid(),NULL)"),
        ("impact_worker", "SELECT impact.privacy_require_case(gen_random_uuid())"),
        ("impact_app", "SELECT impact.privacy_require_case(gen_random_uuid())"),
    ]
    for role, statement in statements:
        with live.db() as c:
            c.execute("SET LOCAL ROLE " + role)
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(statement)
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        # Even the executor marker set by hand does not let the application reach the trigger.
        c.execute("SELECT set_config('impact.privacy_executor','privacy_remove_revisions',true)")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute("UPDATE impact.object_revision SET payload=NULL WHERE object_id=%s", (observation,))
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s AND restriction_state='AVAILABLE'",
                (observation,),
            ).fetchone()["n"]
            >= 1
        )


def test_privacy_registers_are_insert_only_for_the_application(live):
    for table, privileges in {
        "privacy_export_package": {"SELECT", "INSERT"},
        "privacy_export_access": {"SELECT", "INSERT"},
        "retention_sweep": {"SELECT"},
        "retention_proof": {"SELECT"},
    }.items():
        with live.db() as c:
            held = {
                p
                for p in ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE"]
                if c.execute(
                    "SELECT has_table_privilege('impact_app',%s,%s) AS h", ("impact." + table, p)
                ).fetchone()["h"]
            }
        assert held == privileges, (table, held)


@pytest.mark.skipif(not NATIVE, reason="row-level security on the provisioned login roles")
def test_native_privacy_tables_are_fenced_for_the_application_login(connect, live):
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    c = connect("APP")
    subject = member(live)
    created = create_case(live, subject)
    approve(live, created["object_id"])
    execute(live, created["object_id"])
    assert export(live, created["object_id"]).status_code == 200
    for table in ["privacy_export_package", "privacy_export_access"]:
        count = "SELECT count(*) FROM impact." + table + " WHERE case_id=%s"
        assert query(c, count, (created["object_id"],), role="impact_app", tenant=tenant_a) == [(1,)]
        assert query(c, count, (created["object_id"],), role="impact_app", tenant=tenant_b) == [(0,)]
        for statement in [
            "UPDATE impact." + table + " SET tenant_id=tenant_id",
            "DELETE FROM impact." + table,
        ]:
            assert "permission denied" in denied(c, statement, role="impact_app", tenant=tenant_a)
    for statement in [
        "UPDATE impact.object_revision SET payload=NULL",
        "UPDATE impact.retention_proof SET affected_count=0",
        "DELETE FROM impact.deletion_ledger",
    ]:
        assert "permission denied" in denied(c, statement, role="impact_app", tenant=tenant_a)
    for login, role in [("PLATFORM", "impact_platform"), ("IDENTITY", "impact_identity")]:
        assert "permission denied" in denied(
            connect(login), "SELECT count(*) FROM impact.privacy_export_package", role=role, tenant=tenant_a
        )
