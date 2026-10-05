-- Isolated 0.33 candidate; intentionally outside the applied migration directory.
-- The integrator assigns its contiguous migration number after the 0.32 checkpoint.
BEGIN;
SET LOCAL ROLE impact_owner;

DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''HumanAdviceCase'')');
END $$;

CREATE TABLE impact.human_advice_case_current(
 tenant_id uuid NOT NULL, object_id uuid NOT NULL, revision_id uuid NOT NULL,
 object_type text NOT NULL DEFAULT 'HumanAdviceCase' CHECK(object_type='HumanAdviceCase'),
 context_plan_id uuid NOT NULL, context_plan_revision uuid NOT NULL,
 context_plan_type text NOT NULL DEFAULT 'AIAdoptionPlan' CHECK(context_plan_type='AIAdoptionPlan'),
 requester_principal_id uuid NOT NULL, requester_membership_id uuid NOT NULL, requester_natural_id uuid NOT NULL,
 adviser_principal_id uuid NOT NULL, adviser_membership_id uuid NOT NULL, adviser_natural_id uuid NOT NULL,
 case_state text NOT NULL CHECK(case_state IN ('Open','Assigned','AwaitingInput','AdviceDraft','Closed','Cancelled')),
 PRIMARY KEY(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,context_plan_id,context_plan_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
 FOREIGN KEY(tenant_id,context_plan_id,context_plan_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,requester_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,adviser_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,requester_membership_id) REFERENCES impact.membership_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,adviser_membership_id) REFERENCES impact.membership_current(tenant_id,object_id),
 CHECK(requester_principal_id<>adviser_principal_id AND requester_natural_id<>adviser_natural_id)
);
ALTER TABLE impact.human_advice_case_current ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.human_advice_case_current FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.human_advice_case_current
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.human_advice_case_current TO impact_app;

CREATE TABLE impact.human_advice_private_brief(
 tenant_id uuid NOT NULL,object_id uuid NOT NULL,
 problem text NOT NULL CHECK(length(problem) BETWEEN 1 AND 4000 AND problem ~ '\S'),
 problem_sha256 bytea NOT NULL CHECK(octet_length(problem_sha256)=32),
 brief_nonce uuid NOT NULL,
 PRIMARY KEY(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id) REFERENCES impact.human_advice_case_current(tenant_id,object_id)
);
ALTER TABLE impact.human_advice_private_brief ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.human_advice_private_brief FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.human_advice_private_brief
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.human_advice_private_brief TO impact_app;

-- The application sets this only after resolving the authenticated current member,
-- transaction-locally. A writable GUC guards uncertain/missing application context;
-- it does not authenticate a human against a compromised impact_app database login.
CREATE FUNCTION impact.human_advice_principal() RETURNS uuid
 LANGUAGE sql STABLE SET search_path=pg_catalog,impact AS $$
 SELECT nullif(current_setting('impact.human_advice_principal',true),'')::uuid
$$;
REVOKE ALL ON FUNCTION impact.human_advice_principal() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_principal() TO impact_app;

CREATE FUNCTION impact.human_advice_read_scope(principal uuid,membership uuid,anchor uuid) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(SELECT 1 FROM (
  SELECT g.capability,g.scope_id,s.scope_type FROM impact.grant_current g
  JOIN impact.object_registry h ON h.tenant_id=g.tenant_id AND h.object_id=g.object_id
  JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id
  WHERE g.tenant_id=impact.current_tenant() AND g.subject_id=principal AND g.purpose IS NULL
    AND h.lifecycle_state='Active' AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now())
  UNION ALL SELECT e.capability,e.scope_id,s.scope_type FROM impact.group_entitlement e
  JOIN impact.object_registry h ON h.tenant_id=e.tenant_id AND h.object_id=e.group_id
  JOIN impact.scope_definition s ON s.tenant_id=e.tenant_id AND s.scope_id=e.scope_id
  WHERE e.tenant_id=impact.current_tenant() AND e.membership_id=membership
    AND e.expires_at>now() AND h.lifecycle_state='Active'
 ) g WHERE g.capability='ai.enablement.read' AND (g.scope_type='TENANT'
   OR EXISTS(SELECT 1 FROM impact.scope_member sm WHERE sm.tenant_id=impact.current_tenant()
             AND sm.scope_id=g.scope_id AND sm.object_id=anchor)))
