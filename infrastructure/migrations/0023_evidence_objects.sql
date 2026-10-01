BEGIN;
SET LOCAL ROLE impact_owner;
-- Object store and evidence attachments (v0.22). upload_session, file_blob and evidence_current have
-- existed since 0002 with tenant fences (0003); this migration adds the columns the implemented
-- upload, scan and evidence commands write, transition guards on the two upload tables, and three
-- insert-only registers: upload events, evidence attachments (an evidence revision cited by an exact
-- observation or calculated-result revision) and evidence content access (one row per mediated
-- download). The bytes themselves live outside the database in a private, content-addressed object
-- store; file_blob holds the SHA-256, size, object key and scan verdict. Additive only: no row is
-- rewritten, and no existing grant, policy or role changes.
ALTER TABLE impact.file_blob
 ADD COLUMN created_at timestamptz,
 ADD COLUMN scanned_at timestamptz,
 ADD COLUMN scanner varchar(64),
 ADD COLUMN scan_detail varchar(64);
ALTER TABLE impact.upload_session
 ADD COLUMN filename varchar(200),
 ADD COLUMN media_type varchar(64),
 ADD COLUMN blob_id uuid,
 ADD COLUMN created_at timestamptz,
 ADD COLUMN content_received_at timestamptz,
 ADD COLUMN completed_at timestamptz,
 ADD CONSTRAINT upload_session_blob_fk FOREIGN KEY(tenant_id,blob_id) REFERENCES impact.file_blob(tenant_id,blob_id);
ALTER TABLE impact.evidence_current
 ADD COLUMN filename varchar(200),
 ADD COLUMN media_type varchar(64),
 ADD COLUMN byte_size bigint CHECK(byte_size IS NULL OR byte_size>0);

-- A blob's identity (key, digest, size) never changes, and a verdict is final: QUARANTINED ->
-- SCANNING -> CLEAN | INFECTED | FAILED, with FAILED -> SCANNING for a retried scan. CLEAN and
-- INFECTED are never rewritten by any role.
CREATE FUNCTION impact.file_blob_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
  IF NEW.tenant_id<>OLD.tenant_id OR NEW.blob_id<>OLD.blob_id OR NEW.object_key<>OLD.object_key
     OR NEW.sha256<>OLD.sha256 OR NEW.bytes<>OLD.bytes THEN
    RAISE EXCEPTION 'file_blob identity is immutable' USING ERRCODE='23514';
  END IF;
  IF NEW.scan_state<>OLD.scan_state AND NOT (
       (OLD.scan_state='QUARANTINED' AND NEW.scan_state='SCANNING')
    OR (OLD.scan_state='FAILED' AND NEW.scan_state='SCANNING')
    OR (OLD.scan_state='SCANNING' AND NEW.scan_state IN ('CLEAN','INFECTED','FAILED'))) THEN
    RAISE EXCEPTION 'file_blob scan transition refused' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER file_blob_guard BEFORE UPDATE ON impact.file_blob FOR EACH ROW EXECUTE FUNCTION impact.file_blob_guard();
REVOKE ALL ON FUNCTION impact.file_blob_guard() FROM PUBLIC;

-- An upload's declaration (owner, purpose, size, digest, name, media type) is fixed at creation and
-- its received blob is bound once.
CREATE FUNCTION impact.upload_session_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
  IF NEW.tenant_id<>OLD.tenant_id OR NEW.upload_id<>OLD.upload_id OR NEW.owner_id<>OLD.owner_id
     OR NEW.purpose<>OLD.purpose OR NEW.mode<>OLD.mode OR NEW.expected_bytes<>OLD.expected_bytes
     OR NEW.expected_digest<>OLD.expected_digest
     OR NEW.filename IS DISTINCT FROM OLD.filename OR NEW.media_type IS DISTINCT FROM OLD.media_type
     OR (OLD.blob_id IS NOT NULL AND NEW.blob_id IS DISTINCT FROM OLD.blob_id) THEN
    RAISE EXCEPTION 'upload_session declaration is immutable' USING ERRCODE='23514';
  END IF;
  IF OLD.state IN ('CLEAN','REJECTED','CANCELLED','EXPIRED') AND NEW.state<>OLD.state THEN
    RAISE EXCEPTION 'upload_session terminal state is final' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER upload_session_guard BEFORE UPDATE ON impact.upload_session FOR EACH ROW EXECUTE FUNCTION impact.upload_session_guard();
