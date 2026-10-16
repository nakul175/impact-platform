"""Governed qualitative coding primitives."""

from datetime import datetime, timedelta, timezone
from psycopg.types.json import Jsonb
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


class QualitativeEvidence:
    def __init__(self, service):
        self.service = service

    def _run(self, identity, tenant, op, body, correlation, fn):
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
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

    def create_codebook(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            codes = body["data"]["codes"]
            if len({item["code_id"] for item in codes}) != len(codes):
                raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_STABLE_CODE_ID")
            return write(c, ctx, "QualitativeCodebook", body["data"], state="Versioned")

        return self._run(identity, tenant, "create_qualitative_codebook", body, correlation, apply)

    def assign(self, identity, tenant, body, correlation):
        data = body["data"]

        def apply(c, ctx):
            source = load(c, ctx, data["source_id"], data["source_type"], "evidence.read")
            codebook = load(c, ctx, data["codebook_id"], "QualitativeCodebook", "evaluations.read")
            if str(codebook["head_revision"]) != data["codebook_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if not set(data["code_ids"]) <= {item["code_id"] for item in codebook["payload"]["codes"]}:
                raise DomainError("VALIDATION_FAILED", reason="UNKNOWN_CODE_ID")
            payload = {
                **data,
                "source_revision": str(source["head_revision"]),
                "coder_natural_identity_id": str(ctx.identity.natural_identity_id),
                "inherited_classification": source["classification"],
            }
            return write(c, ctx, "QualitativeCodingAssignment", payload, state="Independent")

        return self._run(identity, tenant, "assign_qualitative_codes", body, correlation, apply)

    def adjudicate(self, identity, tenant, body, correlation):
        data = body["data"]

        def apply(c, ctx):
            left = load(
                c,
                ctx,
                data["left_assignment_id"],
                "QualitativeCodingAssignment",
                "evaluations.read",
            )
            right = load(
                c,
                ctx,
                data["right_assignment_id"],
                "QualitativeCodingAssignment",
                "evaluations.read",
            )
            if left["payload"]["unit_id"] != right["payload"]["unit_id"]:
                raise DomainError("VALIDATION_FAILED", reason="UNMATCHED_UNITS_NOT_ADJUDICABLE")
            if left["payload"]["coder_natural_identity_id"] == right["payload"]["coder_natural_identity_id"]:
                raise DomainError("VALIDATION_FAILED", reason="INDEPENDENT_CODERS_REQUIRED")
            if str(ctx.identity.natural_identity_id) in {
                left["payload"]["coder_natural_identity_id"],
                right["payload"]["coder_natural_identity_id"],
            }:
                raise DomainError("INDEPENDENCE_REQUIRED", 409)
            if (
                left["payload"]["codebook_id"] != right["payload"]["codebook_id"]
                or left["payload"]["codebook_revision"] != right["payload"]["codebook_revision"]
            ):
                raise DomainError("VALIDATION_FAILED", reason="CODEBOOK_VERSIONS_NOT_COMPARABLE")
            codebook = load(
                c,
                ctx,
                left["payload"]["codebook_id"],
                "QualitativeCodebook",
                "evaluations.read",
            )
            if str(codebook["head_revision"]) != left["payload"]["codebook_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if not set(data["final_code_ids"]) <= {item["code_id"] for item in codebook["payload"]["codes"]}:
                raise DomainError("VALIDATION_FAILED", reason="UNKNOWN_CODE_ID")
            payload = {
                **data,
                "left_assignment_revision": str(left["head_revision"]),
                "right_assignment_revision": str(right["head_revision"]),
                "individual_assignments_preserved": True,
                "codebook_id": left["payload"]["codebook_id"],
                "codebook_revision": left["payload"]["codebook_revision"],
                "inherited_classification": left["payload"]["inherited_classification"],
            }
            return write(c, ctx, "QualitativeAdjudication", payload, state="Final")

        return self._run(identity, tenant, "adjudicate_qualitative_coding", body, correlation, apply)

    def agreement(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            pairs = []
            for pair in body["data"]["pairs"]:
                left = load(
                    c,
                    ctx,
                    pair["left_assignment_id"],
                    "QualitativeCodingAssignment",
                    "evaluations.read",
                )
                right = load(
                    c,
                    ctx,
                    pair["right_assignment_id"],
                    "QualitativeCodingAssignment",
                    "evaluations.read",
                )
                if (
                    left["payload"]["coder_natural_identity_id"]
                    == right["payload"]["coder_natural_identity_id"]
                ):
                    raise DomainError("VALIDATION_FAILED", reason="INDEPENDENT_CODERS_REQUIRED")
                if (
                    left["payload"]["codebook_id"] != right["payload"]["codebook_id"]
                    or left["payload"]["codebook_revision"] != right["payload"]["codebook_revision"]
                ):
                    raise DomainError("VALIDATION_FAILED", reason="CODEBOOK_VERSIONS_NOT_COMPARABLE")
                if left["payload"]["unit_id"] == right["payload"]["unit_id"]:
                    pairs.append(
                        {
                            "unit_id": left["payload"]["unit_id"],
                            "agrees": sorted(left["payload"]["code_ids"])
                            == sorted(right["payload"]["code_ids"]),
                        }
                    )
            if not pairs:
                raise DomainError("VALIDATION_FAILED", reason="NO_MATCHED_UNITS")
            return write(
                c,
                ctx,
                "QualitativeAgreement",
                {
                    "matched_units_only": True,
                    "matched_count": len(pairs),
                    "agreement_count": sum(1 for item in pairs if item["agrees"]),
                    "pairs": pairs,
                },
                state="Calculated",
            )

        return self._run(identity, tenant, "calculate_qualitative_agreement", body, correlation, apply)
