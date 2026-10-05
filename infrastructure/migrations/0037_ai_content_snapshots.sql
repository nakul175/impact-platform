BEGIN;
SET LOCAL ROLE impact_owner;
-- Editorial guidance is captured only when a new adoption-plan revision is saved.
-- No old revision is backfilled from current content or re-pointed to another edition.
CREATE TABLE impact.ai_content_snapshot(
 tenant_id uuid NOT NULL,
 snapshot_id uuid NOT NULL,
 schema_version varchar(64) NOT NULL CHECK(schema_version='nonprofit-ai-guidance-v1'),
 payload jsonb NOT NULL CHECK(jsonb_typeof(payload)='object'),
 payload_sha256 bytea NOT NULL CHECK(octet_length(payload_sha256)=32),
 captured_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,snapshot_id),
 UNIQUE(tenant_id,payload_sha256),
 FOREIGN KEY(tenant_id) REFERENCES impact.tenant_root(tenant_id)
);
-- A bundle can legitimately share unchanged components with other bundles.
-- Under the tenant write lock the server checks a component edition's exact words;
-- these non-unique indexes support that bounded lookup without cross-tenant reads.
CREATE INDEX ai_content_catalog_edition ON impact.ai_content_snapshot
 (tenant_id,(payload->'catalog'->>'content_version'));
CREATE INDEX ai_content_solutions_edition ON impact.ai_content_snapshot
 (tenant_id,(payload->'solutions'->>'content_version'));
CREATE INDEX ai_content_practice_edition ON impact.ai_content_snapshot
 (tenant_id,(payload->'practice'->>'content_version'));
CREATE TABLE impact.ai_plan_content_binding(
 tenant_id uuid NOT NULL,
 object_id uuid NOT NULL,
 revision_id uuid NOT NULL,
 revision_kind text GENERATED ALWAYS AS ('AIAdoptionPlan') STORED,
 snapshot_id uuid NOT NULL,
 PRIMARY KEY(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,object_id,revision_id)
   REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,revision_id,revision_kind)
   REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,snapshot_id)
   REFERENCES impact.ai_content_snapshot(tenant_id,snapshot_id)
);
CREATE FUNCTION impact.guard_ai_content_insert_only() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
 BEGIN RAISE EXCEPTION 'AI content archives are insert-only' USING ERRCODE='42501'; END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_content_insert_only() FROM PUBLIC;
CREATE TRIGGER ai_content_snapshot_immutable BEFORE UPDATE OR DELETE ON impact.ai_content_snapshot
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_content_insert_only();
CREATE TRIGGER ai_plan_content_binding_immutable BEFORE UPDATE OR DELETE ON impact.ai_plan_content_binding
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_content_insert_only();
ALTER TABLE impact.ai_content_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_content_snapshot FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_content_snapshot
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_plan_content_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_plan_content_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_plan_content_binding
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_content_snapshot,impact.ai_plan_content_binding TO impact_app;
COMMIT;
