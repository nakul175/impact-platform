BEGIN;
SET LOCAL ROLE impact_owner;
-- US-DC-04 disclose commercial relationships on every listing. Archived guidance gains edition
-- nonprofit-ai-guidance-v2 (each tool listing carries its commercial disclosure). Saved revisions
-- captured under v1 keep their rows and remain readable by the retained v1 reader, so the check now
-- admits exactly both editions. It keeps the name PostgreSQL gave 0037's column check. No table,
-- column, grant, role, policy, trigger or function change; snapshots stay insert-only.
ALTER TABLE impact.ai_content_snapshot DROP CONSTRAINT ai_content_snapshot_schema_version_check;
ALTER TABLE impact.ai_content_snapshot ADD CONSTRAINT ai_content_snapshot_schema_version_check
 CHECK(schema_version IN ('nonprofit-ai-guidance-v1','nonprofit-ai-guidance-v2'));
COMMIT;
