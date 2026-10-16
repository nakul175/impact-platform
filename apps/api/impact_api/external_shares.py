"""Authenticated, expiring and revocable sharing of an exact derivative revision."""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from .domain import DomainError
from .store import authorize, context


def _uuid(value):
    try:
        return str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        raise DomainError("VALIDATION_FAILED", 400, reason="EXTERNAL_SHARE_INVALID") from None


class ExternalShares:
    def __init__(self, service, derivatives):
        self.service = service
        self.derivatives = derivatives

    def create(self, identity, tenant, body):
        if not isinstance(body, dict) or set(body) != {
            "derivative_id",
            "revision_id",
            "audience_principal_id",
            "actions",
            "reason",
            "expires_at",
        }:
            raise DomainError("VALIDATION_FAILED", 400, reason="EXTERNAL_SHARE_INVALID")
        derivative, revision, audience = (
            _uuid(body[k]) for k in ("derivative_id", "revision_id", "audience_principal_id")
        )
        actions = body["actions"]
        try:
            expires = datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))
        except (TypeError, ValueError, AttributeError):
            raise DomainError("VALIDATION_FAILED", 400, reason="EXTERNAL_SHARE_INVALID") from None
        now = datetime.now(timezone.utc)
        if (
            not isinstance(actions, list)
            or not actions
            or len(actions) > 8
            or any(a not in {"read", "download"} for a in actions)
            or len(set(actions)) != len(actions)
            or not isinstance(body["reason"], str)
            or not 1 <= len(body["reason"]) <= 500
            or not now < expires <= now + timedelta(days=7)
        ):
            raise DomainError("VALIDATION_FAILED", 400, reason="EXTERNAL_SHARE_INVALID")
        self.derivatives.read(identity, tenant, derivative, revision)
        share = str(uuid4())
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "create_external_share")
            target = c.execute(
                "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s AND active",
                (tenant, audience),
            ).fetchone()
            if not target:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            c.execute(
                "INSERT INTO impact.external_share(tenant_id,share_id,derivative_id,derivative_revision_id,audience_principal_id,actions,owner_principal_id,reason,expires_at,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,now())",
                (
                    tenant,
                    share,
                    derivative,
                    revision,
                    audience,
                    actions,
                    ctx.principal_id,
                    body["reason"],
                    expires,
                ),
            )
        return {
            "share_id": share,
            "derivative_id": derivative,
            "revision_id": revision,
            "audience_principal_id": audience,
            "actions": actions,
            "expires_at": expires.isoformat(),
        }

    def read(self, identity, tenant, share_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_external_share", hidden=True)
            row = c.execute(
                "SELECT derivative_id,derivative_revision_id,audience_principal_id,actions,expires_at,revoked_at FROM impact.external_share WHERE tenant_id=%s AND share_id=%s",
                (tenant, share_id),
            ).fetchone()
            if (
                not row
                or str(row["audience_principal_id"]) != str(ctx.principal_id)
                or row["revoked_at"] is not None
                or row["expires_at"] <= datetime.now(timezone.utc)
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
        derivative = self.derivatives.read(
            identity, tenant, str(row["derivative_id"]), str(row["derivative_revision_id"])
        )
        return {
            "share_id": share_id,
            "actions": row["actions"],
            "expires_at": row["expires_at"].isoformat(),
            "derivative": derivative,
        }

    def revoke(self, identity, tenant, share_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "revoke_external_share")
            row = c.execute(
                "SELECT owner_principal_id,revoked_at FROM impact.external_share WHERE tenant_id=%s AND share_id=%s FOR UPDATE",
                (tenant, share_id),
            ).fetchone()
            if not row:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if str(row["owner_principal_id"]) != str(ctx.principal_id):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if row["revoked_at"] is None:
                c.execute(
                    "UPDATE impact.external_share SET revoked_at=now(),revoked_by=%s WHERE tenant_id=%s AND share_id=%s",
                    (ctx.principal_id, tenant, share_id),
                )
        return {"share_id": share_id, "status": "REVOKED"}
