BEGIN;
SET LOCAL ROLE impact_owner;
-- Usable staging (v0.26a): governed operator onboarding, provider accounts created through the
-- control plane, and initial access whose delegation ceiling includes purpose-bound capabilities.
-- Every independence rule stays as it was: a nomination is accepted only by a different natural
-- person than the nominating operator, and activation still counts natural persons.
--
-- Control-plane events that belong to no tenant (operator onboarding, account provisioning by an
-- operator). Every tenant event keeps its tenant; only these actions may omit it.
ALTER TABLE impact.platform_event ALTER COLUMN tenant_id DROP NOT NULL;
ALTER TABLE impact.platform_event ADD CONSTRAINT platform_event_tenant_scope CHECK(
 tenant_id IS NOT NULL OR action IN ('operator-nominate','operator-cancel','operator-decline',
 'operator-accept','account-create','account-reissue'));

-- A nomination of one person (named by the SHA-256 of a normalised e-mail address) for the platform
-- operator role. The nominating operator never becomes the nominee: acceptance is by the person who
-- signs in with that verified address, through the definer below, and only by another natural
-- person. No clear address is stored.
CREATE TABLE impact.platform_operator_nomination(
 nomination_id uuid PRIMARY KEY, revision_id uuid NOT NULL,
 state varchar(20) NOT NULL CHECK(state IN ('Nominated','Accepted','Declined','Cancelled')),
 nominated_by uuid NOT NULL REFERENCES impact.auth_identity,
 email_hash bytea NOT NULL CHECK(octet_length(email_hash)=32),
 email_mask varchar(254) NOT NULL,
 reason varchar(1000) NOT NULL CHECK(length(trim(reason))>0),
 operator_expires_at timestamptz NOT NULL,
 expires_at timestamptz NOT NULL,
 nominator_auth_time timestamptz NOT NULL,
 nominee_identity_id uuid REFERENCES impact.auth_identity,
 accepted_at timestamptz, accepted_auth_time timestamptz,
 decided_by uuid REFERENCES impact.auth_identity, decision_reason varchar(1000),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK(operator_expires_at>created_at AND expires_at>created_at),
 CHECK((state='Accepted')=(accepted_at IS NOT NULL AND nominee_identity_id IS NOT NULL))
);
CREATE UNIQUE INDEX operator_nomination_one_open ON impact.platform_operator_nomination(email_hash)
 WHERE state='Nominated';
-- Only the definer may record an acceptance; the platform role may cancel or decline.
CREATE FUNCTION impact.guard_operator_nomination() RETURNS trigger LANGUAGE plpgsql
 SET search_path=pg_catalog,impact AS $$
BEGIN
 IF NEW.nomination_id<>OLD.nomination_id OR NEW.nominated_by<>OLD.nominated_by
  OR NEW.email_hash<>OLD.email_hash OR NEW.operator_expires_at<>OLD.operator_expires_at
  OR NEW.expires_at<>OLD.expires_at OR NEW.created_at<>OLD.created_at OR NEW.reason<>OLD.reason
  OR NEW.nominator_auth_time<>OLD.nominator_auth_time THEN
  RAISE EXCEPTION 'nomination is immutable' USING ERRCODE='42501';
 END IF;
 IF OLD.state<>'Nominated' AND NEW.state IS DISTINCT FROM OLD.state THEN
  RAISE EXCEPTION 'nomination is final' USING ERRCODE='42501';
 END IF;
 IF NEW.state='Accepted' AND OLD.state<>'Accepted' AND current_user<>'impact_owner' THEN
  RAISE EXCEPTION 'acceptance only through accept_operator_nomination' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER operator_nomination_guard BEFORE UPDATE ON impact.platform_operator_nomination
 FOR EACH ROW EXECUTE FUNCTION impact.guard_operator_nomination();

-- Identity-provider accounts created through the control plane (an operator, or a tenant owner for
-- a pending invitation of their tenant). Never a password: only who created which account for which
-- address hash, and how often a one-time credential was issued.
CREATE TABLE impact.provider_account(
 account_id uuid PRIMARY KEY, revision_id uuid NOT NULL,
 issuer text NOT NULL, provider_subject varchar(255) NOT NULL,
 email_hash bytea NOT NULL CHECK(octet_length(email_hash)=32),
 email_mask varchar(254) NOT NULL,
 created_by uuid NOT NULL REFERENCES impact.auth_identity,
 tenant_id uuid REFERENCES impact.tenant_root,
 nomination_id uuid REFERENCES impact.platform_operator_nomination,
 provider_created boolean NOT NULL,
 identity_id uuid REFERENCES impact.auth_identity,
 credentials_issued integer NOT NULL DEFAULT 0 CHECK(credentials_issued BETWEEN 0 AND 1000),
 last_issued_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(issuer,provider_subject)
);

