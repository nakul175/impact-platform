BEGIN;
SET LOCAL ROLE impact_owner;
ALTER TABLE impact.ai_use_case_policy DROP CONSTRAINT ai_use_case_policy_use_case_check;
ALTER TABLE impact.ai_use_case_policy ADD CONSTRAINT ai_use_case_policy_use_case_check
 CHECK(use_case IN ('ADVISORY_DRAFT','EXTRACTION','REPORT_DRAFT','CHAT','INDICATOR_DESIGN','IMPORT_CLEANING','EVIDENCE_QUESTION','NUMERIC_ANALYSIS','QUALITATIVE_ASSISTANCE'));
CREATE TABLE impact.ai_qualitative_run(
 tenant_id uuid NOT NULL, run_id uuid NOT NULL, codebook_id uuid NOT NULL, codebook_revision_id uuid NOT NULL,
 policy_version integer NOT NULL CHECK(policy_version>=1), requested_by uuid NOT NULL, operation_id uuid NOT NULL,
 request_hash bytea NOT NULL, created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,run_id), UNIQUE(tenant_id,requested_by,operation_id),
 FOREIGN KEY(tenant_id,codebook_id,codebook_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,requested_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.ai_qualitative_suggestion(
 tenant_id uuid NOT NULL, run_id uuid NOT NULL, suggestion_id uuid NOT NULL, source_object_id uuid NOT NULL,
 source_revision_id uuid NOT NULL, source_classification text NOT NULL CHECK(source_classification IN('PUBLIC','INTERNAL','CONFIDENTIAL','RESTRICTED')),
 source_language text NOT NULL, viewpoint text NOT NULL CHECK(length(viewpoint) BETWEEN 1 AND 200),
 start_character integer NOT NULL CHECK(start_character>=0), end_character integer NOT NULL CHECK(end_character>start_character),
 excerpt text NOT NULL CHECK(length(excerpt) BETWEEN 1 AND 4000), excerpt_sha256 text NOT NULL CHECK(excerpt_sha256~'^[0-9a-f]{64}$'),
 speaker_reference text, suggested_codes jsonb NOT NULL, theme text NOT NULL CHECK(length(theme) BETWEEN 1 AND 500),
 translation_language text, translation_text text, translation_status text NOT NULL CHECK(translation_status IN('NOT_REQUESTED','MACHINE_UNREVIEWED')),
 PRIMARY KEY(tenant_id,suggestion_id),
 FOREIGN KEY(tenant_id,run_id) REFERENCES impact.ai_qualitative_run(tenant_id,run_id),
 FOREIGN KEY(tenant_id,source_object_id,source_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
CREATE TABLE impact.ai_qualitative_review(
 tenant_id uuid NOT NULL, suggestion_id uuid NOT NULL, disposition text NOT NULL CHECK(disposition IN('ACCEPTED','REJECTED')),
 final_codes jsonb NOT NULL, final_theme text, final_translation text, translation_status text NOT NULL CHECK(translation_status IN('NOT_REQUESTED','MACHINE_UNREVIEWED','HUMAN_REVIEWED')),
 qualitative_extract_id uuid, qualitative_extract_revision_id uuid, reviewed_by uuid NOT NULL, operation_id uuid NOT NULL,
 request_hash bytea NOT NULL, reviewed_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,suggestion_id), UNIQUE(tenant_id,reviewed_by,operation_id),
 FOREIGN KEY(tenant_id,suggestion_id) REFERENCES impact.ai_qualitative_suggestion(tenant_id,suggestion_id),
 FOREIGN KEY(tenant_id,qualitative_extract_id,qualitative_extract_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,reviewed_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK((disposition='ACCEPTED')=(qualitative_extract_id IS NOT NULL AND qualitative_extract_revision_id IS NOT NULL))
);
ALTER TABLE impact.ai_qualitative_run ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_qualitative_run FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_qualitative_suggestion ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_qualitative_suggestion FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_qualitative_review ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_qualitative_review FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_qualitative_run USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_qualitative_suggestion USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_qualitative_review USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_qualitative_run,impact.ai_qualitative_suggestion,impact.ai_qualitative_review TO impact_app;
COMMIT;
