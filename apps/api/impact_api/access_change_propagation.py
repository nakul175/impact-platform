"""Short presentation leases bind online content to the current policy epoch."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .domain import DomainError
from .store import context


class AccessChangePropagation:
    def __init__(self, service, derivatives):
        self.service = service
        self.derivatives = derivatives

    def issue(self, identity, tenant, derivative_id, revision_id):
        self.derivatives.read(identity, tenant, derivative_id, revision_id)
        lease = str(uuid4())
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=60)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            c.execute(
                "INSERT INTO impact.presentation_lease(tenant_id,lease_id,principal_id,derivative_id,derivative_revision_id,policy_epoch,issued_at,expires_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    lease,
                    ctx.principal_id,
                    derivative_id,
                    revision_id,
                    ctx.policy_epoch,
                    now,
                    expires,
                ),
            )
        return {
            "lease_id": lease,
            "policy_epoch": ctx.policy_epoch,
            "expires_at": expires.isoformat(),
            "revalidate_after_seconds": 60,
        }

    def validate(self, identity, tenant, lease_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            row = c.execute(
                "SELECT principal_id,derivative_id,derivative_revision_id,policy_epoch,expires_at FROM impact.presentation_lease WHERE tenant_id=%s AND lease_id=%s",
                (tenant, lease_id),
            ).fetchone()
            if (
                not row
                or str(row["principal_id"]) != str(ctx.principal_id)
                or row["expires_at"] <= datetime.now(timezone.utc)
                or row["policy_epoch"] != ctx.policy_epoch
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
        self.derivatives.read(identity, tenant, str(row["derivative_id"]), str(row["derivative_revision_id"]))
        return {"lease_id": lease_id, "valid": True, "expires_at": row["expires_at"].isoformat()}
