# Current data dictionary and schema evolution

Build 0.20.0; schema 21 (0.20.0 adds 0021: `form_current.programme_id` with a typed composite foreign key, `submission_current.observation_ids/quarantine_reason/unit_key`, and the insert-only, tenant-fenced register `form_publication`, SELECT and INSERT for `impact_app` only. 0.19.0 added 0020: nullable `indicator_definition_current.disaggregation` and `calculated_result_current.disaggregation` with jsonb type CHECKs. 0.18.0 added 0019: framework and target payload columns on `framework_current` and `target_current` with typed kind columns, composite foreign keys and the CHECK `target_blank_is_not_zero`; the insert-only, tenant-fenced registers `framework_baseline` and `target_binding`, SELECT and INSERT for `impact_app` only. 0.16.0 added 0018: dispatch columns, constraints and indexes on `outbox_delivery` and the revocation of its UPDATE from `impact_app`; `notification_delivery`, `recovery_channel_challenge`, `authority_reminder` and `worker_heartbeat`; the recovery-contact channel columns and `UNIQUE(tenant_id, contact_id)`; the SECURITY DEFINER functions `enqueue_recovery_channel_delivery` and `worker_tenants`; worker grants; and a replaced `tenant_work_impact`. 0.15.0 added 0017. All twenty-one checksums below match `sha256sum` of the files and were verified by the native run, the restore drill and the upgrade check of 30 September 2026). Executable migrations are authoritative. This dictionary retains each table definition and later alteration in execution order, including constraints and role policy. JSONB domain payload fields are specified by the current OpenAPI schemas; scalar column definitions alone are not the full data model.

## Migration register

| Migration | SHA256 |
| --- | --- |
| 0001_roles.sql | 5e75f33a46817c92888cb1c1077ce06887326e38f68d6db5576786705f0f39f7 |
| 0002_domain.sql | 7cfcffcd735e7b7a2843cb675c67b2f0eb360a8e634fb1f0d220771367af5aa0 |
| 0003_security.sql | 9bb472eb6481f95c83e755d6648928e7269958f647ddabf89ec9509bc4e9d148 |
| 0004_application.sql | c3a6f63502127d4b7865f8035c8a7c84d0307323e7744f9c93dd8189825606a4 |
| 0005_access_administration.sql | 3a5509cb2cbacc5473b83f3e0c9d70cd343f416ba49e6a02de38c73b2734260c |
| 0006_measurement_configuration.sql | 081b24b3927a426d4426912764d16c9a792f4e7b5ae84fffd8f2b1eab13e90ce |
| 0007_measurement_changes.sql | 15d8295c57ecc87fa0e7ab1b2881125bec151c13069f2d6ea6c8cb7465f15db0 |
| 0008_period_governance.sql | 867df4f5da210533648944fbc244b6d35a8cda0aede44e2e95415ee0fb925950 |
| 0009_reporting_packages.sql | 9d29b28d90814ed06cea352a0c35353fcb3f6f34d16e3e3727d40e546248525f |
| 0010_work_and_recalculation.sql | ae1179c228a7e5fa4f7ac7f0e4f42377003b76a9924e473981e52a97f72e24e7 |
| 0011_controlled_publication.sql | c0a97842093f07d621e692e6cbc23923135719bfa751c24fa2c9c32827a14683 |
| 0012_workspace_administration.sql | 5ef1bb4c71af91f7bf19fd3b1606c8354d7d3c640031b90ac78898e6cb032596 |
| 0013_tenant_lifecycle.sql | 564e9c0858336297b379e6bb4930d8a92b3b499bf4d6b632f8a3ad994b2e3e5a |
| 0014_initial_access.sql | b91c517920bb28c77eea184e9dc40e717e3ed0e0db2a2bb7656c456de5d45468 |
| 0015_recovery_contacts.sql | 2b721bd91480033d9b3c3e18f8d77e5e2bcb0f675dcf1e88cb33c60e6ebf9d42 |
| 0016_authority_renewal.sql | 2c95596d9088fb2ec025266cffed824a787ec8df3d3dd4021fefe19cb09290cc |
| 0017_provider_logout.sql | 4378cafe2bacbf6266e0d18f5886966a29c0a53b2ba51566b7afc4c04c9c000b |
| 0018_worker_delivery.sql | bd2defdfb56f3332f0cdb1706fd330893497cc3eeb8f45f4277922f0eca9e8b7 |
| 0019_results_framework.sql | e12728cf4bbb2ff544c75183ac9c5371b393f498f7d61ed791d8a08b356c4161 |
| 0020_calculation_methods.sql | 357f7a80ed9b21b618cdf9209d09c00b7683fc69128fc4938c7e27728d51fa31 |
| 0021_web_forms.sql | afd37bd9e4c5fbaf40d65ad0cb46da1ac8bb7b49adf7bb24ce37493ea11342f2 |
| 0022_import_quality.sql | 7ea2f6f67331f02518ce538528cb06353d686835a5ff7c2849d271096e8002ac |
| 0023_evidence_objects.sql | aa6955e3d950925e9a79192d688b9eaed56bec16cd53702225ad5d4c292570fc |
| 0024_report_exports.sql | 2a162567e6414db5d349850bc0d279678203c830d7a3c4fef8751ce7fab8db9f |

## Executable schema definitions

### 0001 roles

Source: infrastructure/migrations/0001_roles.sql

```sql
-- Run once using a deployment administrator authorised to create roles. No login credentials are stored here.
BEGIN;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_owner') THEN CREATE ROLE impact_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; END IF; END $$;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_app') THEN CREATE ROLE impact_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; END IF; END $$;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_worker') THEN CREATE ROLE impact_worker NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; END IF; END $$;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_identity') THEN CREATE ROLE impact_identity NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; END IF; END $$;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_sensitive') THEN CREATE ROLE impact_sensitive NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; END IF; END $$;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_privacy') THEN CREATE ROLE impact_privacy NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; END IF; END $$;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_observer') THEN CREATE ROLE impact_observer NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; END IF; END $$;
CREATE SCHEMA IF NOT EXISTS impact AUTHORIZATION impact_owner;
DO $$ BEGIN IF (SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname='impact')<>'impact_owner' THEN RAISE EXCEPTION 'unexpected schema owner'; END IF; END $$;
REVOKE ALL ON SCHEMA impact FROM PUBLIC;
GRANT USAGE ON SCHEMA impact TO impact_app,impact_worker,impact_identity,impact_sensitive,impact_privacy,impact_observer;
SET LOCAL ROLE impact_owner; CREATE TABLE IF NOT EXISTS impact.schema_migration(version integer PRIMARY KEY, sha256 char(64) NOT NULL, applied_at timestamptz NOT NULL DEFAULT now());
COMMIT;
```

### 0002 domain

Source: infrastructure/migrations/0002_domain.sql

