"""Qualification of the object store and evidence attachments (v0.22): upload sessions with an
allow-list, magic-byte sniffing, exact size and digest, a scanning verdict before anything becomes
downloadable, evidence revisions that cite only CLEAN uploads, insert-only attachments to exact
observation and calculated-result revisions, and mediated, audited downloads."""
# ruff: noqa: F811

import hashlib
from pathlib import Path
import uuid
from types import SimpleNamespace

import psycopg
import pytest
from impact_api.content_safety import EICAR
from impact_api.store import Context, hash_data, write
from test_live_application import cmd, draft, expect
from test_native_roles import connect, denied, query  # noqa: F401

CSV = b"household,visited\nH1,yes\nH2,no\n"
PDF = b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n"
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + bytes(17)


def unique(content):
    """Distinct bytes per test (blobs are content-addressed per tenant)."""
    return content + ("#" + str(uuid.uuid4()) + "\n").encode()


def declare(live, content, media="text/csv", name="visits.csv", actor="author", **override):
    body = cmd(
        {
            "purpose": "EVIDENCE_MEDIA",
            "content_type": media,
            "expected_bytes": len(content),
            "content_sha256": hashlib.sha256(content).hexdigest(),
            "mode": "WHOLE",
            "filename": name,
            **override,
        }
    )
    return live.request(live.path("uploads"), actor=actor, method="POST", body=body), body


def put(live, upload_id, content, actor="author", tenant=None):
    return live.request(
        live.path("uploads", upload_id, tenant) + "/content",
        actor=actor,
        method="PUT",
        content=content,
        headers={"Content-Type": "application/octet-stream"},
    )


def complete(live, status, actor="author", operation=None, digest=None, revision=None):
    body = cmd(
        {"content_sha256": digest or status["content_sha256"], "parts": []},
        revision or status["revision_id"],
        operation=operation,
    )
    response = live.request(
        live.path("uploads", status["upload_id"]) + "/actions/complete", actor=actor, method="POST", body=body
    )
    return response, body


def uploaded(live, content, media="text/csv", name="visits.csv", actor="author"):
    status = expect(declare(live, content, media, name, actor)[0], 201)
    assert status["state"] == "OPEN" and status["content_received"] is False
    received = expect(put(live, status["upload_id"], content, actor), 200)
    assert received["content_received"] is True and received["state"] == "OPEN"
    return expect(complete(live, received, actor)[0], 200)


def evidence(live, upload_id, actor="author", **extra):
    data = {"upload_id": upload_id, "evidence_type": "ATTENDANCE_SHEET", "source": "Field visit", **extra}
    return live.request(live.path("evidence"), actor=actor, method="POST", body=cmd(data))


def attach(live, item, kind, target, actor="author", revision=None, reason="Signed attendance sheet"):
    return live.request(
        live.path("evidence", item["object_id"]) + "/actions/attach",
        actor=actor,
        method="POST",
        body=cmd(
            {
                "target_kind": kind,
                "target_id": target["object_id"],
                "target_revision": revision or target["revision_id"],
                "reason": reason,
            },
            item["revision_id"],
        ),
    )


def download(live, evidence_id, actor="author", revision=None, tenant=None):
    return live.request(
        live.path("evidence", evidence_id, tenant) + "/content",
        actor=actor,
        params={"revision": revision} if revision else None,
    )


def counts(live, sql, *args):
    with live.db() as c:
        return c.execute(sql, args).fetchone()["n"]


