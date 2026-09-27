BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.tenant_principal ADD COLUMN auth_not_before timestamptz;
ALTER TABLE impact.web_session ADD COLUMN verified_email_hash bytea;
ALTER TABLE impact.web_session ADD COLUMN display_name varchar(120);
ALTER TABLE impact.web_session ADD COLUMN email_mask varchar(254);
ALTER TABLE impact.member_invitation ADD COLUMN generation uuid;
ALTER TABLE impact.member_invitation ADD COLUMN membership_expires_at timestamptz;
ALTER TABLE impact.member_invitation ADD COLUMN external boolean NOT NULL DEFAULT true;
ALTER TABLE impact.member_invitation ADD COLUMN role_revision uuid;
ALTER TABLE impact.member_invitation ADD COLUMN accepted_membership_id uuid;
ALTER TABLE impact.member_invitation ADD CONSTRAINT invitation_role_revision FOREIGN KEY(tenant_id,role_revision) REFERENCES impact.object_revision(tenant_id,revision_id);
ALTER TABLE impact.member_invitation ADD CONSTRAINT invitation_member FOREIGN KEY(tenant_id,accepted_membership_id) REFERENCES impact.membership_current(tenant_id,object_id);
CREATE UNIQUE INDEX one_pending_invitation ON impact.member_invitation(tenant_id,intended_email_hash) WHERE consumed_at IS NULL AND revoked_at IS NULL;
GRANT SELECT,INSERT,UPDATE ON impact.member_invitation TO impact_app;

CREATE TABLE impact.identity_profile(identity_id uuid PRIMARY KEY REFERENCES impact.auth_identity,display_name varchar(120) NOT NULL,verified_email_hash bytea CHECK(octet_length(verified_email_hash)=32),email_mask varchar(254),verified_at timestamptz);
GRANT SELECT,INSERT,UPDATE ON impact.identity_profile TO impact_identity;

CREATE TABLE impact.member_profile(tenant_id uuid NOT NULL,membership_id uuid NOT NULL,display_name varchar(120) NOT NULL,email_mask varchar(254),PRIMARY KEY(tenant_id,membership_id),FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id));
CREATE TABLE impact.tenant_custody(tenant_id uuid PRIMARY KEY REFERENCES impact.tenant_root,owner_membership_id uuid NOT NULL,FOREIGN KEY(tenant_id,owner_membership_id) REFERENCES impact.membership_current(tenant_id,object_id));
CREATE TABLE impact.grant_authority(tenant_id uuid NOT NULL,authority_id uuid NOT NULL,principal_id uuid NOT NULL,capability varchar(64) NOT NULL,scope_id uuid NOT NULL,expires_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,authority_id),UNIQUE(tenant_id,principal_id,capability,scope_id),FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal,FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition);
CREATE TABLE impact.member_role_assignment(tenant_id uuid NOT NULL,assignment_id uuid NOT NULL,membership_id uuid NOT NULL,role_template_id uuid NOT NULL,role_revision uuid NOT NULL,scope_id uuid NOT NULL,expires_at timestamptz NOT NULL,grant_ids uuid[] NOT NULL,PRIMARY KEY(tenant_id,assignment_id),FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id),FOREIGN KEY(tenant_id,role_template_id) REFERENCES impact.object_registry,FOREIGN KEY(tenant_id,role_revision) REFERENCES impact.object_revision(tenant_id,revision_id),FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition);
CREATE TABLE impact.admin_reason(tenant_id uuid NOT NULL,revision_id uuid NOT NULL,reason varchar(2000) NOT NULL CHECK(length(trim(reason))>0),PRIMARY KEY(tenant_id,revision_id),FOREIGN KEY(tenant_id,revision_id) REFERENCES impact.object_revision(tenant_id,revision_id));

ALTER TABLE impact.member_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.member_profile FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.member_profile USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.tenant_custody ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_custody FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_custody USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.grant_authority ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.grant_authority FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.grant_authority USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.member_role_assignment ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.member_role_assignment FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.member_role_assignment USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.admin_reason ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.admin_reason FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.admin_reason USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.member_profile TO impact_app;
GRANT SELECT ON impact.tenant_custody,impact.grant_authority TO impact_app;
GRANT SELECT,INSERT ON impact.member_role_assignment,impact.admin_reason TO impact_app;

CREATE UNIQUE INDEX membership_identity_unique ON impact.membership_current(tenant_id,identity_id);
CREATE INDEX invitation_expiry ON impact.member_invitation(tenant_id,expires_at);
CREATE INDEX authority_subject ON impact.grant_authority(tenant_id,principal_id,capability,expires_at);
CREATE FUNCTION impact.member_natural_identity(requested_tenant uuid,requested_principal uuid) RETURNS uuid LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$ SELECT i.natural_identity_id FROM impact.tenant_principal p JOIN impact.auth_identity i ON i.identity_id=p.identity_id WHERE p.tenant_id=requested_tenant AND p.principal_id=requested_principal AND requested_tenant=impact.current_tenant() $$;
REVOKE ALL ON FUNCTION impact.member_natural_identity(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.member_natural_identity(uuid,uuid) TO impact_app;
COMMIT;
