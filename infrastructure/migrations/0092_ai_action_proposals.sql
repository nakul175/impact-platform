BEGIN;
SET LOCAL ROLE impact_owner;
ALTER TABLE impact.ai_use_case_policy DROP CONSTRAINT ai_use_case_policy_use_case_check;
ALTER TABLE impact.ai_use_case_policy ADD CONSTRAINT ai_use_case_policy_use_case_check
 CHECK(use_case IN ('ADVISORY_DRAFT','EXTRACTION','REPORT_DRAFT','CHAT','INDICATOR_DESIGN','IMPORT_CLEANING','EVIDENCE_QUESTION','NUMERIC_ANALYSIS','QUALITATIVE_ASSISTANCE','PROACTIVE_FINDINGS','ACTION_PROPOSAL'));
CREATE TABLE impact.ai_action_proposal(
 tenant_id uuid NOT NULL, proposal_id uuid NOT NULL, command_type text NOT NULL CHECK(command_type='CREATE_WORK_ITEM_DRAFT'),
 scope_object_id uuid NOT NULL, scope_revision_id uuid NOT NULL, before_values jsonb NOT NULL,
 after_values jsonb NOT NULL CHECK(jsonb_typeof(after_values)='object'), consequences jsonb NOT NULL CHECK(jsonb_typeof(consequences)='array'),
 policy_version integer NOT NULL CHECK(policy_version>=1), execution_operation_id uuid NOT NULL,
 generated_by uuid NOT NULL, operation_id uuid NOT NULL, request_hash bytea NOT NULL, generated_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,proposal_id), UNIQUE(tenant_id,generated_by,operation_id), UNIQUE(tenant_id,execution_operation_id),
 FOREIGN KEY(tenant_id,scope_object_id,scope_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,generated_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK(before_values='null'::jsonb)
);
CREATE TABLE impact.ai_action_proposal_source(
 tenant_id uuid NOT NULL, proposal_id uuid NOT NULL, object_id uuid NOT NULL, revision_id uuid NOT NULL, object_type text NOT NULL CHECK(object_type IN('Evidence','CalculatedResult')),
 PRIMARY KEY(tenant_id,proposal_id,revision_id),
 FOREIGN KEY(tenant_id,proposal_id) REFERENCES impact.ai_action_proposal(tenant_id,proposal_id),
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
CREATE TABLE impact.ai_action_confirmation(
 tenant_id uuid NOT NULL, proposal_id uuid NOT NULL, confirmation_operation_id uuid NOT NULL,
 confirmation_hash bytea NOT NULL, confirmed_by uuid NOT NULL, outcome_object_id uuid NOT NULL,
 outcome_revision_id uuid NOT NULL, confirmed_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,proposal_id), UNIQUE(tenant_id,confirmed_by,confirmation_operation_id),
 FOREIGN KEY(tenant_id,proposal_id) REFERENCES impact.ai_action_proposal(tenant_id,proposal_id),
 FOREIGN KEY(tenant_id,confirmed_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,outcome_object_id,outcome_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
ALTER TABLE impact.ai_action_proposal ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_action_proposal FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_action_proposal_source ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_action_proposal_source FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_action_confirmation ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_action_confirmation FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_action_proposal USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_action_proposal_source USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_action_confirmation USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_action_proposal,impact.ai_action_proposal_source,impact.ai_action_confirmation TO impact_app;
COMMIT;
