"""US-CM-07 platform partner revenue statements reconciled to invoice totals."""

from datetime import timedelta
from decimal import Decimal
from uuid import uuid4
from psycopg.types.json import Jsonb
from .clock import now
from .domain import DomainError, unavailable
from .partner_revenue_contracts import validate_body
from .store import hash_data


class PartnerRevenue:
    def __init__(self, lifecycle):
        self.lifecycle, self.db = lifecycle, lifecycle.db

    def _begin(self, c, identity, operation, body):
        self.lifecycle.assurance(identity)
        if not self.lifecycle.operator(c, identity):
            raise DomainError("POLICY_DENIED", 403)
        fingerprint = hash_data([operation, body])
        c.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
            ("partner-revenue:" + body["operation_id"],),
        )
        old = c.execute(
            "SELECT * FROM impact.platform_receipt WHERE identity_id=%s AND operation_id=%s",
            (identity.identity_id, body["operation_id"]),
        ).fetchone()
        if old:
            if bytes(old["fingerprint"]) != fingerprint or old["expires_at"] <= now():
                raise DomainError("CONFLICT_VERSION", 409, reason="OPERATION_REUSE")
            return fingerprint, old["response"]
        return fingerprint, None

    def _record(self, c, identity, body, fingerprint, action, response):
        c.execute(
            "INSERT INTO impact.platform_event(event_id,tenant_id,identity_id,action,revision_id,reason,payload) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (
                str(uuid4()),
                body.get("tenant_id"),
                identity.identity_id,
                action,
                response.get("statement_id") or response.get("entry_id"),
                body["reason"],
                Jsonb(response),
            ),
        )
        c.execute(
            "INSERT INTO impact.platform_receipt VALUES(%s,%s,%s,%s,%s)",
            (
                identity.identity_id,
                body["operation_id"],
                fingerprint,
                Jsonb(response),
                now() + timedelta(days=7),
            ),
        )

    def entry(self, identity, body):
        validate_body("PartnerRevenueEntryCreate", body)
        with self.db.transaction(platform=True) as c:
            fingerprint, replay = self._begin(c, identity, "record_partner_revenue", body)
            if replay:
                return replay
            if c.execute(
                "SELECT 1 FROM impact.partner_monthly_statement WHERE partner_id=%s AND month=date_trunc('month',%s::date)::date",
                (body["partner_id"], body["occurred_on"]),
            ).fetchone():
                raise DomainError("INVALID_STATE", 409, reason="STATEMENT_ALREADY_GENERATED")
            invoice = c.execute(
                "SELECT * FROM impact.platform_invoice_total(%s,%s)", (body["tenant_id"], body["invoice_id"])
            ).fetchone()
            if not invoice:
                unavailable()
            if invoice["currency"] != body["currency"] or invoice["total"] != Decimal(body["amount"]):
                raise DomainError("INCOMPATIBLE_MEASURE", reason="INVOICE_RECONCILIATION_FAILED")
            entry_id = str(uuid4())
            observed = now()
            c.execute(
                "INSERT INTO impact.partner_revenue_entry VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    entry_id,
                    body["partner_id"],
                    body["tenant_id"],
                    body["invoice_id"],
                    body["amount"],
                    body["currency"],
                    body["occurred_on"],
                    identity.identity_id,
                    observed,
                ),
            )
            response = {
                "entry_id": entry_id,
                **{
                    k: body[k]
                    for k in ("partner_id", "tenant_id", "invoice_id", "amount", "currency", "occurred_on")
                },
                "reconciled": True,
            }
            self._record(c, identity, body, fingerprint, "partner.revenue.record", response)
            return response

    def statement(self, identity, body):
        validate_body("PartnerStatementGenerate", body)
        with self.db.transaction(platform=True) as c:
            fingerprint, replay = self._begin(c, identity, "generate_partner_statement", body)
            if replay:
                return replay
            if c.execute(
                "SELECT 1 FROM impact.partner_monthly_statement WHERE partner_id=%s AND month=%s",
                (body["partner_id"], body["month"]),
            ).fetchone():
                raise DomainError("INVALID_STATE", 409, reason="STATEMENT_ALREADY_GENERATED")
            rows = c.execute(
                "SELECT * FROM impact.partner_revenue_entry WHERE partner_id=%s AND occurred_on>=%s::date AND occurred_on<(%s::date+interval '1 month') ORDER BY entry_id",
                (body["partner_id"], body["month"], body["month"]),
            ).fetchall()
            if not rows:
                unavailable()
            currencies = {r["currency"] for r in rows}
            if len(currencies) != 1:
                raise DomainError("INCOMPATIBLE_MEASURE", reason="MIXED_STATEMENT_CURRENCY")
            reconciled = True
            for row in rows:
                invoice = c.execute(
                    "SELECT * FROM impact.platform_invoice_total(%s,%s)",
                    (row["tenant_id"], row["invoice_id"]),
                ).fetchone()
                reconciled &= bool(
                    invoice and invoice["currency"] == row["currency"] and invoice["total"] == row["amount"]
                )
            statement_id = str(uuid4())
            total = sum((r["amount"] for r in rows), Decimal(0))
            observed = now()
            response = {
                "statement_id": statement_id,
                "partner_id": body["partner_id"],
                "month": body["month"],
                "currency": next(iter(currencies)),
                "amount": str(total),
                "entry_ids": [str(r["entry_id"]) for r in rows],
                "reconciled": reconciled,
                "settled": False,
            }
            c.execute(
                "INSERT INTO impact.partner_monthly_statement(statement_id,partner_id,month,currency,amount,reconciled,entry_ids,generated_by,generated_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    statement_id,
                    body["partner_id"],
                    body["month"],
                    response["currency"],
                    total,
                    reconciled,
                    Jsonb(response["entry_ids"]),
                    identity.identity_id,
                    observed,
                ),
            )
            self._record(c, identity, body, fingerprint, "partner.statement.generate", response)
            return response

    def settle(self, identity, statement_id, body):
        validate_body("PartnerStatementSettle", body)
        with self.db.transaction(platform=True) as c:
            recorded = {**body, "statement_id": str(statement_id)}
            fingerprint, replay = self._begin(c, identity, "settle_partner_statement", recorded)
            if replay:
                return replay
            row = c.execute(
                "SELECT * FROM impact.partner_monthly_statement WHERE statement_id=%s FOR UPDATE",
                (statement_id,),
            ).fetchone()
            if not row:
                unavailable()
            if not row["reconciled"]:
                raise DomainError("INVALID_STATE", 409, reason="UNRECONCILED_STATEMENT")
            if row["settled_at"]:
                raise DomainError("INVALID_STATE", 409, reason="ALREADY_SETTLED")
            for entry_id in row["entry_ids"]:
                entry = c.execute(
                    "SELECT * FROM impact.partner_revenue_entry WHERE entry_id=%s", (entry_id,)
                ).fetchone()
                invoice = (
                    entry
                    and c.execute(
                        "SELECT * FROM impact.platform_invoice_total(%s,%s)",
                        (entry["tenant_id"], entry["invoice_id"]),
                    ).fetchone()
                )
                if (
                    not invoice
                    or invoice["currency"] != entry["currency"]
                    or invoice["total"] != entry["amount"]
                ):
                    raise DomainError("INVALID_STATE", 409, reason="UNRECONCILED_STATEMENT")
            observed = now()
            c.execute(
                "UPDATE impact.partner_monthly_statement SET settled_at=%s,settled_by=%s WHERE statement_id=%s",
                (observed, identity.identity_id, statement_id),
            )
            response = {
                "statement_id": str(statement_id),
                "reconciled": True,
                "settled": True,
                "settled_at": observed.isoformat(),
            }
            self._record(c, identity, recorded, fingerprint, "partner.statement.settle", response)
            return response
