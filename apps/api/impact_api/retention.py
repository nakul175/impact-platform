"""Retention schedule and sweep (v0.25 part B; tenant policies and the audit window since v0.27).

The schedule is a catalogue per data class. The build's fixed values are the defaults; a tenant may
propose a RetentionPolicy for one of the policy-able classes (POLICY_BOUNDS) and, once a second
natural person has approved it, the latest approved binding (`retention_policy_binding`, insert-only)
replaces the default duration for that class. Every other class keeps the fixed value. The worker's
RETENTION_SWEEP job class applies the effective schedule per Active tenant under a generation-fenced
lease (worker.py): in one transaction it renews the lease, applies every class below, writes one
insert-only `retention_proof` row per class (count, cutoff and the SHA-256 of the sorted keys it
affected, with the duration it actually applied) and records the job outcome, all fenced on the
lease generation, so a stale holder's sweep rolls back and leaves no proof. Every cutoff is the
database clock.

Classes and what they reach:
- OPERATION_RECEIPT: idempotency receipts are kept for 7 days (the API contract); expired rows are
  deleted through the definer impact.retention_purge_receipts (the worker has no table privilege).
  A policy may only lengthen the retention (7–90 days): the definer treats anything below 7 as 7.
- UPLOAD_SESSION: an evidence upload left OPEN past its 24-hour window becomes EXPIRED through the
  definer impact.retention_expire_uploads. Bytes such a session may have received stay in the
  object store: the worker has no access to the object store (a documented limit). Not policy-able.
- PRIVACY_EXPORT_PACKAGE: a data-subject access export package is deleted when it expires, 7 days
  after production by default (policy 1–30 days from production); its download log stays.
- OUTBOX_RECIPIENT: the sealed recipient address of an email intent is overwritten with random bytes
  30 days after the intent reached a terminal state (policy 7–365 days); the event and its outcome
  stay.
- SECURITY_EVENT: collapsed access-denial rows (v0.27 denial auditing) are deleted beyond the
  tenant's audit window, 2,555 days (seven years) by default and never less than the 365-day floor
  (AUDIT_FLOOR_DAYS), through the definer impact.retention_purge_security_events, which enforces the
  floor itself. AuditEvent records are never deleted by this build inside or beyond the window: no
  removal path through the insert-only revision store exists (a documented limit).
"""

import hashlib
from datetime import timedelta

BATCH = 5000
AUDIT_FLOOR_DAYS = 365
AUDIT_DEFAULT_DAYS = 2555
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
    {
        "data_class": "SECURITY_EVENT",
        "store": "access_denial",
        "trigger": "Last occurrence of a collapsed access denial",
        "retention_days": AUDIT_DEFAULT_DAYS,
        "action": "DELETE",
        "basis": "Audit window: security events stay at least 365 days (floor) and seven years by default; "
        "AuditEvent records are never deleted by this build.",
    },
]
CLASSES = {c["data_class"]: c for c in SCHEDULE}
# Classes a tenant policy may govern, with the inclusive bounds an approved duration must respect.
POLICY_BOUNDS = {
    "OPERATION_RECEIPT": (7, 90),
    "PRIVACY_EXPORT_PACKAGE": (1, 30),
    "OUTBOX_RECIPIENT": (7, 365),
    "SECURITY_EVENT": (AUDIT_FLOOR_DAYS, 3650),
}


def digest(items):
    """SHA-256 of the sorted affected keys, one per line (the empty digest when nothing was due)."""
    return hashlib.sha256("\n".join(sorted(items)).encode()).digest()


def check_policy(data_class, duration_days, action):
    """The reason a proposed policy is refused, or None: a class outside POLICY_BOUNDS, a duration
    outside its bounds (the audit floor among them) or an action other than the class's own."""
    if data_class not in POLICY_BOUNDS:
        return "DATA_CLASS_NOT_POLICY_ABLE"
    low, high = POLICY_BOUNDS[data_class]
    if not isinstance(duration_days, int) or not low <= duration_days <= high:
        return "RETENTION_OUT_OF_BOUNDS"
    if action != CLASSES[data_class]["action"]:
        return "RETENTION_ACTION_FIXED"
    return None


def bindings(c, tenant):
    """The latest approved binding per data class (binding rows are insert-only, newest wins)."""
    rows = c.execute(
        "SELECT DISTINCT ON (data_class) data_class,policy_id,policy_revision,duration_days,approved_at "
        "FROM impact.retention_policy_binding WHERE tenant_id=%s ORDER BY data_class,approved_at DESC,binding_id DESC",
        (tenant,),
    ).fetchall()
    return {r["data_class"]: r for r in rows}


