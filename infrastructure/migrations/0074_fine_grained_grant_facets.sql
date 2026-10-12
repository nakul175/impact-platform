BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.grant_access_facet(
 tenant_id uuid NOT NULL, grant_id uuid NOT NULL,
 record_object_ids uuid[] NOT NULL CHECK(cardinality(record_object_ids) BETWEEN 1 AND 100),
 readable_field_categories text[] NOT NULL CHECK(cardinality(readable_field_categories) BETWEEN 1 AND 16),
 writable_field_categories text[] NOT NULL CHECK(cardinality(writable_field_categories) BETWEEN 0 AND 16),
 attached_by uuid NOT NULL, attached_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,grant_id),
 FOREIGN KEY(tenant_id,grant_id) REFERENCES impact.grant_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,attached_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK(writable_field_categories <@ readable_field_categories)
);
ALTER TABLE impact.grant_access_facet ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.grant_access_facet FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.grant_access_facet
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.grant_access_facet TO impact_app;
COMMIT;
