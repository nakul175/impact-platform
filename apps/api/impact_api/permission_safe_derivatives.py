"""Immutable derivative provenance with current-authority reads."""

import re
from uuid import UUID

from .domain import DomainError
from .store import authorize, context, load

KINDS = {"Dashboard", "Search", "Analysis", "AIArtifact", "ApprovedAggregate"}


def _uuid(value):
    try:
        return str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        raise DomainError("VALIDATION_FAILED", 400, reason="DERIVATIVE_MANIFEST_INVALID") from None


class PermissionSafeDerivatives:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, derivative_id, body):
        if not isinstance(body, dict) or set(body) != {"revision_id", "kind", "disclosure_mode", "sources"}:
            raise DomainError("VALIDATION_FAILED", 400, reason="DERIVATIVE_MANIFEST_INVALID")
        revision = _uuid(body["revision_id"])
        mode = body["disclosure_mode"]
        sources = body["sources"]
        if (
            body["kind"] not in KINDS
            or mode not in {"PRIVATE", "APPROVED_AGGREGATE"}
            or not isinstance(sources, list)
            or not 1 <= len(sources) <= 100
        ):
            raise DomainError("VALIDATION_FAILED", 400, reason="DERIVATIVE_MANIFEST_INVALID")
        if mode == "APPROVED_AGGREGATE" and body["kind"] != "ApprovedAggregate":
            raise DomainError("VALIDATION_FAILED", 400, reason="PUBLIC_DERIVATIVE_NOT_APPROVED_AGGREGATE")
        normalized = []
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_derivative_manifest")
            for source in sources:
                if (
                    not isinstance(source, dict)
                    or set(source) != {"object_id", "revision_id", "object_type", "capability"}
                    or not re.fullmatch(r"[A-Z][A-Za-z0-9]{0,99}", source["object_type"])
                    or not re.fullmatch(r"[a-z][a-z0-9.-]{0,99}", source["capability"])
                ):
                    raise DomainError("VALIDATION_FAILED", 400, reason="DERIVATIVE_MANIFEST_INVALID")
                item = {
                    **source,
                    "object_id": _uuid(source["object_id"]),
                    "revision_id": _uuid(source["revision_id"]),
                }
                load(c, ctx, item["object_id"], item["object_type"], item["capability"])
                normalized.append(item)
            c.execute(
                "INSERT INTO impact.derivative_manifest(tenant_id,derivative_id,derivative_revision_id,derivative_kind,disclosure_mode,created_by,created_at) VALUES(%s,%s,%s,%s,%s,%s,now())",
                (tenant, derivative_id, revision, body["kind"], mode, ctx.principal_id),
            )
            for ordinal, source in enumerate(normalized, 1):
                c.execute(
                    "INSERT INTO impact.derivative_source VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        tenant,
                        derivative_id,
                        revision,
                        ordinal,
                        source["object_id"],
                        source["revision_id"],
                        source["object_type"],
                        source["capability"],
                    ),
                )
        return {
            "derivative_id": derivative_id,
            "revision_id": revision,
            "kind": body["kind"],
            "disclosure_mode": mode,
            "source_count": len(normalized),
        }

    def read(self, identity, tenant, derivative_id, revision_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_derivative_manifest", derivative_id, hidden=True)
            manifest = c.execute(
                "SELECT derivative_kind,disclosure_mode FROM impact.derivative_manifest WHERE tenant_id=%s AND derivative_id=%s AND derivative_revision_id=%s",
                (tenant, derivative_id, revision_id),
            ).fetchone()
            if not manifest:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            sources = c.execute(
                "SELECT source_object_id,source_revision_id,source_object_type,required_capability FROM impact.derivative_source WHERE tenant_id=%s AND derivative_id=%s AND derivative_revision_id=%s ORDER BY ordinal",
                (tenant, derivative_id, revision_id),
            ).fetchall()
            for source in sources:
                load(
                    c,
                    ctx,
                    str(source["source_object_id"]),
                    source["source_object_type"],
                    source["required_capability"],
                )
            return {
                "derivative_id": derivative_id,
                "revision_id": revision_id,
                "kind": manifest["derivative_kind"],
                "disclosure_mode": manifest["disclosure_mode"],
                "sources": [
                    {
                        "object_id": str(s["source_object_id"]),
                        "revision_id": str(s["source_revision_id"]),
                        "object_type": s["source_object_type"],
                    }
                    for s in sources
                ],
            }
