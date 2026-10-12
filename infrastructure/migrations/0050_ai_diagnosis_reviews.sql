-- Assigned, immutable human review of exact completed diagnosis revisions.
BEGIN;
SET LOCAL ROLE impact_owner;

WITH previous AS (
 SELECT manifest FROM impact.platform_access_profile WHERE source_migration='0049_ai_diagnosis_contributions.sql'
), expanded AS (
 SELECT jsonb_set(previous.manifest,'{roles,REVIEWER}',
  (SELECT jsonb_agg(to_jsonb(capability) ORDER BY capability) FROM (
    SELECT jsonb_array_elements_text(previous.manifest->'roles'->'REVIEWER') capability
    UNION VALUES('ai.diagnosis.review')
  ) x)) AS manifest FROM previous
)
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration)
 SELECT 'a06bc846eba18f57ace5c13e7b74268e38a869a33f834c975c20377d4bd5f316',manifest,'0050_ai_diagnosis_reviews.sql' FROM expanded;

CREATE TABLE impact.ai_diagnosis_review_request(
 tenant_id uuid NOT NULL, review_id uuid NOT NULL, diagnosis_id uuid NOT NULL,
 diagnosis_revision uuid NOT NULL, diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 requester_principal_id uuid NOT NULL, requester_membership_id uuid NOT NULL,
 advisor_principal_id uuid NOT NULL, advisor_membership_id uuid NOT NULL,
 advisor_natural_identity_id uuid NOT NULL, requested_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,review_id), UNIQUE(tenant_id,diagnosis_id,diagnosis_revision,advisor_principal_id),
 FOREIGN KEY(tenant_id,diagnosis_id,diagnosis_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,diagnosis_revision,diagnosis_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,requester_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,requester_membership_id) REFERENCES impact.membership_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,advisor_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,advisor_membership_id) REFERENCES impact.membership_current(tenant_id,object_id)
);
CREATE TABLE impact.ai_diagnosis_review_event(
 tenant_id uuid NOT NULL, event_id uuid NOT NULL, review_id uuid NOT NULL,
 kind text NOT NULL CHECK(kind IN ('STARTED','COMMENTED','VALIDATED')),
 comment text, actor_principal_id uuid NOT NULL, actor_membership_id uuid NOT NULL,
 actor_natural_identity_id uuid NOT NULL, recorded_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,event_id), FOREIGN KEY(tenant_id,review_id) REFERENCES impact.ai_diagnosis_review_request(tenant_id,review_id),
 FOREIGN KEY(tenant_id,actor_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,actor_membership_id) REFERENCES impact.membership_current(tenant_id,object_id),
 CHECK((kind='COMMENTED' AND comment IS NOT NULL AND length(btrim(comment)) BETWEEN 1 AND 4000) OR (kind<>'COMMENTED' AND comment IS NULL))
);
CREATE INDEX ai_diagnosis_review_queue ON impact.ai_diagnosis_review_request(tenant_id,advisor_principal_id,requested_at,review_id);
CREATE INDEX ai_diagnosis_review_history ON impact.ai_diagnosis_review_request(tenant_id,diagnosis_id,requested_at,review_id);
ALTER TABLE impact.ai_diagnosis_review_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_diagnosis_review_request FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_diagnosis_review_request USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_diagnosis_review_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_diagnosis_review_event FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_diagnosis_review_event USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_diagnosis_review_request,impact.ai_diagnosis_review_event TO impact_app;
CREATE FUNCTION impact.guard_ai_diagnosis_review_immutable() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'diagnosis review records are immutable' USING ERRCODE='42501'; END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION impact.guard_ai_diagnosis_review_immutable() FROM PUBLIC;
CREATE TRIGGER ai_diagnosis_review_request_immutable BEFORE UPDATE OR DELETE ON impact.ai_diagnosis_review_request FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_diagnosis_review_immutable();
CREATE TRIGGER ai_diagnosis_review_event_immutable BEFORE UPDATE OR DELETE ON impact.ai_diagnosis_review_event FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_diagnosis_review_immutable();
COMMIT;
