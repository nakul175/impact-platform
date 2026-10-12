BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.ai_option_trial(
 tenant_id uuid NOT NULL, trial_id uuid NOT NULL,
 opportunity_id varchar(120) NOT NULL, solution_id varchar(120) NOT NULL,
 catalogue_content_version varchar(100) NOT NULL,
 starts_on date NOT NULL, ends_on date NOT NULL, duration_days integer NOT NULL CHECK(duration_days BETWEEN 1 AND 28),
 data_mode varchar(16) NOT NULL CHECK(data_mode IN ('OWN_EVIDENCE','SAMPLE')),
 evidence_object_id uuid, evidence_revision_id uuid,
 sample_id varchar(64), success_criteria text NOT NULL CHECK(length(success_criteria)>0),
 advisor_principal_id uuid NOT NULL, advisor_membership_id uuid NOT NULL,
 advisor_natural_identity_id uuid NOT NULL REFERENCES impact.natural_person,
 created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,trial_id),
 FOREIGN KEY(tenant_id,evidence_object_id) REFERENCES impact.object_registry(tenant_id,object_id),
 FOREIGN KEY(tenant_id,evidence_object_id,evidence_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,advisor_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,advisor_membership_id) REFERENCES impact.membership_current(tenant_id,object_id),
 CHECK(ends_on=starts_on+duration_days AND ends_on<=starts_on+28),
 CHECK(
  (data_mode='OWN_EVIDENCE' AND evidence_object_id IS NOT NULL AND evidence_revision_id IS NOT NULL AND sample_id IS NULL)
  OR
  (data_mode='SAMPLE' AND evidence_object_id IS NULL AND evidence_revision_id IS NULL AND sample_id='SYNTHETIC_TABULAR_V1')
 )
);
ALTER TABLE impact.ai_option_trial ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_option_trial FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_option_trial
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_option_trial TO impact_app;

COMMIT;
