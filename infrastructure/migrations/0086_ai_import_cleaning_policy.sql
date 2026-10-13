BEGIN;
SET LOCAL ROLE impact_owner;
ALTER TABLE impact.ai_use_case_policy DROP CONSTRAINT ai_use_case_policy_use_case_check;
ALTER TABLE impact.ai_use_case_policy ADD CONSTRAINT ai_use_case_policy_use_case_check
 CHECK(use_case IN ('ADVISORY_DRAFT','EXTRACTION','REPORT_DRAFT','CHAT','INDICATOR_DESIGN','IMPORT_CLEANING'));
-- Runtime and policy validation keep IMPORT_CLEANING reserved-disabled; this migration only makes
-- the reviewed label representable in an immutable policy revision.
COMMIT;
