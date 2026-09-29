BEGIN;
SET LOCAL ROLE impact_owner;
-- Results framework and planning (v0.18). Framework and Target have been registry kinds with typed
-- projections since 0002; this migration adds the payload columns the implemented contract writes
-- and two insert-only registers of independently approved baselines. A register row is written only
-- in the approval transaction; a later change is a new row that names the revision it supersedes,
-- so an approved revision is never re-pointed and each revision can be superseded exactly once.
ALTER TABLE impact.framework_current
 ADD COLUMN effective_from timestamptz,
 ADD COLUMN supersedes_revision uuid,
 ADD COLUMN supersedes_revision_kind text GENERATED ALWAYS AS ('Framework') STORED,
 ADD COLUMN exceptions jsonb CHECK(exceptions IS NULL OR jsonb_typeof(exceptions)='array'),
 ADD CONSTRAINT framework_supersedes_fk FOREIGN KEY(tenant_id,supersedes_revision,supersedes_revision_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE impact.target_current
 ADD COLUMN indicator_id uuid,
 ADD COLUMN indicator_id_kind text GENERATED ALWAYS AS ('IndicatorInstance') STORED,
 ADD COLUMN milestone_label varchar(200),
 ADD COLUMN due_at timestamptz,
 ADD COLUMN supersedes_revision uuid,
 ADD COLUMN supersedes_revision_kind text GENERATED ALWAYS AS ('Target') STORED,
 ADD COLUMN reason text,
 ADD CONSTRAINT target_indicator_fk FOREIGN KEY(tenant_id,indicator_id,indicator_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 ADD CONSTRAINT target_supersedes_fk FOREIGN KEY(tenant_id,supersedes_revision,supersedes_revision_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 -- A blank target is never zero: only a PRESENT target carries a value or bounds.
 ADD CONSTRAINT target_blank_is_not_zero CHECK(value_state IS NULL OR value_state='PRESENT'
  OR (value IS NULL AND low IS NULL AND high IS NULL));

CREATE TABLE impact.framework_baseline(
  tenant_id uuid NOT NULL,
  programme_id uuid NOT NULL,
  baseline_version integer NOT NULL CHECK(baseline_version>0),
  framework_id uuid NOT NULL,
  framework_revision uuid NOT NULL,
  supersedes_revision uuid,
  effective_from timestamptz NOT NULL,
  workflow_id uuid NOT NULL,
  approved_by uuid NOT NULL,
  approved_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,programme_id,baseline_version),
  UNIQUE(tenant_id,framework_revision),
  UNIQUE(tenant_id,programme_id,framework_revision),
  UNIQUE(tenant_id,supersedes_revision),
  CHECK((baseline_version=1)=(supersedes_revision IS NULL)),
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,framework_id,framework_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,programme_id,supersedes_revision) REFERENCES impact.framework_baseline(tenant_id,programme_id,framework_revision),
  FOREIGN KEY(tenant_id,workflow_id) REFERENCES impact.object_registry(tenant_id,object_id),
  FOREIGN KEY(tenant_id,approved_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.target_binding(
  tenant_id uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  slot varchar(220) NOT NULL CHECK(slot IN ('TARGET','BASELINE') OR slot LIKE 'MILESTONE:_%'),
  binding_version integer NOT NULL CHECK(binding_version>0),
  target_id uuid NOT NULL,
  target_revision uuid NOT NULL,
  supersedes_revision uuid,
  workflow_id uuid NOT NULL,
  approved_by uuid NOT NULL,
  approved_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,indicator_id,period_id,slot,binding_version),
  UNIQUE(tenant_id,target_revision),
  UNIQUE(tenant_id,indicator_id,period_id,slot,target_revision),
  UNIQUE(tenant_id,supersedes_revision),
  CHECK((binding_version=1)=(supersedes_revision IS NULL)),
  FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,target_id,target_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,indicator_id,period_id,slot,supersedes_revision)
    REFERENCES impact.target_binding(tenant_id,indicator_id,period_id,slot,target_revision),
  FOREIGN KEY(tenant_id,workflow_id) REFERENCES impact.object_registry(tenant_id,object_id),
  FOREIGN KEY(tenant_id,approved_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX target_binding_period ON impact.target_binding(tenant_id,period_id);
ALTER TABLE impact.framework_baseline ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.framework_baseline FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.target_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.target_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.framework_baseline USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.target_binding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Insert-only for the application; nothing for the control plane.
GRANT SELECT,INSERT ON impact.framework_baseline,impact.target_binding TO impact_app;
COMMIT;
