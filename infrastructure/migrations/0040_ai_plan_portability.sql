-- Unregistered0040 draft, outside repository; not project-applied or integration-qualified.
-- JSON-only INTERNAL_SELF export of one exact saved adoption-plan revision.
-- Register only after the implemented policy generates this exact target hash.
BEGIN;
SET LOCAL ROLE impact_owner;
-- Existing immutable0036 target and applied tenant ceilings remain unchanged.
-- Runtime impact_platform has SELECT only; owner migrations register new profiles.
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration)
 VALUES('422b86a900e54a661f6c4a4a35ee8146a504ff7d026478e18e9fafe19e510d3f',$profile_0040${"purpose_bound":["audit.export","privacy-cases.draft.create","privacy-cases.draft.edit","privacy-cases.read","privacy.approve","privacy.execute","privacy.export"],"roles":{"ANALYST":["ai.enablement.read","calculated-results.read","dashboards.read","decisions.read","evidence.download","evidence.read","framework.export","frameworks.read","imports.read","indicator-definitions.read","indicator-instances.read","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"AUDIT_READER":["audit-events.read","notifications.read","uploads.read"],"AUTHOR":["ai.enablement.read","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","disclosure.request","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.draft.create","observations.draft.edit","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","report.submit","reporting-calendars.read","reports.draft.create","reports.draft.edit","reports.read","restatement-requests.read","snapshots.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"DATA_STEWARD":["ai.enablement.read","assignments.read","calculated-results.read","dashboards.read","decisions.read","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","forms.read","frameworks.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","notifications.read","observations.draft.create","observations.draft.edit","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","submissions.read","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflows.read"],"ENUMERATOR":["assignments.read","collection-rounds.read","forms.read","notifications.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","upload.create","upload.write","uploads.read"],"EXTERNAL":["calculated-results.read","dashboards.read","decisions.read","evidence.read","frameworks.read","indicator-definitions.read","indicator-instances.read","invitation.accept","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"MEL_ADMIN":["ai.advisory.request","ai.enablement.export","ai.enablement.manage","ai.enablement.read","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","disclosures.read","evidence.read","form.publish","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.export","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.activate","indicator.calculate","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","report.publish","report.withdraw","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"PRIVACY":["disclosure.request","disclosures.read","notifications.read","publication.download","report.withdraw","reports.read","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","uploads.read"],"PROGRAMME_MANAGER":["ai.advisory.request","ai.enablement.export","ai.enablement.manage","ai.enablement.read","assignment.reassign","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","evidence.read","form.submit","forms.read","framework.export","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","indicator.activate","indicator.calculate","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"REVIEWER":["ai.enablement.read","assignments.read","calculated-results.read","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","evidence.download","evidence.read","forms.read","frameworks.read","geographies.read","imports.read","indicator-definitions.read","indicator-instances.read","lineage-manifests.read","measurement-changes.read","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflow.approve","workflow.reject","workflow.return","workflows.read"],"TENANT_ADMIN":["access-denials.read","access-requests.read","access-scopes.create","access-scopes.read","ai.advisory.request","ai.enablement.export","ai.enablement.manage","ai.enablement.read","connections.read","grant.approve","grant.request","grant.revoke","grants.read","groups.approve","groups.manage","groups.read","groups.request","member-invitations.read","member.invite","membership.reactivate","membership.renew.approve","membership.renew.request","membership.revoke","membership.suspend","memberships.read","notifications.read","organisation-units.manage","organisation-units.read","ownership.transfer","reference-data.manage","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","role-templates.read","roles.manage","uploads.read"]},"version":"initial-access-v2"}$profile_0040$::jsonb,'0040_ai_plan_portability.sql');

CREATE TABLE impact.ai_plan_export_issuance(
 tenant_id uuid NOT NULL,
 issuance_id uuid NOT NULL,
 audit_revision_id uuid NOT NULL,
 audit_kind text GENERATED ALWAYS AS ('AuditEvent') STORED,
 plan_object_id uuid NOT NULL,
 plan_revision_id uuid NOT NULL,
 plan_kind text GENERATED ALWAYS AS ('AIAdoptionPlan') STORED,
 principal_id uuid NOT NULL,
 membership_id uuid NOT NULL,
 issuer_slot smallint NOT NULL CHECK(issuer_slot BETWEEN 1 AND 100),
 command_type varchar(64) NOT NULL DEFAULT 'issue_ai_plan_export' CHECK(command_type='issue_ai_plan_export'),
 operation_id uuid NOT NULL,
 request_sha256 bytea NOT NULL CHECK(octet_length(request_sha256)=32),
 format varchar(16) NOT NULL CHECK(format='JSON'),
 restriction varchar(32) NOT NULL CHECK(restriction='INTERNAL_SELF'),
 package_schema_version varchar(64) NOT NULL CHECK(package_schema_version='nonprofit-ai-plan-export-v1'),
 renderer_version varchar(64) NOT NULL CHECK(renderer_version='nonprofit-ai-plan-json-v1'),
 guidance_status varchar(16) NOT NULL CHECK(guidance_status IN ('COMPLETE','PARTIAL','UNAVAILABLE')),
 guidance_snapshot_id uuid,
 guidance_schema_version varchar(64),
 guidance_sha256 bytea CHECK(guidance_sha256 IS NULL OR octet_length(guidance_sha256)=32),
 generated_at timestamptz NOT NULL,
 replay_until timestamptz NOT NULL,
 content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
 byte_count integer NOT NULL CHECK(byte_count BETWEEN 2 AND 1048576),
 correlation_id uuid NOT NULL,
 outbox_event_id uuid NOT NULL,
 PRIMARY KEY(tenant_id,issuance_id),
 UNIQUE(tenant_id,principal_id,command_type,operation_id),
 UNIQUE(tenant_id,principal_id,issuer_slot),
 CHECK(replay_until=generated_at+interval '168 hours'),
 CHECK((guidance_status='UNAVAILABLE' AND guidance_snapshot_id IS NULL AND guidance_schema_version IS NULL AND guidance_sha256 IS NULL)
    OR (guidance_status IN ('COMPLETE','PARTIAL') AND guidance_snapshot_id IS NOT NULL AND guidance_schema_version IS NOT NULL AND guidance_sha256 IS NOT NULL)),
 FOREIGN KEY(tenant_id) REFERENCES impact.tenant_root(tenant_id),
 FOREIGN KEY(tenant_id,issuance_id,audit_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,issuance_id,audit_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,audit_revision_id,audit_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,plan_object_id,plan_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
 FOREIGN KEY(tenant_id,plan_object_id,plan_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,plan_revision_id,plan_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,guidance_snapshot_id) REFERENCES impact.ai_content_snapshot(tenant_id,snapshot_id),
 FOREIGN KEY(tenant_id,outbox_event_id) REFERENCES impact.outbox_event(tenant_id,event_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX ai_plan_export_parent_revision ON impact.ai_plan_export_issuance(tenant_id,plan_object_id,plan_revision_id);
CREATE INDEX ai_plan_export_actor_time ON impact.ai_plan_export_issuance(tenant_id,principal_id,generated_at,issuance_id);

CREATE TABLE impact.ai_plan_export_bytes(
 tenant_id uuid NOT NULL,issuance_id uuid NOT NULL,
 body bytea NOT NULL CHECK(octet_length(body) BETWEEN 2 AND 1048576),
 PRIMARY KEY(tenant_id,issuance_id),
 FOREIGN KEY(tenant_id,issuance_id) REFERENCES impact.ai_plan_export_issuance(tenant_id,issuance_id)
);
ALTER TABLE impact.ai_plan_export_issuance ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_plan_export_issuance FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_plan_export_issuance
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_plan_export_bytes ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_plan_export_bytes FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_plan_export_bytes
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_plan_export_issuance,impact.ai_plan_export_bytes TO impact_app;

-- Resolved after authenticated current context. This writable GUC guards missing
-- or mis-scoped application context; it does not authenticate a human against a
-- compromised impact_app database login. Missing/invalid context returns NULL.
CREATE FUNCTION impact.ai_plan_export_principal() RETURNS uuid
 LANGUAGE plpgsql STABLE SET search_path=pg_catalog,impact AS $$
DECLARE selected text:=current_setting('impact.ai_plan_export_principal',true);
BEGIN
 IF selected IS NULL OR selected='' THEN RETURN NULL; END IF;
 BEGIN RETURN selected::uuid; EXCEPTION WHEN invalid_text_representation THEN RETURN NULL; END;
END $$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_principal() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.ai_plan_export_principal() TO impact_app;

CREATE FUNCTION impact.ai_plan_export_scope(principal uuid,membership uuid,target uuid,required_capability text) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT required_capability IN ('ai.enablement.read','ai.enablement.export') AND EXISTS(SELECT 1 FROM (
  SELECT g.capability,g.scope_id,s.scope_type FROM impact.grant_current g
  JOIN impact.object_registry h ON h.tenant_id=g.tenant_id AND h.object_id=g.object_id
  JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id
  WHERE g.tenant_id=impact.current_tenant() AND g.subject_id=principal AND g.purpose IS NULL
    AND h.lifecycle_state='Active' AND g.starts_at<=statement_timestamp()
    AND (g.expires_at IS NULL OR g.expires_at>statement_timestamp())
  UNION ALL SELECT e.capability,e.scope_id,s.scope_type FROM impact.group_entitlement e
  JOIN impact.object_registry h ON h.tenant_id=e.tenant_id AND h.object_id=e.group_id
  JOIN impact.scope_definition s ON s.tenant_id=e.tenant_id AND s.scope_id=e.scope_id
  WHERE e.tenant_id=impact.current_tenant() AND e.membership_id=membership
    AND e.expires_at>statement_timestamp() AND h.lifecycle_state='Active'
 ) g WHERE g.capability=required_capability AND (g.scope_type='TENANT'
   OR EXISTS(SELECT 1 FROM impact.scope_member sm WHERE sm.tenant_id=impact.current_tenant()
             AND sm.scope_id=g.scope_id AND sm.object_id=target)))
$$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_scope(uuid,uuid,uuid,text) FROM PUBLIC;

CREATE FUNCTION impact.ai_plan_export_authority(actor uuid,member uuid,target uuid,exact_revision uuid) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT current_setting('role',true)='impact_app'
 AND actor=impact.ai_plan_export_principal() AND EXISTS(
  SELECT 1 FROM impact.tenant_root t
  JOIN impact.tenant_principal p ON p.tenant_id=t.tenant_id AND p.principal_id=actor
  JOIN impact.membership_current m ON m.tenant_id=p.tenant_id AND m.identity_id=p.identity_id AND m.object_id=member
  JOIN impact.object_registry mh ON mh.tenant_id=m.tenant_id AND mh.object_id=m.object_id AND mh.object_type='Membership'
  JOIN impact.object_registry plan ON plan.tenant_id=p.tenant_id AND plan.object_id=target AND plan.object_type='AIAdoptionPlan'
  JOIN impact.object_revision head ON head.tenant_id=plan.tenant_id AND head.object_id=plan.object_id
    AND head.revision_id=plan.head_revision AND head.object_type='AIAdoptionPlan'
  JOIN impact.object_revision pin ON pin.tenant_id=plan.tenant_id AND pin.object_id=plan.object_id
    AND pin.revision_id=exact_revision AND pin.object_type='AIAdoptionPlan'
  WHERE t.tenant_id=impact.current_tenant() AND t.lifecycle_state='Active'
    AND p.active AND p.principal_kind='HUMAN' AND mh.lifecycle_state='Active'
    AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>statement_timestamp())
    AND plan.classification<>'RESTRICTED' AND head.restriction_state='AVAILABLE' AND pin.restriction_state='AVAILABLE'
    AND impact.ai_plan_export_scope(p.principal_id,m.object_id,target,'ai.enablement.read')
    AND impact.ai_plan_export_scope(p.principal_id,m.object_id,target,'ai.enablement.export')
 )
$$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_authority(uuid,uuid,uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.ai_plan_export_authority(uuid,uuid,uuid,uuid) TO impact_app;

-- A true structural retained-storage bound, per tenant principal (not per human
-- or whole tenant), including hidden and expired original copies. No count API,
-- no expiry reuse and no deletion/retention policy are introduced. A generic
-- capacity refusal can reveal only that one's retained copies consumed this cap.
CREATE FUNCTION impact.allocate_ai_plan_export_slot() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE selected smallint; caller_role text:=current_setting('role',true);
BEGIN
 IF NEW.tenant_id IS DISTINCT FROM impact.current_tenant() THEN
  RAISE EXCEPTION 'AI_PLAN_EXPORT_UNAVAILABLE' USING ERRCODE='42501';
 END IF;
 IF NEW.issuer_slot IS NOT NULL THEN
  RAISE EXCEPTION 'AI_PLAN_EXPORT_SLOT_SERVER_ASSIGNED' USING ERRCODE='42501';
 END IF;
 -- Same order as commands: tenant lock first, then bounded issuer allocation.
 -- Runtime creation uses a DB timestamp from this transaction; future/backdated
 -- generation cannot extend the fixed168-hour replay window (including executor).
 PERFORM pg_advisory_xact_lock(hashtextextended(NEW.tenant_id::text,0));
 IF caller_role='impact_app' THEN
  IF NOT COALESCE(impact.ai_plan_export_authority(NEW.principal_id,NEW.membership_id,NEW.plan_object_id,NEW.plan_revision_id),false) THEN
   RAISE EXCEPTION 'AI_PLAN_EXPORT_UNAVAILABLE' USING ERRCODE='42501';
  END IF;
  IF NEW.generated_at<transaction_timestamp() OR NEW.generated_at>statement_timestamp() THEN
   RAISE EXCEPTION 'AI_PLAN_EXPORT_GENERATION_TIME_INVALID' USING ERRCODE='23514';
  END IF;
 ELSIF caller_role IS DISTINCT FROM 'impact_owner' AND NOT EXISTS(
  SELECT 1 FROM pg_roles WHERE rolname=session_user AND rolsuper) THEN
  RAISE EXCEPTION 'AI_PLAN_EXPORT_UNAVAILABLE' USING ERRCODE='42501';
 END IF;
 -- impact_owner migration/trusted fixture seeding is not runtime authority;
 -- unavailable/expired-at-insertion synthetic fixtures are labelled separately.
 PERFORM pg_advisory_xact_lock(hashtextextended('ai-plan-export-slot:'||NEW.tenant_id::text||':'||NEW.principal_id::text,0));
 SELECT slot::smallint INTO selected FROM generate_series(1,100) slot
 WHERE NOT EXISTS(SELECT 1 FROM impact.ai_plan_export_issuance e
  WHERE e.tenant_id=NEW.tenant_id AND e.principal_id=NEW.principal_id AND e.issuer_slot=slot)
 ORDER BY slot LIMIT 1;
 IF selected IS NULL THEN
  RAISE EXCEPTION 'AI_PLAN_EXPORT_STORAGE_LIMIT' USING ERRCODE='54000';
 END IF;
 NEW.issuer_slot:=selected;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.allocate_ai_plan_export_slot() FROM PUBLIC;
CREATE TRIGGER ai_plan_export_slot BEFORE INSERT ON impact.ai_plan_export_issuance
 FOR EACH ROW EXECUTE FUNCTION impact.allocate_ai_plan_export_slot();

-- Separate metadata/byte visibility keeps permanent operation uniqueness usable
-- after seven-day receipt purge. Expired metadata cannot authorise byte replay.
CREATE FUNCTION impact.ai_plan_export_visible(target uuid,bytes_required boolean DEFAULT false) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT COALESCE((SELECT impact.ai_plan_export_authority(e.principal_id,e.membership_id,e.plan_object_id,e.plan_revision_id)
   AND (NOT bytes_required OR e.replay_until>statement_timestamp())
  FROM impact.ai_plan_export_issuance e WHERE e.tenant_id=impact.current_tenant() AND e.issuance_id=target),false)
$$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_visible(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.ai_plan_export_visible(uuid,boolean) TO impact_app;
CREATE POLICY ai_plan_export_actor ON impact.ai_plan_export_issuance AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_visible(issuance_id,false))
 WITH CHECK(impact.ai_plan_export_authority(principal_id,membership_id,plan_object_id,plan_revision_id));
CREATE POLICY ai_plan_export_actor ON impact.ai_plan_export_bytes AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_visible(issuance_id,true)) WITH CHECK(impact.ai_plan_export_visible(issuance_id,true));

-- Existing store.write can create the closed AuditEvent first, without changing
-- its writer or schema. Only INSERT may use this current creator gate; reads
-- require completed issuance projection. Deferred commit sealing below prevents
-- any export AuditEvent without its exact issuance/bytes/receipt/event surviving.
CREATE FUNCTION impact.ai_plan_export_audit_creator(actor uuid,target uuid) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(SELECT 1 FROM impact.tenant_principal p JOIN impact.membership_current m
   ON m.tenant_id=p.tenant_id AND m.identity_id=p.identity_id
  JOIN impact.object_registry plan ON plan.tenant_id=p.tenant_id AND plan.object_id=target
  WHERE p.tenant_id=impact.current_tenant() AND p.principal_id=actor
    AND impact.ai_plan_export_authority(actor,m.object_id,target,plan.head_revision))
$$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_audit_creator(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.ai_plan_export_audit_creator(uuid,uuid) TO impact_app;

CREATE FUNCTION impact.ai_plan_export_record_visible(kind text,target uuid,app_participant boolean) RETURNS boolean
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE p jsonb;
BEGIN
 -- Compose existing private-case guards even for direct helper calls; policies
 -- remain restrictive additions and never create a new case/event oracle.
 IF NOT impact.human_advice_record_visible(kind,target,app_participant AND current_setting('role',true)='impact_app') THEN RETURN false; END IF;
 IF kind<>'AuditEvent' THEN RETURN true; END IF;
 IF EXISTS(SELECT 1 FROM impact.ai_plan_export_issuance e WHERE e.tenant_id=impact.current_tenant() AND e.issuance_id=target) THEN
  RETURN app_participant AND current_setting('role',true)='impact_app' AND impact.ai_plan_export_visible(target,false);
 END IF;
 SELECT v.payload INTO p FROM impact.object_registry h JOIN impact.object_revision v
  ON v.tenant_id=h.tenant_id AND v.object_id=h.object_id AND v.revision_id=h.head_revision
  WHERE h.tenant_id=impact.current_tenant() AND h.object_id=target AND h.object_type='AuditEvent';
 IF p IS NULL THEN RETURN false; END IF; -- unknown/unprojected export read is uniformly unavailable
 RETURN COALESCE(p->>'action_type','')<>'issue_ai_plan_export';
END $$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_record_visible(text,uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.ai_plan_export_record_visible(text,uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;
CREATE POLICY ai_plan_export_registry_app ON impact.object_registry AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_record_visible(object_type,object_id,true))
 WITH CHECK(object_type='AuditEvent' OR impact.ai_plan_export_record_visible(object_type,object_id,true));
-- An AuditEvent header has no payload/target yet, so its INSERT check keeps the
-- existing generic header allowance. SELECT remains uniform false when unknown;
-- exact revision/audit creator checks and deferred completeness bind persistence.
CREATE POLICY ai_plan_export_revision_app ON impact.object_revision AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_record_visible(object_type,object_id,true))
 WITH CHECK(CASE WHEN object_type='AuditEvent' THEN CASE
  WHEN payload->>'action_type'='issue_ai_plan_export' THEN
    payload->>'real_actor_id'=impact.ai_plan_export_principal()::text
    AND payload->>'effective_actor_id'=impact.ai_plan_export_principal()::text
    AND author_id=impact.ai_plan_export_principal()
    AND impact.ai_plan_export_audit_creator(author_id,(payload->>'object_reference')::uuid)
  WHEN COALESCE(payload->>'action_type','') ~ '^(human_advice_|create_human_advice_case$)'
    THEN impact.human_advice_participant((payload->>'object_reference')::uuid,false)
  ELSE true END
  ELSE impact.ai_plan_export_record_visible(object_type,object_id,true) END);
-- INSERT sees the NEW first AuditEvent payload, not a missing stored revision.
-- Existing ordinary creation stays allowed; private export/advice creation still
-- proves its exact current actor/participant. SELECT uses uniform read refusal.
CREATE POLICY ai_plan_export_registry_other ON impact.object_registry AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.ai_plan_export_record_visible(object_type,object_id,false))
 WITH CHECK(object_type='AuditEvent' OR impact.ai_plan_export_record_visible(object_type,object_id,false));
CREATE POLICY ai_plan_export_revision_other ON impact.object_revision AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.ai_plan_export_record_visible(object_type,object_id,false))
 WITH CHECK(CASE WHEN object_type='AuditEvent' THEN
  COALESCE(payload->>'action_type','')<>'issue_ai_plan_export'
  AND COALESCE(payload->>'action_type','') !~ '^(human_advice_|create_human_advice_case$)'
  ELSE impact.ai_plan_export_record_visible(object_type,object_id,false) END);
-- Preserve the worker's existing ordinary first-audit INSERT. Other original
-- runtime ACL/type policies stay binding; private advice/export remain refused.
CREATE POLICY ai_plan_export_audit_app ON impact.audit_event_current AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_record_visible('AuditEvent',object_id,true))
 WITH CHECK(CASE WHEN action_type='issue_ai_plan_export'
  THEN real_actor_id=impact.ai_plan_export_principal() AND effective_actor_id=impact.ai_plan_export_principal()
    AND impact.ai_plan_export_audit_creator(real_actor_id,object_reference)
  ELSE impact.ai_plan_export_record_visible('AuditEvent',object_id,true) END);
CREATE POLICY ai_plan_export_audit_other ON impact.audit_event_current AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.ai_plan_export_record_visible('AuditEvent',object_id,false))
 WITH CHECK(COALESCE(action_type,'')<>'issue_ai_plan_export' AND impact.ai_plan_export_record_visible('AuditEvent',object_id,false));
CREATE FUNCTION impact.ai_plan_export_object_visible(target uuid,app_participant boolean) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT COALESCE((SELECT impact.ai_plan_export_record_visible(h.object_type,h.object_id,app_participant)
  FROM impact.object_registry h WHERE h.tenant_id=impact.current_tenant() AND h.object_id=target),false)
$$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_object_visible(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.ai_plan_export_object_visible(uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;
CREATE POLICY ai_plan_export_author_app ON impact.object_natural_author AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_object_visible(object_id,true)) WITH CHECK(impact.ai_plan_export_object_visible(object_id,true));
CREATE POLICY ai_plan_export_author_other ON impact.object_natural_author AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.ai_plan_export_object_visible(object_id,false)) WITH CHECK(impact.ai_plan_export_object_visible(object_id,false));

CREATE FUNCTION impact.ai_plan_export_receipt_structural_match(actor uuid,operation uuid,fingerprint bytea,result jsonb,expiry timestamptz) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT COALESCE((SELECT actor=e.principal_id AND operation=e.operation_id AND fingerprint=e.request_sha256
  AND expiry=e.replay_until AND jsonb_typeof(result)='object'
  AND (SELECT array_agg(key ORDER BY key) FROM jsonb_object_keys(result) key)=ARRAY['business_state','byte_count','content_sha256','correlation_id','object_id','operation_id','replay_until','revision_id','saved_at']
  AND result->>'object_id'=e.issuance_id::text AND result->>'revision_id'=e.audit_revision_id::text
  AND result->>'business_state'='Issued' AND result->>'operation_id'=e.operation_id::text
  AND result->>'correlation_id'=e.correlation_id::text AND (result->>'saved_at')::timestamptz=e.generated_at
  AND result->>'content_sha256'=encode(e.content_sha256,'hex') AND (result->>'byte_count')::integer=e.byte_count
  AND (result->>'replay_until')::timestamptz=e.replay_until
  FROM impact.ai_plan_export_issuance e WHERE e.tenant_id=impact.current_tenant() AND e.issuance_id=(result->>'object_id')::uuid),false)
$$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_receipt_structural_match(uuid,uuid,bytea,jsonb,timestamptz) FROM PUBLIC;
-- Structural matching is private to the owner/commit seal. Public RLS/replay
-- matching must also prove the caller still owns a currently authorised export.
CREATE FUNCTION impact.ai_plan_export_receipt_match(actor uuid,operation uuid,fingerprint bytea,result jsonb,expiry timestamptz) RETURNS boolean
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE target uuid;
BEGIN
 IF current_setting('role',true) IS DISTINCT FROM 'impact_app' OR impact.ai_plan_export_principal() IS NULL THEN RETURN false; END IF;
 BEGIN target:=(result->>'object_id')::uuid; EXCEPTION WHEN invalid_text_representation THEN RETURN false; END;
 IF NOT impact.ai_plan_export_visible(target,false) THEN RETURN false; END IF;
 RETURN COALESCE(impact.ai_plan_export_receipt_structural_match(actor,operation,fingerprint,result,expiry),false);
END $$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_receipt_match(uuid,uuid,bytea,jsonb,timestamptz) FROM PUBLIC;
CREATE POLICY ai_plan_export_receipt_app ON impact.operation_receipt AS RESTRICTIVE TO impact_app
 USING(command_type<>'issue_ai_plan_export' OR impact.ai_plan_export_visible((outcome->>'object_id')::uuid,false))
 WITH CHECK(command_type<>'issue_ai_plan_export' OR (state='SUCCEEDED' AND actor_id=impact.ai_plan_export_principal()
  AND impact.ai_plan_export_visible((outcome->>'object_id')::uuid,false)
  AND impact.ai_plan_export_receipt_match(actor_id,operation_id,payload_hash,outcome,expires_at)));
GRANT EXECUTE ON FUNCTION impact.ai_plan_export_receipt_match(uuid,uuid,bytea,jsonb,timestamptz) TO impact_app;
CREATE POLICY ai_plan_export_receipt_other ON impact.operation_receipt AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(command_type<>'issue_ai_plan_export') WITH CHECK(command_type<>'issue_ai_plan_export');

-- Tolerant selector conversion preserves unrelated legacy event envelopes.
CREATE FUNCTION impact.ai_plan_export_uuid(value text) RETURNS uuid
 LANGUAGE plpgsql IMMUTABLE SET search_path=pg_catalog,impact AS $$
BEGIN
 IF value IS NULL OR value='' THEN RETURN NULL; END IF;
 BEGIN RETURN value::uuid; EXCEPTION WHEN invalid_text_representation THEN RETURN NULL; END;
END $$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_uuid(text) FROM PUBLIC;
CREATE FUNCTION impact.ai_plan_export_event_visible(target uuid,app_participant boolean) RETURNS boolean
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE v jsonb; issuance uuid;
BEGIN
 IF NOT impact.human_advice_event_visible(target,app_participant AND current_setting('role',true)='impact_app') THEN RETURN false; END IF;
 SELECT payload INTO v FROM impact.outbox_event WHERE tenant_id=impact.current_tenant() AND event_id=target;
 IF v IS NULL THEN RETURN false; END IF;
 SELECT e.issuance_id INTO issuance FROM impact.ai_plan_export_issuance e
 WHERE e.tenant_id=impact.current_tenant() AND (e.outbox_event_id=target
   OR e.issuance_id=impact.ai_plan_export_uuid(v->>'aggregate_id')
   OR e.issuance_id=impact.ai_plan_export_uuid(v->'payload'->>'object_id')) LIMIT 1;
 IF issuance IS NOT NULL THEN
  RETURN app_participant AND current_setting('role',true)='impact_app' AND impact.ai_plan_export_visible(issuance,false);
 END IF;
 IF v->>'aggregate_type'='AuditEvent' THEN
  IF impact.ai_plan_export_uuid(v->>'aggregate_id') IS NULL THEN RETURN false; END IF;
  RETURN impact.ai_plan_export_record_visible('AuditEvent',impact.ai_plan_export_uuid(v->>'aggregate_id'),app_participant);
 END IF;
 RETURN true;
END $$;
REVOKE ALL ON FUNCTION impact.ai_plan_export_event_visible(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.ai_plan_export_event_visible(uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;
-- INSERT's direct aggregate gate does not query a not-yet-inserted event.
CREATE POLICY ai_plan_export_outbox_app ON impact.outbox_event AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_event_visible(event_id,true))
 WITH CHECK(CASE WHEN payload->>'aggregate_type'='AuditEvent'
  THEN impact.ai_plan_export_record_visible('AuditEvent',(payload->>'aggregate_id')::uuid,true)
  ELSE true END);
CREATE POLICY ai_plan_export_outbox_other ON impact.outbox_event AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.ai_plan_export_event_visible(event_id,false))
 WITH CHECK(CASE WHEN payload->>'aggregate_type'='AuditEvent'
  THEN impact.ai_plan_export_record_visible('AuditEvent',(payload->>'aggregate_id')::uuid,false)
  ELSE true END);
CREATE POLICY ai_plan_export_delivery_app ON impact.outbox_delivery AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_event_visible(event_id,true)) WITH CHECK(impact.ai_plan_export_event_visible(event_id,true));
CREATE POLICY ai_plan_export_delivery_other ON impact.outbox_delivery AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.ai_plan_export_event_visible(event_id,false)) WITH CHECK(impact.ai_plan_export_event_visible(event_id,false));
CREATE POLICY ai_plan_export_consumer_app ON impact.consumer_receipt AS RESTRICTIVE TO impact_app
 USING(impact.ai_plan_export_event_visible(event_id,true)) WITH CHECK(impact.ai_plan_export_event_visible(event_id,true));
CREATE POLICY ai_plan_export_consumer_other ON impact.consumer_receipt AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.ai_plan_export_event_visible(event_id,false)) WITH CHECK(impact.ai_plan_export_event_visible(event_id,false));

CREATE FUNCTION impact.guard_ai_plan_export_no_delivery() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF EXISTS(SELECT 1 FROM impact.ai_plan_export_issuance e WHERE e.tenant_id=NEW.tenant_id AND e.outbox_event_id=NEW.event_id)
  AND (TG_OP='UPDATE' OR NEW.channel IS NOT NULL OR NEW.state<>'PENDING' OR NEW.sent_at IS NOT NULL) THEN
  RAISE EXCEPTION 'internal export has no delivery channel' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_plan_export_no_delivery() FROM PUBLIC;
CREATE TRIGGER ai_plan_export_no_delivery BEFORE INSERT OR UPDATE ON impact.outbox_delivery
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_plan_export_no_delivery();
CREATE FUNCTION impact.guard_ai_plan_export_insert_only() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN RAISE EXCEPTION 'AI plan export issuance and bytes insert-only' USING ERRCODE='42501'; END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_plan_export_insert_only() FROM PUBLIC;
CREATE TRIGGER ai_plan_export_issuance_immutable BEFORE UPDATE OR DELETE ON impact.ai_plan_export_issuance
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_plan_export_insert_only();
CREATE TRIGGER ai_plan_export_bytes_immutable BEFORE UPDATE OR DELETE ON impact.ai_plan_export_bytes
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_plan_export_insert_only();
CREATE FUNCTION impact.guard_ai_plan_export_bytes() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE evidence impact.ai_plan_export_issuance;
BEGIN
 SELECT * INTO STRICT evidence FROM impact.ai_plan_export_issuance WHERE tenant_id=NEW.tenant_id AND issuance_id=NEW.issuance_id;
 IF octet_length(NEW.body)<>evidence.byte_count OR sha256(NEW.body)<>evidence.content_sha256 THEN
  RAISE EXCEPTION 'issued bytes digest/count mismatch' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_plan_export_bytes() FROM PUBLIC;
CREATE TRIGGER ai_plan_export_bytes_digest BEFORE INSERT ON impact.ai_plan_export_bytes
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_plan_export_bytes();

CREATE FUNCTION impact.check_ai_plan_export_complete(target_tenant uuid,target_issuance uuid) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE e impact.ai_plan_export_issuance; a record; b bytea; g record; o record;
BEGIN
 SELECT * INTO e FROM impact.ai_plan_export_issuance WHERE tenant_id=target_tenant AND issuance_id=target_issuance;
 IF NOT FOUND THEN RAISE EXCEPTION 'export issuance required' USING ERRCODE='23514'; END IF;
 SELECT h.head_revision,h.lifecycle_state,h.created_by,h.owner_id,v.payload,v.revision_number,v.restriction_state,
  p.revision_id AS projection_revision,p.action_type,p.real_actor_id,p.effective_actor_id,p.object_reference,p.occurred_at,p.correlation_id,
  p.outcome AS projection_outcome,p.specification_ref AS projection_specification_ref,v.author_id AS revision_author
 INTO a FROM impact.object_registry h JOIN impact.object_revision v
  ON v.tenant_id=h.tenant_id AND v.object_id=h.object_id AND v.revision_id=e.audit_revision_id AND v.object_type='AuditEvent'
 JOIN impact.audit_event_current p ON p.tenant_id=h.tenant_id AND p.object_id=h.object_id
 WHERE h.tenant_id=target_tenant AND h.object_id=target_issuance AND h.object_type='AuditEvent';
 IF NOT FOUND OR a.head_revision IS DISTINCT FROM e.audit_revision_id OR a.projection_revision IS DISTINCT FROM e.audit_revision_id
  OR a.lifecycle_state IS DISTINCT FROM 'Recorded' OR a.restriction_state IS DISTINCT FROM 'AVAILABLE' OR a.revision_number IS DISTINCT FROM 1
  OR a.created_by IS DISTINCT FROM e.principal_id OR a.owner_id IS DISTINCT FROM e.principal_id
  OR a.payload->>'action_type' IS DISTINCT FROM 'issue_ai_plan_export' OR a.payload->>'outcome' IS DISTINCT FROM 'SUCCEEDED'
  OR a.payload->>'real_actor_id' IS DISTINCT FROM e.principal_id::text OR a.payload->>'effective_actor_id' IS DISTINCT FROM e.principal_id::text
  OR a.payload->>'object_reference' IS DISTINCT FROM e.plan_object_id::text OR (a.payload->>'occurred_at')::timestamptz IS DISTINCT FROM e.generated_at
  OR a.payload->>'correlation_id' IS DISTINCT FROM e.correlation_id::text OR a.action_type IS DISTINCT FROM 'issue_ai_plan_export'
  OR a.real_actor_id IS DISTINCT FROM e.principal_id OR a.effective_actor_id IS DISTINCT FROM e.principal_id OR a.object_reference IS DISTINCT FROM e.plan_object_id
  OR a.occurred_at IS DISTINCT FROM e.generated_at OR a.correlation_id IS DISTINCT FROM e.correlation_id
  OR a.projection_outcome IS DISTINCT FROM 'SUCCEEDED' OR a.revision_author IS DISTINCT FROM e.principal_id
  OR COALESCE(length(a.payload->>'specification_ref'),0)=0
  OR a.projection_specification_ref IS DISTINCT FROM a.payload->>'specification_ref' THEN
  RAISE EXCEPTION 'exact export audit evidence required' USING ERRCODE='23514';
 END IF;
 SELECT body INTO b FROM impact.ai_plan_export_bytes WHERE tenant_id=target_tenant AND issuance_id=target_issuance;
 IF NOT FOUND OR octet_length(b)<>e.byte_count OR sha256(b)<>e.content_sha256 THEN
  RAISE EXCEPTION 'exact issued artifact required' USING ERRCODE='23514';
 END IF;
 IF e.guidance_snapshot_id IS NOT NULL THEN
  SELECT * INTO g FROM impact.ai_content_snapshot WHERE tenant_id=target_tenant AND snapshot_id=e.guidance_snapshot_id;
  IF NOT FOUND OR g.schema_version IS DISTINCT FROM e.guidance_schema_version OR g.payload_sha256 IS DISTINCT FROM e.guidance_sha256
   OR (CASE WHEN g.payload->'practice' IS NULL OR g.payload->'practice'='null'::jsonb THEN 'PARTIAL' ELSE 'COMPLETE' END) IS DISTINCT FROM e.guidance_status
   OR NOT EXISTS(SELECT 1 FROM impact.ai_plan_content_binding WHERE tenant_id=target_tenant
    AND object_id=e.plan_object_id AND revision_id=e.plan_revision_id AND snapshot_id=e.guidance_snapshot_id) THEN
   RAISE EXCEPTION 'exact guidance binding required' USING ERRCODE='23514';
  END IF;
 ELSE
  IF EXISTS(SELECT 1 FROM impact.ai_plan_content_binding WHERE tenant_id=target_tenant
   AND object_id=e.plan_object_id AND revision_id=e.plan_revision_id) THEN
   RAISE EXCEPTION 'available guidance cannot be relabelled unavailable' USING ERRCODE='23514';
  END IF;
 END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.operation_receipt r WHERE r.tenant_id=target_tenant
  AND r.actor_id=e.principal_id AND r.command_type=e.command_type AND r.operation_id=e.operation_id
  AND r.state='SUCCEEDED' AND impact.ai_plan_export_receipt_structural_match(r.actor_id,r.operation_id,r.payload_hash,r.outcome,r.expires_at)) THEN
  RAISE EXCEPTION 'exact atomic export receipt required' USING ERRCODE='23514';
 END IF;
 SELECT * INTO o FROM impact.outbox_event WHERE tenant_id=target_tenant AND event_id=e.outbox_event_id;
 IF NOT FOUND OR o.event_type IS DISTINCT FROM 'object.changed' OR o.occurred_at IS DISTINCT FROM e.generated_at
  OR o.payload->>'aggregate_type' IS DISTINCT FROM 'AuditEvent' OR o.payload->>'aggregate_id' IS DISTINCT FROM e.issuance_id::text
  OR o.payload->>'aggregate_revision' IS DISTINCT FROM e.audit_revision_id::text OR (o.payload->>'aggregate_sequence')::integer IS DISTINCT FROM 1
  OR o.payload->>'actor_id' IS DISTINCT FROM e.principal_id::text OR o.payload->>'correlation_id' IS DISTINCT FROM e.correlation_id::text
  OR o.payload->'payload'->>'object_id' IS DISTINCT FROM e.issuance_id::text OR o.payload->'payload'->>'revision_id' IS DISTINCT FROM e.audit_revision_id::text
  OR o.payload->'payload'->>'state' IS DISTINCT FROM 'Recorded'
  OR NOT EXISTS(SELECT 1 FROM impact.outbox_delivery WHERE tenant_id=target_tenant AND event_id=e.outbox_event_id AND channel IS NULL) THEN
  RAISE EXCEPTION 'exact atomic nondelivery intent required' USING ERRCODE='23514';
 END IF;
END $$;
REVOKE ALL ON FUNCTION impact.check_ai_plan_export_complete(uuid,uuid) FROM PUBLIC;
CREATE FUNCTION impact.check_ai_plan_export_commit() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF TG_TABLE_NAME='object_revision' THEN
  IF NEW.object_type<>'AuditEvent' OR COALESCE(NEW.payload->>'action_type','')<>'issue_ai_plan_export' THEN RETURN NULL; END IF;
  PERFORM impact.check_ai_plan_export_complete(NEW.tenant_id,NEW.object_id);
 ELSE
  PERFORM impact.check_ai_plan_export_complete(NEW.tenant_id,NEW.issuance_id);
 END IF;
 RETURN NULL;
END $$;
REVOKE ALL ON FUNCTION impact.check_ai_plan_export_commit() FROM PUBLIC;
CREATE CONSTRAINT TRIGGER ai_plan_export_audit_complete AFTER INSERT ON impact.object_revision
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION impact.check_ai_plan_export_commit();
CREATE CONSTRAINT TRIGGER ai_plan_export_issuance_complete AFTER INSERT ON impact.ai_plan_export_issuance
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION impact.check_ai_plan_export_commit();

-- A retained original artifact is a child copy of plan text. This guard refuses
-- parent payload removal while it exists; it is not an erasure implementation.
-- No new privacy-case scope, duration, purge path or restore acceptance is added.
CREATE FUNCTION impact.guard_ai_plan_export_retained_child() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF NEW.payload IS NULL AND OLD.payload IS NOT NULL AND (
  (OLD.object_type='AIAdoptionPlan' AND EXISTS(SELECT 1 FROM impact.ai_plan_export_issuance e
   JOIN impact.ai_plan_export_bytes b USING(tenant_id,issuance_id)
   WHERE e.tenant_id=OLD.tenant_id AND e.plan_object_id=OLD.object_id AND e.plan_revision_id=OLD.revision_id))
  OR (OLD.object_type='AuditEvent' AND EXISTS(SELECT 1 FROM impact.ai_plan_export_issuance e
   JOIN impact.ai_plan_export_bytes b USING(tenant_id,issuance_id)
   WHERE e.tenant_id=OLD.tenant_id AND e.issuance_id=OLD.object_id AND e.audit_revision_id=OLD.revision_id))) THEN
  RAISE EXCEPTION 'AI_PLAN_EXPORT_CHILD_RETAINED' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_plan_export_retained_child() FROM PUBLIC;
CREATE TRIGGER ai_plan_export_retained_child BEFORE UPDATE OF payload,restriction_state ON impact.object_revision
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_plan_export_retained_child();
CREATE FUNCTION impact.guard_ai_plan_export_audit_revision() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF NEW.object_type='AuditEvent' AND EXISTS(SELECT 1 FROM impact.ai_plan_export_issuance e
  WHERE e.tenant_id=NEW.tenant_id AND e.issuance_id=NEW.object_id AND e.audit_revision_id<>NEW.revision_id) THEN
  RAISE EXCEPTION 'issued export audit revision immutable' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_plan_export_audit_revision() FROM PUBLIC;
CREATE TRIGGER ai_plan_export_audit_revision BEFORE INSERT ON impact.object_revision
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_plan_export_audit_revision();
CREATE FUNCTION impact.guard_ai_plan_export_audit_header() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF EXISTS(SELECT 1 FROM impact.ai_plan_export_issuance WHERE tenant_id=OLD.tenant_id AND issuance_id=OLD.object_id) THEN
  RAISE EXCEPTION 'issued export audit header immutable' USING ERRCODE='42501';
 END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_plan_export_audit_header() FROM PUBLIC;
CREATE TRIGGER ai_plan_export_audit_header BEFORE UPDATE OR DELETE ON impact.object_registry
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_plan_export_audit_header();

-- Existing worker purge definers intentionally expose affected keys. Private
-- advice/export commands therefore remain excluded until a separately reviewed
-- private retention path exists. Preserve all ordinary purge semantics/ACLs;
-- expiry still closes byte replay, and permanent operation identity is retained.
CREATE OR REPLACE FUNCTION impact.retention_purge_receipts(max_rows integer) RETURNS TABLE(item text)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DELETE FROM impact.operation_receipt o USING (
 SELECT tenant_id,actor_id,command_type,operation_id FROM impact.operation_receipt
 WHERE tenant_id=impact.current_tenant() AND expires_at<=statement_timestamp()
  AND command_type<>'issue_ai_plan_export'
  AND COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)'
 ORDER BY expires_at,operation_id LIMIT greatest(least(max_rows,5000),0)) d
 WHERE o.tenant_id=d.tenant_id AND o.actor_id=d.actor_id AND o.command_type=d.command_type AND o.operation_id=d.operation_id
 RETURNING o.actor_id::text||':'||o.command_type||':'||o.operation_id::text
$$;
CREATE OR REPLACE FUNCTION impact.retention_purge_receipts(max_rows integer,keep_days integer) RETURNS TABLE(item text)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DELETE FROM impact.operation_receipt o USING (
 SELECT tenant_id,actor_id,command_type,operation_id FROM impact.operation_receipt
 WHERE tenant_id=impact.current_tenant() AND expires_at<=statement_timestamp()-make_interval(days=>greatest(keep_days,7)-7)
  AND command_type<>'issue_ai_plan_export'
  AND COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)'
 ORDER BY expires_at,operation_id LIMIT greatest(least(max_rows,5000),0)) d
 WHERE o.tenant_id=d.tenant_id AND o.actor_id=d.actor_id AND o.command_type=d.command_type AND o.operation_id=d.operation_id
 RETURNING o.actor_id::text||':'||o.command_type||':'||o.operation_id::text
$$;
COMMIT;