-- The identity for a provisioned account: the existing (issuer, subject) identity, or a new one that is
-- its own natural person, exactly as scripts/bootstrap_operator.py `identity` registers one. Only for
-- the deployment's qualified issuer. Registration conveys no authority.
CREATE FUNCTION impact.register_provider_account_identity(requested uuid) RETURNS uuid
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE a impact.provider_account; ident uuid;
BEGIN
 SELECT * INTO a FROM impact.provider_account WHERE account_id=requested FOR UPDATE;
 IF NOT FOUND OR NOT EXISTS(SELECT 1 FROM impact.deployment_qualification
  WHERE active AND valid_until>now() AND issuer=a.issuer) THEN
  RAISE EXCEPTION 'account registration denied' USING ERRCODE='42501';
 END IF;
 SELECT identity_id INTO ident FROM impact.auth_identity WHERE issuer=a.issuer AND provider_subject=a.provider_subject;
 IF ident IS NULL THEN
  ident := gen_random_uuid();
  INSERT INTO impact.auth_identity(identity_id,issuer,provider_subject,natural_identity_id)
  VALUES(ident,a.issuer,a.provider_subject,gen_random_uuid());
 END IF;
 UPDATE impact.provider_account SET identity_id=ident,updated_at=now() WHERE account_id=requested;
 RETURN ident;
END $$;

-- Acceptance of a nomination by the nominee. Rechecked here, whatever the caller checked: an open,
-- unexpired nomination; the nominating operator still an active operator; the actor's verified
-- address is the nominated one; the actor is a different natural person from the nominating
-- operator and from every active operator. Fresh MFA is checked by the caller (tenant_lifecycle.py).
CREATE FUNCTION impact.accept_operator_nomination(requested uuid, actor uuid) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE n impact.platform_operator_nomination;
BEGIN
 SELECT * INTO n FROM impact.platform_operator_nomination WHERE nomination_id=requested FOR UPDATE;
 IF NOT FOUND OR n.state<>'Nominated' OR n.expires_at<=now() OR n.operator_expires_at<=now()
  OR actor=n.nominated_by OR NOT impact.lock_platform_operator(n.nominated_by)
  OR NOT EXISTS(SELECT 1 FROM impact.identity_profile p WHERE p.identity_id=actor AND p.verified_email_hash=n.email_hash)
  OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
   WHERE a.identity_id=actor AND b.identity_id=n.nominated_by)
  OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
   JOIN impact.platform_operator o ON o.identity_id=b.identity_id
   WHERE a.identity_id=actor AND o.active AND o.expires_at>now())
 THEN RAISE EXCEPTION 'operator nomination acceptance denied' USING ERRCODE='42501'; END IF;
 INSERT INTO impact.platform_operator(identity_id,active,expires_at,authority_reference)
 VALUES(actor,true,n.operator_expires_at,'Accepted nomination '||n.nomination_id::text||' by operator '||n.nominated_by::text)
 ON CONFLICT(identity_id) DO UPDATE SET active=true,expires_at=EXCLUDED.expires_at,authority_reference=EXCLUDED.authority_reference;
 UPDATE impact.platform_operator_nomination SET state='Accepted',accepted_at=now(),nominee_identity_id=actor,
  decided_by=actor,updated_at=now() WHERE nomination_id=requested;
END $$;

-- Whether a tenant has a pending invitation for this address hash (a tenant owner may create a
-- sign-in account only for such an address). The tenant must be the transaction's tenant.
CREATE FUNCTION impact.tenant_pending_invitation(requested_tenant uuid, digest bytea) RETURNS boolean
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() THEN
  RAISE EXCEPTION 'tenant denied' USING ERRCODE='42501';
 END IF;
 RETURN EXISTS(SELECT 1 FROM impact.member_invitation WHERE tenant_id=requested_tenant
  AND intended_email_hash=digest AND consumed_at IS NULL AND revoked_at IS NULL AND expires_at>now());
END $$;

-- Initial access (initial-access-v2): the delegation ceiling also covers the profile's purpose-bound
-- capabilities, which no role template carries; they are issued only as purpose-bound grants after an
-- independent review (purpose-grants). Every other condition is unchanged from 0014; a v1 manifest
-- has no purpose_bound list and is applied exactly as before.
CREATE OR REPLACE FUNCTION impact.apply_initial_authority(requested uuid) RETURNS void
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
 (SELECT DISTINCT jsonb_array_elements_text(value) AS cap FROM jsonb_each(r.manifest->'roles')
  UNION SELECT jsonb_array_elements_text(COALESCE(r.manifest->'purpose_bound','[]'::jsonb))) caps
 WHERE p.tenant_id=r.tenant_id AND p.active AND p.identity_id IN(r.owner_identity_id,r.second_identity_id);
END $$;

REVOKE ALL ON FUNCTION impact.register_provider_account_identity(uuid),impact.accept_operator_nomination(uuid,uuid),
 impact.tenant_pending_invitation(uuid,bytea),impact.guard_operator_nomination() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.register_provider_account_identity(uuid),impact.accept_operator_nomination(uuid,uuid),
 impact.tenant_pending_invitation(uuid,bytea) TO impact_platform;
-- The platform role records nominations and accounts; it never writes platform_operator itself.
GRANT SELECT,INSERT ON impact.platform_operator_nomination,impact.provider_account TO impact_platform;
GRANT UPDATE(state,revision_id,updated_at,decided_by,decision_reason) ON impact.platform_operator_nomination TO impact_platform;
GRANT UPDATE(revision_id,updated_at,credentials_issued,last_issued_at) ON impact.provider_account TO impact_platform;
COMMIT;
