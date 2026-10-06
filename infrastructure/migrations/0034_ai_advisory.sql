BEGIN;
SET LOCAL ROLE impact_owner;
-- Extend the current check, preserving kinds introduced by every prior migration.
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''AIAdvisoryRequest'')');
END $$;

CREATE TABLE impact.ai_advisory_request(
 tenant_id uuid NOT NULL,
 request_id uuid NOT NULL,
 object_id uuid NOT NULL,
 principal_id uuid NOT NULL,
 fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
 reserved_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,request_id),
 UNIQUE(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id) REFERENCES impact.object_registry(tenant_id,object_id),
 FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX ai_advisory_daily ON impact.ai_advisory_request(tenant_id,reserved_at);
CREATE TABLE impact.ai_advisory_result(
 tenant_id uuid NOT NULL,
 request_id uuid NOT NULL,
 sealed_output bytea,
 failure_reason text CHECK(failure_reason='AI_PROVIDER_UNAVAILABLE'),
 completed_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,request_id),
 FOREIGN KEY(tenant_id,request_id) REFERENCES impact.ai_advisory_request(tenant_id,request_id),
 CHECK((sealed_output IS NOT NULL) <> (failure_reason IS NOT NULL))
);
CREATE FUNCTION impact.guard_ai_advisory_insert_only() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
 BEGIN RAISE EXCEPTION 'AI advisory records are insert-only' USING ERRCODE='42501'; END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_advisory_insert_only() FROM PUBLIC;
CREATE TRIGGER ai_advisory_request_immutable BEFORE UPDATE OR DELETE ON impact.ai_advisory_request
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_advisory_insert_only();
CREATE TRIGGER ai_advisory_result_immutable BEFORE UPDATE OR DELETE ON impact.ai_advisory_result
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_advisory_insert_only();
ALTER TABLE impact.ai_advisory_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_advisory_request FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_advisory_request
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_advisory_result ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_advisory_result FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_advisory_result
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_advisory_request,impact.ai_advisory_result TO impact_app;
COMMIT;
