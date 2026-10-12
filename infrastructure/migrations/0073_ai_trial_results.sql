BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.ai_trial_result(
 tenant_id uuid NOT NULL, result_id uuid NOT NULL, trial_id uuid NOT NULL,
 opportunity_id varchar(120) NOT NULL,
 result_source jsonb NOT NULL CHECK(jsonb_typeof(result_source)='object'),
 evidence_object_id uuid, evidence_revision_id uuid,
 recorded_by uuid NOT NULL, recorded_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,result_id), UNIQUE(tenant_id,trial_id),
 FOREIGN KEY(tenant_id,trial_id) REFERENCES impact.ai_option_trial(tenant_id,trial_id),
 FOREIGN KEY(tenant_id,evidence_object_id,evidence_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,recorded_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK((evidence_object_id IS NULL)=(evidence_revision_id IS NULL))
);
ALTER TABLE impact.ai_trial_result ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_trial_result FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_trial_result
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_trial_result TO impact_app;
COMMIT;
