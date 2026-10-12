-- Governed, scoped contributions to one existing diagnosis.
BEGIN;
SET LOCAL ROLE impact_owner;

-- Registered for governed future/bootstrap upgrades only. Existing tenants are
-- not widened or auto-activated by this migration.
WITH previous AS (
 SELECT manifest FROM impact.platform_access_profile
 WHERE source_migration='0048_ai_problem_baselines.sql'
), first_roles AS (
 SELECT jsonb_set(
  jsonb_set(
   jsonb_set(previous.manifest,'{roles,TENANT_ADMIN}',
    (SELECT jsonb_agg(to_jsonb(capability) ORDER BY capability) FROM (
      SELECT jsonb_array_elements_text(previous.manifest->'roles'->'TENANT_ADMIN') capability
      UNION VALUES('ai.diagnosis.contribute'),('ai.diagnosis.contributors.manage')
    ) x)),
   '{roles,MEL_ADMIN}',
    (SELECT jsonb_agg(to_jsonb(capability) ORDER BY capability) FROM (
      SELECT jsonb_array_elements_text(previous.manifest->'roles'->'MEL_ADMIN') capability
      UNION VALUES('ai.diagnosis.contribute'),('ai.diagnosis.contributors.manage')
    ) x)),
  '{roles,PROGRAMME_MANAGER}',
    (SELECT jsonb_agg(to_jsonb(capability) ORDER BY capability) FROM (
      SELECT jsonb_array_elements_text(previous.manifest->'roles'->'PROGRAMME_MANAGER') capability
      UNION VALUES('ai.diagnosis.contribute'),('ai.diagnosis.contributors.manage')
    ) x)) AS manifest
 FROM previous
), expanded AS (
 SELECT jsonb_set(
  jsonb_set(first_roles.manifest,'{roles,AUTHOR}',
   (SELECT jsonb_agg(to_jsonb(capability) ORDER BY capability) FROM (
     SELECT jsonb_array_elements_text(first_roles.manifest->'roles'->'AUTHOR') capability
     UNION VALUES('ai.diagnosis.contribute')
   ) x)),
  '{roles,REVIEWER}',
   (SELECT jsonb_agg(to_jsonb(capability) ORDER BY capability) FROM (
     SELECT jsonb_array_elements_text(first_roles.manifest->'roles'->'REVIEWER') capability
     UNION VALUES('ai.diagnosis.contribute')
   ) x)) AS manifest
 FROM first_roles
)
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration)
 SELECT 'd58e9f971a4fb2c0d5aa4813cfeabd9edc612a6c61eae9dd2c83b9b1606c32ed',
  manifest,'0049_ai_diagnosis_contributions.sql' FROM expanded;

CREATE TABLE impact.ai_diagnosis_contributor_assignment(
 tenant_id uuid NOT NULL,
 assignment_id uuid NOT NULL,
 diagnosis_id uuid NOT NULL,
 diagnosis_revision uuid NOT NULL,
 diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 member_invitation_id uuid NOT NULL,
 contribution_role text NOT NULL CHECK(contribution_role IN
  ('PROBLEM_OWNER','EVIDENCE_CONTRIBUTOR','PRIORITISATION_CONTRIBUTOR')),
 problem_ids uuid[] NOT NULL CHECK(cardinality(problem_ids) BETWEEN 1 AND 20),
 sections text[] NOT NULL CHECK(cardinality(sections) BETWEEN 1 AND 4),
 inviter_id uuid NOT NULL,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(tenant_id,assignment_id),
 UNIQUE(tenant_id,diagnosis_id,member_invitation_id),
 FOREIGN KEY(tenant_id,diagnosis_id,diagnosis_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,diagnosis_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,member_invitation_id)
  REFERENCES impact.member_invitation(tenant_id,invitation_id),
 FOREIGN KEY(tenant_id,inviter_id)
  REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK(sections <@ ARRAY['PROBLEM_DESCRIPTION','AFFECTED_AREA','SUPPORTING_EVIDENCE','PRIORITY_ORDER']::text[])
);

