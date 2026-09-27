BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.disclosure_current
  ADD COLUMN published_at timestamptz,
  ADD COLUMN withdrawn_at timestamptz,
  ADD COLUMN withdrawal_reason varchar(2000);

CREATE TABLE impact.report_publication_artifact(
  tenant_id uuid NOT NULL,
  disclosure_id uuid NOT NULL,
  disclosure_revision uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('HTML','CSV')),
  media_type text NOT NULL,
  body bytea NOT NULL CHECK(octet_length(body)<=5242880),
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,disclosure_id,format),
  CHECK((format='HTML' AND media_type='text/html; charset=utf-8')
    OR (format='CSV' AND media_type='text/csv; charset=utf-8')),
  FOREIGN KEY(tenant_id,disclosure_id,disclosure_revision)
    REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,report_id,report_revision)
    REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);

CREATE INDEX report_publication_artifact_report
  ON impact.report_publication_artifact(tenant_id,report_id,report_revision);

CREATE TABLE impact.report_publication_access(
  tenant_id uuid NOT NULL,
  access_id uuid NOT NULL,
  disclosure_id uuid NOT NULL,
  recipient_id uuid NOT NULL,
  membership_id uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('HTML','CSV')),
  access_mode text NOT NULL CHECK(access_mode IN ('VIEW','DOWNLOAD')),
  accessed_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,access_id),
  CHECK((format='HTML' AND access_mode='VIEW')
    OR (format='CSV' AND access_mode='DOWNLOAD')),
  FOREIGN KEY(tenant_id,disclosure_id) REFERENCES impact.disclosure_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,recipient_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
  FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id)
);

ALTER TABLE impact.report_publication_artifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_artifact FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_access FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.report_publication_artifact
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.report_publication_access
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT ON impact.report_publication_artifact TO impact_app;
GRANT INSERT ON impact.report_publication_access TO impact_app;

COMMIT;
