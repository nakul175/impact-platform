BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.ai_safety_feedback(
 tenant_id uuid NOT NULL, feedback_id uuid NOT NULL, output_kind text NOT NULL CHECK(output_kind IN('ADVISORY','ADVISORY_JOB','FORECAST')),
 output_id uuid NOT NULL, category text NOT NULL CHECK(category IN('SENSITIVE_CITATION','HARMFUL_CONTENT','UNSUPPORTED_CLAIM','UNAUTHORISED_ACTION','OTHER')),
 safe_detail text NOT NULL CHECK(length(safe_detail) BETWEEN 1 AND 1000), submitted_by uuid NOT NULL, reviewer_id uuid NOT NULL,
 submitted_at timestamptz NOT NULL, PRIMARY KEY(tenant_id,feedback_id),
 FOREIGN KEY(tenant_id,submitted_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,reviewer_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.ai_shutdown_event(
 tenant_id uuid NOT NULL, event_id uuid NOT NULL, sequence bigint GENERATED ALWAYS AS IDENTITY,
 scope_kind text NOT NULL CHECK(scope_kind IN('USE_CASE','CONFIGURATION','DESTINATION')),
 scope_value text NOT NULL CHECK(length(scope_value) BETWEEN 1 AND 300), action text NOT NULL CHECK(action IN('DISABLE','REENABLE')),
 reason_category text NOT NULL CHECK(reason_category IN('SENSITIVE_CITATION','HARMFUL_CONTENT','UNSUPPORTED_CLAIM','UNAUTHORISED_ACTION','OTHER','FIX_VERIFIED')),
 fix_evidence_object_id uuid, fix_evidence_revision_id uuid, regression_approved_by uuid, actor_id uuid NOT NULL, occurred_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,event_id), UNIQUE(tenant_id,sequence),
 FOREIGN KEY(tenant_id,fix_evidence_object_id,fix_evidence_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,regression_approved_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,actor_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK((action='DISABLE' AND fix_evidence_object_id IS NULL AND fix_evidence_revision_id IS NULL AND regression_approved_by IS NULL)
    OR (action='REENABLE' AND fix_evidence_object_id IS NOT NULL AND fix_evidence_revision_id IS NOT NULL AND regression_approved_by IS NOT NULL AND reason_category='FIX_VERIFIED'))
);
CREATE TABLE impact.ai_shutdown_recovery_approval(
 tenant_id uuid NOT NULL, shutdown_event_id uuid NOT NULL, fix_evidence_object_id uuid NOT NULL,
 fix_evidence_revision_id uuid NOT NULL, approved_by uuid NOT NULL, approved_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,shutdown_event_id),
 FOREIGN KEY(tenant_id,shutdown_event_id) REFERENCES impact.ai_shutdown_event(tenant_id,event_id),
 FOREIGN KEY(tenant_id,fix_evidence_object_id,fix_evidence_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,approved_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.ai_safety_feedback ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_safety_feedback FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_shutdown_event ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_shutdown_event FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_shutdown_recovery_approval ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_shutdown_recovery_approval FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_safety_feedback USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_shutdown_event USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_shutdown_recovery_approval USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_safety_feedback,impact.ai_shutdown_event,impact.ai_shutdown_recovery_approval TO impact_app;
GRANT SELECT ON impact.ai_shutdown_event TO impact_worker;
GRANT USAGE,SELECT ON SEQUENCE impact.ai_shutdown_event_sequence_seq TO impact_app;
COMMIT;
