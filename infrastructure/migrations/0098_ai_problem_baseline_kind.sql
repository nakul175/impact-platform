-- Register the problem-baseline registry kind omitted by migration 0048.
BEGIN;
SET LOCAL ROLE impact_owner;

DO $$
DECLARE
 original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check
 FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass
   AND conname='object_registry_object_type_check';
 IF position('AIProblemBaseline' IN original_check) = 0 THEN
  ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
  EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
    || regexp_replace(original_check, '\)$', ' OR object_type = ''AIProblemBaseline'')');
 END IF;
END $$;

-- Baselines contain operational measurements. The worker has no duty for this kind.
CREATE POLICY worker_problem_baseline_registry_fence
 ON impact.object_registry AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AIProblemBaseline')
 WITH CHECK (object_type <> 'AIProblemBaseline');
CREATE POLICY worker_problem_baseline_revision_fence
 ON impact.object_revision AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AIProblemBaseline')
 WITH CHECK (object_type <> 'AIProblemBaseline');

COMMIT;
