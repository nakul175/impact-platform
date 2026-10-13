ALTER TABLE impact.indicator_definition_current
  ADD COLUMN statistical_interpretation jsonb,
  ADD CONSTRAINT indicator_statistical_interpretation_object
    CHECK (
      statistical_interpretation IS NULL
      OR jsonb_typeof(statistical_interpretation) = 'object'
    );
