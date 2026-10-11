-- Unregistered storage experiment; not a migration or linkage implementation.
BEGIN;
SET LOCAL ROLE impact_owner;
CREATE FUNCTION impact.diagnosis_evidence_shape_valid(p jsonb) RETURNS boolean
 LANGUAGE plpgsql IMMUTABLE SET search_path=pg_catalog AS $$
DECLARE problem jsonb; refs jsonb; ref jsonb; pair text; seen text[];
BEGIN
 IF jsonb_typeof(p) IS DISTINCT FROM 'object'
    OR jsonb_typeof(p->'problems') IS DISTINCT FROM 'array'
    OR jsonb_array_length(p->'problems')>20 THEN RETURN false; END IF;
 FOR problem IN SELECT value FROM jsonb_array_elements(p->'problems') LOOP
  IF jsonb_typeof(problem) IS DISTINCT FROM 'object' THEN RETURN false; END IF;
  IF NOT problem ? 'evidence_references' THEN CONTINUE; END IF;
  refs := problem->'evidence_references';
  IF jsonb_typeof(refs) IS DISTINCT FROM 'array' THEN RETURN false; END IF;
  IF jsonb_array_length(refs)>5 THEN RETURN false; END IF;
  seen := ARRAY[]::text[];
  FOR ref IN SELECT value FROM jsonb_array_elements(refs) LOOP
   IF jsonb_typeof(ref) IS DISTINCT FROM 'object' THEN RETURN false; END IF;
   IF NOT ref ?& ARRAY['object_id','revision_id']
      OR ref-ARRAY['object_id','revision_id'] <> '{}'::jsonb
      OR jsonb_typeof(ref->'object_id') IS DISTINCT FROM 'string'
      OR jsonb_typeof(ref->'revision_id') IS DISTINCT FROM 'string' THEN RETURN false; END IF;
   IF ref->>'object_id' !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
      OR ref->>'revision_id' !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN
    RETURN false;
   END IF;
   pair := (ref->>'object_id') || '/' || (ref->>'revision_id');
   IF pair=ANY(seen) THEN RETURN false; END IF;
   seen := array_append(seen,pair);
  END LOOP;
 END LOOP;
 RETURN true;
END;
$$;
REVOKE ALL ON FUNCTION impact.diagnosis_evidence_shape_valid(jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.diagnosis_evidence_shape_valid(jsonb)
 TO impact_app,impact_worker,impact_platform,impact_privacy;
ALTER TABLE impact.object_revision ADD CONSTRAINT diagnosis_evidence_shape_valid
 CHECK(CASE WHEN object_type<>'AIDiagnosis' THEN true
            WHEN restriction_state='REMOVED' AND payload IS NULL THEN true
            ELSE COALESCE(impact.diagnosis_evidence_shape_valid(payload),false) END);
COMMIT;
