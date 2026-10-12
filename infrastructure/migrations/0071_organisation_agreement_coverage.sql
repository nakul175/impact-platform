BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.organisation_agreement_revision(
 tenant_id uuid NOT NULL, revision_id uuid NOT NULL,
 master_agreement_reference text NOT NULL CHECK(length(master_agreement_reference)>0),
 dpa_reference text NOT NULL CHECK(length(dpa_reference)>0),
 effective_on date NOT NULL,
 coverage_scope varchar(32) NOT NULL CHECK(coverage_scope='ALL_PLATFORM_SOLUTIONS'),
 partner_terms_mode varchar(40) NOT NULL CHECK(partner_terms_mode='MASTER_AGREEMENT_FLOW_DOWN'),
 created_by uuid NOT NULL, created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,revision_id),
 FOREIGN KEY(tenant_id,created_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.organisation_agreement_current(
 tenant_id uuid PRIMARY KEY, revision_id uuid NOT NULL,
 FOREIGN KEY(tenant_id,revision_id) REFERENCES impact.organisation_agreement_revision(tenant_id,revision_id)
);
CREATE TABLE impact.solution_agreement_coverage(
 tenant_id uuid NOT NULL, deployment_attestation_id uuid NOT NULL,
 plan_id uuid NOT NULL, solution_id varchar(100) NOT NULL,
 agreement_revision_id uuid NOT NULL,
 partner_terms_mode varchar(40) NOT NULL CHECK(partner_terms_mode='MASTER_AGREEMENT_FLOW_DOWN'),
 separate_contract_required boolean NOT NULL CHECK(separate_contract_required=false),
 separate_dpa_required boolean NOT NULL CHECK(separate_dpa_required=false),
 recorded_by uuid NOT NULL, recorded_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,deployment_attestation_id),
 FOREIGN KEY(tenant_id,plan_id) REFERENCES impact.object_registry(tenant_id,object_id),
 FOREIGN KEY(tenant_id,agreement_revision_id) REFERENCES impact.organisation_agreement_revision(tenant_id,revision_id),
 FOREIGN KEY(tenant_id,recorded_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
DO $$ DECLARE table_name text; BEGIN
 FOREACH table_name IN ARRAY ARRAY['organisation_agreement_revision','organisation_agreement_current','solution_agreement_coverage'] LOOP
  EXECUTE format('ALTER TABLE impact.%I ENABLE ROW LEVEL SECURITY',table_name);
  EXECUTE format('ALTER TABLE impact.%I FORCE ROW LEVEL SECURITY',table_name);
  EXECUTE format('CREATE POLICY tenant_fence ON impact.%I USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant())',table_name);
  EXECUTE format('GRANT SELECT,INSERT ON impact.%I TO impact_app',table_name);
 END LOOP;
END $$;
GRANT UPDATE(revision_id) ON impact.organisation_agreement_current TO impact_app;

COMMIT;