$$;
REVOKE ALL ON FUNCTION impact.human_advice_read_scope(uuid,uuid,uuid) FROM PUBLIC;

CREATE FUNCTION impact.human_advice_participant(target uuid,material boolean DEFAULT false) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(
  SELECT 1 FROM impact.human_advice_case_current c
  JOIN impact.tenant_principal p ON p.tenant_id=c.tenant_id AND p.principal_id=impact.human_advice_principal()
  JOIN impact.auth_identity i ON i.identity_id=p.identity_id
  JOIN impact.membership_current m ON m.tenant_id=c.tenant_id AND m.identity_id=p.identity_id
  JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
  JOIN impact.object_registry plan ON plan.tenant_id=c.tenant_id AND plan.object_id=c.context_plan_id
  JOIN impact.object_revision plan_head ON plan_head.tenant_id=plan.tenant_id
    AND plan_head.object_id=plan.object_id AND plan_head.revision_id=plan.head_revision
  WHERE c.tenant_id=impact.current_tenant() AND c.object_id=target AND p.active
  AND plan.object_type='AIAdoptionPlan' AND plan.classification<>'RESTRICTED'
  AND plan_head.restriction_state='AVAILABLE'
  AND impact.human_advice_read_scope(p.principal_id,m.object_id,c.context_plan_id)
  AND h.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active')
  AND (m.expires_at IS NULL OR m.expires_at>now())
  AND ((p.principal_id=c.requester_principal_id AND m.object_id=c.requester_membership_id AND i.natural_identity_id=c.requester_natural_id)
       OR (p.principal_id=c.adviser_principal_id AND m.object_id=c.adviser_membership_id AND i.natural_identity_id=c.adviser_natural_id
           AND c.case_state NOT IN ('Closed','Cancelled')
           AND (NOT material OR c.case_state IN ('Assigned','AwaitingInput','AdviceDraft'))))
 )
$$;
REVOKE ALL ON FUNCTION impact.human_advice_participant(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_participant(uuid,boolean) TO impact_app;

CREATE FUNCTION impact.human_advice_auth_cutoff(target uuid) RETURNS timestamptz
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT greatest(p.auth_not_before,s.auth_not_before) FROM impact.tenant_principal p
 LEFT JOIN impact.identity_security_state s ON s.identity_id=p.identity_id
 WHERE p.tenant_id=impact.current_tenant() AND p.principal_id=target
$$;
REVOKE ALL ON FUNCTION impact.human_advice_auth_cutoff(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_auth_cutoff(uuid) TO impact_app;

-- Case-related audit metadata must not reveal a hidden case's identity, actor
-- or existence through ordinary audit lists/search/exports. Other audit rows
-- retain their existing policy. The incomplete AuditEvent header is visible
-- only during its own atomic creation, before its deferred revision FK seals.
CREATE FUNCTION impact.human_advice_record_visible(kind text,target uuid,participants boolean) RETURNS boolean
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE p jsonb;
BEGIN
 IF kind='HumanAdviceCase' THEN
  RETURN participants AND impact.human_advice_participant(target,false);
 END IF;
 IF kind<>'AuditEvent' THEN RETURN true; END IF;
 SELECT v.payload INTO p FROM impact.object_registry h JOIN impact.object_revision v
 ON v.tenant_id=h.tenant_id AND v.object_id=h.object_id AND v.revision_id=h.head_revision
 WHERE h.tenant_id=impact.current_tenant() AND h.object_id=target AND h.object_type='AuditEvent';
 IF p IS NULL THEN RETURN true; END IF;
 IF COALESCE(p->>'action_type','') ~ '^(human_advice_|create_human_advice_case$)' THEN
  RETURN participants AND impact.human_advice_participant((p->>'object_reference')::uuid,false);
 END IF;
 RETURN true;
END $$;
REVOKE ALL ON FUNCTION impact.human_advice_record_visible(text,uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_record_visible(text,uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;

CREATE POLICY participant_context ON impact.human_advice_case_current AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_participant(object_id,false))
 WITH CHECK(requester_principal_id=impact.human_advice_principal()
   OR (adviser_principal_id=impact.human_advice_principal() AND case_state NOT IN ('Closed','Cancelled')));
CREATE POLICY participant_material ON impact.human_advice_private_brief AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_participant(object_id,true))
 WITH CHECK(EXISTS(SELECT 1 FROM impact.human_advice_case_current c
   WHERE c.tenant_id=human_advice_private_brief.tenant_id AND c.object_id=human_advice_private_brief.object_id
   AND c.requester_principal_id=impact.human_advice_principal()));
CREATE POLICY human_advice_registry_participants ON impact.object_registry AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_record_visible(object_type,object_id,true))
 WITH CHECK(impact.human_advice_record_visible(object_type,object_id,true));
CREATE POLICY human_advice_revision_participants ON impact.object_revision AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_record_visible(object_type,object_id,true))
 WITH CHECK(impact.human_advice_record_visible(object_type,object_id,true));
