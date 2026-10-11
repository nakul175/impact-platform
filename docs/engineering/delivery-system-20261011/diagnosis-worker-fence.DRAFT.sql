-- REVIEW DRAFT ONLY: NOT an applied migration, NOT run, NOT release approval.
-- Existing migrations 0001-0044 must remain byte-exact.
-- Requires applicable authority, next contiguous migration, source/evidence review,
-- current build/security impact registration and real-role regression before integration.
BEGIN;
SET LOCAL ROLE impact_owner;
CREATE POLICY worker_diagnosis_registry_fence
 ON impact.object_registry AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AIDiagnosis')
 WITH CHECK (object_type <> 'AIDiagnosis');
CREATE POLICY worker_diagnosis_revision_fence
 ON impact.object_revision AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AIDiagnosis')
 WITH CHECK (object_type <> 'AIDiagnosis');
COMMIT;
