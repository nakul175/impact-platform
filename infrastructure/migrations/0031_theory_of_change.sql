BEGIN;
SET LOCAL ROLE impact_owner;
-- Theory of change, assumptions and status thresholds (v0.27 planning). Payload columns only: a
-- framework revision now carries typed relationships between its nodes (the 0002 column
-- `relationships`, written empty until this build) and the assumptions, risks and context records
-- its nodes rely on; a target carries the status thresholds its independent review approves, so the
-- band shown against an official number is the one pinned with that target at close. Additive: no
-- grant, policy, trigger or role change; both arrays and the object are JSON documents of the
-- revision payload, validated by the closed contract schemas before they are written.
ALTER TABLE impact.framework_current
 ADD COLUMN assumptions jsonb CHECK(assumptions IS NULL OR jsonb_typeof(assumptions)='array');
ALTER TABLE impact.target_current
 ADD COLUMN status_thresholds jsonb
  CHECK(status_thresholds IS NULL OR jsonb_typeof(status_thresholds)='object');
COMMIT;
