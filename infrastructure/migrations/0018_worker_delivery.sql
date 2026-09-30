BEGIN;
SET LOCAL ROLE impact_owner;
-- Worker runtime and outbox dispatcher (v0.16). An outbox_delivery row stays intent, never proof of
-- delivery: only the worker records an outcome, under a generation-fenced lease. Rows written before
-- this migration (and every object.changed event) carry no channel and are never dispatched.
ALTER TABLE impact.outbox_delivery
 ADD COLUMN channel varchar(16) CHECK(channel IN ('IN_APP','EMAIL')),
 ADD COLUMN template varchar(64) CHECK(template IN ('IN_APP_NOTICE','MEMBER_INVITATION','RECOVERY_CHANNEL_VERIFICATION')),
 ADD COLUMN reference_id uuid,
 ADD COLUMN reference_generation varchar(64),
 -- The recipient address, AES-256-GCM sealed under a key derived from the delivery secret, which the
 -- database never holds; bound to tenant, template and reference. No token or code is ever stored.
 ADD COLUMN recipient_sealed bytea CHECK(octet_length(recipient_sealed) BETWEEN 29 AND 300),
 ADD COLUMN state varchar(16) NOT NULL DEFAULT 'PENDING'
  CHECK(state IN ('PENDING','LEASED','SENT','DEAD','SUPERSEDED')),
 ADD COLUMN lease_owner varchar(128),
 ADD COLUMN lease_generation bigint NOT NULL DEFAULT 0 CHECK(lease_generation>=0),
 ADD COLUMN lease_expires_at timestamptz,
 ADD COLUMN next_attempt_at timestamptz NOT NULL DEFAULT now(),
 ADD COLUMN last_attempt_at timestamptz,
 ADD COLUMN last_error_class varchar(64) CHECK(last_error_class ~ '^[A-Z][A-Z0-9_]{0,63}$'),
 ADD COLUMN completed_at timestamptz,
 ADD CONSTRAINT outbox_delivery_dispatch CHECK((channel IS NULL)=(template IS NULL) AND (channel IS NOT NULL OR state='PENDING')),
 ADD CONSTRAINT outbox_delivery_channel CHECK((template='IN_APP_NOTICE')=(channel='IN_APP') AND (channel<>'EMAIL' OR recipient_sealed IS NOT NULL)),
 ADD CONSTRAINT outbox_delivery_lease CHECK((state='LEASED')=(lease_owner IS NOT NULL AND lease_expires_at IS NOT NULL)),
 ADD CONSTRAINT outbox_delivery_terminal CHECK(channel IS NULL OR ((state IN ('SENT','DEAD','SUPERSEDED'))=(completed_at IS NOT NULL) AND (state='SENT')=(sent_at IS NOT NULL)));
CREATE INDEX outbox_delivery_due ON impact.outbox_delivery(tenant_id,next_attempt_at)
 WHERE channel IS NOT NULL AND state IN ('PENDING','LEASED') AND held_at IS NULL;
CREATE INDEX outbox_delivery_reference ON impact.outbox_delivery(tenant_id,reference_id) WHERE reference_id IS NOT NULL;
-- The application writes intents; outcomes are the worker's alone.
REVOKE UPDATE ON impact.outbox_delivery FROM impact_app;

-- Exactly-once visible effect of an in-app delivery: one row per notification and channel.
CREATE TABLE impact.notification_delivery(
 tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 notification_id uuid NOT NULL, channel varchar(16) NOT NULL CHECK(channel='IN_APP'),
 event_id uuid NOT NULL, delivered_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,notification_id,channel),
 FOREIGN KEY(tenant_id,notification_id) REFERENCES impact.notification_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,event_id) REFERENCES impact.outbox_event(tenant_id,event_id)
);
ALTER TABLE impact.notification_delivery ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.notification_delivery FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.notification_delivery USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.notification_delivery TO impact_worker;
GRANT SELECT ON impact.notification_delivery TO impact_app;

