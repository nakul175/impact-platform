-- Immutable advisor-authored six-dimensional fit scores for source-backed options.
BEGIN;
SET LOCAL ROLE impact_owner;

WITH previous AS (
 SELECT manifest FROM impact.platform_access_profile WHERE source_migration='0050_ai_diagnosis_reviews.sql'
), expanded AS (
 SELECT jsonb_set(previous.manifest,'{roles,REVIEWER}',
  (SELECT jsonb_agg(to_jsonb(capability) ORDER BY capability) FROM (
    SELECT jsonb_array_elements_text(previous.manifest->'roles'->'REVIEWER') capability
    UNION VALUES('ai.solution-fit.score')
  ) x)) AS manifest FROM previous
)
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration)
 SELECT '873961b446fcb46219703d05cfbde78868783355d27304f0d38bcafafb2f3653',manifest,'0051_ai_solution_fit_scores.sql' FROM expanded;

CREATE TABLE impact.ai_solution_fit_score(
 tenant_id uuid NOT NULL, score_id uuid NOT NULL,
 opportunity_id text NOT NULL CHECK(length(btrim(opportunity_id)) BETWEEN 1 AND 120),
 solution_id text NOT NULL CHECK(length(btrim(solution_id)) BETWEEN 1 AND 120),
 catalogue_content_version text NOT NULL CHECK(length(btrim(catalogue_content_version)) BETWEEN 1 AND 120),
 rubric_version text NOT NULL CHECK(rubric_version='pilot-fit-v1'),
 size smallint NOT NULL CHECK(size BETWEEN 1 AND 5),
 budget smallint NOT NULL CHECK(budget BETWEEN 1 AND 5),
 context smallint NOT NULL CHECK(context BETWEEN 1 AND 5),
 language smallint NOT NULL CHECK(language BETWEEN 1 AND 5),
 data_sensitivity smallint NOT NULL CHECK(data_sensitivity BETWEEN 1 AND 5),
 existing_systems smallint NOT NULL CHECK(existing_systems BETWEEN 1 AND 5),
 explanations jsonb NOT NULL CHECK(jsonb_typeof(explanations)='object' AND
  explanations ?& ARRAY['size','budget','context','language','data_sensitivity','existing_systems'] AND
  explanations-ARRAY['size','budget','context','language','data_sensitivity','existing_systems']='{}'::jsonb),
 advisor_principal_id uuid NOT NULL, advisor_membership_id uuid NOT NULL,
 advisor_natural_identity_id uuid NOT NULL, scored_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,score_id),
 FOREIGN KEY(tenant_id,advisor_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,advisor_membership_id) REFERENCES impact.membership_current(tenant_id,object_id)
);
CREATE INDEX ai_solution_fit_latest ON impact.ai_solution_fit_score(tenant_id,opportunity_id,solution_id,scored_at DESC,score_id DESC);
ALTER TABLE impact.ai_solution_fit_score ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_solution_fit_score FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_solution_fit_score USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_solution_fit_score TO impact_app;
CREATE FUNCTION impact.guard_ai_solution_fit_immutable() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 RAISE EXCEPTION 'solution fit scores are immutable' USING ERRCODE='42501';
END;
$$;
REVOKE ALL ON FUNCTION impact.guard_ai_solution_fit_immutable() FROM PUBLIC;
CREATE TRIGGER ai_solution_fit_immutable BEFORE UPDATE OR DELETE ON impact.ai_solution_fit_score FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_solution_fit_immutable();
COMMIT;
