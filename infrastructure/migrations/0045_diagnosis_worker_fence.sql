BEGIN;
SET LOCAL ROLE impact_owner;
-- The worker needs shared registry/revision access for reminders, audit and pinned exports.
-- Narrow only the diagnosis kind; keep grants, tenant fences and historical rows unchanged.
CREATE POLICY worker_diagnosis_registry_fence
 ON impact.object_registry AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AIDiagnosis')
 WITH CHECK (object_type <> 'AIDiagnosis');
CREATE POLICY worker_diagnosis_revision_fence
 ON impact.object_revision AS RESTRICTIVE FOR ALL TO impact_worker
 USING (object_type <> 'AIDiagnosis')
 WITH CHECK (object_type <> 'AIDiagnosis');
COMMIT;