def test_upload_scan_evidence_version_citation_and_mediated_download(live):
    """FT-EVD-001: link version 1 of evidence to an observation, upload version 2, and the
    observation still cites version 1; both versions download only through the API."""
    first, second = unique(CSV), unique(PDF)
    status = uploaded(live, first)
    assert status["state"] == "CLEAN" and status["scan_state"] == "CLEAN"
    assert status["filename"] == "visits.csv" and status["content_type"] == "text/csv"
    saved = expect(evidence(live, status["upload_id"]), 201)
    item = expect(live.request(live.path("evidence", saved["object_id"])), 200)
    assert item["lifecycle_state"] == "Draft"
    assert item["data"]["integrity_sha256"] == hashlib.sha256(first).hexdigest()
    assert item["data"]["scan_state"] == "CLEAN" and item["data"]["verification_state"] == "UNVERIFIED"
    assert item["data"]["filename"] == "visits.csv" and item["data"]["byte_size"] == len(first)

    observation = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    receipt = expect(attach(live, item, "Observation", observation), 200)
    assert receipt["object_id"] == item["object_id"] and receipt["revision_id"] == item["revision_id"]
    # The observation itself is unchanged: no new revision.
    assert (
        expect(live.request(live.path("observations", observation["object_id"])), 200)["revision_id"]
        == (observation["revision_id"])
    )

    # Version 2: a new upload replaces the file through a governed draft edit.
    v2 = uploaded(live, second, "application/pdf", "attendance.pdf")
    patched = expect(
        live.request(
            live.path("evidence", item["object_id"]),
            method="PATCH",
            body=cmd({"upload_id": v2["upload_id"]}, item["revision_id"]),
        ),
        200,
    )
    head = expect(live.request(live.path("evidence", item["object_id"])), 200)
    assert head["revision_id"] == patched["revision_id"] != item["revision_id"]
    assert head["data"]["media_type"] == "application/pdf"

    cited = expect(live.request(live.path("observations", observation["object_id"]) + "/evidence"), 200)
    [link] = cited["items"]
    assert link["evidence_revision"] == item["revision_id"] and link["evidence_revision_number"] == 1
    assert link["evidence_head_revision"] == head["revision_id"] and link["target_is_current"] is True
    assert link["filename"] == "visits.csv" and link["downloadable"] is True

    old = download(live, item["object_id"], revision=item["revision_id"])
    assert old.status_code == 200 and old.content == first
    assert old.headers["content-type"] == "text/csv; charset=utf-8"
    assert old.headers["content-disposition"].startswith('attachment; filename="visits.csv"')
    assert old.headers["x-content-type-options"] == "nosniff"
    assert old.headers["cache-control"] == "no-store"
    assert "sandbox" in old.headers["content-security-policy"]
    new = download(live, item["object_id"], actor="reviewer")
    assert new.status_code == 200 and new.content == second
    assert new.headers["content-type"] == "application/pdf"

    # One access row and one audit event per mediated response, naming the exact revision.
    with live.db() as c:
        rows = c.execute(
            "SELECT evidence_revision,principal_id,correlation_id FROM impact.evidence_access WHERE evidence_id=%s ORDER BY accessed_at",
            (item["object_id"],),
        ).fetchall()
        audited = c.execute(
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE action_type='read_evidence_content' AND object_reference=%s",
            (item["object_id"],),
        ).fetchone()["n"]
    assert [str(r["evidence_revision"]) for r in rows] == [item["revision_id"], head["revision_id"]]
    assert str(rows[0]["correlation_id"]) == old.headers["x-correlation-id"]
    assert str(rows[1]["principal_id"]) == live.fixture["actors"]["reviewer"]["principal_id"]
    assert audited == 2

    # A revision of another object is not a version of this evidence.
    assert download(live, item["object_id"], revision=observation["revision_id"]).status_code == 404