CREATE POLICY human_advice_registry_no_other_runtime ON impact.object_registry AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_record_visible(object_type,object_id,false))
 WITH CHECK(impact.human_advice_record_visible(object_type,object_id,false));
CREATE POLICY human_advice_revision_no_other_runtime ON impact.object_revision AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_record_visible(object_type,object_id,false))
 WITH CHECK(impact.human_advice_record_visible(object_type,object_id,false));
CREATE FUNCTION impact.human_advice_object_visible(target uuid,participants boolean) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT COALESCE((SELECT impact.human_advice_record_visible(h.object_type,h.object_id,participants)
  FROM impact.object_registry h WHERE h.tenant_id=impact.current_tenant() AND h.object_id=target),false)
$$;
REVOKE ALL ON FUNCTION impact.human_advice_object_visible(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_object_visible(uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;
CREATE POLICY human_advice_authors_participants ON impact.object_natural_author AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_object_visible(object_id,true))
 WITH CHECK(impact.human_advice_object_visible(object_id,true));
CREATE POLICY human_advice_authors_no_other_runtime ON impact.object_natural_author AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_object_visible(object_id,false))
 WITH CHECK(impact.human_advice_object_visible(object_id,false));
CREATE POLICY human_advice_audit_participants ON impact.audit_event_current AS RESTRICTIVE TO impact_app
 USING(COALESCE(action_type,'') !~ '^(human_advice_|create_human_advice_case$)' OR impact.human_advice_participant(object_reference,false))
 WITH CHECK(COALESCE(action_type,'') !~ '^(human_advice_|create_human_advice_case$)' OR impact.human_advice_participant(object_reference,false));
CREATE POLICY human_advice_audit_no_other_runtime ON impact.audit_event_current AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(COALESCE(action_type,'') !~ '^(human_advice_|create_human_advice_case$)')
 WITH CHECK(COALESCE(action_type,'') !~ '^(human_advice_|create_human_advice_case$)');

CREATE POLICY human_advice_receipt_participants ON impact.operation_receipt AS RESTRICTIVE TO impact_app
 USING(COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)'
    OR impact.human_advice_participant((outcome->>'object_id')::uuid,false))
 WITH CHECK(COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)'
    OR (actor_id=impact.human_advice_principal() AND impact.human_advice_participant((outcome->>'object_id')::uuid,false)));
