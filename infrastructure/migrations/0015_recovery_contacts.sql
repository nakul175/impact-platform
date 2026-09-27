BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.tenant_recovery_contact(
 contact_id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES impact.tenant_onboarding,
 revision_id uuid NOT NULL,
 state varchar(20) NOT NULL CHECK(state IN ('Nominated','Verified','Active','Replaced','Revoked','Declined','Cancelled','Rejected')),
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 owner_membership_id uuid NOT NULL, owner_revision uuid NOT NULL, tenant_revision uuid NOT NULL,
 nominee_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 email_hash bytea NOT NULL CHECK(octet_length(email_hash)=32),
 display_name varchar(200) NOT NULL, email_mask varchar(300) NOT NULL,
 replaces_contact_id uuid REFERENCES impact.tenant_recovery_contact, replaces_revision uuid,
 owner_auth_time timestamptz NOT NULL, verified_auth_time timestamptz,
 verified_at timestamptz, approved_by uuid REFERENCES impact.auth_identity, approved_at timestamptz,
 expires_at timestamptz NOT NULL, review_expires_at timestamptz NOT NULL,
 reason varchar(1000) NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK(owner_identity_id<>nominee_identity_id),
 CHECK((replaces_contact_id IS NULL)=(replaces_revision IS NULL))
);
CREATE UNIQUE INDEX recovery_one_active ON impact.tenant_recovery_contact(tenant_id) WHERE state='Active';
CREATE UNIQUE INDEX recovery_one_pending ON impact.tenant_recovery_contact(tenant_id) WHERE state IN ('Nominated','Verified');
GRANT SELECT,INSERT,UPDATE ON impact.tenant_recovery_contact TO impact_platform;

-- Serialize evidence checks against the account revocation path, which locks
-- auth_identity before updating authentication cutoffs. No profile data is returned.
CREATE FUNCTION impact.lock_recovery_identities(actors uuid[]) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 PERFORM identity_id FROM impact.auth_identity WHERE identity_id=ANY(actors) ORDER BY identity_id FOR SHARE;
 PERFORM identity_id FROM impact.identity_profile WHERE identity_id=ANY(actors) ORDER BY identity_id FOR SHARE;
 PERFORM identity_id FROM impact.identity_security_state WHERE identity_id=ANY(actors) ORDER BY identity_id FOR SHARE;
END $$;
REVOKE ALL ON FUNCTION impact.lock_recovery_identities(uuid[]) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.lock_recovery_identities(uuid[]) TO impact_platform;
COMMIT;