def test_attach_to_calculated_result_and_attachment_rules(live):
    status = uploaded(live, unique(CSV))
    item = expect(
        live.request(live.path("evidence", expect(evidence(live, status["upload_id"]), 201)["object_id"])),
        200,
    )
    result = expect(live.request(live.path("calculated-results")), 200)["items"][0]
    body_before = counts(
        live, "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s", result["object_id"]
    )
    expect(attach(live, item, "CalculatedResult", result), 200)
    assert (
        counts(
            live, "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s", result["object_id"]
        )
        == body_before
    )
    listed = expect(live.request(live.path("calculated-results", result["object_id"]) + "/evidence"), 200)
    assert item["revision_id"] in [x["evidence_revision"] for x in listed["items"]]

    duplicate = expect(attach(live, item, "CalculatedResult", result), 409)
    assert duplicate["reason_code"] == "EVIDENCE_ALREADY_ATTACHED"
    observation = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    stale = expect(attach(live, item, "Observation", observation, revision=str(uuid.uuid4())), 409)
    assert stale["reason_code"] == "TARGET_REVISION_CHANGED"
    wrong_kind = attach(live, item, "Observation", result)
    assert wrong_kind.status_code == 404
    old_evidence = {**item, "revision_id": str(uuid.uuid4())}
    expect(attach(live, old_evidence, "Observation", observation), 409)

    # Exact retry returns the same receipt; the same identifier with another payload conflicts.
    body = cmd(
        {
            "target_kind": "Observation",
            "target_id": observation["object_id"],
            "target_revision": observation["revision_id"],
            "reason": "Photo of the register",
        },
        item["revision_id"],
    )
    path = live.path("evidence", item["object_id"]) + "/actions/attach"
    one = expect(live.request(path, method="POST", body=body), 200)
    assert expect(live.request(path, method="POST", body=body), 200) == one
    changed = {**body, "data": {**body["data"], "reason": "Something else"}}
    assert expect(live.request(path, method="POST", body=changed), 409)["code"] == "CONFLICT_OPERATION"
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.evidence_attachment WHERE evidence_revision=%s AND target_id=%s",
                (item["revision_id"], observation["object_id"]),
            ).fetchone()["n"]
            == 1
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE operation_id=%s",
                (body["operation_id"],),
            ).fetchone()["n"]
            == 1
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE correlation_id IN (SELECT (outcome->>'correlation_id')::uuid FROM impact.operation_receipt WHERE operation_id=%s)",
                (body["operation_id"],),
            ).fetchone()["n"]
            == 1
        )


def test_allow_list_names_and_declared_size_are_refused_before_any_byte(live):
    for media, name in [("application/zip", "a.zip"), ("application/x-msdownload", "setup.exe")]:
        refused = expect(declare(live, CSV, media, name)[0], 422)
        assert refused["code"] == "VALIDATION_FAILED"
    for media, name, reason in [
        ("application/pdf", "report.pdf.exe", "FILE_EXTENSION_MISMATCH"),
        ("application/pdf", "photo.png", "FILE_EXTENSION_MISMATCH"),
        ("text/plain", "../../etc/passwd.txt", "FILENAME_INVALID"),
    ]:
        assert expect(declare(live, CSV, media, name)[0], 422)["reason_code"] == reason
    assert expect(declare(live, CSV, expected_bytes=25_000_001)[0], 422)["code"] == "VALIDATION_FAILED"
    # Server-owned upload fields cannot be declared.
    assert expect(declare(live, CSV, state="CLEAN")[0], 422)["code"] == "VALIDATION_FAILED"
    assert expect(declare(live, CSV, purpose="SOURCE_IMPORT")[0], 422)["code"] == "VALIDATION_FAILED"