CREATE TABLE impact.ai_diagnosis_contribution(
 tenant_id uuid NOT NULL,
 contribution_id uuid NOT NULL,
 assignment_id uuid NOT NULL,
 diagnosis_id uuid NOT NULL,
 base_revision uuid NOT NULL,
 diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 contributor_principal_id uuid NOT NULL,
 contributor_membership_id uuid NOT NULL,
 patch jsonb NOT NULL CHECK(jsonb_typeof(patch)='object'),
 submitted_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(tenant_id,contribution_id),
 FOREIGN KEY(tenant_id,assignment_id)
  REFERENCES impact.ai_diagnosis_contributor_assignment(tenant_id,assignment_id),
 FOREIGN KEY(tenant_id,diagnosis_id,base_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,base_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,contributor_principal_id)
  REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,contributor_membership_id)
  REFERENCES impact.membership_current(tenant_id,object_id)
);

CREATE TABLE impact.ai_diagnosis_contribution_decision(
 tenant_id uuid NOT NULL,
 contribution_id uuid NOT NULL,
 decision text NOT NULL CHECK(decision IN ('ACCEPTED','REJECTED')),
 reason text,
 diagnosis_id uuid NOT NULL,
 diagnosis_before_revision uuid NOT NULL,
 diagnosis_after_revision uuid NOT NULL,
 diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 decided_by uuid NOT NULL,
 decided_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(tenant_id,contribution_id),
 FOREIGN KEY(tenant_id,contribution_id)
  REFERENCES impact.ai_diagnosis_contribution(tenant_id,contribution_id),
 FOREIGN KEY(tenant_id,diagnosis_id,diagnosis_before_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,diagnosis_id,diagnosis_after_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,diagnosis_before_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,diagnosis_after_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,decided_by)
  REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK((decision='REJECTED' AND reason IS NOT NULL AND length(btrim(reason)) BETWEEN 1 AND 1000)
    OR (decision='ACCEPTED' AND reason IS NULL))
);

ALTER TABLE impact.ai_diagnosis_contributor_assignment ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_diagnosis_contributor_assignment FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_diagnosis_contributor_assignment
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_diagnosis_contribution ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_diagnosis_contribution FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_diagnosis_contribution
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_diagnosis_contribution_decision ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_diagnosis_contribution_decision FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_diagnosis_contribution_decision
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT ON impact.ai_diagnosis_contributor_assignment TO impact_app;
GRANT SELECT,INSERT ON impact.ai_diagnosis_contribution TO impact_app;
GRANT SELECT,INSERT ON impact.ai_diagnosis_contribution_decision TO impact_app;

CREATE FUNCTION impact.guard_ai_diagnosis_contribution_immutable() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 IF TG_OP<>'INSERT' THEN
  RAISE EXCEPTION 'diagnosis collaboration records are immutable' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION impact.guard_ai_diagnosis_contribution_immutable() FROM PUBLIC;
CREATE TRIGGER ai_diagnosis_assignment_immutable BEFORE UPDATE OR DELETE
 ON impact.ai_diagnosis_contributor_assignment FOR EACH ROW
 EXECUTE FUNCTION impact.guard_ai_diagnosis_contribution_immutable();
CREATE TRIGGER ai_diagnosis_contribution_immutable BEFORE UPDATE OR DELETE
 ON impact.ai_diagnosis_contribution FOR EACH ROW
 EXECUTE FUNCTION impact.guard_ai_diagnosis_contribution_immutable();
CREATE TRIGGER ai_diagnosis_decision_immutable BEFORE UPDATE OR DELETE
 ON impact.ai_diagnosis_contribution_decision FOR EACH ROW
 EXECUTE FUNCTION impact.guard_ai_diagnosis_contribution_immutable();

COMMIT;
