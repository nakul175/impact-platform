"""Data-subject requests for a member of the tenant (v0.25 part B).

A privacy case names one member of this tenant (the subject; no participant records exist in this
build) and a request type:

- ACCESS: after independent approval, `execute` writes one bounded export package of the personal
  data this tenant holds about the subject (JSON, one SHA-256 per section and for the whole body),
  which `GET .../export` hands to a privacy officer as a mediated, recorded attachment.
- ERASURE: the subject must no longer be an active or suspended member and must not hold custody.
  The server computes a per-store plan (privacy_store_action rows) of the subject's personal data:
  the member profile (display name, e-mail mask), the invitations addressed to the subject (the
  register row and every revision payload that carries the e-mail mask), the delivery intents that
  reference those invitations or the subject's notices (open intents superseded, sealed addresses
  overwritten), and the evidence objects and import batches the privacy officer names as the
  subject's personal data (projections redacted, every revision payload removed, evidence bytes
  deleted from the object store once no other evidence uses them). An independent approver confirms
  the plan by its SHA-256; `execute` re-computes it, refuses a changed plan, and runs every database
  store in one transaction. Revision payloads are removed only through the definer
  impact.privacy_remove_revisions under the revision_removal_guard trigger (deletion_ledger rows,
  no active hold). Held items are left in place and reported. Object-store bytes are deleted after
  the commit (no external call inside a transaction) and recorded in a second transaction; a
  failed deletion leaves the case PartiallyCompleted and `execute` can be repeated for it.

What erasure keeps, deliberately: the subject's principal and membership identifiers (pseudonymous
keys that audit, grants, review independence and official results refer to), audit events, and
every observation, calculated result, snapshot and report (approved official numbers are never
altered). The platform identity (sign-in account, sessions, identity profile) is outside the tenant
and outside this case.

Every case operation is purpose-bound: the request names its purpose and a grant for the
capability with exactly that purpose (TENANT scope) is required; a purpose-less grant never
authorises a privacy operation."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from psycopg.types.json import Jsonb

from .contracts import validate
from .domain import DomainError, unavailable
from .retention import effective
from .store import audit, authorize, canonical, context, envelope, hash_data, load, write

ERASED_NAME = "Erased member"
ERASED_MASK = "[erased]"
PACKAGE_DAYS = 7
SECTION_LIMIT = 1000
PLAN_LIMIT = 2000
SECTIONS = [
    "subject",
    "invitations",
    "grants",
    "role_assignments",
    "notifications",
    "uploads",
    "authored_records",
    "audit_events",
]
FINAL = {"Completed", "PartiallyCompleted"}


def now():
    return datetime.now(timezone.utc)


def iso(value):
    return value.isoformat() if value else None


def refuse(reason, status=422, code="VALIDATION_FAILED"):
    raise DomainError(code, status, reason=reason)


class Privacy:
    def __init__(self, service):
        self.service, self.s, self.db = service, service.s, service.db

    @property
    def store(self):
        return self.service.evidence.store

    # ---- authorisation -------------------------------------------------------------------

    def authorize(self, c, ctx, op, purpose, hidden=False):
        """Purpose-bound authorisation: a TENANT-scope grant for the capability whose purpose is
        exactly the declared one; then fresh assurance as for every sensitive operation. One
        mechanism with the audit export: store.authorize, in its exact-purpose mode."""
        authorize(c, ctx, op, hidden=hidden, purpose=purpose, exact_purpose=True)

    # ---- subject -------------------------------------------------------------------------

    def subject(self, c, ctx, membership_id):
        """The subject membership of this tenant and its principal; anything else is unavailable."""
        member = c.execute(
            "SELECT r.object_id,r.lifecycle_state,r.created_at,m.identity_id,m.external,m.expires_at,m.status,"
            "m.joined_at,p.principal_id FROM impact.object_registry r JOIN impact.membership_current m "
            "ON m.tenant_id=r.tenant_id AND m.object_id=r.object_id JOIN impact.tenant_principal p "
            "ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id WHERE r.tenant_id=%s AND r.object_id=%s "
            "AND r.object_type='Membership'",
            (ctx.tenant_id, str(membership_id)),
        ).fetchone()
        if not member:
            refuse("SUBJECT_NOT_A_MEMBER")
        return member

    def owned_objects(self, c, ctx, kind, ids, principal):
        """Evidence or import batches the privacy officer names must be the subject's own: created
        or owned by the subject's principal. Import batches must be finished (Committed/Cancelled)."""
        rows = []
        for obj in ids or []:
            row = c.execute(
                "SELECT object_id,object_type,lifecycle_state,created_by,owner_id FROM impact.object_registry "
                "WHERE tenant_id=%s AND object_id=%s",
                (ctx.tenant_id, obj),
            ).fetchone()
            if (
                not row
                or row["object_type"] != kind
                or principal not in {str(row["created_by"]), str(row["owner_id"])}
            ):
                refuse("NOT_SUBJECT_DATA")
            if kind == "ImportJob" and row["lifecycle_state"] not in {"Committed", "Cancelled"}:
                refuse("IMPORT_NOT_FINISHED", 409, "INVALID_STATE")
            rows.append(row)
        return rows

    def check_draft(self, c, ctx, data):
        member = self.subject(c, ctx, data["subject_membership_id"])
        if data["request_type"] == "ACCESS" and (data.get("evidence_ids") or data.get("import_ids")):
            refuse("ERASURE_SCOPE_ONLY")
        principal = str(member["principal_id"])
        self.owned_objects(c, ctx, "Evidence", data.get("evidence_ids"), principal)
        self.owned_objects(c, ctx, "ImportJob", data.get("import_ids"), principal)
        return member

    def erasable(self, c, ctx, member):
        if member["lifecycle_state"] in {"Active", "Suspended"}:
            refuse("SUBJECT_STILL_ACTIVE", 409, "INVALID_STATE")
        if c.execute(
            "SELECT 1 FROM impact.tenant_custody WHERE tenant_id=%s AND owner_membership_id=%s",
            (ctx.tenant_id, member["object_id"]),
        ).fetchone():
            refuse("SUBJECT_HOLDS_CUSTODY", 409, "INVALID_STATE")

    # ---- plan ----------------------------------------------------------------------------

    def invitations(self, c, ctx, membership_id):
        """Invitations addressed to the subject: the one they accepted and every other invitation
        of this tenant to the same e-mail address (matched by its stored hash)."""
        return c.execute(
            "SELECT i.invitation_id,i.consumed_at,i.revoked_at FROM impact.member_invitation i WHERE i.tenant_id=%s AND "
            "(i.accepted_membership_id=%s OR i.intended_email_hash IN (SELECT x.intended_email_hash FROM "
            "impact.member_invitation x WHERE x.tenant_id=%s AND x.accepted_membership_id=%s)) ORDER BY i.invitation_id",
            (ctx.tenant_id, str(membership_id), ctx.tenant_id, str(membership_id)),
        ).fetchall()

    def holds(self, c, ctx, ids):
        if not ids:
            return {}
        rows = c.execute(
            "SELECT object_id,min(review_at) AS review_at FROM impact.retention_hold WHERE tenant_id=%s "
            "AND object_id=ANY(%s::uuid[]) AND released_at IS NULL GROUP BY object_id",
            (ctx.tenant_id, [str(i) for i in ids]),
        ).fetchall()
        return {str(r["object_id"]): r["review_at"] for r in rows}

    def evidence_blobs(self, c, ctx, evidence_id):
        """Blobs behind every revision of one evidence object, and whether any other evidence
        revision that is still available uses the same blob."""
        rows = c.execute(
            "SELECT DISTINCT b.blob_id,b.purged_at,EXISTS(SELECT 1 FROM impact.object_revision v2 "
            "JOIN impact.upload_session u2 ON u2.tenant_id=v2.tenant_id AND u2.upload_id=(v2.payload->>'upload_id')::uuid "
            "WHERE v2.tenant_id=b.tenant_id AND v2.object_type='Evidence' AND v2.object_id<>%s "
            "AND v2.restriction_state='AVAILABLE' AND u2.blob_id=b.blob_id) AS shared "
            "FROM impact.object_revision v JOIN impact.upload_session u ON u.tenant_id=v.tenant_id "
            "AND u.upload_id=(v.payload->>'upload_id')::uuid JOIN impact.file_blob b ON b.tenant_id=u.tenant_id "
            "AND b.blob_id=u.blob_id WHERE v.tenant_id=%s AND v.object_id=%s AND v.object_type='Evidence' "
            "AND v.payload ? 'upload_id' ORDER BY b.blob_id",
            (str(evidence_id), ctx.tenant_id, str(evidence_id)),
        ).fetchall()
        return rows

    def plan(self, c, ctx, case):
        """(entries, sha256 hex, extras) for the case as the data stands now. Entries are sorted
        dicts {store, action, object_id, object_type, state, reason, hold_review_at}."""
        data = case["payload"]
        member = self.subject(c, ctx, data["subject_membership_id"])
        membership, principal = str(member["object_id"]), str(member["principal_id"])
        entries, extras = [], {"object_store": {}}
        if data["request_type"] == "ERASURE":

            def add(store, action, obj, kind, state="APPROVED", reason=None):
                entries.append(
                    {
                        "store": store,
                        "action": action,
                        "object_id": str(obj),
                        "object_type": kind,
                        "state": state,
                        "reason": reason,
                        "hold_review_at": None,
                    }
                )

            profile = c.execute(
                "SELECT display_name,email_mask FROM impact.member_profile WHERE tenant_id=%s AND membership_id=%s",
                (ctx.tenant_id, membership),
            ).fetchone()
            if profile and (profile["display_name"] != ERASED_NAME or profile["email_mask"] is not None):
                add("MEMBER_PROFILE", "REDACT", membership, "Membership")
            references = []
            for invitation in self.invitations(c, ctx, membership):
                obj = str(invitation["invitation_id"])
                references.append((obj, "EntitlementApproval"))
                register = c.execute(
                    "SELECT intended_subject IS NOT NULL OR NOT EXISTS(SELECT 1 FROM impact.deletion_ledger d "
                    "WHERE d.tenant_id=%s AND d.object_id=%s) AS open FROM impact.member_invitation "
                    "WHERE tenant_id=%s AND invitation_id=%s",
                    (ctx.tenant_id, obj, ctx.tenant_id, obj),
                ).fetchone()
                if register["open"]:
                    add("INVITATION_REGISTER", "REDACT", obj, "EntitlementApproval")
                if c.execute(
                    "SELECT 1 FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND "
                    "restriction_state='AVAILABLE' AND payload->>'email_mask' IS DISTINCT FROM %s LIMIT 1",
                    (ctx.tenant_id, obj, ERASED_MASK),
                ).fetchone():
                    add("DATABASE", "DELETE", obj, "EntitlementApproval")
            for notice in c.execute(
                "SELECT object_id FROM impact.notification_current WHERE tenant_id=%s AND recipient_id=%s "
                "ORDER BY object_id",
                (ctx.tenant_id, principal),
            ).fetchall():
                references.append((str(notice["object_id"]), "Notification"))
            for obj, kind in references:
                if c.execute(
                    "SELECT 1 FROM impact.outbox_delivery WHERE tenant_id=%s AND reference_id=%s AND channel IS NOT NULL "
                    "AND (state IN ('PENDING','LEASED') OR (channel='EMAIL' AND recipient_redacted_at IS NULL)) LIMIT 1",
                    (ctx.tenant_id, obj),
                ).fetchone():
                    add("OUTBOX", "SUPERSEDE", obj, kind)
            for row in self.owned_objects(c, ctx, "Evidence", data.get("evidence_ids"), principal):
                obj = str(row["object_id"])
                available = c.execute(
                    "SELECT 1 FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
                    "AND restriction_state='AVAILABLE' LIMIT 1",
                    (ctx.tenant_id, obj),
                ).fetchone()
                if available:
                    add("PROJECTION", "REDACT", obj, "Evidence")
                    add("DATABASE", "DELETE", obj, "Evidence")
                blobs = [b for b in self.evidence_blobs(c, ctx, obj) if not b["purged_at"]]
                if blobs:
                    shared = any(b["shared"] for b in blobs)
                    add(
                        "OBJECT_STORE",
                        "DELETE",
                        obj,
                        "Evidence",
                        "HELD" if shared else "APPROVED",
                        "SHARED_CONTENT" if shared else None,
                    )
                    extras["object_store"][obj] = [str(b["blob_id"]) for b in blobs]
            for row in self.owned_objects(c, ctx, "ImportJob", data.get("import_ids"), principal):
                obj = str(row["object_id"])
                if c.execute(
                    "SELECT 1 FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
                    "AND restriction_state='AVAILABLE' LIMIT 1",
                    (ctx.tenant_id, obj),
                ).fetchone():
                    add("PROJECTION", "REDACT", obj, "ImportJob")
                    add("DATABASE", "DELETE", obj, "ImportJob")
            held = self.holds(c, ctx, {e["object_id"] for e in entries})
            for entry in entries:
                if entry["object_id"] in held:
                    entry.update(
                        state="HELD", reason="RETENTION_HOLD", hold_review_at=iso(held[entry["object_id"]])
                    )
            entries.sort(key=lambda e: (e["store"], e["object_id"]))
            if len(entries) > PLAN_LIMIT:
                # One case runs in one bounded request transaction; a larger footprint is refused.
                raise DomainError("LIMIT_EXCEEDED", 422, reason="PRIVACY_PLAN_TOO_LARGE")
        digest = hash_data(
            {
                "case_id": str(case["object_id"]),
                "request_type": data["request_type"],
                "subject": [membership, principal],
                "sections": SECTIONS if data["request_type"] == "ACCESS" else None,
                "entries": [
                    [e["store"], e["action"], e["object_id"], e["state"], e["reason"]] for e in entries
                ],
            }
        ).hex()
        return entries, digest, {**extras, "member": member}

    # ---- commands ------------------------------------------------------------------------

    def command(self, identity, tenant, op, schema, body, correlation, obj, handler):
        """The domain command skeleton of Service.command with purpose-bound authorisation."""
        validate(schema, body)
        fingerprint = hash_data([op, obj, body])
        at = now()
        after = None
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            self.authorize(c, ctx, op, body["data"]["purpose"], hidden=bool(obj))
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= at:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            previous = load(c, ctx, obj, "PrivacyCase", lock=True) if obj else None
            if previous and str(previous["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            receipt, after = handler(c, ctx, previous, body["data"])
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    at + timedelta(days=7),
                ),
            )
        if after:
            after(identity, tenant, receipt["object_id"], correlation)
        return receipt

    def create(self, identity, tenant, body, correlation):
        def handler(c, ctx, previous, data):
            member = self.check_draft(c, ctx, data)
            payload = {**data, "subject_principal_id": str(member["principal_id"])}
            return write(c, ctx, "PrivacyCase", payload, "Draft"), None

        return self.command(
            identity, tenant, "create_privacy_cases", "PrivacyCaseCreate", body, correlation, None, handler
        )

    def patch(self, identity, tenant, obj, body, correlation):
        def handler(c, ctx, previous, data):
            if previous["lifecycle_state"] != "Draft":
                raise DomainError("INVALID_STATE", 409)
            payload = {**previous["payload"], **data}
            member = self.check_draft(c, ctx, payload)
            payload["subject_principal_id"] = str(member["principal_id"])
            return write(c, ctx, "PrivacyCase", payload, "Draft", previous), None

        return self.command(
            identity, tenant, "patch_privacy_cases", "PrivacyCasePatch", body, correlation, obj, handler
        )

    def action(self, identity, tenant, obj, action, body, correlation):
        if action == "approve":
            return self.command(
                identity,
                tenant,
                "action_privacy_cases_approve",
                "ActionPrivacyCasesApprove",
                body,
                correlation,
                obj,
                self.approve,
            )
        if action == "execute":
            return self.command(
                identity,
                tenant,
                "action_privacy_cases_execute",
                "ActionPrivacyCasesExecute",
                body,
                correlation,
                obj,
                self.execute,
            )
        unavailable()

    def approve(self, c, ctx, previous, data):
        if previous["lifecycle_state"] != "Draft":
            raise DomainError("INVALID_STATE", 409)
        payload = previous["payload"]
        member = self.check_draft(c, ctx, payload)
        authors = {
            str(r["natural_identity_id"])
            for r in c.execute(
                "SELECT natural_identity_id FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s",
                (ctx.tenant_id, previous["object_id"]),
            ).fetchall()
        }
        subject = c.execute(
            "SELECT impact.member_natural_identity(%s,%s) AS person",
            (ctx.tenant_id, str(member["principal_id"])),
        ).fetchone()["person"]
        if not subject or ctx.identity.natural_identity_id in authors | {str(subject)}:
            raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
        if payload["request_type"] == "ERASURE":
            self.erasable(c, ctx, member)
        entries, digest, _ = self.plan(c, ctx, previous)
        if digest != data["plan_sha256"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="PLAN_CHANGED")
        for entry in entries:
            c.execute(
                "INSERT INTO impact.privacy_store_action(tenant_id,case_id,object_id,store,action,state,plan_hash) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    previous["object_id"],
                    entry["object_id"],
                    entry["store"],
                    entry["action"],
                    entry["state"],
                    bytes.fromhex(digest),
                ),
            )
        approved = {
            **payload,
            "approved_by": ctx.principal_id,
            "approved_at": now().isoformat(),
            "approved_revision": str(previous["head_revision"]),
            "plan_sha256": digest,
        }
        return write(c, ctx, "PrivacyCase", approved, "Approved", previous, track_author=False), None

    def execute(self, c, ctx, previous, data):
        payload = previous["payload"]
        if data["approved_plan_hash"] != payload.get("plan_sha256"):
            raise DomainError("CONFLICT_VERSION", 409, reason="PLAN_CHANGED")
        state = previous["lifecycle_state"]
        if state in {"Executing", "PartiallyCompleted"} and payload["request_type"] == "ERASURE":
            # Only the object-store deletions that were pending or failed are attempted again.
            retried = c.execute(
                "UPDATE impact.privacy_store_action SET state='EXECUTING' WHERE tenant_id=%s AND case_id=%s "
                "AND store='OBJECT_STORE' AND state IN ('EXECUTING','FAILED') RETURNING object_id",
                (ctx.tenant_id, previous["object_id"]),
            ).fetchall()
            if not retried:
                raise DomainError("INVALID_STATE", 409, reason="NOTHING_TO_RETRY")
            row = load(c, ctx, previous["object_id"], "PrivacyCase")
            receipt = {
                "operation_id": "",
                "object_id": str(row["object_id"]),
                "revision_id": str(row["head_revision"]),
                "business_state": row["lifecycle_state"],
                "saved_at": now().isoformat(),
                "correlation_id": "",
            }
            return receipt, self.purge_objects
        if state != "Approved":
            raise DomainError("INVALID_STATE", 409)
        entries, digest, extras = self.plan(c, ctx, previous)
        if digest != payload["plan_sha256"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="PLAN_CHANGED")
        if payload["request_type"] == "ACCESS":
            return self.export(c, ctx, previous, extras["member"]), None
        self.erasable(c, ctx, extras["member"])
        return self.erase(c, ctx, previous, entries, extras)

    # ---- erasure -------------------------------------------------------------------------

    def head(self, c, ctx, obj):
        return c.execute(
            "SELECT r.*,v.payload,v.revision_number FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s "
            "FOR UPDATE OF r",
            (ctx.tenant_id, obj),
        ).fetchone()

    def erase(self, c, ctx, case, entries, extras):
        case_id = str(case["object_id"])
        tenant = ctx.tenant_id
        runnable = [e for e in entries if e["state"] != "HELD"]
        for entry in runnable:
            c.execute(
                "UPDATE impact.privacy_store_action SET state='EXECUTING' WHERE tenant_id=%s AND case_id=%s "
                "AND object_id=%s AND store=%s",
                (tenant, case_id, entry["object_id"], entry["store"]),
            )
        by_store = {}
        for entry in runnable:
            by_store.setdefault(entry["store"], []).append(entry)
        counts = {}
        for entry in by_store.get("MEMBER_PROFILE", []):
            counts["member_profile"] = c.execute(
                "UPDATE impact.member_profile SET display_name=%s,email_mask=NULL WHERE tenant_id=%s AND membership_id=%s",
                (ERASED_NAME, tenant, entry["object_id"]),
            ).rowcount
        for entry in by_store.get("INVITATION_REGISTER", []):
            counts["invitation_register"] = (
                counts.get("invitation_register", 0)
                + c.execute(
                    "UPDATE impact.member_invitation SET intended_email_hash=sha256(convert_to(gen_random_uuid()::text,'UTF8')),"
                    "intended_subject=NULL,revoked_at=CASE WHEN consumed_at IS NULL AND revoked_at IS NULL THEN now() "
                    "ELSE revoked_at END WHERE tenant_id=%s AND invitation_id=%s",
                    (tenant, entry["object_id"]),
                ).rowcount
            )
        removed = 0
        for entry in by_store.get("DATABASE", []):
            if entry["object_type"] != "EntitlementApproval":
                continue
            head = self.head(c, ctx, entry["object_id"])
            tombstone = {
                **(head["payload"] or {}),
                "email_mask": ERASED_MASK,
                "erased_by_case": case_id,
            }
            state = "Revoked" if head["lifecycle_state"] == "Invited" else head["lifecycle_state"]
            kept = write(c, ctx, "EntitlementApproval", tombstone, state, head, track_author=False)
            removed += c.execute(
                "SELECT impact.privacy_remove_revisions(%s,%s,%s) AS n",
                (case_id, entry["object_id"], kept["revision_id"]),
            ).fetchone()["n"]
        for entry in by_store.get("OUTBOX", []):
            counts["outbox"] = (
                counts.get("outbox", 0)
                + c.execute(
                    "SELECT impact.privacy_supersede_deliveries(%s,%s) AS n", (case_id, entry["object_id"])
                ).fetchone()["n"]
            )
        for entry in by_store.get("PROJECTION", []):
            if entry["object_type"] == "Evidence":
                c.execute("SELECT impact.privacy_redact_uploads(%s,%s)", (case_id, entry["object_id"]))
                c.execute(
                    "UPDATE impact.evidence_current SET filename=NULL,media_type=NULL,byte_size=NULL,"
                    "external_reference=NULL,source=NULL,integrity_sha256=NULL WHERE tenant_id=%s AND object_id=%s",
                    (tenant, entry["object_id"]),
                )
            else:
                c.execute(
                    "UPDATE impact.import_job_current SET content=NULL,preview=NULL,file_name=NULL "
                    "WHERE tenant_id=%s AND object_id=%s",
                    (tenant, entry["object_id"]),
                )
        for entry in by_store.get("DATABASE", []):
            if entry["object_type"] == "EntitlementApproval":
                continue
            removed += c.execute(
                "SELECT impact.privacy_remove_revisions(%s,%s,NULL) AS n", (case_id, entry["object_id"])
            ).fetchone()["n"]
        counts["revisions_removed"] = removed
        c.execute(
            "UPDATE impact.privacy_store_action SET state='COMPLETED' WHERE tenant_id=%s AND case_id=%s "
            "AND state='EXECUTING' AND store<>'OBJECT_STORE'",
            (tenant, case_id),
        )
        pending = [e for e in runnable if e["store"] == "OBJECT_STORE"]
        held = [
            {
                "object_id": e["object_id"],
                "store": e["store"],
                "reason": e["reason"],
                "hold_review_at": e["hold_review_at"],
            }
            for e in entries
            if e["state"] == "HELD"
        ]
        manifest = {
            "entries": len(entries),
            "counts": counts,
            "held": held,
            "object_store": extras["object_store"],
            "kept": [
                "principal and membership identifiers",
                "audit events",
                "observations, calculated results, snapshots and reports",
                "platform identity (outside the tenant)",
            ],
        }
        stamp = now().isoformat()
        result = {
            **case["payload"],
            "executed_by": ctx.principal_id,
            "executed_at": stamp,
            "manifest": manifest,
        }
        if pending:
            return write(
                c, ctx, "PrivacyCase", result, "Executing", case, track_author=False
            ), self.purge_objects
        outcome = "PARTIALLY_COMPLETED" if held else "COMPLETED"
        result.update(outcome=outcome, completed_at=stamp)
        state = "PartiallyCompleted" if held else "Completed"
        return write(c, ctx, "PrivacyCase", result, state, case, track_author=False), None

    def purge_objects(self, identity, tenant, case_id, correlation):
        """After the erasure commit: delete the evidence bytes the plan names, then record each
        store outcome and the case's final state in a second transaction."""
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            case = load(c, ctx, case_id, "PrivacyCase")
            mapping = (case["payload"].get("manifest") or {}).get("object_store", {})
            pending = c.execute(
                "SELECT object_id FROM impact.privacy_store_action WHERE tenant_id=%s AND case_id=%s "
                "AND store='OBJECT_STORE' AND state='EXECUTING' ORDER BY object_id",
                (tenant, case_id),
            ).fetchall()
            work = {}
            for row in pending:
                ids = mapping.get(str(row["object_id"]), [])
                work[str(row["object_id"])] = (
                    c.execute(
                        "SELECT blob_id,object_key FROM impact.file_blob WHERE tenant_id=%s AND blob_id=ANY(%s::uuid[]) "
                        "ORDER BY blob_id",
                        (tenant, ids),
                    ).fetchall()
                    if ids
                    else []
                )
        outcomes = {}
        for obj, blobs in work.items():
            if not self.store:
                outcomes[obj] = ("FAILED", "OBJECT_STORE_NOT_CONFIGURED", [])
                continue
            try:
                deleted = [
                    {"blob_id": str(b["blob_id"]), "removed": self.store.delete(b["object_key"])}
                    for b in blobs
                ]
                outcomes[obj] = ("COMPLETED", None, deleted)
            except (OSError, ValueError) as exc:
                outcomes[obj] = ("FAILED", "OBJECT_DELETE_" + type(exc).__name__.upper()[:40], [])
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            case = load(c, ctx, case_id, "PrivacyCase", lock=True)
            for obj, (state, error, deleted) in outcomes.items():
                c.execute(
                    "UPDATE impact.privacy_store_action SET state=%s WHERE tenant_id=%s AND case_id=%s "
                    "AND object_id=%s AND store='OBJECT_STORE' AND state='EXECUTING'",
                    (state, tenant, case_id, obj),
                )
                if state == "COMPLETED" and deleted:
                    c.execute(
                        "UPDATE impact.file_blob SET purged_at=now(),purge_case_id=%s WHERE tenant_id=%s "
                        "AND blob_id=ANY(%s::uuid[]) AND purged_at IS NULL",
                        (case_id, tenant, [d["blob_id"] for d in deleted]),
                    )
            states = {
                r["state"]
                for r in c.execute(
                    "SELECT state FROM impact.privacy_store_action WHERE tenant_id=%s AND case_id=%s",
                    (tenant, case_id),
                ).fetchall()
            }
            payload = dict(case["payload"])
            manifest = dict(payload.get("manifest") or {})
            manifest["object_store_results"] = {
                **manifest.get("object_store_results", {}),
                **{
                    obj: {"state": state, "error_class": error, "blobs": deleted}
                    for obj, (state, error, deleted) in outcomes.items()
                },
            }
            payload["manifest"] = manifest
            if "EXECUTING" in states:
                return
            partial = bool(states & {"HELD", "FAILED"})
            stamp = now().isoformat()
            payload.update(outcome="PARTIALLY_COMPLETED" if partial else "COMPLETED", completed_at=stamp)
            receipt = write(
                c,
                ctx,
                "PrivacyCase",
                payload,
                "PartiallyCompleted" if partial else "Completed",
                case,
                track_author=False,
            )
            receipt.update(correlation_id=correlation)
            audit(c, ctx, "privacy.object_store_purge", receipt, correlation)

    # ---- access export -------------------------------------------------------------------

    def sections(self, c, ctx, member):
        tenant, membership, principal = ctx.tenant_id, str(member["object_id"]), str(member["principal_id"])
        profile = (
            c.execute(
                "SELECT display_name,email_mask FROM impact.member_profile WHERE tenant_id=%s AND membership_id=%s",
                (tenant, membership),
            ).fetchone()
            or {}
        )
        sections = {
            "subject": [
                {
                    "membership_id": membership,
                    "principal_id": principal,
                    "identity_id": str(member["identity_id"]),
                    "membership_state": member["lifecycle_state"],
                    "external": member["external"],
                    "joined_at": iso(member["joined_at"]),
                    "expires_at": iso(member["expires_at"]),
                    "display_name": profile.get("display_name"),
                    "email_mask": profile.get("email_mask"),
                }
            ]
        }
        invitations = []
        for invitation in self.invitations(c, ctx, membership):
            head = c.execute(
                "SELECT r.lifecycle_state,r.created_at,v.payload FROM impact.object_registry r JOIN impact.object_revision v "
                "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
                (tenant, invitation["invitation_id"]),
            ).fetchone()
            data = (head and head["payload"]) or {}
            invitations.append(
                {
                    "invitation_id": str(invitation["invitation_id"]),
                    "state": head["lifecycle_state"] if head else None,
                    "created_at": iso(head["created_at"]) if head else None,
                    "email_mask": data.get("email_mask"),
                    "role_name": data.get("role_name"),
                    "expires_at": data.get("expires_at"),
                    "membership_expires_at": data.get("membership_expires_at"),
                    "accepted": invitation["consumed_at"] is not None,
                }
            )
        sections["invitations"] = invitations
        bounded = " LIMIT " + str(SECTION_LIMIT + 1)
        sections["grants"] = [
            {
                "grant_id": str(r["object_id"]),
                "capability": r["capability"],
                "scope_id": str(r["scope_id"]),
                "purpose": r["purpose"],
                "starts_at": iso(r["starts_at"]),
                "expires_at": iso(r["expires_at"]),
                "state": r["lifecycle_state"],
            }
            for r in c.execute(
                "SELECT g.object_id,g.capability,g.scope_id,g.purpose,g.starts_at,g.expires_at,r.lifecycle_state "
                "FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id "
                "WHERE g.tenant_id=%s AND g.subject_id=%s ORDER BY g.capability,g.object_id" + bounded,
                (tenant, principal),
            ).fetchall()
        ]
        sections["role_assignments"] = [
            {
                "assignment_id": str(r["assignment_id"]),
                "role_name": (r["payload"] or {}).get("name"),
                "scope_id": str(r["scope_id"]),
                "expires_at": iso(r["expires_at"]),
            }
            for r in c.execute(
                "SELECT a.assignment_id,a.scope_id,a.expires_at,v.payload FROM impact.member_role_assignment a "
                "JOIN impact.object_revision v ON v.tenant_id=a.tenant_id AND v.revision_id=a.role_revision "
                "WHERE a.tenant_id=%s AND a.membership_id=%s ORDER BY a.assignment_id" + bounded,
                (tenant, membership),
            ).fetchall()
        ]
        sections["notifications"] = [
            {
                "notification_id": str(r["object_id"]),
                "notice_class": r["notice_class"],
                "state": r["lifecycle_state"],
                "created_at": iso(r["created_at"]),
            }
            for r in c.execute(
                "SELECT n.object_id,n.notice_class,r.lifecycle_state,r.created_at FROM impact.notification_current n "
                "JOIN impact.object_registry r ON r.tenant_id=n.tenant_id AND r.object_id=n.object_id "
                "WHERE n.tenant_id=%s AND n.recipient_id=%s ORDER BY r.created_at,n.object_id" + bounded,
                (tenant, principal),
            ).fetchall()
        ]
        sections["uploads"] = [
            {
                "upload_id": str(r["upload_id"]),
                "filename": r["filename"],
                "media_type": r["media_type"],
                "bytes": r["expected_bytes"],
                "state": r["state"],
                "created_at": iso(r["created_at"]),
            }
            for r in c.execute(
                "SELECT upload_id,filename,media_type,expected_bytes,state,created_at FROM impact.upload_session "
                "WHERE tenant_id=%s AND owner_id=%s ORDER BY created_at,upload_id" + bounded,
                (tenant, principal),
            ).fetchall()
        ]
        # Metadata only: the content of records a member authored is the organisation's, not personal.
        sections["authored_records"] = [
            {
                "object_id": str(r["object_id"]),
                "object_type": r["object_type"],
                "revision_number": r["revision_number"],
                "created_at": iso(r["created_at"]),
            }
            for r in c.execute(
                "SELECT object_id,object_type,revision_number,created_at FROM impact.object_revision "
                "WHERE tenant_id=%s AND author_id=%s AND object_type NOT IN ('AuditEvent','PrivacyCase') "
                "ORDER BY created_at,revision_id" + bounded,
                (tenant, principal),
            ).fetchall()
        ]
        sections["audit_events"] = [
            {
                "action_type": r["action_type"],
                "object_reference": str(r["object_reference"]) if r["object_reference"] else None,
                "outcome": r["outcome"],
                "occurred_at": iso(r["occurred_at"]),
            }
            for r in c.execute(
                "SELECT action_type,object_reference,outcome,occurred_at FROM impact.audit_event_current "
                "WHERE tenant_id=%s AND real_actor_id=%s ORDER BY occurred_at,object_id" + bounded,
                (tenant, principal),
            ).fetchall()
        ]
        return sections

    def export(self, c, ctx, case, member):
        at = now()
        sections = self.sections(c, ctx, member)
        manifest = {}
        for name in SECTIONS:
            items = sections[name]
            truncated = len(items) > SECTION_LIMIT
            sections[name] = items[:SECTION_LIMIT]
            manifest[name] = {
                "count": len(sections[name]),
                "complete": not truncated,
                "sha256": hashlib.sha256(canonical(sections[name])).hexdigest(),
            }
        package_id = str(uuid4())
        document = {
            "format": "impact-data-subject-export-v1",
            "package_id": package_id,
            "case_id": str(case["object_id"]),
            "tenant_id": ctx.tenant_id,
            "generated_at": at.isoformat(),
            "subject_membership_id": str(member["object_id"]),
            "sections": sections,
            "manifest": manifest,
            "limits": [
                "Personal data this workspace holds about the member; the sign-in account, sessions and "
                "identity profile belong to the platform identity and are not part of this package.",
                "Records the member authored are listed by identifier only; their content is the "
                "organisation's record.",
                "Each section holds at most " + str(SECTION_LIMIT) + " items; 'complete' is false when cut.",
            ],
        }
        body = canonical(document)
        if len(body) > 5242880:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="EXPORT_TOO_LARGE")
        digest = hashlib.sha256(body).digest()
        stamp = at.isoformat()
        payload = {
            **case["payload"],
            "executed_by": ctx.principal_id,
            "executed_at": stamp,
            "completed_at": stamp,
            "outcome": "COMPLETED",
            "package_id": package_id,
            "package_sha256": digest.hex(),
            "manifest": {"sections": manifest, "expires_at": (at + timedelta(days=PACKAGE_DAYS)).isoformat()},
        }
        receipt = write(c, ctx, "PrivacyCase", payload, "Completed", case, track_author=False)
        c.execute(
            "INSERT INTO impact.privacy_export_package(tenant_id,package_id,case_id,case_revision,subject_membership_id,"
            "body,content_sha256,manifest,created_by,created_at,expires_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                package_id,
                str(case["object_id"]),
                receipt["revision_id"],
                str(member["object_id"]),
                body,
                digest,
                Jsonb(manifest),
                ctx.principal_id,
                at,
                at + timedelta(days=PACKAGE_DAYS),
            ),
        )
        return receipt

    # ---- reads ---------------------------------------------------------------------------

    def read_context(self, c, identity, tenant, op, purpose, obj=None):
        ctx = context(c, identity, tenant)
        self.authorize(c, ctx, op, purpose, hidden=bool(obj))
        return ctx

    def listing(self, identity, tenant, purpose, limit=50, cursor=None):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.db.transaction(tenant) as c:
            ctx = self.read_context(c, identity, tenant, "list_privacy_cases", purpose)
            bound = self.service.cursor_binding(ctx, "privacy-cases")
            key = self.service.cursor_key(bound, cursor)
            query = (
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type='PrivacyCase' "
                "AND v.restriction_state='AVAILABLE'"
            )
            params = [tenant]
            if key:
                query += " AND (r.created_at,r.object_id)<(%s::timestamptz,%s::uuid)"
                params += key
            rows = c.execute(
                query + " ORDER BY r.created_at DESC,r.object_id DESC LIMIT %s", params + [limit + 1]
            ).fetchall()
            page = rows[:limit]
            return {
                "items": [envelope(r) for r in page],
                "next_cursor": self.service.next_cursor(
                    bound, [page[-1]["created_at"].isoformat(), str(page[-1]["object_id"])]
                )
                if len(rows) > limit
                else None,
                "scope_label": "Data-subject requests of this workspace (purpose: " + purpose + ")",
            }

    def get(self, identity, tenant, obj, purpose):
        with self.db.transaction(tenant) as c:
            ctx = self.read_context(c, identity, tenant, "get_privacy_cases", purpose, obj)
            return envelope(load(c, ctx, obj, "PrivacyCase"))

    def plan_view(self, identity, tenant, obj, purpose):
        with self.db.transaction(tenant) as c:
            ctx = self.read_context(c, identity, tenant, "get_privacy_case_plan", purpose, obj)
            case = load(c, ctx, obj, "PrivacyCase")
            data = case["payload"]
            approved = case["lifecycle_state"] != "Draft"
            if approved:
                entries = [
                    {
                        "store": r["store"],
                        "action": r["action"],
                        "object_id": str(r["object_id"]),
                        "object_type": r["object_type"],
                        "state": r["state"],
                        "reason": None,
                        "hold_review_at": None,
                    }
                    for r in c.execute(
                        "SELECT a.*,o.object_type FROM impact.privacy_store_action a JOIN impact.object_registry o "
                        "ON o.tenant_id=a.tenant_id AND o.object_id=a.object_id WHERE a.tenant_id=%s AND a.case_id=%s "
                        "ORDER BY a.store,a.object_id",
                        (tenant, obj),
                    ).fetchall()
                ]
                digest = data["plan_sha256"]
            else:
                entries, digest, _ = self.plan(c, ctx, case)
            result = {
                "case_id": str(case["object_id"]),
                "revision_id": str(case["head_revision"]),
                "request_type": data["request_type"],
                "subject_membership_id": data["subject_membership_id"],
                "subject_principal_id": data["subject_principal_id"],
                "plan_sha256": digest,
                "approved": approved,
                "entries": entries,
            }
            validate("PrivacyCasePlan", result)
            return result

    def download(self, identity, tenant, obj, purpose, correlation):
        with self.db.transaction(tenant) as c:
            ctx = self.read_context(c, identity, tenant, "read_privacy_case_export", purpose, obj)
            case = load(c, ctx, obj, "PrivacyCase")
            if case["payload"]["request_type"] != "ACCESS" or case["lifecycle_state"] != "Completed":
                unavailable()
            package = c.execute(
                "SELECT * FROM impact.privacy_export_package WHERE tenant_id=%s AND case_id=%s AND expires_at>now()",
                (tenant, obj),
            ).fetchone()
            if not package:
                raise DomainError("RESOURCE_UNAVAILABLE", 404, reason="EXPORT_EXPIRED")
            c.execute(
                "INSERT INTO impact.privacy_export_access(tenant_id,access_id,case_id,package_id,content_sha256,"
                "principal_id,membership_id,purpose,accessed_at,correlation_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,now(),%s)",
                (
                    tenant,
                    str(uuid4()),
                    obj,
                    package["package_id"],
                    package["content_sha256"],
                    ctx.principal_id,
                    ctx.membership_id,
                    purpose,
                    correlation,
                ),
            )
            audit(
                c,
                ctx,
                "read_privacy_case_export",
                {
                    "object_id": str(case["object_id"]),
                    "revision_id": str(case["head_revision"]),
                    "business_state": case["lifecycle_state"],
                    "saved_at": now().isoformat(),
                },
                correlation,
            )
            return {
                "body": bytes(package["body"]),
                "digest": bytes(package["content_sha256"]).hex(),
                "filename": "data-subject-export-" + str(obj) + ".json",
            }

    def retention_schedule(self, identity, tenant):
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_retention_schedule")
            # v0.27: the effective schedule (approved tenant policies over the fixed defaults).
            return {
                "items": effective(c, tenant),
                "next_cursor": None,
                "scope_label": "Effective retention schedule of this workspace",
            }

    def retention_proofs(self, identity, tenant):
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_retention_proofs")
            rows = c.execute(
                "SELECT * FROM impact.retention_proof WHERE tenant_id=%s ORDER BY executed_at DESC,data_class LIMIT 100",
                (tenant,),
            ).fetchall()
            return {
                "items": [
                    {
                        "proof_id": str(r["proof_id"]),
                        "job_id": str(r["job_id"]),
                        "lease_generation": r["lease_generation"],
                        "data_class": r["data_class"],
                        "action": r["action"],
                        "retention_days": r["retention_days"],
                        "cutoff": r["cutoff"].isoformat(),
                        "affected_count": r["affected_count"],
                        "items_sha256": bytes(r["items_sha256"]).hex(),
                        "executed_at": r["executed_at"].isoformat(),
                        "worker_id": r["worker_id"],
                    }
                    for r in rows
                ],
                "next_cursor": None,
                "scope_label": "Latest retention proof records of this workspace",
            }


def package_json(body):
    """Parse an export package (tests and tooling)."""
    return json.loads(body)