def test_magic_bytes_size_and_digest_are_checked(live):
    def opened(content, media="image/png", name="photo.png"):
        return expect(declare(live, content, media, name)[0], 201)

    pdf_as_png = unique(PDF)
    upload = opened(pdf_as_png)
    assert expect(put(live, upload["upload_id"], pdf_as_png), 422)["reason_code"] == "CONTENT_TYPE_MISMATCH"
    executable = b"MZ\x90\x00" + bytes(60)
    upload = opened(executable, "application/pdf", "report.pdf")
    assert expect(put(live, upload["upload_id"], executable), 422)["reason_code"] == "EXECUTABLE_REFUSED"
    active = unique(PDF.replace(b"/Type /Catalog", b"/Type /Catalog /OpenAction << /S /JavaScript >>"))
    upload = opened(active, "application/pdf", "report.pdf")
    assert expect(put(live, upload["upload_id"], active), 422)["reason_code"] == "ACTIVE_CONTENT_REFUSED"
    markup = b"<html><script>alert(1)</script></html>"
    upload = opened(markup, "text/plain", "notes.txt")
    assert expect(put(live, upload["upload_id"], markup), 422)["reason_code"] == "CONTENT_TYPE_MISMATCH"

    content = unique(PNG)
    upload = opened(content)
    assert expect(put(live, upload["upload_id"], content[:-1]), 422)["reason_code"] == "SIZE_MISMATCH"
    assert expect(put(live, upload["upload_id"], content + b"x"), 413)["reason_code"] == "FILE_TOO_LARGE"
    tampered = content[:-1] + b"\x01"
    assert expect(put(live, upload["upload_id"], tampered), 422)["reason_code"] == "HASH_MISMATCH"
    wrong_type = live.request(
        live.path("uploads", upload["upload_id"]) + "/content",
        method="PUT",
        content=content,
        headers={"Content-Type": "image/png"},
    )
    assert wrong_type.status_code == 415
    # Nothing was accepted: still open, no blob, and completion needs the content.
    still = expect(live.request(live.path("uploads", upload["upload_id"])), 200)
    assert still["state"] == "OPEN" and still["content_received"] is False
    assert expect(complete(live, still)[0], 409)["reason_code"] == "CONTENT_REQUIRED"
    expect(put(live, upload["upload_id"], content), 200)
    still = expect(live.request(live.path("uploads", upload["upload_id"])), 200)
    wrong = "0" * 64
    assert expect(complete(live, still, digest=wrong)[0], 422)["reason_code"] == "HASH_MISMATCH"
    assert expect(complete(live, still, revision=str(uuid.uuid4()))[0], 409)["code"] == "CONFLICT_VERSION"
    with live.db() as c:
        for rejected in [pdf_as_png, executable, markup]:
            assert not c.execute(
                "SELECT 1 FROM impact.file_blob WHERE sha256=%s", (hashlib.sha256(rejected).digest(),)
            ).fetchone()


def test_raw_upload_route_alone_exceeds_the_json_cap(live):
    big = b"a,b\n" + b"1,2\n" * 100_000  # 400 KB, above the 256 KiB JSON cap
    status = uploaded(live, unique(big), "text/csv", "large.csv")
    assert status["state"] == "CLEAN" and status["expected_bytes"] > 262144
    oversized = live.request(
        live.path("observations"),
        method="POST",
        content=b'{"x":"' + b"a" * 300_000 + b'"}',
        headers={"Content-Type": "application/json"},
    )
    assert oversized.status_code == 413


def test_eicar_is_infected_rejected_and_never_downloadable(live):
    content = unique(EICAR + b"\n")
    status = uploaded(live, content, "text/plain", "eicar.txt")
    assert status["state"] == "REJECTED" and status["scan_state"] == "INFECTED"
    assert status["scan_detail"] == "EICAR_TEST_SIGNATURE"
    refused = expect(evidence(live, status["upload_id"]), 409)
    assert refused["reason_code"] == "UPLOAD_NOT_CLEAN"
    # Even an evidence revision forged below the API that names the infected upload never serves it.
    actor = live.fixture["actors"]["author"]
    ctx = Context(
        actor["tenant_id"],
        actor["principal_id"],
        actor["membership_id"],
        SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
        0,
        0,
        [],
    )
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (actor["tenant_id"],))
        forged = write(
            c,
            ctx,
            "Evidence",
            {"upload_id": status["upload_id"], "evidence_type": "FORGED", "scan_state": "CLEAN"},
            track_author=False,
        )
        blob = c.execute(
            "SELECT b.blob_id,b.scanner FROM impact.upload_session u JOIN impact.file_blob b ON b.tenant_id=u.tenant_id AND b.blob_id=u.blob_id WHERE u.upload_id=%s",
            (status["upload_id"],),
        ).fetchone()
    assert blob["scanner"] == "eicar-signature/1"
    assert download(live, forged["object_id"]).status_code == 404
    # A verdict is final: no role can turn INFECTED into CLEAN, nor re-point a blob's digest.
    for statement in [
        "UPDATE impact.file_blob SET scan_state='CLEAN' WHERE blob_id=%s",
        "UPDATE impact.file_blob SET sha256=sha256 || ''::bytea, bytes=bytes+1 WHERE blob_id=%s",
    ]:
        with pytest.raises(psycopg.errors.CheckViolation):
            with live.db() as c:
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (actor["tenant_id"],))
                c.execute(statement, (blob["blob_id"],))


