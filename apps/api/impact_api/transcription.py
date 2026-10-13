"""FR-EVD-006 governed transcription and translation artifacts."""

from datetime import datetime, timedelta, timezone
from psycopg.types.json import Jsonb
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


class Transcription:
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

    def request(self, identity, tenant, body, correlation):
        data = body["data"]

        def apply(c, ctx):
            recording = load(c, ctx, data["recording_id"], "Evidence", "evidence.read")
            destination = load(c, ctx, data["destination_id"], "ProcessingDestination")
            if (
                destination["lifecycle_state"] != "Approved"
                or data["task"] not in destination["payload"]["permitted_tasks"]
            ):
                raise DomainError("DESTINATION_NOT_APPROVED", 409)
            payload = {
                **data,
                "recording_revision": str(recording["head_revision"]),
                "destination_revision": str(destination["head_revision"]),
                "classification": recording["classification"],
                "fallback": "PROHIBITED",
                "segments": [
                    {
                        **segment,
                        "speaker": segment.get("speaker") or "UNKNOWN",
                        "start_ms": segment.get("start_ms"),
                        "end_ms": segment.get("end_ms"),
                    }
                    for segment in data["segments"]
                ],
                "automated_output_retained": True,
            }
            return write(c, ctx, "TranscriptArtifact", payload, state="Generated")

        return self._run(identity, tenant, "request_transcription", body, correlation, apply)

    def correct(self, identity, tenant, body, correlation):
        data = body["data"]

        def apply(c, ctx):
            artifact = load(c, ctx, data["artifact_id"], "TranscriptArtifact", lock=True)
            segments = list(artifact["payload"]["segments"])
            found = False
            for segment in segments:
                if segment["segment_id"] == data["segment_id"]:
                    segment["original_automated_text"] = segment["text"]
                    segment["text"] = data["corrected_text"]
                    found = True
            if not found:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            return write(
                c,
                ctx,
                "TranscriptArtifact",
                {**artifact["payload"], "segments": segments},
                state="Corrected",
                previous=artifact,
            )

        return self._run(identity, tenant, "correct_transcript_segment", body, correlation, apply)

    def quote(self, identity, tenant, body, correlation):
        data = body["data"]

        def apply(c, ctx):
            artifact = load(c, ctx, data["artifact_id"], "TranscriptArtifact")
            if not data["original_meaning_reviewed"]:
                raise DomainError("ORIGINAL_MEANING_REVIEW_REQUIRED", 409)
            if not any(x["segment_id"] == data["segment_id"] for x in artifact["payload"]["segments"]):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            return write(
                c,
                ctx,
                "QuotationReference",
                {
                    **data,
                    "artifact_revision": str(artifact["head_revision"]),
                    "recording_id": artifact["payload"]["recording_id"],
                    "recording_revision": artifact["payload"]["recording_revision"],
                },
                state="Reviewed",
            )

        return self._run(identity, tenant, "create_reviewed_quotation", body, correlation, apply)
