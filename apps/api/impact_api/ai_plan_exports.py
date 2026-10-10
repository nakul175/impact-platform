"""Exact-byte internal AI-plan export of one saved revision.

One issuance is an immutable AuditEvent, metadata, retained UTF-8 bytes, an outbox
intent and a pointer-only receipt in the same tenant-locked transaction. Replays
read the original bytes after current authority; they never call a renderer.
"""

from copy import deepcopy
from datetime import timedelta, timezone
import hashlib
import hmac
import json
from uuid import UUID, uuid4

from jsonschema import Draft202012Validator, FormatChecker
from psycopg.errors import ProgramLimitExceeded, UniqueViolation
from psycopg.types.json import Jsonb

from .clock import now
from . import ai_content_archives
from .ai_plan_export_contracts import (
    DISCLAIMER,
    DOCUMENT_VALIDATORS,
    MANIFEST_VALIDATOR,
    MAX_COPY_BYTES,
    OPERATION,
    PUBLIC_SCHEMA,
    PUBLIC_VALIDATOR,
    RECEIPT_VALIDATOR,
    RENDERER_VERSION,
    REPLAY_HOURS,
    REQUEST_VALIDATOR,
    package_for,
)
from .domain import DomainError
from .store import EVENT_VALIDATOR, authorize, canonical, context, hash_data, load, write

KIND = "AIAdoptionPlan"
READ_CAP = "ai.enablement.read"


def observed(c):
    return c.execute("SELECT statement_timestamp() AS generated_at").fetchone()["generated_at"]


