BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.access_change_event(
 tenant_id uuid NOT NULL, event_id bigint GENERATED ALWAYS AS IDENTITY, policy_epoch bigint NOT NULL,
 occurred_at timestamptz NOT NULL, PRIMARY KEY(tenant_id,event_id)
);
CREATE TABLE impact.presentation_lease(
 tenant_id uuid NOT NULL, lease_id uuid NOT NULL, principal_id uuid NOT NULL,
 derivative_id uuid NOT NULL, derivative_revision_id uuid NOT NULL, policy_epoch bigint NOT NULL,
 issued_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,lease_id),
 FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,derivative_id,derivative_revision_id) REFERENCES impact.derivative_manifest(tenant_id,derivative_id,derivative_revision_id),
 CHECK(expires_at>issued_at AND expires_at<=issued_at+interval '60 seconds')
);
CREATE FUNCTION impact.record_policy_epoch_change() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF NEW.policy_epoch<>OLD.policy_epoch THEN
  INSERT INTO impact.access_change_event(tenant_id,policy_epoch,occurred_at) VALUES(NEW.tenant_id,NEW.policy_epoch,clock_timestamp());
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER record_policy_epoch_change AFTER UPDATE OF policy_epoch ON impact.tenant_root FOR EACH ROW EXECUTE FUNCTION impact.record_policy_epoch_change();
ALTER TABLE impact.access_change_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.access_change_event FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.access_change_event USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.presentation_lease ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.presentation_lease FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.presentation_lease USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT ON impact.access_change_event TO impact_app,impact_worker;
GRANT SELECT,INSERT ON impact.presentation_lease TO impact_app;
COMMIT;
