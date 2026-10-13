"""Self-reported current outcomes compared only with an exact locked problem baseline."""

from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID

from psycopg.types.json import Jsonb

from .ai_opportunity_mapping import map_diagnosis
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write

KIND = "AICurrentOutcomeObservation"
BASELINE_KIND = "AIProblemBaseline"
PLAN_KIND = "AIAdoptionPlan"
READ_CAP = "ai.enablement.read"
METRICS = ("time", "cost", "quality", "reach", "usage")
MEASURE_FIELDS = {"value", "unit", "basis", "observed_from", "observed_to"}


def _invalid(reason="OUTCOME_OBSERVATION_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    try:
        canonical = str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        _invalid()
    if canonical != value:
        _invalid()
    return canonical


def _measure(value):
    if not isinstance(value, dict) or set(value) != MEASURE_FIELDS:
        _invalid()
    try:
        number = Decimal(value["value"])
    except (InvalidOperation, TypeError):
        _invalid()
    if not isinstance(value["value"], str) or not number.is_finite() or number.as_tuple().exponent < -12:
        _invalid()
    if len(number.as_tuple().digits) > 38:
        _invalid()
    if not isinstance(value["unit"], str) or not value["unit"].strip() or len(value["unit"]) > 80:
        _invalid()
    if not isinstance(value["basis"], str) or not value["basis"].strip() or len(value["basis"]) > 500:
        _invalid()
    try:
        start, end = date.fromisoformat(value["observed_from"]), date.fromisoformat(value["observed_to"])
    except (TypeError, ValueError):
        _invalid()
    if end < start:
        _invalid("OUTCOME_OBSERVATION_PERIOD_INVALID")
    if end > date.today():
        _invalid("OUTCOME_OBSERVATION_FUTURE_PERIOD")


class AIOutcomeObservations:
    def __init__(self, service, diagnoses, baselines):
        self.service, self.diagnoses, self.baselines = service, diagnoses, baselines

    def _resolve(self, c, identity, tenant, selectors):
        ctx = context(c, identity, tenant)
        authorize(c, ctx, "get_ai_outcome_dashboard", hidden=True)
        plan = load(c, ctx, selectors["plan_id"], PLAN_KIND, READ_CAP)
        if str(plan["head_revision"]) != selectors["plan_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="ADOPTION_PLAN_CHANGED")
        deployment = plan["payload"].get("training_deployment")
        if plan["lifecycle_state"] != "Completed" or not deployment:
            raise DomainError("STATE_TRANSITION_DENIED", 409, reason="DEPLOYED_SOLUTION_REQUIRED")
        if deployment["attestation_id"] != selectors["deployment_attestation_id"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="DEPLOYMENT_ATTESTATION_CHANGED")
        baseline = load(c, ctx, selectors["baseline_object_id"], BASELINE_KIND, "ai.problem-baseline.read")
        if str(baseline["head_revision"]) != selectors["baseline_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="LOCKED_BASELINE_CHANGED")
        payload = self.baselines.revision(
            c, tenant, selectors["baseline_object_id"], selectors["baseline_revision"]
        )
        if baseline["lifecycle_state"] != "Locked" or payload.get("baseline_state") != "Locked":
            raise DomainError("STATE_TRANSITION_DENIED", 409, reason="LOCKED_BASELINE_REQUIRED")
        self.baselines._source(c, identity, tenant, payload, False)
        diagnosis_payload = self.diagnoses.revision(
            c, tenant, payload["diagnosis_id"], payload["diagnosis_revision"]
        )
        mapping = map_diagnosis(
            {
                "object_id": payload["diagnosis_id"],
                "revision_id": payload["diagnosis_revision"],
                "business_state": "Completed",
                "data": diagnosis_payload,
            }
        )
        opportunities = next(
            (
                row["opportunities"]
                for row in mapping["problems"]
                if row["problem_id"] == payload["problem_id"]
            ),
            [],
        )
        opportunity = next(
            (item for item in opportunities if item["pattern_id"] == selectors["opportunity_id"]), None
        )
        if opportunity is None:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return plan, payload, deployment, mapping, opportunity

    @staticmethod
    def _validate(body):
        required = {
            "operation_id",
            "plan_id",
            "plan_revision",
            "deployment_attestation_id",
            "baseline_object_id",
            "baseline_revision",
            "opportunity_id",
            "metrics",
            "notes",
        }
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        for name in required - {"opportunity_id", "metrics", "notes"}:
            _uuid(body[name])
        if (
            not isinstance(body["opportunity_id"], str)
            or not body["opportunity_id"]
            or len(body["opportunity_id"]) > 100
        ):
            _invalid()
        if not isinstance(body["notes"], str) or len(body["notes"]) > 4000:
            _invalid()
        if not isinstance(body["metrics"], dict) or set(body["metrics"]) != set(METRICS):
            _invalid()
        for measure in body["metrics"].values():
            _measure(measure)
        windows = {(measure["observed_from"], measure["observed_to"]) for measure in body["metrics"].values()}
        if len(windows) != 1:
            _invalid("OUTCOME_OBSERVATION_WINDOW_MISMATCH")

    def create(self, identity, tenant, body, correlation):
        self._validate(body)
        fingerprint = hash_data(["create_ai_outcome_observation", body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_outcome_observation", hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, "create_ai_outcome_observation", body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                self._resolve(c, identity, tenant, old["outcome"]["selectors"])
                return old["outcome"]
            plan, baseline, deployment, mapping, opportunity = self._resolve(c, identity, tenant, body)
            payload = {
                "reporting_basis": "SELF_REPORTED",
                "plan_id": body["plan_id"],
                "plan_revision": body["plan_revision"],
                "deployment_attestation_id": body["deployment_attestation_id"],
                "deployed_solution_id": deployment["solution_id"],
                "baseline_object_id": body["baseline_object_id"],
                "baseline_revision": body["baseline_revision"],
                "diagnosis_id": baseline["diagnosis_id"],
                "diagnosis_revision": baseline["diagnosis_revision"],
                "problem_id": baseline["problem_id"],
                "opportunity_id": body["opportunity_id"],
                "pattern_edition": mapping["pattern_edition"],
                "mapping_rule_version": mapping["mapping_rule_version"],
                "opportunity_snapshot": {
                    "pattern_id": opportunity["pattern_id"],
                    "title": opportunity["title"],
                    "kind": opportunity["kind"],
                },
                "metrics": deepcopy(body["metrics"]),
                "notes": body["notes"].strip(),
                "recorded_by": str(ctx.principal_id),
                "recorded_at": now.isoformat(),
            }
            saved = write(c, ctx, KIND, payload, "Recorded")
            selectors = {
                name: body[name]
                for name in (
                    "plan_id",
                    "plan_revision",
                    "deployment_attestation_id",
                    "baseline_object_id",
                    "baseline_revision",
                    "opportunity_id",
                )
            }
            receipt = {
                **saved,
                "operation_id": body["operation_id"],
                "correlation_id": correlation,
                "selectors": selectors,
            }
            audit(c, ctx, "create_ai_outcome_observation", receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    "create_ai_outcome_observation",
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt

    def dashboard(self, identity, tenant, plan_id, baseline_object_id, opportunity_id):
        selectors = {
            "plan_id": _uuid(plan_id),
            "baseline_object_id": _uuid(baseline_object_id),
            "opportunity_id": opportunity_id,
        }
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            plan = load(c, ctx, selectors["plan_id"], PLAN_KIND, READ_CAP)
            baseline = load(
                c, ctx, selectors["baseline_object_id"], BASELINE_KIND, "ai.problem-baseline.read"
            )
            selectors.update(
                plan_revision=str(plan["head_revision"]),
                baseline_revision=str(baseline["head_revision"]),
                deployment_attestation_id=(plan["payload"].get("training_deployment") or {}).get(
                    "attestation_id", ""
                ),
            )
            _, baseline_payload, deployment, mapping, _ = self._resolve(c, identity, tenant, selectors)
            row = c.execute(
                "SELECT object_id,head_revision,payload FROM impact.object_registry r JOIN impact.object_revision v "
                "USING(tenant_id,object_id) WHERE r.tenant_id=%s AND r.object_type=%s "
                "AND v.revision_id=r.head_revision AND v.restriction_state='AVAILABLE' "
                "AND v.payload->>'plan_id'=%s AND v.payload->>'baseline_object_id'=%s "
                "AND v.payload->>'opportunity_id'=%s AND v.payload->>'plan_revision'=%s "
                "AND v.payload->>'deployment_attestation_id'=%s AND v.payload->>'baseline_revision'=%s "
                "AND v.payload->>'pattern_edition'=%s AND v.payload->>'mapping_rule_version'=%s "
                "ORDER BY v.payload->'metrics'->'usage'->>'observed_to' DESC,"
                "v.payload->>'recorded_at' DESC,r.object_id DESC LIMIT 1",
                (
                    tenant,
                    KIND,
                    plan_id,
                    baseline_object_id,
                    opportunity_id,
                    selectors["plan_revision"],
                    selectors["deployment_attestation_id"],
                    selectors["baseline_revision"],
                    mapping["pattern_edition"],
                    mapping["mapping_rule_version"],
                ),
            ).fetchone()
            comparisons = []
            for name in METRICS:
                base = baseline_payload["metrics"].get(name)
                current = row["payload"]["metrics"][name] if row else None
                status, delta = "NOT_RECORDED", None
                if base is None:
                    status = "BASELINE_NOT_RECORDED"
                elif current is not None and (
                    base["unit"] != current["unit"] or base["basis"] != current["basis"]
                ):
                    status = "INCOMPATIBLE"
                elif current is not None:
                    status = "COMPARABLE"
                    delta = str(Decimal(current["value"]) - Decimal(base["value"]))
                comparisons.append(
                    {"metric": name, "baseline": base, "current": current, "status": status, "delta": delta}
                )
            return {
                "plan_id": plan_id,
                "plan_revision": selectors["plan_revision"],
                "deployment_attestation_id": deployment["attestation_id"],
                "deployed_solution_id": deployment["solution_id"],
                "baseline_object_id": baseline_object_id,
                "baseline_revision": selectors["baseline_revision"],
                "opportunity_id": opportunity_id,
                "pattern_edition": mapping["pattern_edition"],
                "observation_id": str(row["object_id"]) if row else None,
                "observation_revision": str(row["head_revision"]) if row else None,
                "reporting_basis": "SELF_REPORTED",
                "comparisons": comparisons,
                "disclaimer": "Self-reported comparison only; it does not establish causality, realised ROI or independent verification.",
            }
