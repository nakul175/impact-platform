ALTER TABLE impact.programme_current
  ADD COLUMN template_code varchar(32),
  ADD COLUMN setup_defaults jsonb,
  ADD CONSTRAINT programme_template_code_closed
    CHECK (template_code IS NULL OR template_code = 'SIMPLE'),
  ADD CONSTRAINT programme_setup_defaults_object
    CHECK (setup_defaults IS NULL OR jsonb_typeof(setup_defaults) = 'object'),
  ADD CONSTRAINT programme_template_defaults_complete
    CHECK (
      template_code IS NULL
      OR (reporting_calendar_id IS NOT NULL AND setup_defaults IS NOT NULL)
    );
