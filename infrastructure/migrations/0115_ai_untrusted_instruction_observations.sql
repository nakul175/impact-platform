-- Persist only coarse refused-instruction categories for advisory inputs; never source content.
BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.ai_untrusted_instruction_observation(
  tenant_id uuid NOT NULL,
  observation_id uuid NOT NULL,
  request_object_id uuid NOT NULL,
  request_revision_id uuid NOT NULL,
  categories text[] NOT NULL,
  executed_actions integer NOT NULL DEFAULT 0 CHECK(executed_actions=0),
  observed_by uuid NOT NULL,
  observed_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,observation_id),
  UNIQUE(tenant_id,request_object_id,request_revision_id),
  FOREIGN KEY(tenant_id,request_object_id,request_revision_id)
    REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,observed_by)
    REFERENCES impact.tenant_principal(tenant_id,principal_id),
  CHECK(cardinality(categories) BETWEEN 1 AND 4),
  CHECK(categories <@ ARRAY[
    'BULK_EXPORT','CREDENTIAL_DISCLOSURE','CROSS_TENANT_RETRIEVAL','UNAPPROVED_DESTINATION'
  ]::text[])
);

ALTER TABLE impact.ai_untrusted_instruction_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_untrusted_instruction_observation FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_untrusted_instruction_observation
  USING(tenant_id=impact.current_tenant())
  WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT ON impact.ai_untrusted_instruction_observation TO impact_app;

COMMIT;
