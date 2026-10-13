BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.ai_advisory_job(
 tenant_id uuid NOT NULL,
 job_id uuid NOT NULL,
 operation_id uuid NOT NULL,
 requester_id uuid NOT NULL,
 request_fingerprint bytea NOT NULL CHECK(octet_length(request_fingerprint)=32),
 sealed_request bytea NOT NULL,
 policy_version_id uuid NOT NULL,
 estimated_units integer NOT NULL CHECK(estimated_units>0),
 requested_at timestamptz NOT NULL,
 completed_at timestamptz,
 PRIMARY KEY(tenant_id,job_id),
 UNIQUE(tenant_id,requester_id,operation_id),
 FOREIGN KEY(tenant_id,job_id) REFERENCES impact.job(tenant_id,job_id),
 FOREIGN KEY(tenant_id,requester_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,policy_version_id) REFERENCES impact.ai_policy_version(tenant_id,policy_version_id)
);
CREATE TABLE impact.ai_budget_reservation(
 tenant_id uuid NOT NULL,
 job_id uuid NOT NULL,
 policy_version_id uuid NOT NULL,
 estimated_units integer NOT NULL CHECK(estimated_units>0),
 actual_units integer CHECK(actual_units>=0),
 state text NOT NULL CHECK(state IN('RESERVED','SETTLED','RELEASED')),
 reserved_at timestamptz NOT NULL,
 settled_at timestamptz,
 PRIMARY KEY(tenant_id,job_id),
 FOREIGN KEY(tenant_id,job_id) REFERENCES impact.ai_advisory_job(tenant_id,job_id),
 FOREIGN KEY(tenant_id,policy_version_id) REFERENCES impact.ai_policy_version(tenant_id,policy_version_id),
 CHECK((state='RESERVED' AND actual_units IS NULL AND settled_at IS NULL) OR
       (state<>'RESERVED' AND actual_units IS NOT NULL AND settled_at IS NOT NULL))
);
ALTER TABLE impact.ai_advisory_job ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_advisory_job FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_advisory_job
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_budget_reservation ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_budget_reservation FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_budget_reservation
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.ai_advisory_job,impact.ai_budget_reservation TO impact_app;
COMMIT;
