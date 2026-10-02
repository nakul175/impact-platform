"""Retention schedule and sweep (v0.25 part B).

The schedule is a fixed catalogue per data class (no tenant-editable retention policy objects
exist in this build). The worker's RETENTION_SWEEP job class applies it per Active tenant under a
generation-fenced lease (worker.py): in one transaction it renews the lease, applies every class
below, writes one insert-only `retention_proof` row per class (count, cutoff and the SHA-256 of
the sorted keys it affected) and records the job outcome, all fenced on the lease generation, so a
stale holder's sweep rolls back and leaves no proof. Every cutoff is the database clock.

Classes and what they reach:
- OPERATION_RECEIPT: idempotency receipts are kept for 7 days (the API contract); expired rows are
  deleted through the definer impact.retention_purge_receipts (the worker has no table privilege).
- UPLOAD_SESSION: an evidence upload left OPEN past its 24-hour window becomes EXPIRED through the
  definer impact.retention_expire_uploads. Bytes such a session may have received stay in the
  object store: the worker has no access to the object store (a documented limit).
- PRIVACY_EXPORT_PACKAGE: a data-subject access export package is deleted 7 days after it was
  produced; its download log (privacy_export_access) stays.
- OUTBOX_RECIPIENT: the sealed recipient address of an email intent is overwritten with random bytes
  30 days after the intent reached a terminal state (SENT, DEAD or SUPERSEDED); the event and its
  outcome stay.
"""

import hashlib
from datetime import timedelta

BATCH = 5000
SCHEDULE = [
    {
        "data_class": "OPERATION_RECEIPT",
        "store": "operation_receipt",
        "trigger": "Receipt expiry (7 days after the command)",
        "retention_days": 7,
        "action": "DELETE",
        "basis": "Idempotency window of the API contract; nothing else reads an expired receipt.",
    },
    {
        "data_class": "UPLOAD_SESSION",
        "store": "upload_session",
        "trigger": "Upload window end (24 hours after the declaration) while still OPEN",
        "retention_days": 1,
        "action": "EXPIRE",
        "basis": "An unfinished upload stops accepting content; received bytes are not purged by the worker.",
    },
    {
        "data_class": "PRIVACY_EXPORT_PACKAGE",
        "store": "privacy_export_package",
        "trigger": "Package production (expires 7 days later)",
        "retention_days": 7,
        "action": "DELETE",
        "basis": "A data-subject export is held only long enough to hand it to the subject.",
    },
    {
        "data_class": "OUTBOX_RECIPIENT",
        "store": "outbox_delivery.recipient_sealed",
        "trigger": "Email intent reached SENT, DEAD or SUPERSEDED",
        "retention_days": 30,
        "action": "REDACT",
        "basis": "Recipient addresses are needed only while delivery can still be attempted or re-queued.",
    },
]
CLASSES = {c["data_class"]: c for c in SCHEDULE}


def digest(items):
    """SHA-256 of the sorted affected keys, one per line (the empty digest when nothing was due)."""
    return hashlib.sha256("\n".join(sorted(items)).encode()).digest()


def apply(c, tenant):
    """Apply every class for the tenant in context (transaction-local tenant already set) and
    return {data_class: (cutoff, [keys])}. Called inside the worker's fenced sweep transaction."""
    at = c.execute("SELECT statement_timestamp() AS at").fetchone()["at"]
    results = {}
    receipts = c.execute("SELECT item FROM impact.retention_purge_receipts(%s)", (BATCH,)).fetchall()
    results["OPERATION_RECEIPT"] = (at, [r["item"] for r in receipts])
    uploads = c.execute("SELECT item FROM impact.retention_expire_uploads(%s)", (BATCH,)).fetchall()
    results["UPLOAD_SESSION"] = (at, [r["item"] for r in uploads])
    packages = c.execute(
        "DELETE FROM impact.privacy_export_package p USING (SELECT tenant_id,package_id FROM "
        "impact.privacy_export_package WHERE tenant_id=%s AND expires_at<=statement_timestamp() "
        "ORDER BY expires_at,package_id LIMIT %s) d WHERE p.tenant_id=d.tenant_id AND "
        "p.package_id=d.package_id RETURNING p.package_id::text||':'||encode(p.content_sha256,'hex') AS item",
        (tenant, BATCH),
    ).fetchall()
    results["PRIVACY_EXPORT_PACKAGE"] = (at, [r["item"] for r in packages])
    days = CLASSES["OUTBOX_RECIPIENT"]["retention_days"]
    recipients = c.execute(
        "UPDATE impact.outbox_delivery o SET recipient_sealed=sha256(convert_to(gen_random_uuid()::text,'UTF8')),"
        "recipient_redacted_at=statement_timestamp() FROM (SELECT tenant_id,event_id FROM impact.outbox_delivery "
        "WHERE tenant_id=%s AND channel='EMAIL' AND recipient_redacted_at IS NULL AND state IN "
        "('SENT','DEAD','SUPERSEDED') AND completed_at<=statement_timestamp()-make_interval(days=>%s) "
        "ORDER BY completed_at,event_id LIMIT %s) d WHERE o.tenant_id=d.tenant_id AND o.event_id=d.event_id "
        "RETURNING o.event_id::text AS item",
        (tenant, days, BATCH),
    ).fetchall()
    results["OUTBOX_RECIPIENT"] = (at - timedelta(days=days), [r["item"] for r in recipients])
    return results
