-- Durable, exact-operation records for authorised calculation attempts that fail after validation.
BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.calculation_failure(
 tenant_id uuid NOT NULL,
 operation_id uuid NOT NULL,
 actor_id uuid NOT NULL,
 indicator_id uuid NOT NULL,
 indicator_revision uuid NOT NULL,
 period_id uuid NOT NULL,
 definition_revision uuid NOT NULL,
 payload_hash bytea NOT NULL CHECK(octet_length(payload_hash)=32),
 input_manifest jsonb NOT NULL CHECK(jsonb_typeof(input_manifest)='object'),
 error_code varchar(64) NOT NULL CHECK(error_code ~ '^[A-Z][A-Z0-9_]{0,63}$'),
 error_status smallint NOT NULL CHECK(error_status BETWEEN 400 AND 599),
 error_message varchar(500) NOT NULL CHECK(length(btrim(error_message))>0),
 reason_code varchar(64) CHECK(reason_code IS NULL OR reason_code ~ '^[A-Z][A-Z0-9_]{0,63}$'),
 failed_at timestamptz NOT NULL,
 correlation_id uuid NOT NULL,
 expires_at timestamptz NOT NULL CHECK(expires_at>failed_at),
 PRIMARY KEY(tenant_id,actor_id,operation_id),
 FOREIGN KEY(tenant_id,actor_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,indicator_revision) REFERENCES impact.object_revision(tenant_id,revision_id),
 FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,definition_revision) REFERENCES impact.object_revision(tenant_id,revision_id)
);
CREATE INDEX calculation_failure_latest
 ON impact.calculation_failure(tenant_id,indicator_id,period_id,failed_at DESC);
ALTER TABLE impact.calculation_failure ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.calculation_failure FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.calculation_failure
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.calculation_failure TO impact_app;

CREATE FUNCTION impact.guard_calculation_failure_immutable() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 RAISE EXCEPTION 'calculation failure records are immutable' USING ERRCODE='42501';
END;
$$;
REVOKE ALL ON FUNCTION impact.guard_calculation_failure_immutable() FROM PUBLIC;
CREATE TRIGGER calculation_failure_immutable BEFORE UPDATE OR DELETE ON impact.calculation_failure
 FOR EACH ROW EXECUTE FUNCTION impact.guard_calculation_failure_immutable();

COMMIT;
