"""Personal work, safe in-app notices and explicit recalculation recovery."""

from datetime import datetime, timedelta, timezone
from uuid import NAMESPACE_URL, uuid4, uuid5

from .delivery import enqueue
from .domain import DomainError, unavailable
from .store import audit, envelope, load, write


class WorkCenter:
    def __init__(self, service):
        self.service = service

    @staticmethod
    def _id(value):
        return str(uuid5(NAMESPACE_URL, "impact-work-v1:" + value))

    def ensure_visible(self, ctx, row):
        field = "assignee_id" if row["object_type"] == "WorkItem" else "recipient_id"
        if str(row["payload"].get(field)) != str(ctx.principal_id):
            unavailable()

    def listing_filter(self, route, ctx):
        if route == "work-items":
            return (
                "EXISTS(SELECT 1 FROM impact.work_item_current personal "
                "WHERE personal.tenant_id=r.tenant_id AND personal.object_id=r.object_id "
                "AND personal.assignee_id=%s)",
                [ctx.principal_id],
            )
        if route == "notifications":
            return (
                "EXISTS(SELECT 1 FROM impact.notification_current personal "
                "WHERE personal.tenant_id=r.tenant_id AND personal.object_id=r.object_id "
                "AND personal.recipient_id=%s)",
                [ctx.principal_id],
            )
        return "TRUE", []

    def decorate(self, c, ctx, row, result=None):
        if row["object_type"] not in {"WorkItem", "Notification"}:
            return result or envelope(row)
        self.ensure_visible(ctx, row)
        result = result or envelope(row)
        data = dict(result["data"])
        if row["object_type"] == "Notification":
            acknowledgement = c.execute(
                "SELECT acknowledged_at FROM impact.notification_acknowledgement "
                "WHERE tenant_id=%s AND notification_id=%s AND recipient_id=%s",
                (ctx.tenant_id, row["object_id"], ctx.principal_id),
            ).fetchone()
            data["acknowledged_at"] = (
                acknowledgement["acknowledged_at"].isoformat() if acknowledgement else None
            )
            delivery = c.execute(
                "SELECT delivered_at FROM impact.notification_delivery "
                "WHERE tenant_id=%s AND notification_id=%s AND channel='IN_APP'",
                (ctx.tenant_id, row["object_id"]),
            ).fetchone()
            data["delivered_at"] = delivery["delivered_at"].isoformat() if delivery else None
        else:
            invalidations = c.execute(
                "SELECT state,result_id,result_revision,indicator_id,period_id,reason_code,"
                "replacement_result_id,created_at,resolved_at FROM impact.calculation_invalidation "
                "WHERE tenant_id=%s AND work_item_id=%s ORDER BY created_at,invalidation_id",
                (ctx.tenant_id, row["object_id"]),
            ).fetchall()
            if invalidations:
                data["calculation"] = {
                    "state": (
                        "PENDING"
                        if any(item["state"] == "PENDING" for item in invalidations)
                        else "RECALCULATED"
                    ),
                    "affected_result_count": len(invalidations),
                    "indicator_id": str(invalidations[0]["indicator_id"]),
                    "period_id": str(invalidations[0]["period_id"]),
                    "reason_codes": sorted({item["reason_code"] for item in invalidations}),
                    "replacement_result_id": (
                        str(invalidations[0]["replacement_result_id"])
                        if invalidations[0]["replacement_result_id"]
                        else None
                    ),
                }
        result["data"] = data
        return result

    def assignee(self, c, ctx, preferred):
        if preferred and self.service.measurement.eligible(c, ctx, preferred, "indicator.calculate"):
            return str(preferred)
        row = c.execute(
            "SELECT p.principal_id FROM impact.tenant_principal p "
            "JOIN impact.membership_current m ON m.tenant_id=p.tenant_id AND m.identity_id=p.identity_id "
            "JOIN impact.object_registry mr ON mr.tenant_id=m.tenant_id AND mr.object_id=m.object_id "
            "JOIN impact.grant_current g ON g.tenant_id=p.tenant_id AND g.subject_id=p.principal_id "
            "JOIN impact.object_registry gr ON gr.tenant_id=g.tenant_id AND gr.object_id=g.object_id "
            "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
            "WHERE p.tenant_id=%s AND p.active AND mr.lifecycle_state='Active' "
            "AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now()) "
            "AND gr.lifecycle_state='Active' AND g.capability='indicator.calculate' AND g.purpose IS NULL "
            "AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now()) "
            "AND s.scope_type='TENANT' ORDER BY p.principal_id LIMIT 1",
            (ctx.tenant_id,),
        ).fetchone()
        return str(row["principal_id"]) if row else None

    def notify(self, c, ctx, work, recipient, notice_class, correlation):
        notification_id = self._id(str(work["object_id"]) + ":" + recipient + ":" + notice_class)
        existing = c.execute(
            "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
            (ctx.tenant_id, notification_id),
        ).fetchone()
        if existing:
            return
        event_id = audit(c, ctx, "work-item.created", work, correlation)
        notice = write(
            c,
            ctx,
            "Notification",
            {
                "event_id": event_id,
                "recipient_id": recipient,
                "channel": "IN_APP",
                "notice_class": notice_class,
                "safe_reference": work["object_id"],
            },
            "Unread",
            object_id=notification_id,
            track_author=False,
        )
        audit(c, ctx, "notification.created", notice, correlation)
        # The notice is visible at once; the worker records its in-app delivery (v0.16).
        enqueue(c, ctx.tenant_id, "IN_APP_NOTICE", notification_id)

    def invalidate(
        self,
        c,
        ctx,
        indicator_id,
        period_id,
        triggering_revision,
        reason_code,
        correlation,
    ):
        results = c.execute(
            "SELECT r.object_id,r.head_revision FROM impact.result_binding b "
            "JOIN impact.object_registry r ON r.tenant_id=b.tenant_id AND r.object_id=b.result_id "
            "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE b.tenant_id=%s AND b.indicator_id=%s AND b.period_id=%s "
            "AND v.payload->>'mode'='PROVISIONAL' ORDER BY r.updated_at DESC,r.object_id LIMIT 501",
            (ctx.tenant_id, indicator_id, period_id),
        ).fetchall()
        if len(results) > 500:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="INVALIDATION_RESULT_LIMIT")
        if not results:
            return None
        indicator = load(c, ctx, indicator_id, "IndicatorInstance")
        programme = load(c, ctx, indicator["payload"]["programme_id"], "Programme")
        period = load(c, ctx, period_id, "Period")
        assignee = self.assignee(c, ctx, indicator["payload"].get("collector_id"))
        if not assignee:
            raise DomainError("INVALID_STATE", 409, reason="RECALCULATION_OWNER_REQUIRED")
        work_id = self._id(
            ":".join(
                [ctx.tenant_id, str(indicator_id), str(period_id), str(triggering_revision), "recalculate"]
            )
        )
        current = c.execute(
            "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
            "FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_id=%s",
            (ctx.tenant_id, work_id),
        ).fetchone()
        if current:
            work = {
                "object_id": str(current["object_id"]),
                "revision_id": str(current["head_revision"]),
                "business_state": current["lifecycle_state"],
                "saved_at": current["updated_at"].isoformat(),
            }
        else:
            indicator_name = indicator["payload"].get("local_applicability") or "indicator"
            period_name = period["payload"].get("label") or period["payload"].get("code") or "period"
            title = f"Recalculate {indicator_name} for {period_name}"
            work = write(
                c,
                ctx,
                "WorkItem",
                {
                    "programme_id": str(programme["object_id"]),
                    "work_type": "ACTION",
                    "title": title[:200],
                    "dependency_ids": [],
                    "due_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                    "assignee_id": assignee,
                    "severity": "MATERIAL",
                },
                "Open",
                object_id=work_id,
                track_author=False,
            )
        for result in results:
            c.execute(
                "INSERT INTO impact.calculation_invalidation "
                "(tenant_id,invalidation_id,result_id,result_revision,indicator_id,period_id,"
                "triggering_revision,reason_code,work_item_id,state,created_at) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,'PENDING',now()) ON CONFLICT DO NOTHING",
                (
                    ctx.tenant_id,
                    str(uuid4()),
                    result["object_id"],
                    result["head_revision"],
                    indicator_id,
                    period_id,
                    triggering_revision,
                    reason_code,
                    work_id,
                ),
            )
        self.notify(c, ctx, work, assignee, "CALCULATION_STALE", correlation)
        return work

    def invalidate_observation(self, c, ctx, observation, triggering_revision, reason_code, correlation):
        periods = c.execute(
            "SELECT DISTINCT b.period_id FROM impact.result_binding b "
            "JOIN impact.period_current p ON p.tenant_id=b.tenant_id AND p.object_id=b.period_id "
            "WHERE b.tenant_id=%s AND b.indicator_id=%s AND %s>=p.starts_at AND %s<p.ends_at "
            "ORDER BY b.period_id LIMIT 501",
            (
                ctx.tenant_id,
                observation["indicator_id"],
                observation["event_at"],
                observation["event_at"],
            ),
        ).fetchall()
        if len(periods) > 500:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="INVALIDATION_PERIOD_LIMIT")
        for period in periods:
            self.invalidate(
                c,
                ctx,
                observation["indicator_id"],
                period["period_id"],
                triggering_revision,
                reason_code,
                correlation,
            )

    def acknowledge(self, c, ctx, notification, _data):
        self.ensure_visible(ctx, notification)
        row = c.execute(
            "SELECT acknowledged_at FROM impact.notification_acknowledgement "
            "WHERE tenant_id=%s AND notification_id=%s",
            (ctx.tenant_id, notification["object_id"]),
        ).fetchone()
        at = row["acknowledged_at"] if row else datetime.now(timezone.utc)
        if not row:
            c.execute(
                "INSERT INTO impact.notification_acknowledgement VALUES(%s,%s,%s,%s)",
                (ctx.tenant_id, notification["object_id"], ctx.principal_id, at),
            )
        return {
            "operation_id": "",
            "object_id": str(notification["object_id"]),
            "revision_id": str(notification["head_revision"]),
            "business_state": "Acknowledged",
            "saved_at": at.isoformat(),
            "correlation_id": "",
        }

    def recalculate(self, c, ctx, work_item, _data, correlation):
        self.ensure_visible(ctx, work_item)
        if work_item["lifecycle_state"] != "Open":
            raise DomainError("INVALID_STATE", 409, reason="WORK_ITEM_NOT_OPEN")
        pending = c.execute(
            "SELECT * FROM impact.calculation_invalidation WHERE tenant_id=%s "
            "AND work_item_id=%s AND state='PENDING' ORDER BY invalidation_id",
            (ctx.tenant_id, work_item["object_id"]),
        ).fetchall()
        if not pending:
            raise DomainError("INVALID_STATE", 409, reason="NO_PENDING_RECALCULATION")
        indicator_id, period_id = pending[0]["indicator_id"], pending[0]["period_id"]
        if any(row["indicator_id"] != indicator_id or row["period_id"] != period_id for row in pending):
            raise DomainError("INVALID_STATE", 409, reason="MIXED_RECALCULATION_TASK")
        indicator = load(c, ctx, indicator_id, "IndicatorInstance", "indicator-instances.read")
        result = self.service.calculate(
            c, ctx, indicator, {"period_id": str(period_id)}, correlation=correlation
        )
        audit(c, ctx, "indicator.recalculated", result, correlation)
        completed = load(c, ctx, work_item["object_id"], "WorkItem")
        if completed["lifecycle_state"] != "Completed":
            raise DomainError("CONFLICT_VERSION", 409)
        receipt = {
            "operation_id": "",
            "object_id": str(completed["object_id"]),
            "revision_id": str(completed["head_revision"]),
            "business_state": "Completed",
            "saved_at": completed["updated_at"].isoformat(),
            "correlation_id": "",
            "result_id": result["object_id"],
            "result_revision": result["revision_id"],
        }
        return receipt

    def resolve(self, c, ctx, indicator_id, period_id, result, correlation):
        related = c.execute(
            "SELECT DISTINCT work_item_id FROM impact.calculation_invalidation "
            "WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s AND state='PENDING'",
            (ctx.tenant_id, indicator_id, period_id),
        ).fetchall()
        c.execute(
            "UPDATE impact.calculation_invalidation SET state='RECALCULATED',resolved_at=now(),"
            "replacement_result_id=%s WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s "
            "AND state='PENDING'",
            (result["object_id"], ctx.tenant_id, indicator_id, period_id),
        )
        for item in related:
            row = load(c, ctx, item["work_item_id"], "WorkItem", lock=True)
            if row["lifecycle_state"] == "Open":
                receipt = write(c, ctx, "WorkItem", row["payload"], "Completed", row, track_author=False)
                audit(c, ctx, "work-item.completed", receipt, correlation)
                self.notify(
                    c,
                    ctx,
                    receipt,
                    str(row["payload"]["assignee_id"]),
                    "RECALCULATION_COMPLETED",
                    correlation,
                )

    def stale(self, c, ctx, result_revision):
        return bool(
            c.execute(
                "SELECT 1 FROM impact.calculation_invalidation WHERE tenant_id=%s "
                "AND result_revision=%s AND state='PENDING' LIMIT 1",
                (ctx.tenant_id, result_revision),
            ).fetchone()
        )
