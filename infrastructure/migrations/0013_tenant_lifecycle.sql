BEGIN;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_platform') THEN
 CREATE ROLE impact_platform NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
END IF; END $$;
GRANT USAGE ON SCHEMA impact TO impact_platform;
SET LOCAL ROLE impact_owner;
GRANT EXECUTE ON FUNCTION impact.current_tenant() TO impact_platform;

-- Provisioned by deployment administration, never writable by HTTP runtime roles.
CREATE TABLE impact.platform_operator(
 identity_id uuid PRIMARY KEY REFERENCES impact.auth_identity,
 active boolean NOT NULL DEFAULT true, expires_at timestamptz NOT NULL,
 authority_reference varchar(300) NOT NULL
);
CREATE TABLE impact.deployment_qualification(
 qualification_id uuid PRIMARY KEY, revision_id uuid NOT NULL,
 environment varchar(20) NOT NULL, region varchar(80) NOT NULL,
 issuer text NOT NULL, required_acr varchar(200) NOT NULL,
 privacy_reference varchar(300) NOT NULL, recovery_reference varchar(300) NOT NULL,
 retention_max_days integer NOT NULL CHECK(retention_max_days BETWEEN 1 AND 36500),
 valid_until timestamptz NOT NULL, active boolean NOT NULL DEFAULT true
);
CREATE TABLE impact.tenant_onboarding(
 tenant_id uuid PRIMARY KEY REFERENCES impact.tenant_root,
 revision_id uuid NOT NULL, requested_by uuid NOT NULL REFERENCES impact.auth_identity,
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 qualification_id uuid NOT NULL REFERENCES impact.deployment_qualification,
 qualification_revision uuid NOT NULL,
 operating_name varchar(200) NOT NULL, reporting_zone varchar(80) NOT NULL,
 retention_days integer NOT NULL CHECK(retention_days BETWEEN 1 AND 36500),
 privacy_reference varchar(300) NOT NULL,
 owner_accepted_at timestamptz, owner_expires_at timestamptz NOT NULL,
 owner_membership_id uuid, tenant_object_id uuid,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE impact.platform_event(
 event_id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 action varchar(50) NOT NULL, revision_id uuid NOT NULL, reason varchar(1000) NOT NULL,
 payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE impact.platform_receipt(
 identity_id uuid NOT NULL REFERENCES impact.auth_identity, operation_id uuid NOT NULL,
 fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
 response jsonb NOT NULL, expires_at timestamptz NOT NULL,
 PRIMARY KEY(identity_id,operation_id)
);
CREATE FUNCTION impact.lock_platform_operator(actor uuid) RETURNS boolean LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(SELECT 1 FROM impact.platform_operator WHERE identity_id=actor AND active AND expires_at>now() FOR SHARE)
$$;
CREATE FUNCTION impact.lock_deployment_qualification(requested uuid) RETURNS SETOF impact.deployment_qualification LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT * FROM impact.deployment_qualification WHERE qualification_id=requested FOR SHARE
$$;
REVOKE ALL ON FUNCTION impact.lock_platform_operator(uuid),impact.lock_deployment_qualification(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.lock_platform_operator(uuid),impact.lock_deployment_qualification(uuid) TO impact_platform;
GRANT SELECT ON impact.platform_operator,impact.deployment_qualification,impact.auth_identity,impact.identity_profile TO impact_platform;
GRANT SELECT,INSERT,UPDATE ON impact.tenant_onboarding TO impact_platform;
GRANT SELECT,INSERT ON impact.platform_event,impact.platform_receipt TO impact_platform;
GRANT SELECT,INSERT,UPDATE ON impact.tenant_root,impact.tenant_principal,impact.object_registry,
 impact.tenant_current,impact.membership_current,impact.retention_policy_current TO impact_platform;
GRANT SELECT,INSERT ON impact.object_revision,impact.tenant_custody,impact.member_profile TO impact_platform;
-- Tenant-scoped metadata only; operators do not gain business-record access.
CREATE POLICY platform_registry_types ON impact.object_registry AS RESTRICTIVE TO impact_platform
 USING(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy'))
 WITH CHECK(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy'));
CREATE POLICY platform_revision_types ON impact.object_revision AS RESTRICTIVE TO impact_platform
 USING(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy'))
 WITH CHECK(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy'));
REVOKE INSERT,UPDATE ON impact.tenant_root FROM impact_app,impact_worker;
GRANT UPDATE(policy_epoch) ON impact.tenant_root TO impact_app,impact_worker;

ALTER TABLE impact.outbox_delivery ADD COLUMN held_at timestamptz;
ALTER TABLE impact.webhook_delivery ADD COLUMN held_at timestamptz;
-- No payloads are returned and only an already-fenced tenant can be quiesced.
CREATE FUNCTION impact.quiesce_tenant(requested_tenant uuid) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() OR NOT EXISTS(
 SELECT 1 FROM impact.tenant_root WHERE tenant_id=requested_tenant AND lifecycle_state IN ('Suspended','Closing'))
 THEN RAISE EXCEPTION 'tenant not fenced' USING ERRCODE='42501'; END IF;
 UPDATE impact.job SET cancellation_requested_at=now(),
 state=CASE WHEN state IN ('Requested','Validating','Queued') THEN 'Cancelled' ELSE 'Cancelling' END,
 lease_generation=lease_generation+1
 WHERE tenant_id=requested_tenant AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled');
 UPDATE impact.outbox_delivery SET held_at=COALESCE(held_at,now()) WHERE tenant_id=requested_tenant AND sent_at IS NULL;
 UPDATE impact.webhook_delivery SET held_at=COALESCE(held_at,now()) WHERE tenant_id=requested_tenant;
 -- Keep schedule revisions intact: an explicit operational hold survives reactivation.
 INSERT INTO impact.tenant_schedule_hold(tenant_id,schedule_id)
 SELECT tenant_id,object_id FROM impact.object_registry WHERE tenant_id=requested_tenant
 AND object_type='Schedule' AND lifecycle_state='Active' ON CONFLICT DO NOTHING;
END $$;
CREATE TABLE impact.tenant_schedule_hold(
 tenant_id uuid NOT NULL, schedule_id uuid NOT NULL, held_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant_id,schedule_id), FOREIGN KEY(tenant_id,schedule_id) REFERENCES impact.object_registry
);
ALTER TABLE impact.tenant_schedule_hold ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_schedule_hold FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_schedule_hold USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT ON impact.tenant_schedule_hold TO impact_app,impact_worker;
REVOKE ALL ON FUNCTION impact.quiesce_tenant(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.quiesce_tenant(uuid) TO impact_platform;
CREATE FUNCTION impact.tenant_work_impact(requested_tenant uuid) RETURNS jsonb
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() THEN RAISE EXCEPTION 'tenant denied' USING ERRCODE='42501'; END IF;
 RETURN jsonb_build_object(
 'unfinished_jobs',(SELECT count(*) FROM impact.job WHERE tenant_id=requested_tenant AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled')),
 'active_schedules',(SELECT count(*) FROM impact.object_registry WHERE tenant_id=requested_tenant AND object_type='Schedule' AND lifecycle_state='Active'),
 'unsent_events',(SELECT count(*) FROM impact.outbox_delivery WHERE tenant_id=requested_tenant AND sent_at IS NULL),
 'retention_holds',(SELECT count(*) FROM impact.retention_hold WHERE tenant_id=requested_tenant AND released_at IS NULL));
END $$;
REVOKE ALL ON FUNCTION impact.tenant_work_impact(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.tenant_work_impact(uuid) TO impact_platform;
CREATE FUNCTION impact.sync_onboarding_custody() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 UPDATE impact.tenant_onboarding SET owner_membership_id=NEW.owner_membership_id,
 owner_identity_id=(SELECT identity_id FROM impact.membership_current WHERE tenant_id=NEW.tenant_id AND object_id=NEW.owner_membership_id),
 revision_id=gen_random_uuid(),updated_at=now() WHERE tenant_id=NEW.tenant_id;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.sync_onboarding_custody() FROM PUBLIC;
CREATE TRIGGER onboarding_custody AFTER UPDATE ON impact.tenant_custody FOR EACH ROW EXECUTE FUNCTION impact.sync_onboarding_custody();
COMMIT;
