"""Governed dashboard pivots over one exact calculated-result revision (FR-ANA-005)."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from uuid import uuid4

from psycopg.types.json import Jsonb

from .domain import DomainError, decimal_value, stored, unavailable
from .store import audit, authorize, context, hash_data, load

LARGE_CARDINALITY = 100
OPEN_JOB_LIMIT = 10
TERMINAL = {"Succeeded", "SucceededWithIssues", "Failed", "Cancelled"}
SUPPORTED = {"DISTINCT_COUNT", "SUM", "MEAN"}


def _pivot(payload, dimension, statistic):
    if statistic not in SUPPORTED:
        raise DomainError("VALIDATION_FAILED", reason="PIVOT_STATISTIC_UNSUPPORTED")
    source_method = (payload.get("formula") or {}).get("method")
    compatible = {
        "DISTINCT_COUNT": {"DISTINCT_COUNT"},
        "SUM": {"SUM", "CUMULATIVE_DIFFERENCE"},
        "MEAN": {"MEAN", "MEDIAN", "MIN", "MAX"},
    }
    if source_method not in compatible[statistic]:
        alternatives = sorted(name for name, methods in compatible.items() if source_method in methods)
        raise DomainError(
            "VALIDATION_FAILED",
            reason="PIVOT_STATISTIC_INCOMPATIBLE",
            fields=[
                {
                    "path": "statistic",
                    "message": "Supported alternative: " + (alternatives[0] if alternatives else "none"),
                }
            ],
        )
    rows = [row for row in payload.get("disaggregation", []) if row.get("dimension") == dimension]
    cells = []
    nonadditive = False
    for row in rows:
        state = row.get("value_state")
        additivity = row.get("additivity") or "UNKNOWN"
        suppressed = state != "PRESENT"
        nonadditive = nonadditive or additivity in {"NON_ADDITIVE", "MULTISELECT", "DISTINCT"}
        cells.append(
            {
                "category": row.get("category"),
                "value_state": state,
                "value": row.get("value") if not suppressed else None,
                "displayed_value": row.get("displayed_value") if not suppressed else None,
                "disclosure": "SUPPRESSED" if suppressed else "VISIBLE",
                "additivity": additivity,
            }
        )
    present = payload.get("value_state") == "PRESENT" and payload.get("value") is not None
    grand_total = payload.get("value") if present else None
    if statistic == "MEAN" and present:
        contributors = [decimal_value(row["value"]) for row in rows if row.get("value_state") == "PRESENT"]
        if not contributors:
            grand_total = None
        else:
            with localcontext() as ctx:
                ctx.prec = 60
                grand_total = stored(sum(contributors, Decimal(0)) / len(contributors))
    return {
        "estimated_cardinality": len(cells),
        "cells": cells,
        "grand_total": grand_total,
        "grand_total_basis": "ELIGIBLE_SOURCE_RESULT" if statistic != "MEAN" else "UNROUNDED_ELIGIBLE_VALUES",
        "cells_may_exceed_grand_total": nonadditive,
        "explanation": (
            "Categories overlap; their displayed cells are not additive. The grand total is recalculated from the governed source result."
            if nonadditive
            else "The grand total comes from governed unrounded source semantics, never from displayed cells."
        ),
    }


class DashboardPivots:
    def __init__(self, service):
        self.service = service

    def _resolve(self, c, ctx, dashboard_id, data):
        authorize(c, ctx, "preview_dashboard_pivot", dashboard_id, hidden=True)
        dashboard = load(c, ctx, dashboard_id, "Dashboard", "dashboards.read")
        widget = next(
            (
                item
                for item in dashboard["payload"].get("widgets", [])
                if item["widget_id"] == data["widget_id"]
            ),
            None,
        )
        if not widget or widget["binding"]["resource_type"] != "CALCULATED_RESULT":
            unavailable()
        binding = widget["binding"]
        result = load(c, ctx, binding["object_id"], "CalculatedResult", "calculated-results.read")
        if str(result["head_revision"]) != binding["revision_id"]:
            unavailable()
        pivot = _pivot(result["payload"], data["row_dimension"], data["statistic"])
        return dashboard, result, pivot

    def preview(self, identity, tenant, dashboard_id, data):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            _, result, pivot = self._resolve(c, ctx, dashboard_id, data)
            return {
                **pivot,
                "execution": "ASYNC_CANCELLABLE_JOB"
                if pivot["estimated_cardinality"] > LARGE_CARDINALITY
                else "SYNC",
                "job_id": None,
                "result_id": str(result["object_id"]),
                "result_revision": str(result["head_revision"]),
                "statistic": data["statistic"],
                "row_dimension": data["row_dimension"],
            }

    def run(self, identity, tenant, dashboard_id, body, correlation):
        op = "action_dashboard_pivot_run"
        fingerprint = hash_data({"dashboard_id": str(dashboard_id), "data": body["data"]})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            dashboard, result, pivot = self._resolve(c, ctx, dashboard_id, body["data"])
            response = {
                **pivot,
                "execution": "SYNC",
                "job_id": None,
                "result_id": str(result["object_id"]),
                "result_revision": str(result["head_revision"]),
                "statistic": body["data"]["statistic"],
                "row_dimension": body["data"]["row_dimension"],
            }
            if pivot["estimated_cardinality"] > LARGE_CARDINALITY:
                open_jobs = c.execute(
                    "SELECT count(*) AS n FROM impact.job WHERE tenant_id=%s AND job_class='DASHBOARD_PIVOT' AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled')",
                    (tenant,),
                ).fetchone()["n"]
                if open_jobs >= OPEN_JOB_LIMIT:
                    raise DomainError("LIMIT_EXCEEDED", 429, reason="PIVOT_QUEUE_LIMIT")
                scope = dashboard["scope_id"]
                job_id = str(uuid4())
                response.update(execution="ASYNC_CANCELLABLE_JOB", job_id=job_id, cells=[], grand_total=None)
                c.execute(
                    "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest) VALUES(%s,%s,'DASHBOARD_PIVOT',%s,%s,'Queued',%s)",
                    (
                        tenant,
                        job_id,
                        ctx.principal_id,
                        scope,
                        Jsonb(
                            {
                                "dashboard_id": str(dashboard["object_id"]),
                                "pivot": {
                                    **pivot,
                                    "result_id": str(result["object_id"]),
                                    "result_revision": str(result["head_revision"]),
                                    "statistic": body["data"]["statistic"],
                                    "row_dimension": body["data"]["row_dimension"],
                                },
                            }
                        ),
                    ),
                )
            receipt = {
                "object_id": str(dashboard["object_id"]),
                "revision_id": str(dashboard["head_revision"]),
                "business_state": response["execution"],
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "operation_id": body["operation_id"],
                "correlation_id": correlation,
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
                    Jsonb(response),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return response

    def status(self, identity, tenant, dashboard_id, job_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_dashboard_pivot_job", dashboard_id, hidden=True)
            load(c, ctx, dashboard_id, "Dashboard", "dashboards.read")
            row = c.execute(
                "SELECT state,input_manifest,output_manifest,cancellation_requested_at FROM impact.job WHERE tenant_id=%s AND job_id=%s AND job_class='DASHBOARD_PIVOT' AND input_manifest->>'dashboard_id'=%s",
                (tenant, job_id, str(dashboard_id)),
            ).fetchone()
            if not row:
                unavailable()
            pin = row["input_manifest"]["pivot"]
            result = load(c, ctx, pin["result_id"], "CalculatedResult", "calculated-results.read")
            if str(result["head_revision"]) != pin["result_revision"]:
                unavailable()
            return {
                "job_id": str(job_id),
                "state": row["state"],
                "cancellation_requested": row["cancellation_requested_at"] is not None,
                "result": row["output_manifest"] if row["state"] in TERMINAL else None,
            }

    def cancel(self, identity, tenant, dashboard_id, job_id, body, correlation):
        op = "cancel_dashboard_pivot_job"
        fingerprint = hash_data({"dashboard_id": str(dashboard_id), "job_id": str(job_id)})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            authorize(c, ctx, "cancel_dashboard_pivot_job", dashboard_id, hidden=True)
            dashboard = load(c, ctx, dashboard_id, "Dashboard", "dashboards.read")
            row = c.execute(
                "UPDATE impact.job SET cancellation_requested_at=COALESCE(cancellation_requested_at,now()) WHERE tenant_id=%s AND job_id=%s AND job_class='DASHBOARD_PIVOT' AND input_manifest->>'dashboard_id'=%s AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled') RETURNING state",
                (tenant, job_id, str(dashboard_id)),
            ).fetchone()
            if not row:
                unavailable()
            response = {
                "job_id": str(job_id),
                "state": row["state"],
                "cancellation_requested": True,
                "result": None,
            }
            receipt = {
                "object_id": str(dashboard_id),
                "revision_id": str(dashboard["head_revision"]),
                "business_state": "CancellationRequested",
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "operation_id": body["operation_id"],
                "correlation_id": correlation,
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
                    Jsonb(response),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return response