CREATE POLICY human_advice_receipt_no_other_runtime ON impact.operation_receipt AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)')
 WITH CHECK(COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)');

CREATE FUNCTION impact.human_advice_event_visible(target uuid,participants boolean) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT COALESCE((SELECT CASE WHEN e.payload->>'aggregate_type'='HumanAdviceCase'
   THEN participants AND impact.human_advice_participant((e.payload->>'aggregate_id')::uuid,false)
   ELSE true END FROM impact.outbox_event e WHERE e.tenant_id=impact.current_tenant() AND e.event_id=target),false)
$$;
REVOKE ALL ON FUNCTION impact.human_advice_event_visible(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_event_visible(uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;
CREATE POLICY human_advice_outbox_participants ON impact.outbox_event AS RESTRICTIVE TO impact_app
 USING(COALESCE(payload->>'aggregate_type','')<>'HumanAdviceCase' OR impact.human_advice_participant((payload->>'aggregate_id')::uuid,false))
 WITH CHECK(COALESCE(payload->>'aggregate_type','')<>'HumanAdviceCase' OR impact.human_advice_participant((payload->>'aggregate_id')::uuid,false));
CREATE POLICY human_advice_outbox_no_other_runtime ON impact.outbox_event AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(COALESCE(payload->>'aggregate_type','')<>'HumanAdviceCase')
 WITH CHECK(COALESCE(payload->>'aggregate_type','')<>'HumanAdviceCase');
CREATE POLICY human_advice_delivery_participants ON impact.outbox_delivery AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_event_visible(event_id,true))
 WITH CHECK(impact.human_advice_event_visible(event_id,true));
CREATE POLICY human_advice_delivery_no_other_runtime ON impact.outbox_delivery AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_event_visible(event_id,false))
 WITH CHECK(impact.human_advice_event_visible(event_id,false));
CREATE POLICY human_advice_consumer_participants ON impact.consumer_receipt AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_event_visible(event_id,true))
 WITH CHECK(impact.human_advice_event_visible(event_id,true));
CREATE POLICY human_advice_consumer_no_other_runtime ON impact.consumer_receipt AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_event_visible(event_id,false))
 WITH CHECK(impact.human_advice_event_visible(event_id,false));

CREATE FUNCTION impact.guard_human_advice_projection() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
DECLARE person record; who text;
BEGIN
 IF TG_OP='UPDATE' THEN
  IF (to_jsonb(NEW)-ARRAY['revision_id','case_state'])<>(to_jsonb(OLD)-ARRAY['revision_id','case_state']) THEN
   RAISE EXCEPTION 'human advice participants and scope immutable' USING ERRCODE='42501';
  END IF;
  IF OLD.case_state IN ('Closed','Cancelled') THEN
   RAISE EXCEPTION 'human advice terminal immutable' USING ERRCODE='42501';
  END IF;
  IF NEW.case_state IN ('Closed','Cancelled') AND impact.human_advice_principal()<>NEW.requester_principal_id THEN
   RAISE EXCEPTION 'requester closure required' USING ERRCODE='42501';
  END IF;
 ELSE
  IF NEW.case_state<>'Open' OR NEW.requester_principal_id<>impact.human_advice_principal() THEN
   RAISE EXCEPTION 'requester opening required' USING ERRCODE='42501';
  END IF;
 END IF;
 FOREACH who IN ARRAY ARRAY['requester','adviser'] LOOP
  SELECT p.principal_id,m.object_id AS membership_id,impact.member_natural_identity(p.tenant_id,p.principal_id) AS natural_id
  INTO person FROM impact.tenant_principal p JOIN impact.membership_current m
    ON m.tenant_id=p.tenant_id AND m.identity_id=p.identity_id
  JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
  WHERE p.tenant_id=NEW.tenant_id AND p.principal_id=(to_jsonb(NEW)->>(who||'_principal_id'))::uuid
    AND m.object_id=(to_jsonb(NEW)->>(who||'_membership_id'))::uuid AND p.active
    AND h.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active')
    AND (m.expires_at IS NULL OR m.expires_at>now());
  -- Requester can always cancel after counterpart expiry; no other mutation may.
  IF (person IS NULL OR person.natural_id IS NULL OR person.natural_id<>(to_jsonb(NEW)->>(who||'_natural_id'))::uuid)
    AND NOT(TG_OP='UPDATE' AND NEW.case_state='Cancelled' AND who='adviser') THEN
   RAISE EXCEPTION 'current human advice participant required' USING ERRCODE='42501';
  END IF;
 END LOOP;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_human_advice_projection() FROM PUBLIC;