def effective(c, tenant):
    """The schedule this tenant's sweep applies now: the fixed catalogue with every approved binding
    substituted (duration only; store, trigger and action are the class's own)."""
    bound = bindings(c, tenant)
    items = []
    for item in SCHEDULE:
        policy = dict(item)
        binding = bound.get(item["data_class"])
        if binding and check_policy(item["data_class"], binding["duration_days"], item["action"]) is None:
            policy["retention_days"] = binding["duration_days"]
            policy["source"] = "APPROVED_POLICY"
            policy["policy_id"] = str(binding["policy_id"])
        else:
            policy["source"] = "DEFAULT"
            policy["policy_id"] = None
        items.append(policy)
    return items


def apply(c, tenant):
    """Apply every class for the tenant in context (transaction-local tenant already set) and
    return {data_class: (cutoff, [keys], policy)}, policy being the effective class entry (its
    retention_days is what was applied). Called inside the worker's fenced sweep transaction."""
    at = c.execute("SELECT statement_timestamp() AS at").fetchone()["at"]
    policies = {p["data_class"]: p for p in effective(c, tenant)}
    results = {}
    receipt_days = policies["OPERATION_RECEIPT"]["retention_days"]
    receipts = c.execute(
        "SELECT item FROM impact.retention_purge_receipts(%s,%s)", (BATCH, receipt_days)
    ).fetchall()
    results["OPERATION_RECEIPT"] = (
        at - timedelta(days=max(receipt_days, 7) - 7),
        [r["item"] for r in receipts],
        policies["OPERATION_RECEIPT"],
    )
    uploads = c.execute("SELECT item FROM impact.retention_expire_uploads(%s)", (BATCH,)).fetchall()
    results["UPLOAD_SESSION"] = (at, [r["item"] for r in uploads], policies["UPLOAD_SESSION"])
    package_days = policies["PRIVACY_EXPORT_PACKAGE"]["retention_days"]
    packages = c.execute(
        "DELETE FROM impact.privacy_export_package p USING (SELECT tenant_id,package_id FROM "
        "impact.privacy_export_package WHERE tenant_id=%s AND created_at<=statement_timestamp()-make_interval(days=>%s) "
        "ORDER BY created_at,package_id LIMIT %s) d WHERE p.tenant_id=d.tenant_id AND "
        "p.package_id=d.package_id RETURNING p.package_id::text||':'||encode(p.content_sha256,'hex') AS item",
        (tenant, package_days, BATCH),
    ).fetchall()
    results["PRIVACY_EXPORT_PACKAGE"] = (
        at - timedelta(days=package_days),
        [r["item"] for r in packages],
        policies["PRIVACY_EXPORT_PACKAGE"],
    )
    days = policies["OUTBOX_RECIPIENT"]["retention_days"]
    recipients = c.execute(
        "UPDATE impact.outbox_delivery o SET recipient_sealed=sha256(convert_to(gen_random_uuid()::text,'UTF8')),"
        "recipient_redacted_at=statement_timestamp() FROM (SELECT tenant_id,event_id FROM impact.outbox_delivery "
        "WHERE tenant_id=%s AND channel='EMAIL' AND recipient_redacted_at IS NULL AND state IN "
        "('SENT','DEAD','SUPERSEDED') AND completed_at<=statement_timestamp()-make_interval(days=>%s) "
        "ORDER BY completed_at,event_id LIMIT %s) d WHERE o.tenant_id=d.tenant_id AND o.event_id=d.event_id "
        "RETURNING o.event_id::text AS item",
        (tenant, days, BATCH),
    ).fetchall()
    results["OUTBOX_RECIPIENT"] = (
        at - timedelta(days=days),
        [r["item"] for r in recipients],
        policies["OUTBOX_RECIPIENT"],
    )
    audit_days = max(policies["SECURITY_EVENT"]["retention_days"], AUDIT_FLOOR_DAYS)
    denials = c.execute(
        "SELECT item FROM impact.retention_purge_security_events(%s,%s)", (BATCH, audit_days)
    ).fetchall()
    results["SECURITY_EVENT"] = (
        at - timedelta(days=audit_days),
        [r["item"] for r in denials],
        policies["SECURITY_EVENT"],
    )
    return results
