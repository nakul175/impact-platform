BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.ai_outcome_sharing_consent(
 tenant_id uuid NOT NULL, consent_event_id uuid NOT NULL,
 outcome_observation_id uuid NOT NULL, outcome_observation_revision uuid NOT NULL,
 outcome_kind text GENERATED ALWAYS AS ('AICurrentOutcomeObservation') STORED,
 decision text NOT NULL CHECK(decision IN ('GRANTED','WITHDRAWN')),
 purpose text NOT NULL CHECK(purpose='WHAT_WORKS_AGGREGATION'),
 notice_version varchar(100) NOT NULL CHECK(length(btrim(notice_version))>0),
 allowed_metrics text[] NOT NULL CHECK(cardinality(allowed_metrics) BETWEEN 1 AND 5),
 metric_manifest jsonb NOT NULL CHECK(jsonb_typeof(metric_manifest)='object'),
 actor_principal_id uuid NOT NULL, actor_membership_id uuid NOT NULL, actor_membership_revision uuid NOT NULL,
 actor_membership_kind text GENERATED ALWAYS AS ('Membership') STORED,
 operation_id uuid NOT NULL, payload_hash bytea NOT NULL CHECK(octet_length(payload_hash)=32),
 correlation_id uuid NOT NULL, reason varchar(1000) NOT NULL CHECK(length(btrim(reason))>0), recorded_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,consent_event_id), UNIQUE(tenant_id,actor_principal_id,operation_id),
 FOREIGN KEY(tenant_id,outcome_observation_id,outcome_observation_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,outcome_observation_revision,outcome_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,actor_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,actor_membership_id,actor_membership_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,actor_membership_revision,actor_membership_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type)
);
CREATE INDEX ai_outcome_sharing_current ON impact.ai_outcome_sharing_consent(tenant_id,outcome_observation_id,recorded_at DESC,consent_event_id DESC);
ALTER TABLE impact.ai_outcome_sharing_consent ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_outcome_sharing_consent FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_outcome_sharing_consent USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_outcome_sharing_consent TO impact_app;
REVOKE ALL ON impact.ai_outcome_sharing_consent FROM impact_worker,impact_platform;

CREATE TABLE impact.ai_outcome_evidence_publication(
 publication_id uuid PRIMARY KEY, revision_id uuid NOT NULL UNIQUE,
 state text NOT NULL CHECK(state IN ('PREPARED','APPROVED','PUBLISHED')),
 operation_id uuid NOT NULL, rule_version varchar(100) NOT NULL, policy_version varchar(100) NOT NULL,
 artifact jsonb NOT NULL CHECK(jsonb_typeof(artifact)='object'), manifest_hash bytea NOT NULL CHECK(octet_length(manifest_hash)=32),
 prepared_by_identity uuid NOT NULL REFERENCES impact.auth_identity, prepared_by_natural uuid NOT NULL REFERENCES impact.natural_person,
 prepared_at timestamptz NOT NULL, approved_by_identity uuid REFERENCES impact.auth_identity,
 approved_by_natural uuid REFERENCES impact.natural_person, approved_at timestamptz,
 published_by_identity uuid REFERENCES impact.auth_identity, published_at timestamptz,
 UNIQUE(prepared_by_identity,operation_id),
 CHECK((state='PREPARED' AND approved_at IS NULL AND published_at IS NULL) OR
       (state='APPROVED' AND approved_at IS NOT NULL AND published_at IS NULL) OR
       (state='PUBLISHED' AND approved_at IS NOT NULL AND published_at IS NOT NULL))
);
CREATE TABLE impact.ai_outcome_evidence_source(
 publication_id uuid NOT NULL REFERENCES impact.ai_outcome_evidence_publication,
 tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 cell_key text NOT NULL, metric text NOT NULL CHECK(metric IN ('time','cost','quality','reach','usage')),
 unit varchar(80) NOT NULL, period_bucket varchar(7) NOT NULL CHECK(period_bucket ~ '^[0-9]{4}-Q[1-4]$'),
 value numeric(38,12) NOT NULL, consent_event_id uuid NOT NULL,
 outcome_observation_revision uuid NOT NULL, selected_at timestamptz NOT NULL,
 PRIMARY KEY(publication_id,tenant_id,cell_key),
 FOREIGN KEY(tenant_id,consent_event_id) REFERENCES impact.ai_outcome_sharing_consent(tenant_id,consent_event_id)
);
CREATE TABLE impact.ai_outcome_evidence_event(
 event_id uuid PRIMARY KEY, publication_id uuid NOT NULL REFERENCES impact.ai_outcome_evidence_publication,
 kind text NOT NULL CHECK(kind IN ('APPROVE','PUBLISH')), actor_identity uuid NOT NULL REFERENCES impact.auth_identity,
 actor_natural uuid NOT NULL REFERENCES impact.natural_person, operation_id uuid NOT NULL,
 response jsonb NOT NULL CHECK(jsonb_typeof(response)='object'), recorded_at timestamptz NOT NULL,
 UNIQUE(actor_identity,operation_id)
);
GRANT SELECT ON impact.ai_outcome_evidence_publication,impact.ai_outcome_evidence_event TO impact_platform;
REVOKE ALL ON impact.ai_outcome_evidence_source FROM impact_app,impact_identity,impact_platform,impact_worker;
REVOKE ALL ON impact.ai_outcome_evidence_publication,impact.ai_outcome_evidence_event FROM impact_app,impact_identity,impact_worker;

