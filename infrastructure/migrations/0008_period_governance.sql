BEGIN;
SET LOCAL ROLE impact_owner;
ALTER TABLE impact.snapshot_current ADD COLUMN programme_id uuid;
ALTER TABLE impact.snapshot_current ADD CONSTRAINT snapshot_programme_fk
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id)
  DEFERRABLE INITIALLY DEFERRED;
DO $$
DECLARE original_check text;
BEGIN
  SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
    WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
  ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
  EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
    || regexp_replace(original_check, '\)$', ' OR object_type IN (''PeriodClose'',''RestatementRequest''))');
END $$;
CREATE TABLE impact.period_snapshot_binding(
  tenant_id uuid NOT NULL,
  programme_id uuid NOT NULL,
  period_id uuid NOT NULL,
  snapshot_version integer NOT NULL CHECK(snapshot_version>0),
  snapshot_id uuid NOT NULL,
  snapshot_revision uuid NOT NULL,
  close_id uuid NOT NULL,
  close_revision uuid NOT NULL,
  supersedes_snapshot_id uuid,
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,programme_id,period_id,snapshot_version),
  UNIQUE(tenant_id,snapshot_id),
  UNIQUE(tenant_id,close_id),
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,snapshot_id,snapshot_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,close_id,close_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,supersedes_snapshot_id) REFERENCES impact.object_registry(tenant_id,object_id)
);
CREATE TABLE impact.programme_period_state(
  tenant_id uuid NOT NULL,
  programme_id uuid NOT NULL,
  period_id uuid NOT NULL,
  lifecycle_state text NOT NULL CHECK(lifecycle_state IN ('Open','Locked','RestatementOpen')),
  current_snapshot_version integer NOT NULL DEFAULT 0 CHECK(current_snapshot_version>=0),
  restatement_expires_at timestamptz,
  updated_at timestamptz NOT NULL,
  updated_by uuid NOT NULL,
  PRIMARY KEY(tenant_id,programme_id,period_id),
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,updated_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
  CHECK((lifecycle_state='RestatementOpen')=(restatement_expires_at IS NOT NULL))
);
CREATE TABLE impact.official_result_snapshot(
  tenant_id uuid NOT NULL,
  snapshot_id uuid NOT NULL,
  result_id uuid NOT NULL,
  result_revision uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,snapshot_id,result_id),
  UNIQUE(tenant_id,result_revision),
  FOREIGN KEY(tenant_id,snapshot_id) REFERENCES impact.object_registry(tenant_id,object_id),
  FOREIGN KEY(tenant_id,result_id,result_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id)
);
CREATE TABLE impact.restatement_source_permission(
  tenant_id uuid NOT NULL,
  request_id uuid NOT NULL,
  request_revision uuid NOT NULL,
  programme_id uuid NOT NULL,
  period_id uuid NOT NULL,
  source_id uuid NOT NULL,
  expires_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,request_id,source_id),
  FOREIGN KEY(tenant_id,request_id,request_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,source_id) REFERENCES impact.observation_current(tenant_id,object_id)
);
ALTER TABLE impact.period_snapshot_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.period_snapshot_binding FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.programme_period_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.programme_period_state FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.official_result_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.official_result_snapshot FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.restatement_source_permission ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.restatement_source_permission FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.period_snapshot_binding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.programme_period_state USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.official_result_snapshot USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.restatement_source_permission USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.period_snapshot_binding,impact.official_result_snapshot,impact.restatement_source_permission TO impact_app;
GRANT SELECT,INSERT,UPDATE ON impact.programme_period_state TO impact_app;
COMMIT;
