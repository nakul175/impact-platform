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