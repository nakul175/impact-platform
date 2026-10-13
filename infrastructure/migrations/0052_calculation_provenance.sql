-- Additive projection fields for FR-CAL-001 deterministic reproduction metadata.
BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.calculated_result_current
 ADD COLUMN calculation_precision_digits smallint CHECK(calculation_precision_digits=100),
 ADD COLUMN formula jsonb CHECK(formula IS NULL OR jsonb_typeof(formula)='object'),
 ADD COLUMN filters jsonb CHECK(filters IS NULL OR jsonb_typeof(filters)='object');

ALTER TABLE impact.indicator_definition_current
 ADD COLUMN allows_negative_adjustments boolean NOT NULL DEFAULT false,
 ADD COLUMN negative_adjustment_basis text CHECK(
   negative_adjustment_basis IS NULL OR char_length(btrim(negative_adjustment_basis)) BETWEEN 1 AND 2000
 );

COMMIT;
