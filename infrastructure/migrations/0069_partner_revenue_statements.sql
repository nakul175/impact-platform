BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.partner_revenue_entry(
 entry_id uuid PRIMARY KEY, partner_id uuid NOT NULL, tenant_id uuid NOT NULL REFERENCES impact.tenant_root(tenant_id),
 invoice_id uuid NOT NULL, amount numeric(38,12) NOT NULL CHECK(amount>0), currency varchar(3) NOT NULL,
 occurred_on date NOT NULL, recorded_by uuid NOT NULL REFERENCES impact.auth_identity(identity_id), recorded_at timestamptz NOT NULL,
 UNIQUE(tenant_id,invoice_id,partner_id)
);
CREATE TABLE impact.partner_monthly_statement(
 statement_id uuid PRIMARY KEY, partner_id uuid NOT NULL, month date NOT NULL CHECK(extract(day from month)=1),
 currency varchar(3) NOT NULL, amount numeric(38,12) NOT NULL CHECK(amount>=0), reconciled boolean NOT NULL,
 entry_ids jsonb NOT NULL CHECK(jsonb_typeof(entry_ids)='array'), generated_by uuid NOT NULL REFERENCES impact.auth_identity(identity_id),
 generated_at timestamptz NOT NULL, settled_at timestamptz, settled_by uuid REFERENCES impact.auth_identity(identity_id),
 UNIQUE(partner_id,month)
);
GRANT SELECT,INSERT ON impact.partner_revenue_entry TO impact_platform;
GRANT SELECT,INSERT,UPDATE ON impact.partner_monthly_statement TO impact_platform;
CREATE FUNCTION impact.platform_invoice_total(request_tenant uuid,request_invoice uuid)
RETURNS TABLE(currency varchar,total numeric) LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$ BEGIN
 PERFORM set_config('impact.tenant_id',request_tenant::text,true);
 RETURN QUERY SELECT i.currency,sum(x.unit_price*x.quantity)::numeric FROM impact.commercial_invoice i JOIN impact.commercial_invoice_item x USING(tenant_id,invoice_id)
 WHERE i.tenant_id=request_tenant AND i.invoice_id=request_invoice GROUP BY i.currency;
END $$;
REVOKE ALL ON FUNCTION impact.platform_invoice_total(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.platform_invoice_total(uuid,uuid) TO impact_platform;
COMMIT;
