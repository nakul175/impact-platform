"""Versioned planning scenarios from exact official result revisions."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import authorize, context, load

METHOD = "LINEAR_TREND_V1"
QUANT = Decimal("0.000001")


def _decimal(value):
    try:
        return Decimal(value).quantize(QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError):
        raise DomainError("VALIDATION_FAILED", 400, reason="FORECAST_VALUE_INVALID") from None


def _text(value):
    return format(value.quantize(QUANT, rounding=ROUND_HALF_UP), "f")


class AIForecasts:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, body):
        operation = str(UUID(body["operation_id"]))
        scenario = str(UUID(body["scenario_id"])) if body.get("scenario_id") else str(uuid4())
        revisions = [str(UUID(value)) for value in body["input_result_revisions"]]
        fingerprint = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).digest()
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_forecast", hidden=True)
            prior = c.execute(
                "SELECT * FROM impact.ai_forecast_scenario WHERE tenant_id=%s AND operation_id=%s",
                (tenant, operation),
            ).fetchone()
            if prior:
                if bytes(prior["request_fingerprint"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409, reason="FORECAST_OPERATION_CHANGED")
                self._recheck(c, ctx, prior)
                return self._view(c, prior)
            values, sources, unit = [], [], None
            for ordinal, revision in enumerate(revisions, 1):
                source = c.execute(
                    "SELECT object_id,payload,restriction_state FROM impact.object_revision "
                    "WHERE tenant_id=%s AND revision_id=%s AND object_type='CalculatedResult'",
                    (tenant, revision),
                ).fetchone()
                if not source or source["restriction_state"] != "AVAILABLE":
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                current = load(c, ctx, source["object_id"], "CalculatedResult", "calculated-results.read")
                payload = source["payload"]
                if payload.get("mode") != "OFFICIAL" or payload.get("value_state") != "PRESENT":
                    raise DomainError("CONFLICT_OPERATION", 409, reason="FORECAST_INPUT_NOT_OFFICIAL")
                found_unit = (payload.get("formula") or {}).get("unit")
                if not found_unit or (unit is not None and found_unit != unit):
                    raise DomainError("CONFLICT_OPERATION", 409, reason="FORECAST_INPUT_UNIT_MISMATCH")
                unit = found_unit
                values.append(_decimal(payload.get("value")))
                sources.append((ordinal, str(source["object_id"]), revision))
                # Current authority is rechecked even when the exact historical revision differs.
                if not current:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if not values:
                raise DomainError("VALIDATION_FAILED", 400, reason="FORECAST_EVIDENCE_REQUIRED")
            bounded = len(values) < 3
            delta = (
                sum((values[index] - values[index - 1] for index in range(1, len(values))), Decimal(0))
                / Decimal(len(values) - 1)
                if len(values) > 1
                else Decimal(0)
            )
            uncertainty = max(
                [abs(values[index] - values[index - 1] - delta) for index in range(1, len(values))]
                or [abs(values[-1])]
            )
            projections = []
            for step in range(1, body["horizon"] + 1):
                value = values[-1] + delta * step
                spread = uncertainty * step
                projections.append(
                    {
                        "step": step,
                        "value": _text(value),
                        "lower": _text(value - spread),
                        "upper": _text(value + spread),
                    }
                )
            version = c.execute(
                "SELECT COALESCE(max(version),0)+1 AS version FROM impact.ai_forecast_scenario "
                "WHERE tenant_id=%s AND scenario_id=%s",
                (tenant, scenario),
            ).fetchone()["version"]
            status = "EXPLORATORY" if bounded else "PROJECTION"
            label = ("Exploratory: " if bounded else "Scenario: ") + body["label"]
            validation = {
                "method": METHOD,
                "input_count": len(values),
                "minimum_for_projection": 3,
                "evidence_sufficient": not bounded,
                "uncertainty_method": "MAX_ABSOLUTE_DELTA_RESIDUAL_V1",
            }
            row = c.execute(
                "INSERT INTO impact.ai_forecast_scenario(tenant_id,scenario_id,version,operation_id,requester_id,"
                "request_fingerprint,label,status,horizon,method,assumptions,validation_history,unit,projections,created_at) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp()) RETURNING *",
                (
                    tenant,
                    scenario,
                    version,
                    operation,
                    ctx.principal_id,
                    fingerprint,
                    label,
                    status,
                    body["horizon"],
                    METHOD,
                    Jsonb(body["assumptions"]),
                    Jsonb(validation),
                    unit,
                    Jsonb(projections),
                ),
            ).fetchone()
            for ordinal, object_id, revision in sources:
                c.execute(
                    "INSERT INTO impact.ai_forecast_input VALUES(%s,%s,%s,%s,%s,%s)",
                    (tenant, scenario, version, ordinal, object_id, revision),
                )
            return self._view(c, row)

    def get(self, identity, tenant, scenario, version=None):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_forecast", hidden=True)
            row = self._row(c, tenant, scenario, version)
            self._recheck(c, ctx, row)
            return self._view(c, row)

    def export(self, identity, tenant, scenario, version=None):
        view = self.get(identity, tenant, scenario, version)
        return {
            "scenario_id": view["scenario_id"],
            "version": view["version"],
            "series": [
                {
                    "kind": "ACTUAL",
                    "unit": view["unit"],
                    "values": [
                        {"step": i + 1, "revision_id": item["revision_id"], "value": item["value"]}
                        for i, item in enumerate(view["inputs"])
                    ],
                },
                {
                    "kind": "PROJECTION",
                    "horizon": view["horizon"],
                    "uncertainty": view["validation_history"]["uncertainty_method"],
                    "values": view["projections"],
                },
            ],
            "approved_targets_changed": False,
        }

    def request_adoption(self, identity, tenant, scenario, version):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "request_ai_forecast_adoption", hidden=True)
            row = self._row(c, tenant, scenario, version)
            self._recheck(c, ctx, row)
            if row["status"] != "PROJECTION":
                raise DomainError("CONFLICT_OPERATION", 409, reason="EXPLORATORY_FORECAST_NOT_ADOPTABLE")
            c.execute(
                "INSERT INTO impact.ai_forecast_adoption_review(tenant_id,review_id,scenario_id,version,requester_id,state,requested_at) "
                "VALUES(%s,%s,%s,%s,%s,'PENDING',statement_timestamp()) ON CONFLICT(tenant_id,scenario_id,version) "
                "DO NOTHING",
                (tenant, str(uuid4()), scenario, version, ctx.principal_id),
            )
            review = c.execute(
                "SELECT * FROM impact.ai_forecast_adoption_review WHERE tenant_id=%s AND scenario_id=%s AND version=%s",
                (tenant, scenario, version),
            ).fetchone()
            return {"review_id": str(review["review_id"]), "state": review["state"], "targets_changed": False}

    @staticmethod
    def _row(c, tenant, scenario, version=None):
        row = c.execute(
            "SELECT * FROM impact.ai_forecast_scenario WHERE tenant_id=%s AND scenario_id=%s "
            + ("AND version=%s" if version is not None else "ORDER BY version DESC LIMIT 1"),
            (tenant, scenario, version) if version is not None else (tenant, scenario),
        ).fetchone()
        if not row:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return row

    @staticmethod
    def _recheck(c, ctx, row):
        for source in c.execute(
            "SELECT object_id,revision_id FROM impact.ai_forecast_input WHERE tenant_id=%s AND scenario_id=%s AND version=%s",
            (ctx.tenant_id, row["scenario_id"], row["version"]),
        ).fetchall():
            load(c, ctx, source["object_id"], "CalculatedResult", "calculated-results.read")
            exact = c.execute(
                "SELECT 1 FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s AND revision_id=%s "
                "AND object_type='CalculatedResult' AND restriction_state='AVAILABLE'",
                (ctx.tenant_id, source["object_id"], source["revision_id"]),
            ).fetchone()
            if not exact:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)

    @staticmethod
    def _view(c, row):
        inputs = c.execute(
            "SELECT i.ordinal,i.object_id,i.revision_id,r.payload->>'value' AS value "
            "FROM impact.ai_forecast_input i JOIN impact.object_revision r ON r.tenant_id=i.tenant_id "
            "AND r.object_id=i.object_id AND r.revision_id=i.revision_id WHERE i.tenant_id=%s "
            "AND i.scenario_id=%s AND i.version=%s ORDER BY i.ordinal",
            (row["tenant_id"], row["scenario_id"], row["version"]),
        ).fetchall()
        return {
            "scenario_id": str(row["scenario_id"]),
            "version": row["version"],
            "label": row["label"],
            "status": row["status"],
            "horizon": row["horizon"],
            "method": row["method"],
            "assumptions": row["assumptions"],
            "validation_history": row["validation_history"],
            "unit": row["unit"],
            "inputs": [
                {
                    "ordinal": x["ordinal"],
                    "object_id": str(x["object_id"]),
                    "revision_id": str(x["revision_id"]),
                    "value": x["value"],
                }
                for x in inputs
            ],
            "projections": row["projections"],
            "can_request_adoption": row["status"] == "PROJECTION",
            "targets_changed": False,
            "created_at": row["created_at"].isoformat(),
        }
