BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.derivative_manifest(
 tenant_id uuid NOT NULL, derivative_id uuid NOT NULL, derivative_revision_id uuid NOT NULL,
 derivative_kind text NOT NULL CHECK(derivative_kind IN ('Dashboard','Search','Analysis','AIArtifact','ApprovedAggregate')),
 disclosure_mode text NOT NULL CHECK(disclosure_mode IN ('PRIVATE','APPROVED_AGGREGATE')),
 created_by uuid NOT NULL, created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,derivative_id,derivative_revision_id),
 FOREIGN KEY(tenant_id,created_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.derivative_source(
 tenant_id uuid NOT NULL, derivative_id uuid NOT NULL, derivative_revision_id uuid NOT NULL,
 ordinal smallint NOT NULL CHECK(ordinal BETWEEN 1 AND 100), source_object_id uuid NOT NULL,
 source_revision_id uuid NOT NULL, source_object_type text NOT NULL, required_capability text NOT NULL,
 PRIMARY KEY(tenant_id,derivative_id,derivative_revision_id,ordinal),
 FOREIGN KEY(tenant_id,derivative_id,derivative_revision_id) REFERENCES impact.derivative_manifest(tenant_id,derivative_id,derivative_revision_id)
);
ALTER TABLE impact.derivative_manifest ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.derivative_manifest FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.derivative_manifest USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.derivative_source ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.derivative_source FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.derivative_source USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.derivative_manifest,impact.derivative_source TO impact_app;
COMMIT;
