"""Atomic period close, immutable official snapshots and scoped restatement windows."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from psycopg.types.json import Jsonb
from .contracts import validate
from .domain import DomainError
from .measurement import coverage
from .store import audit, hash_data, load, write


class PeriodGovernance:
    def __init__(self, service):
        self.service = service

    def latest_snapshot(self, c, ctx, programme_id, period_id):
        return c.execute(
            "SELECT * FROM impact.period_snapshot_binding WHERE tenant_id=%s AND programme_id=%s AND period_id=%s ORDER BY snapshot_version DESC LIMIT 1",
            (ctx.tenant_id, programme_id, period_id),
        ).fetchone()

    def state(self, c, ctx, programme_id, period_id, lock=False):
        suffix = " FOR UPDATE" if lock else ""
        row = c.execute(
            "SELECT * FROM impact.programme_period_state WHERE tenant_id=%s AND programme_id=%s AND period_id=%s"
            + suffix,
            (ctx.tenant_id, programme_id, period_id),
        ).fetchone()
        if not row:
            return {
                "tenant_id": ctx.tenant_id,
                "programme_id": programme_id,
                "period_id": period_id,
                "lifecycle_state": "Open",
                "current_snapshot_version": 0,
                "restatement_expires_at": None,
            }
        if row["lifecycle_state"] == "RestatementOpen" and row["restatement_expires_at"] <= datetime.now(
            timezone.utc
        ):
            return {**row, "lifecycle_state": "Locked"}
        return row

    def set_state(self, c, ctx, programme_id, period_id, state, snapshot_version, expires_at=None):
        if state == "RestatementOpen" and expires_at is None:
            raise RuntimeError("restatement expiry is required")
        c.execute(
            "INSERT INTO impact.programme_period_state VALUES(%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT(tenant_id,programme_id,period_id) DO UPDATE SET "
            "lifecycle_state=EXCLUDED.lifecycle_state,current_snapshot_version=EXCLUDED.current_snapshot_version,"
            "restatement_expires_at=EXCLUDED.restatement_expires_at,updated_at=EXCLUDED.updated_at,updated_by=EXCLUDED.updated_by",
            (
                ctx.tenant_id,
                programme_id,
                period_id,
                state,
                snapshot_version,
                expires_at,
                datetime.now(timezone.utc),
                ctx.principal_id,
            ),
        )

    def assert_source_mutable(self, c, ctx, indicator_id, event_at, source_id):
        indicator = load(c, ctx, indicator_id, "IndicatorInstance", "indicator-instances.read")
        programme_id = indicator["payload"]["programme_id"]
        period = c.execute(
            "SELECT object_id FROM impact.period_current WHERE tenant_id=%s AND starts_at<=%s AND ends_at>%s ORDER BY starts_at DESC LIMIT 1",
            (ctx.tenant_id, event_at, event_at),
        ).fetchone()
        if not period:
            return
        state = self.state(c, ctx, programme_id, period["object_id"])["lifecycle_state"]
        permitted = (
            source_id
            and state == "RestatementOpen"
            and c.execute(
                "SELECT 1 FROM impact.restatement_source_permission WHERE tenant_id=%s AND programme_id=%s AND period_id=%s AND source_id=%s AND expires_at>now() LIMIT 1",
                (ctx.tenant_id, programme_id, period["object_id"], source_id),
            ).fetchone()
        )
        if state != "Open" and not permitted:
            raise DomainError("INVALID_STATE", 409, reason="PERIOD_RESTATEMENT_REQUIRED")

    def workflow(self, c, ctx, candidate, workflow_version, related):
        from .service import revision

        template_row = revision(c, ctx, workflow_version, "WorkflowTemplate", "workflow-templates.read")
        template_head = load(c, ctx, template_row["object_id"])
        template = template_row["payload"]
        if (
            template_head["lifecycle_state"] != "Active"
            or str(template_head["head_revision"]) != workflow_version
            or template.get("required_approvals") != 1
            or template.get("independent") is not True
        ):
            raise DomainError("INVALID_STATE", 409, reason="ACTIVE_INDEPENDENT_WORKFLOW_REQUIRED")
        workflow = write(
            c,
            ctx,
            "Workflow",
            {
                "candidate_id": candidate["object_id"],
                "candidate_revision": candidate["revision_id"],
                "workflow_version": workflow_version,
                "stages": [
                    {
                        "stage_id": str(uuid4()),
                        "position": 0,
                        "required_approvals": 1,
                        "candidate_membership_ids": [],
                        "required_capability": "workflow.approve",
                        "independent": True,
                    }
                ],
            },
            "InReview",
            track_author=False,
        )
        for object_id in {candidate["object_id"], *related}:
            c.execute(
                "INSERT INTO impact.workflow_author SELECT tenant_id,%s,natural_identity_id,%s FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s ON CONFLICT DO NOTHING",
                (workflow["object_id"], candidate["revision_id"], ctx.tenant_id, object_id),
            )
        return workflow

    @staticmethod
    def blocker(code, message, object_id=None):
        return {"code": code, "message": message, "object_id": str(object_id) if object_id else None}

    def preview(self, c, ctx, period, programme_id):
        from .service import revision, source_digest, source_rows

        if period["lifecycle_state"] != "Open":
            raise DomainError("INVALID_STATE", 409, reason="OPEN_CALENDAR_PERIOD_REQUIRED")
        programme = load(c, ctx, programme_id, "Programme", "programmes.read")
        if programme["lifecycle_state"] != "Active":
            raise DomainError("INVALID_STATE", 409, reason="ACTIVE_PROGRAMME_REQUIRED")
        if not (
            programme["payload"].get("starts_at")
            and programme["payload"].get("ends_at")
            and programme["payload"]["starts_at"] <= period["payload"]["starts_at"]
            and programme["payload"]["ends_at"] >= period["payload"]["ends_at"]
        ):
            raise DomainError("VALIDATION_FAILED", reason="PERIOD_OUTSIDE_PROGRAMME")
        prior = self.latest_snapshot(c, ctx, programme_id, period["object_id"])
        state = self.state(c, ctx, programme_id, period["object_id"])
        blockers = []
        if state["lifecycle_state"] == "Locked":
            raise DomainError("INVALID_STATE", 409, reason="PERIOD_ALREADY_SNAPSHOTTED")
        if state["lifecycle_state"] == "Open" and prior:
            raise DomainError("INVALID_STATE", 409, reason="PERIOD_STATE_INCONSISTENT")
        if state["lifecycle_state"] == "RestatementOpen":
            active = c.execute(
                "SELECT 1 FROM impact.restatement_source_permission WHERE tenant_id=%s AND programme_id=%s AND period_id=%s AND expires_at>now() LIMIT 1",
                (ctx.tenant_id, programme_id, period["object_id"]),
            ).fetchone()
            if not prior or not active:
                blockers.append(
                    self.blocker(
                        "RESTATEMENT_WINDOW_REQUIRED",
                        "A current approved restatement window is required before a replacement snapshot can be reviewed.",
                        period["object_id"],
                    )
                )
        candidates = c.execute(
            "SELECT i.object_id FROM impact.indicator_instance_current i JOIN impact.object_registry ir ON ir.tenant_id=i.tenant_id AND ir.object_id=i.object_id WHERE i.tenant_id=%s AND i.programme_id=%s AND ir.lifecycle_state='Active' ORDER BY i.object_id LIMIT 501",
            (ctx.tenant_id, programme_id),
        ).fetchall()
        if len(candidates) > 500:
            raise DomainError("LIMIT_EXCEEDED", 422)
        if not candidates:
            blockers.append(
                self.blocker(
                    "NO_ACTIVE_INDICATORS",
                    "At least one active indicator and programme must apply to the period.",
                    period["object_id"],
                )
            )
        entries = []
        previewed = datetime.now(timezone.utc)
        for candidate in candidates:
            indicator = load(c, ctx, candidate["object_id"], "IndicatorInstance", "indicator-instances.read")
            plan = self.service.measurement.plan(c, ctx, indicator["object_id"], period["object_id"])
            if not plan:
                blockers.append(
                    self.blocker(
                        "APPROVED_PLAN_REQUIRED",
                        "The indicator has no approved collection plan for this period.",
                        indicator["object_id"],
                    )
                )
                continue
            definition = revision(
                c,
                ctx,
                indicator["payload"]["definition_version"],
                "IndicatorDefinition",
                "indicator-definitions.read",
            )
            rows = source_rows(c, ctx, indicator["object_id"], period["payload"])
            digest = source_digest(rows)
            measured, _ = coverage(plan, rows, definition["payload"], previewed)
            entry_blockers = []
            for field, code, message in [
                ("pending_count", "PENDING_VALUES", "Submitted or draft planned values remain."),
                ("missing_count", "MISSING_VALUES", "Mandatory planned values are missing."),
                (
                    "excluded_count",
                    "INVALID_OR_REJECTED_VALUES",
                    "Invalid, non-applicable or rejected planned values require resolution.",
                ),
                (
                    "unplanned_count",
                    "UNPLANNED_VALUES",
                    "Unplanned observations require resolution before close.",
                ),
            ]:
                if measured.get(field, 0):
                    entry_blockers.append(self.blocker(code, message, indicator["object_id"]))
            result_row = c.execute(
                "SELECT r.object_id,r.head_revision,b.source_digest,b.plan_revision FROM impact.result_binding b JOIN impact.object_registry r ON r.tenant_id=b.tenant_id AND r.object_id=b.result_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE b.tenant_id=%s AND b.indicator_id=%s AND b.period_id=%s AND v.payload->>'mode'='PROVISIONAL' ORDER BY r.created_at DESC,r.object_id DESC LIMIT 1",
                (ctx.tenant_id, indicator["object_id"], period["object_id"]),
            ).fetchone()
            if not result_row:
                entry_blockers.append(
                    self.blocker(
                        "CURRENT_RESULT_REQUIRED",
                        "Calculate a current provisional result before close.",
                        indicator["object_id"],
                    )
                )
            elif result_row["source_digest"] != digest or str(result_row["plan_revision"]) != str(
                plan["head_revision"]
            ):
                entry_blockers.append(
                    self.blocker(
                        "RESULT_STALE",
                        "The latest provisional result does not match current sources and plan.",
                        result_row["object_id"],
                    )
                )
            entries.append(
                {
                    "indicator_id": str(indicator["object_id"]),
                    "indicator_revision": str(indicator["head_revision"]),
                    "definition_revision": str(definition["revision_id"]),
                    "plan_id": str(plan["object_id"]),
                    "plan_revision": str(plan["head_revision"]),
                    "result_id": str(result_row["object_id"]) if result_row else None,
                    "result_revision": str(result_row["head_revision"]) if result_row else None,
                    "source_revisions": [str(row["head_revision"]) for row in rows],
                    "source_digest": digest,
                    "coverage": measured,
                    "blockers": entry_blockers,
                }
            )
            blockers.extend(entry_blockers)
        core = {
            "period_revision": str(period["head_revision"]),
            "programme_period_state": state["lifecycle_state"],
            "previous_snapshot_id": str(prior["snapshot_id"]) if prior else None,
            "entries": entries,
            "blockers": blockers,
        }
        return {
            **core,
            "period_id": str(period["object_id"]),
            "programme_id": str(programme_id),
            "previewed_at": previewed.isoformat(),
            "fingerprint": hash_data(core).hex(),
        }

    def close_request(self, c, ctx, period, data):
        preview = self.preview(c, ctx, period, data["programme_id"])
        payload = {**preview, "reason": data["reason"]}
        validate("PeriodCloseData", payload)
        candidate = write(c, ctx, "PeriodClose", payload, "Submitted")
        related = [period["object_id"], data["programme_id"]]
        for entry in payload["entries"]:
            related.extend([entry["indicator_id"], *[str(x) for x in self.source_objects(c, ctx, entry)]])
        return self.workflow(c, ctx, candidate, data["workflow_version"], related)

    def source_objects(self, c, ctx, entry):
        if not entry["source_revisions"]:
            return []
        return [
            row["object_id"]
            for row in c.execute(
                "SELECT object_id FROM impact.object_revision WHERE tenant_id=%s AND revision_id=ANY(%s::uuid[])",
                (ctx.tenant_id, entry["source_revisions"]),
            ).fetchall()
        ]

    def validate_restatement(self, c, ctx, period, data):
        now = datetime.now(timezone.utc)
        expires = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        if expires <= now or expires > now + timedelta(days=7):
            raise DomainError("VALIDATION_FAILED", reason="RESTATEMENT_WINDOW_MAX_SEVEN_DAYS")
        load(c, ctx, data["programme_id"], "Programme", "programmes.read")
        prior = self.latest_snapshot(c, ctx, data["programme_id"], period["object_id"])
        if not prior:
            raise DomainError("INVALID_STATE", 409, reason="LOCKED_SNAPSHOT_REQUIRED")
        state = self.state(c, ctx, data["programme_id"], period["object_id"], lock=True)
        if state["lifecycle_state"] == "RestatementOpen":
            active = c.execute(
                "SELECT 1 FROM impact.restatement_source_permission WHERE tenant_id=%s AND programme_id=%s AND period_id=%s AND expires_at>now() LIMIT 1",
                (ctx.tenant_id, data["programme_id"], period["object_id"]),
            ).fetchone()
            if active:
                raise DomainError("INVALID_STATE", 409, reason="RESTATEMENT_ALREADY_OPEN")
        elif state["lifecycle_state"] != "Locked":
            raise DomainError("INVALID_STATE", 409, reason="LOCKED_PERIOD_REQUIRED")
        snapshot = load(c, ctx, prior["snapshot_id"], "Snapshot", "snapshots.read")
        if str(snapshot["head_revision"]) != str(prior["snapshot_revision"]):
            raise DomainError("CONFLICT_VERSION", 409, reason="SNAPSHOT_CHANGED")
        for source_id in data["source_ids"]:
            source = load(c, ctx, source_id, "Observation", "observations.read")
            if source["lifecycle_state"] != "Approved":
                raise DomainError("INVALID_STATE", 409, reason="APPROVED_SOURCE_REQUIRED")
            included = c.execute(
                "SELECT 1 FROM impact.official_result_snapshot s JOIN impact.lineage_edge e ON e.tenant_id=s.tenant_id AND e.result_revision=s.result_revision WHERE s.tenant_id=%s AND s.snapshot_id=%s AND e.contribution_identity=%s AND e.disposition='INCLUDED' LIMIT 1",
                (ctx.tenant_id, prior["snapshot_id"], source_id),
            ).fetchone()
            if not included:
                raise DomainError("VALIDATION_FAILED", reason="SOURCE_NOT_IN_LOCKED_SNAPSHOT")
        return prior, snapshot

    def restate_request(self, c, ctx, period, data):
        prior, snapshot = self.validate_restatement(c, ctx, period, data)
        payload = {
            "period_id": str(period["object_id"]),
            "programme_id": data["programme_id"],
            "period_revision": str(period["head_revision"]),
            "snapshot_id": str(prior["snapshot_id"]),
            "snapshot_revision": str(prior["snapshot_revision"]),
            "reason": data["reason"],
            "source_ids": data["source_ids"],
            "expires_at": data["expires_at"],
        }
        validate("RestatementRequestData", payload)
        candidate = write(c, ctx, "RestatementRequest", payload, "Submitted")
        return self.workflow(
            c,
            ctx,
            candidate,
            data["workflow_version"],
            [period["object_id"], data["programme_id"], snapshot["object_id"], *data["source_ids"]],
        )

    def apply_restatement(self, c, ctx, request, correlation):
        data = request["payload"]
        period = load(c, ctx, data["period_id"], "Period", "periods.read", lock=True)
        if str(period["head_revision"]) != data["period_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="RESTATEMENT_TARGET_CHANGED")
        self.validate_restatement(c, ctx, period, data)
        state = self.state(c, ctx, data["programme_id"], period["object_id"], lock=True)
        self.set_state(
            c,
            ctx,
            data["programme_id"],
            period["object_id"],
            "RestatementOpen",
            state["current_snapshot_version"],
            data["expires_at"],
        )
        for source_id in data["source_ids"]:
            c.execute(
                "INSERT INTO impact.restatement_source_permission VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    request["object_id"],
                    request["head_revision"],
                    data["programme_id"],
                    period["object_id"],
                    source_id,
                    data["expires_at"],
                ),
            )
        audit(
            c,
            ctx,
            "programme-period.restatement.opened",
            {
                "object_id": str(request["object_id"]),
                "revision_id": str(request["head_revision"]),
                "business_state": "RestatementOpen",
                "saved_at": datetime.now(timezone.utc).isoformat(),
            },
            correlation,
        )

    def apply_close(self, c, ctx, request, correlation):
        from .service import revision

        data = request["payload"]
        period = load(c, ctx, data["period_id"], "Period", "periods.read", lock=True)
        if str(period["head_revision"]) != data["period_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="PERIOD_CLOSE_PREVIEW_STALE")
        current = self.preview(c, ctx, period, data["programme_id"])
        if current["fingerprint"] != data["fingerprint"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="PERIOD_CLOSE_PREVIEW_STALE")
        if current["blockers"]:
            raise DomainError(
                "VALIDATION_FAILED",
                reason="PERIOD_CLOSE_BLOCKED",
                fields=[{"path": "blockers", "message": b["code"]} for b in current["blockers"][:20]],
            )
        snapshot_id = str(uuid4())
        run_id = str(request["object_id"])
        scope_id = next(
            grant["scope_id"]
            for grant in ctx.grants
            if grant["capability"] == "period.close"
            and grant["scope_type"] == "TENANT"
            and grant["purpose"] is None
        )
        c.execute(
            "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest) VALUES(%s,%s,'PERIOD_CLOSE',%s,%s,'Running',%s)",
            (
                ctx.tenant_id,
                run_id,
                ctx.principal_id,
                scope_id,
                Jsonb(
                    {
                        "programme_id": data["programme_id"],
                        "period_id": data["period_id"],
                        "close_revision": str(request["head_revision"]),
                        "fingerprint": data["fingerprint"],
                    }
                ),
            ),
        )
        official = []
        definitions = []
        for entry in current["entries"]:
            source = revision(
                c,
                ctx,
                entry["result_revision"],
                "CalculatedResult",
                "calculated-results.read",
            )
            result = dict(source["payload"])
            result.update(
                mode="OFFICIAL",
                input_snapshot_id=snapshot_id,
                run_id=run_id,
                reason_code="PERIOD_LOCKED",
                freshness={**result["freshness"], "stale": False},
                limitations=[
                    item for item in result.get("limitations", []) if item["code"] != "PERIOD_CLOSE_REQUIRED"
                ],
            )
            receipt = write(c, ctx, "CalculatedResult", result, "Official", track_author=False)
            c.execute(
                "INSERT INTO impact.lineage_edge SELECT tenant_id,%s,source_revision,contribution_identity,disposition,reason_code FROM impact.lineage_edge WHERE tenant_id=%s AND result_revision=%s",
                (receipt["revision_id"], ctx.tenant_id, entry["result_revision"]),
            )
            c.execute(
                "INSERT INTO impact.result_binding(tenant_id,result_id,indicator_id,period_id,source_digest,plan_revision) VALUES(%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    receipt["object_id"],
                    entry["indicator_id"],
                    period["object_id"],
                    entry["source_digest"],
                    entry["plan_revision"],
                ),
            )
            official.append({**receipt, "indicator_id": entry["indicator_id"]})
            definitions.append(entry["definition_revision"])
        snapshot = write(
            c,
            ctx,
            "Snapshot",
            {
                "scope_id": str(scope_id),
                "programme_id": data["programme_id"],
                "period_id": str(period["object_id"]),
                "definition_versions": sorted(set(definitions)),
                "target_versions": [],
                "result_versions": [item["revision_id"] for item in official],
                "evidence_versions": [],
                "policy_context": {
                    "policy_epoch": ctx.policy_epoch,
                    "policy_revision": str(request["head_revision"]),
                    "classification": "INTERNAL",
                    "purpose": "PERIOD_CLOSE",
                },
                "locked_at": datetime.now(timezone.utc).isoformat(),
            },
            "Locked",
            object_id=snapshot_id,
            track_author=False,
        )
        for result in official:
            c.execute(
                "INSERT INTO impact.official_result_snapshot VALUES(%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    snapshot_id,
                    result["object_id"],
                    result["revision_id"],
                    result["indicator_id"],
                    period["object_id"],
                ),
            )
        prior = self.latest_snapshot(c, ctx, data["programme_id"], period["object_id"])
        version = prior["snapshot_version"] + 1 if prior else 1
        c.execute(
            "INSERT INTO impact.period_snapshot_binding VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                data["programme_id"],
                period["object_id"],
                version,
                snapshot_id,
                snapshot["revision_id"],
                request["object_id"],
                request["head_revision"],
                prior["snapshot_id"] if prior else None,
                datetime.now(timezone.utc),
            ),
        )
        self.set_state(
            c,
            ctx,
            data["programme_id"],
            period["object_id"],
            "Locked",
            version,
        )
        c.execute(
            "UPDATE impact.job SET state='Succeeded',output_manifest=%s WHERE tenant_id=%s AND job_id=%s",
            (
                Jsonb(
                    {
                        "snapshot_id": snapshot_id,
                        "snapshot_revision": snapshot["revision_id"],
                        "official_result_revisions": [item["revision_id"] for item in official],
                    }
                ),
                ctx.tenant_id,
                run_id,
            ),
        )
        audit(c, ctx, "programme-period.locked", snapshot, correlation)
        audit(c, ctx, "snapshot.created", snapshot, correlation)
