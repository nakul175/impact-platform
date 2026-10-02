"""Tenant reference data through governed tenant-administration commands (v0.26a, gap A1).

Called by Administration.command inside its transaction: the tenant advisory lock is held, the
caller holds `reference-data.manage` at TENANT scope with a purpose-less grant and authenticated
within 300 seconds, the receipt was checked and `expected_revision` matched. Each command writes
Active records (calendar, its Open periods, a single-stage independent workflow template, a report
template, a geography). The command returns its primary receipt and appends every further record it
wrote to `created`; Administration.command audits each of those, and Administration.record writes the
primary receipt's audit event, outbox event, stated reason and operation receipt, all in the same
transaction.
"""

from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .domain import DomainError, unavailable
from .reference_contracts import DEFAULTS
from .store import write

MONTHS = {"MONTHLY": 1, "QUARTERLY": 3, "ANNUAL": 12}
# Bounds the years one calendar can cover (240 monthly periods at most).
MAX_YEARS = 20
GEOGRAPHY_CODE = (
    "SELECT 1 FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
    "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type='Geography' "
    "AND r.lifecycle_state='Active' AND upper(v.payload->>'code')=upper(%s)"
)


def zone_of(name):
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        raise DomainError("VALIDATION_FAILED", reason="INVALID_TIME_ZONE") from None