-- Recovery-contact channel verification: a single-use, expiring code, stored only as an HMAC under
-- the delivery secret. Evidence that the contact controls the registered mailbox; it changes
-- nothing a recovery contact may do. Written by the control plane; the worker only reads it to
-- recheck that a challenge is still pending before sending.
ALTER TABLE impact.tenant_recovery_contact
 ADD COLUMN channel_verified_at timestamptz,
 ADD COLUMN channel_challenge_id uuid,
 ADD CONSTRAINT tenant_recovery_contact_tenant_contact UNIQUE(tenant_id,contact_id);
CREATE TABLE impact.recovery_channel_challenge(
 tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 challenge_id uuid NOT NULL,
 contact_id uuid NOT NULL,
 contact_revision uuid NOT NULL,
 requested_by uuid NOT NULL REFERENCES impact.auth_identity,
 email_hash bytea NOT NULL CHECK(octet_length(email_hash)=32),
 code_hash bytea NOT NULL CHECK(octet_length(code_hash)=32),
 state varchar(16) NOT NULL CHECK(state IN ('PENDING','VERIFIED','EXPIRED','FAILED','SUPERSEDED')),
 attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5),
 created_at timestamptz NOT NULL DEFAULT now(), expires_at timestamptz NOT NULL,
 consumed_at timestamptz,
 PRIMARY KEY(tenant_id,challenge_id),
 FOREIGN KEY(tenant_id,contact_id) REFERENCES impact.tenant_recovery_contact(tenant_id,contact_id),
 CHECK(expires_at>created_at AND expires_at<=created_at+interval '1 hour'),
 CHECK((state='VERIFIED')=(consumed_at IS NOT NULL))
);
CREATE UNIQUE INDEX recovery_channel_one_pending ON impact.recovery_channel_challenge(contact_id) WHERE state='PENDING';
-- Serves the request rate limit (a few challenges per contact per hour).
CREATE INDEX recovery_channel_recent ON impact.recovery_channel_challenge(tenant_id,contact_id,created_at);
ALTER TABLE impact.recovery_channel_challenge ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.recovery_channel_challenge FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.recovery_channel_challenge USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.recovery_channel_challenge TO impact_platform;
GRANT SELECT ON impact.recovery_channel_challenge TO impact_worker;

-- The control plane may not write the tenant outbox; this function records exactly one email
-- intent for a pending challenge of the current tenant and nothing else.
CREATE FUNCTION impact.enqueue_recovery_channel_delivery(requested_challenge uuid, sealed bytea) RETURNS uuid
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE tenant uuid := impact.current_tenant(); event uuid := gen_random_uuid();
BEGIN
 IF tenant IS NULL OR NOT EXISTS(SELECT 1 FROM impact.recovery_channel_challenge WHERE tenant_id=tenant
  AND challenge_id=requested_challenge AND state='PENDING' AND expires_at>now()) THEN
  RAISE EXCEPTION 'challenge not pending' USING ERRCODE='42501';
 END IF;
 INSERT INTO impact.outbox_event(tenant_id,event_id,event_type,occurred_at,payload) VALUES(tenant,event,
  'delivery.requested',now(),jsonb_build_object('event_id',event,'tenant_id',tenant,'event_type','delivery.requested',
  'schema_version','1.0','channel','EMAIL','template','RECOVERY_CHANNEL_VERIFICATION',
  'reference_id',requested_challenge,'reference_generation',NULL,'occurred_at',now()));
 INSERT INTO impact.outbox_delivery(tenant_id,event_id,channel,template,reference_id,recipient_sealed)
  VALUES(tenant,event,'EMAIL','RECOVERY_CHANNEL_VERIFICATION',requested_challenge,sealed);
 RETURN event;
