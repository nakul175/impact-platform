BEGIN;
SET LOCAL ROLE impact_owner;
-- Import and data quality (v0.21). ImportJob has been a registry kind with a typed projection since
-- 0002; this migration adds the payload columns the implemented import batch writes (the bounded
-- source file carried in the request, its mapping to indicator instances, unit and period, the
-- staged row outcomes with their quality checks, and the commit manifest) and one insert-only
-- register that makes "this unit already reported this indicator for this period through an
-- import" a database fact. A register row is written only by the commit of an independently
-- staged batch, in the same transaction as the observation it names; it is never updated or
-- deleted, so a second batch for the same unit, indicator and period is a duplicate.
ALTER TABLE impact.import_job_current
 ADD COLUMN programme_id uuid,
 ADD COLUMN programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
 ADD COLUMN period_id uuid,
 ADD COLUMN period_id_kind text GENERATED ALWAYS AS ('Period') STORED,
 ADD COLUMN format varchar(16) CHECK(format IS NULL OR format IN ('CSV','XLSX')),
 ADD COLUMN file_name varchar(200),
 ADD COLUMN content text,
 ADD COLUMN content_sha256 varchar(64) CHECK(content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$'),
 ADD COLUMN received_at timestamptz,
 ADD COLUMN mapping jsonb CHECK(mapping IS NULL OR jsonb_typeof(mapping)='object'),
 ADD COLUMN preview jsonb CHECK(preview IS NULL OR jsonb_typeof(preview)='object'),
 ADD COLUMN committed jsonb CHECK(committed IS NULL OR jsonb_typeof(committed)='object'),
 ADD COLUMN cancel_reason text,
 ADD CONSTRAINT import_job_programme_fk FOREIGN KEY(tenant_id,programme_id,programme_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 ADD CONSTRAINT import_job_period_fk FOREIGN KEY(tenant_id,period_id,period_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE impact.import_unit_register(
  tenant_id uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  unit_key varchar(100) NOT NULL CHECK(unit_key ~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$'),
  observation_id uuid NOT NULL,
  import_id uuid NOT NULL,
  import_revision uuid NOT NULL,
  row_number integer NOT NULL CHECK(row_number>1),
  registered_by uuid NOT NULL,
  registered_at timestamptz NOT NULL,
  indicator_id_kind text GENERATED ALWAYS AS ('IndicatorInstance') STORED,
  period_id_kind text GENERATED ALWAYS AS ('Period') STORED,
  observation_id_kind text GENERATED ALWAYS AS ('Observation') STORED,
  import_id_kind text GENERATED ALWAYS AS ('ImportJob') STORED,
  PRIMARY KEY(tenant_id,indicator_id,period_id,unit_key),
  UNIQUE(tenant_id,observation_id),
  FOREIGN KEY(tenant_id,indicator_id,indicator_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,period_id,period_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,observation_id,observation_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,import_id,import_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,import_id,import_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,registered_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX import_unit_register_import ON impact.import_unit_register(tenant_id,import_id);
ALTER TABLE impact.import_unit_register ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.import_unit_register FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.import_unit_register USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Insert-only for the application; nothing for the worker or the control plane.
GRANT SELECT,INSERT ON impact.import_unit_register TO impact_app;
COMMIT;
