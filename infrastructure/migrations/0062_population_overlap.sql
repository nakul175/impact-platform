BEGIN;
SET LOCAL ROLE impact_owner;
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type IN (''PopulationMatchingScope'',''PopulationReachResult''))');
END $$;
CREATE TABLE impact.population_matching_scope_current(
 tenant_id uuid NOT NULL,
 object_id uuid NOT NULL,
 revision_id uuid NOT NULL,
 object_type text GENERATED ALWAYS AS ('PopulationMatchingScope') STORED,
 title varchar(200) NOT NULL,
 entity_type varchar(80) NOT NULL,
 population text NOT NULL,
 project_id uuid NOT NULL,
 window_start timestamptz NOT NULL,
 window_end timestamptz NOT NULL,
 matching_method varchar(64) NOT NULL CHECK(matching_method='EXACT_STABLE_PSEUDONYM'),
 PRIMARY KEY(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
 CHECK(window_start<window_end)
);
ALTER TABLE impact.population_matching_scope_current ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.population_matching_scope_current FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.population_matching_scope_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.population_matching_scope_current TO impact_app;
CREATE POLICY population_identity_registry_worker_fence ON impact.object_registry AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type NOT IN ('PopulationMatchingScope','PopulationReachResult'));
CREATE POLICY population_identity_revision_worker_fence ON impact.object_revision AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type NOT IN ('PopulationMatchingScope','PopulationReachResult'));
COMMIT;
