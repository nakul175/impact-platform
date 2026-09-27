BEGIN;
SET LOCAL ROLE impact_owner;
-- Preserve every original registry kind, adding a separate plan aggregate. Job schedules are unchanged.
DO $$
DECLARE original_check text;
BEGIN
  SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
    WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
  ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
  EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
    || regexp_replace(original_check, '\)$', ' OR object_type = ''CollectionPlan'')');
END $$;
ALTER TABLE impact.indicator_definition_current ADD COLUMN numerator_meaning text;
ALTER TABLE impact.indicator_definition_current ADD COLUMN denominator_meaning text;
CREATE TABLE impact.collection_plan_binding(
  tenant_id uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  plan_id uuid NOT NULL,
  plan_revision uuid NOT NULL,
  PRIMARY KEY(tenant_id,indicator_id,period_id),
  UNIQUE(tenant_id,plan_id),
  FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,plan_id,plan_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
ALTER TABLE impact.collection_plan_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.collection_plan_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.collection_plan_binding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.collection_plan_binding TO impact_app;
ALTER TABLE impact.result_binding ADD COLUMN plan_revision uuid;
ALTER TABLE impact.result_binding ADD FOREIGN KEY(tenant_id,plan_revision) REFERENCES impact.object_revision(tenant_id,revision_id);
COMMIT;
