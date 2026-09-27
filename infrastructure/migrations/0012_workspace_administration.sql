BEGIN;
SET LOCAL ROLE impact_owner;

DO $$ DECLARE definition text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO definition FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(definition, '\)$', ' OR object_type IN (''AccessGroup'',''GroupChangeRequest'',''MembershipRenewal'',''CustodyTransfer''))');
END $$;

CREATE TABLE impact.group_entitlement (
 tenant_id uuid NOT NULL, group_id uuid NOT NULL, membership_id uuid NOT NULL,
 capability varchar(64) NOT NULL, scope_id uuid NOT NULL, expires_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,group_id,membership_id,capability,scope_id),
 FOREIGN KEY(tenant_id,group_id) REFERENCES impact.object_registry,
 FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current,
 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition
);
ALTER TABLE impact.group_entitlement ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.group_entitlement FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.group_entitlement USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,DELETE ON impact.group_entitlement TO impact_app;
CREATE INDEX group_entitlement_member ON impact.group_entitlement(tenant_id,membership_id,expires_at);
CREATE UNIQUE INDEX organisation_unit_code_unique ON impact.organisation_unit_current(tenant_id,lower(code));

ALTER TABLE impact.web_session ADD COLUMN session_id uuid NOT NULL DEFAULT gen_random_uuid();
ALTER TABLE impact.web_session ADD CONSTRAINT web_session_public_id UNIQUE(session_id);
ALTER TABLE impact.web_session ADD COLUMN device_label varchar(120) NOT NULL DEFAULT 'Browser session';
ALTER TABLE impact.web_session ADD COLUMN assurance_acr varchar(200) NOT NULL DEFAULT '';
ALTER TABLE impact.web_session ADD COLUMN assurance_amr text[] NOT NULL DEFAULT '{}';
-- All sessions use the stricter 15-minute inactivity bound; absolute lifetime stays eight hours.
CREATE TABLE impact.identity_preferences(
 identity_id uuid PRIMARY KEY REFERENCES impact.auth_identity,
 display_name varchar(120) NOT NULL,
 language varchar(20) NOT NULL DEFAULT 'en', timezone varchar(80) NOT NULL DEFAULT 'UTC',
 reduced_motion boolean NOT NULL DEFAULT false,
 revision_id uuid NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE impact.identity_security_event(
 event_id uuid PRIMARY KEY, identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 action varchar(64) NOT NULL, target_session uuid, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE impact.identity_security_state(identity_id uuid PRIMARY KEY REFERENCES impact.auth_identity,auth_not_before timestamptz NOT NULL);
GRANT SELECT,INSERT,UPDATE ON impact.identity_security_state TO impact_identity;
GRANT SELECT,INSERT,UPDATE ON impact.identity_preferences TO impact_identity;
GRANT SELECT,INSERT ON impact.identity_security_event TO impact_identity;

-- The runtime role still cannot directly update custody. Transfer requires an immutable
-- nominated request, unchanged custody, and a different active natural identity.
CREATE FUNCTION impact.accept_custody(requested_tenant uuid, request_id uuid, accepting_principal uuid)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE p jsonb; owner_id uuid; successor uuid; old_natural uuid; new_natural uuid;
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() THEN RAISE EXCEPTION 'tenant denied' USING ERRCODE='42501'; END IF;
 SELECT v.payload INTO p FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision
 WHERE r.tenant_id=requested_tenant AND r.object_id=request_id AND r.object_type='CustodyTransfer' AND r.lifecycle_state='Requested';
 IF p IS NULL OR (p->>'expires_at')::timestamptz<=now() THEN RAISE EXCEPTION 'transfer unavailable' USING ERRCODE='23514'; END IF;
 SELECT owner_membership_id INTO owner_id FROM impact.tenant_custody WHERE tenant_id=requested_tenant FOR UPDATE;
 successor:=(p->>'membership_id')::uuid;
 IF owner_id IS DISTINCT FROM (p->>'owner_membership_id')::uuid OR owner_id=successor THEN RAISE EXCEPTION 'custody changed' USING ERRCODE='23514'; END IF;
 SELECT i.natural_identity_id INTO old_natural FROM impact.membership_current m JOIN impact.auth_identity i USING(identity_id) WHERE m.tenant_id=requested_tenant AND m.object_id=owner_id;
 SELECT i.natural_identity_id INTO new_natural FROM impact.membership_current m
 JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id
 JOIN impact.tenant_principal t ON t.tenant_id=m.tenant_id AND t.identity_id=m.identity_id
 JOIN impact.auth_identity i ON i.identity_id=m.identity_id
 WHERE m.tenant_id=requested_tenant AND m.object_id=successor AND t.principal_id=accepting_principal AND t.active
 AND r.lifecycle_state='Active' AND (m.expires_at IS NULL OR m.expires_at>now())
 AND r.head_revision=(p->>'expected_membership_revision')::uuid;
 IF new_natural IS NULL OR old_natural IS NULL OR new_natural=old_natural THEN RAISE EXCEPTION 'independence required' USING ERRCODE='23514'; END IF;
 UPDATE impact.tenant_custody SET owner_membership_id=successor WHERE tenant_id=requested_tenant;
END $$;
REVOKE ALL ON FUNCTION impact.accept_custody(uuid,uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.accept_custody(uuid,uuid,uuid) TO impact_app;
COMMIT;
