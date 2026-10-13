"""Versioned budget and finance governance."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from psycopg.types.json import Jsonb
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write


class FinanceGovernance:
    def __init__(self, service):
        self.service = service

    def _run(self, identity, tenant, op, body, correlation, fn):
        fingerprint = hash_data(body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "create_dashboards")
            old = c.execute(
                "SELECT payload_hash,outcome FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            receipt = fn(c, ctx)
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

    def create_budget(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            d = body["data"]
            total = sum((Decimal(x["amount"]) for x in d["lines"]), Decimal(0))
            payload = {
                **d,
                "total": format(total, "f"),
                "original_baseline_revision": None,
                "current_baseline_revision": None,
                "actual_expenditure_relation": "INDEPENDENT_UNCHANGED",
            }
            return write(c, ctx, "BudgetVersion", payload, state="Draft")

        return self._run(identity, tenant, "create_budget_version", body, correlation, apply)

    def revise_budget(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            d = body["data"]
            base = load(c, ctx, d["budget_id"], "BudgetVersion", lock=True)
            total = sum((Decimal(x["amount"]) for x in d["lines"]), Decimal(0))
            original = base["payload"].get("original_baseline_revision") or str(base["head_revision"])
            payload = {
                **base["payload"],
                "lines": d["lines"],
                "rate_assumptions": d["rate_assumptions"],
                "total": format(total, "f"),
                "original_baseline_revision": original,
                "current_baseline_revision": str(base["head_revision"]),
                "comparison": {
                    "original_total": base["payload"]["total"],
                    "current_total": format(total, "f"),
                },
                "actual_expenditure_relation": "INDEPENDENT_UNCHANGED",
            }
            return write(c, ctx, "BudgetVersion", payload, state="Draft", previous=base)

        return self._run(identity, tenant, "revise_budget_version", body, correlation, apply)

    def approve_budget(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            d = body["data"]
            row = load(c, ctx, d["budget_id"], "BudgetVersion", lock=True)
            if str(row["head_revision"]) != d["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            payload = {
                **row["payload"],
                "approved_budget_revision": str(row["head_revision"]),
                "pinned_rate_assumptions": row["payload"]["rate_assumptions"],
                "historical_variance_relation": "UNCHANGED",
                "actual_expenditure_relation": "INDEPENDENT_UNCHANGED",
            }
            return write(c, ctx, "BudgetVersion", payload, state="Approved", previous=row)

        return self._run(identity, tenant, "approve_budget_version", body, correlation, apply)

    def import_expenditure(self, identity, tenant, body, correlation):
        def apply(c, ctx):
            data = body["data"]
            calculated = sum((Decimal(row["amount"]) for row in data["transactions"]), Decimal(0))
            if calculated != Decimal(data["control_total"]) and not data["permitted_exception"]:
                raise DomainError("CONTROL_TOTAL_UNBALANCED", 409)
            prior_batch = c.execute(
                "SELECT r.*,v.payload FROM impact.object_registry r JOIN impact.object_revision v "
                "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
                "WHERE r.tenant_id=%s AND r.object_type='ExpenditureImport' AND v.payload->>'file_sha256'=%s",
                (tenant, data["file_sha256"]),
            ).fetchone()
            if prior_batch:
                return {
                    "object_id": str(prior_batch["object_id"]),
                    "revision_id": str(prior_batch["head_revision"]),
                    "business_state": "Reconciled",
                    "saved_at": datetime.now(timezone.utc).isoformat(),
                    "repeated_file": True,
                }
            imported, reconciled = [], []
            for transaction in data["transactions"]:
                current = c.execute(
                    "SELECT r.*,v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
                    "WHERE r.tenant_id=%s AND r.object_type='ExpenditureTransaction' AND v.payload->>'source_system'=%s AND v.payload->>'source_transaction_key'=%s ORDER BY r.updated_at DESC LIMIT 1",
                    (tenant, data["source_system"], transaction["source_transaction_key"]),
                ).fetchone()
                candidate = {**transaction, "source_system": data["source_system"]}
                if current and {key: current["payload"].get(key) for key in candidate} == candidate:
                    reconciled.append(str(current["object_id"]))
                    continue
                if current and transaction["adjustment_semantic"] == "ORIGINAL":
                    raise DomainError("EXPLICIT_CORRECTION_SEMANTIC_REQUIRED", 409)
                candidate["supersedes_revision"] = str(current["head_revision"]) if current else None
                imported.append(
                    write(
                        c, ctx, "ExpenditureTransaction", candidate, state=transaction["adjustment_semantic"]
                    )
                )
            return write(
                c,
                ctx,
                "ExpenditureImport",
                {
                    **data,
                    "calculated_total": format(calculated, "f"),
                    "imported_transaction_ids": [x["object_id"] for x in imported],
                    "reconciled_transaction_ids": reconciled,
                    "approval_state": "APPROVED"
                    if calculated == Decimal(data["control_total"]) or data["permitted_exception"]
                    else "BLOCKED",
                },
                state="Reconciled",
            )

        return self._run(identity, tenant, "import_expenditure", body, correlation, apply)
