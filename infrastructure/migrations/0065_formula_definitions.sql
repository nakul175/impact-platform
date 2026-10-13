BEGIN;
SET LOCAL ROLE impact_owner;
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check ' || regexp_replace(original_check, '\)$', ' OR object_type = ''FormulaDefinition'')');
END $$;
CREATE TABLE impact.formula_definition_current(
 tenant_id uuid NOT NULL, object_id uuid NOT NULL, revision_id uuid NOT NULL,
 object_type text GENERATED ALWAYS AS ('FormulaDefinition') STORED,
 title varchar(200) NOT NULL, target_definition_id uuid NOT NULL,
 target_kind text GENERATED ALWAYS AS ('IndicatorDefinition') STORED,
 output_unit varchar(64) NOT NULL, ast jsonb NOT NULL CHECK(jsonb_typeof(ast)='object'),
 PRIMARY KEY(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,target_definition_id,target_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED
);
ALTER TABLE impact.formula_definition_current ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.formula_definition_current FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.formula_definition_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.formula_definition_current TO impact_app;
CREATE POLICY formula_registry_worker_fence ON impact.object_registry AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type<>'FormulaDefinition');
CREATE POLICY formula_revision_worker_fence ON impact.object_revision AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type<>'FormulaDefinition');
COMMIT;
