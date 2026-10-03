BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.import_job_current ADD COLUMN commit_request jsonb;

-- The application executor uses a separate LOGIN with membership in impact_app only. It never
-- receives the migration or worker role. This register tracks one governed import commit job.
CREATE TABLE impact.import_commit(
  tenant_id uuid NOT NULL,
  job_id uuid NOT NULL,
  import_id uuid NOT NULL,
  requested_by uuid NOT NULL,
  attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
  next_attempt_at timestamptz NOT NULL DEFAULT statement_timestamp(),
  lease_owner varchar(128) CHECK(lease_owner ~ '^[A-Za-z0-9._:-]{1,128}$'),
  last_attempt_at timestamptz,
  last_error_class varchar(64) CHECK(last_error_class ~ '^[A-Z0-9_]{1,64}$'),
  completed_at timestamptz,
  PRIMARY KEY(tenant_id,job_id),
  UNIQUE(tenant_id,import_id),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.job(tenant_id,job_id),
  FOREIGN KEY(tenant_id,import_id) REFERENCES impact.import_job_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,requested_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX import_commit_due ON impact.import_commit(tenant_id,next_attempt_at)
  WHERE completed_at IS NULL;
ALTER TABLE impact.import_commit ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.import_commit FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.import_commit
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.import_commit TO impact_app;

-- The owner-side directory returns only identifiers for Active tenants with due application jobs.
-- Tenant rows and job payloads remain behind their forced RLS fences.
CREATE POLICY executor_import_directory ON impact.import_commit FOR SELECT TO impact_owner USING(true);
CREATE FUNCTION impact.executor_due_tenants(at timestamptz)
 RETURNS TABLE(tenant_id uuid) LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,impact AS $$
 SELECT DISTINCT t.tenant_id FROM impact.tenant_root t
 JOIN impact.job j ON j.tenant_id=t.tenant_id AND j.job_class='IMPORT_COMMIT'
 JOIN impact.import_commit i ON i.tenant_id=j.tenant_id AND i.job_id=j.job_id
 WHERE t.lifecycle_state='Active' AND
   ((j.state='Queued' AND j.cancellation_requested_at IS NULL AND i.next_attempt_at<=at)
    OR (j.state='Running' AND j.lease_expires_at<=at))
 ORDER BY t.tenant_id
$$;
REVOKE ALL ON FUNCTION impact.executor_due_tenants(timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.executor_due_tenants(timestamptz) TO impact_app;

-- Process health is operational metadata, never a tenant data read or an approval identity.
CREATE TABLE impact.executor_heartbeat(
 executor_id varchar(128) PRIMARY KEY CHECK(executor_id ~ '^[A-Za-z0-9._:-]{1,128}$'),
 build varchar(32) NOT NULL,
 state text NOT NULL CHECK(state IN ('RUNNING','STOPPING','STOPPED')),
 started_at timestamptz NOT NULL,
 beat_at timestamptz NOT NULL,
 stopped_at timestamptz,
 iterations bigint NOT NULL DEFAULT 0,
 succeeded bigint NOT NULL DEFAULT 0,
 failed bigint NOT NULL DEFAULT 0,
 failures bigint NOT NULL DEFAULT 0
);
GRANT SELECT,INSERT,UPDATE ON impact.executor_heartbeat TO impact_app;
GRANT SELECT ON impact.executor_heartbeat TO impact_platform;
COMMIT;
