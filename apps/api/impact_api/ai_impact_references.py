"""Deliberate AI-plan evidence links; official arithmetic remains in the governed core.

An impact reference pins a programme, indicator, definition and period revision and, when one
exists, the exact locked programme-period snapshot. Ordinary plan edits cannot refresh it. This
module copies no numeric evidence into a plan and makes no causal claim about an AI pilot.
"""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID

from psycopg.types.json import Jsonb

from . import ai_content_archives
from .dashboards import Dashboards, STALE_RULE
from .domain import DomainError, aware
from .service import revision
from .store import audit, authorize, context, hash_data, load, write

KIND = "AIAdoptionPlan"
READ_CAP = "ai.enablement.read"
SAVE_OPERATION = "set_ai_impact_reference"
READ_OPERATION = "get_ai_impact_reference_result"
REFERENCE_VERSION = "nonprofit-ai-impact-reference-v1"
INPUT_FIELDS = {"programme_id", "indicator_id", "period_id", "interpretation_note"}
CORE_PINS = (
    ("programme", "Programme", "programmes.read"),
    ("indicator", "IndicatorInstance", "indicator-instances.read"),
    ("definition", "IndicatorDefinition", "indicator-definitions.read"),
    ("period", "Period", "periods.read"),
    ("calendar", "ReportingCalendar", "reporting-calendars.read"),
)
REFERENCE_FIELDS = {
    "schema_version",
    "interpretation_note",
    "snapshot_id",
    "snapshot_revision",
    "snapshot_version",
    *(name + suffix for name, _, _ in CORE_PINS for suffix in ("_id", "_revision")),
}
DISCLAIMER = (
    "This is a reference to governed programme evidence. Official results come only from the "
    "pinned locked snapshot; provisional results are shown separately. The link and your pilot "
    "notes do not establish that AI caused an impact result. Refresh deliberately to change pins."
)


