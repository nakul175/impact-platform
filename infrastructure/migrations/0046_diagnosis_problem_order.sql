BEGIN;
SET LOCAL ROLE impact_owner;
-- A pure invoker function: no table reads, identity lookup or authority bypass.
-- Draft priorities may be partial; Completed priorities must cover every problem.
CREATE FUNCTION impact.diagnosis_problem_order_valid(p jsonb) RETURNS boolean
 LANGUAGE plpgsql IMMUTABLE SET search_path=pg_catalog AS $$
DECLARE
 item jsonb;
 id text;
 problems text[] := ARRAY[]::text[];
 priorities text[] := ARRAY[]::text[];
BEGIN
 IF jsonb_typeof(p) IS DISTINCT FROM 'object'
    OR jsonb_typeof(p->'problems') IS DISTINCT FROM 'array'
    OR jsonb_typeof(p->'priority_order') IS DISTINCT FROM 'array'
    OR jsonb_typeof(p->'diagnosis_state') IS DISTINCT FROM 'string'
    OR p->>'diagnosis_state' NOT IN ('Draft','Completed') THEN
  RETURN false;
 END IF;
 IF jsonb_array_length(p->'problems')>20 OR jsonb_array_length(p->'priority_order')>20 THEN
  RETURN false;
 END IF;
 FOR item IN SELECT value FROM jsonb_array_elements(p->'problems') LOOP
  IF jsonb_typeof(item) IS DISTINCT FROM 'object'
     OR jsonb_typeof(item->'problem_id') IS DISTINCT FROM 'string' THEN
   RETURN false;
  END IF;
  id := item->>'problem_id';
  IF id !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
     OR id=ANY(problems) THEN
   RETURN false;
  END IF;
  problems := array_append(problems,id);
 END LOOP;
 FOR item IN SELECT value FROM jsonb_array_elements(p->'priority_order') LOOP
  IF jsonb_typeof(item) IS DISTINCT FROM 'string' THEN
   RETURN false;
  END IF;
  id := item #>> '{}';
  IF NOT id=ANY(problems) OR id=ANY(priorities) THEN
   RETURN false;
  END IF;
  priorities := array_append(priorities,id);
 END LOOP;
 RETURN p->>'diagnosis_state'='Draft'
        OR (cardinality(problems)>0 AND cardinality(problems)=cardinality(priorities));
END;
$$;
REVOKE ALL ON FUNCTION impact.diagnosis_problem_order_valid(jsonb) FROM PUBLIC;
-- PostgreSQL checks helper execution privilege even for another kind's CHECK
-- branch. Existing revision writers need only this pure predicate, no new data grant.
GRANT EXECUTE ON FUNCTION impact.diagnosis_problem_order_valid(jsonb)
 TO impact_app,impact_worker,impact_platform,impact_privacy;
-- Existing governed removal uses SQL NULL, never a JSON null/tombstone payload.
-- Validate all existing revisions; invalid historical data blocks the migration
-- atomically rather than being rewritten or silently waived.
ALTER TABLE impact.object_revision ADD CONSTRAINT diagnosis_problem_order_valid
 CHECK(CASE WHEN object_type<>'AIDiagnosis' THEN true
            WHEN restriction_state='REMOVED' AND payload IS NULL THEN true
            ELSE COALESCE(impact.diagnosis_problem_order_valid(payload),false) END);
COMMIT;