def test_finalize_and_content_retries_are_idempotent(live):
    content = unique(CSV)
    response, body = declare(live, content)
    created = expect(response, 201)
    again = live.request(live.path("uploads"), method="POST", body=body)
    assert expect(again, 201) == created
    changed = {**body, "data": {**body["data"], "filename": "other.csv"}}
    assert (
        expect(live.request(live.path("uploads"), method="POST", body=changed), 409)["code"]
        == "CONFLICT_OPERATION"
    )
    first = expect(put(live, created["upload_id"], content), 200)
    assert expect(put(live, created["upload_id"], content), 200) == first
    response, body = complete(live, first)
    done = expect(response, 200)
    replay = live.request(
        live.path("uploads", created["upload_id"]) + "/actions/complete", method="POST", body=body
    )
    assert expect(replay, 200) == done and done["state"] == "CLEAN"
    other = {**body, "data": {**body["data"], "content_sha256": "1" * 64}}
    conflict = live.request(
        live.path("uploads", created["upload_id"]) + "/actions/complete", method="POST", body=other
    )
    assert expect(conflict, 409)["code"] == "CONFLICT_OPERATION"
    # Identical content after completion is a replay; the sealed upload accepts nothing else.
    assert expect(put(live, created["upload_id"], content), 200)["state"] == "CLEAN"
    with live.db() as c:
        events = c.execute(
            "SELECT action,outcome,correlation_id FROM impact.upload_event WHERE upload_id=%s ORDER BY occurred_at",
            (created["upload_id"],),
        ).fetchall()
        assert [(r["action"], r["outcome"]) for r in events] == [
            ("create_upload", "SUCCEEDED"),
            ("put_upload_content", "SUCCEEDED"),
            ("complete_upload", "SUCCEEDED"),
            ("scan_upload", "CLEAN"),
        ]
        # Each upload event has its audit event (same action and correlation).
        for event in events:
            assert (
                c.execute(
                    "SELECT count(*) AS n FROM impact.audit_event_current WHERE action_type=%s AND correlation_id=%s",
                    (event["action"], event["correlation_id"]),
                ).fetchone()["n"]
                == 1
            )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE operation_id=%s",
                (body["operation_id"],),
            ).fetchone()["n"]
            == 1
        )


def test_replay_resumes_a_scan_interrupted_after_the_seal(live):
    """The seal commits before the scan runs outside it; if the process stopped in between, the blob
    is SCANNING and the upload QUARANTINED (never downloadable). Replaying the same completion
    returns its receipt and finishes the scan."""
    content = unique(CSV)
    created = expect(declare(live, content)[0], 201)
    received = expect(put(live, created["upload_id"], content), 200)
    body = cmd({"content_sha256": received["content_sha256"], "parts": []}, received["revision_id"])
    actor = live.fixture["actors"]["author"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (actor["tenant_id"],))
        c.execute(
            "UPDATE impact.upload_session SET state='QUARANTINED' WHERE upload_id=%s", (created["upload_id"],)
        )
        c.execute(
            "UPDATE impact.file_blob SET scan_state='SCANNING' WHERE blob_id=(SELECT blob_id FROM impact.upload_session WHERE upload_id=%s)",
            (created["upload_id"],),
        )
        c.execute(
            "INSERT INTO impact.operation_receipt VALUES(%s,%s,'complete_upload',%s,%s,'SUCCEEDED','{}'::jsonb,now()+interval '1 day')",
            (
                actor["tenant_id"],
                actor["principal_id"],
                body["operation_id"],
                hash_data(["complete_upload", created["upload_id"], body]),
            ),
        )
    pending = expect(live.request(live.path("uploads", created["upload_id"])), 200)
    assert pending["state"] == "QUARANTINED" and pending["scan_state"] == "PENDING"
    assert expect(evidence(live, created["upload_id"]), 409)["reason_code"] == "UPLOAD_NOT_CLEAN"
    resumed = live.request(
        live.path("uploads", created["upload_id"]) + "/actions/complete", method="POST", body=body
    )
    assert expect(resumed, 200)["state"] == "CLEAN"


