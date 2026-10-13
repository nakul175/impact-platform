BEGIN;
SET LOCAL ROLE impact_owner;
ALTER TABLE impact.ai_use_case_policy DROP CONSTRAINT ai_use_case_policy_use_case_check;
ALTER TABLE impact.ai_use_case_policy ADD CONSTRAINT ai_use_case_policy_use_case_check
 CHECK(use_case IN ('ADVISORY_DRAFT','EXTRACTION','REPORT_DRAFT','CHAT','INDICATOR_DESIGN','IMPORT_CLEANING','EVIDENCE_QUESTION','NUMERIC_ANALYSIS','QUALITATIVE_ASSISTANCE','PROACTIVE_FINDINGS'));
CREATE TABLE impact.ai_detection_task(
 tenant_id uuid NOT NULL, task_id uuid NOT NULL, task_code text NOT NULL CHECK(task_code~'^[A-Z][A-Z0-9_]{2,63}$'),
 scope_object_id uuid NOT NULL, scope_revision_id uuid NOT NULL, owner_principal_id uuid NOT NULL,
 cooldown_seconds integer NOT NULL CHECK(cooldown_seconds BETWEEN 60 AND 2592000),
 noise_limit integer NOT NULL CHECK(noise_limit BETWEEN 1 AND 100), enabled boolean NOT NULL,
 policy_version integer NOT NULL CHECK(policy_version>=1), created_by uuid NOT NULL, operation_id uuid NOT NULL,
 request_hash bytea NOT NULL, created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,task_id), UNIQUE(tenant_id,created_by,operation_id),
 FOREIGN KEY(tenant_id,scope_object_id,scope_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,owner_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,created_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.ai_suggested_finding(
 tenant_id uuid NOT NULL, suggestion_id uuid NOT NULL, task_id uuid NOT NULL, detection_event_key text NOT NULL CHECK(length(detection_event_key) BETWEEN 1 AND 200),
 affected_result_revisions jsonb NOT NULL CHECK(jsonb_typeof(affected_result_revisions)='array'),
 evidence_revisions jsonb NOT NULL CHECK(jsonb_typeof(evidence_revisions)='array'),
 summary text NOT NULL CHECK(length(summary) BETWEEN 1 AND 500), limitation text NOT NULL CHECK(length(limitation) BETWEEN 1 AND 1000),
 proposed_follow_up text NOT NULL CHECK(length(proposed_follow_up) BETWEEN 1 AND 1000),
 owner_principal_id uuid NOT NULL, status text NOT NULL DEFAULT 'SUGGESTED' CHECK(status='SUGGESTED'),
 created_by uuid NOT NULL, operation_id uuid NOT NULL, request_hash bytea NOT NULL, created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,suggestion_id), UNIQUE(tenant_id,task_id,detection_event_key), UNIQUE(tenant_id,created_by,operation_id),
 FOREIGN KEY(tenant_id,task_id) REFERENCES impact.ai_detection_task(tenant_id,task_id),
 FOREIGN KEY(tenant_id,owner_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,created_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.ai_finding_feedback(
 tenant_id uuid NOT NULL, suggestion_id uuid NOT NULL, decision text NOT NULL CHECK(decision IN('VERIFIED','DISMISSED','ASSIGNED')),
 reason text NOT NULL CHECK(length(reason) BETWEEN 1 AND 1000), assigned_to uuid,
 reviewed_by uuid NOT NULL, operation_id uuid NOT NULL, request_hash bytea NOT NULL, reviewed_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,suggestion_id), UNIQUE(tenant_id,reviewed_by,operation_id),
 FOREIGN KEY(tenant_id,suggestion_id) REFERENCES impact.ai_suggested_finding(tenant_id,suggestion_id),
 FOREIGN KEY(tenant_id,assigned_to) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,reviewed_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK((decision='ASSIGNED')=(assigned_to IS NOT NULL))
);
CREATE TABLE impact.ai_suggested_finding_result(
 tenant_id uuid NOT NULL, suggestion_id uuid NOT NULL, object_id uuid NOT NULL, revision_id uuid NOT NULL,
 PRIMARY KEY(tenant_id,suggestion_id,revision_id),
 FOREIGN KEY(tenant_id,suggestion_id) REFERENCES impact.ai_suggested_finding(tenant_id,suggestion_id),
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
CREATE TABLE impact.ai_suggested_finding_evidence(
 tenant_id uuid NOT NULL, suggestion_id uuid NOT NULL, object_id uuid NOT NULL, revision_id uuid NOT NULL,
 PRIMARY KEY(tenant_id,suggestion_id,revision_id),
 FOREIGN KEY(tenant_id,suggestion_id) REFERENCES impact.ai_suggested_finding(tenant_id,suggestion_id),
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
ALTER TABLE impact.ai_detection_task ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_detection_task FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_suggested_finding ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_suggested_finding FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_finding_feedback ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_finding_feedback FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_suggested_finding_result ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_suggested_finding_result FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_suggested_finding_evidence ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_suggested_finding_evidence FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_detection_task USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_suggested_finding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_finding_feedback USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_suggested_finding_result USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_suggested_finding_evidence USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_detection_task,impact.ai_suggested_finding,impact.ai_finding_feedback,impact.ai_suggested_finding_result,impact.ai_suggested_finding_evidence TO impact_app;
COMMIT;
