BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.commercial_invoice(
 tenant_id uuid NOT NULL, invoice_id uuid NOT NULL, subscription_id uuid NOT NULL,
 currency varchar(3) NOT NULL, status varchar(16) NOT NULL CHECK(status='OPEN'), created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,invoice_id), UNIQUE(tenant_id,subscription_id,status),
 FOREIGN KEY(tenant_id,subscription_id) REFERENCES impact.subscription_current(tenant_id,object_id)
);
CREATE TABLE impact.commercial_invoice_item(
 tenant_id uuid NOT NULL, invoice_id uuid NOT NULL, item_id uuid NOT NULL, item_kind varchar(32) NOT NULL CHECK(item_kind='FIXED_FEE_SERVICE'),
 package_code varchar(64) NOT NULL, scope text NOT NULL CHECK(length(scope)>0), quantity integer NOT NULL CHECK(quantity=1),
 unit_price numeric(38,12) NOT NULL CHECK(unit_price>0), currency varchar(3) NOT NULL, purchased_by uuid NOT NULL, purchased_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,item_id), FOREIGN KEY(tenant_id,invoice_id) REFERENCES impact.commercial_invoice(tenant_id,invoice_id),
 FOREIGN KEY(tenant_id,purchased_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
DO $$ DECLARE table_name text; BEGIN FOREACH table_name IN ARRAY ARRAY['commercial_invoice','commercial_invoice_item'] LOOP
 EXECUTE format('ALTER TABLE impact.%I ENABLE ROW LEVEL SECURITY',table_name); EXECUTE format('ALTER TABLE impact.%I FORCE ROW LEVEL SECURITY',table_name);
 EXECUTE format('CREATE POLICY tenant_fence ON impact.%I USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant())',table_name);
 EXECUTE format('GRANT SELECT,INSERT ON impact.%I TO impact_app',table_name);
 END LOOP; END $$;
COMMIT;
