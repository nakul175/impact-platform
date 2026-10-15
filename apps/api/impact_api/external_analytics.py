"""FR-ANA-010 revocable, dataset-scoped external analytics extracts."""

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from uuid import uuid4

from psycopg.types.json import Jsonb

from .domain import DomainError
from .keyring import ring
from .store import (
    audit,
    authorize,
    context,
    currently_readable,
    envelope,
    field_allowed,
    hash_data,
    load,
    revision,
    visible_sql,
    write,
)


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


def _credential_key(secret):
    return hashlib.sha256(b"impact-external-analytics-credential-v1\0" + secret.encode()).digest()


class ExternalAnalytics:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body, correlation):
        op = "create_external_analytics_connection"
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op)
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
                outcome = dict(old["outcome"])
                sealed = base64.b64decode(outcome.pop("credential_sealed"))
                outcome["credential"] = (
                    ring(self.service.s, "cookie")
                    .unseal(
                        _credential_key,
                        sealed,
                        f"{tenant}:{body['operation_id']}".encode(),
                    )
                    .decode()
                )
                return outcome
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
            backup = body["data"]["backup_owner_id"]
            if (
                str(backup) == str(ctx.principal_id)
                or not c.execute(
                    "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s "
                    "AND principal_kind='HUMAN' AND active",
                    (tenant, backup),
                ).fetchone()
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            expires = datetime.fromisoformat(body["data"]["expires_at"].replace("Z", "+00:00"))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            if not now < expires <= now + timedelta(days=365):
                raise DomainError("VALIDATION_FAILED", reason="SERVICE_IDENTITY_EXPIRY_INVALID")
            token = secrets.token_urlsafe(32)
            service_identity_id, service_principal_id = str(uuid4()), str(uuid4())
            payload = {
                **body["data"],
                "datasets": datasets,
                "service_identity_id": service_identity_id,
                "service_principal_id": service_principal_id,
                "credential_sha256": _digest(token),
                "status": "ACTIVE",
                "last_successful_extract": None,
                "remote_erasure_claimed": False,
                "unrestricted_database_access": False,
            }
            receipt = write(c, ctx, "ExternalAnalyticsConnection", payload, state="Active")
            c.execute(
                "INSERT INTO impact.tenant_principal(tenant_id,principal_id,principal_kind) "
                "VALUES(%s,%s,'SERVICE')",
                (tenant, service_principal_id),
            )
            c.execute(
                "INSERT INTO impact.service_identity(tenant_id,service_identity_id,principal_id,owner_id,"
                "backup_owner_id,credential_reference,expires_at) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    service_identity_id,
                    service_principal_id,
                    ctx.principal_id,
                    backup,
                    receipt["object_id"],
                    expires,
                ),
            )
            outcome = {
                **receipt,
                "operation_id": body["operation_id"],
                "correlation_id": correlation,
                "service_identity_id": service_identity_id,
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
                    Jsonb(
                        {
                            **{k: v for k, v in outcome.items() if k != "credential"},
                            "credential_sealed": base64.b64encode(
                                ring(self.service.s, "cookie").seal(
                                    _credential_key,
                                    token.encode(),
                                    f"{tenant}:{body['operation_id']}".encode(),
                                )
                            ).decode(),
                        }
                    ),
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
            authorize(c, ctx, op, connection_id, hidden=True)
            connection = load(
                c, ctx, connection_id, "ExternalAnalyticsConnection", "dashboards.draft.edit", lock=True
            )
            data = connection["payload"]
            service = c.execute(
                "SELECT s.*,p.active FROM impact.service_identity s JOIN impact.tenant_principal p "
                "ON p.tenant_id=s.tenant_id AND p.principal_id=s.principal_id "
                "WHERE s.tenant_id=%s AND s.service_identity_id=%s AND s.credential_reference=%s",
                (tenant, data["service_identity_id"], connection_id),
            ).fetchone()
            if (
                data["status"] != "ACTIVE"
                or not service
                or not service["active"]
                or service["expires_at"] <= datetime.now(timezone.utc)
                or not secrets.compare_digest(data["credential_sha256"], _digest(body["credential"]))
            ):
                raise DomainError("POLICY_DENIED", 403, reason="SERVICE_IDENTITY_REVOKED_OR_INVALID")
            sources = []
            for item in data["datasets"]:
                capability = (
                    "calculated-results.read" if item["kind"] == "CalculatedResult" else "evidence.read"
                )
                row = load(c, ctx, item["object_id"], item["kind"], capability)
                if str(row["head_revision"]) != item["revision_id"]:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                if not field_allowed(c, ctx, capability, item["object_id"], "INTERNAL"):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                sources.append((item, row))
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
            package = []
            for item, row in sources:
                payload = row["payload"]
                definition_revision = payload.get("definition_revision") or payload.get("indicator_version")
                definition = None
                if definition_revision:
                    definition_row = revision(
                        c,
                        ctx,
                        definition_revision,
                        "IndicatorDefinition",
                        "indicator-definitions.read",
                    )
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
                    "selected_fields": {item["object_id"]: item["fields"] for item in data["datasets"]},
                    "package_sha256": hash_data(package).hex(),
                    "service_identity_id": data["service_identity_id"],
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
            authorize(c, ctx, op, connection_id, hidden=True)
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
            c.execute(
                "UPDATE impact.tenant_principal SET active=false,subject_epoch=subject_epoch+1 "
                "WHERE tenant_id=%s AND principal_id=%s",
                (tenant, payload["service_principal_id"]),
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

    def read(self, identity, tenant, connection_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_external_analytics_connection", connection_id, hidden=True)
            row = load(c, ctx, connection_id, "ExternalAnalyticsConnection", "dashboards.read")
            item = envelope(row)
            item["data"] = {k: v for k, v in item["data"].items() if k != "credential_sha256"}
            return item

    def listing(self, identity, tenant, limit=50):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_external_analytics_connections")
            predicate, args = visible_sql(ctx, "dashboards.read")
            rows = c.execute(
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
                "AND r.object_type='ExternalAnalyticsConnection' AND v.restriction_state='AVAILABLE' "
                "AND " + predicate + " ORDER BY r.created_at,r.object_id LIMIT %s",
                [tenant, *args, limit],
            ).fetchall()
            items = []
            for row in rows:
                if all(
                    currently_readable(
                        c,
                        ctx,
                        source["object_id"],
                        source["kind"],
                        "calculated-results.read"
                        if source["kind"] == "CalculatedResult"
                        else "evidence.read",
                    )
                    for source in row["payload"]["datasets"]
                ):
                    item = envelope(row)
                    item["data"] = {k: v for k, v in item["data"].items() if k != "credential_sha256"}
                    items.append(item)
            return {"items": items, "next_cursor": None, "scope_label": "Governed BI connections"}

    def extracts(self, identity, tenant, connection_id, limit=50):
        if not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            load(c, ctx, connection_id, "ExternalAnalyticsConnection", "dashboards.read")
            rows = c.execute(
                "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
                "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
                "AND r.object_type='ExternalAnalyticsExtract' AND v.payload->>'connection_id'=%s "
                "ORDER BY r.created_at DESC,r.object_id DESC LIMIT %s",
                (tenant, str(connection_id), limit),
            ).fetchall()
            return {
                "items": [envelope(row) for row in rows],
                "next_cursor": None,
                "scope_label": "Tracked external extracts",
            }
