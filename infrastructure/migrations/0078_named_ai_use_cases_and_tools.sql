BEGIN;
SET LOCAL ROLE impact_owner;
-- FR-AI-001: policy configuration may name every reviewed use case and may separately allow
-- bounded tool identifiers. This grants no runtime by itself: every provider/tool boundary still
-- calls ai_policy.require() with its exact use case and requested tool set before transmission.
ALTER TABLE impact.ai_use_case_policy DROP CONSTRAINT ai_use_case_reserved;
ALTER TABLE impact.ai_use_case_policy DROP CONSTRAINT ai_use_case_policy_tools_check;
ALTER TABLE impact.ai_use_case_policy ADD CONSTRAINT ai_use_case_policy_tools_bounded
 CHECK(cardinality(tools)<=20 AND array_position(tools,NULL) IS NULL
   AND char_length(array_to_string(tools,''))<=1280);
COMMIT;
