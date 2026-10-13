"""FR-ANA-010 revocable, dataset-scoped external analytics extracts."""

from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


ALLOWED_FIELDS = {
    "CalculatedResult": {
        "value_state",
        "value",
        "displayed_value",
        "numerator",
        "denominator",
        "mode",
        "freshness",
    },
    "Evidence": {"title", "description", "evidence_type", "occurred_at"},
}


def _digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


class ExternalAnalytics:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body, correlation):
        op = "create_external_analytics_connection"
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "create_dashboards")
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            datasets = []
            for item in body["data"]["datasets"]:
                capability = (
                    "calculated-results.read" if item["kind"] == "CalculatedResult" else "evidence.read"
                )
                row = load(c, ctx, item["object_id"], item["kind"], capability)
                if str(row["head_revision"]) != item["revision_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                if not set(item["fields"]) <= ALLOWED_FIELDS[item["kind"]]:
                    raise DomainError("VALIDATION_FAILED", reason="EXTERNAL_FIELD_SCOPE_REFUSED")
                datasets.append(item)
            token = secrets.token_urlsafe(32)
            payload = {
                **body["data"],
                "datasets": datasets,
                "service_identity_id": secrets.token_hex(16),
                "credential_sha256": _digest(token),
                "status": "ACTIVE",
                "last_successful_extract": None,
                "remote_erasure_claimed": False,
                "unrestricted_database_access": False,
            }
            receipt = write(c, ctx, "ExternalAnalyticsConnection", payload, state="Active")
            outcome = {
                **receipt,
                "operation_id": body["operation_id"],
                "correlation_id": correlation,
                "service_identity_id": payload["service_identity_id"],
                "credential": token,
            }
            audit(c, ctx, op, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return outcome

    def refresh(self, identity, tenant, connection_id, body, correlation):
        op = "refresh_external_analytics_connection"
        fingerprint = hash_data({"connection_id": str(connection_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            connection = load(c, ctx, connection_id, "ExternalAnalyticsConnection", lock=True)
            data = connection["payload"]
            if data["status"] != "ACTIVE" or not secrets.compare_digest(
                data["credential_sha256"], _digest(body["credential"])
            ):
                raise DomainError("POLICY_DENIED", 403, reason="SERVICE_IDENTITY_REVOKED_OR_INVALID")
            package = []
            for item in data["datasets"]:
                row = c.execute(
                    "SELECT r.head_revision,r.classification,v.restriction_state,v.payload "
                    "FROM impact.object_registry r JOIN impact.object_revision v "
                    "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
                    "WHERE r.tenant_id=%s AND r.object_id=%s AND r.object_type=%s",
                    (tenant, item["object_id"], item["kind"]),
                ).fetchone()
                if (
                    not row
                    or str(row["head_revision"]) != item["revision_id"]
                    or row["restriction_state"] != "AVAILABLE"
                    or row["classification"] == "RESTRICTED"
                ):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                payload = row["payload"]
                definition_revision = payload.get("definition_revision") or payload.get("indicator_version")
                definition = None
                if definition_revision:
                    definition_row = c.execute(
                        "SELECT payload FROM impact.object_revision WHERE tenant_id=%s "
                        "AND revision_id=%s AND object_type='IndicatorDefinition' "
                        "AND restriction_state='AVAILABLE'",
                        (tenant, definition_revision),
                    ).fetchone()
                    if not definition_row:
                        raise DomainError("RESOURCE_UNAVAILABLE", 404)
                    definition = {
                        "name": definition_row["payload"].get("name"),
                        "unit": definition_row["payload"].get("unit"),
                        "measurement_type": definition_row["payload"].get("measurement_type"),
                    }
                package.append(
                    {
                        "object_id": item["object_id"],
                        "revision_id": item["revision_id"],
                        "kind": item["kind"],
                        "fields": {field: payload.get(field) for field in item["fields"]},
                        "definition_revision": definition_revision,
                        "definition": definition,
                        "unit": (definition or {}).get("unit") or payload.get("unit"),
                        "value_state": payload.get("value_state"),
                        "freshness": payload.get("freshness"),
                    }
                )
            extracted_at = datetime.now(timezone.utc).isoformat()
            updated = {
                **data,
                "last_successful_extract": {
                    "at": extracted_at,
                    "dataset_revisions": [item["revision_id"] for item in data["datasets"]],
                },
            }
            write(c, ctx, "ExternalAnalyticsConnection", updated, state="Active", previous=connection)
            extract = write(
                c,
                ctx,
                "ExternalAnalyticsExtract",
                {
                    "connection_id": str(connection_id),
                    "destination": data["destination"],
                    "reuse_terms": data["reuse_terms"],
                    "extracted_at": extracted_at,
                    "dataset_revisions": [item["revision_id"] for item in data["datasets"]],
                    "remote_copy_status": "TRACKED_NOT_REMOTELY_ERASED",
                },
                state="Recorded",
            )
            audit(c, ctx, op, extract, correlation)
            outcome = {
                "connection_id": str(connection_id),
                "extract_id": extract["object_id"],
                "extracted_at": extracted_at,
                "package": package,
            }
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return outcome

    def revoke(self, identity, tenant, connection_id, body, correlation):
        op = "revoke_external_analytics_connection"
        fingerprint = hash_data({"connection_id": str(connection_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "patch_dashboards", connection_id)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            connection = load(c, ctx, connection_id, "ExternalAnalyticsConnection", lock=True)
            payload = {
                **connection["payload"],
                "status": "REVOKED",
                "revoked_at": datetime.now(timezone.utc).isoformat(),
            }
            receipt = write(
                c, ctx, "ExternalAnalyticsConnection", payload, state="Revoked", previous=connection
            )
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            outcome = {
                **receipt,
                "last_successful_extract": payload.get("last_successful_extract"),
                "remote_copy_status": "TRACKED_NOT_REMOTELY_ERASED",
            }
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return outcome
