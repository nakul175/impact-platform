BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.ai_advisory_job
 ADD COLUMN started_at timestamptz,
 ADD COLUMN deadline_at timestamptz,
 ADD COLUMN attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
 ADD COLUMN lease_owner text CHECK(lease_owner IS NULL OR lease_owner~'^[A-Za-z0-9._:-]{1,120}$'),
 ADD COLUMN last_error_class text CHECK(last_error_class IS NULL OR last_error_class~'^[A-Z][A-Z0-9_]{0,99}$');

CREATE TABLE impact.ai_advisory_job_output(
 tenant_id uuid NOT NULL,
 job_id uuid NOT NULL,
 outcome text NOT NULL CHECK(outcome IN('SUCCEEDED','TIMED_OUT','CANCELLED','FAILED')),
 complete boolean NOT NULL,
 label text NOT NULL,
 sealed_output bytea,
 output_sha256 bytea CHECK(output_sha256 IS NULL OR octet_length(output_sha256)=32),
 model_identifier text,
 actual_units integer NOT NULL CHECK(actual_units>=0),
 created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,job_id),
 FOREIGN KEY(tenant_id,job_id) REFERENCES impact.ai_advisory_job(tenant_id,job_id),
 CHECK((complete AND outcome='SUCCEEDED' AND label='Advisory draft' AND sealed_output IS NOT NULL)
    OR (NOT complete AND outcome<>'SUCCEEDED' AND label='Incomplete draft')),
 CHECK((sealed_output IS NULL)=(output_sha256 IS NULL))
);
ALTER TABLE impact.ai_advisory_job_output ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_advisory_job_output FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_advisory_job_output
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,UPDATE ON impact.ai_advisory_job,impact.ai_budget_reservation TO impact_worker;
GRANT SELECT,INSERT ON impact.ai_advisory_job_output TO impact_worker;
GRANT SELECT ON impact.ai_advisory_job_output TO impact_app;

CREATE FUNCTION impact.worker_ai_tenants(at timestamptz)
RETURNS TABLE(tenant_id uuid,due_jobs bigint)
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact
AS $$
 SELECT j.tenant_id,count(*)
 FROM impact.job j JOIN impact.tenant t ON t.tenant_id=j.tenant_id
 WHERE t.lifecycle_state='Active' AND j.job_class='AI_ADVISORY'
   AND ((j.state='Queued' AND j.cancellation_requested_at IS NULL)
     OR (j.state='Running' AND j.lease_expires_at<=at))
 GROUP BY j.tenant_id
$$;
REVOKE ALL ON FUNCTION impact.worker_ai_tenants(timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.worker_ai_tenants(timestamptz) TO impact_worker;

COMMIT;
