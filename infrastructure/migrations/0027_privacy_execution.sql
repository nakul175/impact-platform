BEGIN;
SET LOCAL ROLE impact_owner;
-- Privacy execution (v0.25 part B): data-subject requests for a member of the tenant (access export
-- and erasure propagation) and a scheduled retention sweep with an insert-only proof record.
--
-- Data-subject requests. PrivacyCase has been a registry kind with a typed projection since 0002;
-- this migration adds the payload columns the implemented case writes (the subject membership, the
-- request reason and verification note, the evidence and import batches the privacy officer names,
-- and the server-set approval, plan, execution and package fields). An erasure is an approved plan
-- of per-store actions (privacy_store_action, 0002) executed in one transaction: earlier revision
-- payloads are removed only through the SECURITY DEFINER impact.privacy_remove_revisions below,
-- under the revision_removal_guard trigger of 0003, which still requires the privacy case context,
-- an EXECUTING DATABASE/DELETE store action, a durable deletion_ledger row and no active hold.
--
-- Why a definer and a replaced guard: the guard admits only a role that holds impact_privacy, but
-- the API's login is a member of impact_app alone and a migration cannot grant role membership (the
-- migrator holds neither CREATEROLE nor ADMIN OPTION). The removal therefore runs inside
-- impact.privacy_remove_revisions, owned by impact_owner, which the guard now also admits when (and
-- only when) that definer has set its transaction-local executor marker. impact_app still holds no
-- UPDATE privilege on object_revision, so no other path reaches the trigger; every other condition
-- of the original guard is unchanged.
ALTER TABLE impact.privacy_case_current
 ADD COLUMN subject_membership_id uuid,
 ADD COLUMN subject_membership_id_kind text GENERATED ALWAYS AS ('Membership') STORED,
 ADD COLUMN subject_principal_id uuid,
 ADD COLUMN purpose varchar(64),
 ADD COLUMN reason varchar(2000),
 ADD COLUMN verification_note varchar(2000),
 ADD COLUMN evidence_ids jsonb CHECK(evidence_ids IS NULL OR jsonb_typeof(evidence_ids)='array'),
 ADD COLUMN import_ids jsonb CHECK(import_ids IS NULL OR jsonb_typeof(import_ids)='array'),
 ADD COLUMN approved_by uuid,
 ADD COLUMN approved_at timestamptz,
 ADD COLUMN approved_revision uuid,
 ADD COLUMN plan_sha256 varchar(64) CHECK(plan_sha256 IS NULL OR plan_sha256 ~ '^[0-9a-f]{64}$'),
 ADD COLUMN executed_by uuid,
 ADD COLUMN executed_at timestamptz,
 ADD COLUMN completed_at timestamptz,
 ADD COLUMN outcome varchar(32) CHECK(outcome IS NULL OR outcome IN ('COMPLETED','PARTIALLY_COMPLETED')),
 ADD COLUMN package_id uuid,
 ADD COLUMN package_sha256 varchar(64) CHECK(package_sha256 IS NULL OR package_sha256 ~ '^[0-9a-f]{64}$'),
 ADD COLUMN manifest jsonb CHECK(manifest IS NULL OR jsonb_typeof(manifest)='object'),
 ADD CONSTRAINT privacy_case_request_type CHECK(request_type IS NULL OR request_type IN ('ACCESS','ERASURE')),
 ADD CONSTRAINT privacy_case_subject_fk FOREIGN KEY(tenant_id,subject_membership_id,subject_membership_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 ADD CONSTRAINT privacy_case_subject_principal_fk FOREIGN KEY(tenant_id,subject_principal_id)
  REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

-- The export package of an approved access request: one per case, bounded, written once with its
-- SHA-256 and section manifest, and deleted by the retention sweep when it expires.
CREATE TABLE impact.privacy_export_package(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  package_id uuid NOT NULL,
  case_id uuid NOT NULL,
  case_revision uuid NOT NULL,
  subject_membership_id uuid NOT NULL,
  body bytea NOT NULL CHECK(octet_length(body) BETWEEN 2 AND 5242880),
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  manifest jsonb NOT NULL CHECK(jsonb_typeof(manifest)='object'),
  created_by uuid NOT NULL,
  created_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL CHECK(expires_at>created_at),
  PRIMARY KEY(tenant_id,package_id),
  UNIQUE(tenant_id,case_id),
  FOREIGN KEY(tenant_id,case_id) REFERENCES impact.privacy_case_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,case_id,case_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,created_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX privacy_export_package_expiry ON impact.privacy_export_package(tenant_id,expires_at);

-- One row per mediated download of an export package. No foreign key to the package: the access
-- record outlives the package's deletion. Never updated or deleted.
CREATE TABLE impact.privacy_export_access(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  access_id uuid NOT NULL,
  case_id uuid NOT NULL,
  package_id uuid NOT NULL,
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  principal_id uuid NOT NULL,
  membership_id uuid NOT NULL,
  purpose varchar(64) NOT NULL,
  accessed_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,access_id),
  FOREIGN KEY(tenant_id,case_id) REFERENCES impact.privacy_case_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);

-- Erasure bookkeeping on the stores it reaches. A redacted sealed recipient is overwritten with
-- random bytes (the address cannot be recovered even with the delivery secret); a purged blob's
-- bytes were deleted from the object store by the case that names it.
ALTER TABLE impact.outbox_delivery ADD COLUMN recipient_redacted_at timestamptz;
ALTER TABLE impact.file_blob
 ADD COLUMN purged_at timestamptz,
 ADD COLUMN purge_case_id uuid;

-- Retention sweep: job class RETENTION_SWEEP, executed by the worker under a generation-fenced
-- lease on database time, like REPORT_EXPORT (0024). The job row carries the lifecycle and lease
-- generation; this row carries the holder and attempt bookkeeping.
CREATE TABLE impact.retention_sweep(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  job_id uuid NOT NULL,
  lease_owner varchar(128),
  attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
  next_attempt_at timestamptz NOT NULL,
  last_attempt_at timestamptz,
  last_error_class varchar(64) CHECK(last_error_class IS NULL OR last_error_class ~ '^[A-Z][A-Z0-9_]{0,63}$'),
  completed_at timestamptz,
  PRIMARY KEY(tenant_id,job_id),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.job(tenant_id,job_id)
);

-- Proof of retention: one insert-only row per data class per sweep, with the policy applied, the
-- cutoff, the number of items deleted or redacted and the SHA-256 of their sorted keys. Written in
-- the same fenced transaction as the deletions it proves; never updated or deleted.
CREATE TABLE impact.retention_proof(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  proof_id uuid NOT NULL,
  job_id uuid NOT NULL,
  lease_generation bigint NOT NULL CHECK(lease_generation>0),
  data_class varchar(64) NOT NULL CHECK(data_class ~ '^[A-Z][A-Z0-9_]{0,63}$'),
  action varchar(16) NOT NULL CHECK(action IN ('DELETE','REDACT','EXPIRE')),
  retention_days integer NOT NULL CHECK(retention_days>=0),
  cutoff timestamptz NOT NULL,
  affected_count integer NOT NULL CHECK(affected_count>=0),
  items_sha256 bytea NOT NULL CHECK(octet_length(items_sha256)=32),
  executed_at timestamptz NOT NULL,
  worker_id varchar(128) NOT NULL,
  PRIMARY KEY(tenant_id,proof_id),
  UNIQUE(tenant_id,job_id,data_class),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.retention_sweep(tenant_id,job_id)
);
CREATE INDEX retention_proof_recent ON impact.retention_proof(tenant_id,executed_at);

ALTER TABLE impact.privacy_export_package ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.privacy_export_package FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.privacy_export_package USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.privacy_export_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.privacy_export_access FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.privacy_export_access USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.retention_sweep ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.retention_sweep FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.retention_sweep USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.retention_proof ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.retention_proof FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.retention_proof USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

-- The original guard of 0003, plus the definer path described above.
CREATE OR REPLACE FUNCTION impact.guard_revision_removal() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE case_ref uuid;
BEGIN
 IF NOT (pg_has_role(current_user,'impact_privacy','USAGE')
         OR (current_user='impact_owner' AND current_setting('impact.privacy_executor',true)='privacy_remove_revisions')) THEN
   RAISE EXCEPTION 'immutable revision';
 END IF;
 case_ref := nullif(current_setting('impact.privacy_case_id',true),'')::uuid;
 IF case_ref IS NULL OR NEW.tenant_id<>impact.current_tenant() THEN RAISE EXCEPTION 'privacy context required'; END IF;
 IF (to_jsonb(OLD)-'payload'-'restriction_state') IS DISTINCT FROM (to_jsonb(NEW)-'payload'-'restriction_state') THEN RAISE EXCEPTION 'immutable metadata'; END IF;
 IF NEW.payload IS NOT NULL OR NEW.restriction_state<>'REMOVED' THEN RAISE EXCEPTION 'removal only'; END IF;
 IF EXISTS(SELECT 1 FROM impact.retention_hold WHERE tenant_id=OLD.tenant_id AND object_id=OLD.object_id AND released_at IS NULL) THEN RAISE EXCEPTION 'active hold'; END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=OLD.tenant_id AND case_id=case_ref AND object_id=OLD.object_id AND store='DATABASE' AND action='DELETE' AND state='EXECUTING') THEN RAISE EXCEPTION 'approved executing plan required'; END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.deletion_ledger WHERE tenant_id=OLD.tenant_id AND case_id=case_ref AND object_id=OLD.object_id) THEN RAISE EXCEPTION 'durable ledger prerequisite'; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_revision_removal() FROM PUBLIC;

