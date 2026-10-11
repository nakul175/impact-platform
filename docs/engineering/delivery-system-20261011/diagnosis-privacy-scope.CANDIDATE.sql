-- Unregistered local candidate: install only in disposable synthetic qualification.
-- No schema/migration-ledger claim; no new roles, privileges or removal definer.
BEGIN;
SET LOCAL ROLE impact_owner;
ALTER TABLE impact.privacy_case_current
    ADD COLUMN diagnosis_ids jsonb
    CHECK (diagnosis_ids IS NULL OR jsonb_typeof(diagnosis_ids) = 'array');
COMMIT;
