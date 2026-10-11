-- Unregistered complete linkage candidate. Qualify before migration registration.
BEGIN;
SET LOCAL ROLE impact_owner;
CREATE FUNCTION impact.diagnosis_reference_shape_valid(p jsonb) RETURNS boolean
 LANGUAGE plpgsql IMMUTABLE SET search_path=pg_catalog AS $$
DECLARE problem jsonb; refs jsonb; ref jsonb; pair text; seen text[];
BEGIN
 IF jsonb_typeof(p) IS DISTINCT FROM 'object'
    OR jsonb_typeof(p->'problems') IS DISTINCT FROM 'array'
    OR jsonb_array_length(p->'problems')>20 THEN RETURN false; END IF;
 FOR problem IN SELECT value FROM jsonb_array_elements(p->'problems') LOOP
  IF jsonb_typeof(problem) IS DISTINCT FROM 'object' THEN RETURN false; END IF;
  IF NOT problem ? 'evidence_references' THEN CONTINUE; END IF;
  refs := problem->'evidence_references';
  IF jsonb_typeof(refs) IS DISTINCT FROM 'array' THEN RETURN false; END IF;
  IF jsonb_array_length(refs)>5 THEN RETURN false; END IF;
  seen := ARRAY[]::text[];
  FOR ref IN SELECT value FROM jsonb_array_elements(refs) LOOP
   IF jsonb_typeof(ref) IS DISTINCT FROM 'object' THEN RETURN false; END IF;
   IF NOT ref ?& ARRAY['object_id','revision_id']
      OR ref-ARRAY['object_id','revision_id'] <> '{}'::jsonb
      OR jsonb_typeof(ref->'object_id') IS DISTINCT FROM 'string'
      OR jsonb_typeof(ref->'revision_id') IS DISTINCT FROM 'string' THEN RETURN false; END IF;
   IF ref->>'object_id' !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
      OR ref->>'revision_id' !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN
    RETURN false;
   END IF;
   pair := (ref->>'object_id') || '/' || (ref->>'revision_id');
   IF pair=ANY(seen) THEN RETURN false; END IF;
   seen := array_append(seen,pair);
  END LOOP;
 END LOOP;
 RETURN true;
END;
$$;
REVOKE ALL ON FUNCTION impact.diagnosis_reference_shape_valid(jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.diagnosis_reference_shape_valid(jsonb)
 TO impact_app,impact_worker,impact_platform,impact_privacy;
ALTER TABLE impact.object_revision ADD CONSTRAINT diagnosis_reference_shape_valid
 CHECK(CASE WHEN object_type<>'AIDiagnosis' THEN true
            WHEN restriction_state='REMOVED' AND payload IS NULL THEN true
            ELSE COALESCE(impact.diagnosis_reference_shape_valid(payload),false) END);
CREATE TABLE impact.diagnosis_evidence_binding(
 tenant_id uuid NOT NULL,
 object_id uuid NOT NULL,
 revision_id uuid NOT NULL,
 diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 problem_id uuid NOT NULL,
 reference_position integer NOT NULL CHECK(reference_position BETWEEN 1 AND 5),
 evidence_id uuid NOT NULL,
 evidence_revision uuid NOT NULL,
 evidence_kind text GENERATED ALWAYS AS ('Evidence') STORED,
 PRIMARY KEY(tenant_id,object_id,revision_id,problem_id,reference_position),
 UNIQUE(tenant_id,object_id,revision_id,problem_id,evidence_id,evidence_revision),
 FOREIGN KEY(tenant_id,object_id,revision_id)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,revision_id,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,evidence_id,evidence_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,evidence_revision,evidence_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type)
);
ALTER TABLE impact.diagnosis_evidence_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.diagnosis_evidence_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.diagnosis_evidence_binding
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.diagnosis_evidence_binding TO impact_app;

