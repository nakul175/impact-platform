-- Register immutable pinned dashboard publications omitted by the original candidate.
BEGIN;
SET LOCAL ROLE impact_owner;

DO $$
DECLARE
    original_check text;
BEGIN
    SELECT pg_get_constraintdef(oid)
      INTO STRICT original_check
      FROM pg_constraint
     WHERE conrelid = 'impact.object_registry'::regclass
       AND conname = 'object_registry_object_type_check';

    IF position('DashboardPublication' IN original_check) = 0 THEN
        ALTER TABLE impact.object_registry
            DROP CONSTRAINT object_registry_object_type_check;
        EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
            || regexp_replace(
                original_check,
                '\)$',
                ' OR object_type = ''DashboardPublication'')'
            );
    END IF;
END $$;

-- The worker has no duty for pinned publication manifests.
CREATE POLICY worker_dashboard_publication_registry_fence
    ON impact.object_registry
    AS RESTRICTIVE
    FOR ALL
    TO impact_worker
    USING (object_type <> 'DashboardPublication')
    WITH CHECK (object_type <> 'DashboardPublication');

CREATE POLICY worker_dashboard_publication_revision_fence
    ON impact.object_revision
    AS RESTRICTIVE
    FOR ALL
    TO impact_worker
    USING (object_type <> 'DashboardPublication')
    WITH CHECK (object_type <> 'DashboardPublication');

COMMIT;
