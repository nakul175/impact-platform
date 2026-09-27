"""Proposals never replace effective data until their independent approval commits."""

from .contracts import validate
from .domain import DomainError, decimal_value, unavailable
from .measurement import valid_value
from .store import load, scopes, write, audit

TARGETS = {
    "Observation": ("observations", "Approved", "observations.draft.edit"),
    "CollectionPlan": ("collection-plans", "Approved", "collection-plans.draft.edit"),
    "IndicatorInstance": ("indicator-instances", "Active", "indicator-instances.draft.edit"),
}


class Changes:
    def __init__(self, service):
        self.service = service

    def validate(self, c, ctx, data, proposing=True):
        from .service import revision

        validate("MeasurementChangeData", data)
        kind = data["target_kind"]
        route, state, capability = TARGETS[kind]
        row = load(c, ctx, data["target_id"], kind, route + ".read")
        if proposing and not scopes(c, ctx, capability, row["object_id"]):
            unavailable()
        if str(row["head_revision"]) != data["target_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="AMENDMENT_TARGET_CHANGED")
        if row["lifecycle_state"] != state:
            raise DomainError("INVALID_STATE", 409, reason="APPROVED_TARGET_REQUIRED")
        merged = {**row["payload"], **data["proposed_data"]}
        if merged == row["payload"]:
            raise DomainError("VALIDATION_FAILED", reason="NO_CHANGE")
        self.service.validate_data(c, ctx, kind, merged)
        measurement = self.service.measurement
        if kind == "CollectionPlan":
            # Removal would falsely improve coverage without separately reviewed exclusion evidence.
            old = {(o["source_namespace"], o["source_key"]) for o in row["payload"]["obligations"]}
            new = {(o["source_namespace"], o["source_key"]) for o in merged["obligations"]}
            if not old <= new:
                raise DomainError("VALIDATION_FAILED", reason="OBLIGATION_REMOVAL_REQUIRES_EXCLUSION")
            measurement.validate_plan(c, ctx, merged, complete=True, approved=True)
        elif kind == "Observation":
            indicator = load(c, ctx, merged["indicator_id"], "IndicatorInstance", "indicator-instances.read")
            programme = load(c, ctx, indicator["payload"]["programme_id"], "Programme", "programmes.read")
            if indicator["lifecycle_state"] != "Active" or programme["lifecycle_state"] != "Active":
                raise DomainError("INVALID_STATE", 409, reason="ACTIVE_MEASUREMENT_REQUIRED")
            self.service.periods.assert_source_mutable(
                c, ctx, merged["indicator_id"], merged["event_at"], row["object_id"]
            )
            definition = revision(
                c,
                ctx,
                indicator["payload"]["definition_version"],
                "IndicatorDefinition",
                "indicator-definitions.read",
            )["payload"]
            if merged["value_state"] == "PRESENT" and not valid_value(definition, merged):
                raise DomainError("VALIDATION_FAILED", reason="INVALID_MEASUREMENT_VALUE")
            if definition["measurement_type"] == "PERCENTAGE" and merged["value_state"] == "PRESENT":
                if decimal_value(merged["numerator"]) > decimal_value(merged["denominator"]):
                    raise DomainError("VALIDATION_FAILED", reason="INVALID_COMPONENTS")
        else:
            # Validate assignments against live identities, capabilities and the approved measurement setup.
            measurement.indicator_ready(c, ctx, {**row, "payload": merged})
        return row, merged

    def protect_authors(self, c, ctx, proposal, workflow, candidate_revision):
        c.execute(
            "INSERT INTO impact.workflow_author SELECT tenant_id,%s,natural_identity_id,%s FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s ON CONFLICT DO NOTHING",
            (workflow, candidate_revision, ctx.tenant_id, proposal["target_id"]),
        )

    def apply(self, c, ctx, proposal, correlation):
        data = proposal["payload"]
        row, merged = self.validate(c, ctx, data, proposing=False)
        if data["target_kind"] == "IndicatorInstance":
            for field in ["collector_id", "reviewer_id"]:
                natural = c.execute(
                    "SELECT impact.member_natural_identity(%s,%s) AS person", (ctx.tenant_id, merged[field])
                ).fetchone()["person"]
                if str(natural) == str(ctx.identity.natural_identity_id):
                    raise DomainError("POLICY_DENIED", 403, reason="ASSIGNMENT_RECIPIENT_CANNOT_APPROVE")
        effect = write(c, ctx, data["target_kind"], merged, row["lifecycle_state"], row, track_author=False)
        audit(c, ctx, "measurement.change.applied", effect, correlation)
        # The approving reviewer does not become a content author; proposal authors do.
        c.execute(
            "INSERT INTO impact.object_natural_author SELECT tenant_id,%s,natural_identity_id FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s ON CONFLICT DO NOTHING",
            (row["object_id"], ctx.tenant_id, proposal["object_id"]),
        )
        if data["target_kind"] == "CollectionPlan":
            c.execute(
                "UPDATE impact.collection_plan_binding SET plan_revision=%s WHERE tenant_id=%s AND plan_id=%s",
                (effect["revision_id"], ctx.tenant_id, row["object_id"]),
            )
            self.service.work.invalidate(
                c,
                ctx,
                merged["indicator_id"],
                merged["period_id"],
                effect["revision_id"],
                "PLAN_AMENDED",
                correlation,
            )
        elif data["target_kind"] == "Observation":
            self.service.work.invalidate_observation(
                c,
                ctx,
                merged,
                effect["revision_id"],
                "SOURCE_CORRECTED",
                correlation,
            )
        if (
            data["target_kind"] == "IndicatorInstance"
            and merged["reviewer_id"] != row["payload"]["reviewer_id"]
        ):
            member = self.service.measurement.principal(c, ctx, merged["reviewer_id"])
            pending = c.execute(
                "SELECT w.object_id FROM impact.workflow_current w JOIN impact.object_registry r ON r.tenant_id=w.tenant_id AND r.object_id=w.object_id JOIN impact.observation_current o ON o.tenant_id=w.tenant_id AND o.object_id=w.candidate_id WHERE w.tenant_id=%s AND o.indicator_id=%s AND r.lifecycle_state='InReview' ORDER BY w.object_id LIMIT 501",
                (ctx.tenant_id, row["object_id"]),
            ).fetchall()
            if len(pending) > 500:
                raise DomainError("LIMIT_EXCEEDED", 422)
            for item in pending:
                workflow = load(c, ctx, item["object_id"], "Workflow", "workflows.read")
                payload = workflow["payload"]
                conflict = c.execute(
                    "SELECT 1 FROM impact.workflow_author WHERE tenant_id=%s AND workflow_id=%s AND candidate_revision=%s AND natural_identity_id=impact.member_natural_identity(%s,%s)",
                    (
                        ctx.tenant_id,
                        item["object_id"],
                        payload["candidate_revision"],
                        ctx.tenant_id,
                        merged["reviewer_id"],
                    ),
                ).fetchone()
                if conflict:
                    raise DomainError("VALIDATION_FAILED", reason="REASSIGNMENT_INDEPENDENCE_CONFLICT")
                if len(payload["stages"]) != 1:
                    raise DomainError("INVALID_STATE", 409, reason="UNSUPPORTED_WORKFLOW")
                payload["stages"][0]["candidate_membership_ids"] = [str(member["membership_id"])]
                write(c, ctx, "Workflow", payload, "InReview", workflow, track_author=False)
        c.execute(
            "INSERT INTO impact.measurement_change_effect VALUES(%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                proposal["object_id"],
                row["object_id"],
                row["head_revision"],
                effect["revision_id"],
            ),
        )
