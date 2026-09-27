BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.report_package_binding(
  tenant_id uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  snapshot_id uuid NOT NULL,
  snapshot_revision uuid NOT NULL,
  template_revision uuid NOT NULL,
  reconciliation_digest bytea NOT NULL CHECK(octet_length(reconciliation_digest)=32),
  approved_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,report_id,report_revision),
  UNIQUE(tenant_id,report_revision),
  FOREIGN KEY(tenant_id,report_id,report_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,snapshot_id,snapshot_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,template_revision) REFERENCES impact.object_revision(tenant_id,revision_id)
);
ALTER TABLE impact.report_package_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_package_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.report_package_binding
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.report_package_binding TO impact_app;
COMMIT;