def test_access_is_capability_owner_and_tenant_bound(live):
    status = uploaded(live, unique(CSV))
    item = expect(evidence(live, status["upload_id"]), 201)
    evidence_id = item["object_id"]
    # Missing and hidden are the same 404.
    assert expect(download(live, str(uuid.uuid4())), 404)["code"] == "RESOURCE_UNAVAILABLE"
    assert expect(download(live, evidence_id, actor="partner"), 404)["code"] == "RESOURCE_UNAVAILABLE"
    assert download(live, evidence_id, actor="other_tenant").status_code == 404
    other = live.fixture["tenant_b"]
    assert download(live, evidence_id, actor="other_tenant", tenant=other).status_code == 404
    assert download(live, evidence_id, actor="revoked").status_code in {401, 404}
    assert download(live, evidence_id, actor=None).status_code == 401
    # Upload sessions are visible to their owner only; writing needs upload.write and ownership.
    assert live.request(live.path("uploads", status["upload_id"]), actor="reviewer").status_code == 404
    assert live.request(live.path("uploads", status["upload_id"]), actor="other_tenant").status_code == 404
    assert put(live, status["upload_id"], CSV, actor="enumerator").status_code == 404
    assert expect(declare(live, CSV, actor="reviewer")[0], 403)["code"] == "POLICY_DENIED"
    # Another member's CLEAN upload cannot back this member's evidence.
    theirs = uploaded(live, unique(CSV), actor="enumerator")
    assert theirs["state"] == "CLEAN"
    assert evidence(live, theirs["upload_id"]).status_code == 404
    assert evidence(live, status["upload_id"], actor="enumerator").status_code == 403
    # Server-owned evidence fields never come from the body.
    forged = evidence(live, status["upload_id"], scan_state="CLEAN", integrity_sha256="0" * 64)
    assert expect(forged, 422)["code"] == "VALIDATION_FAILED"
    assert expect(evidence(live, None), 422)["code"] == "VALIDATION_FAILED"
    sourceless = live.request(
        live.path("evidence"), method="POST", body=cmd({"evidence_type": "NOTE", "source": "Memory"})
    )
    assert expect(sourceless, 422)["reason_code"] == "EVIDENCE_SOURCE_REQUIRED"
    linked = live.request(
        live.path("evidence"),
        method="POST",
        body=cmd({"evidence_type": "WEB_PAGE", "external_reference": "javascript:alert(1)"}),
    )
    assert expect(linked, 422)["code"] == "VALIDATION_FAILED"
    # Attaching needs evidence.attach (reviewer lacks it) and read access to the target.
    head = expect(live.request(live.path("evidence", evidence_id)), 200)
    observation = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    assert attach(live, head, "Observation", observation, actor="reviewer").status_code == 404
    foreign = {"object_id": live.fixture["programme_b"], "revision_id": str(uuid.uuid4())}
    assert attach(live, head, "Observation", foreign).status_code == 404
    # Without evidence.read the citation list is refused; with it but without download, items are
    # listed and marked not downloadable.
    expect(attach(live, head, "Observation", observation), 200)
    assert live.request(
        live.path("observations", observation["object_id"]) + "/evidence", actor="enumerator"
    ).status_code in {403, 404}
    partner = expect(
        live.request(live.path("observations", observation["object_id"]) + "/evidence", actor="partner"), 200
    )
    assert [x["downloadable"] for x in partner["items"]] == [False]


