BEGIN;
SET LOCAL ROLE impact_owner;
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check ' || regexp_replace(original_check, '\)$', ' OR object_type = ''PortfolioAllocationView'')');
END $$;
CREATE TABLE impact.portfolio_allocation_view_current(
 tenant_id uuid NOT NULL, object_id uuid NOT NULL, revision_id uuid NOT NULL,
 object_type text GENERATED ALWAYS AS ('PortfolioAllocationView') STORED,
 title varchar(200) NOT NULL, portfolios jsonb NOT NULL CHECK(jsonb_typeof(portfolios)='array'),
 allocations jsonb NOT NULL CHECK(jsonb_typeof(allocations)='array'), remainder_policy varchar(64) NOT NULL,
 nonadditive boolean NOT NULL, nonadditive_label varchar(500),
 PRIMARY KEY(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);
ALTER TABLE impact.portfolio_allocation_view_current ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.portfolio_allocation_view_current FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.portfolio_allocation_view_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.portfolio_allocation_view_current TO impact_app;
CREATE POLICY portfolio_allocation_registry_worker_fence ON impact.object_registry AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type<>'PortfolioAllocationView');
CREATE POLICY portfolio_allocation_revision_worker_fence ON impact.object_revision AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type<>'PortfolioAllocationView');
COMMIT;