CREATE TRIGGER human_advice_projection_guard BEFORE INSERT OR UPDATE ON impact.human_advice_case_current
 FOR EACH ROW EXECUTE FUNCTION impact.guard_human_advice_projection();

CREATE FUNCTION impact.check_human_advice_head() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE p impact.human_advice_case_current; r record; b record; who text;
BEGIN
 SELECT * INTO STRICT p FROM impact.human_advice_case_current WHERE tenant_id=NEW.tenant_id AND object_id=NEW.object_id;
 SELECT h.head_revision,h.lifecycle_state,v.payload INTO STRICT r
 FROM impact.object_registry h JOIN impact.object_revision v
 ON v.tenant_id=h.tenant_id AND v.object_id=h.object_id AND v.revision_id=h.head_revision
 WHERE h.tenant_id=p.tenant_id AND h.object_id=p.object_id AND h.object_type='HumanAdviceCase';
 SELECT * INTO STRICT b FROM impact.human_advice_private_brief WHERE tenant_id=p.tenant_id AND object_id=p.object_id;
 IF p.revision_id IS DISTINCT FROM r.head_revision OR p.case_state IS DISTINCT FROM r.lifecycle_state
    OR r.payload->>'state' IS DISTINCT FROM p.case_state OR r.payload IS NULL
    OR r.payload->>'context_plan_id' IS DISTINCT FROM p.context_plan_id::text
    OR r.payload->>'context_plan_revision' IS DISTINCT FROM p.context_plan_revision::text
    OR r.payload->>'problem_sha256' IS DISTINCT FROM encode(b.problem_sha256,'hex') OR r.payload ? 'problem' THEN
  RAISE EXCEPTION 'human advice head and private brief must agree' USING ERRCODE='23514';
 END IF;
 FOREACH who IN ARRAY ARRAY['requester','adviser'] LOOP
  IF r.payload->>(who||'_principal_id') IS DISTINCT FROM (to_jsonb(p)->>(who||'_principal_id'))
     OR r.payload->>(who||'_membership_id') IS DISTINCT FROM (to_jsonb(p)->>(who||'_membership_id'))
     OR r.payload->>(who||'_natural_id') IS DISTINCT FROM (to_jsonb(p)->>(who||'_natural_id')) THEN
   RAISE EXCEPTION 'human advice participant proof differs' USING ERRCODE='23514';
  END IF;
 END LOOP;
 RETURN NULL;
END $$;
REVOKE ALL ON FUNCTION impact.check_human_advice_head() FROM PUBLIC;
CREATE CONSTRAINT TRIGGER human_advice_head_consistency AFTER INSERT OR UPDATE ON impact.human_advice_case_current
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION impact.check_human_advice_head();

CREATE FUNCTION impact.guard_human_advice_brief() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN RAISE EXCEPTION 'human advice brief immutable' USING ERRCODE='42501'; END $$;
REVOKE ALL ON FUNCTION impact.guard_human_advice_brief() FROM PUBLIC;
CREATE TRIGGER human_advice_brief_immutable BEFORE UPDATE OR DELETE ON impact.human_advice_private_brief
 FOR EACH ROW EXECUTE FUNCTION impact.guard_human_advice_brief();

COMMIT;
