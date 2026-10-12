"""Safe effective-access explanations without resource names or field values."""

from datetime import datetime, timezone
from uuid import UUID

from .contracts import OPERATIONS
from .domain import DomainError
from .store import authorize, context


def _invalid():
    raise DomainError("VALIDATION_FAILED", 400, reason="EFFECTIVE_ACCESS_REQUEST_INVALID")


class EffectiveAccess:
    def __init__(self, service):
        self.service = service

    @staticmethod
    def _request(body, simulation=False):
        required = {"operation_id", "object_id"} | ({"subject_principal_id"} if simulation else set())
        if not isinstance(body, dict) or set(body) != required or body["operation_id"] not in OPERATIONS:
            _invalid()
        try:
            obj = str(UUID(body["object_id"])) if body["object_id"] is not None else None
            subject = str(UUID(body["subject_principal_id"])) if simulation else None
        except (TypeError, ValueError, AttributeError):
            _invalid()
        return body["operation_id"], obj, subject

    @staticmethod
    def _grants(c, tenant, principal, membership):
        now = datetime.now(timezone.utc)
        direct = c.execute(
            "SELECT 'DIRECT' AS source,g.object_id,g.capability,g.scope_id,g.purpose,s.scope_type,f.record_object_ids,f.readable_field_categories,f.writable_field_categories FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id LEFT JOIN impact.grant_access_facet f ON f.tenant_id=g.tenant_id AND f.grant_id=g.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND r.lifecycle_state='Active' AND g.starts_at<=%s AND (g.expires_at IS NULL OR g.expires_at>%s)",
            (tenant, principal, now, now),
        ).fetchall()
        groups = c.execute(
            "SELECT 'GROUP' AS source,e.group_id AS object_id,e.capability,e.scope_id,NULL AS purpose,s.scope_type,NULL::uuid[] AS record_object_ids,NULL::text[] AS readable_field_categories,NULL::text[] AS writable_field_categories FROM impact.group_entitlement e JOIN impact.object_registry r ON r.tenant_id=e.tenant_id AND r.object_id=e.group_id JOIN impact.scope_definition s ON s.tenant_id=e.tenant_id AND s.scope_id=e.scope_id WHERE e.tenant_id=%s AND e.membership_id=%s AND e.expires_at>%s AND r.lifecycle_state='Active'",
            (tenant, membership, now),
        ).fetchall()
        return [*direct, *groups]

    @staticmethod
    def _explain(c, tenant, operation_id, object_id, grants, identity=None):
        operation = OPERATIONS[operation_id]
        paths = []
        for grant in grants:
            if grant["capability"] != operation["capability"] or grant["purpose"] is not None:
                continue
            record_ids = grant.get("record_object_ids")
            if record_ids and (not object_id or object_id not in {str(value) for value in record_ids}):
                continue
            if grant["scope_type"] != "TENANT":
                if (
                    not object_id
                    or not c.execute(
                        "SELECT 1 FROM impact.scope_member WHERE tenant_id=%s AND scope_id=%s AND object_id=%s",
                        (tenant, grant["scope_id"], object_id),
                    ).fetchone()
                ):
                    continue
            paths.append(
                {
                    "source": grant["source"],
                    "scope_type": grant["scope_type"],
                    "scope_id": str(grant["scope_id"]),
                    "record_condition_applied": bool(record_ids),
                    "readable_field_categories": grant.get("readable_field_categories"),
                    "writable_field_categories": grant.get("writable_field_categories"),
                }
            )
        missing = []
        seconds = operation.get("fresh_assurance_seconds")
        if seconds:
            if identity is None:
                missing.append("CURRENT_SESSION_ASSURANCE")
            else:
                if not getattr(identity, "assurance_verified", True):
                    missing.append("MFA_ASSURANCE")
                if (datetime.now(timezone.utc) - identity.auth_time).total_seconds() > seconds:
                    missing.append("FRESH_AUTHENTICATION")
        return {
            "operation_id": operation_id,
            "capability": operation["capability"],
            "decision": "PERMITTED" if paths and not missing else "DENIED",
            "grant_paths": paths,
            "restrictions": ["RECORD_CONDITION"] if any(p["record_condition_applied"] for p in paths) else [],
            "missing_assurance": missing,
        }

    def own(self, identity, tenant, body):
        operation, object_id, _ = self._request(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "explain_own_effective_access")
            return self._explain(c, tenant, operation, object_id, ctx.grants, identity)

    def simulate(self, identity, tenant, body):
        operation, object_id, subject = self._request(body, simulation=True)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "simulate_effective_access")
            target = c.execute(
                "SELECT p.principal_id,m.object_id AS membership_id FROM impact.tenant_principal p JOIN impact.membership_current m ON m.tenant_id=p.tenant_id AND m.identity_id=p.identity_id JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id WHERE p.tenant_id=%s AND p.principal_id=%s AND p.active AND r.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now())",
                (tenant, subject),
            ).fetchone()
            if not target:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            grants = self._grants(c, tenant, target["principal_id"], target["membership_id"])
            result = self._explain(c, tenant, operation, object_id, grants)
            result["subject_principal_id"] = subject
            return result
