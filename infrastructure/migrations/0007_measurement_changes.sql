BEGIN;
SET LOCAL ROLE impact_owner;
DO $$
DECLARE original_check text;
BEGIN
  SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
    WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
  ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
  EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
    || regexp_replace(original_check, '\)$', ' OR object_type = ''MeasurementChange'')');
END $$;
CREATE TABLE impact.measurement_change_effect (
  tenant_id uuid NOT NULL,
  change_id uuid NOT NULL,
  target_id uuid NOT NULL,
  before_revision uuid NOT NULL,
  after_revision uuid NOT NULL,
  PRIMARY KEY(tenant_id,change_id),
  FOREIGN KEY(tenant_id,change_id) REFERENCES impact.object_registry(tenant_id,object_id),
  FOREIGN KEY(tenant_id,target_id,before_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,target_id,after_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
ALTER TABLE impact.measurement_change_effect ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.measurement_change_effect FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.measurement_change_effect
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.measurement_change_effect TO impact_app;
GRANT UPDATE(plan_revision) ON impact.collection_plan_binding TO impact_app;
COMMIT;
