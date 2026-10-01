"""Operator re-queue of outbox deliveries (control plane, platform API 1.5.0).

A platform operator, with fresh assurance and a stated reason, may re-queue a DEAD delivery or
release one held by a suspension, once the tenant is Active again. Nothing is replayed
automatically (FR-TEN-001): each row needs its own reviewed decision, recorded as a platform event
with a receipt. The control plane never reads the outbox directly; the SECURITY DEFINER functions of
migration 0025 expose the attention list without addresses or references and apply one fenced
transition, advancing the lease generation so a worker that still believes it holds the row
matches nothing. The worker still rechecks the intent before sending (an expired invitation or
challenge becomes SUPERSEDED, never sent).
"""

from datetime import timedelta
from uuid import uuid4
from psycopg.types.json import Jsonb
from .domain import DomainError, unavailable
from .requeue_contracts import ACTIONS, validate_body
from .store import hash_data
from .tenant_lifecycle import now

REASONS = {
    "STALE": None,
    "NOT_DEAD": "DELIVERY_NOT_DEAD",
    "NOT_HELD": "DELIVERY_NOT_HELD",
    "NOT_PENDING": "DELIVERY_NOT_PENDING",
}


def stamp(value):
    return value.isoformat() if value else None


def permitted(row):
    if row["lifecycle_state"] != "Active":
        return []
    if row["state"] == "DEAD":
        return ["requeue"]
    if row["held"] and row["state"] == "PENDING":
        return ["release"]
    return []


class DeliveryOperations:
    def __init__(self, lifecycle):
        self.lifecycle, self.db, self.s = lifecycle, lifecycle.db, lifecycle.s

    def directory(self, identity, tenant_id=None):
        if not self.s.platform_dsn:
            unavailable()
        with self.db.transaction(platform=True) as c:
            if not self.lifecycle.operator(c, identity):
                unavailable()
            rows = c.execute(
                "SELECT a.*,o.operating_name FROM impact.operator_delivery_attention(%s,50) a "
                "LEFT JOIN impact.tenant_onboarding o USING(tenant_id)",
                (tenant_id,),
            ).fetchall()
        return {
            "items": [
                {
                    "tenant_id": str(row["tenant_id"]),
                    "operating_name": row["operating_name"] or "Tenant " + str(row["tenant_id"])[:8],
                    "lifecycle_state": row["lifecycle_state"],
                    "event_id": str(row["event_id"]),
                    "channel": row["channel"],
                    "template": row["template"],
                    "state": row["state"],
                    "held": row["held"],
                    "attempts": row["attempts"],
                    "last_error_class": row["last_error_class"],
                    "last_attempt_at": stamp(row["last_attempt_at"]),
                    "completed_at": stamp(row["completed_at"]),
                    "revision": str(row["lease_generation"]),
                    "permitted_actions": permitted(row),
                }
                for row in rows
            ]
        }

    def command(self, identity, action, body, tenant_id, event_id):
        if action not in ACTIONS or not self.s.platform_dsn:
            unavailable()
        validate_body(body)
        self.lifecycle.assurance(identity)
        fingerprint = hash_data(
            {"delivery_action": action, "tenant": tenant_id, "event": event_id, "body": body}
        )
        with self.db.transaction(platform=True) as c:
            c.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
                ("platform:" + identity.identity_id + ":" + body["operation_id"],),
            )
            if not self.lifecycle.operator(c, identity):
                unavailable()
            # The shared tenant lock before any row lock, as every tenant write (LLD lock order).
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant_id,))
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_id,))
            tenant = c.execute(
                "SELECT lifecycle_state FROM impact.tenant_root WHERE tenant_id=%s FOR SHARE", (tenant_id,)
            ).fetchone()
            if not tenant:
                unavailable()
            old = c.execute(
                "SELECT * FROM impact.platform_receipt WHERE identity_id=%s AND operation_id=%s",
                (identity.identity_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["fingerprint"]) != fingerprint or old["expires_at"] <= now():
                    raise DomainError("CONFLICT_VERSION", 409, reason="OPERATION_REUSE")
                return old["response"]
            if tenant["lifecycle_state"] != "Active":
                raise DomainError("POLICY_DENIED", 403, reason="TENANT_NOT_ACTIVE")
            row = c.execute(
                "SELECT * FROM impact.operator_requeue_delivery(%s,%s,%s)",
                (event_id, action, int(body["expected_revision"])),
            ).fetchone()
            if row["outcome"] == "NOT_FOUND":
                unavailable()
            if row["outcome"] in REASONS:
                raise DomainError("CONFLICT_VERSION", 409, reason=REASONS[row["outcome"]])
            response = {
                "operation_id": body["operation_id"],
                "tenant_id": tenant_id,
                "event_id": event_id,
                "action": action,
                "state": row["state"],
                "held": row["held"],
                "attempts": row["attempts"],
                "previous_state": row["previous_state"],
                "previous_attempts": row["previous_attempts"],
                "previous_error_class": row["previous_error_class"],
                "revision": str(row["lease_generation"]),
                "reason": body["data"]["reason"],
            }
            c.execute(
                "INSERT INTO impact.platform_event(event_id,tenant_id,identity_id,action,revision_id,reason,payload) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    str(uuid4()),
                    tenant_id,
                    identity.identity_id,
                    "delivery-" + action,
                    str(uuid4()),
                    body["data"]["reason"],
                    Jsonb(response),
                ),
            )
            c.execute(
                "INSERT INTO impact.platform_receipt VALUES(%s,%s,%s,%s,%s)",
                (
                    identity.identity_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(response),
                    now() + timedelta(days=7),
                ),
            )
            return response
