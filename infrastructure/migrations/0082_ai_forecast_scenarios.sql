BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.ai_forecast_scenario(
 tenant_id uuid NOT NULL, scenario_id uuid NOT NULL, version integer NOT NULL CHECK(version>0),
 operation_id uuid NOT NULL, requester_id uuid NOT NULL, request_fingerprint bytea NOT NULL CHECK(octet_length(request_fingerprint)=32),
 label text NOT NULL CHECK(length(label) BETWEEN 1 AND 240),
 status text NOT NULL CHECK(status IN('EXPLORATORY','PROJECTION')),
 horizon integer NOT NULL CHECK(horizon BETWEEN 1 AND 24), method text NOT NULL CHECK(method='LINEAR_TREND_V1'),
 assumptions jsonb NOT NULL CHECK(jsonb_typeof(assumptions)='array' AND jsonb_array_length(assumptions)<=20),
 validation_history jsonb NOT NULL CHECK(jsonb_typeof(validation_history)='object'),
 unit text NOT NULL CHECK(length(unit) BETWEEN 1 AND 64), projections jsonb NOT NULL CHECK(jsonb_typeof(projections)='array'),
 created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,scenario_id,version), UNIQUE(tenant_id,operation_id),
 FOREIGN KEY(tenant_id,requester_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.ai_forecast_input(
 tenant_id uuid NOT NULL, scenario_id uuid NOT NULL, version integer NOT NULL,
 ordinal integer NOT NULL CHECK(ordinal BETWEEN 1 AND 24), object_id uuid NOT NULL, revision_id uuid NOT NULL,
 PRIMARY KEY(tenant_id,scenario_id,version,ordinal), UNIQUE(tenant_id,scenario_id,version,revision_id),
 FOREIGN KEY(tenant_id,scenario_id,version) REFERENCES impact.ai_forecast_scenario(tenant_id,scenario_id,version),
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
CREATE TABLE impact.ai_forecast_adoption_review(
 tenant_id uuid NOT NULL, review_id uuid NOT NULL, scenario_id uuid NOT NULL, version integer NOT NULL,
 requester_id uuid NOT NULL, state text NOT NULL CHECK(state='PENDING'), requested_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,review_id), UNIQUE(tenant_id,scenario_id,version),
 FOREIGN KEY(tenant_id,scenario_id,version) REFERENCES impact.ai_forecast_scenario(tenant_id,scenario_id,version),
 FOREIGN KEY(tenant_id,requester_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.ai_forecast_scenario ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_forecast_scenario FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_forecast_input ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_forecast_input FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_forecast_adoption_review ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.ai_forecast_adoption_review FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_forecast_scenario USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_forecast_input USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.ai_forecast_adoption_review USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_forecast_scenario,impact.ai_forecast_input,impact.ai_forecast_adoption_review TO impact_app;
COMMIT;
