BEGIN;
SET LOCAL ROLE impact_owner;
-- Personal saved views use the existing forced-RLS registry and immutable revision history.
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''SavedView'')');
END $$;
-- Search terms and exact definition bindings are personal navigation metadata, never worker input.
CREATE POLICY saved_view_registry_worker_fence ON impact.object_registry AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type<>'SavedView');
CREATE POLICY saved_view_revision_worker_fence ON impact.object_revision AS RESTRICTIVE FOR SELECT TO impact_worker USING(object_type<>'SavedView');
COMMIT;