```sql
BEGIN;

SET LOCAL ROLE impact_owner;

CREATE TABLE impact.tenant_root(tenant_id uuid PRIMARY KEY, region_policy text NOT NULL, lifecycle_state text NOT NULL CHECK(lifecycle_state IN ('Requested','Provisioning','Active','Suspended','Closing','Archived','Deleted')),policy_epoch bigint NOT NULL DEFAULT 0 CHECK(policy_epoch>=0));

CREATE TABLE impact.auth_identity(identity_id uuid PRIMARY KEY,issuer text NOT NULL,provider_subject text NOT NULL,natural_identity_id uuid NOT NULL,UNIQUE(issuer,provider_subject));

CREATE TABLE impact.tenant_principal(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,principal_id uuid NOT NULL,identity_id uuid REFERENCES impact.auth_identity,principal_kind text NOT NULL CHECK(principal_kind IN ('HUMAN','SERVICE')),active boolean NOT NULL DEFAULT true,subject_epoch bigint NOT NULL DEFAULT 0 CHECK(subject_epoch>=0),PRIMARY KEY(tenant_id,principal_id),UNIQUE(tenant_id,identity_id));

CREATE TABLE impact.object_registry(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,object_id uuid NOT NULL,object_type text NOT NULL CHECK(object_type IN ('Tenant','Membership','Grant','OrganisationUnit','Programme','Framework','IndicatorDefinition','IndicatorInstance','Target','Dimension','Period','Observation','CalculatedResult','Form','FormField','Assignment','Submission','Participant','ServiceEvent','HandlingRecord','Dataset','ImportJob','QualityIssue','Evidence','Workflow','Decision','Snapshot','Report','Disclosure','BudgetLine','Connection','AITask','PrivacyCase','AuditEvent','Evaluation','RetentionPolicy','Subscription','FundingAgreement','FinanceTransaction','ExchangeRate','AllocationRule','WorkItem','Dashboard','ReportTemplate','Notification','Schedule','QualitativeExtract','Device','SupportRequest','HostingPolicy','PrivacyPolicy','ReportingCalendar','Geography','CalculationRule','LineageManifest','CollectionRound','Notice','Transformation','ImportMapping','QualityRule','WorkflowTemplate','DisclosureReview','AIConfiguration','AIBudget','VerifiedRequester','VerifiedContact','AudienceGroup','Codebook','Attestation','RoleTemplate','ReadinessManifest','AIProposal','CredentialReference','Predicate','Qualification','Checkpoint','EntitlementApproval')),head_revision uuid NOT NULL,lifecycle_state text NOT NULL,classification text NOT NULL CHECK(classification IN ('PUBLIC','INTERNAL','CONFIDENTIAL','RESTRICTED')),owner_id uuid,created_at timestamptz NOT NULL,created_by uuid NOT NULL,updated_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,object_id),UNIQUE(tenant_id,object_id,object_type),FOREIGN KEY(tenant_id,owner_id) REFERENCES impact.tenant_principal DEFERRABLE INITIALLY DEFERRED,FOREIGN KEY(tenant_id,created_by) REFERENCES impact.tenant_principal DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE impact.object_revision(tenant_id uuid NOT NULL,object_id uuid NOT NULL,revision_id uuid NOT NULL,object_type text NOT NULL,predecessor_revision uuid,schema_version text NOT NULL,payload jsonb,payload_sha256 bytea NOT NULL CHECK(octet_length(payload_sha256)=32),author_id uuid NOT NULL,created_at timestamptz NOT NULL,restriction_state text NOT NULL DEFAULT 'AVAILABLE' CHECK(restriction_state IN ('AVAILABLE','RESTRICTED','REMOVED')),PRIMARY KEY(tenant_id,object_id,revision_id),UNIQUE(tenant_id,revision_id),UNIQUE(tenant_id,revision_id,object_type),FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,FOREIGN KEY(tenant_id,object_id,predecessor_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,FOREIGN KEY(tenant_id,author_id) REFERENCES impact.tenant_principal DEFERRABLE INITIALLY DEFERRED,CHECK(payload IS NULL OR jsonb_typeof(payload)='object'),CHECK((restriction_state='REMOVED')=(payload IS NULL)));

ALTER TABLE impact.object_registry ADD CONSTRAINT registry_head FOREIGN KEY(tenant_id,object_id,head_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.object_revision ADD COLUMN revision_number bigint NOT NULL DEFAULT 1 CHECK(revision_number>=1), ADD UNIQUE(tenant_id,object_id,revision_number);

CREATE TABLE impact.tenant_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Tenant') STORED,
operating_name varchar(200),
owner_membership_id uuid,
owner_membership_id_kind text GENERATED ALWAYS AS ('Membership') STORED,
reporting_zone text,
hosting_policy_id uuid,
hosting_policy_id_kind text GENERATED ALWAYS AS ('HostingPolicy') STORED,
privacy_policy_id uuid,
privacy_policy_id_kind text GENERATED ALWAYS AS ('PrivacyPolicy') STORED,
retention_policy_id uuid,
retention_policy_id_kind text GENERATED ALWAYS AS ('RetentionPolicy') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.membership_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Membership') STORED,
identity_id uuid,
authority_source text,
external boolean,
expires_at timestamptz,
status text,
joined_at timestamptz,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(external IS DISTINCT FROM true OR expires_at IS NOT NULL)
);

CREATE TABLE impact.grant_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Grant') STORED,
subject_id uuid,
capability varchar(64),
scope_id uuid,
starts_at timestamptz,
expires_at timestamptz,
purpose varchar(64),
issuer_id uuid,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(starts_at IS NULL OR expires_at IS NULL OR starts_at<expires_at)
);

CREATE TABLE impact.organisation_unit_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('OrganisationUnit') STORED,
code varchar(64),
name varchar(200),
parent_id uuid,
parent_id_kind text GENERATED ALWAYS AS ('OrganisationUnit') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.programme_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Programme') STORED,
code varchar(64),
title varchar(200),
programme_type varchar(64),
starts_at timestamptz,
ends_at timestamptz,
reporting_calendar_id uuid,
reporting_calendar_id_kind text GENERATED ALWAYS AS ('ReportingCalendar') STORED,
geography_id uuid,
geography_id_kind text GENERATED ALWAYS AS ('Geography') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(ends_at IS NULL OR starts_at IS NULL OR ends_at>=starts_at)
);

CREATE TABLE impact.framework_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Framework') STORED,
programme_id uuid,
programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
version_label varchar(64),
nodes jsonb,
relationships jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(nodes IS NULL OR jsonb_typeof(nodes)='array'),
CHECK(relationships IS NULL OR jsonb_typeof(relationships)='array')
);

CREATE TABLE impact.indicator_definition_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('IndicatorDefinition') STORED,
code varchar(64),
name varchar(200),
measurement_type varchar(64),
unit varchar(64),
population text,
inclusion text,
exclusion text,
method text,
source_mode varchar(64),
time_semantic varchar(64),
combination_rule varchar(64),
display_decimals integer,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(display_decimals IS NULL OR display_decimals>=0),
CHECK(display_decimals IS NULL OR display_decimals BETWEEN 0 AND 6)
);

CREATE TABLE impact.indicator_instance_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('IndicatorInstance') STORED,
definition_version uuid,
definition_version_kind text GENERATED ALWAYS AS ('IndicatorDefinition') STORED,
programme_id uuid,
programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
local_applicability text,
collector_id uuid,
reviewer_id uuid,
schedule_id uuid,
schedule_id_kind text GENERATED ALWAYS AS ('Schedule') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.target_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Target') STORED,
indicator_version uuid,
indicator_version_kind text GENERATED ALWAYS AS ('IndicatorDefinition') STORED,
period_id uuid,
period_id_kind text GENERATED ALWAYS AS ('Period') STORED,
target_kind varchar(64),
value_state varchar(32),
value numeric(38,12),
low numeric(38,12),
high numeric(38,12),
direction varchar(64),
target_basis varchar(64),
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(low IS NULL OR high IS NULL OR low<=high)
);

CREATE TABLE impact.dimension_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Dimension') STORED,
code varchar(64),
label varchar(200),
categories jsonb,
mutually_exclusive boolean,
exhaustive boolean,
effective_at timestamptz,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(categories IS NULL OR jsonb_typeof(categories)='array')
);

CREATE TABLE impact.period_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Period') STORED,
calendar_version uuid,
calendar_version_kind text GENERATED ALWAYS AS ('ReportingCalendar') STORED,
code varchar(64),
starts_at timestamptz,
ends_at timestamptz,
reporting_zone text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(starts_at IS NULL OR ends_at IS NULL OR starts_at<ends_at)
);

CREATE TABLE impact.observation_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Observation') STORED,
source_namespace varchar(64),
source_key text,
indicator_id uuid,
indicator_id_kind text GENERATED ALWAYS AS ('IndicatorInstance') STORED,
dataset_id uuid,
dataset_id_kind text GENERATED ALWAYS AS ('Dataset') STORED,
event_at timestamptz,
captured_at timestamptz,
capture_zone text,
value_state varchar(32),
value numeric(38,12),
numerator numeric(38,12),
denominator numeric(38,12),
source_version text,
dimension_values jsonb,
approval_state text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(dimension_values IS NULL OR jsonb_typeof(dimension_values)='object'),
CHECK(value_state IS NULL OR value_state IN ('PRESENT','MISSING','NOT_COLLECTED','NOT_APPLICABLE','INVALID','UNDEFINED')),
CHECK((value_state='PRESENT' AND value IS NOT NULL) OR ((value_state IS NULL OR value_state<>'PRESENT') AND value IS NULL)),
CHECK(numerator IS NULL OR denominator IS NULL OR denominator>=0)
) PARTITION BY HASH(tenant_id);

CREATE TABLE impact.observation_p00 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 0);

CREATE TABLE impact.observation_p01 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 1);

CREATE TABLE impact.observation_p02 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 2);

CREATE TABLE impact.observation_p03 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 3);

CREATE TABLE impact.observation_p04 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 4);

CREATE TABLE impact.observation_p05 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 5);

CREATE TABLE impact.observation_p06 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 6);

CREATE TABLE impact.observation_p07 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 7);

CREATE TABLE impact.observation_p08 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 8);

CREATE TABLE impact.observation_p09 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 9);

CREATE TABLE impact.observation_p10 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 10);

CREATE TABLE impact.observation_p11 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 11);

CREATE TABLE impact.observation_p12 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 12);

CREATE TABLE impact.observation_p13 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 13);

CREATE TABLE impact.observation_p14 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 14);

CREATE TABLE impact.observation_p15 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 15);

CREATE TABLE impact.observation_p16 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 16);

CREATE TABLE impact.observation_p17 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 17);

CREATE TABLE impact.observation_p18 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 18);

CREATE TABLE impact.observation_p19 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 19);

CREATE TABLE impact.observation_p20 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 20);

CREATE TABLE impact.observation_p21 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 21);

CREATE TABLE impact.observation_p22 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 22);

CREATE TABLE impact.observation_p23 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 23);

CREATE TABLE impact.observation_p24 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 24);

CREATE TABLE impact.observation_p25 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 25);

CREATE TABLE impact.observation_p26 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 26);

CREATE TABLE impact.observation_p27 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 27);

CREATE TABLE impact.observation_p28 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 28);

CREATE TABLE impact.observation_p29 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 29);

CREATE TABLE impact.observation_p30 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 30);

CREATE TABLE impact.observation_p31 PARTITION OF impact.observation_current FOR VALUES WITH(MODULUS 32,REMAINDER 31);

CREATE TABLE impact.calculated_result_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('CalculatedResult') STORED,
indicator_version uuid,
indicator_version_kind text GENERATED ALWAYS AS ('IndicatorDefinition') STORED,
period_id uuid,
period_id_kind text GENERATED ALWAYS AS ('Period') STORED,
dimensions jsonb,
rule_version uuid,
rule_version_kind text GENERATED ALWAYS AS ('CalculationRule') STORED,
input_snapshot_id uuid,
input_snapshot_id_kind text GENERATED ALWAYS AS ('Snapshot') STORED,
run_id uuid,
value_state varchar(32),
value numeric(38,12),
numerator numeric(38,12),
denominator numeric(38,12),
unit varchar(64),
displayed_value text,
display_decimals integer,
rounding_rule varchar(64),
mode varchar(64),
coverage jsonb,
freshness jsonb,
limitations jsonb,
reason_code varchar(64),
lineage_manifest_id uuid,
lineage_manifest_id_kind text GENERATED ALWAYS AS ('LineageManifest') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(dimensions IS NULL OR jsonb_typeof(dimensions)='object'),
CHECK(display_decimals IS NULL OR display_decimals>=0),
CHECK(coverage IS NULL OR jsonb_typeof(coverage)='object'),
CHECK(freshness IS NULL OR jsonb_typeof(freshness)='object'),
CHECK(limitations IS NULL OR jsonb_typeof(limitations)='array'),
CHECK(value_state IS NULL OR value_state IN ('PRESENT','MISSING','NOT_COLLECTED','NOT_APPLICABLE','INVALID','UNDEFINED')),
CHECK((value_state='PRESENT' AND value IS NOT NULL) OR ((value_state IS NULL OR value_state<>'PRESENT') AND value IS NULL)),
CHECK(display_decimals IS NULL OR display_decimals BETWEEN 0 AND 6)
);

CREATE TABLE impact.form_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Form') STORED,
code varchar(64),
title varchar(200),
fields jsonb,
logic jsonb,
translation_versions jsonb,
compatibility_policy varchar(64),
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(fields IS NULL OR jsonb_typeof(fields)='array'),
CHECK(logic IS NULL OR jsonb_typeof(logic)='array'),
CHECK(translation_versions IS NULL OR jsonb_typeof(translation_versions)='array')
);

CREATE TABLE impact.form_field_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('FormField') STORED,
form_id uuid,
form_id_kind text GENERATED ALWAYS AS ('Form') STORED,
stable_code varchar(64),
field_type varchar(64),
label varchar(200),
required_expression text,
relevance_expression text,
validation_expression text,
calculation_expression text,
choices jsonb,
parent_field_id uuid,
parent_field_id_kind text GENERATED ALWAYS AS ('FormField') STORED,
hidden_value_policy varchar(64),
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(choices IS NULL OR jsonb_typeof(choices)='array')
);

CREATE TABLE impact.assignment_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Assignment') STORED,
round_id uuid,
round_id_kind text GENERATED ALWAYS AS ('CollectionRound') STORED,
form_version uuid,
form_version_kind text GENERATED ALWAYS AS ('Form') STORED,
assignee_id uuid,
scope_id uuid,
due_at timestamptz,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.submission_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Submission') STORED,
submission_id uuid,
form_version uuid,
form_version_kind text GENERATED ALWAYS AS ('Form') STORED,
assignment_id uuid,
assignment_id_kind text GENERATED ALWAYS AS ('Assignment') STORED,
respondent_scope_id uuid,
event_at timestamptz,
captured_at timestamptz,
capture_zone text,
answers jsonb,
attachments jsonb,
offline_grant_id uuid,
server_received_at timestamptz,
authenticated_uploader_id uuid,
original_author_id uuid,
review_state text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(answers IS NULL OR jsonb_typeof(answers)='object'),
CHECK(attachments IS NULL OR jsonb_typeof(attachments)='array')
);

CREATE TABLE impact.participant_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Participant') STORED,
programme_id uuid,
programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
pseudonym varchar(64),
entity_type varchar(64),
purpose varchar(64),
direct_identifiers jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(direct_identifiers IS NULL OR jsonb_typeof(direct_identifiers)='object'),
CHECK(direct_identifiers IS NULL)
);

CREATE TABLE impact.service_event_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('ServiceEvent') STORED,
subject_id uuid,
subject_id_kind text GENERATED ALWAYS AS ('Participant') STORED,
related_subject_id uuid,
related_subject_id_kind text GENERATED ALWAYS AS ('Participant') STORED,
event_code varchar(64),
event_at timestamptz,
ends_at timestamptz,
source_namespace varchar(64),
source_key text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.handling_record_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('HandlingRecord') STORED,
subject_id uuid,
subject_id_kind text GENERATED ALWAYS AS ('Participant') STORED,
notice_version uuid,
notice_version_kind text GENERATED ALWAYS AS ('Notice') STORED,
purpose varchar(64),
handling_basis varchar(64),
language varchar(64),
scope_id uuid,
effective_at timestamptz,
recorder_id uuid,
recorded_at timestamptz,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.dataset_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Dataset') STORED,
name varchar(200),
purpose varchar(64),
source jsonb,
schema_version varchar(64),
refresh_contract jsonb,
transformation_id uuid,
transformation_id_kind text GENERATED ALWAYS AS ('Transformation') STORED,
parent_versions jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(source IS NULL OR jsonb_typeof(source)='object'),
CHECK(refresh_contract IS NULL OR jsonb_typeof(refresh_contract)='object'),
CHECK(parent_versions IS NULL OR jsonb_typeof(parent_versions)='array')
);

CREATE TABLE impact.import_job_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('ImportJob') STORED,
upload_id uuid,
source_namespace varchar(64),
mapping_version uuid,
mapping_version_kind text GENERATED ALWAYS AS ('ImportMapping') STORED,
mode varchar(64),
source_key_policy jsonb,
locale varchar(64),
date_pattern varchar(64),
expected_totals jsonb,
atomic boolean,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(source_key_policy IS NULL OR jsonb_typeof(source_key_policy)='object'),
CHECK(expected_totals IS NULL OR jsonb_typeof(expected_totals)='object')
);

CREATE TABLE impact.quality_issue_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('QualityIssue') STORED,
rule_version uuid,
rule_version_kind text GENERATED ALWAYS AS ('QualityRule') STORED,
affected_object_id uuid,
affected_revision_id uuid,
severity varchar(64),
description text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.evidence_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Evidence') STORED,
upload_id uuid,
external_reference text,
source text,
evidence_date timestamptz,
evidence_type varchar(64),
publication_handling_id uuid,
publication_handling_id_kind text GENERATED ALWAYS AS ('HandlingRecord') STORED,
scan_state text,
verification_state text,
integrity_sha256 text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.workflow_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Workflow') STORED,
candidate_id uuid,
candidate_revision uuid,
workflow_version uuid,
workflow_version_kind text GENERATED ALWAYS AS ('WorkflowTemplate') STORED,
stages jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(stages IS NULL OR jsonb_typeof(stages)='array')
);

CREATE TABLE impact.decision_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Decision') STORED,
candidate_revision uuid,
workflow_version uuid,
workflow_version_kind text GENERATED ALWAYS AS ('WorkflowTemplate') STORED,
action varchar(64),
reason text,
evidence_revisions jsonb,
actor_id uuid,
decided_at timestamptz,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(evidence_revisions IS NULL OR jsonb_typeof(evidence_revisions)='array')
);

CREATE TABLE impact.snapshot_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Snapshot') STORED,
scope_id uuid,
period_id uuid,
period_id_kind text GENERATED ALWAYS AS ('Period') STORED,
definition_versions jsonb,
target_versions jsonb,
result_versions jsonb,
evidence_versions jsonb,
policy_context jsonb,
locked_at timestamptz,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(definition_versions IS NULL OR jsonb_typeof(definition_versions)='array'),
CHECK(target_versions IS NULL OR jsonb_typeof(target_versions)='array'),
CHECK(result_versions IS NULL OR jsonb_typeof(result_versions)='array'),
CHECK(evidence_versions IS NULL OR jsonb_typeof(evidence_versions)='array'),
CHECK(policy_context IS NULL OR jsonb_typeof(policy_context)='object')
);

CREATE TABLE impact.report_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Report') STORED,
template_version uuid,
template_version_kind text GENERATED ALWAYS AS ('ReportTemplate') STORED,
snapshot_id uuid,
snapshot_id_kind text GENERATED ALWAYS AS ('Snapshot') STORED,
language varchar(64),
audience_class varchar(64),
sections jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(sections IS NULL OR jsonb_typeof(sections)='array')
);

CREATE TABLE impact.disclosure_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Disclosure') STORED,
artifact_version uuid,
recipients jsonb,
purpose varchar(64),
policy_review_id uuid,
policy_review_id_kind text GENERATED ALWAYS AS ('DisclosureReview') STORED,
expires_at timestamptz,
public boolean,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(recipients IS NULL OR jsonb_typeof(recipients)='array')
);

CREATE TABLE impact.budget_line_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('BudgetLine') STORED,
agreement_id uuid,
agreement_id_kind text GENERATED ALWAYS AS ('FundingAgreement') STORED,
programme_id uuid,
programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
category varchar(64),
period_id uuid,
period_id_kind text GENERATED ALWAYS AS ('Period') STORED,
amount numeric(38,12),
currency varchar(64),
rate_version uuid,
rate_version_kind text GENERATED ALWAYS AS ('ExchangeRate') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.connection_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Connection') STORED,
connection_type varchar(64),
scope_id uuid,
credential_reference uuid,
credential_reference_kind text GENERATED ALWAYS AS ('CredentialReference') STORED,
mapping_version uuid,
mapping_version_kind text GENERATED ALWAYS AS ('ImportMapping') STORED,
schedule_id uuid,
schedule_id_kind text GENERATED ALWAYS AS ('Schedule') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.a_i_task_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('AITask') STORED,
use_case varchar(64),
source_revisions jsonb,
configuration_version uuid,
configuration_version_kind text GENERATED ALWAYS AS ('AIConfiguration') STORED,
prompt text,
budget_context uuid,
budget_context_kind text GENERATED ALWAYS AS ('AIBudget') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(source_revisions IS NULL OR jsonb_typeof(source_revisions)='array')
);

CREATE TABLE impact.privacy_case_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('PrivacyCase') STORED,
requester_reference uuid,
requester_reference_kind text GENERATED ALWAYS AS ('VerifiedRequester') STORED,
request_type varchar(64),
scope_id uuid,
handling_authority varchar(64),
deadline timestamptz,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.audit_event_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('AuditEvent') STORED,
real_actor_id uuid,
effective_actor_id uuid,
action_type varchar(64),
object_reference uuid,
outcome varchar(64),
occurred_at timestamptz,
correlation_id uuid,
specification_ref varchar(64),
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.evaluation_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Evaluation') STORED,
questions jsonb,
programme_baseline uuid,
programme_baseline_kind text GENERATED ALWAYS AS ('Programme') STORED,
methods text,
study_starts_at timestamptz,
study_ends_at timestamptz,
evaluator_id uuid,
evidence_versions jsonb,
limitations text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(questions IS NULL OR jsonb_typeof(questions)='array'),
CHECK(evidence_versions IS NULL OR jsonb_typeof(evidence_versions)='array'),
CHECK(study_starts_at IS NULL OR study_ends_at IS NULL OR study_ends_at>=study_starts_at)
);

CREATE TABLE impact.retention_policy_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('RetentionPolicy') STORED,
data_class varchar(64),
purpose varchar(64),
trigger varchar(64),
duration_days integer,
expiry_action varchar(64),
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(duration_days IS NULL OR duration_days>=0)
);

CREATE TABLE impact.subscription_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Subscription') STORED,
plan_reference varchar(64),
effective_at timestamptz,
ends_at timestamptz,
authorised_limits jsonb,
billing_contact_id uuid,
billing_contact_id_kind text GENERATED ALWAYS AS ('VerifiedContact') STORED,
commercial_status text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(authorised_limits IS NULL OR jsonb_typeof(authorised_limits)='object')
);

CREATE TABLE impact.funding_agreement_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('FundingAgreement') STORED,
code varchar(64),
donor_reference text,
starts_at timestamptz,
ends_at timestamptz,
currency varchar(64),
ceiling numeric(38,12),
restrictions jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(restrictions IS NULL OR jsonb_typeof(restrictions)='object'),
CHECK(ceiling IS NULL OR ceiling>=0),
CHECK(starts_at IS NULL OR ends_at IS NULL OR ends_at>=starts_at)
);

CREATE TABLE impact.finance_transaction_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('FinanceTransaction') STORED,
source_namespace varchar(64),
source_key text,
programme_id uuid,
programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
amount numeric(38,12),
currency varchar(64),
posting_at timestamptz,
event_at timestamptz,
category varchar(64),
reversal_of uuid,
reversal_of_kind text GENERATED ALWAYS AS ('FinanceTransaction') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.exchange_rate_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('ExchangeRate') STORED,
source_currency varchar(64),
reporting_currency varchar(64),
rate numeric(38,12),
effective_at timestamptz,
source text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(rate IS NULL OR rate>0),
CHECK(source_currency IS NULL OR reporting_currency IS NULL OR source_currency<>reporting_currency)
);

CREATE TABLE impact.allocation_rule_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('AllocationRule') STORED,
basis varchar(64),
weights jsonb,
residual_order jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(weights IS NULL OR jsonb_typeof(weights)='array'),
CHECK(residual_order IS NULL OR jsonb_typeof(residual_order)='array')
);

CREATE TABLE impact.work_item_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('WorkItem') STORED,
programme_id uuid,
programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
work_type varchar(64),
title varchar(200),
parent_id uuid,
parent_id_kind text GENERATED ALWAYS AS ('WorkItem') STORED,
dependency_ids jsonb,
due_at timestamptz,
assignee_id uuid,
severity varchar(64),
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(dependency_ids IS NULL OR jsonb_typeof(dependency_ids)='array')
);

CREATE TABLE impact.dashboard_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Dashboard') STORED,
title varchar(200),
mode varchar(64),
widgets jsonb,
filters jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(widgets IS NULL OR jsonb_typeof(widgets)='array'),
CHECK(filters IS NULL OR jsonb_typeof(filters)='object')
);

CREATE TABLE impact.report_template_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('ReportTemplate') STORED,
title varchar(200),
language varchar(64),
sections jsonb,
numeric_bindings jsonb,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(sections IS NULL OR jsonb_typeof(sections)='array'),
CHECK(numeric_bindings IS NULL OR jsonb_typeof(numeric_bindings)='array')
);

CREATE TABLE impact.notification_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Notification') STORED,
event_id uuid,
recipient_id uuid,
channel varchar(64),
notice_class varchar(64),
safe_reference uuid,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.schedule_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Schedule') STORED,
command_type varchar(64),
service_identity_id uuid,
scope_id uuid,
timezone text,
expression text,
missed_run_policy varchar(64),
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.qualitative_extract_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('QualitativeExtract') STORED,
evidence_version uuid,
evidence_version_kind text GENERATED ALWAYS AS ('Evidence') STORED,
source_span jsonb,
codebook_version uuid,
codebook_version_kind text GENERATED ALWAYS AS ('Codebook') STORED,
assigned_codes jsonb,
interpretation text,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(source_span IS NULL OR jsonb_typeof(source_span)='object'),
CHECK(assigned_codes IS NULL OR jsonb_typeof(assigned_codes)='array')
);

CREATE TABLE impact.device_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('Device') STORED,
public_key text,
security_profile varchar(64),
attestation_reference uuid,
attestation_reference_kind text GENERATED ALWAYS AS ('Attestation') STORED,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.support_request_current(
tenant_id uuid NOT NULL,
object_id uuid NOT NULL,
revision_id uuid NOT NULL,
object_type text GENERATED ALWAYS AS ('SupportRequest') STORED,
scope_id uuid,
reason text,
requested_capabilities jsonb,
requested_expires_at timestamptz,
PRIMARY KEY(tenant_id,object_id),
FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
CHECK(requested_capabilities IS NULL OR jsonb_typeof(requested_capabilities)='array')
);

CREATE TABLE impact.scope_definition(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
scope_id uuid NOT NULL,scope_type text NOT NULL CHECK(scope_type IN ('TENANT','PROGRAMME','ASSIGNMENT','OBJECT_SET')),predicate_version uuid NOT NULL,PRIMARY KEY(tenant_id,scope_id),FOREIGN KEY(tenant_id,predicate_version) REFERENCES impact.object_revision(tenant_id,revision_id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE impact.scope_member(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
scope_id uuid NOT NULL,object_id uuid NOT NULL,PRIMARY KEY(tenant_id,scope_id,object_id),FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition,FOREIGN KEY(tenant_id,object_id) REFERENCES impact.object_registry
);

CREATE TABLE impact.operation_receipt(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
actor_id uuid NOT NULL,command_type varchar(64) NOT NULL,operation_id uuid NOT NULL,payload_hash bytea NOT NULL CHECK(octet_length(payload_hash)=32),state text NOT NULL CHECK(state IN ('IN_PROGRESS','SUCCEEDED','FAILED')),outcome jsonb,expires_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,actor_id,command_type,operation_id),FOREIGN KEY(tenant_id,actor_id) REFERENCES impact.tenant_principal
);

CREATE TABLE impact.source_key_registry(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
namespace varchar(64) NOT NULL,source_key text NOT NULL,object_id uuid NOT NULL,PRIMARY KEY(tenant_id,namespace,source_key),FOREIGN KEY(tenant_id,object_id) REFERENCES impact.object_registry
);

CREATE TABLE impact.source_revision_receipt(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
namespace varchar(64) NOT NULL,source_key text NOT NULL,source_revision text NOT NULL,content_hash bytea NOT NULL CHECK(octet_length(content_hash)=32),destination_revision uuid NOT NULL,PRIMARY KEY(tenant_id,namespace,source_key,source_revision),FOREIGN KEY(tenant_id,namespace,source_key) REFERENCES impact.source_key_registry,FOREIGN KEY(tenant_id,destination_revision) REFERENCES impact.object_revision(tenant_id,revision_id)
);

CREATE TABLE impact.workflow_author(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
workflow_id uuid NOT NULL,natural_identity_id uuid NOT NULL,candidate_revision uuid NOT NULL,PRIMARY KEY(tenant_id,workflow_id,natural_identity_id,candidate_revision),FOREIGN KEY(tenant_id,workflow_id) REFERENCES impact.workflow_current(tenant_id,object_id),FOREIGN KEY(tenant_id,candidate_revision) REFERENCES impact.object_revision(tenant_id,revision_id)
);

CREATE TABLE impact.review_decision(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
decision_id uuid NOT NULL,workflow_id uuid NOT NULL,stage_id uuid NOT NULL,natural_identity_id uuid NOT NULL,candidate_revision uuid NOT NULL,decision text NOT NULL CHECK(decision IN ('APPROVE','RETURN','REJECT')),decided_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,decision_id),UNIQUE(tenant_id,workflow_id,stage_id,natural_identity_id,candidate_revision),FOREIGN KEY(tenant_id,workflow_id) REFERENCES impact.workflow_current(tenant_id,object_id),FOREIGN KEY(tenant_id,candidate_revision) REFERENCES impact.object_revision(tenant_id,revision_id)
);

CREATE TABLE impact.lineage_edge(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
result_revision uuid NOT NULL,source_revision uuid NOT NULL,contribution_identity text NOT NULL,disposition text NOT NULL CHECK(disposition IN ('INCLUDED','EXCLUDED')),reason_code text,PRIMARY KEY(tenant_id,result_revision,source_revision,contribution_identity),FOREIGN KEY(tenant_id,result_revision) REFERENCES impact.object_revision(tenant_id,revision_id),FOREIGN KEY(tenant_id,source_revision) REFERENCES impact.object_revision(tenant_id,revision_id)
);

CREATE TABLE impact.snapshot_member(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
snapshot_id uuid NOT NULL,member_revision uuid NOT NULL,member_type text NOT NULL,PRIMARY KEY(tenant_id,snapshot_id,member_revision),FOREIGN KEY(tenant_id,snapshot_id) REFERENCES impact.snapshot_current(tenant_id,object_id),FOREIGN KEY(tenant_id,member_revision,member_type) REFERENCES impact.object_revision(tenant_id,revision_id,object_type)
);

CREATE TABLE impact.file_blob(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
blob_id uuid NOT NULL,object_key text NOT NULL,sha256 bytea NOT NULL CHECK(octet_length(sha256)=32),bytes bigint NOT NULL CHECK(bytes>0),scan_state text NOT NULL CHECK(scan_state IN ('QUARANTINED','SCANNING','CLEAN','INFECTED','FAILED')),classification text NOT NULL,PRIMARY KEY(tenant_id,blob_id),UNIQUE(tenant_id,object_key)
);

CREATE TABLE impact.offline_grant(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
grant_id uuid NOT NULL,subject_id uuid NOT NULL,device_id uuid NOT NULL,scope_id uuid NOT NULL,issued_at timestamptz NOT NULL,expires_at timestamptz NOT NULL,policy_epoch bigint NOT NULL,signed_manifest jsonb NOT NULL,PRIMARY KEY(tenant_id,grant_id),CHECK(expires_at>issued_at AND expires_at<=issued_at+interval '24 hours'),FOREIGN KEY(tenant_id,subject_id) REFERENCES impact.tenant_principal,FOREIGN KEY(tenant_id,device_id) REFERENCES impact.device_current(tenant_id,object_id),FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition
);

CREATE TABLE impact.sync_receipt(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
device_id uuid NOT NULL,submission_id uuid NOT NULL,object_id uuid NOT NULL,content_hash bytea NOT NULL CHECK(octet_length(content_hash)=32),receipt jsonb NOT NULL,PRIMARY KEY(tenant_id,device_id,submission_id),FOREIGN KEY(tenant_id,device_id) REFERENCES impact.device_current(tenant_id,object_id),FOREIGN KEY(tenant_id,object_id) REFERENCES impact.submission_current(tenant_id,object_id)
);

CREATE TABLE impact.service_identity(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
service_identity_id uuid NOT NULL,principal_id uuid NOT NULL,owner_id uuid NOT NULL,backup_owner_id uuid NOT NULL,credential_reference uuid NOT NULL,expires_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,service_identity_id),CHECK(owner_id<>backup_owner_id),FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal,FOREIGN KEY(tenant_id,owner_id) REFERENCES impact.tenant_principal,FOREIGN KEY(tenant_id,backup_owner_id) REFERENCES impact.tenant_principal,FOREIGN KEY(tenant_id,credential_reference) REFERENCES impact.object_registry(tenant_id,object_id)
);

CREATE TABLE impact.job(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
job_id uuid NOT NULL,job_class text NOT NULL,requester_id uuid NOT NULL,service_identity_id uuid,scope_id uuid NOT NULL,state text NOT NULL CHECK(state IN ('Requested','Validating','Queued','Running','Cancelling','Succeeded','SucceededWithIssues','Failed','Cancelled')),lease_generation bigint NOT NULL DEFAULT 0,lease_expires_at timestamptz,cancellation_requested_at timestamptz,input_manifest jsonb NOT NULL,output_manifest jsonb,PRIMARY KEY(tenant_id,job_id),FOREIGN KEY(tenant_id,requester_id) REFERENCES impact.tenant_principal,FOREIGN KEY(tenant_id,service_identity_id) REFERENCES impact.service_identity,FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition
);

CREATE TABLE impact.job_item(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
job_id uuid NOT NULL,item_key text NOT NULL,outcome text NOT NULL,destination_revision uuid,error_code text,PRIMARY KEY(tenant_id,job_id,item_key),FOREIGN KEY(tenant_id,job_id) REFERENCES impact.job,FOREIGN KEY(tenant_id,destination_revision) REFERENCES impact.object_revision(tenant_id,revision_id)
);

CREATE TABLE impact.outbox_event(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
event_id uuid NOT NULL,event_type text NOT NULL,occurred_at timestamptz NOT NULL,payload jsonb NOT NULL,PRIMARY KEY(tenant_id,event_id)
);

CREATE TABLE impact.outbox_delivery(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
event_id uuid NOT NULL,sent_at timestamptz,attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),PRIMARY KEY(tenant_id,event_id),FOREIGN KEY(tenant_id,event_id) REFERENCES impact.outbox_event
);

CREATE TABLE impact.consumer_receipt(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
consumer text NOT NULL,event_id uuid NOT NULL,applied_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,consumer,event_id),FOREIGN KEY(tenant_id,event_id) REFERENCES impact.outbox_event
);

CREATE TABLE impact.deletion_ledger(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
entry_id uuid NOT NULL,case_id uuid NOT NULL,object_id uuid NOT NULL,effective_at timestamptz NOT NULL,disposition text NOT NULL,PRIMARY KEY(tenant_id,entry_id),FOREIGN KEY(tenant_id,case_id) REFERENCES impact.privacy_case_current(tenant_id,object_id),FOREIGN KEY(tenant_id,object_id) REFERENCES impact.object_registry
);

CREATE TABLE impact.retention_hold(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
hold_id uuid NOT NULL,object_id uuid NOT NULL,authority_reference text NOT NULL,review_at timestamptz NOT NULL,released_at timestamptz,PRIMARY KEY(tenant_id,hold_id),FOREIGN KEY(tenant_id,object_id) REFERENCES impact.object_registry
);

CREATE TABLE impact.privacy_store_action(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
case_id uuid NOT NULL,object_id uuid NOT NULL,store text NOT NULL,action text NOT NULL,state text NOT NULL CHECK(state IN ('APPROVED','EXECUTING','COMPLETED','FAILED','HELD')),plan_hash bytea NOT NULL CHECK(octet_length(plan_hash)=32),PRIMARY KEY(tenant_id,case_id,object_id,store),FOREIGN KEY(tenant_id,case_id) REFERENCES impact.privacy_case_current(tenant_id,object_id),FOREIGN KEY(tenant_id,object_id) REFERENCES impact.object_registry
);

CREATE TABLE impact.participant_private(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
object_id uuid NOT NULL,ciphertext bytea NOT NULL,key_reference uuid NOT NULL,PRIMARY KEY(tenant_id,object_id),FOREIGN KEY(tenant_id,object_id) REFERENCES impact.participant_current(tenant_id,object_id),FOREIGN KEY(tenant_id,key_reference) REFERENCES impact.object_registry(tenant_id,object_id)
);

CREATE TABLE impact.webhook_delivery(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
event_id uuid NOT NULL,destination_id uuid NOT NULL,delivery_id uuid NOT NULL,attempt integer NOT NULL CHECK(attempt>0),outcome text NOT NULL,PRIMARY KEY(tenant_id,delivery_id),UNIQUE(tenant_id,event_id,destination_id,attempt),FOREIGN KEY(tenant_id,event_id) REFERENCES impact.outbox_event,FOREIGN KEY(tenant_id,destination_id) REFERENCES impact.connection_current(tenant_id,object_id)
);

CREATE TABLE impact.audit_batch_root(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
batch_id uuid NOT NULL,starts_at timestamptz NOT NULL,ends_at timestamptz NOT NULL,root_digest bytea NOT NULL CHECK(octet_length(root_digest)=32),previous_digest bytea,external_checkpoint text NOT NULL,PRIMARY KEY(tenant_id,batch_id),CHECK(ends_at>=starts_at)
);

CREATE TABLE impact.application_session(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
session_id uuid NOT NULL,subject_id uuid NOT NULL,token_hash bytea NOT NULL CHECK(octet_length(token_hash)=32),issued_at timestamptz NOT NULL,last_active_at timestamptz NOT NULL,absolute_expires_at timestamptz NOT NULL,assurance_at timestamptz,revoked_at timestamptz,PRIMARY KEY(tenant_id,session_id),FOREIGN KEY(tenant_id,subject_id) REFERENCES impact.tenant_principal,CHECK(absolute_expires_at>issued_at)
);

CREATE TABLE impact.member_invitation(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
invitation_id uuid NOT NULL,token_hash bytea NOT NULL UNIQUE,intended_issuer text,intended_subject text,intended_email_hash bytea NOT NULL,inviter_id uuid NOT NULL,role_template_id uuid NOT NULL,scope_ids uuid[] NOT NULL,expires_at timestamptz NOT NULL,consumed_at timestamptz,revoked_at timestamptz,PRIMARY KEY(tenant_id,invitation_id),FOREIGN KEY(tenant_id,inviter_id) REFERENCES impact.tenant_principal,FOREIGN KEY(tenant_id,role_template_id) REFERENCES impact.object_registry(tenant_id,object_id)
);

CREATE TABLE impact.upload_session(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
upload_id uuid NOT NULL,revision_id uuid NOT NULL,owner_id uuid NOT NULL,purpose text NOT NULL CHECK(purpose IN ('SOURCE_IMPORT','EVIDENCE_MEDIA')),mode text NOT NULL CHECK(mode IN ('WHOLE','MULTIPART')),expected_bytes bigint NOT NULL CHECK(expected_bytes BETWEEN 1 AND 100000000),expected_digest bytea NOT NULL CHECK(octet_length(expected_digest)=32),state text NOT NULL CHECK(state IN ('OPEN','ASSEMBLING','QUARANTINED','SCANNING','CLEAN','REJECTED','CANCELLED','EXPIRED')),expires_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,upload_id),FOREIGN KEY(tenant_id,owner_id) REFERENCES impact.tenant_principal,CHECK(purpose<>'EVIDENCE_MEDIA' OR expected_bytes<=25000000)
);

CREATE TABLE impact.upload_part(tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
upload_id uuid NOT NULL,part_number integer NOT NULL CHECK(part_number BETWEEN 1 AND 96),bytes integer NOT NULL CHECK(bytes BETWEEN 1 AND 1048576),sha256 bytea NOT NULL CHECK(octet_length(sha256)=32),object_key text NOT NULL,received_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,upload_id,part_number),FOREIGN KEY(tenant_id,upload_id) REFERENCES impact.upload_session
);

ALTER TABLE impact.tenant_current ADD CONSTRAINT fk_001 FOREIGN KEY(tenant_id,owner_membership_id,owner_membership_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.tenant_current ADD CONSTRAINT fk_002 FOREIGN KEY(tenant_id,hosting_policy_id,hosting_policy_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.tenant_current ADD CONSTRAINT fk_003 FOREIGN KEY(tenant_id,privacy_policy_id,privacy_policy_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.tenant_current ADD CONSTRAINT fk_004 FOREIGN KEY(tenant_id,retention_policy_id,retention_policy_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.membership_current ADD CONSTRAINT fk_005 FOREIGN KEY(identity_id) REFERENCES impact.auth_identity(identity_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.grant_current ADD CONSTRAINT fk_006 FOREIGN KEY(tenant_id,subject_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.grant_current ADD CONSTRAINT fk_007 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.grant_current ADD CONSTRAINT fk_008 FOREIGN KEY(tenant_id,issuer_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.organisation_unit_current ADD CONSTRAINT fk_009 FOREIGN KEY(tenant_id,parent_id,parent_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.programme_current ADD CONSTRAINT fk_010 FOREIGN KEY(tenant_id,reporting_calendar_id,reporting_calendar_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.programme_current ADD CONSTRAINT fk_011 FOREIGN KEY(tenant_id,geography_id,geography_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.framework_current ADD CONSTRAINT fk_012 FOREIGN KEY(tenant_id,programme_id,programme_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.indicator_instance_current ADD CONSTRAINT fk_013 FOREIGN KEY(tenant_id,definition_version,definition_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.indicator_instance_current ADD CONSTRAINT fk_014 FOREIGN KEY(tenant_id,programme_id,programme_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.indicator_instance_current ADD CONSTRAINT fk_015 FOREIGN KEY(tenant_id,collector_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.indicator_instance_current ADD CONSTRAINT fk_016 FOREIGN KEY(tenant_id,reviewer_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.indicator_instance_current ADD CONSTRAINT fk_017 FOREIGN KEY(tenant_id,schedule_id,schedule_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.target_current ADD CONSTRAINT fk_018 FOREIGN KEY(tenant_id,indicator_version,indicator_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.target_current ADD CONSTRAINT fk_019 FOREIGN KEY(tenant_id,period_id,period_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.period_current ADD CONSTRAINT fk_020 FOREIGN KEY(tenant_id,calendar_version,calendar_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.observation_current ADD CONSTRAINT fk_021 FOREIGN KEY(tenant_id,indicator_id,indicator_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.observation_current ADD CONSTRAINT fk_022 FOREIGN KEY(tenant_id,dataset_id,dataset_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.calculated_result_current ADD CONSTRAINT fk_023 FOREIGN KEY(tenant_id,indicator_version,indicator_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.calculated_result_current ADD CONSTRAINT fk_024 FOREIGN KEY(tenant_id,period_id,period_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.calculated_result_current ADD CONSTRAINT fk_025 FOREIGN KEY(tenant_id,rule_version,rule_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.calculated_result_current ADD CONSTRAINT fk_026 FOREIGN KEY(tenant_id,input_snapshot_id,input_snapshot_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.calculated_result_current ADD CONSTRAINT fk_027 FOREIGN KEY(tenant_id,run_id) REFERENCES impact.job(tenant_id,job_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.calculated_result_current ADD CONSTRAINT fk_028 FOREIGN KEY(tenant_id,lineage_manifest_id,lineage_manifest_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.form_field_current ADD CONSTRAINT fk_029 FOREIGN KEY(tenant_id,form_id,form_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.form_field_current ADD CONSTRAINT fk_030 FOREIGN KEY(tenant_id,parent_field_id,parent_field_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.assignment_current ADD CONSTRAINT fk_031 FOREIGN KEY(tenant_id,round_id,round_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.assignment_current ADD CONSTRAINT fk_032 FOREIGN KEY(tenant_id,form_version,form_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.assignment_current ADD CONSTRAINT fk_033 FOREIGN KEY(tenant_id,assignee_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.assignment_current ADD CONSTRAINT fk_034 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.submission_current ADD CONSTRAINT fk_036 FOREIGN KEY(tenant_id,form_version,form_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.submission_current ADD CONSTRAINT fk_037 FOREIGN KEY(tenant_id,assignment_id,assignment_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.submission_current ADD CONSTRAINT fk_038 FOREIGN KEY(tenant_id,respondent_scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.submission_current ADD CONSTRAINT fk_039 FOREIGN KEY(tenant_id,offline_grant_id) REFERENCES impact.offline_grant(tenant_id,grant_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.submission_current ADD CONSTRAINT fk_040 FOREIGN KEY(tenant_id,authenticated_uploader_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.submission_current ADD CONSTRAINT fk_041 FOREIGN KEY(tenant_id,original_author_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.participant_current ADD CONSTRAINT fk_042 FOREIGN KEY(tenant_id,programme_id,programme_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.service_event_current ADD CONSTRAINT fk_043 FOREIGN KEY(tenant_id,subject_id,subject_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.service_event_current ADD CONSTRAINT fk_044 FOREIGN KEY(tenant_id,related_subject_id,related_subject_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.handling_record_current ADD CONSTRAINT fk_045 FOREIGN KEY(tenant_id,subject_id,subject_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.handling_record_current ADD CONSTRAINT fk_046 FOREIGN KEY(tenant_id,notice_version,notice_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.handling_record_current ADD CONSTRAINT fk_047 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.handling_record_current ADD CONSTRAINT fk_048 FOREIGN KEY(tenant_id,recorder_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.dataset_current ADD CONSTRAINT fk_049 FOREIGN KEY(tenant_id,transformation_id,transformation_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.import_job_current ADD CONSTRAINT fk_050 FOREIGN KEY(tenant_id,upload_id) REFERENCES impact.upload_session(tenant_id,upload_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.import_job_current ADD CONSTRAINT fk_051 FOREIGN KEY(tenant_id,mapping_version,mapping_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.quality_issue_current ADD CONSTRAINT fk_052 FOREIGN KEY(tenant_id,rule_version,rule_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.quality_issue_current ADD CONSTRAINT fk_053 FOREIGN KEY(tenant_id,affected_object_id) REFERENCES impact.object_registry(tenant_id,object_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.quality_issue_current ADD CONSTRAINT fk_054 FOREIGN KEY(tenant_id,affected_revision_id) REFERENCES impact.object_revision(tenant_id,revision_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.evidence_current ADD CONSTRAINT fk_055 FOREIGN KEY(tenant_id,upload_id) REFERENCES impact.upload_session(tenant_id,upload_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.evidence_current ADD CONSTRAINT fk_056 FOREIGN KEY(tenant_id,publication_handling_id,publication_handling_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.workflow_current ADD CONSTRAINT fk_057 FOREIGN KEY(tenant_id,candidate_id) REFERENCES impact.object_registry(tenant_id,object_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.workflow_current ADD CONSTRAINT fk_058 FOREIGN KEY(tenant_id,candidate_revision) REFERENCES impact.object_revision(tenant_id,revision_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.workflow_current ADD CONSTRAINT fk_059 FOREIGN KEY(tenant_id,workflow_version,workflow_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.decision_current ADD CONSTRAINT fk_060 FOREIGN KEY(tenant_id,candidate_revision) REFERENCES impact.object_revision(tenant_id,revision_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.decision_current ADD CONSTRAINT fk_061 FOREIGN KEY(tenant_id,workflow_version,workflow_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.decision_current ADD CONSTRAINT fk_062 FOREIGN KEY(tenant_id,actor_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.snapshot_current ADD CONSTRAINT fk_063 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.snapshot_current ADD CONSTRAINT fk_064 FOREIGN KEY(tenant_id,period_id,period_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.report_current ADD CONSTRAINT fk_065 FOREIGN KEY(tenant_id,template_version,template_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.report_current ADD CONSTRAINT fk_066 FOREIGN KEY(tenant_id,snapshot_id,snapshot_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.disclosure_current ADD CONSTRAINT fk_067 FOREIGN KEY(tenant_id,artifact_version) REFERENCES impact.object_revision(tenant_id,revision_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.disclosure_current ADD CONSTRAINT fk_068 FOREIGN KEY(tenant_id,policy_review_id,policy_review_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.budget_line_current ADD CONSTRAINT fk_069 FOREIGN KEY(tenant_id,agreement_id,agreement_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.budget_line_current ADD CONSTRAINT fk_070 FOREIGN KEY(tenant_id,programme_id,programme_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.budget_line_current ADD CONSTRAINT fk_071 FOREIGN KEY(tenant_id,period_id,period_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.budget_line_current ADD CONSTRAINT fk_072 FOREIGN KEY(tenant_id,rate_version,rate_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.connection_current ADD CONSTRAINT fk_073 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.connection_current ADD CONSTRAINT fk_074 FOREIGN KEY(tenant_id,credential_reference,credential_reference_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.connection_current ADD CONSTRAINT fk_075 FOREIGN KEY(tenant_id,mapping_version,mapping_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.connection_current ADD CONSTRAINT fk_076 FOREIGN KEY(tenant_id,schedule_id,schedule_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.a_i_task_current ADD CONSTRAINT fk_077 FOREIGN KEY(tenant_id,configuration_version,configuration_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.a_i_task_current ADD CONSTRAINT fk_078 FOREIGN KEY(tenant_id,budget_context,budget_context_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.privacy_case_current ADD CONSTRAINT fk_079 FOREIGN KEY(tenant_id,requester_reference,requester_reference_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.privacy_case_current ADD CONSTRAINT fk_080 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.audit_event_current ADD CONSTRAINT fk_081 FOREIGN KEY(tenant_id,real_actor_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.audit_event_current ADD CONSTRAINT fk_082 FOREIGN KEY(tenant_id,effective_actor_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.audit_event_current ADD CONSTRAINT fk_083 FOREIGN KEY(tenant_id,object_reference) REFERENCES impact.object_registry(tenant_id,object_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.evaluation_current ADD CONSTRAINT fk_085 FOREIGN KEY(tenant_id,programme_baseline,programme_baseline_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.evaluation_current ADD CONSTRAINT fk_086 FOREIGN KEY(tenant_id,evaluator_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.subscription_current ADD CONSTRAINT fk_087 FOREIGN KEY(tenant_id,billing_contact_id,billing_contact_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.finance_transaction_current ADD CONSTRAINT fk_088 FOREIGN KEY(tenant_id,programme_id,programme_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.finance_transaction_current ADD CONSTRAINT fk_089 FOREIGN KEY(tenant_id,reversal_of,reversal_of_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.work_item_current ADD CONSTRAINT fk_090 FOREIGN KEY(tenant_id,programme_id,programme_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.work_item_current ADD CONSTRAINT fk_091 FOREIGN KEY(tenant_id,parent_id,parent_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.work_item_current ADD CONSTRAINT fk_092 FOREIGN KEY(tenant_id,assignee_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.notification_current ADD CONSTRAINT fk_093 FOREIGN KEY(tenant_id,event_id) REFERENCES impact.outbox_event(tenant_id,event_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.notification_current ADD CONSTRAINT fk_094 FOREIGN KEY(tenant_id,recipient_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.notification_current ADD CONSTRAINT fk_095 FOREIGN KEY(tenant_id,safe_reference) REFERENCES impact.object_registry(tenant_id,object_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.schedule_current ADD CONSTRAINT fk_096 FOREIGN KEY(tenant_id,service_identity_id) REFERENCES impact.service_identity(tenant_id,service_identity_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.schedule_current ADD CONSTRAINT fk_097 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.qualitative_extract_current ADD CONSTRAINT fk_098 FOREIGN KEY(tenant_id,evidence_version,evidence_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.qualitative_extract_current ADD CONSTRAINT fk_099 FOREIGN KEY(tenant_id,codebook_version,codebook_version_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.device_current ADD CONSTRAINT fk_100 FOREIGN KEY(tenant_id,attestation_reference,attestation_reference_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.support_request_current ADD CONSTRAINT fk_101 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition(tenant_id,scope_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.workflow_current ADD FOREIGN KEY(tenant_id,candidate_id,candidate_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE impact.quality_issue_current ADD FOREIGN KEY(tenant_id,affected_object_id,affected_revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED;

CREATE UNIQUE INDEX submission_business_identity ON impact.submission_current(tenant_id,submission_id) WHERE submission_id IS NOT NULL;

CREATE UNIQUE INDEX financial_source_identity ON impact.finance_transaction_current(tenant_id,source_namespace,source_key) WHERE source_namespace IS NOT NULL AND source_key IS NOT NULL;

CREATE UNIQUE INDEX service_event_identity ON impact.service_event_current(tenant_id,source_namespace,source_key) WHERE source_namespace IS NOT NULL AND source_key IS NOT NULL;

CREATE INDEX observation_by_indicator_event ON impact.observation_current(tenant_id,indicator_id,event_at,object_id);

CREATE INDEX revision_by_object ON impact.object_revision(tenant_id,object_id,created_at DESC);

CREATE INDEX queued_jobs ON impact.job(tenant_id,job_class,state,job_id);

CREATE INDEX upload_expiry ON impact.upload_session(tenant_id,expires_at) WHERE state='OPEN';

CREATE INDEX active_holds ON impact.retention_hold(tenant_id,object_id) WHERE released_at IS NULL;

COMMIT;
```

