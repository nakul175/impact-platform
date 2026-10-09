"""Opportunity ranking with the organisation's own weights (US-MP-03, migration 0042).

Each editorial use case that `assess()` recommends for a brief gets four scores on the 1-5 scale of
`ai_opportunity_scores`: impact, effort and cost (editorial) and readiness (computed here from the
capacity gaps `assess()` found). Each score becomes 0-100 points with "higher is better":

    impact, readiness: (score - 1) x 25        effort, cost: (5 - score) x 25   (reverse-scored)

The weighted total is sum(weight x points) / 100 with integer weights 0-100 that add up to 100, so
it lies between 0 and 100 and is exact at two decimal places. It is computed with integers and
Decimal (no floating point) and returned as a decimal string. Opportunities are listed by
descending total; equal totals are ordered by use-case ID. A use case without all three editorial
scores is never ranked and is returned under `unranked` ("Not ranked: scores incomplete").

The weights are the tenant's single `AIRankingWeights` registry object; each change is its next
immutable revision with audit event, outbox intent and operation receipt in one transaction under
the tenant write lock. Changing weights is a preference, not an approval: it needs
`ai.enablement.manage` and `expected_revision`, no independent review and no fresh sign-in. Until
weights are saved the defaults 25/25/25/25 apply and no revision exists. Every ranking names the
weights and the revision (or DEFAULT) that produced it.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from uuid import UUID

from psycopg.types.json import Jsonb

from .ai_enablement_contracts import WEIGHT_FIELDS as CRITERIA_IN_ORDER
from .ai_enablement_catalog import (
    CONTENT_VERSION,
    SENSITIVE_DATA_GAP,
    SMALL_TEAM_GAP,
    assess,
    catalog,
    validate_profile,
)
from .ai_opportunity_scores import (
    CRITERIA,
    MAXIMUM,
    MINIMUM,
    SCORE_VERSION,
    STATUS,
    scores,
    validate_table,
)
from .domain import PRECISION, DomainError, display
from .store import audit, authorize, context, hash_data, write

KIND = "AIRankingWeights"
OPERATION = "update_ai_ranking_weights"
READ_OPERATION = "get_ai_ranking_weights"
RANK_OPERATION = "rank_ai_opportunities"
AUDIT_ACTION = "ai_ranking_weights.changed"
METHOD = "WEIGHTED_EDITORIAL_SCORES"
WEIGHT_FIELDS = tuple(CRITERIA_IN_ORDER)
DEFAULT_WEIGHTS = {"impact": 25, "effort": 25, "cost": 25, "readiness": 25}
WEIGHT_TOTAL = 100
REVERSED = frozenset({"effort", "cost"})
POINTS_PER_STEP = 25  # 4 steps between 1 and 5 make 0-100 points


def _invalid(reason="AI_RANKING_WEIGHTS_INVALID", message=None):
    raise DomainError("VALIDATION_FAILED", message=message, reason=reason)


def validate_weights(data):
    """Closed {impact, effort, cost, readiness}: integers 0-100 that add up to 100.

    Returns the weights in canonical order; raises 422 VALIDATION_FAILED otherwise. Booleans and
    numbers with a fraction (including 25.0, which JSON Schema accepts as an integer) are refused."""
    if not isinstance(data, dict) or set(data) != set(WEIGHT_FIELDS):
        _invalid()
    for field in WEIGHT_FIELDS:
        value = data[field]
        if type(value) is not int or not 0 <= value <= WEIGHT_TOTAL:
            _invalid(message="Each weight is a whole number from 0 to 100.")
    total = sum(data[field] for field in WEIGHT_FIELDS)
    if total != WEIGHT_TOTAL:
        _invalid(
            "AI_RANKING_WEIGHTS_TOTAL",
            "The four weights must add up to 100; these add up to " + str(total) + ".",
        )
    return {field: data[field] for field in WEIGHT_FIELDS}


def readiness(recommendation, kind, organisation_gaps):
    """Readiness 1-5 from the gaps assess() found: 5 minus one for each of the use case's own
    capacity gaps (no AI practice for an AI example; data organisation below what the example
    needs), one for the small-team gap and, for AI-assisted examples, one for the sensitive-data
    review gap. At most four gaps apply, so the score never falls below 1.

    Returns (score, the gaps that lowered it)."""
    gaps = list(recommendation["capacity_gaps"])
    if SMALL_TEAM_GAP in organisation_gaps:
        gaps.append(SMALL_TEAM_GAP)
    if kind == "AI_ASSISTED" and SENSITIVE_DATA_GAP in organisation_gaps:
        gaps.append(SENSITIVE_DATA_GAP)
    score = MAXIMUM - len(gaps)
    if not MINIMUM <= score <= MAXIMUM:
        raise ValueError("Readiness is outside the 1-5 scale.")
    return score, gaps


def points(criterion, score):
    """0-100 points, higher is better; effort and cost count in reverse."""
    if criterion not in WEIGHT_FIELDS or type(score) is not int or not MINIMUM <= score <= MAXIMUM:
        raise ValueError("Scores are integers from 1 to 5.")
    steps = MAXIMUM - score if criterion in REVERSED else score - MINIMUM
    return steps * POINTS_PER_STEP


def weighted_total(score_set, weights):
    """(exact integer numerator over 100, decimal string with two places).

    sum(weight x points) is an integer, so dividing by 100 is exact at two places; the display
    helper rounds half-up once and the assertion proves nothing was rounded."""
    numerator = sum(weights[field] * points(field, score_set[field]) for field in WEIGHT_FIELDS)
    with localcontext() as c:
        c.prec = PRECISION
        total = Decimal(numerator) / Decimal(WEIGHT_TOTAL)
        shown = display(total, 2)
        if Decimal(shown) * WEIGHT_TOTAL != numerator:
            raise ValueError("The weighted total is not exact at two places.")
    return numerator, shown


def rank(profile, weights, table=None):
    """Rank the use cases assess() recommends for `profile`. Pure and deterministic.

    Raises ValueError for an invalid profile (assess) or score table."""
    weights = validate_weights(weights)
    table = scores() if table is None else validate_table(table)
    assessment = assess(profile)
    kinds = {case["id"]: case["kind"] for case in catalog()["use_cases"]}
    ranked, unranked = [], []
    for recommendation in assessment["recommendations"]:
        use_case = recommendation["use_case_id"]
        editorial = table.get(use_case) or {}
        missing = [criterion for criterion in CRITERIA if criterion not in editorial]
        if missing:
            unranked.append({"use_case_id": use_case, "missing_scores": missing})
            continue
        score, gaps = readiness(recommendation, kinds[use_case], assessment["capacity_gaps"])
        score_set = {criterion: editorial[criterion] for criterion in CRITERIA}
        score_set["readiness"] = score
        numerator, total = weighted_total(score_set, weights)
        ranked.append(
            (
                (-numerator, use_case),
                {
                    "use_case_id": use_case,
                    "scores": score_set,
                    "weighted_total": total,
                    "readiness_gaps": gaps,
                },
            )
        )
    ranked.sort(key=lambda pair: pair[0])
    return {
        "items": [{"rank": position, **item} for position, (_, item) in enumerate(ranked, 1)],
        "unranked": sorted(unranked, key=lambda item: item["use_case_id"]),
    }


def _request(body):
    if not isinstance(body, dict) or set(body) != {"operation_id", "expected_revision", "data"}:
        _invalid()
    for field, nullable in (("operation_id", False), ("expected_revision", True)):
        value = body[field]
        if value is None and nullable:
            continue
        if not isinstance(value, str):
            _invalid()
        try:
            UUID(value)
        except ValueError:
            _invalid()


def _iso(value):
    return value.isoformat() if value else None


class AIRanking:
    """GET/PUT .../ai-enablement/ranking-weights and POST .../ai-enablement/ranking."""

    def __init__(self, service, table=None):
        # `table` replaces the editorial scores (qualification only); None reads the current table.
        self.service, self.table = service, table

    @staticmethod
    def _current(c, tenant, lock=False):
        return c.execute(
            "SELECT r.object_id,r.head_revision,r.lifecycle_state,r.classification,v.payload,"
            "v.revision_number,v.author_id,v.created_at AS saved_at,v.restriction_state "
            "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
            "AND v.object_id=r.object_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_type=%s" + (" FOR UPDATE OF r" if lock else ""),
            (tenant, KIND),
        ).fetchone()

    @staticmethod
    def _view(row):
        if row is None:
            return {
                "source": "DEFAULT",
                "revision_id": None,
                "weights": dict(DEFAULT_WEIGHTS),
                "saved_at": None,
                "saved_by": None,
            }
        try:
            if row["restriction_state"] != "AVAILABLE":
                raise DomainError("VALIDATION_FAILED")
            weights = validate_weights(row["payload"])
        except DomainError:
            # Never rank with weights that cannot be read exactly as saved (fail closed).
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_RANKING_WEIGHTS_UNREADABLE") from None
        return {
            "source": "SAVED",
            "revision_id": str(row["head_revision"]),
            "weights": weights,
            "saved_at": _iso(row["saved_at"]),
            "saved_by": str(row["author_id"]),
        }

    def get(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, READ_OPERATION, hidden=True)
            return self._view(self._current(c, tenant))

    def rank(self, identity, tenant, profile):
        try:
            # The closed six-field brief, checked before any database work.
            validate_profile(profile)
        except ValueError:
            raise DomainError("VALIDATION_FAILED", reason="AI_PROFILE_INVALID") from None
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, RANK_OPERATION, hidden=True)
            view = self._view(self._current(c, tenant))
        result = rank(profile, view["weights"], self.table)
        return {
            "method": METHOD,
            "content_version": CONTENT_VERSION,
            "score_version": SCORE_VERSION,
            "score_status": STATUS,
            "weights": view["weights"],
            "weights_source": view["source"],
            "weights_revision_id": view["revision_id"],
            **result,
        }

    def save(self, identity, tenant, body, correlation):
        _request(body)
        weights = validate_weights(body["data"])
        fingerprint = hash_data([OPERATION, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            # Tenant write lock before resolving authority (rule 17).
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, READ_OPERATION, hidden=True)
            authorize(c, ctx, OPERATION)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, OPERATION, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            previous = self._current(c, tenant, lock=True)
            current = str(previous["head_revision"]) if previous else None
            expected = str(UUID(body["expected_revision"])) if body["expected_revision"] else None
            if expected != current:
                raise DomainError(
                    "CONFLICT_VERSION",
                    409,
                    message="The ranking weights changed since you opened them. Reload them and try again.",
                    reason="AI_RANKING_WEIGHTS_CHANGED",
                )
            receipt = write(c, ctx, KIND, weights, "Active", previous=previous)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, AUDIT_ACTION, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    OPERATION,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt
