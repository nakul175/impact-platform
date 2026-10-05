"""Programme and indicator dashboards (v0.24): read-only views over official snapshots.

A programme dashboard shows, per indicator instance of one programme and one period, the OFFICIAL
value from the programme's own latest locked snapshot for that period, a clearly separated
PROVISIONAL value when one exists (no official value yet, or a calculation newer than the lock), the
approved target and baseline (pinned by the snapshot once the period is locked), status against the
target only where a target exists, coverage from the period's obligation set and a freshness block
with an explicit stale flag. An indicator series shows the same values across periods.

Numbers are the stored decimal strings; each displayed figure is rounded half-up once from the
stored value with the pinned definition's display places; nothing is summed from displayed values,
a blank stays blank and an UNDEFINED value is never shown as zero. Nothing is attributed through a
shared definition: a value counts only when its result was calculated under the definition revision
the instance pins and, for OFFICIAL, when it sits in a snapshot bound to this programme and period.

Reads only: no revision, audit or receipt is written. Capability `dashboards.read` gates the route;
every underlying record is still filtered by its own read capability.
"""

from datetime import datetime, timezone

from .domain import DomainError, decimal_value, display
from .measurement import coverage
from .planning import safe_progress
from .store import authorize, context, currently_readable, load, scopes, visible_sql

STALE_RULE = (
    "Stale when the source observations or the approved collection plan changed since the shown "
    "value was calculated or locked, when an approved amendment left a recalculation pending, or "
    "when a provisional calculation is newer than the locked official value. Unknown (null) when "
    "you cannot read every source observation of the period. A successful read never makes a "
    "value fresh."
)
MAX_SOURCES = 10000
COVERAGE_COUNTS = [
    "expected_count",
    "required_count",
    "received_count",
    "approved_count",
    "pending_count",
    "missing_count",
    "excluded_count",
    "excepted_count",
    "overdue_count",
]


def shown(value, places):
    """The display string of a stored decimal string, rounded half-up once; None stays None."""
    if value is None:
        return None
    try:
        return display(decimal_value(value), places)
    except DomainError:
        return None


def summarize(measured, source, reason=None):
    """The dashboard's coverage block: counts from one obligation set, never from membership. With
    no required obligation coverage is NOT_APPLICABLE: no percentage, never 100 % and never 0 %."""
    if measured is None:
        # No obligation set: nothing is expected (zero, not applicable). Withheld: counts unknown.
        return {
            "source": source,
            "plan_revision": None,
            **{k: None if reason else 0 for k in COVERAGE_COUNTS},
            "applicability": "UNAVAILABLE" if reason else "NOT_APPLICABLE",
            "approval_percent": None,
            "complete": False,
            "reason_code": reason or "NO_COLLECTION_PLAN",
        }
    required = measured.get("required_count", measured.get("expected_count", 0))
    applicable = required > 0
    return {
        "source": source,
        "plan_revision": measured.get("plan_revision"),
        **{k: measured.get(k, 0) for k in COVERAGE_COUNTS},
        "required_count": required,
        "applicability": "APPLICABLE" if applicable else "NOT_APPLICABLE",
        "approval_percent": measured.get("approval_percent") if applicable else None,
        "complete": bool(applicable and measured.get("complete")),
        "reason_code": None if applicable else "NO_REQUIRED_OBLIGATIONS",
    }


def value_block(row, places):
    """One result's value as the dashboard shows it, from the stored decimal only."""
    p = row["payload"]
    present = p.get("value_state") == "PRESENT" and p.get("value") is not None
    entries = []
    for e in p.get("disaggregation") or []:
        here = e.get("value_state") == "PRESENT" and e.get("value") is not None
        entries.append(
            {
                "dimension": e.get("dimension"),
                "dimension_version": e.get("dimension_version"),
                "category": e.get("category"),
                "additivity": e.get("additivity"),
                "contributor_count": e.get("contributor_count", 0),
                "value_state": e.get("value_state"),
                "value": e.get("value") if here else None,
                "displayed_value": shown(e.get("value"), places) if here else None,
                "reason_code": e.get("reason_code"),
            }
        )
    return {
        "mode": p.get("mode", "PROVISIONAL"),
        "result_id": str(row["result_id"]),
        "result_revision": str(row["result_revision"]),
        "value_state": p.get("value_state"),
        "value": p["value"] if present else None,
        "displayed_value": shown(p["value"], places) if present else None,
        "numerator": p.get("numerator"),
        "denominator": p.get("denominator"),
        "reason_code": p.get("reason_code"),
        "calculated_at": (p.get("freshness") or {}).get("calculated_at"),
        "disaggregation": entries,
    }


def target_block(view, places):
    if view is None:
        return None
    return {
        **{
            k: view.get(k)
            for k in [
                "target_id",
                "revision_id",
                "target_kind",
                "target_basis",
                "direction",
                "value_state",
                "value",
                "low",
                "high",
                "binding_version",
            ]
        },
        "displayed_value": shown(view.get("value"), places) if view.get("value_state") == "PRESENT" else None,
        "displayed_low": shown(view.get("low"), places),
        "displayed_high": shown(view.get("high"), places),
    }


def iso(value):
    return value.isoformat() if value else None


class Dashboards:
    def __init__(self, service):
        self.service = service

    # Entry -------------------------------------------------------------------------------------
    def read(self, identity, tenant, op, obj, limit=50, cursor=None, period_id=None):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            if not any(g["capability"] == "dashboards.read" and g["purpose"] is None for g in ctx.grants):
                raise DomainError("POLICY_DENIED", 403)
            authorize(c, ctx, op, obj, hidden=True)
            if not 1 <= limit <= 100:
                raise DomainError("VALIDATION_FAILED")
            if op in {"programme_dashboard", "indicator_dashboard_sources", "indicator_definition_portfolio"}:
                if not period_id:
                    raise DomainError(
                        "VALIDATION_FAILED", fields=[{"path": "period_id", "message": "Required."}]
                    )
            if op == "programme_dashboard":
                return self.programme(c, ctx, obj, period_id, limit, cursor)
            if op == "indicator_dashboard_sources":
                return self.drilldown(c, ctx, obj, period_id, limit, cursor)
            if op == "indicator_definition_portfolio":
                return self.portfolio(c, ctx, obj, period_id, limit, cursor)
            return self.series(c, ctx, obj, limit, cursor)

    # Shared lookups ----------------------------------------------------------------------------
    def snapshot(self, c, ctx, programme_id, period_id):
        """The latest locked snapshot bound to this programme and period, or None."""
        return c.execute(
            "SELECT b.snapshot_id,b.snapshot_version,b.close_revision,b.created_at,v.payload FROM impact.period_snapshot_binding b JOIN impact.object_revision v ON v.tenant_id=b.tenant_id AND v.revision_id=b.snapshot_revision WHERE b.tenant_id=%s AND b.programme_id=%s AND b.period_id=%s ORDER BY b.snapshot_version DESC LIMIT 1",
            (ctx.tenant_id, str(programme_id), str(period_id)),
        ).fetchone()

    def official(self, c, ctx, snapshot, indicator_id, pin):
        if not snapshot:
            return None
        row = c.execute(
            "SELECT o.result_id,o.result_revision,v.payload,b.source_digest,b.plan_revision FROM impact.official_result_snapshot o JOIN impact.object_revision v ON v.tenant_id=o.tenant_id AND v.revision_id=o.result_revision LEFT JOIN impact.result_binding b ON b.tenant_id=o.tenant_id AND b.result_id=o.result_id WHERE o.tenant_id=%s AND o.snapshot_id=%s AND o.indicator_id=%s AND v.restriction_state='AVAILABLE'",
            (ctx.tenant_id, str(snapshot["snapshot_id"]), indicator_id),
        ).fetchone()
        if (
            not row
            or row["payload"].get("indicator_version") != pin
            or not currently_readable(c, ctx, row["result_id"], "CalculatedResult", "calculated-results.read")
        ):
            return None
        return row

    def provisional(self, c, ctx, indicator_id, period_id, pin):
        row = c.execute(
            "SELECT b.result_id,r.head_revision AS result_revision,r.created_at,b.source_digest,b.plan_revision,v.payload FROM impact.result_binding b JOIN impact.object_registry r ON r.tenant_id=b.tenant_id AND r.object_id=b.result_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE b.tenant_id=%s AND b.indicator_id=%s AND b.period_id=%s AND r.lifecycle_state='Calculated' AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' ORDER BY r.created_at DESC,r.object_id DESC LIMIT 1",
            (ctx.tenant_id, indicator_id, str(period_id)),
        ).fetchone()
        if (
            not row
            or row["payload"].get("indicator_version") != pin
            or not scopes(c, ctx, "calculated-results.read", row["result_id"])
        ):
            return None
        return row

    def targets(self, c, ctx, indicator_id, period_id, snapshot):
        if snapshot:
            registers = c.execute(
                "SELECT * FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s AND target_revision=ANY(%s::uuid[])",
                (ctx.tenant_id, indicator_id, str(period_id), snapshot["payload"].get("target_versions", [])),
            ).fetchall()
        else:
            registers = c.execute(
                "SELECT DISTINCT ON (slot) * FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s ORDER BY slot,binding_version DESC",
                (ctx.tenant_id, indicator_id, str(period_id)),
            ).fetchall()
        views = self.service.planning.target_views(c, ctx, registers)
        return (
            views.get((indicator_id, str(period_id), "TARGET")),
            views.get((indicator_id, str(period_id), "BASELINE")),
        )

    def sources(self, c, ctx, indicator_id, period):
        """The period's source observations of one indicator when the reader may see every one of
        them, else None: a partial set would misstate coverage and freshness."""
        rows = c.execute(
            "SELECT r.object_id,r.head_revision,r.classification,r.updated_at,v.restriction_state,v.payload FROM impact.observation_current o JOIN impact.object_registry r ON r.tenant_id=o.tenant_id AND r.object_id=o.object_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE o.tenant_id=%s AND o.indicator_id=%s AND o.event_at>=%s AND o.event_at<%s ORDER BY r.object_id LIMIT %s",
            (ctx.tenant_id, indicator_id, period["starts_at"], period["ends_at"], MAX_SOURCES + 1),
        ).fetchall()
        if len(rows) > MAX_SOURCES:
            return None
        for row in rows:
            if (
                row["restriction_state"] != "AVAILABLE"
                or row["classification"] == "RESTRICTED"
                or not scopes(c, ctx, "observations.read", row["object_id"])
            ):
                return None
        return rows

    def plan(self, c, ctx, indicator_id, period_id):
        binding = c.execute(
            "SELECT * FROM impact.collection_plan_binding WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s",
            (ctx.tenant_id, indicator_id, str(period_id)),
        ).fetchone()
        if not binding:
            return None, None
        row = c.execute(
            "SELECT r.object_id,r.lifecycle_state,v.revision_id AS head_revision,v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=%s WHERE r.tenant_id=%s AND r.object_id=%s AND v.restriction_state='AVAILABLE' AND r.classification<>'RESTRICTED'",
            (binding["plan_revision"], ctx.tenant_id, binding["plan_id"]),
        ).fetchone()
        if not row or not scopes(c, ctx, "collection-plans.read", binding["plan_id"]):
            return binding, None
        return binding, row

    # One indicator in one period ---------------------------------------------------------------
    def cell(self, c, ctx, programme_id, indicator_id, pin, definition, period_row, snapshot, detail):
        period_id = str(period_row["object_id"])
        places = definition.get("display_decimals", 2)
        official = self.official(c, ctx, snapshot, indicator_id, pin)
        latest = self.provisional(c, ctx, indicator_id, period_id, pin)
        # A provisional value is shown beside an official one only when it is newer than the lock
        # (a restatement in progress); otherwise it is the very calculation the close promoted.
        provisional = (
            latest if latest and (not snapshot or latest["created_at"] > snapshot["created_at"]) else None
        )
        target, baseline = self.targets(c, ctx, indicator_id, period_id, snapshot)
        official_block = value_block(official, places) if official else None
        provisional_block = value_block(provisional, places) if provisional else None
        compared = official_block or provisional_block
        status = None
        if target is not None:
            actual = compared or {"mode": "NONE", "value_state": "MISSING", "value": None}
            status = {
                **{
                    k: v
                    for k, v in safe_progress(actual, target, baseline, places).items()
                    if k
                    in {"status", "attainment_percent", "deviation", "displayed_deviation", "reason_code"}
                },
                "compared_with": compared["mode"] if compared else None,
            }
        cell = {
            "official": official_block,
            "provisional": provisional_block,
            "target": target_block(target, places),
            "baseline": target_block(baseline, places),
            "status": status,
        }
        if not detail:
            return cell
        cell["coverage"] = self.coverage(c, ctx, indicator_id, definition, period_row, snapshot)
        cell["freshness"] = self.freshness(
            c, ctx, programme_id, indicator_id, period_row, snapshot, official, provisional, latest
        )
        return cell

    def coverage(self, c, ctx, indicator_id, definition, period_row, snapshot):
        if snapshot:
            close = c.execute(
                "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
                (ctx.tenant_id, str(snapshot["close_revision"])),
            ).fetchone()
            entry = next(
                (
                    e
                    for e in (close["payload"] if close else {}).get("entries", [])
                    if e["indicator_id"] == indicator_id
                ),
                None,
            )
            if not entry:
                return summarize(None, "CLOSE_SNAPSHOT")
            if not currently_readable(c, ctx, entry["plan_id"], "CollectionPlan", "collection-plans.read"):
                return summarize(None, "CLOSE_SNAPSHOT", "COVERAGE_ACCESS_REQUIRED")
            return summarize(entry["coverage"], "CLOSE_SNAPSHOT")
        binding, plan = self.plan(c, ctx, indicator_id, period_row["object_id"])
        if not binding:
            return summarize(None, "COLLECTION_PLAN")
        if not plan:
            return summarize(None, "COLLECTION_PLAN", "COVERAGE_ACCESS_REQUIRED")
        rows = self.sources(c, ctx, indicator_id, period_row["payload"])
        if rows is None:
            return summarize(None, "COLLECTION_PLAN", "SOURCE_ACCESS_REQUIRED")
        measured, _ = coverage(plan, rows, definition, datetime.now(timezone.utc))
        return summarize(measured, "COLLECTION_PLAN")

    def freshness(
        self, c, ctx, programme_id, indicator_id, period_row, snapshot, official, provisional, latest
    ):
        from .service import source_digest

        rows = self.sources(c, ctx, indicator_id, period_row["payload"])
        binding, _ = self.plan(c, ctx, indicator_id, period_row["object_id"])
        plan_revision = str(binding["plan_revision"]) if binding else None
        reasons = []

        def compare(row, sources_code, plan_code):
            if rows is not None and source_digest(rows) != row["source_digest"]:
                reasons.append(sources_code)
            if plan_revision != (str(row["plan_revision"]) if row["plan_revision"] else None):
                reasons.append(plan_code)

        if official:
            compare(official, "SOURCES_CHANGED_SINCE_CLOSE", "PLAN_CHANGED_SINCE_CLOSE")
        if provisional:
            compare(provisional, "SOURCES_CHANGED_SINCE_CALCULATION", "PLAN_CHANGED_SINCE_CALCULATION")
            if self.service.work.stale(c, ctx, provisional["result_revision"]):
                reasons.append("RECALCULATION_PENDING")
            if official:
                reasons.append("PROVISIONAL_NEWER_THAN_OFFICIAL")
        has_value = bool(official or provisional)
        if not has_value:
            stale, check = None, "NO_VALUE"
        elif rows is None:
            stale, check = (True if reasons else None), "NOT_PERMITTED"
        else:
            stale, check = bool(reasons), "CHECKED"
        last_change = max((r["updated_at"] for r in rows), default=None) if rows is not None else None
        return {
            "stale": stale,
            "stale_reasons": sorted(set(reasons)),
            "source_check": check,
            "snapshot_id": str(snapshot["snapshot_id"]) if snapshot else None,
            "snapshot_version": snapshot["snapshot_version"] if snapshot else None,
            "locked_at": iso(snapshot["created_at"]) if snapshot else None,
            "official_calculated_at": (official["payload"].get("freshness") or {}).get("calculated_at")
            if official
            else None,
            "provisional_calculated_at": (latest["payload"].get("freshness") or {}).get("calculated_at")
            if latest
            else None,
            "last_source_change_at": iso(last_change),
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def definition(self, c, ctx, pin):
        row = c.execute(
            "SELECT object_id,payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s AND object_type='IndicatorDefinition' AND restriction_state='AVAILABLE'",
            (ctx.tenant_id, pin),
        ).fetchone()
        if not row or not currently_readable(
            c, ctx, row["object_id"], "IndicatorDefinition", "indicator-definitions.read"
        ):
            return {}
        return row["payload"]

    @staticmethod
    def indicator_head(instance, definition):
        applicability = instance["payload"].get("local_applicability")
        return {
            "indicator_id": str(instance["object_id"]),
            "indicator_label": (definition.get("name") or "Indicator")
            + (" · " + applicability if applicability else ""),
            "definition_revision": instance["payload"].get("definition_version"),
            "unit": definition.get("unit"),
            "measurement_type": definition.get("measurement_type"),
            "combination_rule": definition.get("combination_rule"),
            "display_decimals": definition.get("display_decimals", 2),
            "lifecycle_state": instance.get("lifecycle_state"),
        }

    @staticmethod
    def period_head(period_row, state):
        p = period_row["payload"]
        return {
            "period_id": str(period_row["object_id"]),
            "period_code": p.get("code"),
            "starts_at": p.get("starts_at"),
            "ends_at": p.get("ends_at"),
            "period_state": state["lifecycle_state"],
        }

    # Programme dashboard -----------------------------------------------------------------------
    def programme(self, c, ctx, obj, period_id, limit, cursor):
        programme = load(c, ctx, obj, "Programme", "programmes.read")
        period = load(c, ctx, period_id, "Period", "periods.read")
        pid = str(programme["object_id"])
        bound = self.service.cursor_binding(ctx, "dashboards/programmes/" + pid + "?period=" + str(period_id))
        key = self.service.cursor_key(bound, cursor)
        state = self.service.periods.state(c, ctx, pid, str(period["object_id"]))
        snapshot = self.snapshot(c, ctx, pid, period["object_id"])
        predicate, args = visible_sql(ctx, "indicator-instances.read")
        instances = c.execute(
            "SELECT r.object_id,r.lifecycle_state,v.payload FROM impact.indicator_instance_current i JOIN impact.object_registry r ON r.tenant_id=i.tenant_id AND r.object_id=i.object_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE i.tenant_id=%s AND i.programme_id=%s AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' AND "
            + predicate
            + (" AND r.object_id>%s::uuid" if key else "")
            + " ORDER BY r.object_id LIMIT %s",
            [ctx.tenant_id, pid, *args, *([key[0]] if key else []), limit + 1],
        ).fetchall()
        more = len(instances) > limit
        instances = instances[:limit]
        cards = []
        for instance in instances:
            pin = instance["payload"].get("definition_version")
            definition = self.definition(c, ctx, pin)
            cards.append(
                {
                    **self.indicator_head(instance, definition),
                    **self.cell(
                        c,
                        ctx,
                        pid,
                        str(instance["object_id"]),
                        pin,
                        definition,
                        period,
                        snapshot,
                        detail=True,
                    ),
                }
            )
        return {
            "programme_id": pid,
            "programme_title": programme["payload"].get("title") or programme["payload"].get("code"),
            "period": self.period_head(period, state),
            "snapshot": {
                "snapshot_id": str(snapshot["snapshot_id"]),
                "snapshot_version": snapshot["snapshot_version"],
                "locked_at": iso(snapshot["created_at"]),
            }
            if snapshot
            else None,
            "stale_rule": STALE_RULE,
            "indicators": cards,
            "next_cursor": self.service.next_cursor(bound, [str(instances[-1]["object_id"])])
            if more
            else None,
        }

    # Indicator series --------------------------------------------------------------------------
    def series(self, c, ctx, obj, limit, cursor):
        instance = load(c, ctx, obj, "IndicatorInstance", "indicator-instances.read")
        pid = str(instance["payload"]["programme_id"])
        load(c, ctx, pid, "Programme", "programmes.read")
        indicator_id = str(instance["object_id"])
        pin = instance["payload"].get("definition_version")
        definition = self.definition(c, ctx, pin)
        bound = self.service.cursor_binding(ctx, "dashboards/indicator-instances/" + indicator_id + "/series")
        key = self.service.cursor_key(bound, cursor)
        # Periods holding this programme's snapshots or this indicator's results or targets, in
        # calendar order; keyset on (start, identifier).
        rows = c.execute(
            "SELECT p.object_id,p.starts_at,v.payload FROM impact.period_current p JOIN impact.object_registry r ON r.tenant_id=p.tenant_id AND r.object_id=p.object_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE p.tenant_id=%s AND v.restriction_state='AVAILABLE' AND p.object_id IN (SELECT period_id FROM impact.period_snapshot_binding WHERE tenant_id=%s AND programme_id=%s UNION SELECT period_id FROM impact.result_binding WHERE tenant_id=%s AND indicator_id=%s UNION SELECT period_id FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=%s)"
            + (" AND (p.starts_at,p.object_id)>(%s::timestamptz,%s::uuid)" if key else "")
            + " ORDER BY p.starts_at,p.object_id LIMIT %s",
            [
                ctx.tenant_id,
                ctx.tenant_id,
                pid,
                ctx.tenant_id,
                indicator_id,
                ctx.tenant_id,
                indicator_id,
                *(key if key else []),
                limit + 1,
            ],
        ).fetchall()
        more = len(rows) > limit
        rows = rows[:limit]
        points = []
        for period_row in rows:
            if not scopes(c, ctx, "periods.read", period_row["object_id"]):
                continue
            state = self.service.periods.state(c, ctx, pid, str(period_row["object_id"]))
            snapshot = self.snapshot(c, ctx, pid, period_row["object_id"])
            points.append(
                {
                    **self.period_head(period_row, state),
                    "snapshot_version": snapshot["snapshot_version"] if snapshot else None,
                    "locked_at": iso(snapshot["created_at"]) if snapshot else None,
                    **self.cell(
                        c, ctx, pid, indicator_id, pin, definition, period_row, snapshot, detail=False
                    ),
                }
            )
        last = rows[-1] if more else None
        return {
            **self.indicator_head(instance, definition),
            "programme_id": pid,
            "points": points,
            "next_cursor": self.service.next_cursor(
                bound, [last["starts_at"].isoformat(), str(last["object_id"])]
            )
            if last
            else None,
        }

    # Drill-down: the source observations behind a card (v0.27, FR-ANA-002 subset) ----------------
    def drilldown(self, c, ctx, obj, period_id, limit, cursor):
        """The period's source observations of one indicator instance as the reader may see them,
        each marked with its disposition in the value the card shows (INCLUDED, EXCLUDED, or not an
        input of that calculation). Rows the reader cannot read are absent and the response says
        the set is PARTIAL — never a count of hidden rows; the card's coverage already says
        UNAVAILABLE in that case."""
        instance = load(c, ctx, obj, "IndicatorInstance", "indicator-instances.read")
        period = load(c, ctx, period_id, "Period", "periods.read")
        pid = str(instance["payload"]["programme_id"])
        load(c, ctx, pid, "Programme", "programmes.read")
        indicator_id = str(instance["object_id"])
        pin = instance["payload"].get("definition_version")
        definition = self.definition(c, ctx, pin)
        places = definition.get("display_decimals", 2)
        bound = self.service.cursor_binding(
            ctx,
            "dashboards/indicator-instances/" + indicator_id + "/sources?period=" + str(period["object_id"]),
        )
        key = self.service.cursor_key(bound, cursor)
        state = self.service.periods.state(c, ctx, pid, str(period["object_id"]))
        snapshot = self.snapshot(c, ctx, pid, period["object_id"])
        official = self.official(c, ctx, snapshot, indicator_id, pin)
        latest = self.provisional(c, ctx, indicator_id, str(period["object_id"]), pin)
        shown_value = official or latest
        edges = {}
        if shown_value:
            for edge in c.execute(
                "SELECT source_revision,contribution_identity,disposition,reason_code FROM impact.lineage_edge WHERE tenant_id=%s AND result_revision=%s",
                (ctx.tenant_id, str(shown_value["result_revision"])),
            ).fetchall():
                edges[edge["contribution_identity"]] = edge
        complete = self.sources(c, ctx, indicator_id, period["payload"]) is not None
        predicate, args = visible_sql(ctx, "observations.read")
        rows = c.execute(
            "SELECT r.object_id,r.head_revision,r.lifecycle_state,r.updated_at,v.payload FROM impact.observation_current o JOIN impact.object_registry r ON r.tenant_id=o.tenant_id AND r.object_id=o.object_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE o.tenant_id=%s AND o.indicator_id=%s AND o.event_at>=%s AND o.event_at<%s AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' AND "
            + predicate
            + (" AND r.object_id>%s::uuid" if key else "")
            + " ORDER BY r.object_id LIMIT %s",
            [
                ctx.tenant_id,
                indicator_id,
                period["payload"]["starts_at"],
                period["payload"]["ends_at"],
                *args,
                *([key[0]] if key else []),
                limit + 1,
            ],
        ).fetchall()
        more = len(rows) > limit
        rows = rows[:limit]
        items = []
        for row in rows:
            p = row["payload"]
            present = p.get("value_state") == "PRESENT" and p.get("value") is not None
            edge = edges.get(str(row["object_id"]))
            items.append(
                {
                    "observation_id": str(row["object_id"]),
                    "revision_id": str(row["head_revision"]),
                    "source_namespace": p.get("source_namespace"),
                    "source_key": p.get("source_key"),
                    "event_at": p.get("event_at"),
                    "value_state": p.get("value_state"),
                    "value": p.get("value") if present else None,
                    "displayed_value": shown(p.get("value"), places) if present else None,
                    "numerator": p.get("numerator"),
                    "denominator": p.get("denominator"),
                    "approval_state": p.get("approval_state"),
                    "lifecycle_state": row["lifecycle_state"],
                    "contribution": edge["disposition"]
                    if edge
                    else ("NOT_IN_RESULT" if shown_value else None),
                    "contribution_reason": edge["reason_code"] if edge else None,
                    "changed_since_calculation": bool(edge)
                    and str(edge["source_revision"]) != str(row["head_revision"]),
                    "updated_at": iso(row["updated_at"]),
                }
            )
        return {
            **self.indicator_head(instance, definition),
            "programme_id": pid,
            "period": self.period_head(period, state),
            "value": {
                "mode": shown_value["payload"].get("mode", "PROVISIONAL") if shown_value else None,
                "result_id": str(shown_value["result_id"]) if shown_value else None,
                "result_revision": str(shown_value["result_revision"]) if shown_value else None,
            },
            "source_check": "COMPLETE" if complete else "PARTIAL",
            "items": items,
            "next_cursor": self.service.next_cursor(bound, [str(rows[-1]["object_id"])]) if more else None,
        }

    # Portfolio: one indicator definition across every programme (v0.27) -------------------------
    def portfolio(self, c, ctx, obj, period_id, limit, cursor):
        """For one indicator definition and period: the official value of every instance of it in
        the tenant (one row per programme instance, keyset on the instance identifier), grouped by
        definition version, with a pooled total per version only where the version's method pools
        (SUM, COUNT: sum of the official values; POOLED_RATIO: sum of numerators over sum of
        denominators from the stored components — never a sum of displayed percentages). A total
        is withheld when the reader cannot see every instance, when any visible instance lacks an
        official PRESENT value for the period, or when the method does not pool."""
        head = load(c, ctx, obj, "IndicatorDefinition", "indicator-definitions.read")
        period = load(c, ctx, period_id, "Period", "periods.read")
        did = str(head["object_id"])
        bound = self.service.cursor_binding(
            ctx, "dashboards/indicator-definitions/" + did + "/portfolio?period=" + str(period["object_id"])
        )
        key = self.service.cursor_key(bound, cursor)
        predicate, args = visible_sql(ctx, "indicator-instances.read")
        everything = c.execute(
            "SELECT count(*) AS n FROM impact.indicator_instance_current i JOIN impact.object_revision d ON d.tenant_id=i.tenant_id AND d.revision_id=i.definition_version WHERE i.tenant_id=%s AND d.object_id=%s",
            (ctx.tenant_id, did),
        ).fetchone()["n"]
        visible = c.execute(
            "SELECT r.object_id,r.lifecycle_state,v.payload,i.programme_id FROM impact.indicator_instance_current i JOIN impact.object_revision d ON d.tenant_id=i.tenant_id AND d.revision_id=i.definition_version JOIN impact.object_registry r ON r.tenant_id=i.tenant_id AND r.object_id=i.object_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE i.tenant_id=%s AND d.object_id=%s AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' AND "
            + predicate
            + " ORDER BY r.object_id LIMIT %s",
            [ctx.tenant_id, did, *args, PORTFOLIO_LIMIT + 1],
        ).fetchall()
        too_many = len(visible) > PORTFOLIO_LIMIT
        visible = visible[:PORTFOLIO_LIMIT]
        scope = "COMPLETE" if everything == len(visible) and not too_many else "PARTIAL"
        definitions, snapshots, cells = {}, {}, {}
        for instance in visible:
            pin = instance["payload"].get("definition_version")
            if pin not in definitions:
                definitions[pin] = self.definition(c, ctx, pin)
            pid = str(instance["programme_id"])
            if pid not in snapshots:
                snapshots[pid] = (
                    self.snapshot(c, ctx, pid, period["object_id"])
                    if scopes(c, ctx, "programmes.read", pid)
                    else None
                )
            cells[str(instance["object_id"])] = self.official(
                c, ctx, snapshots[pid], str(instance["object_id"]), pin
            )
        versions = []
        for pin in sorted(definitions, key=lambda p: (definitions[p].get("version_number") or 0, p)):
            members = [i for i in visible if i["payload"].get("definition_version") == pin]
            versions.append(
                {
                    "definition_revision": pin,
                    "version_number": definitions[pin].get("version_number"),
                    "combination_rule": definitions[pin].get("combination_rule"),
                    "instance_count": len(members),
                    "pooled": pooled(definitions[pin], [cells[str(i["object_id"])] for i in members], scope),
                }
            )
        page = [i for i in visible if not key or str(i["object_id"]) > key[0]][: limit + 1]
        more = len(page) > limit
        page = page[:limit]
        programmes = []
        for instance in page:
            pid = str(instance["programme_id"])
            pin = instance["payload"].get("definition_version")
            definition = definitions[pin]
            places = definition.get("display_decimals", 2)
            programme = (
                load(c, ctx, pid, "Programme", "programmes.read")
                if scopes(c, ctx, "programmes.read", pid)
                else None
            )
            snapshot = snapshots.get(pid)
            official = cells[str(instance["object_id"])]
            state = self.service.periods.state(c, ctx, pid, str(period["object_id"]))
            programmes.append(
                {
                    **self.indicator_head(instance, definition),
                    "programme_id": pid,
                    "programme_title": (programme["payload"].get("title") or programme["payload"].get("code"))
                    if programme
                    else None,
                    "period_state": state["lifecycle_state"],
                    "snapshot_version": snapshot["snapshot_version"] if snapshot else None,
                    "locked_at": iso(snapshot["created_at"]) if snapshot else None,
                    "official": value_block(official, places) if official else None,
                    "coverage": self.coverage(
                        c, ctx, str(instance["object_id"]), definition, period, snapshot
                    ),
                }
            )
        p = period["payload"]
        return {
            "definition_id": did,
            "definition_name": head["payload"].get("name"),
            "unit": head["payload"].get("unit"),
            "measurement_type": head["payload"].get("measurement_type"),
            "combination_rule": head["payload"].get("combination_rule"),
            "display_decimals": head["payload"].get("display_decimals", 2),
            "period": {
                "period_id": str(period["object_id"]),
                "period_code": p.get("code"),
                "starts_at": p.get("starts_at"),
                "ends_at": p.get("ends_at"),
            },
            "scope": scope,
            "versions": versions,
            "programmes": programmes,
            "next_cursor": self.service.next_cursor(bound, [str(page[-1]["object_id"])]) if more else None,
        }


PORTFOLIO_LIMIT = 500
POOLABLE = {"SUM", "COUNT", "POOLED_RATIO"}


def pooled(definition, officials, scope):
    """The pooled total of one definition version's official values, or a withheld block. Pooled
    ratios come from the stored numerators and denominators (51/110 + 8/10 -> 59/120 = 49.17,
    never an average of displayed percentages); a zero denominator is UNDEFINED, never 0."""
    from decimal import Decimal, localcontext

    from .domain import PRECISION, stored

    rule = definition.get("combination_rule")
    places = definition.get("display_decimals", 2)
    block = {
        "method": rule,
        "value_state": "UNDEFINED",
        "value": None,
        "displayed_value": None,
        "numerator": None,
        "denominator": None,
        "instance_count": len(officials),
        "contributing_count": sum(1 for o in officials if o is not None),
        "reason_code": None,
    }
    if rule not in POOLABLE:
        return {**block, "value_state": "NOT_APPLICABLE", "reason_code": "NOT_POOLABLE"}
    if scope != "COMPLETE":
        return {**block, "value_state": "MISSING", "reason_code": "SCOPE_PARTIAL"}
    if not officials:
        return {**block, "value_state": "MISSING", "reason_code": "NO_INSTANCES"}
    payloads = [o["payload"] for o in officials if o is not None]
    if len(payloads) != len(officials) or any(p.get("value_state") != "PRESENT" for p in payloads):
        return {**block, "value_state": "MISSING", "reason_code": "OFFICIAL_VALUES_INCOMPLETE"}
    with localcontext() as context:
        context.prec = PRECISION
        if rule == "POOLED_RATIO":
            if any(p.get("numerator") is None or p.get("denominator") is None for p in payloads):
                return {**block, "value_state": "MISSING", "reason_code": "COMPONENTS_MISSING"}
            n = sum((decimal_value(p["numerator"]) for p in payloads), Decimal(0))
            d = sum((decimal_value(p["denominator"]) for p in payloads), Decimal(0))
            block.update(numerator=stored(n), denominator=stored(d))
            if d == 0:
                return {**block, "value_state": "UNDEFINED", "reason_code": "ZERO_DENOMINATOR"}
            value = n / d * (100 if definition.get("measurement_type") == "PERCENTAGE" else 1)
        else:
            value = sum((decimal_value(p["value"]) for p in payloads), Decimal(0))
    kept = stored(value)
    return {**block, "value_state": "PRESENT", "value": kept, "displayed_value": shown(kept, places)}