-- The upload guard of 0023, plus one transition: a declared file name may be cleared (never
-- changed) by impact.privacy_redact_uploads for an erasure case. Everything else is unchanged.
CREATE OR REPLACE FUNCTION impact.upload_session_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
  IF NEW.tenant_id<>OLD.tenant_id OR NEW.upload_id<>OLD.upload_id OR NEW.owner_id<>OLD.owner_id
     OR NEW.purpose<>OLD.purpose OR NEW.mode<>OLD.mode OR NEW.expected_bytes<>OLD.expected_bytes
     OR NEW.expected_digest<>OLD.expected_digest
     OR (NEW.filename IS DISTINCT FROM OLD.filename AND NOT (NEW.filename IS NULL AND current_user='impact_owner'
         AND current_setting('impact.privacy_executor',true)='privacy_redact_uploads'))
     OR NEW.media_type IS DISTINCT FROM OLD.media_type
     OR (OLD.blob_id IS NOT NULL AND NEW.blob_id IS DISTINCT FROM OLD.blob_id) THEN
    RAISE EXCEPTION 'upload_session declaration is immutable' USING ERRCODE='23514';
  END IF;
  IF OLD.state IN ('CLEAN','REJECTED','CANCELLED','EXPIRED') AND NEW.state<>OLD.state THEN
    RAISE EXCEPTION 'upload_session terminal state is final' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.upload_session_guard() FROM PUBLIC;

