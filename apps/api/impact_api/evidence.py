"""Evidence uploads, scanning, attachments and mediated downloads (v0.22).

Upload session (WHOLE mode, EVIDENCE_MEDIA only):
  create (declared name, allow-listed media type, size, SHA-256) -> OPEN
  PUT content (exact bytes, digest, magic-byte sniff; written to the private object store first,
    then bound to a file_blob row in QUARANTINED) -> OPEN with content
  complete (sealed) -> QUARANTINED, blob SCANNING -> scan outside any transaction -> CLEAN or REJECTED
The bytes are never served from the store directly. An Evidence revision may name only a CLEAN
upload of its author; attaching cites an exact evidence revision from an exact observation or
calculated-result revision in an insert-only register; a download re-authorises the caller,
re-verifies the stored digest and records the access."""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from psycopg.types.json import Jsonb

from .content_safety import check_declaration, refuse, scanner, sniff
from .contracts import validate
from .domain import DomainError, unavailable
from .evidence_contracts import TARGET_KINDS
from .object_store import object_store
from .store import authorize, context, hash_data, load, scopes, write

LOG = logging.getLogger("impact")
UPLOAD_HOURS = 24
SERVER_FIELDS = (
    "filename",
    "media_type",
    "byte_size",
    "integrity_sha256",
    "scan_state",
    "verification_state",
)
PENDING = {"QUARANTINED": "PENDING", "SCANNING": "PENDING"}


def now():
    return datetime.now(timezone.utc)


def record(c, ctx, action, correlation, outcome="SUCCEEDED", evidence_id=None, upload_id=None):
    """An audit event for an action that writes no domain revision: a download names the evidence
    object; an upload action (upload sessions are not registry objects, so an audit event cannot
    reference one) is linked to its upload through the insert-only upload_event register."""
    at = now()
    write(
        c,
        ctx,
        "AuditEvent",
        {
            "real_actor_id": ctx.principal_id,
            "effective_actor_id": ctx.principal_id,
            "action_type": action,
            **({"object_reference": str(evidence_id)} if evidence_id else {}),
            "outcome": outcome,
            "occurred_at": at.isoformat(),
            "correlation_id": correlation,
            "specification_ref": "FR-SEC-005",
        },
        "Recorded",
        track_author=False,
    )
    if upload_id:
        c.execute(
            "INSERT INTO impact.upload_event VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
            (ctx.tenant_id, str(uuid4()), upload_id, action, outcome, ctx.principal_id, at, correlation),
        )


def status(row):
    """The UploadStatus view of an upload_session row joined with its blob (columns b_*)."""
    blob = row.get("b_scan_state")
    return {
        "upload_id": str(row["upload_id"]),
        "revision_id": str(row["revision_id"]),
        "state": row["state"],
        "purpose": row["purpose"],
        "expected_bytes": row["expected_bytes"],
        "content_sha256": bytes(row["expected_digest"]).hex(),
        "part_size": 1048576,
        "parts": [],
        "expires_at": row["expires_at"].isoformat(),
        "scan_state": PENDING.get(blob, blob) if blob else "PENDING",
        "scan_detail": row.get("b_scan_detail"),
        "filename": row["filename"],
        "content_type": row["media_type"],
        "content_received": row["blob_id"] is not None,
    }


UPLOAD_QUERY = (
    "SELECT u.*,b.scan_state AS b_scan_state,b.scan_detail AS b_scan_detail,b.object_key AS b_object_key,"
    "b.sha256 AS b_sha256,b.bytes AS b_bytes,b.purged_at AS b_purged_at FROM impact.upload_session u LEFT JOIN impact.file_blob b "
    "ON b.tenant_id=u.tenant_id AND b.blob_id=u.blob_id WHERE u.tenant_id=%s AND u.upload_id=%s"
)


