BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.tenant_access_bootstrap(
 request_id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES impact.tenant_onboarding,
 revision_id uuid NOT NULL, state varchar(20) NOT NULL CHECK(state IN ('Requested','Accepted','Applied','Rejected','Cancelled')),
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 second_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 tenant_revision uuid NOT NULL, owner_revision uuid NOT NULL,
 manifest jsonb NOT NULL, profile_hash varchar(64) NOT NULL,
 expires_at timestamptz NOT NULL, review_expires_at timestamptz NOT NULL,
 owner_auth_time timestamptz NOT NULL, second_auth_time timestamptz,
 accepted_at timestamptz, approved_by uuid REFERENCES impact.auth_identity,
 scope_id uuid, second_membership_id uuid,
 reason varchar(1000) NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK(owner_identity_id<>second_identity_id)
);
CREATE UNIQUE INDEX bootstrap_one_live ON impact.tenant_access_bootstrap(tenant_id)
 WHERE state IN ('Requested','Accepted','Applied');
CREATE TABLE impact.tenant_access_bootstrap_applied(
 tenant_id uuid PRIMARY KEY REFERENCES impact.tenant_onboarding,
 request_id uuid NOT NULL UNIQUE REFERENCES impact.tenant_access_bootstrap,
 applied_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT,INSERT,UPDATE ON impact.tenant_access_bootstrap TO impact_platform;
GRANT SELECT ON impact.tenant_access_bootstrap_applied,impact.grant_authority,impact.identity_security_state TO impact_platform;
GRANT SELECT,INSERT ON impact.scope_definition,impact.member_role_assignment TO impact_platform;
GRANT SELECT,INSERT,UPDATE ON impact.grant_current TO impact_platform;
ALTER POLICY platform_registry_types ON impact.object_registry
 USING(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy','Grant','RoleTemplate','Predicate'))
 WITH CHECK(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy','Grant','RoleTemplate','Predicate'));
ALTER POLICY platform_revision_types ON impact.object_revision
 USING(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy','Grant','RoleTemplate','Predicate'))
 WITH CHECK(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy','Grant','RoleTemplate','Predicate'));
-- The HTTP role cannot insert arbitrary delegation authority or reset this marker.
-- This function can apply only the reviewed manifest once for an active tenant.
CREATE FUNCTION impact.apply_initial_authority(requested uuid) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE r impact.tenant_access_bootstrap;
BEGIN
 SELECT * INTO r FROM impact.tenant_access_bootstrap WHERE request_id=requested FOR UPDATE;
 IF NOT FOUND OR r.tenant_id IS DISTINCT FROM impact.current_tenant() OR r.state<>'Applied'
 OR r.accepted_at IS NULL OR r.expires_at<=now() OR r.review_expires_at<=now()
 OR r.approved_by IS NULL OR NOT impact.lock_platform_operator(r.approved_by)
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_root WHERE tenant_id=r.tenant_id AND lifecycle_state='Active')
 OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
 WHERE a.identity_id=r.approved_by AND b.identity_id IN(r.owner_identity_id,r.second_identity_id))
 THEN RAISE EXCEPTION 'initial authority denied' USING ERRCODE='42501'; END IF;
 INSERT INTO impact.tenant_access_bootstrap_applied(tenant_id,request_id) VALUES(r.tenant_id,r.request_id);
 INSERT INTO impact.grant_authority(tenant_id,authority_id,principal_id,capability,scope_id,expires_at)
 SELECT r.tenant_id,gen_random_uuid(),p.principal_id,cap,r.scope_id,r.expires_at
 FROM impact.tenant_principal p CROSS JOIN
 (SELECT DISTINCT jsonb_array_elements_text(value) AS cap FROM jsonb_each(r.manifest->'roles')) caps
 WHERE p.tenant_id=r.tenant_id AND p.active AND p.identity_id IN(r.owner_identity_id,r.second_identity_id);
END $$;
REVOKE ALL ON FUNCTION impact.apply_initial_authority(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.apply_initial_authority(uuid) TO impact_platform;
COMMIT;
