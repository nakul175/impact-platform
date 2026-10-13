"""US-CM-08 local-currency invoice profiles and immutable tax issuance."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from psycopg.types.json import Jsonb
from .contracts import validate
from .domain import DomainError, unavailable
from .sponsored_access import record_audit
from .store import authorize, context, hash_data

SCALE = Decimal("0.000000000001")


class TaxInvoicing:
    def __init__(self, service):
        self.service = service

    @staticmethod
    def _receipt(c, tenant, principal, command, body, outcome, observed):
        c.execute(
            "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
            (
                tenant,
                principal,
                command,
                body["operation_id"],
                hash_data([command, body]),
                Jsonb(outcome),
                observed + timedelta(days=7),
            ),
        )

    @staticmethod
    def _replay(c, tenant, principal, command, body):
        old = c.execute(
            "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
            (tenant, principal, command, body["operation_id"]),
        ).fetchone()
        if not old:
            return None
        if bytes(old["payload_hash"]) != hash_data([command, body]):
            raise DomainError("CONFLICT_OPERATION", 409)
        return old["outcome"]

    def configure(self, identity, tenant, body, correlation):
        validate("BillingProfileConfigure", body)
        observed = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "configure_billing_profile", hidden=True)
            replay = self._replay(c, tenant, ctx.principal_id, "configure_billing_profile", body)
            if replay:
                return replay
            market = c.execute(
                "SELECT * FROM impact.billing_market_definition WHERE country_code=%s AND active",
                (body["country_code"],),
            ).fetchone()
            if not market:
                unavailable()
            c.execute(
                "INSERT INTO impact.tenant_billing_profile VALUES(%s,%s,%s,%s,%s) ON CONFLICT(tenant_id) DO UPDATE SET country_code=excluded.country_code,currency=excluded.currency,configured_by=excluded.configured_by,configured_at=excluded.configured_at",
                (tenant, market["country_code"], market["currency"], ctx.principal_id, observed),
            )
            outcome = {
                "country_code": market["country_code"],
                "currency": market["currency"],
                "tax_name": market["tax_name"],
                "tax_rate": str(market["tax_rate"]),
                "configured_at": observed.isoformat(),
            }
            record_audit(c, ctx, "billing.profile.configure", tenant, observed, correlation)
            self._receipt(c, tenant, ctx.principal_id, "configure_billing_profile", body, outcome, observed)
            return outcome

    def issue(self, identity, tenant, invoice_id, body, correlation):
        validate("CommercialInvoiceIssue", body)
        recorded = {**body, "invoice_id": str(invoice_id)}
        observed = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "issue_commercial_invoice", invoice_id, hidden=True)
            replay = self._replay(c, tenant, ctx.principal_id, "issue_commercial_invoice", recorded)
            if replay:
                return replay
            invoice = c.execute(
                "SELECT * FROM impact.commercial_invoice WHERE tenant_id=%s AND invoice_id=%s FOR UPDATE",
                (tenant, invoice_id),
            ).fetchone()
            if not invoice:
                unavailable()
            if invoice["status"] != "OPEN":
                raise DomainError("INVALID_STATE", 409, reason="INVOICE_ALREADY_ISSUED")
            market = c.execute(
                "SELECT m.* FROM impact.tenant_billing_profile p JOIN impact.billing_market_definition m ON m.country_code=p.country_code WHERE p.tenant_id=%s AND m.active",
                (tenant,),
            ).fetchone()
            if not market or market["currency"] != invoice["currency"]:
                raise DomainError("INVALID_STATE", 409, reason="BILLING_MARKET_NOT_AVAILABLE")
            if invoice["currency"] == "INR" and (
                market["country_code"] != "IN" or market["tax_name"] != "GST" or market["tax_rate"] <= 0
            ):
                raise DomainError("INVALID_STATE", 409, reason="GST_REQUIRED")
            subtotal = c.execute(
                "SELECT sum(unit_price*quantity) AS amount FROM impact.commercial_invoice_item WHERE tenant_id=%s AND invoice_id=%s",
                (tenant, invoice_id),
            ).fetchone()["amount"]
            if not subtotal or subtotal <= 0:
                raise DomainError("INVALID_STATE", 409, reason="EMPTY_INVOICE")
            tax_amount = (subtotal * Decimal(market["tax_rate"]) / Decimal(100)).quantize(
                SCALE, rounding=ROUND_HALF_UP
            )
            if tax_amount <= 0:
                raise DomainError("INCOMPATIBLE_MEASURE", reason="TAX_ROUNDS_TO_ZERO")
            total = subtotal + tax_amount
            c.execute(
                "UPDATE impact.commercial_invoice SET status='ISSUED',market_code=%s,subtotal=%s,tax_name=%s,tax_rate=%s,tax_amount=%s,total=%s,issued_at=%s,issued_by=%s WHERE tenant_id=%s AND invoice_id=%s",
                (
                    market["country_code"],
                    subtotal,
                    market["tax_name"],
                    market["tax_rate"],
                    tax_amount,
                    total,
                    observed,
                    ctx.principal_id,
                    tenant,
                    invoice_id,
                ),
            )
            outcome = self._outcome(
                invoice_id, invoice["currency"], market, subtotal, tax_amount, total, observed
            )
            record_audit(c, ctx, "commercial.invoice.issue", invoice_id, observed, correlation)
            self._receipt(
                c, tenant, ctx.principal_id, "issue_commercial_invoice", recorded, outcome, observed
            )
            return outcome

    def read(self, identity, tenant, invoice_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_commercial_invoice", invoice_id, hidden=True)
            row = c.execute(
                "SELECT * FROM impact.commercial_invoice WHERE tenant_id=%s AND invoice_id=%s AND status='ISSUED'",
                (tenant, invoice_id),
            ).fetchone()
            if not row:
                unavailable()
            return {
                "invoice_id": str(row["invoice_id"]),
                "currency": row["currency"],
                "country_code": row["market_code"],
                "subtotal": str(row["subtotal"]),
                "tax_name": row["tax_name"],
                "tax_rate": str(row["tax_rate"]),
                "tax_amount": str(row["tax_amount"]),
                "total": str(row["total"]),
                "issued_at": row["issued_at"].isoformat(),
            }

    @staticmethod
    def _outcome(invoice_id, currency, market, subtotal, tax_amount, total, observed):
        return {
            "invoice_id": str(invoice_id),
            "currency": currency,
            "country_code": market["country_code"],
            "subtotal": str(subtotal),
            "tax_name": market["tax_name"],
            "tax_rate": str(market["tax_rate"]),
            "tax_amount": str(tax_amount),
            "total": str(total),
            "issued_at": observed.isoformat(),
        }
