BEGIN;
SET LOCAL ROLE impact_owner;

-- Tenant identifiers and due counts only. Pivot payloads remain tenant-fenced in impact.job.
CREATE FUNCTION impact.worker_pivot_tenants(at timestamptz)
 RETURNS TABLE(tenant_id uuid, due_pivots bigint)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
SELECT t.tenant_id,count(*) FROM impact.tenant_root t
 JOIN impact.job j ON j.tenant_id=t.tenant_id AND j.job_class='DASHBOARD_PIVOT'
 WHERE t.lifecycle_state='Active'
  AND ((j.state='Queued' AND j.cancellation_requested_at IS NULL)
   OR (j.state='Running' AND j.lease_expires_at<=at))
 GROUP BY t.tenant_id ORDER BY t.tenant_id
$$;
REVOKE ALL ON FUNCTION impact.worker_pivot_tenants(timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.worker_pivot_tenants(timestamptz) TO impact_worker;

COMMIT;
