"""Tenant retention policies and retention holds (v0.27; FR-PRV-004, VF-PRV-002, FR-PRV-005).

Retention policy (registry kind RetentionPolicy, route `retention-policies`): a proposal names one
policy-able data class (retention.POLICY_BOUNDS), a duration inside the class's bounds and the
class's own action; it is a Draft until a second natural person approves it (`retention-policy
.approve`, 300 s fresh assurance). Approval is the only transition: it writes the Approved revision
and appends one row to the insert-only `retention_policy_binding` register, which the worker's
sweep reads (retention.effective) — the latest binding per class governs, the fixed schedule
otherwise. An approved policy is immutable; a later proposal for the same class is a new Draft
that may name the revision it `supersedes_revision`.

Retention hold (`retention-holds`): a hold on one object of this tenant with an authority
reference, a reason and a review date, effective at once (`retention.hold`, 300 s). The privacy
erasure plan reports a held object as HELD and the revision-removal guard refuses it (0003/0027).
A hold is released only by a natural person other than the one who placed it (`retention.release`,
300 s, INDEPENDENCE_REQUIRED) and a released hold is final (guard trigger, 0030). Holds placed
before this build (no placer) may be released by any holder of the capability.
"""

from datetime import datetime, timedelta
from uuid import uuid4

from psycopg.types.json import Jsonb

from .clock import now
from .contracts import validate
from .domain import DomainError, unavailable
from .retention import check_policy
from .store import audit, authorize, context, envelope, hash_data, load, write

KIND = "RetentionPolicy"
ROUTE = "retention-policies"
HOLD_ROUTE = "retention-holds"


def iso(value):
    return value.isoformat() if value else None


def natural_person(c, ctx, principal):
    row = c.execute(
        "SELECT impact.member_natural_identity(%s,%s) AS person", (ctx.tenant_id, str(principal))
    ).fetchone()
    return str(row["person"]) if row and row["person"] else None


