BEGIN;
SET LOCAL ROLE impact_owner;

-- Deployment metadata, not tenant-owned data. Only additive migrations may
-- register an exact generated profile. Runtime control-plane code can read
-- these immutable targets and cannot invent a wider profile for an old tenant.
CREATE TABLE impact.platform_access_profile(
 profile_hash varchar(64) PRIMARY KEY CHECK(profile_hash~'^[0-9a-f]{64}$'),
 manifest jsonb NOT NULL CHECK(jsonb_typeof(manifest)='object'),
 registered_at timestamptz NOT NULL DEFAULT now(), source_migration varchar(100) NOT NULL
);
GRANT SELECT ON impact.platform_access_profile TO impact_platform;
CREATE FUNCTION impact.guard_platform_access_profile() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 RAISE EXCEPTION 'registered access profile immutable' USING ERRCODE='42501';
END $$;
REVOKE ALL ON FUNCTION impact.guard_platform_access_profile() FROM PUBLIC;
CREATE TRIGGER platform_access_profile_guard BEFORE UPDATE OR DELETE ON impact.platform_access_profile
 FOR EACH ROW EXECUTE FUNCTION impact.guard_platform_access_profile();
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration) VALUES('48e75c64f1ea2ddceeadce089d1c3f2b056254f236060f1c7d4a18ff439183b0',$profile_0036${"purpose_bound":["audit.export","privacy-cases.draft.create","privacy-cases.draft.edit","privacy-cases.read","privacy.approve","privacy.execute","privacy.export"],"roles":{"ANALYST":["ai.enablement.read","calculated-results.read","dashboards.read","decisions.read","evidence.download","evidence.read","framework.export","frameworks.read","imports.read","indicator-definitions.read","indicator-instances.read","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"AUDIT_READER":["audit-events.read","notifications.read","uploads.read"],"AUTHOR":["ai.enablement.read","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","disclosure.request","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.draft.create","observations.draft.edit","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","report.submit","reporting-calendars.read","reports.draft.create","reports.draft.edit","reports.read","restatement-requests.read","snapshots.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"DATA_STEWARD":["ai.enablement.read","assignments.read","calculated-results.read","dashboards.read","decisions.read","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","forms.read","frameworks.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","notifications.read","observations.draft.create","observations.draft.edit","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","submissions.read","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflows.read"],"ENUMERATOR":["assignments.read","collection-rounds.read","forms.read","notifications.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","upload.create","upload.write","uploads.read"],"EXTERNAL":["calculated-results.read","dashboards.read","decisions.read","evidence.read","frameworks.read","indicator-definitions.read","indicator-instances.read","invitation.accept","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"MEL_ADMIN":["ai.advisory.request","ai.enablement.manage","ai.enablement.read","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","disclosures.read","evidence.read","form.publish","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.export","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.activate","indicator.calculate","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","report.publish","report.withdraw","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"PRIVACY":["disclosure.request","disclosures.read","notifications.read","publication.download","report.withdraw","reports.read","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","uploads.read"],"PROGRAMME_MANAGER":["ai.advisory.request","ai.enablement.manage","ai.enablement.read","assignment.reassign","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","evidence.read","form.submit","forms.read","framework.export","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","indicator.activate","indicator.calculate","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"REVIEWER":["ai.enablement.read","assignments.read","calculated-results.read","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","evidence.download","evidence.read","forms.read","frameworks.read","geographies.read","imports.read","indicator-definitions.read","indicator-instances.read","lineage-manifests.read","measurement-changes.read","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflow.approve","workflow.reject","workflow.return","workflows.read"],"TENANT_ADMIN":["access-denials.read","access-requests.read","access-scopes.create","access-scopes.read","ai.advisory.request","ai.enablement.manage","ai.enablement.read","connections.read","grant.approve","grant.request","grant.revoke","grants.read","groups.approve","groups.manage","groups.read","groups.request","member-invitations.read","member.invite","membership.reactivate","membership.renew.approve","membership.renew.request","membership.revoke","membership.suspend","memberships.read","notifications.read","organisation-units.manage","organisation-units.read","ownership.transfer","reference-data.manage","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","role-templates.read","roles.manage","uploads.read"]},"version":"initial-access-v2"}$profile_0036$::jsonb,'0036_reviewed_ceiling_widening.sql');

-- Existing applied profiles stay unchanged until the owner, named second
-- administrator and an independent active platform operator review an upgrade.
ALTER TABLE impact.tenant_access_bootstrap ADD CONSTRAINT access_bootstrap_tenant_request
 UNIQUE(tenant_id,request_id);

CREATE TABLE impact.tenant_access_upgrade(
 tenant_id uuid NOT NULL REFERENCES impact.tenant_onboarding,
 request_id uuid NOT NULL, revision_id uuid NOT NULL,
 state varchar(20) NOT NULL CHECK(state IN ('Requested','Accepted','Applied','Rejected','Cancelled')),
 bootstrap_request_id uuid NOT NULL,
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 second_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 tenant_revision uuid NOT NULL, owner_revision uuid NOT NULL,
 current_manifest jsonb NOT NULL CHECK(jsonb_typeof(current_manifest)='object'),
 authority_hash varchar(64) NOT NULL CHECK(authority_hash~'^[0-9a-f]{64}$'),
 profile_hash varchar(64) NOT NULL REFERENCES impact.platform_access_profile,
 target_manifest jsonb NOT NULL CHECK(jsonb_typeof(target_manifest)='object'),
 new_capabilities jsonb NOT NULL CHECK(jsonb_typeof(new_capabilities)='array'),
 review_expires_at timestamptz NOT NULL,
 owner_auth_time timestamptz NOT NULL, second_auth_time timestamptz,
 accepted_at timestamptz, approved_by uuid REFERENCES impact.auth_identity,
 approved_auth_time timestamptz, applied_at timestamptz,
 reason varchar(1000) NOT NULL CHECK(reason~'\S'),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant_id,request_id), UNIQUE(request_id),
 FOREIGN KEY(tenant_id,bootstrap_request_id) REFERENCES impact.tenant_access_bootstrap(tenant_id,request_id),
 CHECK(owner_identity_id<>second_identity_id),
 CHECK(review_expires_at>created_at AND review_expires_at<=created_at+interval '7 days'),
 CHECK((state IN ('Accepted','Applied'))=(accepted_at IS NOT NULL AND second_auth_time IS NOT NULL)
       OR state IN ('Rejected','Cancelled')),
 CHECK((state='Applied')=(approved_by IS NOT NULL AND approved_auth_time IS NOT NULL AND applied_at IS NOT NULL))
);
CREATE UNIQUE INDEX access_upgrade_one_live ON impact.tenant_access_upgrade(tenant_id)
 WHERE state IN ('Requested','Accepted');
ALTER TABLE impact.tenant_access_upgrade ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_access_upgrade FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_access_upgrade
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Only the owner-executed bounded inbox selector can discover tenant IDs
-- before transaction-local tenant context is known. Runtime roles stay fenced.
CREATE POLICY access_upgrade_owner_directory ON impact.tenant_access_upgrade TO impact_owner USING(true);
GRANT SELECT,INSERT,UPDATE ON impact.tenant_access_upgrade TO impact_platform;

CREATE TABLE impact.tenant_access_upgrade_applied(
 tenant_id uuid NOT NULL, request_id uuid NOT NULL,
 applied_at timestamptz NOT NULL DEFAULT now(), authorities_added integer NOT NULL CHECK(authorities_added>=0),
 PRIMARY KEY(tenant_id,request_id),
 FOREIGN KEY(tenant_id,request_id) REFERENCES impact.tenant_access_upgrade(tenant_id,request_id)
);
ALTER TABLE impact.tenant_access_upgrade_applied ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_access_upgrade_applied FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_access_upgrade_applied
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT ON impact.tenant_access_upgrade_applied TO impact_platform;

CREATE FUNCTION impact.access_upgrade_refs(viewer uuid, after_request uuid)
 RETURNS TABLE(tenant_id uuid,request_id uuid)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT u.tenant_id,u.request_id FROM impact.tenant_access_upgrade u
 JOIN impact.tenant_onboarding o ON o.tenant_id=u.tenant_id
 WHERE (impact.lock_platform_operator(viewer)
        OR (viewer=o.owner_identity_id AND viewer=u.owner_identity_id)
        OR (viewer=u.second_identity_id AND EXISTS(
            SELECT 1 FROM impact.auth_identity i JOIN impact.identity_profile p USING(identity_id)
            WHERE i.identity_id=viewer AND p.verified_email_hash IS NOT NULL)))
 AND (after_request IS NULL OR u.request_id>after_request)
 ORDER BY u.request_id LIMIT 51
$$;
REVOKE ALL ON FUNCTION impact.access_upgrade_refs(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.access_upgrade_refs(uuid,uuid) TO impact_platform;

-- Principal epochs are metadata about the viewer only. The existing
-- principal_identity_directory owner policy supports this global visibility
-- fingerprint without granting any cross-tenant runtime table access.
CREATE FUNCTION impact.access_upgrade_visibility(viewer uuid) RETURNS jsonb
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE previous_context text:=current_setting('impact.tenant_id',true); person record;
 principals jsonb:='[]'::jsonb; members jsonb; authorities jsonb;
BEGIN
 FOR person IN SELECT p.* FROM impact.tenant_principal p WHERE p.identity_id=viewer ORDER BY p.tenant_id,p.principal_id LOOP
  PERFORM set_config('impact.tenant_id',person.tenant_id::text,true);
  SELECT COALESCE(jsonb_agg(jsonb_build_object('member',m.object_id,'revision',h.head_revision,
    'state',h.lifecycle_state,'status',m.status,'expiry',m.expires_at,
    'unexpired',m.expires_at IS NULL OR m.expires_at>now()) ORDER BY m.object_id),'[]'::jsonb)
    INTO members FROM impact.membership_current m JOIN impact.object_registry h
    ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
    WHERE m.tenant_id=person.tenant_id AND m.identity_id=viewer;
  SELECT COALESCE(jsonb_agg(jsonb_build_object('authority',a.authority_id,'capability',a.capability,
    'scope',a.scope_id,'expiry',a.expires_at) ORDER BY a.authority_id),'[]'::jsonb)
    INTO authorities FROM impact.grant_authority a WHERE a.tenant_id=person.tenant_id
    AND a.principal_id=person.principal_id AND a.expires_at>now();
  principals:=principals||jsonb_build_array(jsonb_build_object('tenant',person.tenant_id,
    'principal',person.principal_id,'active',person.active,'epoch',person.subject_epoch,
    'cutoff',person.auth_not_before,'members',members,'authorities',authorities));
 END LOOP;
 PERFORM set_config('impact.tenant_id',COALESCE(previous_context,''),true);
 RETURN jsonb_build_object(
  'operator',(SELECT to_jsonb(o) FROM impact.platform_operator o WHERE o.identity_id=viewer),
  'operator_current',impact.lock_platform_operator(viewer),
  'identity_cutoff',(SELECT s.auth_not_before FROM impact.identity_security_state s WHERE s.identity_id=viewer),
  'principals',principals);
END $$;
REVOKE ALL ON FUNCTION impact.access_upgrade_visibility(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.access_upgrade_visibility(uuid) TO impact_platform;

CREATE FUNCTION impact.guard_access_upgrade() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'access upgrade immutable' USING ERRCODE='42501'; END IF;
 IF TG_OP='INSERT' THEN
  IF NEW.state<>'Requested' OR NEW.accepted_at IS NOT NULL OR NEW.second_auth_time IS NOT NULL
  OR NEW.approved_by IS NOT NULL OR NEW.applied_at IS NOT NULL THEN
   RAISE EXCEPTION 'access upgrade must start requested' USING ERRCODE='42501';
  END IF;
  RETURN NEW;
 END IF;
 IF OLD.state IN ('Applied','Rejected','Cancelled') THEN
  RAISE EXCEPTION 'access upgrade final' USING ERRCODE='42501';
 END IF;
 IF (to_jsonb(NEW)-ARRAY['state','revision_id','updated_at','second_auth_time','accepted_at',
                       'approved_by','approved_auth_time','applied_at'])
 IS DISTINCT FROM
 (to_jsonb(OLD)-ARRAY['state','revision_id','updated_at','second_auth_time','accepted_at',
                       'approved_by','approved_auth_time','applied_at']) THEN
  RAISE EXCEPTION 'access upgrade identity immutable' USING ERRCODE='42501';
 END IF;
 IF NOT ((OLD.state='Requested' AND NEW.state IN ('Accepted','Rejected','Cancelled'))
      OR (OLD.state='Accepted' AND NEW.state IN ('Applied','Rejected','Cancelled'))) THEN
  RAISE EXCEPTION 'invalid access upgrade transition' USING ERRCODE='42501';
 END IF;
 IF NEW.state='Applied' AND current_user<>'impact_owner' THEN
  RAISE EXCEPTION 'access upgrade applicator required' USING ERRCODE='42501';
 END IF;
 IF OLD.state='Accepted' AND (NEW.second_auth_time IS DISTINCT FROM OLD.second_auth_time
                             OR NEW.accepted_at IS DISTINCT FROM OLD.accepted_at) THEN
  RAISE EXCEPTION 'access upgrade consent immutable' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_access_upgrade() FROM PUBLIC;
CREATE TRIGGER access_upgrade_guard BEFORE INSERT OR UPDATE OR DELETE ON impact.tenant_access_upgrade
 FOR EACH ROW EXECUTE FUNCTION impact.guard_access_upgrade();

CREATE FUNCTION impact.guard_access_upgrade_applied() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 RAISE EXCEPTION 'access upgrade applied marker immutable' USING ERRCODE='42501';
END $$;
REVOKE ALL ON FUNCTION impact.guard_access_upgrade_applied() FROM PUBLIC;
CREATE TRIGGER access_upgrade_applied_guard BEFORE UPDATE OR DELETE ON impact.tenant_access_upgrade_applied
 FOR EACH ROW EXECUTE FUNCTION impact.guard_access_upgrade_applied();

-- Fixed search path, tenant-scoped selector, exact pre-change ceiling and
-- consent checks, one-use marker. No runtime role receives INSERT on ceilings.
CREATE FUNCTION impact.apply_access_upgrade(tenant uuid, requested uuid, approver uuid, authenticated timestamptz)
 RETURNS integer LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE r impact.tenant_access_upgrade; p jsonb; item jsonb; added integer:=0;
 expected integer; actual integer; principal uuid; scope uuid; expiry timestamptz;
 cap text; owner_person uuid; second_person uuid; approver_person uuid;
BEGIN
 IF tenant IS DISTINCT FROM impact.current_tenant() THEN
  RAISE EXCEPTION 'access upgrade denied' USING ERRCODE='42501';
 END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(tenant::text,0));
 SELECT * INTO r FROM impact.tenant_access_upgrade WHERE tenant_id=tenant AND request_id=requested FOR UPDATE;
 IF NOT FOUND OR r.state<>'Accepted' OR r.accepted_at IS NULL OR r.second_auth_time IS NULL
 OR r.review_expires_at<=now() OR r.review_expires_at>r.created_at+interval '7 days'
 OR authenticated IS NULL OR authenticated<=now()-interval '300 seconds' OR authenticated>now()
 OR NOT impact.lock_platform_operator(approver)
 OR EXISTS(SELECT 1 FROM impact.tenant_access_upgrade_applied WHERE tenant_id=tenant AND request_id=requested)
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_root WHERE tenant_id=tenant AND lifecycle_state='Active')
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_onboarding WHERE tenant_id=tenant
               AND revision_id=r.tenant_revision AND owner_identity_id=r.owner_identity_id)
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_access_bootstrap_applied
               WHERE tenant_id=tenant AND request_id=r.bootstrap_request_id)
 OR NOT EXISTS(SELECT 1 FROM impact.platform_access_profile p
               WHERE p.profile_hash=r.profile_hash AND p.manifest=r.target_manifest)
 OR EXISTS(SELECT 1 FROM impact.tenant_authority_renewal WHERE tenant_id=tenant AND state IN ('Requested','Accepted'))
 THEN RAISE EXCEPTION 'access upgrade denied' USING ERRCODE='42501'; END IF;

 SELECT natural_identity_id INTO owner_person FROM impact.auth_identity WHERE identity_id=r.owner_identity_id;
 SELECT natural_identity_id INTO second_person FROM impact.auth_identity WHERE identity_id=r.second_identity_id;
 SELECT natural_identity_id INTO approver_person FROM impact.auth_identity WHERE identity_id=approver;
 IF owner_person IS NULL OR second_person IS NULL OR approver_person IS NULL
 OR owner_person=second_person OR approver_person IN(owner_person,second_person)
 OR EXISTS(SELECT 1 FROM impact.identity_security_state s WHERE
           (s.identity_id=r.owner_identity_id AND r.owner_auth_time<=s.auth_not_before)
        OR (s.identity_id=r.second_identity_id AND r.second_auth_time<=s.auth_not_before)
        OR (s.identity_id=approver AND authenticated<=s.auth_not_before))
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_custody t JOIN impact.membership_current m
               ON m.tenant_id=t.tenant_id AND m.object_id=t.owner_membership_id
               JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
               JOIN impact.tenant_principal o ON o.tenant_id=m.tenant_id AND o.identity_id=m.identity_id
               WHERE t.tenant_id=tenant AND m.identity_id=r.owner_identity_id AND h.head_revision=r.owner_revision
               AND h.lifecycle_state='Active' AND o.active AND (m.expires_at IS NULL OR m.expires_at>now())
               AND (o.auth_not_before IS NULL OR r.owner_auth_time>o.auth_not_before))
 THEN RAISE EXCEPTION 'access upgrade consent denied' USING ERRCODE='42501'; END IF;

 IF jsonb_array_length(r.current_manifest->'principals')<>2 THEN
  RAISE EXCEPTION 'access upgrade principals denied' USING ERRCODE='42501';
 END IF;
 SELECT count(*) INTO expected FROM jsonb_array_elements(r.current_manifest->'authority_rows');
 SELECT count(*) INTO actual FROM impact.grant_authority a
 WHERE a.tenant_id=tenant AND a.expires_at>now() AND a.principal_id IN
 (SELECT (v->>'principal_id')::uuid FROM jsonb_array_elements(r.current_manifest->'principals') v);
 IF expected<>actual THEN RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501'; END IF;
 FOR item IN SELECT value FROM jsonb_array_elements(r.current_manifest->'authority_rows') LOOP
  IF NOT EXISTS(SELECT 1 FROM impact.grant_authority a WHERE a.tenant_id=tenant
    AND a.authority_id=(item->>'authority_id')::uuid AND a.principal_id=(item->>'principal_id')::uuid
    AND a.capability=item->>'capability' AND a.scope_id=(item->>'scope_id')::uuid
    AND a.expires_at=(item->>'expires_at')::timestamptz AND a.expires_at>now()) THEN
   RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501';
  END IF;
 END LOOP;
 FOR item IN SELECT value FROM jsonb_array_elements(r.current_manifest->'grant_revisions')
 UNION ALL SELECT value FROM jsonb_array_elements(r.current_manifest->'membership_revisions') LOOP
  IF NOT EXISTS(SELECT 1 FROM impact.object_registry h JOIN impact.object_revision v
    ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision
    WHERE h.tenant_id=tenant AND h.object_id=(item->>'object_id')::uuid
    AND h.head_revision=(item->>'revision_id')::uuid AND h.lifecycle_state='Active'
    AND encode(v.payload_sha256,'hex')=item->>'payload_sha256') THEN
   RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501';
  END IF;
 END LOOP;
 FOR item IN SELECT value FROM jsonb_array_elements(r.current_manifest->'managed_roles') LOOP
  IF NOT EXISTS(SELECT 1 FROM impact.object_registry h JOIN impact.object_revision v
    ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision
    WHERE h.tenant_id=tenant AND h.object_id=(item->>'object_id')::uuid
    AND h.head_revision=(item->>'revision_id')::uuid AND h.lifecycle_state=item->>'state'
    AND encode(v.payload_sha256,'hex')=item->>'payload_sha256') THEN
   RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501';
  END IF;
 END LOOP;
 -- Source baseline is an immutable applied manifest; revoked baseline
 -- capabilities cannot be classified as new and silently resurrected.
 IF (r.current_manifest->>'source_request_id')::uuid IS DISTINCT FROM COALESCE(
  (SELECT u.request_id FROM impact.tenant_access_upgrade u WHERE u.tenant_id=tenant AND u.state='Applied'
   ORDER BY u.applied_at DESC,u.request_id DESC LIMIT 1),r.bootstrap_request_id) THEN
  RAISE EXCEPTION 'access upgrade source stale' USING ERRCODE='42501';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.tenant_access_upgrade u WHERE u.tenant_id=tenant AND u.state='Applied'
               AND u.request_id=(r.current_manifest->>'source_request_id')::uuid
               AND u.target_manifest=r.current_manifest->'source_manifest')
 AND NOT EXISTS(SELECT 1 FROM impact.tenant_access_bootstrap b WHERE b.tenant_id=tenant AND b.state='Applied'
                AND b.request_id=r.bootstrap_request_id AND b.request_id=(r.current_manifest->>'source_request_id')::uuid
                AND b.manifest=r.current_manifest->'source_manifest') THEN
  RAISE EXCEPTION 'access upgrade source denied' USING ERRCODE='42501';
 END IF;
 IF EXISTS(SELECT 1 FROM jsonb_each(r.current_manifest->'source_manifest'->'roles') source
  WHERE NOT (r.target_manifest->'roles' ? source.key)
  OR NOT (r.target_manifest->'roles'->source.key @> source.value))
 OR NOT (COALESCE(r.target_manifest->'purpose_bound','[]'::jsonb)
         @> COALESCE(r.current_manifest->'source_manifest'->'purpose_bound','[]'::jsonb)) THEN
  RAISE EXCEPTION 'access upgrade profile not monotonic' USING ERRCODE='42501';
 END IF;
 IF r.new_capabilities IS DISTINCT FROM COALESCE((SELECT jsonb_agg(delta.cap ORDER BY delta.cap)
  FROM (SELECT jsonb_array_elements_text(value) AS cap FROM jsonb_each(r.target_manifest->'roles')
        UNION SELECT jsonb_array_elements_text(COALESCE(r.target_manifest->'purpose_bound','[]'::jsonb))
        EXCEPT (SELECT jsonb_array_elements_text(value) FROM jsonb_each(r.current_manifest->'source_manifest'->'roles')
                UNION SELECT jsonb_array_elements_text(COALESCE(r.current_manifest->'source_manifest'->'purpose_bound','[]'::jsonb)))) delta),'[]'::jsonb) THEN
  RAISE EXCEPTION 'access upgrade delta denied' USING ERRCODE='42501';
 END IF;
 IF EXISTS(SELECT 1 FROM jsonb_array_elements_text(r.new_capabilities) n
  WHERE n.value IN(SELECT jsonb_array_elements_text(value) FROM jsonb_each(r.current_manifest->'source_manifest'->'roles')
                   UNION SELECT jsonb_array_elements_text(COALESCE(r.current_manifest->'source_manifest'->'purpose_bound','[]'::jsonb))))
 OR EXISTS(SELECT 1 FROM jsonb_array_elements_text(r.new_capabilities) n
  WHERE n.value NOT IN(SELECT jsonb_array_elements_text(value) FROM jsonb_each(r.target_manifest->'roles')
                       UNION SELECT jsonb_array_elements_text(COALESCE(r.target_manifest->'purpose_bound','[]'::jsonb)))) THEN
  RAISE EXCEPTION 'access upgrade delta denied' USING ERRCODE='42501';
 END IF;

 FOR p IN SELECT value FROM jsonb_array_elements(r.current_manifest->'principals') LOOP
  principal:=(p->>'principal_id')::uuid; scope:=(p->>'scope_id')::uuid;
  IF (p->>'identity_id')::uuid NOT IN(r.owner_identity_id,r.second_identity_id)
  OR NOT EXISTS(SELECT 1 FROM impact.tenant_principal t WHERE t.tenant_id=tenant AND t.principal_id=principal
                AND t.identity_id=(p->>'identity_id')::uuid AND t.active
                AND (t.auth_not_before IS NULL OR
                     CASE WHEN t.identity_id=r.owner_identity_id THEN r.owner_auth_time ELSE r.second_auth_time END>t.auth_not_before))
  OR NOT EXISTS(SELECT 1 FROM impact.membership_current m JOIN impact.object_registry h
                ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
                WHERE m.tenant_id=tenant AND m.object_id=(p->>'membership_id')::uuid
                AND m.identity_id=(p->>'identity_id')::uuid AND h.lifecycle_state='Active'
                AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now()))
  THEN RAISE EXCEPTION 'access upgrade membership denied' USING ERRCODE='42501'; END IF;
  SELECT min(a.expires_at) INTO expiry FROM impact.grant_authority a
   WHERE a.tenant_id=tenant AND a.principal_id=principal AND a.expires_at>now();
  IF expiry IS NULL OR expiry<r.review_expires_at THEN
   RAISE EXCEPTION 'access upgrade expiry denied' USING ERRCODE='42501';
  END IF;
  FOR cap IN SELECT value FROM jsonb_array_elements_text(r.new_capabilities) LOOP
   IF NOT EXISTS(SELECT 1 FROM impact.grant_authority a WHERE a.tenant_id=tenant
                  AND a.principal_id=principal AND a.capability=cap AND a.scope_id=scope AND a.expires_at>now()) THEN
    INSERT INTO impact.grant_authority(tenant_id,authority_id,principal_id,capability,scope_id,expires_at)
     VALUES(tenant,gen_random_uuid(),principal,cap,scope,expiry);
    added:=added+1;
   END IF;
  END LOOP;
 END LOOP;
 INSERT INTO impact.tenant_access_upgrade_applied(tenant_id,request_id,authorities_added) VALUES(tenant,requested,added);
 UPDATE impact.tenant_access_upgrade SET state='Applied',approved_by=approver,approved_auth_time=authenticated,
  applied_at=now(),updated_at=now(),revision_id=gen_random_uuid() WHERE tenant_id=tenant AND request_id=requested;
 RETURN added;
END $$;
REVOKE ALL ON FUNCTION impact.apply_access_upgrade(uuid,uuid,uuid,timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.apply_access_upgrade(uuid,uuid,uuid,timestamptz) TO impact_platform;
COMMIT;
