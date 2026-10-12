BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.sponsored_cohort(
 sponsor_tenant_id uuid NOT NULL REFERENCES impact.tenant_root(tenant_id), cohort_id uuid NOT NULL,
 title varchar(200) NOT NULL, duration_days integer NOT NULL CHECK(duration_days BETWEEN 1 AND 3660),
 budget numeric(38,12) NOT NULL CHECK(budget>0), currency varchar(3) NOT NULL,
 terms_version varchar(100) NOT NULL, created_by uuid NOT NULL, created_at timestamptz NOT NULL,
 PRIMARY KEY(sponsor_tenant_id,cohort_id),
 FOREIGN KEY(sponsor_tenant_id,created_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.sponsored_cohort ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.sponsored_cohort FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.sponsored_cohort USING(sponsor_tenant_id=impact.current_tenant()) WITH CHECK(sponsor_tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.sponsored_cohort TO impact_app;
CREATE TABLE impact.sponsored_enrolment(
 sponsor_tenant_id uuid NOT NULL, cohort_id uuid NOT NULL, grantee_tenant_id uuid NOT NULL REFERENCES impact.tenant_root(tenant_id),
 enrolment_id uuid NOT NULL, duration_days integer NOT NULL, budget numeric(38,12) NOT NULL, currency varchar(3) NOT NULL,
 terms_version varchar(100) NOT NULL, status varchar(16) NOT NULL CHECK(status IN('INVITED','ACCEPTED')),
 accepted_by uuid, accepted_at timestamptz, access_starts_at timestamptz, access_ends_at timestamptz,
 no_charge boolean NOT NULL DEFAULT true CHECK(no_charge),
 PRIMARY KEY(sponsor_tenant_id,enrolment_id), UNIQUE(sponsor_tenant_id,cohort_id,grantee_tenant_id), UNIQUE(grantee_tenant_id,enrolment_id),
 FOREIGN KEY(sponsor_tenant_id,cohort_id) REFERENCES impact.sponsored_cohort(sponsor_tenant_id,cohort_id),
 FOREIGN KEY(grantee_tenant_id,accepted_by) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED
);
ALTER TABLE impact.sponsored_enrolment ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.sponsored_enrolment FORCE ROW LEVEL SECURITY;
CREATE POLICY sponsored_enrolment_select ON impact.sponsored_enrolment FOR SELECT USING(sponsor_tenant_id=impact.current_tenant() OR grantee_tenant_id=impact.current_tenant());
CREATE POLICY sponsored_enrolment_insert ON impact.sponsored_enrolment FOR INSERT WITH CHECK(sponsor_tenant_id=impact.current_tenant() AND status='INVITED');
CREATE POLICY sponsored_enrolment_accept ON impact.sponsored_enrolment FOR UPDATE USING(grantee_tenant_id=impact.current_tenant() AND status='INVITED') WITH CHECK(grantee_tenant_id=impact.current_tenant() AND status='ACCEPTED' AND no_charge);
GRANT SELECT,INSERT,UPDATE ON impact.sponsored_enrolment TO impact_app;
CREATE FUNCTION impact.guard_sponsored_enrolment_acceptance() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
 IF NEW.sponsor_tenant_id IS DISTINCT FROM OLD.sponsor_tenant_id OR NEW.cohort_id IS DISTINCT FROM OLD.cohort_id OR NEW.grantee_tenant_id IS DISTINCT FROM OLD.grantee_tenant_id OR NEW.enrolment_id IS DISTINCT FROM OLD.enrolment_id OR NEW.duration_days IS DISTINCT FROM OLD.duration_days OR NEW.budget IS DISTINCT FROM OLD.budget OR NEW.currency IS DISTINCT FROM OLD.currency OR NEW.terms_version IS DISTINCT FROM OLD.terms_version OR NEW.no_charge IS DISTINCT FROM OLD.no_charge OR OLD.status<>'INVITED' OR NEW.status<>'ACCEPTED' OR NEW.accepted_by IS NULL OR NEW.accepted_at IS NULL OR NEW.access_starts_at IS DISTINCT FROM NEW.accepted_at OR NEW.access_ends_at IS DISTINCT FROM NEW.accepted_at+make_interval(days=>NEW.duration_days) THEN RAISE EXCEPTION 'invalid sponsored acceptance'; END IF; RETURN NEW; END $$;
CREATE TRIGGER sponsored_enrolment_acceptance_guard BEFORE UPDATE ON impact.sponsored_enrolment FOR EACH ROW EXECUTE FUNCTION impact.guard_sponsored_enrolment_acceptance();
CREATE TABLE impact.sponsored_enrolment_event(
 grantee_tenant_id uuid NOT NULL, event_id uuid NOT NULL, sponsor_tenant_id uuid NOT NULL, enrolment_id uuid NOT NULL,
 event_type varchar(16) NOT NULL CHECK(event_type='ACCEPTED'), actor_id uuid NOT NULL, occurred_at timestamptz NOT NULL,
 PRIMARY KEY(grantee_tenant_id,event_id),
 FOREIGN KEY(sponsor_tenant_id,enrolment_id) REFERENCES impact.sponsored_enrolment(sponsor_tenant_id,enrolment_id)
);
ALTER TABLE impact.sponsored_enrolment_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.sponsored_enrolment_event FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.sponsored_enrolment_event USING(grantee_tenant_id=impact.current_tenant()) WITH CHECK(grantee_tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.sponsored_enrolment_event TO impact_app;
COMMIT;
