BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.ai_extraction_draft(
 tenant_id uuid NOT NULL, draft_id uuid NOT NULL, source_object_id uuid NOT NULL, source_revision_id uuid NOT NULL,
 source_sha256 text NOT NULL CHECK(source_sha256~'^[0-9a-f]{64}$'), policy_version integer NOT NULL CHECK(policy_version>=1),
 language text NOT NULL, requested_by uuid NOT NULL, operation_id uuid NOT NULL, request_hash bytea NOT NULL,
 missing_fields jsonb NOT NULL, created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,draft_id), UNIQUE(tenant_id,requested_by,operation_id),
 FOREIGN KEY(tenant_id,source_object_id,source_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,requested_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.ai_extraction_field(
 tenant_id uuid NOT NULL, draft_id uuid NOT NULL, proposal_id uuid NOT NULL, field_key text NOT NULL,
 proposed_value text NOT NULL CHECK(length(proposed_value) BETWEEN 1 AND 2000), classification text NOT NULL CHECK(classification IN('EXTRACTED','INFERRED','SUGGESTED')),
 source_location jsonb NOT NULL, evidence_span text NOT NULL CHECK(length(evidence_span) BETWEEN 1 AND 2200), conflict boolean NOT NULL,
 PRIMARY KEY(tenant_id,proposal_id), FOREIGN KEY(tenant_id,draft_id) REFERENCES impact.ai_extraction_draft(tenant_id,draft_id)
);
CREATE TABLE impact.ai_extraction_review(
 tenant_id uuid NOT NULL, draft_id uuid NOT NULL, selected_proposal_ids jsonb NOT NULL, human_additions jsonb NOT NULL,
 unresolved_fields jsonb NOT NULL, accepted_fields jsonb NOT NULL, reviewed_by uuid NOT NULL,
 operation_id uuid NOT NULL, request_hash bytea NOT NULL, reviewed_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,draft_id), UNIQUE(tenant_id,reviewed_by,operation_id), FOREIGN KEY(tenant_id,draft_id) REFERENCES impact.ai_extraction_draft(tenant_id,draft_id),
 FOREIGN KEY(tenant_id,reviewed_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.ai_extraction_draft ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_extraction_draft FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_extraction_field ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_extraction_field FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_extraction_review ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_extraction_review FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_extraction_draft USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_extraction_field USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_extraction_review USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_extraction_draft,impact.ai_extraction_field,impact.ai_extraction_review TO impact_app;
COMMIT;