-- An erasure case that is approved (or executing) for the current tenant, or an exception.
CREATE FUNCTION impact.privacy_require_case(case_ref uuid) RETURNS void
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
  IF impact.current_tenant() IS NULL OR NOT EXISTS(
    SELECT 1 FROM impact.privacy_case_current p JOIN impact.object_registry r
      ON r.tenant_id=p.tenant_id AND r.object_id=p.object_id
     WHERE p.tenant_id=impact.current_tenant() AND p.object_id=case_ref AND p.request_type='ERASURE'
       AND p.approved_by IS NOT NULL AND r.lifecycle_state IN ('Approved','Executing')) THEN
    RAISE EXCEPTION 'approved erasure case required' USING ERRCODE='42501';
  END IF;
END $$;
REVOKE ALL ON FUNCTION impact.privacy_require_case(uuid) FROM PUBLIC;

-- Remove the payload of every revision of one object except keep_revision (the tombstone the
-- application has just written, or NULL to remove every revision), for an approved erasure case
-- whose plan names this object with an EXECUTING DATABASE/DELETE action. The deletion_ledger row is
-- written first (the guard requires it); the guard re-checks everything. Returns the number removed.
CREATE FUNCTION impact.privacy_remove_revisions(case_ref uuid, target uuid, keep_revision uuid) RETURNS integer
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE removed integer;
BEGIN
  PERFORM impact.privacy_require_case(case_ref);
  IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=impact.current_tenant()
      AND case_id=case_ref AND object_id=target AND store='DATABASE' AND action='DELETE' AND state='EXECUTING') THEN
    RAISE EXCEPTION 'approved executing plan required' USING ERRCODE='42501';
  END IF;
  INSERT INTO impact.deletion_ledger(tenant_id,entry_id,case_id,object_id,effective_at,disposition)
   SELECT impact.current_tenant(),gen_random_uuid(),case_ref,target,statement_timestamp(),
     CASE WHEN keep_revision IS NULL THEN 'ALL_REVISIONS_REMOVED' ELSE 'EARLIER_REVISIONS_REMOVED_TOMBSTONE_KEPT' END
   WHERE NOT EXISTS(SELECT 1 FROM impact.deletion_ledger WHERE tenant_id=impact.current_tenant()
     AND case_id=case_ref AND object_id=target);
  PERFORM set_config('impact.privacy_case_id',case_ref::text,true);
  PERFORM set_config('impact.privacy_executor','privacy_remove_revisions',true);
  UPDATE impact.object_revision SET payload=NULL,restriction_state='REMOVED'
   WHERE tenant_id=impact.current_tenant() AND object_id=target AND restriction_state<>'REMOVED'
     AND (keep_revision IS NULL OR revision_id<>keep_revision);
  GET DIAGNOSTICS removed = ROW_COUNT;
  PERFORM set_config('impact.privacy_executor','',true);
  RETURN removed;
