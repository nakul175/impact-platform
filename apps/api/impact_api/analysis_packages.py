"""FR-EVA-003 frozen, integrity-bound analysis packages."""

from datetime import datetime, timedelta, timezone
import hashlib
import json

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


SOURCE_CAPS = {
    "Observation": "observations.read",
    "CalculatedResult": "calculated-results.read",
}
VARIABLES = {
    "value_state",
    "value",
    "displayed_value",
    "numerator",
    "denominator",
    "event_at",
    "approval_state",
    "mode",
    "freshness",
    "indicator_id",
    "period_id",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


class AnalysisPackages:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body, correlation):
        op = "create_analysis_package"
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "create_dashboards")
            old = c.execute(
                "SELECT payload_hash,outcome FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            data = body["data"]
            load(c, ctx, data["evaluation_id"], "EvaluationRegistration")
            methodology = load(c, ctx, data["methodology_id"], "EvaluationMethodology")
            if (
                str(methodology["head_revision"]) != data["methodology_revision"]
                or methodology["payload"]["review_state"] != "REVIEWED"
            ):
                raise DomainError("CONFLICT_VERSION", 409, reason="METHODOLOGY_NOT_CURRENT_REVIEWED")
            if not set(data["variables"]) <= VARIABLES:
                raise DomainError("VALIDATION_FAILED", reason="ANALYSIS_VARIABLE_NOT_ALLOWED")
            rows = []
            for source in data["sources"]:
                current = load(
                    c,
                    ctx,
                    source["object_id"],
                    source["kind"],
                    SOURCE_CAPS[source["kind"]],
                )
                revision = c.execute(
                    "SELECT payload,payload_sha256 FROM impact.object_revision WHERE tenant_id=%s "
                    "AND object_id=%s AND revision_id=%s AND object_type=%s "
                    "AND restriction_state='AVAILABLE'",
                    (tenant, source["object_id"], source["revision_id"], source["kind"]),
                ).fetchone()
                if not revision or str(current["object_id"]) != source["object_id"]:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                payload = revision["payload"]
                approved = (
                    payload.get("approval_state") == "APPROVED"
                    if source["kind"] == "Observation"
                    else payload.get("mode") == "OFFICIAL"
                )
                if not approved:
                    raise DomainError("INVALID_STATE", 409, reason="ANALYSIS_SOURCE_NOT_APPROVED")
                rows.append(
                    {
                        **source,
                        "source_sha256": bytes(revision["payload_sha256"]).hex(),
                        "values": {name: payload.get(name) for name in data["variables"]},
                    }
                )
            attachments = []
            for attachment in data["reviewed_code_evidence"]:
                evidence = load(c, ctx, attachment["object_id"], "Evidence", "evidence.read")
                if str(evidence["head_revision"]) != attachment["revision_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                attachments.append({**attachment, "execution": "PROHIBITED"})
            frozen = {
                "evaluation_id": data["evaluation_id"],
                "methodology_id": data["methodology_id"],
                "methodology_revision": data["methodology_revision"],
                "variables": data["variables"],
                "filters": data["filters"],
                "dictionary": data["dictionary"],
                "rows": rows,
                "reviewed_code_evidence": attachments,
                "code_execution": "PROHIBITED",
            }
            payload = {
                **frozen,
                "integrity_sha256": hashlib.sha256(canonical(frozen)).hexdigest(),
                "frozen_at": datetime.now(timezone.utc).isoformat(),
                "immutable": True,
            }
            receipt = write(c, ctx, "AnalysisPackage", payload, state="Frozen")
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

    def export(self, identity, tenant, package_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "action_reports_export", package_id)
            package = load(c, ctx, package_id, "AnalysisPackage")
            payload = package["payload"]
            frozen = {
                key: payload[key]
                for key in [
                    "evaluation_id",
                    "methodology_id",
                    "methodology_revision",
                    "variables",
                    "filters",
                    "dictionary",
                    "rows",
                    "reviewed_code_evidence",
                    "code_execution",
                ]
            }
            digest = hashlib.sha256(canonical(frozen)).hexdigest()
            if digest != payload["integrity_sha256"]:
                raise DomainError("INTEGRITY_MISMATCH", 409)
            return {
                "package_id": str(package_id),
                "package_revision": str(package["head_revision"]),
                "integrity_sha256": digest,
                "content": frozen,
            }

    def register_result(self, identity, tenant, package_id, body, correlation):
        op = "register_analysis_result"
        fingerprint = hash_data({"package_id": str(package_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "patch_dashboards", package_id)
            old = c.execute(
                "SELECT payload_hash,outcome FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            package = load(c, ctx, package_id, "AnalysisPackage", lock=True)
            payload = {
                **body["data"],
                "package_id": str(package_id),
                "package_revision": str(package["head_revision"]),
                "package_integrity_sha256": package["payload"]["integrity_sha256"],
                "methodology_revision": package["payload"]["methodology_revision"],
            }
            receipt = write(c, ctx, "AnalysisResultReference", payload, state="Submitted")
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
