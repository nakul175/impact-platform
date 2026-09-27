BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.calculation_invalidation(
  tenant_id uuid NOT NULL,
  invalidation_id uuid NOT NULL,
  result_id uuid NOT NULL,
  result_revision uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  triggering_revision uuid NOT NULL,
  reason_code text NOT NULL CHECK(reason_code IN ('SOURCE_APPROVED','SOURCE_CORRECTED','PLAN_APPROVED','PLAN_AMENDED')),
  work_item_id uuid NOT NULL,
  state text NOT NULL CHECK(state IN ('PENDING','RECALCULATED','CANCELLED')),
  created_at timestamptz NOT NULL,
  resolved_at timestamptz,
  replacement_result_id uuid,
  PRIMARY KEY(tenant_id,invalidation_id),
  UNIQUE(tenant_id,result_revision,triggering_revision),
  FOREIGN KEY(tenant_id,result_id,result_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,triggering_revision) REFERENCES impact.object_revision(tenant_id,revision_id),
  FOREIGN KEY(tenant_id,work_item_id) REFERENCES impact.work_item_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,replacement_result_id) REFERENCES impact.calculated_result_current(tenant_id,object_id),
  CHECK((state='PENDING' AND resolved_at IS NULL AND replacement_result_id IS NULL)
    OR (state='RECALCULATED' AND resolved_at IS NOT NULL AND replacement_result_id IS NOT NULL)
    OR (state='CANCELLED' AND resolved_at IS NOT NULL AND replacement_result_id IS NULL))
);

CREATE INDEX calculation_invalidation_pending
  ON impact.calculation_invalidation(tenant_id,indicator_id,period_id)
  WHERE state='PENDING';

CREATE TABLE impact.notification_acknowledgement(
  tenant_id uuid NOT NULL,
  notification_id uuid NOT NULL,
  recipient_id uuid NOT NULL,
  acknowledged_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,notification_id),
  FOREIGN KEY(tenant_id,notification_id) REFERENCES impact.notification_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,recipient_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);

ALTER TABLE impact.calculation_invalidation ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.calculation_invalidation FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.notification_acknowledgement ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.notification_acknowledgement FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_fence ON impact.calculation_invalidation
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.notification_acknowledgement
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT ON impact.calculation_invalidation TO impact_app;
GRANT UPDATE(state,resolved_at,replacement_result_id) ON impact.calculation_invalidation TO impact_app;
GRANT SELECT,INSERT ON impact.notification_acknowledgement TO impact_app;

COMMIT;