def stamp(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def unreadable():
    raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_PLAN_EXPORT_SOURCE_UNREADABLE")


def uuid(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise DomainError("VALIDATION_FAILED", 422, reason="INVALID_IDENTIFIER") from None


def _schema_at(schema):
    while "$ref" in schema:
        reference = schema["$ref"]
        if not reference.startswith("#/$defs/"):
            unreadable()
        schema = PUBLIC_SCHEMA["$defs"][reference.rsplit("/", 1)[-1]]
    return schema


def _project(value, schema):
    """Copy only frozen known fields, recursively; never coerce or reinterpret them."""
    schema = _schema_at(schema)
    if "oneOf" in schema:
        accepted = []
        for candidate in schema["oneOf"]:
            projected = _project(value, candidate)
            retained = {**candidate, "$defs": PUBLIC_SCHEMA["$defs"]}
            if Draft202012Validator(retained, format_checker=FormatChecker()).is_valid(projected):
                accepted.append(projected)
        if len(accepted) != 1:
            unreadable()
        return accepted[0]
    if schema.get("type") == "object" and isinstance(value, dict):
        return {
            name: _project(value[name], child)
            for name, child in schema.get("properties", {}).items()
            if name in value
        }
    if schema.get("type") == "array" and isinstance(value, list):
        return [_project(item, schema["items"]) for item in value]
    return deepcopy(value)


def public_plan(value):
    try:
        projected = _project(value, PUBLIC_SCHEMA)
        if not PUBLIC_VALIDATOR.is_valid(projected):
            unreadable()
        canonical(projected)
        return projected
    except (ValueError, TypeError, UnicodeError, KeyError):
        unreadable()


def _guidance_consistent(guidance, plan_id, revision_id):
    if guidance["object_id"] != plan_id or guidance["revision_id"] != revision_id:
        unreadable()
    status = guidance["status"]
    available = status != "UNAVAILABLE"
    if available:
        if any(
            guidance[name] is None for name in ("snapshot_schema_version", "captured_at", "snapshot_sha256")
        ):
            unreadable()
        bundle = {"schema_version": guidance["snapshot_schema_version"]}
        for name in ("catalog", "solutions", "practice"):
            component = guidance[name]
            expected = name != "practice" or status == "COMPLETE"
            if (component["status"] == "AVAILABLE") != expected:
                unreadable()
            bundle[name] = component["payload"]
            if expected and component["content_version"] != component["payload"]["content_version"]:
                unreadable()
        if not hmac.compare_digest(hash_data(bundle).hex(), guidance["snapshot_sha256"]):
            unreadable()
    elif any(
        guidance[name] is not None for name in ("snapshot_schema_version", "captured_at", "snapshot_sha256")
    ) or any(guidance[name]["status"] != "UNAVAILABLE" for name in ("catalog", "solutions", "practice")):
        unreadable()


def valid_document(document):
    """The document satisfies the schema of the package edition it names, and that edition is the
    one its guidance requires (v1 for a v1 or missing archive, v2 for a v2 archive)."""
    if not isinstance(document, dict):
        return False
    validator = DOCUMENT_VALIDATORS.get(document.get("schema_version"))
    return bool(
        validator
        and validator.is_valid(document)
        and package_for(document["guidance"]) == document["schema_version"]
    )


def render_document(tenant, issuance, generated, plan_id, revision_id, source, guidance):
    package = package_for(guidance)
    if package is None:
        unreadable()
    document = {
        "schema_version": package,
        "renderer_version": RENDERER_VERSION,
        "tenant_id": tenant,
        "issuance_id": issuance,
        "generated_at": stamp(generated),
        "restriction": "INTERNAL_SELF",
        "record_status": "Draft",
        "declared_components": ["PUBLIC_PLAN", "ARCHIVED_GUIDANCE"],
        "plan": {
            "object_id": plan_id,
            "revision_id": revision_id,
            "saved_at": stamp(source["created_at"]),
            "schema_version": source["schema_version"],
            "data": public_plan(source["payload"]),
        },
        "guidance": guidance,
        "disclaimer": DISCLAIMER,
    }
    if not valid_document(document):
        unreadable()
    _guidance_consistent(guidance, plan_id, revision_id)
    try:
        body = canonical(document)
    except (ValueError, TypeError, UnicodeError):
        unreadable()
    if not 2 <= len(body) <= MAX_COPY_BYTES:
        raise DomainError("LIMIT_EXCEEDED", 422, reason="AI_PLAN_EXPORT_SIZE_LIMIT")
    return body


def receipt(metadata):
    result = {
        "object_id": str(metadata["issuance_id"]),
        "revision_id": str(metadata["audit_revision_id"]),
        "business_state": "Issued",
        "operation_id": str(metadata["operation_id"]),
        "correlation_id": str(metadata["correlation_id"]),
        "saved_at": stamp(metadata["generated_at"]),
        "content_sha256": bytes(metadata["content_sha256"]).hex(),
        "byte_count": metadata["byte_count"],
        "replay_until": stamp(metadata["replay_until"]),
    }
    if not RECEIPT_VALIDATOR.is_valid(result):
        unreadable()
    return result


def original_response(metadata, body, at=None):
    """Validate a retained artifact (package v1 or v2) and build its original manifest without rendering."""
    if metadata["replay_until"] <= (at or now()):
        raise DomainError("IDEMPOTENCY_EXPIRED", 409)
    raw = bytes(body)
    if not 2 <= len(raw) <= MAX_COPY_BYTES or len(raw) != metadata["byte_count"]:
        unreadable()
    if not hmac.compare_digest(hashlib.sha256(raw).digest(), bytes(metadata["content_sha256"])):
        unreadable()
    try:
        content = raw.decode("utf-8", errors="strict")
        document = json.loads(content)
        if not valid_document(document) or canonical(document) != raw:
            unreadable()
    except (ValueError, TypeError, UnicodeError):
        unreadable()
    plan, guidance = document["plan"], document["guidance"]
    _guidance_consistent(guidance, plan["object_id"], plan["revision_id"])
    if (
        document["tenant_id"] != str(metadata["tenant_id"])
        or document["issuance_id"] != str(metadata["issuance_id"])
        or document["schema_version"] != metadata["package_schema_version"]
        or document["renderer_version"] != metadata["renderer_version"]
        or document["generated_at"] != stamp(metadata["generated_at"])
        or metadata["format"] != "JSON"
        or metadata["restriction"] != document["restriction"]
        or plan["object_id"] != str(metadata["plan_object_id"])
        or plan["revision_id"] != str(metadata["plan_revision_id"])
        or guidance["object_id"] != plan["object_id"]
        or guidance["revision_id"] != plan["revision_id"]
        or guidance["status"] != metadata["guidance_status"]
        or guidance["snapshot_schema_version"] != metadata["guidance_schema_version"]
        or guidance["snapshot_sha256"]
        != (bytes(metadata["guidance_sha256"]).hex() if metadata["guidance_sha256"] else None)
        or (metadata["guidance_snapshot_id"] is not None) != (guidance["status"] != "UNAVAILABLE")
        or metadata["replay_until"] != metadata["generated_at"] + timedelta(hours=REPLAY_HOURS)
    ):
        unreadable()
    manifest = {
        "plan_id": plan["object_id"],
        "revision_id": plan["revision_id"],
        "title": plan["data"]["title"],
        "saved_at": plan["saved_at"],
        "generated_at": document["generated_at"],
        "schema": document["schema_version"],
        "renderer": document["renderer_version"],
        "filename": "impact-ai-plan-" + plan["object_id"] + "-" + plan["revision_id"] + ".json",
        "media_type": "application/json",
        "content_sha256": bytes(metadata["content_sha256"]).hex(),
        "size_bytes": len(raw),
        "replay_expires_at": stamp(metadata["replay_until"]),
        "guidance_status": guidance["status"],
    }
    if not MANIFEST_VALIDATOR.is_valid(manifest):
        unreadable()
    return {"manifest": manifest, "content": content, "receipt": receipt(metadata)}


def _intent(c, ctx, metadata):
    event = {
        "event_id": metadata["outbox_event_id"],
        "tenant_id": ctx.tenant_id,
        "event_type": "object.changed",
        "schema_version": "1.1",
        "aggregate_type": "AuditEvent",
        "aggregate_id": metadata["issuance_id"],
        "aggregate_revision": metadata["audit_revision_id"],
        "aggregate_sequence": 1,
        "occurred_at": stamp(metadata["generated_at"]),
        "actor_id": ctx.principal_id,
        "correlation_id": metadata["correlation_id"],
        "payload": {
            "object_id": metadata["issuance_id"],
            "revision_id": metadata["audit_revision_id"],
            "state": "Recorded",
        },
    }
    EVENT_VALIDATOR.validate(event)
    c.execute(
        "INSERT INTO impact.outbox_event VALUES(%s,%s,%s,%s,%s)",
        (ctx.tenant_id, event["event_id"], event["event_type"], event["occurred_at"], Jsonb(event)),
    )
    c.execute(
        "INSERT INTO impact.outbox_delivery(tenant_id,event_id) VALUES(%s,%s)",
        (ctx.tenant_id, event["event_id"]),
    )


class AIPlanExports:
    def __init__(self, service):
        self.service, self.db = service, service.db

    def create(self, identity, tenant, object_id, revision_id, body, correlation):
        object_id, revision_id, correlation = uuid(object_id), uuid(revision_id), uuid(correlation)
        if not REQUEST_VALIDATOR.is_valid(body):
            raise DomainError("VALIDATION_FAILED", 422, reason="AI_PLAN_EXPORT_REQUEST_INVALID")
        operation_id = uuid(body["operation_id"])
        try:
            with self.db.transaction(tenant) as c:
                c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (str(tenant),))
                ctx = context(c, identity, tenant, write=True)
                authorize(c, ctx, OPERATION, object_id, hidden=True)
                authorize(c, ctx, "get_ai_adoption_plan", object_id, hidden=True)
                load(c, ctx, object_id, KIND, READ_CAP)
                source = c.execute(
                    "SELECT payload,payload_sha256,schema_version,created_at FROM impact.object_revision "
                    "WHERE tenant_id=%s AND object_id=%s AND revision_id=%s "
                    "AND object_type=%s AND restriction_state='AVAILABLE'",
                    (tenant, object_id, revision_id, KIND),
                ).fetchone()
                if not source:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                c.execute("SELECT set_config('impact.ai_plan_export_principal',%s,true)", (ctx.principal_id,))
                fingerprint = hash_data([OPERATION, tenant, ctx.principal_id, object_id, revision_id, body])
                c.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s,1))",
                    (str(tenant) + ":" + ctx.principal_id + ":" + OPERATION + ":" + operation_id,),
                )
                existing = c.execute(
                    "SELECT * FROM impact.ai_plan_export_issuance WHERE tenant_id=%s "
                    "AND principal_id=%s AND command_type=%s AND operation_id=%s",
                    (tenant, ctx.principal_id, OPERATION, operation_id),
                ).fetchone()
                if existing:
                    if not hmac.compare_digest(bytes(existing["request_sha256"]), fingerprint):
                        raise DomainError("CONFLICT_OPERATION", 409)
                    at = observed(c)
                    if existing["replay_until"] <= at:
                        raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                    saved = c.execute(
                        "SELECT body FROM impact.ai_plan_export_bytes WHERE tenant_id=%s AND issuance_id=%s",
                        (tenant, existing["issuance_id"]),
                    ).fetchone()
                    if not saved:
                        if existing["replay_until"] <= observed(c):
                            raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                        unreadable()
                    return original_response(existing, saved["body"], at=at)
                # Older receipts or hidden prior issuances cannot be silently replaced.
                prior = c.execute(
                    "SELECT 1 FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                    "AND command_type=%s AND operation_id=%s",
                    (tenant, ctx.principal_id, OPERATION, operation_id),
                ).fetchone()
                if prior:
                    unreadable()
                return self._issue(c, ctx, object_id, revision_id, source, body, fingerprint, correlation)
        except UniqueViolation as error:
            if getattr(error.diag, "table_name", None) == "ai_plan_export_issuance":
                raise DomainError("CONFLICT_OPERATION", 409) from None
            raise
        except ProgramLimitExceeded as error:
            if getattr(error.diag, "message_primary", None) == "AI_PLAN_EXPORT_STORAGE_LIMIT":
                raise DomainError("LIMIT_EXCEEDED", 429, reason="AI_PLAN_EXPORT_STORAGE_LIMIT") from None
            raise

    def _issue(self, c, ctx, object_id, revision_id, source, body, fingerprint, correlation):
        try:
            if not hmac.compare_digest(bytes(source["payload_sha256"]), hash_data(source["payload"])):
                unreadable()
        except (ValueError, TypeError, UnicodeError):
            unreadable()
        guidance = ai_content_archives.result(c, ctx.tenant_id, object_id, revision_id, source["payload"])
        archived = ai_content_archives._bound(c, ctx.tenant_id, object_id, revision_id)
        generated, issuance = observed(c), str(uuid4())
        raw = render_document(ctx.tenant_id, issuance, generated, object_id, revision_id, source, guidance)
        audit = write(
            c,
            ctx,
            "AuditEvent",
            {
                "real_actor_id": ctx.principal_id,
                "effective_actor_id": ctx.principal_id,
                "action_type": OPERATION,
                "object_reference": object_id,
                "outcome": "SUCCEEDED",
                "occurred_at": stamp(generated),
                "correlation_id": correlation,
                "specification_ref": "FR-NPA-030",
            },
            "Recorded",
            object_id=issuance,
            track_author=False,
        )
        metadata = {
            "tenant_id": ctx.tenant_id,
            "issuance_id": issuance,
            "audit_revision_id": audit["revision_id"],
            "plan_object_id": object_id,
            "plan_revision_id": revision_id,
            "principal_id": ctx.principal_id,
            "membership_id": str(ctx.membership_id),
            "command_type": OPERATION,
            "operation_id": uuid(body["operation_id"]),
            "request_sha256": fingerprint,
            "format": "JSON",
            "restriction": "INTERNAL_SELF",
            "package_schema_version": package_for(guidance),
            "renderer_version": RENDERER_VERSION,
            "guidance_status": guidance["status"],
            "guidance_snapshot_id": archived["snapshot_id"] if archived else None,
            "guidance_schema_version": guidance["snapshot_schema_version"],
            "guidance_sha256": bytes.fromhex(guidance["snapshot_sha256"]) if archived else None,
            "generated_at": generated,
            "replay_until": generated + timedelta(hours=REPLAY_HOURS),
            "content_sha256": hashlib.sha256(raw).digest(),
            "byte_count": len(raw),
            "correlation_id": correlation,
            "outbox_event_id": str(uuid4()),
        }
        names = list(metadata)
        c.execute(
            "INSERT INTO impact.ai_plan_export_issuance("
            + ",".join(names)
            + ") VALUES("
            + ",".join(["%s"] * len(names))
            + ")",
            [metadata[name] for name in names],
        )
        c.execute(
            "INSERT INTO impact.ai_plan_export_bytes(tenant_id,issuance_id,body) VALUES(%s,%s,%s)",
            (ctx.tenant_id, issuance, raw),
        )
        _intent(c, ctx, metadata)
        result = receipt(metadata)
        c.execute(
            "INSERT INTO impact.operation_receipt(tenant_id,actor_id,command_type,operation_id,payload_hash,"
            "state,outcome,expires_at) VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
            (
                ctx.tenant_id,
                ctx.principal_id,
                OPERATION,
                metadata["operation_id"],
                fingerprint,
                Jsonb(result),
                metadata["replay_until"],
            ),
        )
        return original_response(metadata, raw, at=generated)
