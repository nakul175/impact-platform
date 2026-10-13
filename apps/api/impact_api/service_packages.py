"""US-CM-06 fixed-fee packages bound to the subscription invoice."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from psycopg.types.json import Jsonb
from .contracts import validate
from .domain import DomainError, unavailable
from .sponsored_access import record_audit
from .store import authorize, context, hash_data

CATALOGUE = (
    {
        "package_code": "DEPLOYMENT_START",
        "title": "Deployment start",
        "scope": "Configuration workshop, deployment checklist and one administrator handover session.",
        "price": "75000",
        "currency": "INR",
    },
    {
        "package_code": "DATA_MIGRATION_ASSIST",
        "title": "Data migration assist",
        "scope": "One agreed source export mapping, validation report and supervised import handover.",
        "price": "125000",
        "currency": "INR",
    },
)


class ServicePackages:
    def __init__(self, service):
        self.service = service

    def listing(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_service_packages", hidden=True)
            result = {"items": [dict(row) for row in CATALOGUE]}
            validate("ServicePackageList", result)
            return result

    def purchase(self, identity, tenant, subscription_id, body, correlation):
        validate("ServicePackagePurchase", body)
        fingerprint = hash_data(["purchase_service_package", subscription_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "purchase_service_package", subscription_id, hidden=True)
            now = datetime.now(timezone.utc)
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type='purchase_service_package' AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            subscription = c.execute(
                "SELECT s.* FROM impact.subscription_current s JOIN impact.object_registry r ON r.tenant_id=s.tenant_id AND r.object_id=s.object_id WHERE s.tenant_id=%s AND s.object_id=%s AND r.lifecycle_state='Active' AND s.commercial_status='ACTIVE' AND (s.effective_at IS NULL OR s.effective_at<=%s) AND (s.ends_at IS NULL OR s.ends_at>%s)",
                (tenant, subscription_id, now, now),
            ).fetchone()
            if not subscription:
                unavailable()
            package = next((row for row in CATALOGUE if row["package_code"] == body["package_code"]), None)
            if package is None:
                unavailable()
            invoice = c.execute(
                "SELECT * FROM impact.commercial_invoice WHERE tenant_id=%s AND subscription_id=%s AND status='OPEN' FOR UPDATE",
                (tenant, subscription_id),
            ).fetchone()
            if not invoice:
                invoice_id = str(uuid4())
                c.execute(
                    "INSERT INTO impact.commercial_invoice VALUES(%s,%s,%s,%s,'OPEN',%s)",
                    (tenant, invoice_id, subscription_id, package["currency"], now),
                )
            else:
                invoice_id = str(invoice["invoice_id"])
                if invoice["currency"] != package["currency"]:
                    raise DomainError("INCOMPATIBLE_MEASURE", reason="INVOICE_CURRENCY_MISMATCH")
            item_id = str(uuid4())
            c.execute(
                "INSERT INTO impact.commercial_invoice_item VALUES(%s,%s,%s,'FIXED_FEE_SERVICE',%s,%s,1,%s,%s,%s,%s)",
                (
                    tenant,
                    invoice_id,
                    item_id,
                    package["package_code"],
                    package["scope"],
                    package["price"],
                    package["currency"],
                    ctx.principal_id,
                    now,
                ),
            )
            outcome = {
                "invoice_id": invoice_id,
                "subscription_id": str(subscription_id),
                "item_id": item_id,
                **package,
                "quantity": 1,
                "separate_invoice_created": False,
            }
            record_audit(c, ctx, "service.package.purchase", item_id, now, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,'purchase_service_package',%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    now + timedelta(days=7),
                ),
            )
            return outcome