END $$;
REVOKE ALL ON FUNCTION impact.privacy_remove_revisions(uuid,uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.privacy_remove_revisions(uuid,uuid,uuid) TO impact_app;

-- Clear the declared file name of the uploads one evidence object was built from, for an approved
-- erasure case whose plan names that evidence with an EXECUTING PROJECTION/REDACT action. Must run
-- before the evidence revisions are removed (it finds the uploads through their payloads).
CREATE FUNCTION impact.privacy_redact_uploads(case_ref uuid, target uuid) RETURNS integer
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE redacted integer;
BEGIN
  PERFORM impact.privacy_require_case(case_ref);
  IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=impact.current_tenant()
      AND case_id=case_ref AND object_id=target AND store='PROJECTION' AND action='REDACT' AND state='EXECUTING') THEN
    RAISE EXCEPTION 'approved executing plan required' USING ERRCODE='42501';
  END IF;
  PERFORM set_config('impact.privacy_executor','privacy_redact_uploads',true);
  UPDATE impact.upload_session u SET filename=NULL
   WHERE u.tenant_id=impact.current_tenant() AND u.filename IS NOT NULL AND u.upload_id IN (
     SELECT (v.payload->>'upload_id')::uuid FROM impact.object_revision v
      WHERE v.tenant_id=impact.current_tenant() AND v.object_id=target AND v.object_type='Evidence'
        AND v.payload ? 'upload_id');
  GET DIAGNOSTICS redacted = ROW_COUNT;
  PERFORM set_config('impact.privacy_executor','',true);
  RETURN redacted;
END $$;
REVOKE ALL ON FUNCTION impact.privacy_redact_uploads(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.privacy_redact_uploads(uuid,uuid) TO impact_app;

-- Supersede the open delivery intents that reference one object (an invitation or a notice of the
-- subject) and overwrite every sealed recipient address they carry, for an approved erasure case
-- whose plan names that reference with an EXECUTING OUTBOX/SUPERSEDE action. The lease generation
-- advances, so a worker holding one of these rows cannot record an outcome for it.
CREATE FUNCTION impact.privacy_supersede_deliveries(case_ref uuid, reference uuid) RETURNS integer
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE superseded integer; redacted integer;
BEGIN
  PERFORM impact.privacy_require_case(case_ref);
  IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=impact.current_tenant()
      AND case_id=case_ref AND object_id=reference AND store='OUTBOX' AND action='SUPERSEDE' AND state='EXECUTING') THEN
    RAISE EXCEPTION 'approved executing plan required' USING ERRCODE='42501';
  END IF;
  UPDATE impact.outbox_delivery SET state='SUPERSEDED',lease_owner=NULL,lease_expires_at=NULL,
    lease_generation=lease_generation+1,last_error_class='SUBJECT_ERASED',completed_at=statement_timestamp()
   WHERE tenant_id=impact.current_tenant() AND reference_id=reference AND channel IS NOT NULL
     AND state IN ('PENDING','LEASED');
  GET DIAGNOSTICS superseded = ROW_COUNT;
  UPDATE impact.outbox_delivery SET recipient_sealed=sha256(convert_to(gen_random_uuid()::text,'UTF8')),
    recipient_redacted_at=statement_timestamp()
   WHERE tenant_id=impact.current_tenant() AND reference_id=reference AND channel='EMAIL'
     AND recipient_redacted_at IS NULL;
  GET DIAGNOSTICS redacted = ROW_COUNT;
  RETURN superseded+redacted;
