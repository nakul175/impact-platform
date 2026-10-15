"""Safe effective-access explanations without resource names or field values."""

from datetime import datetime, timezone
from uuid import UUID

from .contracts import OPERATIONS
from .domain import DomainError
from .store import _matching_grants, _record_restriction_allows, authorize, context

FIELD_CATEGORIES = {"PUBLIC", "INTERNAL", "SENSITIVE", "DIRECT_IDENTIFIER"}


def _invalid():
    raise DomainError("VALIDATION_FAILED", 400, reason="EFFECTIVE_ACCESS_REQUEST_INVALID")


class EffectiveAccess:
    def __init__(self, service):
        self.service = service

    @staticmethod
    def _request(body, simulation=False):
        required = {"operation_id", "object_id"} | ({"subject_principal_id"} if simulation else set())
        optional = {"purpose", "field_category", "field_access"}
        if (
            not isinstance(body, dict)
            or not required <= set(body)
            or set(body) - required - optional
            or body["operation_id"] not in OPERATIONS
            or body.get("field_category") not in FIELD_CATEGORIES | {None}
            or body.get("field_access") not in {"READ", "WRITE", None}
            or (body.get("field_category") is None) != (body.get("field_access") is None)
            or (
                body.get("purpose") is not None
                and (not isinstance(body["purpose"], str) or not 1 <= len(body["purpose"]) <= 100)
            )
        ):
            _invalid()
        try:
            obj = str(UUID(body["object_id"])) if body["object_id"] is not None else None
            subject = str(UUID(body["subject_principal_id"])) if simulation else None
        except (TypeError, ValueError, AttributeError):
            _invalid()
        return (
            body["operation_id"],
            obj,
            subject,
            body.get("purpose"),
            body.get("field_category"),
            body.get("field_access"),
        )

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
    def _explain(
        c,
        tenant,
        operation_id,
        object_id,
        grants,
        identity=None,
        purpose=None,
        field_category=None,
        field_access=None,
    ):
        operation = OPERATIONS[operation_id]
        matching = _matching_grants(grants, operation["capability"], purpose)
        record_allowed = _record_restriction_allows(matching, object_id)
        candidate_grants = [grant for grant in grants if grant["capability"] == operation["capability"]]
        field_key = "writable_field_categories" if field_access == "WRITE" else "readable_field_categories"
        field_restrictions = [grant.get(field_key) for grant in matching if grant.get(field_key) is not None]
        field_allowed = (
            not field_category
            or not field_restrictions
            or all(field_category in categories for categories in field_restrictions)
        )
        object_available = True
        if object_id:
            object_available = bool(
                c.execute(
                    "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s "
                    "AND lifecycle_state<>'Deleted'",
                    (tenant, object_id),
                ).fetchone()
            )
        paths = []
        all_restrictions = set()
        for position, grant in enumerate(matching, 1):
            restrictions = []
            record_ids = grant.get("record_object_ids")
            if record_ids and (not object_id or object_id not in {str(value) for value in record_ids}):
                restrictions.append("RECORD_CONDITION")
            if grant["scope_type"] != "TENANT":
                if (
                    not object_id
                    or not c.execute(
                        "SELECT 1 FROM impact.scope_member WHERE tenant_id=%s AND scope_id=%s AND object_id=%s",
                        (tenant, grant["scope_id"], object_id),
                    ).fetchone()
                ):
                    restrictions.append("OUTSIDE_SCOPE")
            categories = grant.get(
                "writable_field_categories" if field_access == "WRITE" else "readable_field_categories"
            )
            if field_category and categories is not None and field_category not in categories:
                restrictions.append("FIELD_CATEGORY")
            all_restrictions.update(restrictions)
            paths.append(
                {
                    "path_id": f"PATH-{position}",
                    "source": grant["source"],
                    "scope_type": grant["scope_type"],
                    "record_condition_applied": bool(record_ids),
                    "readable_field_categories": grant.get("readable_field_categories"),
                    "writable_field_categories": grant.get("writable_field_categories"),
                    "decision": "DENIED" if restrictions else "PERMITTED",
                    "restrictions": restrictions,
                }
            )
        missing = []
        if operation.get("purpose_required") and not purpose:
            missing.append("PURPOSE_REQUIRED")
        elif purpose and candidate_grants and not matching:
            missing.append("PURPOSE_MISMATCH")
        seconds = operation.get("fresh_assurance_seconds")
        if seconds:
            if identity is None:
                missing.append("CURRENT_SESSION_ASSURANCE")
            else:
                if not getattr(identity, "assurance_verified", True):
                    missing.append("MFA_ASSURANCE")
                if (datetime.now(timezone.utc) - identity.auth_time).total_seconds() > seconds:
                    missing.append("FRESH_AUTHENTICATION")
        if not object_available:
            all_restrictions.add("RESOURCE_UNAVAILABLE")
        if not record_allowed:
            all_restrictions.add("RECORD_CONDITION")
        if not field_allowed:
            all_restrictions.add("FIELD_CATEGORY")
        permitted_path = any(path["decision"] == "PERMITTED" for path in paths)
        return {
            "operation_id": operation_id,
            "capability": operation["capability"],
            "decision": (
                "PERMITTED"
                if permitted_path and record_allowed and field_allowed and object_available and not missing
                else "DENIED"
            ),
            "grant_paths": paths,
            "restrictions": sorted(all_restrictions),
            "missing_assurance": missing,
        }

    def own(self, identity, tenant, body):
        operation, object_id, _, purpose, field_category, field_access = self._request(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "explain_own_effective_access")
            return self._explain(
                c,
                tenant,
                operation,
                object_id,
                ctx.grants,
                identity,
                purpose,
                field_category,
                field_access,
            )

    def simulate(self, identity, tenant, body):
        operation, object_id, subject, purpose, field_category, field_access = self._request(
            body, simulation=True
        )
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
            return self._explain(
                c,
                tenant,
                operation,
                object_id,
                grants,
                purpose=purpose,
                field_category=field_category,
                field_access=field_access,
            )
