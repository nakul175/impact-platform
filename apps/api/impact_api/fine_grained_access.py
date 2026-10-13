"""Attach strictly narrowing record and field facets to an existing approved grant."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data

CATEGORIES = {"PUBLIC", "INTERNAL", "SENSITIVE", "DIRECT_IDENTIFIER"}


def _invalid(reason="GRANT_FACET_INVALID"):
    raise DomainError("VALIDATION_FAILED", 400, reason=reason)


class FineGrainedAccess:
    def __init__(self, service):
        self.service = service

    def attach(self, identity, tenant, grant_id, body, correlation):
        if not isinstance(body, dict) or set(body) != {
            "operation_id",
            "record_object_ids",
            "readable_field_categories",
            "writable_field_categories",
        }:
            _invalid()
        try:
            operation_id = str(UUID(body["operation_id"]))
            grant_id = str(UUID(grant_id))
            record_ids = [str(UUID(value)) for value in body["record_object_ids"]]
        except (TypeError, ValueError, AttributeError):
            _invalid()
        readable, writable = body["readable_field_categories"], body["writable_field_categories"]
        if (
            not isinstance(body["record_object_ids"], list)
            or not 1 <= len(record_ids) <= 100
            or len(record_ids) != len(set(record_ids))
            or not isinstance(readable, list)
            or not 1 <= len(readable) <= len(CATEGORIES)
            or len(readable) != len(set(readable))
            or not set(readable) <= CATEGORIES
            or not isinstance(writable, list)
            or len(writable) != len(set(writable))
            or not set(writable) <= set(readable)
        ):
            _invalid()
        operation = "attach_fine_grained_grant_facets"
        fingerprint = hash_data([operation, grant_id, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, grant_id, hidden=True)
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, operation, operation_id),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            grant = c.execute(
                "SELECT g.*,s.scope_type FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id WHERE g.tenant_id=%s AND g.object_id=%s AND r.lifecycle_state='Active' AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now()) FOR SHARE OF g",
                (tenant, grant_id),
            ).fetchone()
            if not grant:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            visible_records = c.execute(
                "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s AND object_id=ANY(%s::uuid[]) AND lifecycle_state='Active' AND classification<>'RESTRICTED'",
                (tenant, record_ids),
            ).fetchone()["n"]
            if visible_records != len(record_ids):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if grant["scope_type"] != "TENANT":
                count = c.execute(
                    "SELECT count(*) AS n FROM impact.scope_member WHERE tenant_id=%s AND scope_id=%s AND object_id=ANY(%s::uuid[])",
                    (tenant, grant["scope_id"], record_ids),
                ).fetchone()["n"]
                if count != len(record_ids):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
            exists = c.execute(
                "SELECT 1 FROM impact.grant_access_facet WHERE tenant_id=%s AND grant_id=%s",
                (tenant, grant_id),
            ).fetchone()
            if exists:
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="GRANT_FACETS_ALREADY_ATTACHED")
            c.execute(
                "INSERT INTO impact.grant_access_facet VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (tenant, grant_id, record_ids, readable, writable, ctx.principal_id, now),
            )
            c.execute(
                "UPDATE impact.tenant_root SET policy_epoch=policy_epoch+1 WHERE tenant_id=%s", (tenant,)
            )
            c.execute(
                "UPDATE impact.tenant_principal SET subject_epoch=subject_epoch+1 WHERE tenant_id=%s AND principal_id=%s",
                (tenant, grant["subject_id"]),
            )
            outcome = {
                "grant_id": grant_id,
                "record_object_ids": record_ids,
                "readable_field_categories": readable,
                "writable_field_categories": writable,
                "attached_at": now.isoformat(),
            }
            audit(
                c,
                ctx,
                operation,
                {
                    "object_id": grant_id,
                    "revision_id": str(grant["revision_id"]),
                    "business_state": "Active",
                    "saved_at": now.isoformat(),
                },
                correlation,
            )
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    operation,
                    operation_id,
                    fingerprint,
                    Jsonb(outcome),
                    now + timedelta(days=7),
                ),
            )
            return outcome
