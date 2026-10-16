-- Additive projection fields for FR-CAL-005 governed cumulative differences.
BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.indicator_definition_current
  ADD COLUMN cumulative_baseline numeric(38,12),
  ADD COLUMN cumulative_baseline_basis text,
  ADD CONSTRAINT indicator_cumulative_baseline_nonnegative
    CHECK (cumulative_baseline IS NULL OR cumulative_baseline >= 0),
  ADD CONSTRAINT indicator_cumulative_baseline_basis_bounded
    CHECK (
      cumulative_baseline_basis IS NULL
      OR char_length(btrim(cumulative_baseline_basis)) BETWEEN 1 AND 2000
    );

ALTER TABLE impact.calculated_result_current
  ADD COLUMN cumulative_increments jsonb,
  ADD CONSTRAINT calculated_result_cumulative_increments_array
    CHECK (cumulative_increments IS NULL OR jsonb_typeof(cumulative_increments) = 'array');

COMMIT;
