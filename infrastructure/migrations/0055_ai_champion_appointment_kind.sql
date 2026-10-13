BEGIN;
SET LOCAL ROLE impact_owner;
-- Reuse the forced-RLS registry and immutable revisions. Preserve every existing kind.
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''AIChampionAppointment'')');
END $$;
-- Champion records contain participant identities and schedules. The worker has no duty for them.
CREATE POLICY worker_champion_appointment_registry_fence
 ON impact.object_registry AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AIChampionAppointment')
 WITH CHECK (object_type <> 'AIChampionAppointment');
CREATE POLICY worker_champion_appointment_revision_fence
 ON impact.object_revision AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AIChampionAppointment')
 WITH CHECK (object_type <> 'AIChampionAppointment');
COMMIT;