def test_native_evidence_registers_are_fenced_and_insert_only(connect, live):
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    c = connect("APP")  # skips on PGlite before any work
    status = uploaded(live, unique(CSV))
    item = expect(
        live.request(live.path("evidence", expect(evidence(live, status["upload_id"]), 201)["object_id"])),
        200,
    )
    observation = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    expect(attach(live, item, "Observation", observation), 200)
    assert download(live, item["object_id"]).status_code == 200
    for table in ["evidence_attachment", "evidence_access"]:
        assert query(c, "SELECT count(*) FROM impact." + table, role="impact_app") == [(0,)]
        for statement in [
            "UPDATE impact." + table + " SET tenant_id=tenant_id",
            "DELETE FROM impact." + table,
        ]:
            assert "permission denied" in denied(c, statement, role="impact_app", tenant=tenant_a)
        count = "SELECT count(*) FROM impact." + table + " WHERE evidence_id=%s"
        assert query(c, count, (item["object_id"],), role="impact_app", tenant=tenant_a) == [(1,)]
        assert query(c, count, (item["object_id"],), role="impact_app", tenant=tenant_b) == [(0,)]
        for login, role in [("PLATFORM", "impact_platform"), ("IDENTITY", "impact_identity")]:
            assert "permission denied" in denied(
                connect(login), "SELECT count(*) FROM impact." + table, role=role, tenant=tenant_a
            )
    events = "SELECT count(*) FROM impact.upload_event WHERE upload_id=%s"
    assert query(c, events, (status["upload_id"],), role="impact_app", tenant=tenant_a) == [(4,)]
    assert query(c, events, (status["upload_id"],), role="impact_app", tenant=tenant_b) == [(0,)]
    for statement in ["UPDATE impact.upload_event SET outcome='X'", "DELETE FROM impact.upload_event"]:
        assert "permission denied" in denied(c, statement, role="impact_app", tenant=tenant_a)
    # The upload tables stay tenant-fenced for the application role.
    blob = "SELECT count(*) FROM impact.upload_session WHERE upload_id=%s"
    assert query(c, blob, (status["upload_id"],), role="impact_app", tenant=tenant_a) == [(1,)]
    assert query(c, blob, (status["upload_id"],), role="impact_app", tenant=tenant_b) == [(0,)]


def stored(live, content):
    digest = hashlib.sha256(content).hexdigest()
    return Path(live.config["object_store_dir"]) / live.fixture["tenant_a"] / digest[:2] / digest


def test_failed_scan_and_changed_bytes_are_never_served(live):
    """A scan that cannot read the exact recorded bytes is FAILED (never CLEAN), and bytes changed in
    the store after a CLEAN verdict are refused at download with no access recorded."""
    content = unique(CSV)
    created = expect(declare(live, content)[0], 201)
    received = expect(put(live, created["upload_id"], content), 200)
    path = stored(live, content)
    assert path.read_bytes() == content
    path.write_bytes(content + b"tampered")
    failed = expect(complete(live, received)[0], 200)
    assert failed["state"] == "REJECTED" and failed["scan_state"] == "FAILED"
    assert failed["scan_detail"] == "OBJECT_INTEGRITY_FAILED"
    assert expect(evidence(live, created["upload_id"]), 409)["reason_code"] == "UPLOAD_NOT_CLEAN"

    content = unique(CSV)
    status = uploaded(live, content)
    item = expect(evidence(live, status["upload_id"]), 201)
    stored(live, content).write_bytes(content[:-1] + b"!")
    broken = expect(download(live, item["object_id"]), 503)
    assert broken["reason_code"] == "OBJECT_INTEGRITY_FAILED"
    assert (
        counts(
            live, "SELECT count(*) AS n FROM impact.evidence_access WHERE evidence_id=%s", item["object_id"]
        )
        == 0
    )