REVOKE ALL ON FUNCTION impact.upload_session_guard() FROM PUBLIC;

-- One evidence revision cited by one exact revision of an observation or calculated result. The
-- cited record is not changed (an approved record stays immutable); a later revision of either side
-- is a new citation. Never updated or deleted.
CREATE TABLE impact.evidence_attachment(
  tenant_id uuid NOT NULL,
  attachment_id uuid NOT NULL,
  evidence_id uuid NOT NULL,
  evidence_revision uuid NOT NULL,
  evidence_revision_kind text GENERATED ALWAYS AS ('Evidence') STORED,
  target_id uuid NOT NULL,
  target_revision uuid NOT NULL,
  target_type text NOT NULL CHECK(target_type IN ('Observation','CalculatedResult')),
  reason text NOT NULL CHECK(char_length(reason) BETWEEN 1 AND 2000),
  attached_by uuid NOT NULL,
  attached_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,attachment_id),
  UNIQUE(tenant_id,evidence_revision,target_revision),
  FOREIGN KEY(tenant_id,evidence_id,evidence_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,evidence_revision,evidence_revision_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,target_id,target_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,target_revision,target_type) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,attached_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX evidence_attachment_target ON impact.evidence_attachment(tenant_id,target_id,attached_at);

-- One row per mediated content response: who read which evidence revision's bytes, when, under which
-- correlation. Never updated or deleted.
CREATE TABLE impact.evidence_access(
  tenant_id uuid NOT NULL,
  access_id uuid NOT NULL,
  evidence_id uuid NOT NULL,
  evidence_revision uuid NOT NULL,
  blob_id uuid NOT NULL,
  principal_id uuid NOT NULL,
  membership_id uuid NOT NULL,
  accessed_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,access_id),
  FOREIGN KEY(tenant_id,evidence_id,evidence_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,blob_id) REFERENCES impact.file_blob(tenant_id,blob_id),
  FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX evidence_access_evidence ON impact.evidence_access(tenant_id,evidence_id,accessed_at);

-- The history of an upload session (create, content received, sealed, scan verdict): upload sessions
-- are not registry objects, so an audit event cannot reference them; this register links each
-- audited action to its upload. Never updated or deleted.
CREATE TABLE impact.upload_event(
  tenant_id uuid NOT NULL,
  event_id uuid NOT NULL,
  upload_id uuid NOT NULL,
  action varchar(64) NOT NULL,
  outcome varchar(64) NOT NULL,
  actor_id uuid NOT NULL,
  occurred_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,event_id),
  FOREIGN KEY(tenant_id,upload_id) REFERENCES impact.upload_session(tenant_id,upload_id),
  FOREIGN KEY(tenant_id,actor_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX upload_event_upload ON impact.upload_event(tenant_id,upload_id,occurred_at);

ALTER TABLE impact.upload_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.upload_event FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.upload_event USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.evidence_attachment ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.evidence_attachment FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.evidence_attachment USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.evidence_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.evidence_access FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.evidence_access USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Insert-only for the application; nothing for the worker, identity or control plane.
GRANT SELECT,INSERT ON impact.evidence_attachment TO impact_app;
GRANT SELECT,INSERT ON impact.evidence_access TO impact_app;
GRANT SELECT,INSERT ON impact.upload_event TO impact_app;
COMMIT;