def _invalid(reason="AI_IMPACT_REFERENCE_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    if not isinstance(value, str):
        _invalid()
    try:
        return str(UUID(value))
    except (ValueError, AttributeError):
        _invalid()


def validate_input(data):
    if data is None:
        return
    if not isinstance(data, dict) or set(data) != INPUT_FIELDS:
        _invalid()
    for name in ("programme_id", "indicator_id", "period_id"):
        _uuid(data[name])
    if not isinstance(data["interpretation_note"], str) or len(data["interpretation_note"]) > 1000:
        _invalid()


def _request(body):
    if not isinstance(body, dict) or set(body) != {"operation_id", "expected_revision", "data"}:
        _invalid()
    _uuid(body["operation_id"])
    _uuid(body["expected_revision"])
    validate_input(body["data"])


def _stored(reference):
    """A malformed server pin is unreadable; it is never reinterpreted as current evidence."""
    try:
        if not isinstance(reference, dict) or set(reference) != REFERENCE_FIELDS:
            _invalid()
        if reference["schema_version"] != REFERENCE_VERSION:
            _invalid()
        validate_input({name: reference[name] for name in INPUT_FIELDS})
        for name, _, _ in CORE_PINS:
            _uuid(reference[name + "_id"])
            _uuid(reference[name + "_revision"])
        snapshot = reference["snapshot_id"]
        if snapshot is None:
            if reference["snapshot_revision"] is not None or reference["snapshot_version"] is not None:
                _invalid()
        else:
            _uuid(snapshot)
            _uuid(reference["snapshot_revision"])
            if type(reference["snapshot_version"]) is not int or reference["snapshot_version"] < 1:
                _invalid()
    except DomainError:
        # A malformed private link cannot prove current core authority. Keep its outcome
        # identical to an absent/hidden reference, without logging private selectors.
        raise DomainError("RESOURCE_UNAVAILABLE", 404) from None


def _relationships(rows):
    def same_uuid(left, right):
        try:
            return UUID(str(left)) == UUID(str(right))
        except (ValueError, AttributeError):
            return False

    programme, indicator, period, calendar = (
        rows[name] for name in ("programme", "indicator", "period", "calendar")
    )
    if not same_uuid(indicator["payload"].get("programme_id"), programme["object_id"]):
        _invalid("INDICATOR_NOT_IN_PROGRAMME")
    if not same_uuid(programme["payload"].get("reporting_calendar_id"), calendar["object_id"]):
        _invalid("PERIOD_NOT_IN_PROGRAMME_CALENDAR")
    if not same_uuid(indicator["payload"].get("definition_version"), rows["definition"]["revision_id"]):
        _invalid("INDICATOR_DEFINITION_MISMATCH")
    if not same_uuid(period["payload"].get("calendar_version"), calendar["revision_id"]):
        _invalid("PERIOD_NOT_IN_PROGRAMME_CALENDAR")
    start, end = aware(period["payload"].get("starts_at")), aware(period["payload"].get("ends_at"))
    programme_start = aware(programme["payload"].get("starts_at"))
    programme_end = aware(programme["payload"].get("ends_at"))
    if start < programme_start or end > programme_end or start >= end:
        _invalid("PERIOD_OUTSIDE_PROGRAMME")


def _inherit_guidance(c, ctx, previous, receipt):
    """Bind only actual verified prior guidance; a relationship edit cannot invent old wording."""
    archive = ai_content_archives._bound(c, ctx.tenant_id, previous["object_id"], previous["head_revision"])
    if archive is None:
        return
    ai_content_archives._verified(archive)
    c.execute(
        "INSERT INTO impact.ai_plan_content_binding(tenant_id,object_id,revision_id,snapshot_id) "
        "VALUES(%s,%s,%s,%s)",
        (ctx.tenant_id, receipt["object_id"], receipt["revision_id"], archive["snapshot_id"]),
    )


class AIImpactReferences:
    def __init__(self, service, dashboards=None):
        self.service = service
        self.dashboards = dashboards if dashboards is not None else Dashboards(service)

    def _latest_snapshot(self, c, ctx, programme_id, period_id):
        row = c.execute(
            "SELECT b.snapshot_id,b.snapshot_revision,b.snapshot_version,b.close_revision,b.created_at,v.payload "
            "FROM impact.period_snapshot_binding b JOIN impact.object_revision v "
            "ON v.tenant_id=b.tenant_id AND v.revision_id=b.snapshot_revision "
            "WHERE b.tenant_id=%s AND b.programme_id=%s AND b.period_id=%s "
            "AND v.restriction_state='AVAILABLE' ORDER BY b.snapshot_version DESC LIMIT 1",
            (ctx.tenant_id, programme_id, period_id),
        ).fetchone()
        if row:
            load(c, ctx, row["snapshot_id"], "Snapshot", "snapshots.read")
        return row

    def _current_pins(self, c, ctx, data):
        rows = {
            name: dict(load(c, ctx, data[name + "_id"], kind, capability))
            for name, kind, capability in CORE_PINS
            if name in {"programme", "indicator", "period"}
        }
        for name in rows:
            rows[name]["revision_id"] = rows[name]["head_revision"]
        rows["definition"] = revision(
            c,
            ctx,
            rows["indicator"]["payload"].get("definition_version"),
            "IndicatorDefinition",
            "indicator-definitions.read",
        )
        rows["calendar"] = revision(
            c,
            ctx,
            rows["period"]["payload"].get("calendar_version"),
            "ReportingCalendar",
            "reporting-calendars.read",
        )
        _relationships(rows)
        authorize(c, ctx, "programme_dashboard", data["programme_id"], hidden=True)
        snapshot = self._latest_snapshot(c, ctx, data["programme_id"], data["period_id"])
        return {
            "schema_version": REFERENCE_VERSION,
            **{
                name + suffix: str(row["object_id" if suffix == "_id" else "revision_id"])
                for name, row in rows.items()
                for suffix in ("_id", "_revision")
            },
            "snapshot_id": str(snapshot["snapshot_id"]) if snapshot else None,
            "snapshot_revision": str(snapshot["snapshot_revision"]) if snapshot else None,
            "snapshot_version": snapshot["snapshot_version"] if snapshot else None,
            "interpretation_note": data["interpretation_note"],
        }

    def save(self, identity, tenant, object_id, body, correlation):
        _uuid(object_id)
        _request(body)
        fingerprint = hash_data([SAVE_OPERATION, object_id, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, SAVE_OPERATION, object_id, hidden=True)
            authorize(c, ctx, "get_ai_adoption_plan", object_id, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, SAVE_OPERATION, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                load(c, ctx, old["outcome"]["object_id"], KIND, READ_CAP)
                authorize(c, ctx, SAVE_OPERATION, old["outcome"]["object_id"], hidden=True)
                return old["outcome"]
            previous = load(c, ctx, object_id, KIND, READ_CAP, lock=True)
            if str(previous["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if previous["lifecycle_state"] != "Draft":
                raise DomainError("STATE_TRANSITION_DENIED", 409)
            reference = self._current_pins(c, ctx, body["data"]) if body["data"] is not None else None
            payload = {**deepcopy(previous["payload"]), "impact_reference": reference}
            receipt = write(c, ctx, KIND, payload, "Draft", previous=previous)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            _inherit_guidance(c, ctx, previous, receipt)
            audit(c, ctx, SAVE_OPERATION, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    SAVE_OPERATION,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt

    def _pinned_rows(self, c, ctx, reference):
        rows, statuses = {}, {}
        for name, kind, capability in CORE_PINS:
            row = revision(c, ctx, reference[name + "_revision"], kind, capability)
            if str(row["object_id"]) != reference[name + "_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            current = load(c, ctx, row["object_id"], kind, capability)
            statuses[name] = (
                "CURRENT" if str(current["head_revision"]) == reference[name + "_revision"] else "CHANGED"
            )
            rows[name] = {**row, "lifecycle_state": current["lifecycle_state"]}
        try:
            _relationships(rows)
        except DomainError:
            raise DomainError("RESOURCE_UNAVAILABLE", 404) from None
        return rows, statuses

    def _pinned_snapshot(self, c, ctx, reference):
        if reference["snapshot_id"] is None:
            return None
        load(c, ctx, reference["snapshot_id"], "Snapshot", "snapshots.read")
        row = c.execute(
            "SELECT b.snapshot_id,b.snapshot_revision,b.snapshot_version,b.close_revision,b.created_at,v.payload "
            "FROM impact.period_snapshot_binding b JOIN impact.object_revision v "
            "ON v.tenant_id=b.tenant_id AND v.revision_id=b.snapshot_revision "
            "WHERE b.tenant_id=%s AND b.programme_id=%s AND b.period_id=%s "
            "AND b.snapshot_id=%s AND b.snapshot_revision=%s AND b.snapshot_version=%s "
            "AND v.restriction_state='AVAILABLE'",
            (
                ctx.tenant_id,
                reference["programme_id"],
                reference["period_id"],
                reference["snapshot_id"],
                reference["snapshot_revision"],
                reference["snapshot_version"],
            ),
        ).fetchone()
        if not row:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return row

    def result(self, identity, tenant, object_id):
        _uuid(object_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, READ_OPERATION, object_id, hidden=True)
            plan = load(c, ctx, object_id, KIND, READ_CAP)
            if not any(
                grant["capability"] == "dashboards.read" and grant["purpose"] is None for grant in ctx.grants
            ):
                # Apply the same capability gate even to an empty reference. A plan-only
                # reader must not distinguish an absent link from a hidden linked record.
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            reference = plan["payload"].get("impact_reference")
            if reference is None:
                # Absence and a hidden linked object share the exact opaque outcome, even
                # for readers whose dashboard grant covers a different programme.
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            _stored(reference)
            rows, statuses = self._pinned_rows(c, ctx, reference)
            authorize(c, ctx, "programme_dashboard", reference["programme_id"], hidden=True)
            snapshot = self._pinned_snapshot(c, ctx, reference)
            latest = self._latest_snapshot(c, ctx, reference["programme_id"], reference["period_id"])
            statuses["snapshot"] = (
                "ABSENT"
                if not snapshot and not latest
                else "CURRENT"
                if snapshot and latest and snapshot["snapshot_id"] == latest["snapshot_id"]
                else "CHANGED"
            )
            definition = rows["definition"]["payload"]
            cell = self.dashboards.cell(
                c,
                ctx,
                reference["programme_id"],
                reference["indicator_id"],
                reference["definition_revision"],
                definition,
                rows["period"],
                snapshot,
                detail=True,
            )
            for name in ("official", "provisional"):
                if cell[name] is not None:
                    load(c, ctx, cell[name]["result_id"], "CalculatedResult", "calculated-results.read")
            for name in ("target", "baseline"):
                if cell[name] is not None:
                    load(c, ctx, cell[name]["target_id"], "Target", "targets.read")
            if cell["coverage"].get("plan_revision") is not None:
                revision(c, ctx, cell["coverage"]["plan_revision"], "CollectionPlan", "collection-plans.read")
            state = self.service.periods.state(c, ctx, reference["programme_id"], reference["period_id"])
            return {
                "object_id": object_id,
                "revision_id": str(plan["head_revision"]),
                "status": "LINKED",
                "reference": deepcopy(reference),
                "reference_status": statuses,
                "programme_title": rows["programme"]["payload"].get("title")
                or rows["programme"]["payload"].get("code"),
                "period": self.dashboards.period_head(rows["period"], state),
                "indicator": {
                    **self.dashboards.indicator_head(rows["indicator"], definition),
                    **cell,
                },
                "stale_rule": STALE_RULE,
                "disclaimer": DISCLAIMER,
            }
