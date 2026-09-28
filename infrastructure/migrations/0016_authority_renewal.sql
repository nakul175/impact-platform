BEGIN;
SET LOCAL ROLE impact_owner;
-- Reviewed renewal of the delegated authority created by initial access (0014).
-- The review row pins the exact authority manifest; approval can only extend the
-- pinned, still-present rows and never recreates a revoked or removed one.
CREATE TABLE impact.tenant_authority_renewal(
 request_id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES impact.tenant_onboarding,
 revision_id uuid NOT NULL, state varchar(20) NOT NULL CHECK(state IN ('Requested','Accepted','Applied','Rejected','Cancelled')),
 bootstrap_request_id uuid NOT NULL REFERENCES impact.tenant_access_bootstrap,
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 second_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 tenant_revision uuid NOT NULL, owner_revision uuid NOT NULL,
 manifest jsonb NOT NULL, authority_hash varchar(64) NOT NULL,
 previous_expires_at timestamptz NOT NULL, expires_at timestamptz NOT NULL, review_expires_at timestamptz NOT NULL,
 owner_auth_time timestamptz NOT NULL, second_auth_time timestamptz,
 accepted_at timestamptz, approved_by uuid REFERENCES impact.auth_identity, applied_at timestamptz,
 reason varchar(1000) NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK(owner_identity_id<>second_identity_id),
 CHECK(expires_at>previous_expires_at)
);
CREATE UNIQUE INDEX renewal_one_live ON impact.tenant_authority_renewal(tenant_id)
 WHERE state IN ('Requested','Accepted');
GRANT SELECT,INSERT,UPDATE ON impact.tenant_authority_renewal TO impact_platform;
-- The HTTP control-plane role keeps the 0014 write surface: delegation ceilings and role
-- assignment expiry are re-dated only through the reviewed applicator below, which extends
-- exactly the pinned, unexpired rows of an Applied renewal that an independent active
-- operator approved for an Active tenant whose initial access marker is the pinned one.
-- Any pinned row that is missing or already expired aborts the whole transaction.
CREATE FUNCTION impact.apply_authority_renewal(requested uuid, OUT authorities integer, OUT assignments integer)
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE r impact.tenant_authority_renewal; expected integer;
BEGIN
 SELECT * INTO r FROM impact.tenant_authority_renewal WHERE request_id=requested FOR UPDATE;
 IF NOT FOUND OR r.tenant_id IS DISTINCT FROM impact.current_tenant() OR r.state<>'Applied'
 OR r.accepted_at IS NULL OR r.expires_at<=now() OR r.review_expires_at<=now()
 OR r.expires_at>now()+interval '90 days' OR r.expires_at<=r.previous_expires_at OR r.review_expires_at>r.expires_at
 OR r.approved_by IS NULL OR NOT impact.lock_platform_operator(r.approved_by)
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_root WHERE tenant_id=r.tenant_id AND lifecycle_state='Active')
 OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
 WHERE a.identity_id=r.approved_by AND b.identity_id IN(r.owner_identity_id,r.second_identity_id))
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_access_bootstrap_applied
 WHERE tenant_id=r.tenant_id AND request_id=r.bootstrap_request_id)
 THEN RAISE EXCEPTION 'authority renewal denied' USING ERRCODE='42501'; END IF;
 SELECT count(*) INTO expected FROM jsonb_array_elements_text(r.manifest->'authority_ids');
 UPDATE impact.grant_authority SET expires_at=r.expires_at
 WHERE tenant_id=r.tenant_id AND expires_at>now()
 AND authority_id=ANY(ARRAY(SELECT value::uuid FROM jsonb_array_elements_text(r.manifest->'authority_ids')));
 GET DIAGNOSTICS authorities=ROW_COUNT;
 IF authorities<>expected THEN RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501'; END IF;
 SELECT count(*) INTO expected FROM jsonb_array_elements(r.manifest->'principals') p
 CROSS JOIN LATERAL jsonb_array_elements_text(p->'assignment_ids') i;
 UPDATE impact.member_role_assignment a SET expires_at=r.expires_at
 FROM (SELECT (p->>'membership_id')::uuid AS membership_id,(p->>'scope_id')::uuid AS scope_id,i.value::uuid AS assignment_id
 FROM jsonb_array_elements(r.manifest->'principals') p CROSS JOIN LATERAL jsonb_array_elements_text(p->'assignment_ids') i) pinned
 WHERE a.tenant_id=r.tenant_id AND a.assignment_id=pinned.assignment_id AND a.membership_id=pinned.membership_id
 AND a.scope_id=pinned.scope_id AND a.expires_at>now();
 GET DIAGNOSTICS assignments=ROW_COUNT;
 IF assignments<>expected THEN RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501'; END IF;
END $$;
REVOKE ALL ON FUNCTION impact.apply_authority_renewal(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.apply_authority_renewal(uuid) TO impact_platform;
COMMIT;
