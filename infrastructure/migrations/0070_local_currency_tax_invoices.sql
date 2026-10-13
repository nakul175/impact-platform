BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.billing_market_definition(
 country_code varchar(2) PRIMARY KEY CHECK(country_code~'^[A-Z]{2}$'),
 currency varchar(3) NOT NULL CHECK(currency~'^[A-Z]{3}$'),
 tax_name varchar(32) NOT NULL CHECK(length(tax_name)>0),
 tax_rate numeric(8,5) NOT NULL CHECK(tax_rate>0 AND tax_rate<=100),
 active boolean NOT NULL,
 configured_at timestamptz NOT NULL,
 UNIQUE(country_code,currency)
);
INSERT INTO impact.billing_market_definition VALUES('IN','INR','GST',18,true,statement_timestamp());
GRANT SELECT ON impact.billing_market_definition TO impact_app,impact_platform;

CREATE TABLE impact.tenant_billing_profile(
 tenant_id uuid PRIMARY KEY REFERENCES impact.tenant_root(tenant_id),
 country_code varchar(2) NOT NULL REFERENCES impact.billing_market_definition(country_code),
 currency varchar(3) NOT NULL,
 configured_by uuid NOT NULL,
 configured_at timestamptz NOT NULL,
 FOREIGN KEY(tenant_id,configured_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(country_code,currency) REFERENCES impact.billing_market_definition(country_code,currency)
);
ALTER TABLE impact.tenant_billing_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_billing_profile FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_billing_profile
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.tenant_billing_profile TO impact_app;

ALTER TABLE impact.commercial_invoice
 DROP CONSTRAINT commercial_invoice_status_check,
 DROP CONSTRAINT commercial_invoice_tenant_id_subscription_id_status_key;
CREATE UNIQUE INDEX commercial_invoice_one_open_per_subscription
 ON impact.commercial_invoice(tenant_id,subscription_id) WHERE status='OPEN';
ALTER TABLE impact.commercial_invoice
 ADD COLUMN market_code varchar(2) REFERENCES impact.billing_market_definition(country_code),
 ADD COLUMN subtotal numeric(38,12),
 ADD COLUMN tax_name varchar(32),
 ADD COLUMN tax_rate numeric(8,5),
 ADD COLUMN tax_amount numeric(38,12),
 ADD COLUMN total numeric(38,12),
 ADD COLUMN issued_at timestamptz,
 ADD COLUMN issued_by uuid,
 ADD CONSTRAINT commercial_invoice_issuer_fk FOREIGN KEY(tenant_id,issued_by)
  REFERENCES impact.tenant_principal(tenant_id,principal_id),
 ADD CONSTRAINT commercial_invoice_issue_shape CHECK(
  (status='OPEN' AND market_code IS NULL AND subtotal IS NULL AND tax_name IS NULL AND tax_rate IS NULL AND tax_amount IS NULL AND total IS NULL AND issued_at IS NULL AND issued_by IS NULL)
  OR
  (status='ISSUED' AND market_code IS NOT NULL AND subtotal>0 AND tax_name IS NOT NULL AND tax_rate>0 AND tax_amount>0 AND total=subtotal+tax_amount AND issued_at IS NOT NULL AND issued_by IS NOT NULL)
 );
CREATE FUNCTION impact.freeze_issued_commercial_invoice() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$ BEGIN
 IF OLD.status='ISSUED' THEN RAISE EXCEPTION 'issued commercial invoice is immutable' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER commercial_invoice_issued_immutable BEFORE UPDATE ON impact.commercial_invoice
 FOR EACH ROW EXECUTE FUNCTION impact.freeze_issued_commercial_invoice();
GRANT UPDATE(status,market_code,subtotal,tax_name,tax_rate,tax_amount,total,issued_at,issued_by)
 ON impact.commercial_invoice TO impact_app;

COMMIT;