class RetentionPolicies:
    def __init__(self, service):
        self.service, self.s, self.db = service, service.s, service.db

    # ---- command skeleton (Service.command without the generic dispatcher) ------------------

    def command(self, identity, tenant, op, schema, body, correlation, obj, kind, handler):
        validate(schema, body)
        fingerprint = hash_data([op, obj, body])
        at = now()
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, op, obj, hidden=bool(obj))
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
            previous = load(c, ctx, obj, kind, lock=True) if obj and kind else None
            if previous and str(previous["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            receipt = handler(c, ctx, previous, body["data"])
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
            return receipt

    # ---- retention policies ------------------------------------------------------------------

    def check(self, c, ctx, data):
        reason = check_policy(data.get("data_class"), data.get("duration_days"), data.get("expiry_action"))
        if reason:
            raise DomainError("VALIDATION_FAILED", reason=reason)
        if data.get("supersedes_revision"):
            row = c.execute(
                "SELECT r.object_id,r.object_type,g.lifecycle_state,g.head_revision FROM impact.object_revision r "
                "JOIN impact.object_registry g ON g.tenant_id=r.tenant_id AND g.object_id=r.object_id "
                "WHERE r.tenant_id=%s AND r.revision_id=%s",
                (ctx.tenant_id, data["supersedes_revision"]),
            ).fetchone()
            if not row or row["object_type"] != KIND or row["lifecycle_state"] != "Approved":
                raise DomainError("VALIDATION_FAILED", reason="SUPERSEDES_NOT_APPROVED")
            if str(row["head_revision"]) != data["supersedes_revision"]:
                raise DomainError("VALIDATION_FAILED", reason="SUPERSEDES_NOT_CURRENT")

    def create(self, identity, tenant, body, correlation):
        def handler(c, ctx, previous, data):
            self.check(c, ctx, data)
            return write(c, ctx, KIND, data, "Draft")

        return self.command(
            identity,
            tenant,
            "create_retention_policies",
            "RetentionPolicyCreate",
            body,
            correlation,
            None,
            KIND,
            handler,
        )

    def patch(self, identity, tenant, obj, body, correlation):
        def handler(c, ctx, previous, data):
            if previous["lifecycle_state"] != "Draft":
                raise DomainError("INVALID_STATE", 409)
            payload = {**previous["payload"], **data}
            self.check(c, ctx, payload)
            return write(c, ctx, KIND, payload, "Draft", previous)

        return self.command(
            identity,
            tenant,
            "patch_retention_policies",
            "RetentionPolicyPatch",
            body,
            correlation,
            obj,
            KIND,
            handler,
        )

    def approve(self, identity, tenant, obj, body, correlation):
        def handler(c, ctx, previous, data):
            if previous["lifecycle_state"] != "Draft":
                raise DomainError("INVALID_STATE", 409)
            payload = previous["payload"]
            self.check(c, ctx, payload)
            authors = {
                str(r["natural_identity_id"])
                for r in c.execute(
                    "SELECT natural_identity_id FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s",
                    (ctx.tenant_id, previous["object_id"]),
                ).fetchall()
            }
            if ctx.identity.natural_identity_id in authors:
                raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
            approved = {
                **payload,
                "approved_by": ctx.principal_id,
                "approved_at": now().isoformat(),
                "approved_revision": str(previous["head_revision"]),
            }
            receipt = write(c, ctx, KIND, approved, "Approved", previous, track_author=False)
            c.execute(
                "INSERT INTO impact.retention_policy_binding(tenant_id,binding_id,data_class,policy_id,policy_revision,"
                "duration_days,action,proposed_by,approved_by,approved_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    str(uuid4()),
                    payload["data_class"],
                    receipt["object_id"],
                    receipt["revision_id"],
                    payload["duration_days"],
                    payload["expiry_action"],
                    str(previous["created_by"]),
                    ctx.principal_id,
                    approved["approved_at"],
                ),
            )
            return receipt

        return self.command(
            identity,
            tenant,
            "action_retention_policies_approve",
            "ActionRetentionPoliciesApprove",
            body,
            correlation,
            obj,
            KIND,
            handler,
        )

    def listing(self, identity, tenant, limit=50, cursor=None):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_retention_policies")
            bound = self.service.cursor_binding(ctx, ROUTE)
            key = self.service.cursor_key(bound, cursor)
            query = (
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type=%s "
                "AND v.restriction_state='AVAILABLE'"
            )
            params = [tenant, KIND]
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
                "scope_label": "Retention policies of this workspace",
            }

    def get(self, identity, tenant, obj):
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_retention_policies", obj, hidden=True)
            return envelope(load(c, ctx, obj, KIND))

    # ---- retention holds ---------------------------------------------------------------------

    def place(self, identity, tenant, body, correlation):
        def handler(c, ctx, previous, data):
            # The object must exist in this tenant and be available; no content is returned, so the
            # TENANT-scope retention.hold grant (authorize) is the only visibility required.
            target = load(c, ctx, data["object_id"])
            review_at = datetime.fromisoformat(data["review_at"].replace("Z", "+00:00"))
            if review_at <= now():
                raise DomainError("VALIDATION_FAILED", reason="REVIEW_DATE_PAST")
            hold_id, at = str(uuid4()), now()
            c.execute(
                "INSERT INTO impact.retention_hold(tenant_id,hold_id,object_id,authority_reference,review_at,"
                "reason,placed_by,placed_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    hold_id,
                    str(target["object_id"]),
                    data["authority_reference"],
                    review_at,
                    data["reason"],
                    ctx.principal_id,
                    at,
                ),
            )
            # The receipt (and the audit event) name the held object and pin its current revision;
            # the hold itself is returned as hold_id (a hold is not a registry object).
            return {
                "operation_id": "",
                "object_id": str(target["object_id"]),
                "revision_id": str(target["head_revision"]),
                "business_state": "Held",
                "saved_at": at.isoformat(),
                "correlation_id": "",
                "hold_id": hold_id,
            }

        return self.command(
            identity,
            tenant,
            "create_retention_holds",
            "RetentionHoldCreate",
            body,
            correlation,
            None,
            None,
            handler,
        )

    def release(self, identity, tenant, hold_id, body, correlation):
        def handler(c, ctx, previous, data):
            hold = c.execute(
                "SELECT * FROM impact.retention_hold WHERE tenant_id=%s AND hold_id=%s FOR UPDATE",
                (ctx.tenant_id, str(hold_id)),
            ).fetchone()
            if not hold:
                unavailable()
            target = load(c, ctx, hold["object_id"])
            if hold["released_at"] is not None:
                raise DomainError("INVALID_STATE", 409, reason="HOLD_ALREADY_RELEASED")
            if hold["placed_by"] and natural_person(c, ctx, hold["placed_by"]) in {
                ctx.identity.natural_identity_id,
                None,
            }:
                raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
            at = now()
            c.execute(
                "UPDATE impact.retention_hold SET released_at=%s,released_by=%s,release_reason=%s "
                "WHERE tenant_id=%s AND hold_id=%s",
                (at, ctx.principal_id, data["reason"], ctx.tenant_id, str(hold_id)),
            )
            return {
                "operation_id": "",
                "object_id": str(target["object_id"]),
                "revision_id": str(target["head_revision"]),
                "business_state": "Released",
                "saved_at": at.isoformat(),
                "correlation_id": "",
                "hold_id": str(hold_id),
            }

        return self.command(
            identity,
            tenant,
            "action_retention_holds_release",
            "ActionRetentionHoldsRelease",
            body,
            correlation,
            str(hold_id),
            None,
            handler,
        )

    def holds(self, identity, tenant, limit=50):
        if not 1 <= limit <= 200:
            raise DomainError("VALIDATION_FAILED")
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_retention_holds")
            rows = c.execute(
                "SELECT h.*,r.object_type FROM impact.retention_hold h JOIN impact.object_registry r "
                "ON r.tenant_id=h.tenant_id AND r.object_id=h.object_id WHERE h.tenant_id=%s "
                "ORDER BY (h.released_at IS NULL) DESC,h.review_at,h.hold_id LIMIT %s",
                (tenant, limit),
            ).fetchall()
            return {
                "items": [
                    {
                        "hold_id": str(r["hold_id"]),
                        "object_id": str(r["object_id"]),
                        "object_type": r["object_type"],
                        "authority_reference": r["authority_reference"],
                        "reason": r["reason"],
                        "review_at": iso(r["review_at"]),
                        "placed_by": str(r["placed_by"]) if r["placed_by"] else None,
                        "placed_at": iso(r["placed_at"]),
                        "released_at": iso(r["released_at"]),
                        "released_by": str(r["released_by"]) if r["released_by"] else None,
                        "release_reason": r["release_reason"],
                    }
                    for r in rows
                ],
                "next_cursor": None,
                "scope_label": "Retention holds of this workspace (active first)",
            }