CREATE FUNCTION impact.guard_ai_outcome_evidence_immutable() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN RAISE EXCEPTION 'outcome evidence record is immutable' USING ERRCODE='42501'; END;
$$;
CREATE TRIGGER ai_outcome_sharing_consent_immutable BEFORE UPDATE OR DELETE ON impact.ai_outcome_sharing_consent FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_outcome_evidence_immutable();
CREATE TRIGGER ai_outcome_evidence_source_immutable BEFORE UPDATE OR DELETE ON impact.ai_outcome_evidence_source FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_outcome_evidence_immutable();
CREATE TRIGGER ai_outcome_evidence_event_immutable BEFORE UPDATE OR DELETE ON impact.ai_outcome_evidence_event FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_outcome_evidence_immutable();

CREATE FUNCTION impact.present_ai_outcome_evidence(p uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT jsonb_build_object('publication_id',publication_id,'revision_id',revision_id,'state',state,
  'rule_version',rule_version,'policy_version',policy_version,'manifest_hash',encode(manifest_hash,'hex'),
  'artifact',artifact,'prepared_at',prepared_at,'approved_at',approved_at,'published_at',published_at)
 FROM impact.ai_outcome_evidence_publication WHERE publication_id=p
$$;

CREATE FUNCTION impact.ai_outcome_evidence_reconstruction_risk(p uuid,k text) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(
  SELECT 1 FROM impact.ai_outcome_evidence_publication old
  WHERE old.state='PUBLISHED' AND old.publication_id<>p AND EXISTS(
   SELECT 1 FROM (
    (SELECT tenant_id FROM impact.ai_outcome_evidence_source WHERE publication_id=p AND cell_key=k
     EXCEPT SELECT tenant_id FROM impact.ai_outcome_evidence_source WHERE publication_id=old.publication_id AND cell_key=k)
    UNION ALL
    (SELECT tenant_id FROM impact.ai_outcome_evidence_source WHERE publication_id=old.publication_id AND cell_key=k
     EXCEPT SELECT tenant_id FROM impact.ai_outcome_evidence_source WHERE publication_id=p AND cell_key=k)
   ) delta HAVING count(*) BETWEEN 1 AND 4
  )
 )
$$;

CREATE FUNCTION impact.ai_outcome_evidence_sources_current(p uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 WITH latest AS (
  SELECT DISTINCT ON (tenant_id,outcome_observation_id) * FROM impact.ai_outcome_sharing_consent
  ORDER BY tenant_id,outcome_observation_id,recorded_at DESC,consent_event_id DESC
 ), eligible AS (
  SELECT l.tenant_id,l.consent_event_id,l.outcome_observation_revision,e.key metric,e.value->>'unit' unit,
   e.value->>'period_bucket' period_bucket,(e.value->>'value')::numeric value,
   e.key||'|'||(e.value->>'unit')||'|'||(e.value->>'period_bucket') cell_key,l.recorded_at
  FROM latest l JOIN impact.tenant_root t ON t.tenant_id=l.tenant_id AND t.lifecycle_state='Active'
  JOIN impact.object_revision r ON r.tenant_id=l.tenant_id AND r.revision_id=l.outcome_observation_revision AND r.restriction_state='AVAILABLE'
  CROSS JOIN LATERAL jsonb_each(l.metric_manifest) e WHERE l.decision='GRANTED'
 ), reduced AS (
  SELECT DISTINCT ON (tenant_id,cell_key) tenant_id,cell_key,consent_event_id,outcome_observation_revision,value
  FROM eligible ORDER BY tenant_id,cell_key,recorded_at DESC,consent_event_id DESC
 ), stored AS (
  SELECT tenant_id,cell_key,consent_event_id,outcome_observation_revision,value FROM impact.ai_outcome_evidence_source WHERE publication_id=p
 )
 SELECT NOT EXISTS(((SELECT * FROM reduced EXCEPT SELECT * FROM stored) UNION ALL (SELECT * FROM stored EXCEPT SELECT * FROM reduced)))
$$;

CREATE FUNCTION impact.prepare_ai_outcome_evidence(viewer uuid,op uuid,rule text,policy text) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE pub uuid; rev uuid; natural uuid; old uuid; art jsonb; manifest_digest bytea; now_at timestamptz:=statement_timestamp();
BEGIN
 IF NOT impact.lock_platform_operator(viewer) THEN RAISE EXCEPTION 'platform operator required' USING ERRCODE='42501'; END IF;
 SELECT publication_id INTO old FROM impact.ai_outcome_evidence_publication WHERE prepared_by_identity=viewer AND operation_id=op;
 IF old IS NOT NULL THEN RETURN impact.present_ai_outcome_evidence(old); END IF;
 SELECT natural_identity_id INTO STRICT natural FROM impact.auth_identity WHERE identity_id=viewer;
 pub:=gen_random_uuid(); rev:=gen_random_uuid();
 INSERT INTO impact.ai_outcome_evidence_publication VALUES(pub,rev,'PREPARED',op,rule,policy,'{}'::jsonb,sha256('pending'::bytea),viewer,natural,now_at,NULL,NULL,NULL,NULL,NULL);
 WITH latest AS (
  SELECT DISTINCT ON (tenant_id,outcome_observation_id) * FROM impact.ai_outcome_sharing_consent
  ORDER BY tenant_id,outcome_observation_id,recorded_at DESC,consent_event_id DESC
 ), eligible AS (
  SELECT l.tenant_id,l.consent_event_id,l.outcome_observation_revision,e.key metric,e.value->>'unit' unit,
   e.value->>'period_bucket' period_bucket,(e.value->>'value')::numeric value,
   e.key||'|'||(e.value->>'unit')||'|'||(e.value->>'period_bucket') cell_key,l.recorded_at
  FROM latest l JOIN impact.tenant_root t ON t.tenant_id=l.tenant_id AND t.lifecycle_state='Active'
  JOIN impact.object_revision r ON r.tenant_id=l.tenant_id AND r.revision_id=l.outcome_observation_revision AND r.restriction_state='AVAILABLE'
  CROSS JOIN LATERAL jsonb_each(l.metric_manifest) e WHERE l.decision='GRANTED'
 ), reduced AS (
  SELECT DISTINCT ON (tenant_id,cell_key) * FROM eligible ORDER BY tenant_id,cell_key,recorded_at DESC,consent_event_id DESC
 )
 INSERT INTO impact.ai_outcome_evidence_source(publication_id,tenant_id,cell_key,metric,unit,period_bucket,value,consent_event_id,outcome_observation_revision,selected_at)
 SELECT pub,tenant_id,cell_key,metric,unit,period_bucket,value,consent_event_id,outcome_observation_revision,now_at FROM reduced;
 SELECT COALESCE(jsonb_agg(jsonb_build_object('metric',metric,'unit',unit,'period_bucket',period_bucket,
  'status',CASE WHEN n<5 THEN 'WITHHELD' WHEN impact.ai_outcome_evidence_reconstruction_risk(pub,cell_key) THEN 'WITHHELD' ELSE 'RELEASABLE' END,
  'reason',CASE WHEN n<5 THEN 'INSUFFICIENT_ORGANISATIONS' WHEN impact.ai_outcome_evidence_reconstruction_risk(pub,cell_key) THEN 'RECONSTRUCTION_RISK' ELSE NULL END,
  'mean_value',CASE WHEN n>=5 AND NOT impact.ai_outcome_evidence_reconstruction_risk(pub,cell_key) THEN mean_value ELSE NULL END,
  'organisation_count',CASE WHEN n>=5 AND NOT impact.ai_outcome_evidence_reconstruction_risk(pub,cell_key) THEN n ELSE NULL END) ORDER BY metric,unit,period_bucket),'[]'::jsonb)
 INTO art FROM (
  SELECT cell_key,metric,unit,period_bucket,count(DISTINCT tenant_id) n,avg(value)::text mean_value,
   count(*) source_rows
  FROM impact.ai_outcome_evidence_source WHERE publication_id=pub GROUP BY cell_key,metric,unit,period_bucket
 ) cells;
 art:=jsonb_build_object('rule_version',rule,'policy_version',policy,'reporting_basis','SELF_REPORTED','items',art,
  'limitations','Consent-current self-reported observed changes only; no causal, independently verified, or realised-ROI claim.');
 SELECT sha256(convert_to(COALESCE(string_agg(cell_key||':'||tenant_id::text||':'||outcome_observation_revision::text,',' ORDER BY cell_key,tenant_id),'empty'),'UTF8')) INTO manifest_digest
 FROM impact.ai_outcome_evidence_source WHERE publication_id=pub;
 UPDATE impact.ai_outcome_evidence_publication SET artifact=art,manifest_hash=manifest_digest WHERE publication_id=pub;
 RETURN impact.present_ai_outcome_evidence(pub);
END;
$$;

CREATE FUNCTION impact.act_ai_outcome_evidence(viewer uuid,pub uuid,act text,op uuid,expected uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE r impact.ai_outcome_evidence_publication; natural uuid; answer jsonb; now_at timestamptz:=statement_timestamp();
BEGIN
 IF NOT impact.lock_platform_operator(viewer) THEN RAISE EXCEPTION 'platform operator required' USING ERRCODE='42501'; END IF;
 SELECT response INTO answer FROM impact.ai_outcome_evidence_event WHERE actor_identity=viewer AND operation_id=op;
 IF answer IS NOT NULL THEN RETURN answer; END IF;
 SELECT natural_identity_id INTO STRICT natural FROM impact.auth_identity WHERE identity_id=viewer;
 SELECT * INTO r FROM impact.ai_outcome_evidence_publication WHERE publication_id=pub FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'publication unavailable' USING ERRCODE='P0002'; END IF;
 IF r.revision_id<>expected THEN RAISE EXCEPTION 'publication changed' USING ERRCODE='40001'; END IF;
 IF NOT impact.ai_outcome_evidence_sources_current(pub) THEN RAISE EXCEPTION 'consent or source changed' USING ERRCODE='40001'; END IF;
 IF act='approve' THEN
  IF r.state<>'PREPARED' OR r.prepared_by_natural=natural THEN RAISE EXCEPTION 'independent approval required' USING ERRCODE='42501'; END IF;
  UPDATE impact.ai_outcome_evidence_publication SET state='APPROVED',revision_id=gen_random_uuid(),approved_by_identity=viewer,approved_by_natural=natural,approved_at=now_at WHERE publication_id=pub;
 ELSIF act='publish' THEN
  IF r.state<>'APPROVED' THEN RAISE EXCEPTION 'approval required' USING ERRCODE='42501'; END IF;
  UPDATE impact.ai_outcome_evidence_publication SET state='PUBLISHED',revision_id=gen_random_uuid(),published_by_identity=viewer,published_at=now_at WHERE publication_id=pub;
 ELSE RAISE EXCEPTION 'invalid action' USING ERRCODE='22023'; END IF;
 answer:=impact.present_ai_outcome_evidence(pub);
 INSERT INTO impact.ai_outcome_evidence_event VALUES(gen_random_uuid(),pub,upper(act),viewer,natural,op,answer,now_at);
 RETURN answer;
END;
$$;

REVOKE ALL ON FUNCTION impact.guard_ai_outcome_evidence_immutable(),impact.present_ai_outcome_evidence(uuid),impact.ai_outcome_evidence_reconstruction_risk(uuid,text),impact.ai_outcome_evidence_sources_current(uuid),impact.prepare_ai_outcome_evidence(uuid,uuid,text,text),impact.act_ai_outcome_evidence(uuid,uuid,text,uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.prepare_ai_outcome_evidence(uuid,uuid,text,text),impact.act_ai_outcome_evidence(uuid,uuid,text,uuid,uuid) TO impact_platform;
REVOKE ALL ON FUNCTION impact.prepare_ai_outcome_evidence(uuid,uuid,text,text),impact.act_ai_outcome_evidence(uuid,uuid,text,uuid,uuid) FROM impact_app,impact_identity,impact_worker;
COMMIT;
