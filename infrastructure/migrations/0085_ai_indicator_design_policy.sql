BEGIN;
SET LOCAL ROLE impact_owner;
ALTER TABLE impact.ai_use_case_policy DROP CONSTRAINT ai_use_case_policy_use_case_check;
ALTER TABLE impact.ai_use_case_policy ADD CONSTRAINT ai_use_case_policy_use_case_check
 CHECK(use_case IN ('ADVISORY_DRAFT','EXTRACTION','REPORT_DRAFT','CHAT','INDICATOR_DESIGN'));
-- ai_use_case_reserved remains unchanged: INDICATOR_DESIGN can be represented in a reviewed policy
-- only while disabled. Enabling it requires a later reviewed activation migration.
COMMIT;
