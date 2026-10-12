BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.external_share(
 tenant_id uuid NOT NULL, share_id uuid NOT NULL, derivative_id uuid NOT NULL, derivative_revision_id uuid NOT NULL,
 audience_principal_id uuid NOT NULL, actions text[] NOT NULL CHECK(cardinality(actions) BETWEEN 1 AND 8),
 owner_principal_id uuid NOT NULL, reason text NOT NULL CHECK(length(reason) BETWEEN 1 AND 500),
 expires_at timestamptz NOT NULL, created_at timestamptz NOT NULL, revoked_at timestamptz, revoked_by uuid,
 PRIMARY KEY(tenant_id,share_id),
 FOREIGN KEY(tenant_id,derivative_id,derivative_revision_id) REFERENCES impact.derivative_manifest(tenant_id,derivative_id,derivative_revision_id),
 FOREIGN KEY(tenant_id,audience_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,owner_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,revoked_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.external_share ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.external_share FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.external_share USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE(revoked_at,revoked_by) ON impact.external_share TO impact_app;
COMMIT;
