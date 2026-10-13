BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.ai_report_draft(
 tenant_id uuid NOT NULL, draft_id uuid NOT NULL, snapshot_id uuid NOT NULL, snapshot_revision_id uuid NOT NULL,
 template_revision_id uuid NOT NULL, policy_version integer NOT NULL CHECK(policy_version>=1), language text NOT NULL,
 requested_by uuid NOT NULL, operation_id uuid NOT NULL, request_hash bytea NOT NULL, generation integer NOT NULL CHECK(generation>=1),
 prior_draft_id uuid, regenerated_section_codes jsonb NOT NULL, proposed_sections jsonb NOT NULL, evidence_gaps jsonb NOT NULL,
 mandatory_caveat_codes jsonb NOT NULL, created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,draft_id), UNIQUE(tenant_id,requested_by,operation_id),
 FOREIGN KEY(tenant_id,snapshot_id,snapshot_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,template_revision_id) REFERENCES impact.object_revision(tenant_id,revision_id),
 FOREIGN KEY(tenant_id,requested_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,prior_draft_id) REFERENCES impact.ai_report_draft(tenant_id,draft_id)
);
CREATE TABLE impact.ai_report_draft_review(
 tenant_id uuid NOT NULL, draft_id uuid NOT NULL, corrections jsonb NOT NULL, final_sections jsonb NOT NULL,
 mandatory_caveat_codes jsonb NOT NULL, reviewed_by uuid NOT NULL, operation_id uuid NOT NULL,
 request_hash bytea NOT NULL, reviewed_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,draft_id), UNIQUE(tenant_id,reviewed_by,operation_id),
 FOREIGN KEY(tenant_id,draft_id) REFERENCES impact.ai_report_draft(tenant_id,draft_id),
 FOREIGN KEY(tenant_id,reviewed_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.ai_report_draft ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_report_draft FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_report_draft_review ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_report_draft_review FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_report_draft USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_report_draft_review USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_report_draft,impact.ai_report_draft_review TO impact_app;
COMMIT;
