BEGIN;
SET LOCAL ROLE impact_owner;
-- US-DC-04 disclose commercial relationships on every listing. Archived guidance gains edition
-- nonprofit-ai-guidance-v2 (each tool listing carries its commercial disclosure). Saved revisions
-- captured under v1 keep their rows and remain readable by the retained v1 reader, so the check now
-- admits exactly both editions. It keeps the name PostgreSQL gave 0037's column check.
ALTER TABLE impact.ai_content_snapshot DROP CONSTRAINT ai_content_snapshot_schema_version_check;
ALTER TABLE impact.ai_content_snapshot ADD CONSTRAINT ai_content_snapshot_schema_version_check
 CHECK(schema_version IN ('nonprofit-ai-guidance-v1','nonprofit-ai-guidance-v2'));
-- An internal plan copy whose archived guidance is v2 is issued as package nonprofit-ai-plan-export-v2;
-- copies of v1 or unarchived guidance stay nonprofit-ai-plan-export-v1 with the published v1 shape.
-- Existing issuances keep their label and bytes. Same name as 0040's column check.
ALTER TABLE impact.ai_plan_export_issuance DROP CONSTRAINT ai_plan_export_issuance_package_schema_version_check;
ALTER TABLE impact.ai_plan_export_issuance ADD CONSTRAINT ai_plan_export_issuance_package_schema_version_check
 CHECK(package_schema_version IN ('nonprofit-ai-plan-export-v1','nonprofit-ai-plan-export-v2'));
-- No table, column, grant, role, policy, trigger or function change; both tables stay insert-only.
COMMIT;
