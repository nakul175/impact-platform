BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.calculation_invalidation_dependency(
  tenant_id uuid NOT NULL,
  invalidation_id uuid NOT NULL,
  dependency_type text NOT NULL CHECK(dependency_type IN ('RESULT','LIVE_DASHBOARD','UNPUBLISHED_REPORT')),
  object_id uuid NOT NULL,
  revision_id uuid NOT NULL,
  recorded_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,invalidation_id,dependency_type,object_id,revision_id),
  FOREIGN KEY(tenant_id,invalidation_id) REFERENCES impact.calculation_invalidation(tenant_id,invalidation_id),
  FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);

ALTER TABLE impact.calculation_invalidation_dependency ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.calculation_invalidation_dependency FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.calculation_invalidation_dependency
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.calculation_invalidation_dependency TO impact_app;

COMMIT;
