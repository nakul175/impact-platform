BEGIN;
SET LOCAL ROLE impact_owner;
-- Security and privacy (v0.27): denial auditing, the durable audit-export register, tenant
-- retention policies with an insert-only binding register, a guarded retention-hold API and the
-- retention definers the worker needs to honour an approved policy.
--
-- Denial auditing. A refused authorisation (store.authorize: POLICY_DENIED, a hidden
-- RESOURCE_UNAVAILABLE, PURPOSE_REQUIRED, ASSURANCE_REQUIRED) is recorded after the refused
-- transaction rolled back, through the SECURITY DEFINER impact.record_access_denial only: the
-- application holds SELECT on the table and nothing else. Repeats by the same principal for the
-- same operation and reason inside one window collapse into one row whose counter advances, and a
-- principal that is refused for more than a bounded number of distinct (operation, reason) pairs in
-- a window is collapsed into one overflow row, so a scan cannot flood the table. Rows are deleted
-- only by the retention sweep (SECURITY_EVENT class) beyond the tenant's audit window, never
-- inside the 365-day floor. No payload, secret or address is ever recorded.
CREATE TABLE impact.access_denial(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  denial_id uuid NOT NULL,
  principal_id uuid NOT NULL,
  window_start timestamptz NOT NULL,
  operation_id varchar(128) NOT NULL,
  capability varchar(128) NOT NULL,
  route varchar(256) NOT NULL,
  status integer NOT NULL CHECK(status IN (403,404)),
  code varchar(64) NOT NULL CHECK(code ~ '^[A-Z][A-Z0-9_]{0,63}$'),
  reason_code varchar(64) NOT NULL CHECK(reason_code ~ '^[A-Z][A-Z0-9_]{0,63}$'),
  object_id uuid,
  first_at timestamptz NOT NULL,
  last_at timestamptz NOT NULL,
  first_correlation_id uuid NOT NULL,
  last_correlation_id uuid NOT NULL,
  occurrences integer NOT NULL CHECK(occurrences>=1),
  PRIMARY KEY(tenant_id,denial_id),
  UNIQUE(tenant_id,principal_id,window_start,operation_id,reason_code),
  FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX access_denial_recent ON impact.access_denial(tenant_id,first_at,denial_id);
CREATE INDEX access_denial_age ON impact.access_denial(tenant_id,last_at);

-- Identity columns are immutable; only the counter and the last-seen fields may advance.
CREATE FUNCTION impact.access_denial_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
  IF (to_jsonb(OLD)-'occurrences'-'last_at'-'last_correlation_id') IS DISTINCT FROM
     (to_jsonb(NEW)-'occurrences'-'last_at'-'last_correlation_id') OR NEW.occurrences<OLD.occurrences THEN
    RAISE EXCEPTION 'access_denial rows only accumulate' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.access_denial_guard() FROM PUBLIC;
CREATE TRIGGER access_denial_guard BEFORE UPDATE ON impact.access_denial FOR EACH ROW EXECUTE FUNCTION impact.access_denial_guard();

-- Record one denial for the current tenant: collapse a repeat (same principal, operation and reason
-- in the same window), else insert, unless the principal already holds cap distinct rows in the
-- window, in which case one overflow row (operation '*', reason DENIAL_LIMIT) counts the rest.
-- The window is anchored on the database clock. Returns the row that absorbed the denial.
CREATE FUNCTION impact.record_access_denial(principal uuid, operation text, cap_name text, route_name text,
  http_status integer, error_code text, reason text, selector uuid, correlation uuid,
  window_seconds integer, cap integer) RETURNS uuid
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE v_tenant uuid := impact.current_tenant(); v_at timestamptz := statement_timestamp();
        v_window timestamptz; v_id uuid; v_rows integer;
BEGIN
  IF v_tenant IS NULL OR window_seconds<1 OR cap<1 THEN RAISE EXCEPTION 'tenant context required' USING ERRCODE='42501'; END IF;
  IF NOT EXISTS(SELECT 1 FROM impact.tenant_principal p WHERE p.tenant_id=v_tenant AND p.principal_id=principal) THEN
    RAISE EXCEPTION 'principal required' USING ERRCODE='42501';
  END IF;
  v_window := to_timestamp(floor(extract(epoch FROM v_at)/window_seconds)*window_seconds);
  UPDATE impact.access_denial SET occurrences=occurrences+1,last_at=v_at,last_correlation_id=correlation
   WHERE tenant_id=v_tenant AND principal_id=principal AND window_start=v_window AND operation_id=operation
     AND reason_code=reason RETURNING denial_id INTO v_id;
  IF v_id IS NOT NULL THEN RETURN v_id; END IF;
  SELECT count(*) INTO v_rows FROM impact.access_denial
   WHERE tenant_id=v_tenant AND principal_id=principal AND window_start=v_window;
  IF v_rows>=cap THEN
    UPDATE impact.access_denial SET occurrences=occurrences+1,last_at=v_at,last_correlation_id=correlation
     WHERE tenant_id=v_tenant AND principal_id=principal AND window_start=v_window AND operation_id='*'
       AND reason_code='DENIAL_LIMIT' RETURNING denial_id INTO v_id;
    IF v_id IS NOT NULL THEN RETURN v_id; END IF;
    operation := '*'; cap_name := '*'; route_name := '*'; reason := 'DENIAL_LIMIT'; error_code := 'POLICY_DENIED';
    http_status := 403; selector := NULL;
  END IF;
  v_id := gen_random_uuid();
  INSERT INTO impact.access_denial(tenant_id,denial_id,principal_id,window_start,operation_id,capability,route,status,
    code,reason_code,object_id,first_at,last_at,first_correlation_id,last_correlation_id,occurrences)
   VALUES(v_tenant,v_id,principal,v_window,operation,cap_name,route_name,http_status,error_code,reason,selector,
    v_at,v_at,correlation,correlation,1);
  RETURN v_id;
END $$;
REVOKE ALL ON FUNCTION impact.record_access_denial(uuid,text,text,text,integer,text,text,uuid,uuid,integer,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.record_access_denial(uuid,text,text,text,integer,text,text,uuid,uuid,integer,integer) TO impact_app;

-- Durable audit-export register (the DDL proposal of RELEASE-0.25a): one insert-only row per
-- exported page, keyed by the export's own AuditEvent, so the window, purpose, digest, chain and
-- seal key of every export outlive the 7-day operation receipt. Never updated or deleted.
CREATE TABLE impact.audit_export_register(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  export_id uuid NOT NULL,
  export_id_kind text GENERATED ALWAYS AS ('AuditEvent') STORED,
  principal_id uuid NOT NULL,
  purpose varchar(64) NOT NULL,
  reason varchar(2000) NOT NULL,
  window_start timestamptz NOT NULL,
  window_end timestamptz NOT NULL CHECK(window_end>window_start),
  page integer NOT NULL CHECK(page>=1),
  first_sequence integer CHECK(first_sequence IS NULL OR first_sequence>=1),
  event_count integer NOT NULL CHECK(event_count>=0),
  denial_count integer NOT NULL DEFAULT 0 CHECK(denial_count>=0),
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  chain_start bytea NOT NULL CHECK(octet_length(chain_start)=32),
  chain_end bytea NOT NULL CHECK(octet_length(chain_end)=32),
  seal_key_id varchar(12) NOT NULL CHECK(seal_key_id ~ '^[0-9a-f]{12}$'),
  correlation_id uuid NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,export_id),
  FOREIGN KEY(tenant_id,export_id,export_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX audit_export_register_recent ON impact.audit_export_register(tenant_id,created_at);

-- Tenant retention policies (FR-PRV-004, VF-PRV-002). RetentionPolicy has been a registry kind with
-- a typed projection since 0002; these columns carry the proposal's reason and the server-set
-- approval. Each independent approval appends one row to the insert-only binding register; the
-- sweep applies, per data class, the latest binding and otherwise the build's fixed schedule.
ALTER TABLE impact.retention_policy_current
 ADD COLUMN reason varchar(2000),
 ADD COLUMN approved_by uuid,
 ADD COLUMN approved_at timestamptz,
 ADD COLUMN approved_revision uuid,
 ADD COLUMN supersedes_revision uuid,
 ADD COLUMN supersedes_revision_kind text GENERATED ALWAYS AS ('RetentionPolicy') STORED,
 ADD CONSTRAINT retention_policy_supersedes_fk FOREIGN KEY(tenant_id,supersedes_revision)
  REFERENCES impact.object_revision(tenant_id,revision_id) DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE impact.retention_policy_binding(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  binding_id uuid NOT NULL,
  data_class varchar(64) NOT NULL CHECK(data_class ~ '^[A-Z][A-Z0-9_]{0,63}$'),
  policy_id uuid NOT NULL,
  policy_revision uuid NOT NULL,
  duration_days integer NOT NULL CHECK(duration_days>=0),
  action varchar(16) NOT NULL CHECK(action IN ('DELETE','REDACT','EXPIRE')),
  proposed_by uuid NOT NULL,
  approved_by uuid NOT NULL,
  approved_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,binding_id),
  UNIQUE(tenant_id,policy_id,policy_revision),
  FOREIGN KEY(tenant_id,policy_id) REFERENCES impact.retention_policy_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,policy_id,policy_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,approved_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX retention_policy_binding_current ON impact.retention_policy_binding(tenant_id,data_class,approved_at DESC);

-- Retention holds through the API: who placed the hold, why, and the independent release.
ALTER TABLE impact.retention_hold
 ADD COLUMN reason varchar(2000),
 ADD COLUMN placed_by uuid,
 ADD COLUMN placed_at timestamptz,
 ADD COLUMN released_by uuid,
 ADD COLUMN release_reason varchar(2000),
 ADD CONSTRAINT retention_hold_release CHECK((released_at IS NULL)=(released_by IS NULL) OR placed_by IS NULL);
CREATE FUNCTION impact.retention_hold_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
  IF (to_jsonb(OLD)-'released_at'-'released_by'-'release_reason') IS DISTINCT FROM
     (to_jsonb(NEW)-'released_at'-'released_by'-'release_reason') THEN
    RAISE EXCEPTION 'retention_hold is immutable except for its release' USING ERRCODE='23514';
  END IF;
  IF OLD.released_at IS NOT NULL AND (to_jsonb(OLD) IS DISTINCT FROM to_jsonb(NEW)) THEN
    RAISE EXCEPTION 'a released hold is final' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.retention_hold_guard() FROM PUBLIC;
CREATE TRIGGER retention_hold_guard BEFORE UPDATE ON impact.retention_hold FOR EACH ROW EXECUTE FUNCTION impact.retention_hold_guard();

ALTER TABLE impact.access_denial ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.access_denial FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.access_denial USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.audit_export_register ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.audit_export_register FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.audit_export_register USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.retention_policy_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.retention_policy_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.retention_policy_binding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

-- Retention definers for an approved policy (worker). A policy can only lengthen the receipt
-- retention beyond the API's 7-day idempotency window (keep_days below 7 is treated as 7); the
-- security-event window never goes below the 365-day floor whatever the caller supplies. Both act
-- on the current tenant only and compare with the database clock.
CREATE FUNCTION impact.retention_purge_receipts(max_rows integer, keep_days integer) RETURNS TABLE(item text)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DELETE FROM impact.operation_receipt o USING (
  SELECT tenant_id,actor_id,command_type,operation_id FROM impact.operation_receipt
   WHERE tenant_id=impact.current_tenant()
     AND expires_at<=statement_timestamp()-make_interval(days=>greatest(keep_days,7)-7)
   ORDER BY expires_at,operation_id LIMIT greatest(least(max_rows,5000),0)) d
 WHERE o.tenant_id=d.tenant_id AND o.actor_id=d.actor_id AND o.command_type=d.command_type
   AND o.operation_id=d.operation_id
 RETURNING o.actor_id::text||':'||o.command_type||':'||o.operation_id::text
$$;
REVOKE ALL ON FUNCTION impact.retention_purge_receipts(integer,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.retention_purge_receipts(integer,integer) TO impact_worker;

CREATE FUNCTION impact.retention_purge_security_events(max_rows integer, keep_days integer) RETURNS TABLE(item text)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DELETE FROM impact.access_denial a USING (
  SELECT tenant_id,denial_id FROM impact.access_denial
   WHERE tenant_id=impact.current_tenant()
     AND last_at<=statement_timestamp()-make_interval(days=>greatest(keep_days,365))
   ORDER BY last_at,denial_id LIMIT greatest(least(max_rows,5000),0)) d
 WHERE a.tenant_id=d.tenant_id AND a.denial_id=d.denial_id
 RETURNING a.denial_id::text||':'||a.occurrences::text
$$;
REVOKE ALL ON FUNCTION impact.retention_purge_security_events(integer,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.retention_purge_security_events(integer,integer) TO impact_worker;

-- Application: denials are read-only (written through the definer); the export register and the
-- binding register are insert-only; holds keep their 0003 privileges under the new guard.
GRANT SELECT ON impact.access_denial TO impact_app;
GRANT SELECT,INSERT ON impact.audit_export_register TO impact_app;
GRANT SELECT,INSERT ON impact.retention_policy_binding TO impact_app;
-- Worker: the effective policy per data class, nothing else new.
GRANT SELECT ON impact.retention_policy_binding TO impact_worker;
COMMIT;
