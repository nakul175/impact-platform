BEGIN;
SET LOCAL ROLE impact_owner;
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check ' || regexp_replace(original_check, '\)$', ' OR object_type = ''DimensionCrosswalk'')');
END $$;
CREATE TABLE impact.dimension_crosswalk_current(
 tenant_id uuid NOT NULL, object_id uuid NOT NULL, revision_id uuid NOT NULL,
 object_type text GENERATED ALWAYS AS ('DimensionCrosswalk') STORED,
 title varchar(200) NOT NULL, source_definition_revision uuid NOT NULL, source_dimension_code varchar(64) NOT NULL,
 target_definition_revision uuid NOT NULL, target_dimension_code varchar(64) NOT NULL,
 mapping_type varchar(32) NOT NULL CHECK(mapping_type IN ('EXACT','MANY_TO_ONE','PROPORTIONAL')),
 information_loss varchar(32) NOT NULL CHECK(information_loss IN ('NONE','POOLING','ESTIMATED')),
 estimation_method text, mappings jsonb NOT NULL CHECK(jsonb_typeof(mappings)='array'),
 source_kind text GENERATED ALWAYS AS ('IndicatorDefinition') STORED, target_kind text GENERATED ALWAYS AS ('IndicatorDefinition') STORED,
 PRIMARY KEY(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,source_definition_revision,source_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,target_definition_revision,target_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED
);
ALTER TABLE impact.dimension_crosswalk_current ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.dimension_crosswalk_current FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.dimension_crosswalk_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.dimension_crosswalk_current TO impact_app;
CREATE POLICY crosswalk_registry_worker_fence ON impact.object_registry AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type<>'DimensionCrosswalk');
CREATE POLICY crosswalk_revision_worker_fence ON impact.object_revision AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type<>'DimensionCrosswalk');
COMMIT;
