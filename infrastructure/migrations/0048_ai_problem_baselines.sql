-- Immutable, self-reported time/cost/quality/reach baselines for completed diagnosis problems.
BEGIN;
SET LOCAL ROLE impact_owner;

-- Register the generated profile for governed future/bootstrap upgrades. This
-- does not activate it or widen an existing tenant's authority automatically.
WITH previous AS (
 SELECT manifest FROM impact.platform_access_profile
 WHERE source_migration='0044_ai_diagnoses.sql'
), tenant_admin AS (
 SELECT jsonb_agg(to_jsonb(capability) ORDER BY capability) AS capabilities
 FROM (
  SELECT jsonb_array_elements_text(manifest->'roles'->'TENANT_ADMIN') AS capability
  FROM previous
  UNION
  VALUES('ai.problem-baseline.manage'),('ai.problem-baseline.read')
 ) sorted
), profile AS (
 SELECT jsonb_set(previous.manifest,'{roles,TENANT_ADMIN}',tenant_admin.capabilities) AS manifest
 FROM previous,tenant_admin
)
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration)
 SELECT 'cce40deacb3bdb9051a48550ffc6a49e513960bfb18cca950ae936bc15a5f921',
  manifest,'0048_ai_problem_baselines.sql' FROM profile;

CREATE TABLE impact.problem_baseline_lock(
 tenant_id uuid NOT NULL,
 object_id uuid NOT NULL,
 revision_id uuid NOT NULL,
 baseline_kind text GENERATED ALWAYS AS ('AIProblemBaseline') STORED,
 diagnosis_id uuid NOT NULL,
 diagnosis_revision uuid NOT NULL,
 diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 problem_id uuid NOT NULL,
 locked_by uuid NOT NULL,
 locked_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(tenant_id,object_id),
 UNIQUE(tenant_id,revision_id),
 FOREIGN KEY(tenant_id,object_id,revision_id)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,revision_id,baseline_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,diagnosis_id,diagnosis_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,diagnosis_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,locked_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.problem_baseline_lock ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.problem_baseline_lock FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.problem_baseline_lock
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.problem_baseline_lock TO impact_app;

CREATE FUNCTION impact.guard_problem_baseline_lock() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
DECLARE payload jsonb;
BEGIN
 IF TG_OP<>'INSERT' THEN
  RAISE EXCEPTION 'problem baseline locks are insert-only' USING ERRCODE='42501';
 END IF;
 SELECT r.payload INTO payload FROM impact.object_revision r
  WHERE r.tenant_id=NEW.tenant_id AND r.object_id=NEW.object_id
   AND r.revision_id=NEW.revision_id AND r.object_type='AIProblemBaseline'
   AND r.restriction_state='AVAILABLE';
 IF payload IS NULL OR payload->>'baseline_state'<>'Locked'
    OR payload->>'diagnosis_id'<>NEW.diagnosis_id::text
    OR payload->>'diagnosis_revision'<>NEW.diagnosis_revision::text
    OR payload->>'problem_id'<>NEW.problem_id::text
    OR payload->>'locked_by'<>NEW.locked_by::text THEN
  RAISE EXCEPTION 'problem baseline lock must match immutable revision'
   USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION impact.guard_problem_baseline_lock() FROM PUBLIC;
CREATE TRIGGER problem_baseline_lock_guard BEFORE INSERT OR UPDATE OR DELETE
 ON impact.problem_baseline_lock FOR EACH ROW
 EXECUTE FUNCTION impact.guard_problem_baseline_lock();

COMMIT;