CREATE FUNCTION impact.guard_diagnosis_binding() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
DECLARE matched boolean;
BEGIN
 IF TG_OP='INSERT' THEN
  SELECT EXISTS(SELECT 1 FROM impact.object_revision v,
   LATERAL jsonb_array_elements(v.payload->'problems') p
   WHERE v.tenant_id=NEW.tenant_id AND v.object_id=NEW.object_id
    AND v.revision_id=NEW.revision_id AND v.object_type='AIDiagnosis'
    AND p.value->>'problem_id'=NEW.problem_id::text
    AND p.value->'evidence_references'->(NEW.reference_position-1)=
     jsonb_build_object('object_id',NEW.evidence_id::text,'revision_id',NEW.evidence_revision::text))
   INTO matched;
  IF NOT matched THEN RAISE EXCEPTION 'diagnosis binding must match immutable payload' USING ERRCODE='23514'; END IF;
  RETURN NEW;
 ELSIF TG_OP='DELETE' AND current_user='impact_owner'
   AND current_setting('impact.privacy_executor',true)='privacy_remove_revisions'
   AND OLD.tenant_id=impact.current_tenant() THEN
  IF EXISTS(SELECT 1 FROM impact.object_revision v WHERE v.tenant_id=OLD.tenant_id
    AND v.object_id=OLD.object_id AND v.revision_id=OLD.revision_id
    AND v.object_type='AIDiagnosis' AND v.restriction_state='REMOVED' AND v.payload IS NULL)
   AND EXISTS(SELECT 1 FROM impact.privacy_store_action a WHERE a.tenant_id=OLD.tenant_id
    AND a.case_id=nullif(current_setting('impact.privacy_case_id',true),'')::uuid
    AND a.object_id=OLD.object_id AND a.store='DATABASE' AND a.action='DELETE' AND a.state='EXECUTING')
   AND EXISTS(SELECT 1 FROM impact.deletion_ledger d WHERE d.tenant_id=OLD.tenant_id
    AND d.case_id=nullif(current_setting('impact.privacy_case_id',true),'')::uuid
    AND d.object_id=OLD.object_id) THEN RETURN OLD; END IF;
 END IF;
 RAISE EXCEPTION 'diagnosis bindings are immutable' USING ERRCODE='42501';
END;
$$;
REVOKE ALL ON FUNCTION impact.guard_diagnosis_binding() FROM PUBLIC;
CREATE TRIGGER diagnosis_binding_guard BEFORE INSERT OR UPDATE OR DELETE
 ON impact.diagnosis_evidence_binding FOR EACH ROW EXECUTE FUNCTION impact.guard_diagnosis_binding();

CREATE FUNCTION impact.populate_diagnosis_bindings() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 INSERT INTO impact.diagnosis_evidence_binding
  (tenant_id,object_id,revision_id,problem_id,reference_position,evidence_id,evidence_revision)
 SELECT NEW.tenant_id,NEW.object_id,NEW.revision_id,(p.value->>'problem_id')::uuid,
  ref.ordinality::integer,(ref.value->>'object_id')::uuid,(ref.value->>'revision_id')::uuid
 FROM jsonb_array_elements(NEW.payload->'problems') p,
 LATERAL jsonb_array_elements(COALESCE(p.value->'evidence_references','[]'::jsonb))
  WITH ORDINALITY ref(value,ordinality);
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION impact.populate_diagnosis_bindings() FROM PUBLIC;
CREATE TRIGGER populate_diagnosis_bindings AFTER INSERT ON impact.object_revision
 FOR EACH ROW WHEN(NEW.object_type='AIDiagnosis' AND NEW.payload IS NOT NULL)
 EXECUTE FUNCTION impact.populate_diagnosis_bindings();

-- Called only after the existing revision-removal guard has validated the update.
-- No definer, public entry point, account grant or new privacy target is added.
CREATE FUNCTION impact.cleanup_diagnosis_bindings() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 DELETE FROM impact.diagnosis_evidence_binding WHERE tenant_id=NEW.tenant_id
  AND object_id=NEW.object_id AND revision_id=NEW.revision_id;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION impact.cleanup_diagnosis_bindings() FROM PUBLIC;
CREATE TRIGGER cleanup_diagnosis_bindings AFTER UPDATE ON impact.object_revision
 FOR EACH ROW WHEN(NEW.object_type='AIDiagnosis' AND NEW.payload IS NULL
  AND NEW.restriction_state='REMOVED' AND OLD.payload IS NOT NULL)
 EXECUTE FUNCTION impact.cleanup_diagnosis_bindings();

-- Existing0018 owner-only tenant directory covers legacy tenants too. Keep every
-- tenant RLS policy enabled; use transaction-local context and the tenant lock.
DO $$ DECLARE t record; previous_tenant text := current_setting('impact.tenant_id',true);
BEGIN
 FOR t IN SELECT tenant_id FROM impact.tenant_root ORDER BY tenant_id LOOP
  PERFORM set_config('impact.tenant_id',t.tenant_id::text,true);
  PERFORM pg_advisory_xact_lock(hashtextextended(t.tenant_id::text,0));
  INSERT INTO impact.diagnosis_evidence_binding
   (tenant_id,object_id,revision_id,problem_id,reference_position,evidence_id,evidence_revision)
  SELECT v.tenant_id,v.object_id,v.revision_id,(p.value->>'problem_id')::uuid,
   ref.ordinality::integer,(ref.value->>'object_id')::uuid,(ref.value->>'revision_id')::uuid
  FROM impact.object_revision v,
   LATERAL jsonb_array_elements(v.payload->'problems') p,
   LATERAL jsonb_array_elements(COALESCE(p.value->'evidence_references','[]'::jsonb))
    WITH ORDINALITY ref(value,ordinality)
  WHERE v.tenant_id=t.tenant_id AND v.object_type='AIDiagnosis' AND v.payload IS NOT NULL;
 END LOOP;
 PERFORM set_config('impact.tenant_id',COALESCE(previous_tenant,''),true);
END $$;
COMMIT;