### 0003 security

Source: infrastructure/migrations/0003_security.sql

```sql
BEGIN;

SET LOCAL ROLE impact_owner;

CREATE FUNCTION impact.current_tenant() RETURNS uuid LANGUAGE sql STABLE AS $$ SELECT nullif(current_setting('impact.tenant_id',true),'')::uuid $$;

REVOKE ALL ON FUNCTION impact.current_tenant() FROM PUBLIC;

GRANT EXECUTE ON FUNCTION impact.current_tenant() TO impact_app,impact_worker,impact_identity,impact_sensitive,impact_privacy,impact_observer;

ALTER TABLE impact.tenant_root ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.tenant_root FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.tenant_root USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.tenant_principal ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.tenant_principal FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.tenant_principal USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.object_registry ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.object_registry FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.object_registry USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.object_revision ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.object_revision FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.object_revision USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.tenant_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.tenant_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.tenant_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.membership_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.membership_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.membership_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.grant_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.grant_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.grant_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.organisation_unit_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.organisation_unit_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.organisation_unit_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.programme_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.programme_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.programme_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.framework_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.framework_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.framework_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.indicator_definition_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.indicator_definition_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.indicator_definition_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.indicator_instance_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.indicator_instance_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.indicator_instance_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.target_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.target_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.target_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.dimension_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.dimension_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.dimension_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.period_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.period_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.period_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p00 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p00 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p00 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p01 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p01 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p01 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p02 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p02 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p02 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p03 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p03 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p03 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p04 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p04 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p04 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p05 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p05 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p05 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p06 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p06 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p06 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p07 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p07 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p07 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p08 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p08 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p08 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p09 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p09 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p09 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p10 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p10 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p10 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p11 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p11 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p11 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p12 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p12 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p12 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p13 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p13 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p13 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p14 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p14 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p14 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p15 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p15 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p15 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p16 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p16 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p16 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p17 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p17 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p17 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p18 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p18 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p18 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p19 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p19 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p19 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p20 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p20 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p20 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p21 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p21 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p21 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p22 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p22 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p22 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p23 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p23 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p23 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p24 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p24 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p24 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p25 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p25 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p25 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p26 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p26 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p26 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p27 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p27 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p27 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p28 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p28 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p28 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p29 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p29 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p29 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p30 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p30 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p30 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p31 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p31 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p31 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.calculated_result_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.calculated_result_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.calculated_result_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.form_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.form_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.form_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.form_field_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.form_field_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.form_field_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.assignment_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.assignment_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.assignment_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.submission_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.submission_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.submission_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.participant_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.participant_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.participant_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.service_event_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.service_event_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.service_event_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.handling_record_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.handling_record_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.handling_record_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.dataset_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.dataset_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.dataset_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.import_job_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.import_job_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.import_job_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.quality_issue_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.quality_issue_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.quality_issue_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.evidence_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.evidence_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.evidence_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.workflow_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.workflow_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.workflow_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.decision_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.decision_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.decision_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.snapshot_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.snapshot_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.snapshot_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.report_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.report_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.report_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.disclosure_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.disclosure_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.disclosure_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.budget_line_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.budget_line_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.budget_line_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.connection_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.connection_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.connection_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.a_i_task_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.a_i_task_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.a_i_task_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.privacy_case_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.privacy_case_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.privacy_case_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.audit_event_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.audit_event_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.audit_event_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.evaluation_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.evaluation_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.evaluation_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.retention_policy_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.retention_policy_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.retention_policy_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.subscription_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.subscription_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.subscription_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.funding_agreement_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.funding_agreement_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.funding_agreement_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.finance_transaction_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.finance_transaction_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.finance_transaction_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.exchange_rate_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.exchange_rate_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.exchange_rate_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.allocation_rule_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.allocation_rule_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.allocation_rule_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.work_item_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.work_item_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.work_item_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.dashboard_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.dashboard_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.dashboard_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.report_template_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.report_template_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.report_template_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.notification_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.notification_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.notification_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.schedule_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.schedule_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.schedule_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.qualitative_extract_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.qualitative_extract_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.qualitative_extract_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.device_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.device_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.device_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.support_request_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.support_request_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.support_request_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.scope_definition ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.scope_definition FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.scope_definition USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.scope_member ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.scope_member FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.scope_member USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.operation_receipt ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.operation_receipt FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.operation_receipt USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.source_key_registry ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.source_key_registry FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.source_key_registry USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.source_revision_receipt ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.source_revision_receipt FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.source_revision_receipt USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.workflow_author ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.workflow_author FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.workflow_author USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.review_decision ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.review_decision FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.review_decision USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.lineage_edge ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.lineage_edge FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.lineage_edge USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.snapshot_member ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.snapshot_member FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.snapshot_member USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.file_blob ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.file_blob FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.file_blob USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.offline_grant ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.offline_grant FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.offline_grant USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.sync_receipt ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.sync_receipt FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.sync_receipt USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.service_identity ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.service_identity FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.service_identity USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.job ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.job FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.job USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.job_item ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.job_item FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.job_item USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.outbox_event ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.outbox_event FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.outbox_event USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.outbox_delivery ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.outbox_delivery FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.outbox_delivery USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.consumer_receipt ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.consumer_receipt FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.consumer_receipt USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.deletion_ledger ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.deletion_ledger FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.deletion_ledger USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.retention_hold ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.retention_hold FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.retention_hold USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.privacy_store_action ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.privacy_store_action FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.privacy_store_action USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.participant_private ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.participant_private FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.participant_private USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.webhook_delivery ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.webhook_delivery FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.webhook_delivery USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.audit_batch_root ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.audit_batch_root FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.audit_batch_root USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.application_session ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.application_session FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.application_session USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.member_invitation ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.member_invitation FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.member_invitation USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.upload_session ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.upload_session FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.upload_session USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.upload_part ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.upload_part FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.upload_part USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT,UPDATE ON impact.tenant_root TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.tenant_principal TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.object_registry TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.object_revision TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.tenant_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.membership_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.grant_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.organisation_unit_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.programme_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.framework_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.indicator_definition_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.indicator_instance_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.target_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.dimension_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.period_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.observation_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.calculated_result_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.form_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.form_field_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.assignment_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.submission_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.participant_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.service_event_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.handling_record_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.dataset_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.import_job_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.quality_issue_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.evidence_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.workflow_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.decision_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.snapshot_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.report_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.disclosure_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.budget_line_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.connection_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.a_i_task_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.privacy_case_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.audit_event_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.evaluation_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.retention_policy_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.subscription_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.funding_agreement_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.finance_transaction_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.exchange_rate_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.allocation_rule_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.work_item_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.dashboard_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.report_template_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.notification_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.schedule_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.qualitative_extract_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.device_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.support_request_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.scope_definition TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.scope_member TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.operation_receipt TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.source_key_registry TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.source_revision_receipt TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.workflow_author TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.review_decision TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.lineage_edge TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.snapshot_member TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.file_blob TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.offline_grant TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.sync_receipt TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.service_identity TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.job TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.job_item TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.outbox_event TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.outbox_delivery TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.consumer_receipt TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.deletion_ledger TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.retention_hold TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.privacy_store_action TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.webhook_delivery TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.audit_batch_root TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.upload_session TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.upload_part TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.auth_identity TO impact_identity;

GRANT SELECT,INSERT,UPDATE ON impact.application_session,impact.member_invitation TO impact_identity;

GRANT SELECT,INSERT,UPDATE ON impact.participant_private TO impact_sensitive;

GRANT SELECT ON impact.tenant_root TO impact_observer;

GRANT SELECT ON impact.object_revision,impact.object_registry,impact.privacy_case_current,impact.privacy_store_action,impact.retention_hold,impact.deletion_ledger TO impact_privacy;

GRANT UPDATE(payload,restriction_state) ON impact.object_revision TO impact_privacy;

GRANT INSERT ON impact.deletion_ledger TO impact_privacy;

GRANT UPDATE(state) ON impact.privacy_store_action TO impact_privacy;

GRANT SELECT,DELETE ON impact.participant_private TO impact_privacy;

ALTER DEFAULT PRIVILEGES FOR ROLE impact_owner IN SCHEMA impact REVOKE ALL ON TABLES FROM PUBLIC;

ALTER DEFAULT PRIVILEGES FOR ROLE impact_owner IN SCHEMA impact REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

CREATE FUNCTION impact.guard_revision_removal() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE case_ref uuid;
BEGIN
 IF NOT pg_has_role(current_user,'impact_privacy','USAGE') THEN RAISE EXCEPTION 'immutable revision'; END IF;
 case_ref := nullif(current_setting('impact.privacy_case_id',true),'')::uuid;
 IF case_ref IS NULL OR NEW.tenant_id<>impact.current_tenant() THEN RAISE EXCEPTION 'privacy context required'; END IF;
 IF (to_jsonb(OLD)-'payload'-'restriction_state') IS DISTINCT FROM (to_jsonb(NEW)-'payload'-'restriction_state') THEN RAISE EXCEPTION 'immutable metadata'; END IF;
 IF NEW.payload IS NOT NULL OR NEW.restriction_state<>'REMOVED' THEN RAISE EXCEPTION 'removal only'; END IF;
 IF EXISTS(SELECT 1 FROM impact.retention_hold WHERE tenant_id=OLD.tenant_id AND object_id=OLD.object_id AND released_at IS NULL) THEN RAISE EXCEPTION 'active hold'; END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=OLD.tenant_id AND case_id=case_ref AND object_id=OLD.object_id AND store='DATABASE' AND action='DELETE' AND state='EXECUTING') THEN RAISE EXCEPTION 'approved executing plan required'; END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.deletion_ledger WHERE tenant_id=OLD.tenant_id AND case_id=case_ref AND object_id=OLD.object_id) THEN RAISE EXCEPTION 'durable ledger prerequisite'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER revision_removal_guard BEFORE UPDATE ON impact.object_revision FOR EACH ROW EXECUTE FUNCTION impact.guard_revision_removal();


REVOKE ALL ON FUNCTION impact.guard_revision_removal() FROM PUBLIC;

COMMIT;
```

