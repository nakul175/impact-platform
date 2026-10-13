"""FR-EVD-008 versioned triangulated findings."""

from datetime import datetime, timedelta, timezone
from psycopg.types.json import Jsonb
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


class Findings:
    def __init__(self, service):
        self.service = service

    def _run(self, identity, tenant, op, body, correlation, fn):
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "create_dashboards")
            old = c.execute(
                "SELECT payload_hash,outcome FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            receipt = fn(c, ctx)
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
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return receipt

    def _pins(self, c, ctx, pins):
        out = []
        for pin in pins:
            row = load(c, ctx, pin["object_id"], pin["object_type"])
            if str(row["head_revision"]) != pin["revision_id"]:
                raise DomainError("CONFLICT_VERSION", 409)
            out.append(pin)
        return out

    def create(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            d = body["data"]
            if d.get("ai_confidence") is not None and not d["confidence_rationale"]:
                raise DomainError("EVIDENTIAL_RATIONALE_REQUIRED", 409)
            return write(
                c,
                ctx,
                "TriangulatedFinding",
                {
                    **d,
                    "supporting_evidence": self._pins(c, ctx, d["supporting_evidence"]),
                    "contradictory_evidence": self._pins(c, ctx, d["contradictory_evidence"]),
                    "observation_distinct_from_interpretation": True,
                },
                state="Recorded",
            )

        return self._run(identity, tenant, "create_triangulated_finding", body, correlation, apply)

    def revise(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            d = body["data"]
            row = load(c, ctx, d["finding_id"], "TriangulatedFinding", lock=True)
            supporting = self._pins(c, ctx, d["supporting_evidence"])
            contrary = self._pins(c, ctx, d["contradictory_evidence"])
            return write(
                c,
                ctx,
                "TriangulatedFinding",
                {
                    **row["payload"],
                    **d,
                    "supporting_evidence": supporting,
                    "contradictory_evidence": contrary,
                    "prior_evidence_set": {
                        "revision": str(row["head_revision"]),
                        "supporting": row["payload"]["supporting_evidence"],
                        "contradictory": row["payload"]["contradictory_evidence"],
                    },
                },
                state="Revised",
                previous=row,
            )

        return self._run(identity, tenant, "revise_finding_interpretation", body, correlation, apply)

    def publish(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            d = body["data"]
            row = load(c, ctx, d["finding_id"], "TriangulatedFinding", lock=True)
            if row["payload"]["contradictory_evidence"] and not (
                d["preserve_contradictory_evidence"] or d["disclosed_limitation"]
            ):
                raise DomainError("CONTRADICTORY_EVIDENCE_REQUIRED", 409)
            return write(
                c,
                ctx,
                "FindingPublication",
                {
                    "finding_id": d["finding_id"],
                    "finding_revision": str(row["head_revision"]),
                    "preserve_contradictory_evidence": d["preserve_contradictory_evidence"],
                    "disclosed_limitation": d["disclosed_limitation"],
                },
                state="Published",
            )

        return self._run(identity, tenant, "publish_triangulated_finding", body, correlation, apply)