def period_code(frequency, year, month):
    if frequency == "ANNUAL":
        return str(year)
    if frequency == "QUARTERLY":
        return str(year) + "-Q" + str((month - 1) // 3 + 1)
    return str(year) + "-" + str(month).zfill(2)


def periods(frequency, zone, first_year, years):
    """Contiguous, non-overlapping periods: local midnight of the first day of each period in the
    reporting zone, as UTC instants with an exclusive end."""
    tz = zone_of(zone)
    step = MONTHS[frequency]
    for year in range(first_year, first_year + years):
        for month in range(1, 13, step):
            start = datetime(year, month, 1, tzinfo=tz)
            following = month + step
            end = datetime(year + (following - 1) // 12, (following - 1) % 12 + 1, 1, tzinfo=tz)
            yield (
                period_code(frequency, year, month),
                start.astimezone(timezone.utc).isoformat(),
                end.astimezone(timezone.utc).isoformat(),
            )


def default_id(tenant, name):
    return str(uuid5(NAMESPACE_URL, "impact-reference-default-v1:" + str(tenant) + ":" + name))


class ReferenceData:
    def __init__(self, administration):
        self.a = administration

    def tenant_zone(self, c, ctx):
        row = c.execute(
            "SELECT v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type='Tenant' ORDER BY r.created_at LIMIT 1",
            (ctx.tenant_id,),
        ).fetchone()
        return ((row and row["payload"]) or {}).get("reporting_zone") or "UTC"

    def command(self, c, ctx, route, previous, action, data, created):
        if route == "reporting-calendars" and action is None:
            return self.calendar(
                c,
                ctx,
                created,
                data["title"],
                data["frequency"],
                data["zone"],
                data["first_year"],
                data["years"],
            )
        if route == "reporting-calendars":
            return self.extend(c, ctx, created, previous, data["years"])
        if route == "workflow-templates":
            return self.workflow_template(c, ctx, data["title"])
        if route == "report-templates":
            return self.report_template(c, ctx, data["title"], data["language"], data["sections"])
        if route == "geographies":
            return self.geography(c, ctx, data["title"], data["code"])
        if route == "reference-defaults":
            return self.defaults(c, ctx, created)
        unavailable()

    def calendar(self, c, ctx, created, title, frequency, zone, first_year, years, object_id=None):
        zone_of(zone)
        payload = {
            "title": title.strip(),
            "zone": zone,
            "frequency": frequency,
            "first_year": first_year,
            "last_year": first_year + years - 1,
        }
        receipt = write(
            c, ctx, "ReportingCalendar", payload, "Active", object_id=object_id, track_author=False
        )
        self.write_periods(c, ctx, created, receipt["revision_id"], frequency, zone, first_year, years)
        return receipt

    def write_periods(self, c, ctx, created, calendar_revision, frequency, zone, first_year, years):
        for code, starts, ends in periods(frequency, zone, first_year, years):
            created.append(
                write(
                    c,
                    ctx,
                    "Period",
                    {
                        "calendar_version": calendar_revision,
                        "code": code,
                        "starts_at": starts,
                        "ends_at": ends,
                        "reporting_zone": zone,
                    },
                    "Open",
                    track_author=False,
                )
            )

    def extend(self, c, ctx, created, calendar, years):
        if calendar["object_type"] != "ReportingCalendar":
            unavailable()
        if calendar["lifecycle_state"] != "Active":
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        payload = dict(calendar["payload"])
        # Calendars from the fixture or earlier builds carry only zone and frequency: their coverage
        # is unknown, so they are not extended here (create a new calendar instead).
        if (
            payload.get("frequency") not in MONTHS
            or not isinstance(payload.get("first_year"), int)
            or not isinstance(payload.get("last_year"), int)
        ):
            raise DomainError("VALIDATION_FAILED", reason="CALENDAR_NOT_EXTENSIBLE")
        start = payload["last_year"] + 1
        if start + years - payload["first_year"] > MAX_YEARS:
            raise DomainError("VALIDATION_FAILED", reason="CALENDAR_SPAN_LIMIT")
        payload["last_year"] = start + years - 1
        receipt = write(c, ctx, "ReportingCalendar", payload, "Active", calendar, track_author=False)
        self.write_periods(
            c, ctx, created, receipt["revision_id"], payload["frequency"], payload["zone"], start, years
        )
        return receipt

    def workflow_template(self, c, ctx, title, object_id=None):
        # The only review shape this build executes: one stage, one approval, independent of every
        # author (service.submit, period_governance.workflow, reporting.submit).
        return write(
            c,
            ctx,
            "WorkflowTemplate",
            {"title": title.strip(), "independent": True, "required_approvals": 1},
            "Active",
            object_id=object_id,
            track_author=False,
        )

    def report_template(self, c, ctx, title, language, sections, object_id=None):
        codes = [s["section_code"] for s in sections]
        if len(set(codes)) != len(codes):
            raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_SECTION_CODE")
        payload = {
            "title": title.strip(),
            "language": language,
            "sections": [
                {
                    **section,
                    "heading": section["heading"].strip(),
                    "required_binding_codes": [],
                    "caveat_codes": [],
                }
                for section in sections
            ],
            "numeric_bindings": [],
        }
        return write(c, ctx, "ReportTemplate", payload, "Active", object_id=object_id, track_author=False)

    def geography(self, c, ctx, title, code, object_id=None):
        if c.execute(GEOGRAPHY_CODE, (ctx.tenant_id, code)).fetchone():
            raise DomainError("CONFLICT_OPERATION", 409, reason="GEOGRAPHY_CODE_EXISTS")
        return write(
            c,
            ctx,
            "Geography",
            {"title": title.strip(), "code": code},
            "Active",
            object_id=object_id,
            track_author=False,
        )

    def defaults(self, c, ctx, created):
        calendar_id = default_id(ctx.tenant_id, "calendar")
        if c.execute(
            "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
            (ctx.tenant_id, calendar_id),
        ).fetchone():
            raise DomainError("CONFLICT_OPERATION", 409, reason="REFERENCE_DEFAULTS_APPLIED")
        zone = self.tenant_zone(c, ctx)
        year = datetime.now(zone_of(zone)).year
        spec = DEFAULTS["calendar"]
        receipt = self.calendar(
            c,
            ctx,
            created,
            spec["title"],
            spec["frequency"],
            zone,
            year,
            spec["years"],
            object_id=calendar_id,
        )
        created.append(
            self.workflow_template(
                c, ctx, DEFAULTS["workflow_template"]["title"], default_id(ctx.tenant_id, "workflow")
            )
        )
        report = DEFAULTS["report_template"]
        created.append(
            self.report_template(
                c,
                ctx,
                report["title"],
                report["language"],
                report["sections"],
                default_id(ctx.tenant_id, "report-template"),
            )
        )
        geography = DEFAULTS["geography"]
        if not c.execute(GEOGRAPHY_CODE, (ctx.tenant_id, geography["code"])).fetchone():
            created.append(
                self.geography(
                    c, ctx, geography["title"], geography["code"], default_id(ctx.tenant_id, "geography")
                )
            )
        return receipt