### 0004 application

Source: infrastructure/migrations/0004_application.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.web_session(session_hash bytea PRIMARY KEY CHECK(octet_length(session_hash)=32),identity_id uuid NOT NULL REFERENCES impact.auth_identity,created_at timestamptz NOT NULL,last_seen_at timestamptz NOT NULL,expires_at timestamptz NOT NULL,auth_time timestamptz NOT NULL,revoked_at timestamptz);
CREATE TABLE impact.login_attempt(attempt_hash bytea PRIMARY KEY CHECK(octet_length(attempt_hash)=32),window_start timestamptz NOT NULL,failures integer NOT NULL CHECK(failures>=0));
CREATE TABLE impact.oidc_login(state_hash bytea PRIMARY KEY CHECK(octet_length(state_hash)=32),browser_hash bytea NOT NULL,nonce text NOT NULL,verifier text NOT NULL,expires_at timestamptz NOT NULL,consumed_at timestamptz);
GRANT SELECT,INSERT,UPDATE,DELETE ON impact.web_session,impact.login_attempt,impact.oidc_login TO impact_identity;
CREATE FUNCTION impact.identity_tenants(requested_identity uuid) RETURNS TABLE(tenant_id uuid) LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$ SELECT DISTINCT p.tenant_id FROM impact.tenant_principal p WHERE p.identity_id=requested_identity AND p.active $$;
REVOKE ALL ON FUNCTION impact.identity_tenants(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.identity_tenants(uuid) TO impact_identity;
CREATE POLICY principal_identity_directory ON impact.tenant_principal FOR SELECT TO impact_owner USING(true);
CREATE TABLE impact.object_natural_author(tenant_id uuid NOT NULL,object_id uuid NOT NULL,natural_identity_id uuid NOT NULL,PRIMARY KEY(tenant_id,object_id,natural_identity_id),FOREIGN KEY(tenant_id,object_id) REFERENCES impact.object_registry);
CREATE TABLE impact.result_binding(tenant_id uuid NOT NULL,result_id uuid NOT NULL,indicator_id uuid NOT NULL,period_id uuid NOT NULL,source_digest char(64) NOT NULL,PRIMARY KEY(tenant_id,result_id),FOREIGN KEY(tenant_id,result_id) REFERENCES impact.calculated_result_current(tenant_id,object_id),FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id));
ALTER TABLE impact.object_natural_author ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.object_natural_author FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.object_natural_author USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.result_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.result_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.result_binding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.object_natural_author,impact.result_binding TO impact_app;
GRANT SELECT ON impact.schema_migration TO impact_app;
REVOKE UPDATE ON impact.operation_receipt FROM impact_app;
CREATE INDEX grant_by_subject_capability ON impact.grant_current(tenant_id,subject_id,capability,expires_at);
CREATE INDEX registry_type_page ON impact.object_registry(tenant_id,object_type,created_at,object_id);
CREATE INDEX membership_by_identity ON impact.membership_current(tenant_id,identity_id,status);
CREATE INDEX scope_object_lookup ON impact.scope_member(tenant_id,object_id,scope_id);
COMMIT;
```

### 0005 access administration

Source: infrastructure/migrations/0005_access_administration.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.tenant_principal ADD COLUMN auth_not_before timestamptz;
ALTER TABLE impact.web_session ADD COLUMN verified_email_hash bytea;
ALTER TABLE impact.web_session ADD COLUMN display_name varchar(120);
ALTER TABLE impact.web_session ADD COLUMN email_mask varchar(254);
ALTER TABLE impact.member_invitation ADD COLUMN generation uuid;
ALTER TABLE impact.member_invitation ADD COLUMN membership_expires_at timestamptz;
ALTER TABLE impact.member_invitation ADD COLUMN external boolean NOT NULL DEFAULT true;
ALTER TABLE impact.member_invitation ADD COLUMN role_revision uuid;
ALTER TABLE impact.member_invitation ADD COLUMN accepted_membership_id uuid;
ALTER TABLE impact.member_invitation ADD CONSTRAINT invitation_role_revision FOREIGN KEY(tenant_id,role_revision) REFERENCES impact.object_revision(tenant_id,revision_id);
ALTER TABLE impact.member_invitation ADD CONSTRAINT invitation_member FOREIGN KEY(tenant_id,accepted_membership_id) REFERENCES impact.membership_current(tenant_id,object_id);
CREATE UNIQUE INDEX one_pending_invitation ON impact.member_invitation(tenant_id,intended_email_hash) WHERE consumed_at IS NULL AND revoked_at IS NULL;
GRANT SELECT,INSERT,UPDATE ON impact.member_invitation TO impact_app;

CREATE TABLE impact.identity_profile(identity_id uuid PRIMARY KEY REFERENCES impact.auth_identity,display_name varchar(120) NOT NULL,verified_email_hash bytea CHECK(octet_length(verified_email_hash)=32),email_mask varchar(254),verified_at timestamptz);
GRANT SELECT,INSERT,UPDATE ON impact.identity_profile TO impact_identity;

CREATE TABLE impact.member_profile(tenant_id uuid NOT NULL,membership_id uuid NOT NULL,display_name varchar(120) NOT NULL,email_mask varchar(254),PRIMARY KEY(tenant_id,membership_id),FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id));
CREATE TABLE impact.tenant_custody(tenant_id uuid PRIMARY KEY REFERENCES impact.tenant_root,owner_membership_id uuid NOT NULL,FOREIGN KEY(tenant_id,owner_membership_id) REFERENCES impact.membership_current(tenant_id,object_id));
CREATE TABLE impact.grant_authority(tenant_id uuid NOT NULL,authority_id uuid NOT NULL,principal_id uuid NOT NULL,capability varchar(64) NOT NULL,scope_id uuid NOT NULL,expires_at timestamptz NOT NULL,PRIMARY KEY(tenant_id,authority_id),UNIQUE(tenant_id,principal_id,capability,scope_id),FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal,FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition);
CREATE TABLE impact.member_role_assignment(tenant_id uuid NOT NULL,assignment_id uuid NOT NULL,membership_id uuid NOT NULL,role_template_id uuid NOT NULL,role_revision uuid NOT NULL,scope_id uuid NOT NULL,expires_at timestamptz NOT NULL,grant_ids uuid[] NOT NULL,PRIMARY KEY(tenant_id,assignment_id),FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id),FOREIGN KEY(tenant_id,role_template_id) REFERENCES impact.object_registry,FOREIGN KEY(tenant_id,role_revision) REFERENCES impact.object_revision(tenant_id,revision_id),FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition);
CREATE TABLE impact.admin_reason(tenant_id uuid NOT NULL,revision_id uuid NOT NULL,reason varchar(2000) NOT NULL CHECK(length(trim(reason))>0),PRIMARY KEY(tenant_id,revision_id),FOREIGN KEY(tenant_id,revision_id) REFERENCES impact.object_revision(tenant_id,revision_id));

ALTER TABLE impact.member_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.member_profile FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.member_profile USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.tenant_custody ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_custody FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_custody USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.grant_authority ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.grant_authority FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.grant_authority USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.member_role_assignment ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.member_role_assignment FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.member_role_assignment USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.admin_reason ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.admin_reason FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.admin_reason USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.member_profile TO impact_app;
GRANT SELECT ON impact.tenant_custody,impact.grant_authority TO impact_app;
GRANT SELECT,INSERT ON impact.member_role_assignment,impact.admin_reason TO impact_app;

CREATE UNIQUE INDEX membership_identity_unique ON impact.membership_current(tenant_id,identity_id);
CREATE INDEX invitation_expiry ON impact.member_invitation(tenant_id,expires_at);
CREATE INDEX authority_subject ON impact.grant_authority(tenant_id,principal_id,capability,expires_at);
CREATE FUNCTION impact.member_natural_identity(requested_tenant uuid,requested_principal uuid) RETURNS uuid LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$ SELECT i.natural_identity_id FROM impact.tenant_principal p JOIN impact.auth_identity i ON i.identity_id=p.identity_id WHERE p.tenant_id=requested_tenant AND p.principal_id=requested_principal AND requested_tenant=impact.current_tenant() $$;
REVOKE ALL ON FUNCTION impact.member_natural_identity(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.member_natural_identity(uuid,uuid) TO impact_app;
COMMIT;
```

