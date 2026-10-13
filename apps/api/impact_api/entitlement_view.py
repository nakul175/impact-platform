"""US-CM-03 source-labelled effective commercial entitlements."""

from .contracts import validate
from .store import authorize, context


class EntitlementView:
    def __init__(self, service):
        self.service = service

    def read(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_effective_entitlements", hidden=True)
            direct = c.execute(
                "SELECT s.* FROM impact.subscription_current s JOIN impact.object_registry r ON r.tenant_id=s.tenant_id AND r.object_id=s.object_id WHERE s.tenant_id=%s AND r.lifecycle_state='Active' AND s.commercial_status='ACTIVE' AND (s.effective_at IS NULL OR s.effective_at<=statement_timestamp()) AND (s.ends_at IS NULL OR s.ends_at>statement_timestamp()) ORDER BY s.object_id",
                (tenant,),
            ).fetchall()
            sponsored = c.execute(
                "SELECT * FROM impact.sponsored_enrolment WHERE grantee_tenant_id=%s AND status='ACCEPTED' AND access_starts_at<=statement_timestamp() AND access_ends_at>statement_timestamp() ORDER BY sponsor_tenant_id,enrolment_id",
                (tenant,),
            ).fetchall()
            direct_sources = [
                {
                    "source_type": "DIRECT_SUBSCRIPTION",
                    "source_id": str(row["object_id"]),
                    "source_tenant_id": str(tenant),
                    "reference": row["plan_reference"] or "UNSPECIFIED_DIRECT_PLAN",
                    "chargeable": index == 0,
                }
                for index, row in enumerate(direct)
            ]
            sources = direct_sources + [
                {
                    "source_type": "SPONSORSHIP",
                    "source_id": str(row["enrolment_id"]),
                    "source_tenant_id": str(row["sponsor_tenant_id"]),
                    "reference": row["terms_version"],
                    "chargeable": False,
                }
                for row in sponsored
            ]
            items = []
            if sources:
                items.append(
                    {
                        "entitlement": "PLATFORM_ACCESS",
                        "sources": sources,
                        "charge_count": 1 if direct else 0,
                        "charge_source_id": direct_sources[0]["source_id"] if direct_sources else None,
                        "duplicate_charge_prevented": len(direct) > 1,
                    }
                )
            result = {"items": items}
            validate("EffectiveEntitlementList", result)
            return result
