BEGIN;
SET LOCAL ROLE impact_owner;
-- Report exports (v0.23): PDF, XLSX and DOCX renderings of an approved, frozen report package,
-- produced by the worker as its first executed job class. A request writes one impact.job row
-- (job_class REPORT_EXPORT, state Queued) and one report_export row in the business transaction;
-- the worker claims due rows under a generation-fenced lease on the database clock, renders outside
-- any transaction and stores the artifact in a fenced outcome transaction. Artifacts are insert-only
-- and immutable; a disclosure binds the exact artifacts it was approved with, never re-pointed.
-- Nothing here depends on migrations 0022, 0023 or 0025.

-- Server-resolved export artifacts a disclosure names (the requester names formats; the server pins
-- each to the exact artifact before review). Payload columns of the Disclosure projection.
ALTER TABLE impact.disclosure_current
 ADD COLUMN export_formats jsonb CHECK(export_formats IS NULL OR jsonb_typeof(export_formats)='array'),
 ADD COLUMN export_artifacts jsonb CHECK(export_artifacts IS NULL OR jsonb_typeof(export_artifacts)='array');

-- The export-specific lease state of a REPORT_EXPORT job. The job row carries the lifecycle state,
-- lease generation, lease expiry and cancellation request; this row the pinned package, the lease
-- owner, attempts, backoff and the error class (never a message).
CREATE TABLE impact.report_export(
  tenant_id uuid NOT NULL,
  job_id uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  report_revision_kind text GENERATED ALWAYS AS ('Report') STORED,
  format text NOT NULL CHECK(format IN ('PDF','XLSX','DOCX')),
  renderer_version varchar(32) NOT NULL CHECK(renderer_version ~ '^[a-z0-9.-]{1,32}$'),
  reconciliation_digest bytea NOT NULL CHECK(octet_length(reconciliation_digest)=32),
  requested_by uuid NOT NULL,
  requested_at timestamptz NOT NULL,
  attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
  next_attempt_at timestamptz NOT NULL,
  lease_owner varchar(128) CHECK(lease_owner ~ '^[A-Za-z0-9._:-]{1,128}$'),
  last_attempt_at timestamptz,
  last_error_class varchar(64) CHECK(last_error_class ~ '^[A-Z0-9_]{1,64}$'),
  completed_at timestamptz,
  PRIMARY KEY(tenant_id,job_id),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.job(tenant_id,job_id),
  FOREIGN KEY(tenant_id,report_id,report_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,report_revision,report_revision_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,report_id,report_revision) REFERENCES impact.report_package_binding(tenant_id,report_id,report_revision),
  FOREIGN KEY(tenant_id,requested_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX report_export_report ON impact.report_export(tenant_id,report_id,report_revision,format);
CREATE INDEX report_export_due ON impact.report_export(tenant_id,next_attempt_at) WHERE completed_at IS NULL;

-- One immutable artifact per successful export job: written once by the worker's fenced outcome.
CREATE TABLE impact.report_export_artifact(
  tenant_id uuid NOT NULL,
  job_id uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('PDF','XLSX','DOCX')),
  renderer_version varchar(32) NOT NULL,
  media_type text NOT NULL,
  body bytea NOT NULL CHECK(octet_length(body) BETWEEN 1 AND 10485760),
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  lease_generation bigint NOT NULL CHECK(lease_generation>0),
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,job_id),
  CHECK((format='PDF' AND media_type='application/pdf')
    OR (format='XLSX' AND media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    OR (format='DOCX' AND media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.report_export(tenant_id,job_id),
  FOREIGN KEY(tenant_id,report_id,report_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);

-- The export artifacts a published disclosure delivers: one row per format, written in the publish
-- transaction from the artifacts the reviewed disclosure pinned, never re-pointed.
CREATE TABLE impact.report_publication_export(
  tenant_id uuid NOT NULL,
  disclosure_id uuid NOT NULL,
  disclosure_revision uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('PDF','XLSX','DOCX')),
  job_id uuid NOT NULL,
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,disclosure_id,format),
  FOREIGN KEY(tenant_id,disclosure_id,disclosure_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.report_export_artifact(tenant_id,job_id)
);

-- Every mediated download of an export artifact: internal (report.export) or by a named recipient.
CREATE TABLE impact.report_export_access(
  tenant_id uuid NOT NULL,
  access_id uuid NOT NULL,
  job_id uuid NOT NULL,
  disclosure_id uuid,
  principal_id uuid NOT NULL,
  membership_id uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('PDF','XLSX','DOCX')),
  access_mode text NOT NULL CHECK(access_mode IN ('INTERNAL_DOWNLOAD','RECIPIENT_DOWNLOAD')),
  accessed_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,access_id),
  CHECK((disclosure_id IS NULL)=(access_mode='INTERNAL_DOWNLOAD')),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.report_export_artifact(tenant_id,job_id),
  FOREIGN KEY(tenant_id,disclosure_id) REFERENCES impact.disclosure_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
  FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id)
);

ALTER TABLE impact.report_export ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export_artifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export_artifact FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_export ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_export FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export_access FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.report_export USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.report_export_artifact USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.report_publication_export USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.report_export_access USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

-- The worker's directory of tenants with due export jobs (identifiers and counts only), read by the
-- definer through owner-only SELECT policies, as impact.worker_tenants reads outbox_delivery (0018).
CREATE POLICY worker_export_directory ON impact.job FOR SELECT TO impact_owner USING(true);
CREATE POLICY worker_export_directory ON impact.report_export FOR SELECT TO impact_owner USING(true);
CREATE FUNCTION impact.worker_export_tenants(at timestamptz)
 RETURNS TABLE(tenant_id uuid, due_exports bigint)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
SELECT t.tenant_id,count(*) FROM impact.tenant_root t
 JOIN impact.job j ON j.tenant_id=t.tenant_id AND j.job_class='REPORT_EXPORT'
 JOIN impact.report_export e ON e.tenant_id=j.tenant_id AND e.job_id=j.job_id
 WHERE t.lifecycle_state='Active'
  AND ((j.state='Queued' AND j.cancellation_requested_at IS NULL AND e.next_attempt_at<=at)
   OR (j.state='Running' AND j.lease_expires_at<=at))
 GROUP BY t.tenant_id ORDER BY t.tenant_id
$$;
REVOKE ALL ON FUNCTION impact.worker_export_tenants(timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.worker_export_tenants(timestamptz) TO impact_worker;

-- Application: request, status, internal download, publication binding and access log.
GRANT SELECT,INSERT ON impact.report_export TO impact_app;
GRANT SELECT ON impact.report_export_artifact TO impact_app;
GRANT SELECT,INSERT ON impact.report_publication_export TO impact_app;
GRANT INSERT ON impact.report_export_access TO impact_app;

-- Worker: exactly what export execution needs, stated explicitly so that a later narrowing of the
-- broad 0003 worker grants can keep them (job and job_item are also granted by 0003).
GRANT SELECT,UPDATE ON impact.job TO impact_worker;
GRANT SELECT,INSERT ON impact.job_item TO impact_worker;
GRANT SELECT,UPDATE ON impact.report_export TO impact_worker;
GRANT SELECT,INSERT ON impact.report_export_artifact TO impact_worker;
GRANT SELECT ON impact.report_package_binding,impact.object_revision TO impact_worker;
COMMIT;