### 0006 measurement configuration

Source: infrastructure/migrations/0006_measurement_configuration.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Preserve every original registry kind, adding a separate plan aggregate. Job schedules are unchanged.
DO $$
DECLARE original_check text;
BEGIN
  SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
    WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
  ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
  EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
    || regexp_replace(original_check, '\)$', ' OR object_type = ''CollectionPlan'')');
END $$;
ALTER TABLE impact.indicator_definition_current ADD COLUMN numerator_meaning text;
ALTER TABLE impact.indicator_definition_current ADD COLUMN denominator_meaning text;
CREATE TABLE impact.collection_plan_binding(
  tenant_id uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  plan_id uuid NOT NULL,
  plan_revision uuid NOT NULL,
  PRIMARY KEY(tenant_id,indicator_id,period_id),
  UNIQUE(tenant_id,plan_id),
  FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,plan_id,plan_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
ALTER TABLE impact.collection_plan_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.collection_plan_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.collection_plan_binding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.collection_plan_binding TO impact_app;
ALTER TABLE impact.result_binding ADD COLUMN plan_revision uuid;
ALTER TABLE impact.result_binding ADD FOREIGN KEY(tenant_id,plan_revision) REFERENCES impact.object_revision(tenant_id,revision_id);
COMMIT;
```

### 0007 measurement changes

Source: infrastructure/migrations/0007_measurement_changes.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
DO $$
DECLARE original_check text;
BEGIN
  SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
    WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
  ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
  EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
    || regexp_replace(original_check, '\)$', ' OR object_type = ''MeasurementChange'')');
END $$;
CREATE TABLE impact.measurement_change_effect (
  tenant_id uuid NOT NULL,
  change_id uuid NOT NULL,
  target_id uuid NOT NULL,
  before_revision uuid NOT NULL,
  after_revision uuid NOT NULL,
  PRIMARY KEY(tenant_id,change_id),
  FOREIGN KEY(tenant_id,change_id) REFERENCES impact.object_registry(tenant_id,object_id),
  FOREIGN KEY(tenant_id,target_id,before_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,target_id,after_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);
ALTER TABLE impact.measurement_change_effect ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.measurement_change_effect FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.measurement_change_effect
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.measurement_change_effect TO impact_app;
GRANT UPDATE(plan_revision) ON impact.collection_plan_binding TO impact_app;
COMMIT;
```

### 0008 period governance

Source: infrastructure/migrations/0008_period_governance.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
ALTER TABLE impact.snapshot_current ADD COLUMN programme_id uuid;
ALTER TABLE impact.snapshot_current ADD CONSTRAINT snapshot_programme_fk
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id)
  DEFERRABLE INITIALLY DEFERRED;
DO $$
DECLARE original_check text;
BEGIN
  SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
    WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
  ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
  EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
    || regexp_replace(original_check, '\)$', ' OR object_type IN (''PeriodClose'',''RestatementRequest''))');
END $$;
CREATE TABLE impact.period_snapshot_binding(
  tenant_id uuid NOT NULL,
  programme_id uuid NOT NULL,
  period_id uuid NOT NULL,
  snapshot_version integer NOT NULL CHECK(snapshot_version>0),
  snapshot_id uuid NOT NULL,
  snapshot_revision uuid NOT NULL,
  close_id uuid NOT NULL,
  close_revision uuid NOT NULL,
  supersedes_snapshot_id uuid,
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,programme_id,period_id,snapshot_version),
  UNIQUE(tenant_id,snapshot_id),
  UNIQUE(tenant_id,close_id),
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,snapshot_id,snapshot_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,close_id,close_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,supersedes_snapshot_id) REFERENCES impact.object_registry(tenant_id,object_id)
);
CREATE TABLE impact.programme_period_state(
  tenant_id uuid NOT NULL,
  programme_id uuid NOT NULL,
  period_id uuid NOT NULL,
  lifecycle_state text NOT NULL CHECK(lifecycle_state IN ('Open','Locked','RestatementOpen')),
  current_snapshot_version integer NOT NULL DEFAULT 0 CHECK(current_snapshot_version>=0),
  restatement_expires_at timestamptz,
  updated_at timestamptz NOT NULL,
  updated_by uuid NOT NULL,
  PRIMARY KEY(tenant_id,programme_id,period_id),
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,updated_by) REFERENCES impact.tenant_principal(tenant_id,principal_id),
  CHECK((lifecycle_state='RestatementOpen')=(restatement_expires_at IS NOT NULL))
);
CREATE TABLE impact.official_result_snapshot(
  tenant_id uuid NOT NULL,
  snapshot_id uuid NOT NULL,
  result_id uuid NOT NULL,
  result_revision uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,snapshot_id,result_id),
  UNIQUE(tenant_id,result_revision),
  FOREIGN KEY(tenant_id,snapshot_id) REFERENCES impact.object_registry(tenant_id,object_id),
  FOREIGN KEY(tenant_id,result_id,result_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id)
);
CREATE TABLE impact.restatement_source_permission(
  tenant_id uuid NOT NULL,
  request_id uuid NOT NULL,
  request_revision uuid NOT NULL,
  programme_id uuid NOT NULL,
  period_id uuid NOT NULL,
  source_id uuid NOT NULL,
  expires_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,request_id,source_id),
  FOREIGN KEY(tenant_id,request_id,request_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,source_id) REFERENCES impact.observation_current(tenant_id,object_id)
);
ALTER TABLE impact.period_snapshot_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.period_snapshot_binding FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.programme_period_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.programme_period_state FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.official_result_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.official_result_snapshot FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.restatement_source_permission ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.restatement_source_permission FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.period_snapshot_binding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.programme_period_state USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.official_result_snapshot USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.restatement_source_permission USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.period_snapshot_binding,impact.official_result_snapshot,impact.restatement_source_permission TO impact_app;
GRANT SELECT,INSERT,UPDATE ON impact.programme_period_state TO impact_app;
COMMIT;
```

### 0009 reporting packages

Source: infrastructure/migrations/0009_reporting_packages.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.report_package_binding(
  tenant_id uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  snapshot_id uuid NOT NULL,
  snapshot_revision uuid NOT NULL,
  template_revision uuid NOT NULL,
  reconciliation_digest bytea NOT NULL CHECK(octet_length(reconciliation_digest)=32),
  approved_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,report_id,report_revision),
  UNIQUE(tenant_id,report_revision),
  FOREIGN KEY(tenant_id,report_id,report_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,snapshot_id,snapshot_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,template_revision) REFERENCES impact.object_revision(tenant_id,revision_id)
);
ALTER TABLE impact.report_package_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_package_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.report_package_binding
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.report_package_binding TO impact_app;
COMMIT;
```

### 0010 work and recalculation

Source: infrastructure/migrations/0010_work_and_recalculation.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;

CREATE TABLE impact.calculation_invalidation(
  tenant_id uuid NOT NULL,
  invalidation_id uuid NOT NULL,
  result_id uuid NOT NULL,
  result_revision uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  triggering_revision uuid NOT NULL,
  reason_code text NOT NULL CHECK(reason_code IN ('SOURCE_APPROVED','SOURCE_CORRECTED','PLAN_APPROVED','PLAN_AMENDED')),
  work_item_id uuid NOT NULL,
  state text NOT NULL CHECK(state IN ('PENDING','RECALCULATED','CANCELLED')),
  created_at timestamptz NOT NULL,
  resolved_at timestamptz,
  replacement_result_id uuid,
  PRIMARY KEY(tenant_id,invalidation_id),
  UNIQUE(tenant_id,result_revision,triggering_revision),
  FOREIGN KEY(tenant_id,result_id,result_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,triggering_revision) REFERENCES impact.object_revision(tenant_id,revision_id),
  FOREIGN KEY(tenant_id,work_item_id) REFERENCES impact.work_item_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,replacement_result_id) REFERENCES impact.calculated_result_current(tenant_id,object_id),
  CHECK((state='PENDING' AND resolved_at IS NULL AND replacement_result_id IS NULL)
    OR (state='RECALCULATED' AND resolved_at IS NOT NULL AND replacement_result_id IS NOT NULL)
    OR (state='CANCELLED' AND resolved_at IS NOT NULL AND replacement_result_id IS NULL))
);

CREATE INDEX calculation_invalidation_pending
  ON impact.calculation_invalidation(tenant_id,indicator_id,period_id)
  WHERE state='PENDING';

CREATE TABLE impact.notification_acknowledgement(
  tenant_id uuid NOT NULL,
  notification_id uuid NOT NULL,
  recipient_id uuid NOT NULL,
  acknowledged_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,notification_id),
  FOREIGN KEY(tenant_id,notification_id) REFERENCES impact.notification_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,recipient_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);

ALTER TABLE impact.calculation_invalidation ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.calculation_invalidation FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.notification_acknowledgement ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.notification_acknowledgement FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_fence ON impact.calculation_invalidation
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.notification_acknowledgement
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT ON impact.calculation_invalidation TO impact_app;
GRANT UPDATE(state,resolved_at,replacement_result_id) ON impact.calculation_invalidation TO impact_app;
GRANT SELECT,INSERT ON impact.notification_acknowledgement TO impact_app;

COMMIT;
```

### 0011 controlled publication

Source: infrastructure/migrations/0011_controlled_publication.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.disclosure_current
  ADD COLUMN published_at timestamptz,
  ADD COLUMN withdrawn_at timestamptz,
  ADD COLUMN withdrawal_reason varchar(2000);

CREATE TABLE impact.report_publication_artifact(
  tenant_id uuid NOT NULL,
  disclosure_id uuid NOT NULL,
  disclosure_revision uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('HTML','CSV')),
  media_type text NOT NULL,
  body bytea NOT NULL CHECK(octet_length(body)<=5242880),
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,disclosure_id,format),
  CHECK((format='HTML' AND media_type='text/html; charset=utf-8')
    OR (format='CSV' AND media_type='text/csv; charset=utf-8')),
  FOREIGN KEY(tenant_id,disclosure_id,disclosure_revision)
    REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,report_id,report_revision)
    REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);

CREATE INDEX report_publication_artifact_report
  ON impact.report_publication_artifact(tenant_id,report_id,report_revision);

CREATE TABLE impact.report_publication_access(
  tenant_id uuid NOT NULL,
  access_id uuid NOT NULL,
  disclosure_id uuid NOT NULL,
  recipient_id uuid NOT NULL,
  membership_id uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('HTML','CSV')),
  access_mode text NOT NULL CHECK(access_mode IN ('VIEW','DOWNLOAD')),
  accessed_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,access_id),
  CHECK((format='HTML' AND access_mode='VIEW')
    OR (format='CSV' AND access_mode='DOWNLOAD')),
  FOREIGN KEY(tenant_id,disclosure_id) REFERENCES impact.disclosure_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,recipient_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
  FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id)
);

ALTER TABLE impact.report_publication_artifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_artifact FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_access FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.report_publication_artifact
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.report_publication_access
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT ON impact.report_publication_artifact TO impact_app;
GRANT INSERT ON impact.report_publication_access TO impact_app;

COMMIT;
```

### 0012 workspace administration

Source: infrastructure/migrations/0012_workspace_administration.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;

DO $$ DECLARE definition text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO definition FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(definition, '\)$', ' OR object_type IN (''AccessGroup'',''GroupChangeRequest'',''MembershipRenewal'',''CustodyTransfer''))');
END $$;

CREATE TABLE impact.group_entitlement (
 tenant_id uuid NOT NULL, group_id uuid NOT NULL, membership_id uuid NOT NULL,
 capability varchar(64) NOT NULL, scope_id uuid NOT NULL, expires_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,group_id,membership_id,capability,scope_id),
 FOREIGN KEY(tenant_id,group_id) REFERENCES impact.object_registry,
 FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current,
 FOREIGN KEY(tenant_id,scope_id) REFERENCES impact.scope_definition
);
ALTER TABLE impact.group_entitlement ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.group_entitlement FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.group_entitlement USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,DELETE ON impact.group_entitlement TO impact_app;
CREATE INDEX group_entitlement_member ON impact.group_entitlement(tenant_id,membership_id,expires_at);
CREATE UNIQUE INDEX organisation_unit_code_unique ON impact.organisation_unit_current(tenant_id,lower(code));

