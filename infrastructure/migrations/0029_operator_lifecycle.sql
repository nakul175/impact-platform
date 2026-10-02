BEGIN;
SET LOCAL ROLE impact_owner;
-- Operator lifecycle (v0.27): renewal before expiry and deactivation of a platform operator, each by
-- a different active operator (a different natural person), with fresh assurance and a reason. The
-- platform role still never writes platform_operator: both changes go through the SECURITY DEFINER
-- apply_operator_change below, which rechecks every condition, and every applied change is one row
-- of the insert-only register platform_operator_change. The last active operator is never
-- deactivated (the actor must be another active operator, and the definer counts again).
--
-- An operator row now carries a revision, so a change names the exact state it saw
-- (expected_revision); the guard trigger refreshes it on every update and keeps the identity fixed.
ALTER TABLE impact.platform_operator ADD COLUMN revision_id uuid NOT NULL DEFAULT gen_random_uuid();
ALTER TABLE impact.platform_operator ADD COLUMN updated_at timestamptz NOT NULL DEFAULT now();
CREATE FUNCTION impact.guard_platform_operator() RETURNS trigger LANGUAGE plpgsql
 SET search_path=pg_catalog,impact AS $$
BEGIN
 IF NEW.identity_id<>OLD.identity_id THEN
  RAISE EXCEPTION 'operator identity is immutable' USING ERRCODE='42501';
 END IF;
 NEW.revision_id := gen_random_uuid();
 NEW.updated_at := now();
 RETURN NEW;
END $$;
CREATE TRIGGER platform_operator_guard BEFORE UPDATE ON impact.platform_operator
 FOR EACH ROW EXECUTE FUNCTION impact.guard_platform_operator();

-- Control-plane events of operator renewal and deactivation belong to no tenant, like onboarding.
ALTER TABLE impact.platform_event DROP CONSTRAINT platform_event_tenant_scope;
ALTER TABLE impact.platform_event ADD CONSTRAINT platform_event_tenant_scope CHECK(
 tenant_id IS NOT NULL OR action IN ('operator-nominate','operator-cancel','operator-decline',
 'operator-accept','account-create','account-reissue','operator-renew','operator-deactivate'));

-- Insert-only register of applied operator changes: who changed whose role, from what to what, why.
-- Written only by the definer; the platform role reads it.
CREATE TABLE impact.platform_operator_change(
 change_id uuid PRIMARY KEY,
 operator_identity_id uuid NOT NULL REFERENCES impact.platform_operator,
 action varchar(20) NOT NULL CHECK(action IN ('renew','deactivate')),
 actor_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 actor_auth_time timestamptz NOT NULL,
 reason varchar(1000) NOT NULL CHECK(length(trim(reason))>0),
 previous_revision_id uuid NOT NULL, revision_id uuid NOT NULL,
 previous_expires_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
 previous_active boolean NOT NULL, active boolean NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(actor_identity_id<>operator_identity_id),
 CHECK((action='renew' AND active AND previous_active AND expires_at>previous_expires_at)
  OR (action='deactivate' AND NOT active AND previous_active AND expires_at=previous_expires_at))
);

-- Renewal or deactivation of one operator by another. Rechecked here, whatever the caller checked:
-- the actor is an active, unexpired operator and not the subject, nor another identity of the
-- subject's natural person; the subject row is at the expected revision and still active and
-- unexpired (expired or deactivated authority is not renewed; a deactivated operator is not
-- deactivated again); a renewal moves the expiry later, at most 365 days ahead; a deactivation
-- leaves at least one other active operator. Fresh assurance is checked by the caller
-- (tenant_lifecycle.py) and its instant recorded here. Returns the subject's new revision.
CREATE FUNCTION impact.apply_operator_change(requested_change uuid, subject uuid, actor uuid,
 requested_action text, expected uuid, new_expiry timestamptz, actor_auth_time timestamptz, why text)
 RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE o impact.platform_operator; fresh uuid;
BEGIN
 IF requested_change IS NULL OR subject IS NULL OR actor IS NULL OR subject=actor
  OR requested_action NOT IN ('renew','deactivate') OR expected IS NULL OR actor_auth_time IS NULL
  OR why IS NULL OR length(trim(why))=0 OR NOT impact.lock_platform_operator(actor)
  OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
   WHERE a.identity_id=actor AND b.identity_id=subject)
 THEN RAISE EXCEPTION 'operator change denied' USING ERRCODE='42501'; END IF;
 SELECT * INTO o FROM impact.platform_operator WHERE identity_id=subject FOR UPDATE;
 IF NOT FOUND OR o.revision_id<>expected OR NOT o.active OR o.expires_at<=now() THEN
  RAISE EXCEPTION 'operator change denied' USING ERRCODE='42501';
 END IF;
 IF requested_action='renew' THEN
  IF new_expiry IS NULL OR new_expiry<=o.expires_at OR new_expiry>now()+interval '365 days' THEN
   RAISE EXCEPTION 'operator change denied' USING ERRCODE='42501';
  END IF;
  UPDATE impact.platform_operator SET expires_at=new_expiry WHERE identity_id=subject;
 ELSE
  IF (SELECT count(*) FROM impact.platform_operator WHERE active AND expires_at>now() AND identity_id<>subject)<1 THEN
   RAISE EXCEPTION 'operator change denied' USING ERRCODE='42501';
  END IF;
  UPDATE impact.platform_operator SET active=false WHERE identity_id=subject;
 END IF;
 SELECT revision_id INTO fresh FROM impact.platform_operator WHERE identity_id=subject;
 INSERT INTO impact.platform_operator_change(change_id,operator_identity_id,action,actor_identity_id,actor_auth_time,
  reason,previous_revision_id,revision_id,previous_expires_at,expires_at,previous_active,active)
 VALUES(requested_change,subject,requested_action,actor,actor_auth_time,trim(why),o.revision_id,fresh,
  o.expires_at,CASE WHEN requested_action='renew' THEN new_expiry ELSE o.expires_at END,o.active,requested_action='renew');
 RETURN fresh;
END $$;

REVOKE ALL ON FUNCTION impact.apply_operator_change(uuid,uuid,uuid,text,uuid,timestamptz,timestamptz,text),
 impact.guard_platform_operator() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.apply_operator_change(uuid,uuid,uuid,text,uuid,timestamptz,timestamptz,text) TO impact_platform;
-- The platform role reads the register; only the definer writes it, and platform_operator stays unwritable.
GRANT SELECT ON impact.platform_operator_change TO impact_platform;
COMMIT;