END $$;
REVOKE ALL ON FUNCTION impact.enqueue_recovery_channel_delivery(uuid,bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.enqueue_recovery_channel_delivery(uuid,bytea) TO impact_platform;

-- The worker discovers which tenants to visit without reading any tenant row: identifiers, lifecycle
-- state and due counts only. Everything else happens in a per-tenant transaction under tenant_fence.
-- Provisioning and Suspended tenants are listed because recovery-contact verification belongs to
-- activation and reactivation; a suspension holds (held_at) what was queued before it. A held row
-- whose lease has expired counts as due so that the worker returns it to PENDING (still held, never
-- sent): a suspension never leaves a row LEASED for ever and never replays it (v0.10 semantics).
CREATE POLICY worker_tenant_directory ON impact.tenant_root FOR SELECT TO impact_owner USING(true);
CREATE POLICY worker_dispatch_directory ON impact.outbox_delivery FOR SELECT TO impact_owner USING(true);
CREATE FUNCTION impact.worker_tenants(at timestamptz)
 RETURNS TABLE(tenant_id uuid, lifecycle_state text, due_deliveries bigint)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT t.tenant_id,t.lifecycle_state,(SELECT count(*) FROM impact.outbox_delivery d WHERE d.tenant_id=t.tenant_id
  AND d.channel IS NOT NULL AND ((d.held_at IS NULL AND d.state='PENDING' AND d.next_attempt_at<=at)
  OR (d.state='LEASED' AND d.lease_expires_at<=at)))
 FROM impact.tenant_root t WHERE t.lifecycle_state IN ('Provisioning','Active','Suspended') ORDER BY t.tenant_id
$$;
REVOKE ALL ON FUNCTION impact.worker_tenants(timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.worker_tenants(timestamptz) TO impact_worker;

-- What the worker reads and writes beyond migration 0003's grants.
GRANT SELECT ON impact.member_invitation,impact.grant_authority TO impact_worker;

-- Operator liveness signal: one row per worker process, no tenant data.
CREATE TABLE impact.worker_heartbeat(
 worker_id varchar(128) PRIMARY KEY CHECK(worker_id ~ '^[A-Za-z0-9._:-]{1,128}$'),
 build varchar(32) NOT NULL, state varchar(16) NOT NULL CHECK(state IN ('RUNNING','STOPPING','STOPPED')),
 started_at timestamptz NOT NULL, beat_at timestamptz NOT NULL, stopped_at timestamptz,
 iterations bigint NOT NULL DEFAULT 0 CHECK(iterations>=0),
 sent bigint NOT NULL DEFAULT 0 CHECK(sent>=0), retried bigint NOT NULL DEFAULT 0 CHECK(retried>=0),
 dead bigint NOT NULL DEFAULT 0 CHECK(dead>=0),
 failures bigint NOT NULL DEFAULT 0 CHECK(failures>=0),
 CHECK((state='STOPPED')=(stopped_at IS NOT NULL))
);
GRANT SELECT,INSERT,UPDATE ON impact.worker_heartbeat TO impact_worker;
GRANT SELECT ON impact.worker_heartbeat TO impact_platform;

-- One row per delegated-authority reminder the worker has created: (principal, expiry instant,
-- threshold in days). The scan excludes these in SQL, so its batch limit cannot starve later groups.
CREATE TABLE impact.authority_reminder(
 tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 principal_id uuid NOT NULL, expires_at timestamptz NOT NULL,
 threshold_days integer NOT NULL CHECK(threshold_days IN (3,14)),
 notification_id uuid NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant_id,principal_id,expires_at,threshold_days),
 FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,notification_id) REFERENCES impact.notification_current(tenant_id,object_id)
);
ALTER TABLE impact.authority_reminder ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.authority_reminder FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.authority_reminder USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.authority_reminder TO impact_worker;

-- The operator's suspension preview counts only dispatchable intents that are still open: legacy
-- object.changed rows (never dispatched) and SENT/DEAD/SUPERSEDED rows are not unsent work.
CREATE OR REPLACE FUNCTION impact.tenant_work_impact(requested_tenant uuid) RETURNS jsonb
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() THEN RAISE EXCEPTION 'tenant denied' USING ERRCODE='42501'; END IF;
 RETURN jsonb_build_object(
 'unfinished_jobs',(SELECT count(*) FROM impact.job WHERE tenant_id=requested_tenant AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled')),
 'active_schedules',(SELECT count(*) FROM impact.object_registry WHERE tenant_id=requested_tenant AND object_type='Schedule' AND lifecycle_state='Active'),
 'unsent_events',(SELECT count(*) FROM impact.outbox_delivery WHERE tenant_id=requested_tenant AND channel IS NOT NULL AND state IN ('PENDING','LEASED')),
 'retention_holds',(SELECT count(*) FROM impact.retention_hold WHERE tenant_id=requested_tenant AND released_at IS NULL));
END $$;
COMMIT;