ALTER TABLE impact.web_session ADD COLUMN session_id uuid NOT NULL DEFAULT gen_random_uuid();
ALTER TABLE impact.web_session ADD CONSTRAINT web_session_public_id UNIQUE(session_id);
ALTER TABLE impact.web_session ADD COLUMN device_label varchar(120) NOT NULL DEFAULT 'Browser session';
ALTER TABLE impact.web_session ADD COLUMN assurance_acr varchar(200) NOT NULL DEFAULT '';
ALTER TABLE impact.web_session ADD COLUMN assurance_amr text[] NOT NULL DEFAULT '{}';
-- All sessions use the stricter 15-minute inactivity bound; absolute lifetime stays eight hours.
CREATE TABLE impact.identity_preferences(
 identity_id uuid PRIMARY KEY REFERENCES impact.auth_identity,
 display_name varchar(120) NOT NULL,
 language varchar(20) NOT NULL DEFAULT 'en', timezone varchar(80) NOT NULL DEFAULT 'UTC',
 reduced_motion boolean NOT NULL DEFAULT false,
 revision_id uuid NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE impact.identity_security_event(
 event_id uuid PRIMARY KEY, identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 action varchar(64) NOT NULL, target_session uuid, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE impact.identity_security_state(identity_id uuid PRIMARY KEY REFERENCES impact.auth_identity,auth_not_before timestamptz NOT NULL);
GRANT SELECT,INSERT,UPDATE ON impact.identity_security_state TO impact_identity;
GRANT SELECT,INSERT,UPDATE ON impact.identity_preferences TO impact_identity;
GRANT SELECT,INSERT ON impact.identity_security_event TO impact_identity;

-- The runtime role still cannot directly update custody. Transfer requires an immutable
-- nominated request, unchanged custody, and a different active natural identity.
CREATE FUNCTION impact.accept_custody(requested_tenant uuid, request_id uuid, accepting_principal uuid)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE p jsonb; owner_id uuid; successor uuid; old_natural uuid; new_natural uuid;
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() THEN RAISE EXCEPTION 'tenant denied' USING ERRCODE='42501'; END IF;
 SELECT v.payload INTO p FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision
 WHERE r.tenant_id=requested_tenant AND r.object_id=request_id AND r.object_type='CustodyTransfer' AND r.lifecycle_state='Requested';
 IF p IS NULL OR (p->>'expires_at')::timestamptz<=now() THEN RAISE EXCEPTION 'transfer unavailable' USING ERRCODE='23514'; END IF;
 SELECT owner_membership_id INTO owner_id FROM impact.tenant_custody WHERE tenant_id=requested_tenant FOR UPDATE;
 successor:=(p->>'membership_id')::uuid;
 IF owner_id IS DISTINCT FROM (p->>'owner_membership_id')::uuid OR owner_id=successor THEN RAISE EXCEPTION 'custody changed' USING ERRCODE='23514'; END IF;
 SELECT i.natural_identity_id INTO old_natural FROM impact.membership_current m JOIN impact.auth_identity i USING(identity_id) WHERE m.tenant_id=requested_tenant AND m.object_id=owner_id;
 SELECT i.natural_identity_id INTO new_natural FROM impact.membership_current m
 JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id
 JOIN impact.tenant_principal t ON t.tenant_id=m.tenant_id AND t.identity_id=m.identity_id
 JOIN impact.auth_identity i ON i.identity_id=m.identity_id
 WHERE m.tenant_id=requested_tenant AND m.object_id=successor AND t.principal_id=accepting_principal AND t.active
 AND r.lifecycle_state='Active' AND (m.expires_at IS NULL OR m.expires_at>now())
 AND r.head_revision=(p->>'expected_membership_revision')::uuid;
 IF new_natural IS NULL OR old_natural IS NULL OR new_natural=old_natural THEN RAISE EXCEPTION 'independence required' USING ERRCODE='23514'; END IF;
 UPDATE impact.tenant_custody SET owner_membership_id=successor WHERE tenant_id=requested_tenant;
END $$;
REVOKE ALL ON FUNCTION impact.accept_custody(uuid,uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.accept_custody(uuid,uuid,uuid) TO impact_app;
COMMIT;
```

### 0013 tenant lifecycle

Source: infrastructure/migrations/0013_tenant_lifecycle.sql

```sql
BEGIN;
DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='impact_platform') THEN
 CREATE ROLE impact_platform NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
END IF; END $$;
GRANT USAGE ON SCHEMA impact TO impact_platform;
SET LOCAL ROLE impact_owner;
GRANT EXECUTE ON FUNCTION impact.current_tenant() TO impact_platform;

-- Provisioned by deployment administration, never writable by HTTP runtime roles.
CREATE TABLE impact.platform_operator(
 identity_id uuid PRIMARY KEY REFERENCES impact.auth_identity,
 active boolean NOT NULL DEFAULT true, expires_at timestamptz NOT NULL,
 authority_reference varchar(300) NOT NULL
);
CREATE TABLE impact.deployment_qualification(
 qualification_id uuid PRIMARY KEY, revision_id uuid NOT NULL,
 environment varchar(20) NOT NULL, region varchar(80) NOT NULL,
 issuer text NOT NULL, required_acr varchar(200) NOT NULL,
 privacy_reference varchar(300) NOT NULL, recovery_reference varchar(300) NOT NULL,
 retention_max_days integer NOT NULL CHECK(retention_max_days BETWEEN 1 AND 36500),
 valid_until timestamptz NOT NULL, active boolean NOT NULL DEFAULT true
);
CREATE TABLE impact.tenant_onboarding(
 tenant_id uuid PRIMARY KEY REFERENCES impact.tenant_root,
 revision_id uuid NOT NULL, requested_by uuid NOT NULL REFERENCES impact.auth_identity,
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 qualification_id uuid NOT NULL REFERENCES impact.deployment_qualification,
 qualification_revision uuid NOT NULL,
 operating_name varchar(200) NOT NULL, reporting_zone varchar(80) NOT NULL,
 retention_days integer NOT NULL CHECK(retention_days BETWEEN 1 AND 36500),
 privacy_reference varchar(300) NOT NULL,
 owner_accepted_at timestamptz, owner_expires_at timestamptz NOT NULL,
 owner_membership_id uuid, tenant_object_id uuid,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE impact.platform_event(
 event_id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 action varchar(50) NOT NULL, revision_id uuid NOT NULL, reason varchar(1000) NOT NULL,
 payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE impact.platform_receipt(
 identity_id uuid NOT NULL REFERENCES impact.auth_identity, operation_id uuid NOT NULL,
 fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
 response jsonb NOT NULL, expires_at timestamptz NOT NULL,
 PRIMARY KEY(identity_id,operation_id)
);
CREATE FUNCTION impact.lock_platform_operator(actor uuid) RETURNS boolean LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(SELECT 1 FROM impact.platform_operator WHERE identity_id=actor AND active AND expires_at>now() FOR SHARE)
$$;
CREATE FUNCTION impact.lock_deployment_qualification(requested uuid) RETURNS SETOF impact.deployment_qualification LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT * FROM impact.deployment_qualification WHERE qualification_id=requested FOR SHARE
$$;
REVOKE ALL ON FUNCTION impact.lock_platform_operator(uuid),impact.lock_deployment_qualification(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.lock_platform_operator(uuid),impact.lock_deployment_qualification(uuid) TO impact_platform;
GRANT SELECT ON impact.platform_operator,impact.deployment_qualification,impact.auth_identity,impact.identity_profile TO impact_platform;
GRANT SELECT,INSERT,UPDATE ON impact.tenant_onboarding TO impact_platform;
GRANT SELECT,INSERT ON impact.platform_event,impact.platform_receipt TO impact_platform;
GRANT SELECT,INSERT,UPDATE ON impact.tenant_root,impact.tenant_principal,impact.object_registry,
 impact.tenant_current,impact.membership_current,impact.retention_policy_current TO impact_platform;
GRANT SELECT,INSERT ON impact.object_revision,impact.tenant_custody,impact.member_profile TO impact_platform;
-- Tenant-scoped metadata only; operators do not gain business-record access.
CREATE POLICY platform_registry_types ON impact.object_registry AS RESTRICTIVE TO impact_platform
 USING(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy'))
 WITH CHECK(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy'));
CREATE POLICY platform_revision_types ON impact.object_revision AS RESTRICTIVE TO impact_platform
 USING(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy'))
 WITH CHECK(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy'));
REVOKE INSERT,UPDATE ON impact.tenant_root FROM impact_app,impact_worker;
GRANT UPDATE(policy_epoch) ON impact.tenant_root TO impact_app,impact_worker;

ALTER TABLE impact.outbox_delivery ADD COLUMN held_at timestamptz;
ALTER TABLE impact.webhook_delivery ADD COLUMN held_at timestamptz;
-- No payloads are returned and only an already-fenced tenant can be quiesced.
CREATE FUNCTION impact.quiesce_tenant(requested_tenant uuid) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() OR NOT EXISTS(
 SELECT 1 FROM impact.tenant_root WHERE tenant_id=requested_tenant AND lifecycle_state IN ('Suspended','Closing'))
 THEN RAISE EXCEPTION 'tenant not fenced' USING ERRCODE='42501'; END IF;
 UPDATE impact.job SET cancellation_requested_at=now(),
 state=CASE WHEN state IN ('Requested','Validating','Queued') THEN 'Cancelled' ELSE 'Cancelling' END,
 lease_generation=lease_generation+1
 WHERE tenant_id=requested_tenant AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled');
 UPDATE impact.outbox_delivery SET held_at=COALESCE(held_at,now()) WHERE tenant_id=requested_tenant AND sent_at IS NULL;
 UPDATE impact.webhook_delivery SET held_at=COALESCE(held_at,now()) WHERE tenant_id=requested_tenant;
 -- Keep schedule revisions intact: an explicit operational hold survives reactivation.
 INSERT INTO impact.tenant_schedule_hold(tenant_id,schedule_id)
 SELECT tenant_id,object_id FROM impact.object_registry WHERE tenant_id=requested_tenant
 AND object_type='Schedule' AND lifecycle_state='Active' ON CONFLICT DO NOTHING;
END $$;
CREATE TABLE impact.tenant_schedule_hold(
 tenant_id uuid NOT NULL, schedule_id uuid NOT NULL, held_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant_id,schedule_id), FOREIGN KEY(tenant_id,schedule_id) REFERENCES impact.object_registry
);
ALTER TABLE impact.tenant_schedule_hold ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_schedule_hold FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_schedule_hold USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT ON impact.tenant_schedule_hold TO impact_app,impact_worker;
REVOKE ALL ON FUNCTION impact.quiesce_tenant(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.quiesce_tenant(uuid) TO impact_platform;
CREATE FUNCTION impact.tenant_work_impact(requested_tenant uuid) RETURNS jsonb
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() THEN RAISE EXCEPTION 'tenant denied' USING ERRCODE='42501'; END IF;
 RETURN jsonb_build_object(
 'unfinished_jobs',(SELECT count(*) FROM impact.job WHERE tenant_id=requested_tenant AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled')),
 'active_schedules',(SELECT count(*) FROM impact.object_registry WHERE tenant_id=requested_tenant AND object_type='Schedule' AND lifecycle_state='Active'),
 'unsent_events',(SELECT count(*) FROM impact.outbox_delivery WHERE tenant_id=requested_tenant AND sent_at IS NULL),
 'retention_holds',(SELECT count(*) FROM impact.retention_hold WHERE tenant_id=requested_tenant AND released_at IS NULL));
END $$;
REVOKE ALL ON FUNCTION impact.tenant_work_impact(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.tenant_work_impact(uuid) TO impact_platform;
CREATE FUNCTION impact.sync_onboarding_custody() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 UPDATE impact.tenant_onboarding SET owner_membership_id=NEW.owner_membership_id,
 owner_identity_id=(SELECT identity_id FROM impact.membership_current WHERE tenant_id=NEW.tenant_id AND object_id=NEW.owner_membership_id),
 revision_id=gen_random_uuid(),updated_at=now() WHERE tenant_id=NEW.tenant_id;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.sync_onboarding_custody() FROM PUBLIC;
CREATE TRIGGER onboarding_custody AFTER UPDATE ON impact.tenant_custody FOR EACH ROW EXECUTE FUNCTION impact.sync_onboarding_custody();
COMMIT;
```

### 0014 initial access

Source: infrastructure/migrations/0014_initial_access.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.tenant_access_bootstrap(
 request_id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES impact.tenant_onboarding,
 revision_id uuid NOT NULL, state varchar(20) NOT NULL CHECK(state IN ('Requested','Accepted','Applied','Rejected','Cancelled')),
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 second_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 tenant_revision uuid NOT NULL, owner_revision uuid NOT NULL,
 manifest jsonb NOT NULL, profile_hash varchar(64) NOT NULL,
 expires_at timestamptz NOT NULL, review_expires_at timestamptz NOT NULL,
 owner_auth_time timestamptz NOT NULL, second_auth_time timestamptz,
 accepted_at timestamptz, approved_by uuid REFERENCES impact.auth_identity,
 scope_id uuid, second_membership_id uuid,
 reason varchar(1000) NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK(owner_identity_id<>second_identity_id)
);
CREATE UNIQUE INDEX bootstrap_one_live ON impact.tenant_access_bootstrap(tenant_id)
 WHERE state IN ('Requested','Accepted','Applied');
CREATE TABLE impact.tenant_access_bootstrap_applied(
 tenant_id uuid PRIMARY KEY REFERENCES impact.tenant_onboarding,
 request_id uuid NOT NULL UNIQUE REFERENCES impact.tenant_access_bootstrap,
 applied_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT,INSERT,UPDATE ON impact.tenant_access_bootstrap TO impact_platform;
GRANT SELECT ON impact.tenant_access_bootstrap_applied,impact.grant_authority,impact.identity_security_state TO impact_platform;
GRANT SELECT,INSERT ON impact.scope_definition,impact.member_role_assignment TO impact_platform;
GRANT SELECT,INSERT,UPDATE ON impact.grant_current TO impact_platform;
ALTER POLICY platform_registry_types ON impact.object_registry
 USING(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy','Grant','RoleTemplate','Predicate'))
 WITH CHECK(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy','Grant','RoleTemplate','Predicate'));
ALTER POLICY platform_revision_types ON impact.object_revision
 USING(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy','Grant','RoleTemplate','Predicate'))
 WITH CHECK(object_type IN ('Tenant','Membership','HostingPolicy','PrivacyPolicy','RetentionPolicy','Grant','RoleTemplate','Predicate'));
-- The HTTP role cannot insert arbitrary delegation authority or reset this marker.
-- This function can apply only the reviewed manifest once for an active tenant.
CREATE FUNCTION impact.apply_initial_authority(requested uuid) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE r impact.tenant_access_bootstrap;
BEGIN
 SELECT * INTO r FROM impact.tenant_access_bootstrap WHERE request_id=requested FOR UPDATE;
 IF NOT FOUND OR r.tenant_id IS DISTINCT FROM impact.current_tenant() OR r.state<>'Applied'
 OR r.accepted_at IS NULL OR r.expires_at<=now() OR r.review_expires_at<=now()
 OR r.approved_by IS NULL OR NOT impact.lock_platform_operator(r.approved_by)
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_root WHERE tenant_id=r.tenant_id AND lifecycle_state='Active')
 OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
 WHERE a.identity_id=r.approved_by AND b.identity_id IN(r.owner_identity_id,r.second_identity_id))
 THEN RAISE EXCEPTION 'initial authority denied' USING ERRCODE='42501'; END IF;
 INSERT INTO impact.tenant_access_bootstrap_applied(tenant_id,request_id) VALUES(r.tenant_id,r.request_id);
 INSERT INTO impact.grant_authority(tenant_id,authority_id,principal_id,capability,scope_id,expires_at)
 SELECT r.tenant_id,gen_random_uuid(),p.principal_id,cap,r.scope_id,r.expires_at
 FROM impact.tenant_principal p CROSS JOIN
 (SELECT DISTINCT jsonb_array_elements_text(value) AS cap FROM jsonb_each(r.manifest->'roles')) caps
 WHERE p.tenant_id=r.tenant_id AND p.active AND p.identity_id IN(r.owner_identity_id,r.second_identity_id);
END $$;
REVOKE ALL ON FUNCTION impact.apply_initial_authority(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.apply_initial_authority(uuid) TO impact_platform;
COMMIT;
```

### 0015 recovery contacts

Source: infrastructure/migrations/0015_recovery_contacts.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
CREATE TABLE impact.tenant_recovery_contact(
 contact_id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES impact.tenant_onboarding,
 revision_id uuid NOT NULL,
 state varchar(20) NOT NULL CHECK(state IN ('Nominated','Verified','Active','Replaced','Revoked','Declined','Cancelled','Rejected')),
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 owner_membership_id uuid NOT NULL, owner_revision uuid NOT NULL, tenant_revision uuid NOT NULL,
 nominee_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 email_hash bytea NOT NULL CHECK(octet_length(email_hash)=32),
 display_name varchar(200) NOT NULL, email_mask varchar(300) NOT NULL,
 replaces_contact_id uuid REFERENCES impact.tenant_recovery_contact, replaces_revision uuid,
 owner_auth_time timestamptz NOT NULL, verified_auth_time timestamptz,
 verified_at timestamptz, approved_by uuid REFERENCES impact.auth_identity, approved_at timestamptz,
 expires_at timestamptz NOT NULL, review_expires_at timestamptz NOT NULL,
 reason varchar(1000) NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK(owner_identity_id<>nominee_identity_id),
 CHECK((replaces_contact_id IS NULL)=(replaces_revision IS NULL))
);
CREATE UNIQUE INDEX recovery_one_active ON impact.tenant_recovery_contact(tenant_id) WHERE state='Active';
CREATE UNIQUE INDEX recovery_one_pending ON impact.tenant_recovery_contact(tenant_id) WHERE state IN ('Nominated','Verified');
GRANT SELECT,INSERT,UPDATE ON impact.tenant_recovery_contact TO impact_platform;

-- Serialize evidence checks against the account revocation path, which locks
-- auth_identity before updating authentication cutoffs. No profile data is returned.
CREATE FUNCTION impact.lock_recovery_identities(actors uuid[]) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 PERFORM identity_id FROM impact.auth_identity WHERE identity_id=ANY(actors) ORDER BY identity_id FOR SHARE;
 PERFORM identity_id FROM impact.identity_profile WHERE identity_id=ANY(actors) ORDER BY identity_id FOR SHARE;
 PERFORM identity_id FROM impact.identity_security_state WHERE identity_id=ANY(actors) ORDER BY identity_id FOR SHARE;
END $$;
REVOKE ALL ON FUNCTION impact.lock_recovery_identities(uuid[]) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.lock_recovery_identities(uuid[]) TO impact_platform;
COMMIT;
```

### 0016 authority renewal

Source: infrastructure/migrations/0016_authority_renewal.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Reviewed renewal of the delegated authority created by initial access (0014).
-- The review row pins the exact authority manifest; approval can only extend the
-- pinned, still-present rows and never recreates a revoked or removed one.
CREATE TABLE impact.tenant_authority_renewal(
 request_id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES impact.tenant_onboarding,
 revision_id uuid NOT NULL, state varchar(20) NOT NULL CHECK(state IN ('Requested','Accepted','Applied','Rejected','Cancelled')),
 bootstrap_request_id uuid NOT NULL REFERENCES impact.tenant_access_bootstrap,
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 second_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 tenant_revision uuid NOT NULL, owner_revision uuid NOT NULL,
 manifest jsonb NOT NULL, authority_hash varchar(64) NOT NULL,
 previous_expires_at timestamptz NOT NULL, expires_at timestamptz NOT NULL, review_expires_at timestamptz NOT NULL,
 owner_auth_time timestamptz NOT NULL, second_auth_time timestamptz,
 accepted_at timestamptz, approved_by uuid REFERENCES impact.auth_identity, applied_at timestamptz,
 reason varchar(1000) NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK(owner_identity_id<>second_identity_id),
 CHECK(expires_at>previous_expires_at)
);
CREATE UNIQUE INDEX renewal_one_live ON impact.tenant_authority_renewal(tenant_id)
 WHERE state IN ('Requested','Accepted');
GRANT SELECT,INSERT,UPDATE ON impact.tenant_authority_renewal TO impact_platform;
-- The HTTP control-plane role keeps the 0014 write surface: delegation ceilings and role
-- assignment expiry are re-dated only through the reviewed applicator below, which extends
-- exactly the pinned, unexpired rows of an Applied renewal that an independent active
-- operator approved for an Active tenant whose initial access marker is the pinned one.
-- Any pinned row that is missing or already expired aborts the whole transaction.
CREATE FUNCTION impact.apply_authority_renewal(requested uuid, OUT authorities integer, OUT assignments integer)
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE r impact.tenant_authority_renewal; expected integer;
BEGIN
 SELECT * INTO r FROM impact.tenant_authority_renewal WHERE request_id=requested FOR UPDATE;
 IF NOT FOUND OR r.tenant_id IS DISTINCT FROM impact.current_tenant() OR r.state<>'Applied'
 OR r.accepted_at IS NULL OR r.expires_at<=now() OR r.review_expires_at<=now()
 OR r.expires_at>now()+interval '90 days' OR r.expires_at<=r.previous_expires_at OR r.review_expires_at>r.expires_at
 OR r.approved_by IS NULL OR NOT impact.lock_platform_operator(r.approved_by)
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_root WHERE tenant_id=r.tenant_id AND lifecycle_state='Active')
 OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
 WHERE a.identity_id=r.approved_by AND b.identity_id IN(r.owner_identity_id,r.second_identity_id))
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_access_bootstrap_applied
 WHERE tenant_id=r.tenant_id AND request_id=r.bootstrap_request_id)
 THEN RAISE EXCEPTION 'authority renewal denied' USING ERRCODE='42501'; END IF;
 SELECT count(*) INTO expected FROM jsonb_array_elements_text(r.manifest->'authority_ids');
 UPDATE impact.grant_authority SET expires_at=r.expires_at
 WHERE tenant_id=r.tenant_id AND expires_at>now()
 AND authority_id=ANY(ARRAY(SELECT value::uuid FROM jsonb_array_elements_text(r.manifest->'authority_ids')));
 GET DIAGNOSTICS authorities=ROW_COUNT;
 IF authorities<>expected THEN RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501'; END IF;
 SELECT count(*) INTO expected FROM jsonb_array_elements(r.manifest->'principals') p
 CROSS JOIN LATERAL jsonb_array_elements_text(p->'assignment_ids') i;
 UPDATE impact.member_role_assignment a SET expires_at=r.expires_at
 FROM (SELECT (p->>'membership_id')::uuid AS membership_id,(p->>'scope_id')::uuid AS scope_id,i.value::uuid AS assignment_id
 FROM jsonb_array_elements(r.manifest->'principals') p CROSS JOIN LATERAL jsonb_array_elements_text(p->'assignment_ids') i) pinned
 WHERE a.tenant_id=r.tenant_id AND a.assignment_id=pinned.assignment_id AND a.membership_id=pinned.membership_id
 AND a.scope_id=pinned.scope_id AND a.expires_at>now();
 GET DIAGNOSTICS assignments=ROW_COUNT;
 IF assignments<>expected THEN RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501'; END IF;
END $$;
REVOKE ALL ON FUNCTION impact.apply_authority_renewal(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.apply_authority_renewal(uuid) TO impact_platform;
COMMIT;
```

### 0017 provider logout

Source: infrastructure/migrations/0017_provider_logout.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Live identity provider (v0.15). A browser session created from an OIDC sign-in records the
-- provider's session identifier (the ID token's sid claim) so that a verified back-channel logout
-- token revokes exactly the platform sessions of that provider session, and a sealed logout hint:
-- the ID token encrypted (AES-256-GCM) under a key derived from the session cookie value, which
-- the database never stores, so the hint is usable only by a request that presents the session.
-- No provider access or refresh token is stored anywhere. Development sign-in leaves both NULL.
ALTER TABLE impact.web_session ADD COLUMN provider_sid varchar(255);
ALTER TABLE impact.web_session ADD COLUMN provider_logout_hint bytea
 CHECK(octet_length(provider_logout_hint) BETWEEN 29 AND 16412);
CREATE INDEX web_session_provider_sid ON impact.web_session(provider_sid) WHERE provider_sid IS NOT NULL;
-- Back-channel logout tokens already accepted, per issuer and jti, until the token expires: a
-- replayed token is refused. Insert-once (no UPDATE grant); expired rows are purged by the
-- identity role in bounded batches. Identity table: no tenant_id, reached only via impact_identity.
CREATE TABLE impact.oidc_logout_token(
 issuer varchar(512) NOT NULL, jti varchar(255) NOT NULL, expires_at timestamptz NOT NULL,
 accepted_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(issuer,jti)
);
CREATE INDEX oidc_logout_token_expiry ON impact.oidc_logout_token(expires_at);
GRANT SELECT,INSERT,DELETE ON impact.oidc_logout_token TO impact_identity;
COMMIT;
```

### 0018 worker delivery

Source: infrastructure/migrations/0018_worker_delivery.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Worker runtime and outbox dispatcher (v0.16). An outbox_delivery row stays intent, never proof of
-- delivery: only the worker records an outcome, under a generation-fenced lease. Rows written before
-- this migration (and every object.changed event) carry no channel and are never dispatched.
ALTER TABLE impact.outbox_delivery
 ADD COLUMN channel varchar(16) CHECK(channel IN ('IN_APP','EMAIL')),
 ADD COLUMN template varchar(64) CHECK(template IN ('IN_APP_NOTICE','MEMBER_INVITATION','RECOVERY_CHANNEL_VERIFICATION')),
 ADD COLUMN reference_id uuid,
 ADD COLUMN reference_generation varchar(64),
 -- The recipient address, AES-256-GCM sealed under a key derived from the delivery secret, which the
 -- database never holds; bound to tenant, template and reference. No token or code is ever stored.
 ADD COLUMN recipient_sealed bytea CHECK(octet_length(recipient_sealed) BETWEEN 29 AND 300),
 ADD COLUMN state varchar(16) NOT NULL DEFAULT 'PENDING'
  CHECK(state IN ('PENDING','LEASED','SENT','DEAD','SUPERSEDED')),
 ADD COLUMN lease_owner varchar(128),
 ADD COLUMN lease_generation bigint NOT NULL DEFAULT 0 CHECK(lease_generation>=0),
 ADD COLUMN lease_expires_at timestamptz,
 ADD COLUMN next_attempt_at timestamptz NOT NULL DEFAULT now(),
 ADD COLUMN last_attempt_at timestamptz,
 ADD COLUMN last_error_class varchar(64) CHECK(last_error_class ~ '^[A-Z][A-Z0-9_]{0,63}$'),
 ADD COLUMN completed_at timestamptz,
 ADD CONSTRAINT outbox_delivery_dispatch CHECK((channel IS NULL)=(template IS NULL) AND (channel IS NOT NULL OR state='PENDING')),
 ADD CONSTRAINT outbox_delivery_channel CHECK((template='IN_APP_NOTICE')=(channel='IN_APP') AND (channel<>'EMAIL' OR recipient_sealed IS NOT NULL)),
 ADD CONSTRAINT outbox_delivery_lease CHECK((state='LEASED')=(lease_owner IS NOT NULL AND lease_expires_at IS NOT NULL)),
 ADD CONSTRAINT outbox_delivery_terminal CHECK(channel IS NULL OR ((state IN ('SENT','DEAD','SUPERSEDED'))=(completed_at IS NOT NULL) AND (state='SENT')=(sent_at IS NOT NULL)));
CREATE INDEX outbox_delivery_due ON impact.outbox_delivery(tenant_id,next_attempt_at)
 WHERE channel IS NOT NULL AND state IN ('PENDING','LEASED') AND held_at IS NULL;
CREATE INDEX outbox_delivery_reference ON impact.outbox_delivery(tenant_id,reference_id) WHERE reference_id IS NOT NULL;
-- The application writes intents; outcomes are the worker's alone.
REVOKE UPDATE ON impact.outbox_delivery FROM impact_app;

-- Exactly-once visible effect of an in-app delivery: one row per notification and channel.
CREATE TABLE impact.notification_delivery(
 tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 notification_id uuid NOT NULL, channel varchar(16) NOT NULL CHECK(channel='IN_APP'),
 event_id uuid NOT NULL, delivered_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,notification_id,channel),
 FOREIGN KEY(tenant_id,notification_id) REFERENCES impact.notification_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,event_id) REFERENCES impact.outbox_event(tenant_id,event_id)
);
ALTER TABLE impact.notification_delivery ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.notification_delivery FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.notification_delivery USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.notification_delivery TO impact_worker;
GRANT SELECT ON impact.notification_delivery TO impact_app;

-- Recovery-contact channel verification: a single-use, expiring code, stored only as an HMAC under
-- the delivery secret. Evidence that the contact controls the registered mailbox; it changes
-- nothing a recovery contact may do. Written by the control plane; the worker only reads it to
-- recheck that a challenge is still pending before sending.
ALTER TABLE impact.tenant_recovery_contact
 ADD COLUMN channel_verified_at timestamptz,
 ADD COLUMN channel_challenge_id uuid,
 ADD CONSTRAINT tenant_recovery_contact_tenant_contact UNIQUE(tenant_id,contact_id);
CREATE TABLE impact.recovery_channel_challenge(
 tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 challenge_id uuid NOT NULL,
 contact_id uuid NOT NULL,
 contact_revision uuid NOT NULL,
 requested_by uuid NOT NULL REFERENCES impact.auth_identity,
 email_hash bytea NOT NULL CHECK(octet_length(email_hash)=32),
 code_hash bytea NOT NULL CHECK(octet_length(code_hash)=32),
 state varchar(16) NOT NULL CHECK(state IN ('PENDING','VERIFIED','EXPIRED','FAILED','SUPERSEDED')),
 attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5),
 created_at timestamptz NOT NULL DEFAULT now(), expires_at timestamptz NOT NULL,
 consumed_at timestamptz,
 PRIMARY KEY(tenant_id,challenge_id),
 FOREIGN KEY(tenant_id,contact_id) REFERENCES impact.tenant_recovery_contact(tenant_id,contact_id),
 CHECK(expires_at>created_at AND expires_at<=created_at+interval '1 hour'),
 CHECK((state='VERIFIED')=(consumed_at IS NOT NULL))
);
CREATE UNIQUE INDEX recovery_channel_one_pending ON impact.recovery_channel_challenge(contact_id) WHERE state='PENDING';
-- Serves the request rate limit (a few challenges per contact per hour).
CREATE INDEX recovery_channel_recent ON impact.recovery_channel_challenge(tenant_id,contact_id,created_at);
ALTER TABLE impact.recovery_channel_challenge ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.recovery_channel_challenge FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.recovery_channel_challenge USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.recovery_channel_challenge TO impact_platform;
GRANT SELECT ON impact.recovery_channel_challenge TO impact_worker;

-- The control plane may not write the tenant outbox; this function records exactly one email
-- intent for a pending challenge of the current tenant and nothing else.
CREATE FUNCTION impact.enqueue_recovery_channel_delivery(requested_challenge uuid, sealed bytea) RETURNS uuid
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE tenant uuid := impact.current_tenant(); event uuid := gen_random_uuid();
BEGIN
 IF tenant IS NULL OR NOT EXISTS(SELECT 1 FROM impact.recovery_channel_challenge WHERE tenant_id=tenant
  AND challenge_id=requested_challenge AND state='PENDING' AND expires_at>now()) THEN
  RAISE EXCEPTION 'challenge not pending' USING ERRCODE='42501';
 END IF;
 INSERT INTO impact.outbox_event(tenant_id,event_id,event_type,occurred_at,payload) VALUES(tenant,event,
  'delivery.requested',now(),jsonb_build_object('event_id',event,'tenant_id',tenant,'event_type','delivery.requested',
  'schema_version','1.0','channel','EMAIL','template','RECOVERY_CHANNEL_VERIFICATION',
  'reference_id',requested_challenge,'reference_generation',NULL,'occurred_at',now()));
 INSERT INTO impact.outbox_delivery(tenant_id,event_id,channel,template,reference_id,recipient_sealed)
  VALUES(tenant,event,'EMAIL','RECOVERY_CHANNEL_VERIFICATION',requested_challenge,sealed);
 RETURN event;
END $$;
REVOKE ALL ON FUNCTION impact.enqueue_recovery_channel_delivery(uuid,bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.enqueue_recovery_channel_delivery(uuid,bytea) TO impact_platform;

-- The worker discovers which tenants to visit without reading any tenant row: identifiers, lifecycle
-- state and due counts only. Everything else happens in a per-tenant transaction under tenant_fence.
-- Provisioning and Suspended tenants are listed because recovery-contact verification belongs to
-- activation and reactivation; a suspension holds (held_at) what was queued before it. A held row
-- whose lease has expired counts as due so that the worker returns it to PENDING (still held, never
-- sent): a suspension never leaves a row LEASED for ever and never replays it (v0.10 semantics).
CREATE POLICY worker_tenant_directory ON impact.tenant_root FOR SELECT TO impact_owner USING(true);
CREATE POLICY worker_dispatch_directory ON impact.outbox_delivery FOR SELECT TO impact_owner USING(true);
CREATE FUNCTION impact.worker_tenants(at timestamptz)
 RETURNS TABLE(tenant_id uuid, lifecycle_state text, due_deliveries bigint)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT t.tenant_id,t.lifecycle_state,(SELECT count(*) FROM impact.outbox_delivery d WHERE d.tenant_id=t.tenant_id
  AND d.channel IS NOT NULL AND ((d.held_at IS NULL AND d.state='PENDING' AND d.next_attempt_at<=at)
  OR (d.state='LEASED' AND d.lease_expires_at<=at)))
 FROM impact.tenant_root t WHERE t.lifecycle_state IN ('Provisioning','Active','Suspended') ORDER BY t.tenant_id
$$;
REVOKE ALL ON FUNCTION impact.worker_tenants(timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.worker_tenants(timestamptz) TO impact_worker;

-- What the worker reads and writes beyond migration 0003's grants.
GRANT SELECT ON impact.member_invitation,impact.grant_authority TO impact_worker;

-- Operator liveness signal: one row per worker process, no tenant data.
CREATE TABLE impact.worker_heartbeat(
 worker_id varchar(128) PRIMARY KEY CHECK(worker_id ~ '^[A-Za-z0-9._:-]{1,128}$'),
 build varchar(32) NOT NULL, state varchar(16) NOT NULL CHECK(state IN ('RUNNING','STOPPING','STOPPED')),
 started_at timestamptz NOT NULL, beat_at timestamptz NOT NULL, stopped_at timestamptz,
 iterations bigint NOT NULL DEFAULT 0 CHECK(iterations>=0),
 sent bigint NOT NULL DEFAULT 0 CHECK(sent>=0), retried bigint NOT NULL DEFAULT 0 CHECK(retried>=0),
 dead bigint NOT NULL DEFAULT 0 CHECK(dead>=0),
 failures bigint NOT NULL DEFAULT 0 CHECK(failures>=0),
 CHECK((state='STOPPED')=(stopped_at IS NOT NULL))
);
GRANT SELECT,INSERT,UPDATE ON impact.worker_heartbeat TO impact_worker;
GRANT SELECT ON impact.worker_heartbeat TO impact_platform;

-- One row per delegated-authority reminder the worker has created: (principal, expiry instant,
-- threshold in days). The scan excludes these in SQL, so its batch limit cannot starve later groups.
CREATE TABLE impact.authority_reminder(
 tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
 principal_id uuid NOT NULL, expires_at timestamptz NOT NULL,
 threshold_days integer NOT NULL CHECK(threshold_days IN (3,14)),
 notification_id uuid NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant_id,principal_id,expires_at,threshold_days),
 FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,notification_id) REFERENCES impact.notification_current(tenant_id,object_id)
);
ALTER TABLE impact.authority_reminder ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.authority_reminder FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.authority_reminder USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.authority_reminder TO impact_worker;

-- The operator's suspension preview counts only dispatchable intents that are still open: legacy
-- object.changed rows (never dispatched) and SENT/DEAD/SUPERSEDED rows are not unsent work.
CREATE OR REPLACE FUNCTION impact.tenant_work_impact(requested_tenant uuid) RETURNS jsonb
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() THEN RAISE EXCEPTION 'tenant denied' USING ERRCODE='42501'; END IF;
 RETURN jsonb_build_object(
 'unfinished_jobs',(SELECT count(*) FROM impact.job WHERE tenant_id=requested_tenant AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled')),
 'active_schedules',(SELECT count(*) FROM impact.object_registry WHERE tenant_id=requested_tenant AND object_type='Schedule' AND lifecycle_state='Active'),
 'unsent_events',(SELECT count(*) FROM impact.outbox_delivery WHERE tenant_id=requested_tenant AND channel IS NOT NULL AND state IN ('PENDING','LEASED')),
 'retention_holds',(SELECT count(*) FROM impact.retention_hold WHERE tenant_id=requested_tenant AND released_at IS NULL));
END $$;
COMMIT;
```

### 0019 results framework

Source: infrastructure/migrations/0019_results_framework.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Results framework and planning (v0.18). Framework and Target have been registry kinds with typed
-- projections since 0002; this migration adds the payload columns the implemented contract writes
-- and two insert-only registers of independently approved baselines. A register row is written only
-- in the approval transaction; a later change is a new row that names the revision it supersedes,
-- so an approved revision is never re-pointed and each revision can be superseded exactly once.
ALTER TABLE impact.framework_current
 ADD COLUMN effective_from timestamptz,
 ADD COLUMN supersedes_revision uuid,
 ADD COLUMN supersedes_revision_kind text GENERATED ALWAYS AS ('Framework') STORED,
 ADD COLUMN exceptions jsonb CHECK(exceptions IS NULL OR jsonb_typeof(exceptions)='array'),
 ADD CONSTRAINT framework_supersedes_fk FOREIGN KEY(tenant_id,supersedes_revision,supersedes_revision_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE impact.target_current
 ADD COLUMN indicator_id uuid,
 ADD COLUMN indicator_id_kind text GENERATED ALWAYS AS ('IndicatorInstance') STORED,
 ADD COLUMN milestone_label varchar(200),
 ADD COLUMN due_at timestamptz,
 ADD COLUMN supersedes_revision uuid,
 ADD COLUMN supersedes_revision_kind text GENERATED ALWAYS AS ('Target') STORED,
 ADD COLUMN reason text,
 ADD CONSTRAINT target_indicator_fk FOREIGN KEY(tenant_id,indicator_id,indicator_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 ADD CONSTRAINT target_supersedes_fk FOREIGN KEY(tenant_id,supersedes_revision,supersedes_revision_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 -- A blank target is never zero: only a PRESENT target carries a value or bounds.
 -- A row without a value state carries no value either.
 ADD CONSTRAINT target_blank_is_not_zero CHECK((value_state IS NOT NULL AND value_state='PRESENT')
  OR (value IS NULL AND low IS NULL AND high IS NULL));

CREATE TABLE impact.framework_baseline(
  tenant_id uuid NOT NULL,
  programme_id uuid NOT NULL,
  baseline_version integer NOT NULL CHECK(baseline_version>0),
  framework_id uuid NOT NULL,
  framework_revision uuid NOT NULL,
  supersedes_revision uuid,
  effective_from timestamptz NOT NULL,
  workflow_id uuid NOT NULL,
  approved_by uuid NOT NULL,
  approved_at timestamptz NOT NULL,
  framework_revision_kind text GENERATED ALWAYS AS ('Framework') STORED,
  workflow_kind text GENERATED ALWAYS AS ('Workflow') STORED,
  PRIMARY KEY(tenant_id,programme_id,baseline_version),
  UNIQUE(tenant_id,framework_revision),
  UNIQUE(tenant_id,programme_id,framework_revision),
  UNIQUE(tenant_id,supersedes_revision),
  CHECK((baseline_version=1)=(supersedes_revision IS NULL)),
  FOREIGN KEY(tenant_id,programme_id) REFERENCES impact.programme_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,framework_id,framework_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,framework_revision,framework_revision_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,programme_id,supersedes_revision) REFERENCES impact.framework_baseline(tenant_id,programme_id,framework_revision),
  FOREIGN KEY(tenant_id,workflow_id,workflow_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,approved_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE TABLE impact.target_binding(
  tenant_id uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  slot varchar(220) NOT NULL CHECK(slot IN ('TARGET','BASELINE') OR slot LIKE 'MILESTONE:_%'),
  binding_version integer NOT NULL CHECK(binding_version>0),
  target_id uuid NOT NULL,
  target_revision uuid NOT NULL,
  supersedes_revision uuid,
  workflow_id uuid NOT NULL,
  approved_by uuid NOT NULL,
  approved_at timestamptz NOT NULL,
  target_revision_kind text GENERATED ALWAYS AS ('Target') STORED,
  workflow_kind text GENERATED ALWAYS AS ('Workflow') STORED,
  PRIMARY KEY(tenant_id,indicator_id,period_id,slot,binding_version),
  UNIQUE(tenant_id,target_revision),
  UNIQUE(tenant_id,indicator_id,period_id,slot,target_revision),
  UNIQUE(tenant_id,supersedes_revision),
  CHECK((binding_version=1)=(supersedes_revision IS NULL)),
  FOREIGN KEY(tenant_id,indicator_id) REFERENCES impact.indicator_instance_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,period_id) REFERENCES impact.period_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,target_id,target_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,target_revision,target_revision_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,indicator_id,period_id,slot,supersedes_revision)
    REFERENCES impact.target_binding(tenant_id,indicator_id,period_id,slot,target_revision),
  FOREIGN KEY(tenant_id,workflow_id,workflow_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,approved_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX target_binding_period ON impact.target_binding(tenant_id,period_id);
ALTER TABLE impact.framework_baseline ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.framework_baseline FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.target_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.target_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.framework_baseline USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.target_binding USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Insert-only for the application; nothing for the control plane.
GRANT SELECT,INSERT ON impact.framework_baseline,impact.target_binding TO impact_app;
COMMIT;
```

### 0020 calculation methods

Source: infrastructure/migrations/0020_calculation_methods.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Indicator and calculation completion (v0.19). The approved definition pins its disaggregation
-- scheme and a calculated result carries its category breakdown; both are payload properties that
-- the typed projections must hold. Additive columns only: no row is rewritten and no policy, grant
-- or role changes (both projections keep their existing RLS policies and grants).
ALTER TABLE impact.indicator_definition_current
 ADD COLUMN disaggregation jsonb CHECK(disaggregation IS NULL OR jsonb_typeof(disaggregation)='object');
ALTER TABLE impact.calculated_result_current
 ADD COLUMN disaggregation jsonb CHECK(disaggregation IS NULL OR jsonb_typeof(disaggregation)='array');
COMMIT;
```

### 0021 web forms

Source: infrastructure/migrations/0021_web_forms.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Web forms (v0.20). Form and Submission have been registry kinds with typed projections since
-- 0002; this migration adds the payload columns the implemented contract writes and one insert-only
-- register of published form versions. A register row is written only by the publish command, after
-- an independent approval of the exact revision; a later version is a new row naming the revision it
-- supersedes, so a published version is never re-pointed and each version is superseded at most once.
ALTER TABLE impact.form_current
 ADD COLUMN programme_id uuid,
 ADD COLUMN programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
 ADD CONSTRAINT form_programme_fk FOREIGN KEY(tenant_id,programme_id,programme_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE impact.submission_current
 ADD COLUMN observation_ids jsonb CHECK(observation_ids IS NULL OR jsonb_typeof(observation_ids)='array'),
 ADD COLUMN quarantine_reason varchar(64),
 ADD COLUMN unit_key varchar(100);

CREATE TABLE impact.form_publication(
  tenant_id uuid NOT NULL,
  form_id uuid NOT NULL,
  version_number integer NOT NULL CHECK(version_number>0),
  form_revision uuid NOT NULL,
  approved_revision uuid NOT NULL,
  supersedes_revision uuid,
  published_by uuid NOT NULL,
  published_at timestamptz NOT NULL,
  form_revision_kind text GENERATED ALWAYS AS ('Form') STORED,
  PRIMARY KEY(tenant_id,form_id,version_number),
  UNIQUE(tenant_id,form_revision),
  UNIQUE(tenant_id,form_id,form_revision),
  UNIQUE(tenant_id,supersedes_revision),
  CHECK((version_number=1)=(supersedes_revision IS NULL)),
  FOREIGN KEY(tenant_id,form_id,form_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,form_revision,form_revision_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,form_id,approved_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,form_id,supersedes_revision) REFERENCES impact.form_publication(tenant_id,form_id,form_revision),
  FOREIGN KEY(tenant_id,published_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.form_publication ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.form_publication FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.form_publication USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Insert-only for the application; nothing for the control plane.
GRANT SELECT,INSERT ON impact.form_publication TO impact_app;
COMMIT;
```

### 0022 import quality

Source: infrastructure/migrations/0022_import_quality.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Import and data quality (v0.21). ImportJob has been a registry kind with a typed projection since
-- 0002; this migration adds the payload columns the implemented import batch writes (the bounded
-- source file carried in the request, its mapping to indicator instances, unit and period, the
-- staged row outcomes with their quality checks, and the commit manifest) and one insert-only
-- register that makes "this unit already reported this indicator for this period through an
-- import" a database fact. A register row is written only by the commit of an independently
-- staged batch, in the same transaction as the observation it names; it is never updated or
-- deleted, so a second batch for the same unit, indicator and period is a duplicate.
ALTER TABLE impact.import_job_current
 ADD COLUMN programme_id uuid,
 ADD COLUMN programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
 ADD COLUMN period_id uuid,
 ADD COLUMN period_id_kind text GENERATED ALWAYS AS ('Period') STORED,
 ADD COLUMN format varchar(16) CHECK(format IS NULL OR format IN ('CSV','XLSX')),
 ADD COLUMN file_name varchar(200),
 ADD COLUMN content text,
 ADD COLUMN content_sha256 varchar(64) CHECK(content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$'),
 ADD COLUMN received_at timestamptz,
 ADD COLUMN mapping jsonb CHECK(mapping IS NULL OR jsonb_typeof(mapping)='object'),
 ADD COLUMN preview jsonb CHECK(preview IS NULL OR jsonb_typeof(preview)='object'),
 ADD COLUMN committed jsonb CHECK(committed IS NULL OR jsonb_typeof(committed)='object'),
 ADD COLUMN cancel_reason text,
 ADD CONSTRAINT import_job_programme_fk FOREIGN KEY(tenant_id,programme_id,programme_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 ADD CONSTRAINT import_job_period_fk FOREIGN KEY(tenant_id,period_id,period_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE impact.import_unit_register(
  tenant_id uuid NOT NULL,
  indicator_id uuid NOT NULL,
  period_id uuid NOT NULL,
  unit_key varchar(100) NOT NULL CHECK(unit_key ~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$'),
  observation_id uuid NOT NULL,
  import_id uuid NOT NULL,
  import_revision uuid NOT NULL,
  row_number integer NOT NULL CHECK(row_number>1),
  registered_by uuid NOT NULL,
  registered_at timestamptz NOT NULL,
  indicator_id_kind text GENERATED ALWAYS AS ('IndicatorInstance') STORED,
  period_id_kind text GENERATED ALWAYS AS ('Period') STORED,
  observation_id_kind text GENERATED ALWAYS AS ('Observation') STORED,
  import_id_kind text GENERATED ALWAYS AS ('ImportJob') STORED,
  PRIMARY KEY(tenant_id,indicator_id,period_id,unit_key),
  UNIQUE(tenant_id,observation_id),
  FOREIGN KEY(tenant_id,indicator_id,indicator_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,period_id,period_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,observation_id,observation_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,import_id,import_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
  FOREIGN KEY(tenant_id,import_id,import_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,registered_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX import_unit_register_import ON impact.import_unit_register(tenant_id,import_id);
ALTER TABLE impact.import_unit_register ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.import_unit_register FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.import_unit_register USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Insert-only for the application; nothing for the worker or the control plane.
GRANT SELECT,INSERT ON impact.import_unit_register TO impact_app;
COMMIT;
```

### 0023 evidence objects

Source: infrastructure/migrations/0023_evidence_objects.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Object store and evidence attachments (v0.22). upload_session, file_blob and evidence_current have
-- existed since 0002 with tenant fences (0003); this migration adds the columns the implemented
-- upload, scan and evidence commands write, transition guards on the two upload tables, and three
-- insert-only registers: upload events, evidence attachments (an evidence revision cited by an exact
-- observation or calculated-result revision) and evidence content access (one row per mediated
-- download). The bytes themselves live outside the database in a private, content-addressed object
-- store; file_blob holds the SHA-256, size, object key and scan verdict. Additive only: no row is
-- rewritten, and no existing grant, policy or role changes.
ALTER TABLE impact.file_blob
 ADD COLUMN created_at timestamptz,
 ADD COLUMN scanned_at timestamptz,
 ADD COLUMN scanner varchar(64),
 ADD COLUMN scan_detail varchar(64);
ALTER TABLE impact.upload_session
 ADD COLUMN filename varchar(200),
 ADD COLUMN media_type varchar(64),
 ADD COLUMN blob_id uuid,
 ADD COLUMN created_at timestamptz,
 ADD COLUMN content_received_at timestamptz,
 ADD COLUMN completed_at timestamptz,
 ADD CONSTRAINT upload_session_blob_fk FOREIGN KEY(tenant_id,blob_id) REFERENCES impact.file_blob(tenant_id,blob_id);
ALTER TABLE impact.evidence_current
 ADD COLUMN filename varchar(200),
 ADD COLUMN media_type varchar(64),
 ADD COLUMN byte_size bigint CHECK(byte_size IS NULL OR byte_size>0);

-- A blob's identity (key, digest, size) never changes, and a verdict is final: QUARANTINED ->
-- SCANNING -> CLEAN | INFECTED | FAILED, with FAILED -> SCANNING for a retried scan. CLEAN and
-- INFECTED are never rewritten by any role.
CREATE FUNCTION impact.file_blob_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
  IF NEW.tenant_id<>OLD.tenant_id OR NEW.blob_id<>OLD.blob_id OR NEW.object_key<>OLD.object_key
     OR NEW.sha256<>OLD.sha256 OR NEW.bytes<>OLD.bytes THEN
    RAISE EXCEPTION 'file_blob identity is immutable' USING ERRCODE='23514';
  END IF;
  IF NEW.scan_state<>OLD.scan_state AND NOT (
       (OLD.scan_state='QUARANTINED' AND NEW.scan_state='SCANNING')
    OR (OLD.scan_state='FAILED' AND NEW.scan_state='SCANNING')
    OR (OLD.scan_state='SCANNING' AND NEW.scan_state IN ('CLEAN','INFECTED','FAILED'))) THEN
    RAISE EXCEPTION 'file_blob scan transition refused' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER file_blob_guard BEFORE UPDATE ON impact.file_blob FOR EACH ROW EXECUTE FUNCTION impact.file_blob_guard();
REVOKE ALL ON FUNCTION impact.file_blob_guard() FROM PUBLIC;

-- An upload's declaration (owner, purpose, size, digest, name, media type) is fixed at creation and
-- its received blob is bound once.
CREATE FUNCTION impact.upload_session_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
  IF NEW.tenant_id<>OLD.tenant_id OR NEW.upload_id<>OLD.upload_id OR NEW.owner_id<>OLD.owner_id
     OR NEW.purpose<>OLD.purpose OR NEW.mode<>OLD.mode OR NEW.expected_bytes<>OLD.expected_bytes
     OR NEW.expected_digest<>OLD.expected_digest
     OR NEW.filename IS DISTINCT FROM OLD.filename OR NEW.media_type IS DISTINCT FROM OLD.media_type
     OR (OLD.blob_id IS NOT NULL AND NEW.blob_id IS DISTINCT FROM OLD.blob_id) THEN
    RAISE EXCEPTION 'upload_session declaration is immutable' USING ERRCODE='23514';
  END IF;
  IF OLD.state IN ('CLEAN','REJECTED','CANCELLED','EXPIRED') AND NEW.state<>OLD.state THEN
    RAISE EXCEPTION 'upload_session terminal state is final' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER upload_session_guard BEFORE UPDATE ON impact.upload_session FOR EACH ROW EXECUTE FUNCTION impact.upload_session_guard();
REVOKE ALL ON FUNCTION impact.upload_session_guard() FROM PUBLIC;

-- One evidence revision cited by one exact revision of an observation or calculated result. The
-- cited record is not changed (an approved record stays immutable); a later revision of either side
-- is a new citation. Never updated or deleted.
CREATE TABLE impact.evidence_attachment(
  tenant_id uuid NOT NULL,
  attachment_id uuid NOT NULL,
  evidence_id uuid NOT NULL,
  evidence_revision uuid NOT NULL,
  evidence_revision_kind text GENERATED ALWAYS AS ('Evidence') STORED,
  target_id uuid NOT NULL,
  target_revision uuid NOT NULL,
  target_type text NOT NULL CHECK(target_type IN ('Observation','CalculatedResult')),
  reason text NOT NULL CHECK(char_length(reason) BETWEEN 1 AND 2000),
  attached_by uuid NOT NULL,
  attached_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,attachment_id),
  UNIQUE(tenant_id,evidence_revision,target_revision),
  FOREIGN KEY(tenant_id,evidence_id,evidence_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,evidence_revision,evidence_revision_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,target_id,target_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,target_revision,target_type) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,attached_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX evidence_attachment_target ON impact.evidence_attachment(tenant_id,target_id,attached_at);

-- One row per mediated content response: who read which evidence revision's bytes, when, under which
-- correlation. Never updated or deleted.
CREATE TABLE impact.evidence_access(
  tenant_id uuid NOT NULL,
  access_id uuid NOT NULL,
  evidence_id uuid NOT NULL,
  evidence_revision uuid NOT NULL,
  blob_id uuid NOT NULL,
  principal_id uuid NOT NULL,
  membership_id uuid NOT NULL,
  accessed_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,access_id),
  FOREIGN KEY(tenant_id,evidence_id,evidence_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,blob_id) REFERENCES impact.file_blob(tenant_id,blob_id),
  FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX evidence_access_evidence ON impact.evidence_access(tenant_id,evidence_id,accessed_at);

-- The history of an upload session (create, content received, sealed, scan verdict): upload sessions
-- are not registry objects, so an audit event cannot reference them; this register links each
-- audited action to its upload. Never updated or deleted.
CREATE TABLE impact.upload_event(
  tenant_id uuid NOT NULL,
  event_id uuid NOT NULL,
  upload_id uuid NOT NULL,
  action varchar(64) NOT NULL,
  outcome varchar(64) NOT NULL,
  actor_id uuid NOT NULL,
  occurred_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,event_id),
  FOREIGN KEY(tenant_id,upload_id) REFERENCES impact.upload_session(tenant_id,upload_id),
  FOREIGN KEY(tenant_id,actor_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX upload_event_upload ON impact.upload_event(tenant_id,upload_id,occurred_at);

ALTER TABLE impact.upload_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.upload_event FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.upload_event USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.evidence_attachment ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.evidence_attachment FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.evidence_attachment USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.evidence_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.evidence_access FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.evidence_access USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Insert-only for the application; nothing for the worker, identity or control plane.
GRANT SELECT,INSERT ON impact.evidence_attachment TO impact_app;
GRANT SELECT,INSERT ON impact.evidence_access TO impact_app;
GRANT SELECT,INSERT ON impact.upload_event TO impact_app;
COMMIT;
```

### 0024 report exports

Source: infrastructure/migrations/0024_report_exports.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Report exports (v0.23): PDF, XLSX and DOCX renderings of an approved, frozen report package,
-- produced by the worker as its first executed job class. A request writes one impact.job row
-- (job_class REPORT_EXPORT, state Queued) and one report_export row in the business transaction;
-- the worker claims due rows under a generation-fenced lease on the database clock, renders outside
-- any transaction and stores the artifact in a fenced outcome transaction. Artifacts are insert-only
-- and immutable; a disclosure binds the exact artifacts it was approved with, never re-pointed.
-- Nothing here depends on migrations 0022, 0023 or 0025.

-- Server-resolved export artifacts a disclosure names (the requester names formats; the server pins
-- each to the exact artifact before review). Payload columns of the Disclosure projection.
ALTER TABLE impact.disclosure_current
 ADD COLUMN export_formats jsonb CHECK(export_formats IS NULL OR jsonb_typeof(export_formats)='array'),
 ADD COLUMN export_artifacts jsonb CHECK(export_artifacts IS NULL OR jsonb_typeof(export_artifacts)='array');

-- The export-specific lease state of a REPORT_EXPORT job. The job row carries the lifecycle state,
-- lease generation, lease expiry and cancellation request; this row the pinned package, the lease
-- owner, attempts, backoff and the error class (never a message).
CREATE TABLE impact.report_export(
  tenant_id uuid NOT NULL,
  job_id uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  report_revision_kind text GENERATED ALWAYS AS ('Report') STORED,
  format text NOT NULL CHECK(format IN ('PDF','XLSX','DOCX')),
  renderer_version varchar(32) NOT NULL CHECK(renderer_version ~ '^[a-z0-9.-]{1,32}$'),
  reconciliation_digest bytea NOT NULL CHECK(octet_length(reconciliation_digest)=32),
  requested_by uuid NOT NULL,
  requested_at timestamptz NOT NULL,
  attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
  next_attempt_at timestamptz NOT NULL,
  lease_owner varchar(128) CHECK(lease_owner ~ '^[A-Za-z0-9._:-]{1,128}$'),
  last_attempt_at timestamptz,
  last_error_class varchar(64) CHECK(last_error_class ~ '^[A-Z0-9_]{1,64}$'),
  completed_at timestamptz,
  PRIMARY KEY(tenant_id,job_id),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.job(tenant_id,job_id),
  FOREIGN KEY(tenant_id,report_id,report_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,report_revision,report_revision_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,report_id,report_revision) REFERENCES impact.report_package_binding(tenant_id,report_id,report_revision),
  FOREIGN KEY(tenant_id,requested_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX report_export_report ON impact.report_export(tenant_id,report_id,report_revision,format);
CREATE INDEX report_export_due ON impact.report_export(tenant_id,next_attempt_at) WHERE completed_at IS NULL;

-- One immutable artifact per successful export job: written once by the worker's fenced outcome.
CREATE TABLE impact.report_export_artifact(
  tenant_id uuid NOT NULL,
  job_id uuid NOT NULL,
  report_id uuid NOT NULL,
  report_revision uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('PDF','XLSX','DOCX')),
  renderer_version varchar(32) NOT NULL,
  media_type text NOT NULL,
  body bytea NOT NULL CHECK(octet_length(body) BETWEEN 1 AND 10485760),
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  lease_generation bigint NOT NULL CHECK(lease_generation>0),
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,job_id),
  CHECK((format='PDF' AND media_type='application/pdf')
    OR (format='XLSX' AND media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    OR (format='DOCX' AND media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.report_export(tenant_id,job_id),
  FOREIGN KEY(tenant_id,report_id,report_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id)
);

-- The export artifacts a published disclosure delivers: one row per format, written in the publish
-- transaction from the artifacts the reviewed disclosure pinned, never re-pointed.
CREATE TABLE impact.report_publication_export(
  tenant_id uuid NOT NULL,
  disclosure_id uuid NOT NULL,
  disclosure_revision uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('PDF','XLSX','DOCX')),
  job_id uuid NOT NULL,
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  created_at timestamptz NOT NULL,
  PRIMARY KEY(tenant_id,disclosure_id,format),
  FOREIGN KEY(tenant_id,disclosure_id,disclosure_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.report_export_artifact(tenant_id,job_id)
);

-- Every mediated download of an export artifact: internal (report.export) or by a named recipient.
CREATE TABLE impact.report_export_access(
  tenant_id uuid NOT NULL,
  access_id uuid NOT NULL,
  job_id uuid NOT NULL,
  disclosure_id uuid,
  principal_id uuid NOT NULL,
  membership_id uuid NOT NULL,
  format text NOT NULL CHECK(format IN ('PDF','XLSX','DOCX')),
  access_mode text NOT NULL CHECK(access_mode IN ('INTERNAL_DOWNLOAD','RECIPIENT_DOWNLOAD')),
  accessed_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,access_id),
  CHECK((disclosure_id IS NULL)=(access_mode='INTERNAL_DOWNLOAD')),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.report_export_artifact(tenant_id,job_id),
  FOREIGN KEY(tenant_id,disclosure_id) REFERENCES impact.disclosure_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
  FOREIGN KEY(tenant_id,membership_id) REFERENCES impact.membership_current(tenant_id,object_id)
);

ALTER TABLE impact.report_export ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export_artifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export_artifact FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_export ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_publication_export FORCE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.report_export_access FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.report_export USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.report_export_artifact USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.report_publication_export USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
CREATE POLICY tenant_fence ON impact.report_export_access USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

-- The worker's directory of tenants with due export jobs (identifiers and counts only), read by the
-- definer through owner-only SELECT policies, as impact.worker_tenants reads outbox_delivery (0018).
CREATE POLICY worker_export_directory ON impact.job FOR SELECT TO impact_owner USING(true);
CREATE POLICY worker_export_directory ON impact.report_export FOR SELECT TO impact_owner USING(true);
CREATE FUNCTION impact.worker_export_tenants(at timestamptz)
 RETURNS TABLE(tenant_id uuid, due_exports bigint)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
SELECT t.tenant_id,count(*) FROM impact.tenant_root t
 JOIN impact.job j ON j.tenant_id=t.tenant_id AND j.job_class='REPORT_EXPORT'
 JOIN impact.report_export e ON e.tenant_id=j.tenant_id AND e.job_id=j.job_id
 WHERE t.lifecycle_state='Active'
  AND ((j.state='Queued' AND j.cancellation_requested_at IS NULL AND e.next_attempt_at<=at)
   OR (j.state='Running' AND j.lease_expires_at<=at))
 GROUP BY t.tenant_id ORDER BY t.tenant_id
$$;
REVOKE ALL ON FUNCTION impact.worker_export_tenants(timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.worker_export_tenants(timestamptz) TO impact_worker;

-- Application: request, status, internal download, publication binding and access log.
GRANT SELECT,INSERT ON impact.report_export TO impact_app;
GRANT SELECT ON impact.report_export_artifact TO impact_app;
GRANT SELECT,INSERT ON impact.report_publication_export TO impact_app;
GRANT INSERT ON impact.report_export_access TO impact_app;

-- Worker: exactly what export execution needs, stated explicitly so that a later narrowing of the
-- broad 0003 worker grants can keep them (job and job_item are also granted by 0003).
GRANT SELECT,UPDATE ON impact.job TO impact_worker;
GRANT SELECT,INSERT ON impact.job_item TO impact_worker;
GRANT SELECT,UPDATE ON impact.report_export TO impact_worker;
GRANT SELECT,INSERT ON impact.report_export_artifact TO impact_worker;
GRANT SELECT ON impact.report_package_binding,impact.object_revision TO impact_worker;
COMMIT;
```
