BEGIN;
SET LOCAL ROLE impact_owner;
-- Immutable self-reported observations reuse the forced-RLS registry and revisions.
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''AICurrentOutcomeObservation'')');
END $$;
-- Organizational usage and outcome measures are outside every worker duty.
CREATE POLICY worker_current_outcome_registry_fence
 ON impact.object_registry AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AICurrentOutcomeObservation')
 WITH CHECK (object_type <> 'AICurrentOutcomeObservation');
CREATE POLICY worker_current_outcome_revision_fence
 ON impact.object_revision AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AICurrentOutcomeObservation')
 WITH CHECK (object_type <> 'AICurrentOutcomeObservation');
COMMIT;
