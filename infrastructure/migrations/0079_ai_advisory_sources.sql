BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.ai_advisory_source(
 tenant_id uuid NOT NULL,
 request_id uuid NOT NULL,
 ordinal smallint NOT NULL CHECK(ordinal BETWEEN 1 AND 20),
 source_object_id uuid NOT NULL,
 source_revision_id uuid NOT NULL,
 source_object_type text NOT NULL CHECK(source_object_type ~ '^[A-Z][A-Za-z0-9]{0,99}$'),
 required_capability text NOT NULL CHECK(required_capability ~ '^[a-z][a-z0-9.-]{0,99}$'),
 PRIMARY KEY(tenant_id,request_id,ordinal),
 UNIQUE(tenant_id,request_id,source_object_id,source_revision_id),
 FOREIGN KEY(tenant_id,request_id) REFERENCES impact.ai_advisory_request(tenant_id,request_id),
 FOREIGN KEY(tenant_id,source_object_id,source_revision_id)
   REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
CREATE TRIGGER ai_advisory_source_immutable BEFORE UPDATE OR DELETE ON impact.ai_advisory_source
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_advisory_insert_only();
ALTER TABLE impact.ai_advisory_source ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_advisory_source FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_advisory_source
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_advisory_source TO impact_app;
COMMIT;