class Evidence:
    def __init__(self, service):
        self.service, self.s, self.db = service, service.s, service.db
        self.store = object_store(self.s)
        self.scanner = scanner(self.s.evidence_scanner) if self.s.evidence_scanner else None

    def configured(self):
        if not self.store or not self.scanner:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="OBJECT_STORE_NOT_CONFIGURED")

    # ---- upload sessions -----------------------------------------------------------------

    def owned(self, c, ctx, upload_id, lock=False):
        """The caller's own upload (with its blob), or RESOURCE_UNAVAILABLE: another member's upload
        and a missing one are indistinguishable."""
        row = c.execute(
            UPLOAD_QUERY + (" FOR UPDATE OF u" if lock else ""), (ctx.tenant_id, upload_id)
        ).fetchone()
        if not row or str(row["owner_id"]) != ctx.principal_id or row["purpose"] != "EVIDENCE_MEDIA":
            unavailable()
        return row

    def receipted(self, c, ctx, op, body, fingerprint, handler):
        """Operation-identifier idempotency for the upload commands, as in Service.command."""
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
        old = c.execute(
            "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
            (ctx.tenant_id, ctx.principal_id, op, body["operation_id"]),
        ).fetchone()
        if old:
            if bytes(old["payload_hash"]) != fingerprint:
                raise DomainError("CONFLICT_OPERATION", 409)
            if old["expires_at"] <= now():
                raise DomainError("IDEMPOTENCY_EXPIRED", 409)
            return old["outcome"], True
        outcome = handler()
        c.execute(
            "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
            (
                ctx.tenant_id,
                ctx.principal_id,
                op,
                body["operation_id"],
                fingerprint,
                Jsonb(outcome),
                now() + timedelta(days=7),
            ),
        )
        return outcome, False

    def create_upload(self, identity, tenant, body, correlation):
        validate("UploadCreate", body)
        data = body["data"]
        check_declaration(data["content_type"], data["filename"], data["expected_bytes"])
        self.configured()
        fingerprint = hash_data(["create_upload", None, body])
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_upload")

            def handler():
                upload_id, at = str(uuid4()), now()
                c.execute(
                    "INSERT INTO impact.upload_session(tenant_id,upload_id,revision_id,owner_id,purpose,mode,expected_bytes,expected_digest,state,expires_at,filename,media_type,created_at) VALUES(%s,%s,%s,%s,'EVIDENCE_MEDIA','WHOLE',%s,%s,'OPEN',%s,%s,%s,%s)",
                    (
                        tenant,
                        upload_id,
                        str(uuid4()),
                        ctx.principal_id,
                        data["expected_bytes"],
                        bytes.fromhex(data["content_sha256"]),
                        at + timedelta(hours=UPLOAD_HOURS),
                        data["filename"],
                        data["content_type"],
                        at,
                    ),
                )
                record(c, ctx, "create_upload", correlation, upload_id=upload_id)
                return status(c.execute(UPLOAD_QUERY, (tenant, upload_id)).fetchone())

            outcome, _ = self.receipted(c, ctx, "create_upload", body, fingerprint, handler)
            return outcome

    def upload(self, identity, tenant, upload_id):
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_uploads", upload_id, hidden=True)
            return status(self.owned(c, ctx, upload_id))

    def content_limit(self, identity, tenant, upload_id):
        """Checked before a byte of the body is read: the caller may write this upload, which is still
        open, and the body may be at most its declared size."""
        self.configured()
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "put_upload_content", upload_id, hidden=True)
            row = self.owned(c, ctx, upload_id)
            if row["blob_id"] is None and (row["state"] != "OPEN" or row["expires_at"] <= now()):
                raise DomainError("INVALID_STATE", 409, reason="UPLOAD_NOT_OPEN")
            return row["expected_bytes"]

    def put_content(self, identity, tenant, upload_id, raw, correlation):
        self.configured()
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "put_upload_content", upload_id, hidden=True)
            row = self.owned(c, ctx, upload_id)
        if len(raw) != row["expected_bytes"]:
            refuse("SIZE_MISMATCH")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != bytes(row["expected_digest"]).hex():
            refuse("HASH_MISMATCH")
        if row["blob_id"] is not None:
            # Identical replay of an accepted write: the same status, nothing rewritten.
            return status(row)
        sniff(raw, row["media_type"])
        # The bytes are stored before the transaction that records them: a failed transaction leaves
        # an unreferenced quarantined object (never served), never a row naming missing bytes.
        key = self.store.put(tenant, digest, raw)
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "put_upload_content", upload_id, hidden=True)
            row = self.owned(c, ctx, upload_id, lock=True)
            if row["blob_id"] is not None:
                return status(row)
            if row["state"] != "OPEN" or row["expires_at"] <= now():
                raise DomainError("INVALID_STATE", 409, reason="UPLOAD_NOT_OPEN")
            blob = c.execute(
                "SELECT blob_id FROM impact.file_blob WHERE tenant_id=%s AND object_key=%s", (tenant, key)
            ).fetchone()
            blob_id = str(blob["blob_id"]) if blob else str(uuid4())
            if not blob:
                c.execute(
                    "INSERT INTO impact.file_blob(tenant_id,blob_id,object_key,sha256,bytes,scan_state,classification,created_at) VALUES(%s,%s,%s,%s,%s,'QUARANTINED','INTERNAL',%s)",
                    (tenant, blob_id, key, bytes.fromhex(digest), len(raw), now()),
                )
            c.execute(
                "UPDATE impact.upload_session SET blob_id=%s,content_received_at=%s,revision_id=%s WHERE tenant_id=%s AND upload_id=%s",
                (blob_id, now(), str(uuid4()), tenant, upload_id),
            )
            record(c, ctx, "put_upload_content", correlation, upload_id=upload_id)
            return status(c.execute(UPLOAD_QUERY, (tenant, upload_id)).fetchone())

    def complete(self, identity, tenant, upload_id, body, correlation):
        validate("UploadComplete", body)
        self.configured()
        fingerprint = hash_data(["complete_upload", upload_id, body])
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "complete_upload", upload_id, hidden=True)

            def handler():
                row = self.owned(c, ctx, upload_id, lock=True)
                if str(row["revision_id"]) != body["expected_revision"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                if body["data"]["content_sha256"] != bytes(row["expected_digest"]).hex():
                    refuse("HASH_MISMATCH")
                if row["blob_id"] is None:
                    raise DomainError("INVALID_STATE", 409, reason="CONTENT_REQUIRED")
                if row["state"] != "OPEN":
                    raise DomainError("INVALID_STATE", 409, reason="UPLOAD_NOT_OPEN")
                verdict = row["b_scan_state"]
                # A blob is judged once per content: an earlier CLEAN or INFECTED verdict on the same
                # bytes stands (with the scanner that gave it); otherwise the blob is (re)scanned.
                state = {"CLEAN": "CLEAN", "INFECTED": "REJECTED"}.get(verdict, "QUARANTINED")
                if verdict in {"QUARANTINED", "FAILED"}:
                    c.execute(
                        "UPDATE impact.file_blob SET scan_state='SCANNING' WHERE tenant_id=%s AND blob_id=%s",
                        (tenant, row["blob_id"]),
                    )
                c.execute(
                    "UPDATE impact.upload_session SET state=%s,completed_at=%s,revision_id=%s WHERE tenant_id=%s AND upload_id=%s",
                    (state, now(), str(uuid4()), tenant, upload_id),
                )
                record(c, ctx, "complete_upload", correlation, upload_id=upload_id)
                return status(c.execute(UPLOAD_QUERY, (tenant, upload_id)).fetchone())

            self.receipted(c, ctx, "complete_upload", body, fingerprint, handler)
        # Outside the command transaction: the scan, then a separate transaction for its verdict. A
        # replay of the same operation re-runs a scan that an earlier attempt did not finish.
        self.scan(identity, tenant, upload_id, correlation)
        return self.upload(identity, tenant, upload_id)

    def scan(self, identity, tenant, upload_id, correlation):
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            row = self.owned(c, ctx, upload_id)
        if row["b_scan_state"] != "SCANNING":
            return
        try:
            data = self.store.get(row["b_object_key"], bytes(row["b_sha256"]).hex())
            verdict, detail = self.scanner.scan(data)
            if verdict not in {"CLEAN", "INFECTED", "FAILED"}:
                verdict, detail = "FAILED", "SCANNER_ERROR"
        except DomainError as exc:
            verdict, detail = "FAILED", exc.reason or "OBJECT_UNREADABLE"
        except Exception as exc:  # a scanner failure is a verdict, never a CLEAN
            LOG.error("evidence scan failed upload=%s type=%s", upload_id, type(exc).__name__)
            verdict, detail = "FAILED", "SCANNER_ERROR"
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            changed = c.execute(
                "UPDATE impact.file_blob SET scan_state=%s,scan_detail=%s,scanner=%s,scanned_at=%s WHERE tenant_id=%s AND blob_id=%s AND scan_state='SCANNING' RETURNING blob_id",
                (verdict, detail, self.scanner.name, now(), tenant, row["blob_id"]),
            ).fetchone()
            if not changed:
                return
            # Every sealed upload of these bytes takes the verdict (a concurrent upload of the same
            # content may be waiting on this scan).
            sealed = c.execute(
                "SELECT upload_id FROM impact.upload_session WHERE tenant_id=%s AND blob_id=%s AND state='QUARANTINED'",
                (tenant, row["blob_id"]),
            ).fetchall()
            for item in sealed:
                c.execute(
                    "UPDATE impact.upload_session SET state=%s,revision_id=%s WHERE tenant_id=%s AND upload_id=%s",
                    ("CLEAN" if verdict == "CLEAN" else "REJECTED", str(uuid4()), tenant, item["upload_id"]),
                )
                record(c, ctx, "scan_upload", correlation, outcome=verdict, upload_id=item["upload_id"])

    # ---- evidence revisions --------------------------------------------------------------

    def clean_upload(self, c, ctx, upload_id):
        row = c.execute(UPLOAD_QUERY, (ctx.tenant_id, upload_id)).fetchone()
        if not row or row["purpose"] != "EVIDENCE_MEDIA":
            unavailable()
        if row["state"] != "CLEAN" or row["b_scan_state"] != "CLEAN":
            raise DomainError("INVALID_STATE", 409, reason="UPLOAD_NOT_CLEAN")
        if row["b_purged_at"]:
            # Bytes erased by a privacy case (v0.25 part B): the upload can back nothing any more.
            raise DomainError("INVALID_STATE", 409, reason="UPLOAD_CONTENT_ERASED")
        return row

    def stamp(self, c, ctx, data, previous):
        """Server-owned evidence fields, derived from the named upload; never taken from the body.
        A new upload must be the caller's own and CLEAN; an unchanged one keeps its stamped values."""
        prior = previous["payload"] if previous else {}
        data = {k: v for k, v in data.items() if k not in SERVER_FIELDS}
        if not data.get("evidence_type"):
            refuse("EVIDENCE_TYPE_REQUIRED")
        upload_id = data.get("upload_id")
        if not upload_id and not data.get("external_reference"):
            refuse("EVIDENCE_SOURCE_REQUIRED")
        if upload_id:
            row = self.clean_upload(c, ctx, upload_id)
            if upload_id != prior.get("upload_id") and str(row["owner_id"]) != ctx.principal_id:
                unavailable()
            data.update(
                filename=row["filename"],
                media_type=row["media_type"],
                byte_size=row["expected_bytes"],
                integrity_sha256=bytes(row["expected_digest"]).hex(),
                scan_state="CLEAN",
            )
        data["verification_state"] = "UNVERIFIED"
        return data

    def attach(self, c, ctx, evidence, data):
        load(c, ctx, evidence["object_id"], "Evidence", "evidence.read")
        kind = data["target_kind"]
        target = load(c, ctx, data["target_id"], kind, TARGET_KINDS[kind] + ".read")
        if str(target["head_revision"]) != data["target_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="TARGET_REVISION_CHANGED")
        payload = evidence["payload"]
        if payload.get("upload_id"):
            self.clean_upload(c, ctx, payload["upload_id"])
        elif not payload.get("external_reference"):
            raise DomainError("INVALID_STATE", 409, reason="EVIDENCE_SOURCE_REQUIRED")
        if c.execute(
            "SELECT 1 FROM impact.evidence_attachment WHERE tenant_id=%s AND evidence_revision=%s AND target_revision=%s",
            (ctx.tenant_id, evidence["head_revision"], data["target_revision"]),
        ).fetchone():
            raise DomainError("INVALID_STATE", 409, reason="EVIDENCE_ALREADY_ATTACHED")
        at = now()
        c.execute(
            "INSERT INTO impact.evidence_attachment(tenant_id,attachment_id,evidence_id,evidence_revision,target_id,target_revision,target_type,reason,attached_by,attached_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                str(uuid4()),
                evidence["object_id"],
                evidence["head_revision"],
                data["target_id"],
                data["target_revision"],
                kind,
                data["reason"],
                ctx.principal_id,
                at,
            ),
        )
        # No revision of either side is written: the receipt names the cited evidence revision.
        return {
            "operation_id": "",
            "object_id": str(evidence["object_id"]),
            "revision_id": str(evidence["head_revision"]),
            "business_state": evidence["lifecycle_state"],
            "saved_at": at.isoformat(),
            "correlation_id": "",
        }

    def attachments(self, identity, tenant, kind, target_id):
        op = "list_observation_evidence" if kind == "Observation" else "list_calculated_result_evidence"
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            target = load(c, ctx, target_id, kind, TARGET_KINDS[kind] + ".read")
            if not any(g["capability"] == "evidence.read" and g["purpose"] is None for g in ctx.grants):
                authorize(c, ctx, op)
            rows = c.execute(
                "SELECT a.*,v.revision_number,v.payload,v.restriction_state,r.head_revision,r.classification,"
                "u.state AS upload_state,b.scan_state AS blob_state FROM impact.evidence_attachment a "
                "JOIN impact.object_revision v ON v.tenant_id=a.tenant_id AND v.revision_id=a.evidence_revision "
                "JOIN impact.object_registry r ON r.tenant_id=a.tenant_id AND r.object_id=a.evidence_id "
                "LEFT JOIN impact.upload_session u ON u.tenant_id=a.tenant_id AND u.upload_id=(v.payload->>'upload_id')::uuid "
                "LEFT JOIN impact.file_blob b ON b.tenant_id=u.tenant_id AND b.blob_id=u.blob_id "
                "WHERE a.tenant_id=%s AND a.target_id=%s ORDER BY a.attached_at,a.attachment_id LIMIT 200",
                (tenant, target_id),
            ).fetchall()
            items = []
            for row in rows:
                if (
                    row["restriction_state"] != "AVAILABLE"
                    or row["classification"] == "RESTRICTED"
                    or not scopes(c, ctx, "evidence.read", row["evidence_id"])
                ):
                    continue
                payload = row["payload"]
                items.append(
                    {
                        "attachment_id": str(row["attachment_id"]),
                        "evidence_id": str(row["evidence_id"]),
                        "evidence_revision": str(row["evidence_revision"]),
                        "evidence_revision_number": row["revision_number"],
                        "evidence_head_revision": str(row["head_revision"]),
                        "target_kind": kind,
                        "target_id": str(row["target_id"]),
                        "target_revision": str(row["target_revision"]),
                        "target_is_current": str(row["target_revision"]) == str(target["head_revision"]),
                        "evidence_type": payload.get("evidence_type"),
                        "filename": payload.get("filename"),
                        "media_type": payload.get("media_type"),
                        "byte_size": payload.get("byte_size"),
                        "integrity_sha256": payload.get("integrity_sha256"),
                        "external_reference": payload.get("external_reference"),
                        "scan_state": row["blob_state"],
                        "downloadable": row["upload_state"] == "CLEAN"
                        and row["blob_state"] == "CLEAN"
                        and scopes(c, ctx, "evidence.download", row["evidence_id"]),
                        "reason": row["reason"],
                        "attached_by": str(row["attached_by"]),
                        "attached_at": row["attached_at"].isoformat(),
                    }
                )
            return {
                "items": items,
                "next_cursor": None,
                "scope_label": "Evidence permitted by your current access",
            }

    # ---- mediated download ---------------------------------------------------------------

    def content(self, identity, tenant, evidence_id, revision, correlation):
        self.configured()
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_evidence_content", evidence_id, hidden=True)
            head = load(c, ctx, evidence_id, "Evidence")
            if revision:
                version = c.execute(
                    "SELECT revision_id,payload,restriction_state FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
                    (tenant, evidence_id, revision),
                ).fetchone()
                if not version or version["restriction_state"] != "AVAILABLE":
                    unavailable()
            else:
                version = {"revision_id": head["head_revision"], "payload": head["payload"]}
            upload_id = version["payload"].get("upload_id")
            row = c.execute(UPLOAD_QUERY, (tenant, upload_id)).fetchone() if upload_id else None
            # Only bytes whose verdict is CLEAN ever leave: quarantined, scanning, infected and failed
            # content is indistinguishable from absent content.
            if not row or row["state"] != "CLEAN" or row["b_scan_state"] != "CLEAN" or row["b_purged_at"]:
                unavailable()
            data = self.store.get(row["b_object_key"], bytes(row["b_sha256"]).hex())
            c.execute(
                "INSERT INTO impact.evidence_access VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    str(uuid4()),
                    evidence_id,
                    version["revision_id"],
                    row["blob_id"],
                    ctx.principal_id,
                    ctx.membership_id,
                    now(),
                    correlation,
                ),
            )
            record(c, ctx, "read_evidence_content", correlation, evidence_id=evidence_id)
            return {
                "body": data,
                "media_type": row["media_type"],
                "filename": row["filename"],
                "digest": bytes(row["b_sha256"]).hex(),
            }
