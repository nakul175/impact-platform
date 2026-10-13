BEGIN;
SET LOCAL ROLE impact_owner;
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''AIImproveDiagnosisCycle'')');
END $$;
CREATE TABLE impact.ai_improve_diagnosis_cycle(
 tenant_id uuid NOT NULL, cycle_id uuid NOT NULL, cycle_revision uuid NOT NULL,
 cycle_kind text GENERATED ALWAYS AS ('AIImproveDiagnosisCycle') STORED,
 suggestion_id uuid NOT NULL, source_review_id uuid NOT NULL, source_review_revision uuid NOT NULL,
 source_review_kind text GENERATED ALWAYS AS ('AIQuarterlyValueReview') STORED,
 source_diagnosis_id uuid NOT NULL, source_diagnosis_revision uuid NOT NULL,
 source_diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 source_problem_id uuid NOT NULL, created_diagnosis_id uuid NOT NULL, created_diagnosis_revision uuid NOT NULL,
 created_diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 taker_principal_id uuid NOT NULL, taker_membership_id uuid NOT NULL, taker_membership_revision uuid NOT NULL,
 taker_membership_kind text GENERATED ALWAYS AS ('Membership') STORED,
 operation_id uuid NOT NULL, payload_hash bytea NOT NULL CHECK(octet_length(payload_hash)=32),
 correlation_id uuid NOT NULL, taken_up_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,cycle_id), UNIQUE(tenant_id,suggestion_id), UNIQUE(tenant_id,taker_principal_id,operation_id),
 FOREIGN KEY(tenant_id,cycle_id,cycle_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,cycle_revision,cycle_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,source_review_id,source_review_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,source_review_revision,source_review_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,source_diagnosis_id,source_diagnosis_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,source_diagnosis_revision,source_diagnosis_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,created_diagnosis_id,created_diagnosis_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,created_diagnosis_revision,created_diagnosis_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,taker_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,taker_membership_id,taker_membership_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,taker_membership_revision,taker_membership_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type)
);
ALTER TABLE impact.ai_improve_diagnosis_cycle ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_improve_diagnosis_cycle FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_improve_diagnosis_cycle USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_improve_diagnosis_cycle TO impact_app;
CREATE FUNCTION impact.guard_ai_improve_cycle_immutable() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN RAISE EXCEPTION 'improve diagnosis cycle records are immutable' USING ERRCODE='42501'; END;
$$;
REVOKE ALL ON FUNCTION impact.guard_ai_improve_cycle_immutable() FROM PUBLIC;
CREATE TRIGGER ai_improve_cycle_immutable BEFORE UPDATE OR DELETE ON impact.ai_improve_diagnosis_cycle FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_improve_cycle_immutable();
CREATE POLICY worker_improve_cycle_registry_fence ON impact.object_registry AS RESTRICTIVE FOR ALL TO impact_worker USING(object_type<>'AIImproveDiagnosisCycle') WITH CHECK(object_type<>'AIImproveDiagnosisCycle');
CREATE POLICY worker_improve_cycle_revision_fence ON impact.object_revision AS RESTRICTIVE FOR ALL TO impact_worker USING(object_type<>'AIImproveDiagnosisCycle') WITH CHECK(object_type<>'AIImproveDiagnosisCycle');
COMMIT;