END $$;
REVOKE ALL ON FUNCTION impact.privacy_supersede_deliveries(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.privacy_supersede_deliveries(uuid,uuid) TO impact_app;

-- Retention definers for the worker, which holds no privilege on operation_receipt or
-- upload_session (0025). Each acts on the current tenant only, compares with the database clock
-- (never a cutoff the caller supplies) and returns the keys it affected, for the proof digest.
CREATE FUNCTION impact.retention_purge_receipts(max_rows integer) RETURNS TABLE(item text)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DELETE FROM impact.operation_receipt o USING (
  SELECT tenant_id,actor_id,command_type,operation_id FROM impact.operation_receipt
   WHERE tenant_id=impact.current_tenant() AND expires_at<=statement_timestamp()
   ORDER BY expires_at,operation_id LIMIT greatest(least(max_rows,5000),0)) d
 WHERE o.tenant_id=d.tenant_id AND o.actor_id=d.actor_id AND o.command_type=d.command_type
   AND o.operation_id=d.operation_id
 RETURNING o.actor_id::text||':'||o.command_type||':'||o.operation_id::text
$$;
REVOKE ALL ON FUNCTION impact.retention_purge_receipts(integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.retention_purge_receipts(integer) TO impact_worker;

CREATE FUNCTION impact.retention_expire_uploads(max_rows integer) RETURNS TABLE(item text)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
UPDATE impact.upload_session u SET state='EXPIRED' FROM (
  SELECT tenant_id,upload_id FROM impact.upload_session
   WHERE tenant_id=impact.current_tenant() AND state='OPEN' AND expires_at<=statement_timestamp()
   ORDER BY expires_at,upload_id LIMIT greatest(least(max_rows,5000),0)) d
 WHERE u.tenant_id=d.tenant_id AND u.upload_id=d.upload_id
 RETURNING u.upload_id::text
$$;
REVOKE ALL ON FUNCTION impact.retention_expire_uploads(integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.retention_expire_uploads(integer) TO impact_worker;

-- Schedule one RETENTION_SWEEP job for the current tenant when none is queued or running and none
-- completed within the interval. The requester is the tenant's SERVICE principal (no identity), the
-- scope its TENANT scope. Returns the new job, or NULL when nothing is due.
CREATE FUNCTION impact.worker_schedule_retention(service_principal uuid, interval_seconds integer) RETURNS uuid
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE v_tenant uuid := impact.current_tenant(); v_scope uuid; v_job uuid;
BEGIN
  IF v_tenant IS NULL OR interval_seconds<60 THEN RAISE EXCEPTION 'tenant context required' USING ERRCODE='42501'; END IF;
  IF NOT EXISTS(SELECT 1 FROM impact.tenant_principal p WHERE p.tenant_id=v_tenant AND p.principal_id=service_principal
      AND p.principal_kind='SERVICE' AND p.identity_id IS NULL) THEN
    RAISE EXCEPTION 'service principal required' USING ERRCODE='42501';
  END IF;
  IF EXISTS(SELECT 1 FROM impact.job j LEFT JOIN impact.retention_sweep s ON s.tenant_id=j.tenant_id AND s.job_id=j.job_id
      WHERE j.tenant_id=v_tenant AND j.job_class='RETENTION_SWEEP' AND (j.state IN ('Queued','Running')
        OR (s.completed_at IS NOT NULL AND s.completed_at>statement_timestamp()-make_interval(secs=>interval_seconds)))) THEN
    RETURN NULL;
  END IF;
  SELECT d.scope_id INTO v_scope FROM impact.scope_definition d WHERE d.tenant_id=v_tenant AND d.scope_type='TENANT'
   ORDER BY d.scope_id LIMIT 1;
  IF v_scope IS NULL THEN RETURN NULL; END IF;
  v_job := gen_random_uuid();
  INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest)
   VALUES(v_tenant,v_job,'RETENTION_SWEEP',service_principal,v_scope,'Queued',
     jsonb_build_object('scheduled_at',statement_timestamp(),'interval_seconds',interval_seconds));
  INSERT INTO impact.retention_sweep(tenant_id,job_id,next_attempt_at) VALUES(v_tenant,v_job,statement_timestamp());
  RETURN v_job;
END $$;
REVOKE ALL ON FUNCTION impact.worker_schedule_retention(uuid,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.worker_schedule_retention(uuid,integer) TO impact_worker;

-- Application: case packages, access log and read-only views of the sweep and its proof.
GRANT SELECT,INSERT ON impact.privacy_export_package TO impact_app;
GRANT SELECT,INSERT ON impact.privacy_export_access TO impact_app;
GRANT SELECT ON impact.retention_sweep,impact.retention_proof TO impact_app;
-- Worker: exactly what the RETENTION_SWEEP job class uses (worker.py). It already holds SELECT and
-- UPDATE on job, SELECT and INSERT on job_item (0024) and SELECT, INSERT and UPDATE on
-- outbox_delivery (0003/0018); receipts and uploads are reached only through the definers above.
GRANT SELECT,UPDATE ON impact.retention_sweep TO impact_worker;
GRANT SELECT,INSERT ON impact.retention_proof TO impact_worker;
GRANT SELECT,DELETE ON impact.privacy_export_package TO impact_worker;
COMMIT;
