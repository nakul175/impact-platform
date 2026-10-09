BEGIN;
SET LOCAL ROLE impact_owner;
-- US-MP-03 rank opportunities with the organisation's weights. Additive: the registry kind
-- AIRankingWeights (each saved set of weights is the next immutable revision of the tenant's single
-- object, using the existing forced-RLS registry, revisions, audit, outbox and receipts) and the
-- singleton index. No projection table, no new grant, no role or policy change.

-- Extend the current check, preserving kinds introduced by every prior migration (as 0034, 0035, 0038).
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''AIRankingWeights'')');
END $$;

-- One AIRankingWeights object per tenant; every change of weights is its next revision.
CREATE UNIQUE INDEX ai_ranking_weights_one_per_tenant ON impact.object_registry(tenant_id)
 WHERE object_type='AIRankingWeights';
COMMIT;
