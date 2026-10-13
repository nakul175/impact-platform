"""US-CM-02 accepted, time-bounded, no-charge sponsored access."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from psycopg.types.json import Jsonb
from .contracts import validate
from .domain import DomainError, unavailable
from .store import authorize, context, hash_data, write


def record_audit(c, ctx, action, reference, observed, correlation):
    write(
        c,
        ctx,
        "AuditEvent",
        {
            "real_actor_id": ctx.principal_id,
            "effective_actor_id": ctx.principal_id,
            "action_type": action,
            "object_reference": reference,
            "outcome": "SUCCEEDED",
            "occurred_at": observed.isoformat(),
            "correlation_id": correlation,
            "specification_ref": "US-CM-02",
        },
        "Recorded",
        track_author=False,
    )


class SponsoredAccess:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body, correlation):
        validate("SponsoredCohortCreate", body)
        fingerprint = hash_data(["create_sponsored_cohort", body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_sponsored_cohort")
            now = datetime.now(timezone.utc)
            op = body["operation_id"]
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type='create_sponsored_cohort' AND operation_id=%s",
                (tenant, ctx.principal_id, op),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            cohort = str(uuid4())
            c.execute(
                "INSERT INTO impact.sponsored_cohort VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    cohort,
                    body["title"],
                    body["duration_days"],
                    body["budget"],
                    body["currency"],
                    body["terms_version"],
                    ctx.principal_id,
                    now,
                ),
            )
            enrolments = []
            for grantee in body["grantee_tenant_ids"]:
                root = c.execute(
                    "SELECT lifecycle_state FROM impact.tenant_root WHERE tenant_id=%s", (grantee,)
                ).fetchone()
                if not root or root["lifecycle_state"] != "Active":
                    unavailable()
                eid = str(uuid4())
                enrolments.append({"enrolment_id": eid, "grantee_tenant_id": grantee, "status": "INVITED"})
                c.execute(
                    "INSERT INTO impact.sponsored_enrolment(sponsor_tenant_id,cohort_id,grantee_tenant_id,enrolment_id,duration_days,budget,currency,terms_version,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'INVITED')",
                    (
                        tenant,
                        cohort,
                        grantee,
                        eid,
                        body["duration_days"],
                        body["budget"],
                        body["currency"],
                        body["terms_version"],
                    ),
                )
            outcome = {
                "cohort_id": cohort,
                "title": body["title"],
                "duration_days": body["duration_days"],
                "budget": body["budget"],
                "currency": body["currency"],
                "terms_version": body["terms_version"],
                "enrolments": enrolments,
            }
            record_audit(c, ctx, "sponsored.cohort.create", cohort, now, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,'create_sponsored_cohort',%s,%s,'SUCCEEDED',%s,%s)",
                (tenant, ctx.principal_id, op, fingerprint, Jsonb(outcome), now + timedelta(days=7)),
            )
            return outcome

    def accept(self, identity, tenant, enrolment_id, body, correlation):
        validate("SponsoredAccessAccept", body)
        fingerprint = hash_data(["accept_sponsored_access", enrolment_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "accept_sponsored_access", hidden=True)
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type='accept_sponsored_access' AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            row = c.execute(
                "SELECT * FROM impact.sponsored_enrolment WHERE grantee_tenant_id=%s AND enrolment_id=%s FOR UPDATE",
                (tenant, enrolment_id),
            ).fetchone()
            if not row:
                unavailable()
            if row["terms_version"] != body["terms_version"]:
                raise DomainError("STALE_REVISION", 409)
            now = datetime.now(timezone.utc)
            if row["status"] == "INVITED":
                c.execute(
                    "UPDATE impact.sponsored_enrolment SET status='ACCEPTED',accepted_by=%s,accepted_at=%s,access_starts_at=%s,access_ends_at=%s WHERE sponsor_tenant_id=%s AND enrolment_id=%s",
                    (
                        ctx.principal_id,
                        now,
                        now,
                        now + timedelta(days=row["duration_days"]),
                        row["sponsor_tenant_id"],
                        enrolment_id,
                    ),
                )
                c.execute(
                    "INSERT INTO impact.sponsored_enrolment_event VALUES(%s,%s,%s,%s,'ACCEPTED',%s,%s)",
                    (tenant, str(uuid4()), row["sponsor_tenant_id"], enrolment_id, ctx.principal_id, now),
                )
            current = c.execute(
                "SELECT * FROM impact.sponsored_enrolment WHERE grantee_tenant_id=%s AND enrolment_id=%s",
                (tenant, enrolment_id),
            ).fetchone()
            outcome = self._entitlement(current)
            record_audit(c, ctx, "sponsored.access.accept", enrolment_id, now, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,'accept_sponsored_access',%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    now + timedelta(days=7),
                ),
            )
            return outcome

    @staticmethod
    def _entitlement(row):
        return {
            "enrolment_id": str(row["enrolment_id"]),
            "sponsor_tenant_id": str(row["sponsor_tenant_id"]),
            "status": row["status"],
            "access_starts_at": row["access_starts_at"].isoformat(),
            "access_ends_at": row["access_ends_at"].isoformat(),
            "no_charge": True,
            "data_authority_granted": False,
        }

    def active(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_sponsored_access", hidden=True)
            rows = c.execute(
                "SELECT * FROM impact.sponsored_enrolment WHERE grantee_tenant_id=%s AND status='ACCEPTED' AND access_starts_at<=statement_timestamp() AND access_ends_at>statement_timestamp() ORDER BY access_ends_at,enrolment_id",
                (tenant,),
            ).fetchall()
            return {"items": [self._entitlement(row) for row in rows]}
