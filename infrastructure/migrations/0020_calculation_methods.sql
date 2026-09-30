BEGIN;
SET LOCAL ROLE impact_owner;
-- Indicator and calculation completion (v0.19). The approved definition pins its disaggregation
-- scheme and a calculated result carries its category breakdown; both are payload properties that
-- the typed projections must hold. Additive columns only: no row is rewritten and no policy, grant
-- or role changes (both projections keep their existing RLS policies and grants).
ALTER TABLE impact.indicator_definition_current
 ADD COLUMN disaggregation jsonb CHECK(disaggregation IS NULL OR jsonb_typeof(disaggregation)='object');
ALTER TABLE impact.calculated_result_current
 ADD COLUMN disaggregation jsonb CHECK(disaggregation IS NULL OR jsonb_typeof(disaggregation)='array');
COMMIT;
