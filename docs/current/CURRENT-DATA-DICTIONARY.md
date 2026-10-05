# Current data dictionary and schema evolution

Local proposed build 0.33.0, schema 39: migration0039 narrows the central participant helper to require the exact tenant/object/revision/type-qualified AI adoption plan anchor to remain AVAILABLE, in addition to its currently readable head. Earlier unavailable plan pins now withhold all case-related projections and pointer reads without changing old rows or roles. Migration0038 adds an existing-member human advice case projection and immutable private brief, tenant-qualified keys and forced participant row security. Invitation details and explicit sharing consent precede material adviser access; terminal adviser access ends. Narrow owner-definer helpers protect case-related registry/revision, audit, author, receipt and event pointers. The writable transaction-local principal context supports the authenticated application boundary and does not authenticate a human against a compromised database login. Programme evidence links reuse existing immutable AI-plan revisions without a new numeric-result table. Not merged or deployed.

Local proposed build 0.32.0, schema 37: migration 0036 adds reviewed access-extension proposals and immutable application markers, forced tenant row security, an immutable registered access-profile directory and narrowly granted control-plane review/application functions. Existing tenants retain revoked capabilities, managed-role omissions and expiry dates; only the newly introduced registered-profile delta can be approved. Migration 0037 adds insert-only tenant-fenced AI guidance bundles and exact adoption-plan revision bindings, SELECT/INSERT for `impact_app` only. Retained archive schemas and verified content hashes preserve actual historical wording; missing historical text remains unavailable. Not merged or deployed.

Local proposed build 0.30.0, schema 35: migration 0034 adds insert-only, forced-RLS AI advisory request/result registers. Only `impact_app` receives SELECT/INSERT; drafts are sealed, server-generated record IDs are independent from operation IDs. Migration 0035 adds the AIAdoptionPlan registry kind, using existing immutable tenant-fenced revisions and receipts without widening database-role grants. Not merged or deployed.

Proposed build 0.28.0, schema 33 (PR 1, not merged): 0033 adds the application executor's
tenant-fenced `import_commit` register, its due-tenant directory and an operational heartbeat.
The executor login is separately provisioned with membership in `impact_app` only. No
`impact_worker` privilege changes. The migration remains additive to deployed schema 32.

Build 0.27.0; schema 32 (integrated 3 October 2026 on branch `integration/0.27`; the four v0.27 slices each numbered their migration 0029 locally and were renumbered in merge order by renaming the files only, so their bytes and SHA-256 values are those the slices recorded). 0029 (operator lifecycle, PR #72) adds `platform_operator.revision_id` and `updated_at` with the guard trigger `guard_platform_operator` (identity immutable; every update refreshes the revision), widens the CHECK `platform_event_tenant_scope` to the tenant-less actions `operator-renew` and `operator-deactivate`, adds the insert-only register `platform_operator_change` (who renewed or deactivated whom, from which revision and expiry to which, the actor's assurance instant and reason; SELECT to `impact_platform` only) and the SECURITY DEFINER `apply_operator_change` (EXECUTE to `impact_platform` only): the only run-time writer of `platform_operator` besides `accept_operator_nomination` — the actor must be an active operator other than the subject and of another natural person, the subject at the expected revision and still active and unexpired, a renewal later than the current expiry and at most 365 days ahead, a deactivation leaving at least one other active operator. 0030 (security and privacy, PR #74) adds `access_denial` (collapsed refused authorisations per tenant, principal, operation, reason and 300-second window with an occurrence counter; written only through the SECURITY DEFINER `record_access_denial`, which also folds a principal's denials beyond a per-window cap into one overflow row; `impact_app` holds SELECT only; the trigger `access_denial_guard` lets only the counter and the last-seen fields advance), the insert-only `audit_export_register` (one row per exported audit page: principal, purpose, reason, window, page, counts, content digest, chain start and end, seal key id; keyed by the export's AuditEvent; `impact_app` SELECT/INSERT), the approval columns of `retention_policy_current` (reason, approved_by/at/revision, supersedes_revision with a typed foreign key) and the insert-only `retention_policy_binding` (one row per independently approved policy revision; `impact_app` SELECT/INSERT, `impact_worker` SELECT), the hold columns of `retention_hold` (reason, placed_by/at, released_by, release_reason; CHECK `retention_hold_release`) with the trigger `retention_hold_guard` (immutable except for one release, a released hold final), and the worker definers `retention_purge_receipts(integer,integer)` (a policy can only lengthen the 7-day receipt window) and `retention_purge_security_events(integer,integer)` (never below the 365-day floor); all new tables with forced RLS and `tenant_fence`. Nothing is revoked or granted back. 0031 (theory of change, PR #70) adds the payload columns of this build's planning contract and nothing else: `framework_current.assumptions` (a JSON array of the assumption, risk and context records a framework revision carries beside its 0002 `relationships` column, which this build writes for the first time) and `target_current.status_thresholds` (the JSON object of reviewed status thresholds a target carries). No grant, policy, trigger or role change; the closed contract schemas validate both documents before they are written. 0032 (web forms continued, PR #73) is additive and changes no grant, role or policy: `form_current.default_language` (the language of the field definitions; the existing `translation_versions` array now carries the language versions), `submission_current.language` (the language presented to the respondent), `submission_current.correction_of_revision` and `correction_reason` (a correction of returned work names the Submitted revision it supersedes), a typed composite foreign key `submission_assignment_kind` from the existing `assignment_id` column to `object_registry`, and on `assignment_current` the columns `unit_key`, `previous_assignee_id` and `reason` with the composite foreign keys `assignment_round_kind` (to the `CollectionRound` registry row) and `assignment_assignee` (to `tenant_principal`). Collection rounds are the 0002 registry kind `CollectionRound` kept in `object_registry`/`object_revision` without a projection, as `CollectionPlan` is.

Build 0.26.0; schema 28 (v0.26a usable staging, 1 October 2026, branch `release/0.26a-usable-staging`). 0028 lets `platform_event.tenant_id` be NULL only for the tenant-less control-plane actions (`operator-nominate/cancel/decline/accept`, `account-create/reissue`; CHECK `platform_event_tenant_scope`); adds `platform_operator_nomination` (one open nomination per e-mail hash, no clear address, an immutability and finality trigger `guard_operator_nomination` that admits an acceptance only from the definer) and `provider_account` (who created which identity-provider subject for which address hash, credentials issued, never a password; UNIQUE issuer and subject), both readable and insertable by `impact_platform` only with UPDATE on a few decision columns; the SECURITY DEFINER functions `register_provider_account_identity` (the identity of a provisioned account, only for an active qualification's issuer), `accept_operator_nomination` (the only run-time writer of `platform_operator`: open, unexpired nomination, nominating operator still active, the actor's verified address, a natural person different from the nominator and from every active operator) and `tenant_pending_invitation` (whether the transaction's tenant has a pending invitation for an address hash), EXECUTE to `impact_platform` only; and replaces `apply_initial_authority` so the reviewed ceiling also covers a v2 manifest's `purpose_bound` capabilities (every other condition unchanged).

Build 0.25.0; schema 27 (integrated 1 October 2026 on branch `integration/0.25`). v0.25 part B's 0027 adds the privacy-case payload columns of `privacy_case_current` (subject membership and principal with typed foreign keys, reason, verification note, named evidence and import batches, approval, plan, execution and package fields; CHECKs on request type and outcome), the export package `privacy_export_package` (bounded body, SHA-256, expiry; SELECT/INSERT for `impact_app`, SELECT/DELETE for `impact_worker`) and the insert-only download log `privacy_export_access`, `outbox_delivery.recipient_redacted_at`, `file_blob.purged_at/purge_case_id`, the RETENTION_SWEEP lease table `retention_sweep` and the insert-only proof register `retention_proof` (all with forced RLS and `tenant_fence`); it replaces `guard_revision_removal` (adds the definer path, every other condition unchanged) and `upload_session_guard` (a file name may be cleared by the erasure definer only), and adds the SECURITY DEFINER functions `privacy_require_case` (no grantee), `privacy_remove_revisions`, `privacy_redact_uploads`, `privacy_supersede_deliveries` (EXECUTE to `impact_app`), `retention_purge_receipts`, `retention_expire_uploads` and `worker_schedule_retention` (EXECUTE to `impact_worker`). v0.25 part A and the October 2026 operations hardening add no migration.

Build 0.24.0; schema 26 (0.24.0 adds 0022: the import batch payload columns of `import_job_current` with typed composite foreign keys and the insert-only, tenant-fenced `import_unit_register`, SELECT and INSERT for `impact_app` only; 0023: upload, blob and evidence file columns, the guard triggers `file_blob_guard` and `upload_session_guard`, and the insert-only registers `evidence_attachment`, `evidence_access` and `upload_event`; 0024: disclosure export columns, `report_export`, the insert-only `report_export_artifact`, `report_publication_export` and `report_export_access`, owner-only `worker_export_directory` policies and the SECURITY DEFINER `worker_export_tenants`, with the worker's export grants; 0025: the narrowing of `impact_worker` to the tables the worker touches and the SECURITY DEFINER functions `operator_delivery_attention` and `operator_requeue_delivery` for `impact_platform`; 0026: the narrowing of `impact_worker` on `job`, `job_item`, `report_current` and `report_template_current`. 0.20.0 added 0021: `form_current.programme_id` with a typed composite foreign key, `submission_current.observation_ids/quarantine_reason/unit_key`, and the insert-only, tenant-fenced register `form_publication`, SELECT and INSERT for `impact_app` only. 0.19.0 added 0020: nullable `indicator_definition_current.disaggregation` and `calculated_result_current.disaggregation` with jsonb type CHECKs. 0.18.0 added 0019: framework and target payload columns on `framework_current` and `target_current` with typed kind columns, composite foreign keys and the CHECK `target_blank_is_not_zero`; the insert-only, tenant-fenced registers `framework_baseline` and `target_binding`, SELECT and INSERT for `impact_app` only. 0.16.0 added 0018: dispatch columns, constraints and indexes on `outbox_delivery` and the revocation of its UPDATE from `impact_app`; `notification_delivery`, `recovery_channel_challenge`, `authority_reminder` and `worker_heartbeat`; the recovery-contact channel columns and `UNIQUE(tenant_id, contact_id)`; the SECURITY DEFINER functions `enqueue_recovery_channel_delivery` and `worker_tenants`; worker grants; and a replaced `tenant_work_impact`. 0.15.0 added 0017. All twenty-six checksums below match `sha256sum` of the files and were verified by the native run, the restore drill and the upgrade check of 1 October 2026). Executable migrations are authoritative. This dictionary retains each table definition and later alteration in execution order, including constraints and role policy. JSONB domain payload fields are specified by the current OpenAPI schemas; scalar column definitions alone are not the full data model.

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
| 0025_worker_grants.sql | e15906bfddde70bc978f93785dfec60ed60ddd45d0135d351a2584bbffbc5047 |
| 0026_worker_job_grants.sql | c01bcd55621e71fd6e5bd3d11ac08f085eec8bd51efcefb25b8de11fded64310 |
| 0027_privacy_execution.sql | b7fca9754e818ded1e856c66cf4c525aa6049bab924edfbc7e5f050b728e1e9d |
| 0028_usable_staging.sql | 2a7775799ee960728e21395d3d85c4027b5fe8f7e135853c4197ef3acf6f0c1c |
| 0029_operator_lifecycle.sql | de05d78b232cfea0ec5f75479f2f374fbfd8196c0df5a4694d871b73e68d4d41 |
| 0030_security_privacy.sql | 5ea8601b29f10e1bc7d500a8f177a6aa6a95b9fcb9b094867e2c9366f453ec12 |
| 0031_theory_of_change.sql | 2b0f3736515b77fc5657470d1a95fdfd87e560f4a6a5cc758a840ee86b80b4ac |
| 0032_forms_languages_rounds.sql | 999df25fb357cf91ef227240dfde6e42145e74abc1e4bf2867c0865374389b2b |
| 0033_application_executor.sql | a0e86eda72775b6a6f14e488be51bbdbcae31ec8dc41adf8137be9860fe4fc33 |

| 0034_ai_advisory.sql | 5835d7e222cc56211463d006bd2d79411293f48f2424942babbde918cf894415 |
| 0035_ai_adoption_plans.sql | 543e3ac6c3f0317cd4792c7cb86d318baca93efd270584940f1b9e0f88c45be5 |

| 0036_reviewed_ceiling_widening.sql | 4e4bf01ebee650fb5c910c944e9ee6344f66c540d178f8c673bd54116710a464 |
| 0037_ai_content_snapshots.sql | 668f0fd4e90e3548fcea922a088976e273e9b164cbdcb12fca97f79fca126d7e |
| 0038_human_advice_cases.sql | ace70f9e77a2636df7e0cf5f85f5ffd29de74af8efa94df6e5804077e5331e00 |
| 0039_human_advice_anchor_availability.sql | 12fb7073f1f841965f6e8c5874444b48ae2da0c39f0e93dae820e7fbedd5b0f0 |

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

### 0025 worker grants

Source: infrastructure/migrations/0025_worker_grants.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Worker privileges and operator re-queue (quality hardening, October 2026).
-- Part 1 narrows impact_worker. Migration 0003 granted impact_worker the
-- same SELECT/INSERT/UPDATE as impact_app on nearly every domain table. The worker of build 0.20.0
-- (impact_api/worker.py with store.write/audit and delivery.enqueue) touches only:
--   object_registry, object_revision, notification_current, audit_event_current: reminder notices
--     and their audit events (INSERT; SELECT for the reminder scan and the audit revision number)
--   tenant_principal      SELECT, INSERT (the SERVICE principal, ON CONFLICT DO NOTHING; recipients)
--   membership_current    SELECT (reminder recipients hold an active membership)
--   outbox_event          SELECT, INSERT;  outbox_delivery  SELECT, INSERT, UPDATE
--   consumer_receipt      SELECT, INSERT (worker.in_app)
--   job, job_item         cancellation of not-started jobs
--   from 0018: notification_delivery, recovery_channel_challenge, member_invitation,
--     grant_authority, worker_heartbeat, authority_reminder and EXECUTE on worker_tenants.
-- Tenant discovery goes through the SECURITY DEFINER impact.worker_tenants, so tenant_root is not
-- needed. Everything else is revoked below, one explicit statement per table: no dynamic
-- revoke-all-then-grant, which would undo explicit grants of other migrations.
-- Deliberately not touched, left for a follow-up once report exports (0024) have settled the
-- worker's export-job privileges: job, job_item, report_current, report_template_current.
-- Foreign-key checks run as the table owner and no row-level policy reads another table, so the
-- kept privileges cover every statement the worker issues. Nothing here depends on 0022-0024.
REVOKE ALL ON impact.a_i_task_current FROM impact_worker;
REVOKE ALL ON impact.allocation_rule_current FROM impact_worker;
REVOKE ALL ON impact.assignment_current FROM impact_worker;
REVOKE ALL ON impact.audit_batch_root FROM impact_worker;
REVOKE ALL ON impact.budget_line_current FROM impact_worker;
REVOKE ALL ON impact.calculated_result_current FROM impact_worker;
REVOKE ALL ON impact.connection_current FROM impact_worker;
REVOKE ALL ON impact.dashboard_current FROM impact_worker;
REVOKE ALL ON impact.dataset_current FROM impact_worker;
REVOKE ALL ON impact.decision_current FROM impact_worker;
REVOKE ALL ON impact.deletion_ledger FROM impact_worker;
REVOKE ALL ON impact.device_current FROM impact_worker;
REVOKE ALL ON impact.dimension_current FROM impact_worker;
REVOKE ALL ON impact.disclosure_current FROM impact_worker;
REVOKE ALL ON impact.evaluation_current FROM impact_worker;
REVOKE ALL ON impact.evidence_current FROM impact_worker;
REVOKE ALL ON impact.exchange_rate_current FROM impact_worker;
REVOKE ALL ON impact.file_blob FROM impact_worker;
REVOKE ALL ON impact.finance_transaction_current FROM impact_worker;
REVOKE ALL ON impact.form_current FROM impact_worker;
REVOKE ALL ON impact.form_field_current FROM impact_worker;
REVOKE ALL ON impact.framework_current FROM impact_worker;
REVOKE ALL ON impact.funding_agreement_current FROM impact_worker;
REVOKE ALL ON impact.grant_current FROM impact_worker;
REVOKE ALL ON impact.handling_record_current FROM impact_worker;
REVOKE ALL ON impact.import_job_current FROM impact_worker;
REVOKE ALL ON impact.indicator_definition_current FROM impact_worker;
REVOKE ALL ON impact.indicator_instance_current FROM impact_worker;
REVOKE ALL ON impact.lineage_edge FROM impact_worker;
REVOKE INSERT,UPDATE ON impact.membership_current FROM impact_worker;
REVOKE UPDATE ON impact.notification_current FROM impact_worker;
REVOKE UPDATE ON impact.object_registry FROM impact_worker;
REVOKE ALL ON impact.observation_current FROM impact_worker;
REVOKE ALL ON impact.offline_grant FROM impact_worker;
REVOKE ALL ON impact.operation_receipt FROM impact_worker;
REVOKE ALL ON impact.organisation_unit_current FROM impact_worker;
REVOKE ALL ON impact.participant_current FROM impact_worker;
REVOKE ALL ON impact.period_current FROM impact_worker;
REVOKE ALL ON impact.privacy_case_current FROM impact_worker;
REVOKE ALL ON impact.privacy_store_action FROM impact_worker;
REVOKE ALL ON impact.programme_current FROM impact_worker;
REVOKE ALL ON impact.qualitative_extract_current FROM impact_worker;
REVOKE ALL ON impact.quality_issue_current FROM impact_worker;
REVOKE ALL ON impact.retention_hold FROM impact_worker;
REVOKE ALL ON impact.retention_policy_current FROM impact_worker;
REVOKE ALL ON impact.review_decision FROM impact_worker;
REVOKE ALL ON impact.schedule_current FROM impact_worker;
REVOKE ALL ON impact.scope_definition FROM impact_worker;
REVOKE ALL ON impact.scope_member FROM impact_worker;
REVOKE ALL ON impact.service_event_current FROM impact_worker;
REVOKE ALL ON impact.service_identity FROM impact_worker;
REVOKE ALL ON impact.snapshot_current FROM impact_worker;
REVOKE ALL ON impact.snapshot_member FROM impact_worker;
REVOKE ALL ON impact.source_key_registry FROM impact_worker;
REVOKE ALL ON impact.source_revision_receipt FROM impact_worker;
REVOKE ALL ON impact.submission_current FROM impact_worker;
REVOKE ALL ON impact.subscription_current FROM impact_worker;
REVOKE ALL ON impact.support_request_current FROM impact_worker;
REVOKE ALL ON impact.sync_receipt FROM impact_worker;
REVOKE ALL ON impact.target_current FROM impact_worker;
REVOKE ALL ON impact.tenant_current FROM impact_worker;
REVOKE UPDATE ON impact.tenant_principal FROM impact_worker;
REVOKE ALL ON impact.tenant_root FROM impact_worker;
REVOKE ALL ON impact.tenant_schedule_hold FROM impact_worker;
REVOKE ALL ON impact.upload_part FROM impact_worker;
REVOKE ALL ON impact.upload_session FROM impact_worker;
REVOKE ALL ON impact.webhook_delivery FROM impact_worker;
REVOKE ALL ON impact.work_item_current FROM impact_worker;
REVOKE ALL ON impact.workflow_author FROM impact_worker;
REVOKE ALL ON impact.workflow_current FROM impact_worker;

-- Operator re-queue (control plane, platform API 1.5.0). impact_platform may not read or write the
-- tenant outbox; these two functions expose exactly the attention list (dispatchable rows that are
-- DEAD or held by a suspension, optionally of one tenant; no address, reference or payload) and one
-- fenced transition per row.
-- They read through the owner-only SELECT policies of 0018 and update under tenant_fence, so the
-- caller must have set impact.tenant_id. The lease generation is the row's revision: a re-queue or
-- a release advances it, so a worker that still believes it holds the row matches nothing (0018).
CREATE FUNCTION impact.operator_delivery_attention(requested_tenant uuid, max_rows integer)
 RETURNS TABLE(tenant_id uuid, lifecycle_state text, event_id uuid, channel text, template text,
  state text, held boolean, attempts integer, last_error_class text, last_attempt_at timestamptz,
  completed_at timestamptz, lease_generation bigint)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT d.tenant_id,t.lifecycle_state,d.event_id,d.channel,d.template,d.state,d.held_at IS NOT NULL,
  d.attempts,d.last_error_class,d.last_attempt_at,d.completed_at,d.lease_generation
 FROM impact.outbox_delivery d JOIN impact.tenant_root t ON t.tenant_id=d.tenant_id
 WHERE d.channel IS NOT NULL AND (d.state='DEAD' OR (d.held_at IS NOT NULL AND d.state IN ('PENDING','LEASED')))
  AND (requested_tenant IS NULL OR d.tenant_id=requested_tenant)
 ORDER BY coalesce(d.last_attempt_at,d.next_attempt_at) DESC,d.tenant_id,d.event_id
 LIMIT least(greatest(max_rows,1),50)
$$;
REVOKE ALL ON FUNCTION impact.operator_delivery_attention(uuid,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.operator_delivery_attention(uuid,integer) TO impact_platform;
-- 'requeue': a DEAD row becomes PENDING with a fresh attempt budget, due now, released from any
-- hold. 'release': a held PENDING row is released, due now. Anything else changes nothing and
-- answers a reason. The caller holds the tenant advisory lock and checks the tenant is Active.
CREATE FUNCTION impact.operator_requeue_delivery(requested_event uuid, mode text, expected_generation bigint)
 RETURNS TABLE(outcome text, state text, held boolean, attempts integer, lease_generation bigint,
  previous_state text, previous_attempts integer, previous_error_class text)
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
#variable_conflict use_column
DECLARE tenant uuid := impact.current_tenant(); r impact.outbox_delivery%ROWTYPE;
BEGIN
 IF tenant IS NULL OR mode NOT IN ('requeue','release') THEN
  RAISE EXCEPTION 'operator re-queue needs a tenant context and a known mode' USING ERRCODE='42501';
 END IF;
 SELECT * INTO r FROM impact.outbox_delivery d WHERE d.tenant_id=tenant AND d.event_id=requested_event
  AND d.channel IS NOT NULL FOR UPDATE;
 IF NOT FOUND THEN
  RETURN QUERY SELECT 'NOT_FOUND'::text,NULL::text,NULL::boolean,NULL::integer,NULL::bigint,NULL::text,NULL::integer,NULL::text;
  RETURN;
 END IF;
 IF r.lease_generation<>expected_generation THEN outcome := 'STALE';
 ELSIF mode='requeue' AND r.state<>'DEAD' THEN outcome := 'NOT_DEAD';
 ELSIF mode='release' AND r.held_at IS NULL THEN outcome := 'NOT_HELD';
 ELSIF mode='release' AND r.state<>'PENDING' THEN outcome := 'NOT_PENDING';
 ELSIF mode='requeue' THEN
  UPDATE impact.outbox_delivery d SET state='PENDING',attempts=0,completed_at=NULL,held_at=NULL,
   next_attempt_at=now(),lease_generation=d.lease_generation+1
   WHERE d.tenant_id=tenant AND d.event_id=requested_event;
  outcome := 'REQUEUED';
 ELSE
  UPDATE impact.outbox_delivery d SET held_at=NULL,next_attempt_at=now(),lease_generation=d.lease_generation+1
   WHERE d.tenant_id=tenant AND d.event_id=requested_event;
  outcome := 'RELEASED';
 END IF;
 RETURN QUERY SELECT outcome,d.state::text,d.held_at IS NOT NULL,d.attempts,d.lease_generation,
  r.state::text,r.attempts,r.last_error_class::text
  FROM impact.outbox_delivery d WHERE d.tenant_id=tenant AND d.event_id=requested_event;
END $$;
REVOKE ALL ON FUNCTION impact.operator_requeue_delivery(uuid,text,bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.operator_requeue_delivery(uuid,text,bigint) TO impact_platform;
COMMIT;
```

### 0026 worker job grants

Source: infrastructure/migrations/0026_worker_job_grants.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Worker privileges, part 2 (integration of builds 0.21.0-0.24.0, October 2026).
-- Migration 0025 left four tables of migration 0003's SELECT/INSERT/UPDATE grant to impact_worker
-- untouched until report exports (0024) had settled the worker's job privileges. 0024 grants the
-- worker exactly what the REPORT_EXPORT job class and the cancellation pass use (worker.py):
--   job        SELECT, UPDATE  (claim, lease renewal, fenced outcome, cancellation before start)
--   job_item   SELECT, INSERT  (artifact and cancellation outcomes; never updated)
-- The worker never inserts a job (jobs are requested by the application) and never reads or writes
-- report_current or report_template_current (an export reads the pinned package through
-- object_revision and report_package_binding). Those privileges are revoked here; a REVOKE removes
-- only what it names, so the grants of 0024 that the worker uses stay in place. impact_app is not
-- touched.
REVOKE INSERT ON impact.job FROM impact_worker;
REVOKE UPDATE ON impact.job_item FROM impact_worker;
REVOKE ALL ON impact.report_current FROM impact_worker;
REVOKE ALL ON impact.report_template_current FROM impact_worker;
COMMIT;
```

### 0027 privacy execution

Source: infrastructure/migrations/0027_privacy_execution.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Privacy execution (v0.25 part B): data-subject requests for a member of the tenant (access export
-- and erasure propagation) and a scheduled retention sweep with an insert-only proof record.
--
-- Data-subject requests. PrivacyCase has been a registry kind with a typed projection since 0002;
-- this migration adds the payload columns the implemented case writes (the subject membership, the
-- request reason and verification note, the evidence and import batches the privacy officer names,
-- and the server-set approval, plan, execution and package fields). An erasure is an approved plan
-- of per-store actions (privacy_store_action, 0002) executed in one transaction: earlier revision
-- payloads are removed only through the SECURITY DEFINER impact.privacy_remove_revisions below,
-- under the revision_removal_guard trigger of 0003, which still requires the privacy case context,
-- an EXECUTING DATABASE/DELETE store action, a durable deletion_ledger row and no active hold.
--
-- Why a definer and a replaced guard: the guard admits only a role that holds impact_privacy, but
-- the API's login is a member of impact_app alone and a migration cannot grant role membership (the
-- migrator holds neither CREATEROLE nor ADMIN OPTION). The removal therefore runs inside
-- impact.privacy_remove_revisions, owned by impact_owner, which the guard now also admits when (and
-- only when) that definer has set its transaction-local executor marker. impact_app still holds no
-- UPDATE privilege on object_revision, so no other path reaches the trigger; every other condition
-- of the original guard is unchanged.
ALTER TABLE impact.privacy_case_current
 ADD COLUMN subject_membership_id uuid,
 ADD COLUMN subject_membership_id_kind text GENERATED ALWAYS AS ('Membership') STORED,
 ADD COLUMN subject_principal_id uuid,
 ADD COLUMN purpose varchar(64),
 ADD COLUMN reason varchar(2000),
 ADD COLUMN verification_note varchar(2000),
 ADD COLUMN evidence_ids jsonb CHECK(evidence_ids IS NULL OR jsonb_typeof(evidence_ids)='array'),
 ADD COLUMN import_ids jsonb CHECK(import_ids IS NULL OR jsonb_typeof(import_ids)='array'),
 ADD COLUMN approved_by uuid,
 ADD COLUMN approved_at timestamptz,
 ADD COLUMN approved_revision uuid,
 ADD COLUMN plan_sha256 varchar(64) CHECK(plan_sha256 IS NULL OR plan_sha256 ~ '^[0-9a-f]{64}$'),
 ADD COLUMN executed_by uuid,
 ADD COLUMN executed_at timestamptz,
 ADD COLUMN completed_at timestamptz,
 ADD COLUMN outcome varchar(32) CHECK(outcome IS NULL OR outcome IN ('COMPLETED','PARTIALLY_COMPLETED')),
 ADD COLUMN package_id uuid,
 ADD COLUMN package_sha256 varchar(64) CHECK(package_sha256 IS NULL OR package_sha256 ~ '^[0-9a-f]{64}$'),
 ADD COLUMN manifest jsonb CHECK(manifest IS NULL OR jsonb_typeof(manifest)='object'),
 ADD CONSTRAINT privacy_case_request_type CHECK(request_type IS NULL OR request_type IN ('ACCESS','ERASURE')),
 ADD CONSTRAINT privacy_case_subject_fk FOREIGN KEY(tenant_id,subject_membership_id,subject_membership_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 ADD CONSTRAINT privacy_case_subject_principal_fk FOREIGN KEY(tenant_id,subject_principal_id)
  REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;

-- The export package of an approved access request: one per case, bounded, written once with its
-- SHA-256 and section manifest, and deleted by the retention sweep when it expires.
CREATE TABLE impact.privacy_export_package(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  package_id uuid NOT NULL,
  case_id uuid NOT NULL,
  case_revision uuid NOT NULL,
  subject_membership_id uuid NOT NULL,
  body bytea NOT NULL CHECK(octet_length(body) BETWEEN 2 AND 5242880),
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  manifest jsonb NOT NULL CHECK(jsonb_typeof(manifest)='object'),
  created_by uuid NOT NULL,
  created_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL CHECK(expires_at>created_at),
  PRIMARY KEY(tenant_id,package_id),
  UNIQUE(tenant_id,case_id),
  FOREIGN KEY(tenant_id,case_id) REFERENCES impact.privacy_case_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,case_id,case_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,created_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX privacy_export_package_expiry ON impact.privacy_export_package(tenant_id,expires_at);

-- One row per mediated download of an export package. No foreign key to the package: the access
-- record outlives the package's deletion. Never updated or deleted.
CREATE TABLE impact.privacy_export_access(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  access_id uuid NOT NULL,
  case_id uuid NOT NULL,
  package_id uuid NOT NULL,
  content_sha256 bytea NOT NULL CHECK(octet_length(content_sha256)=32),
  principal_id uuid NOT NULL,
  membership_id uuid NOT NULL,
  purpose varchar(64) NOT NULL,
  accessed_at timestamptz NOT NULL,
  correlation_id uuid NOT NULL,
  PRIMARY KEY(tenant_id,access_id),
  FOREIGN KEY(tenant_id,case_id) REFERENCES impact.privacy_case_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);

-- Erasure bookkeeping on the stores it reaches. A redacted sealed recipient is overwritten with
-- random bytes (the address cannot be recovered even with the delivery secret); a purged blob's
-- bytes were deleted from the object store by the case that names it.
ALTER TABLE impact.outbox_delivery ADD COLUMN recipient_redacted_at timestamptz;
ALTER TABLE impact.file_blob
 ADD COLUMN purged_at timestamptz,
 ADD COLUMN purge_case_id uuid;

-- Retention sweep: job class RETENTION_SWEEP, executed by the worker under a generation-fenced
-- lease on database time, like REPORT_EXPORT (0024). The job row carries the lifecycle and lease
-- generation; this row carries the holder and attempt bookkeeping.
CREATE TABLE impact.retention_sweep(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  job_id uuid NOT NULL,
  lease_owner varchar(128),
  attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
  next_attempt_at timestamptz NOT NULL,
  last_attempt_at timestamptz,
  last_error_class varchar(64) CHECK(last_error_class IS NULL OR last_error_class ~ '^[A-Z][A-Z0-9_]{0,63}$'),
  completed_at timestamptz,
  PRIMARY KEY(tenant_id,job_id),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.job(tenant_id,job_id)
);

-- Proof of retention: one insert-only row per data class per sweep, with the policy applied, the
-- cutoff, the number of items deleted or redacted and the SHA-256 of their sorted keys. Written in
-- the same fenced transaction as the deletions it proves; never updated or deleted.
CREATE TABLE impact.retention_proof(
  tenant_id uuid NOT NULL REFERENCES impact.tenant_root,
  proof_id uuid NOT NULL,
  job_id uuid NOT NULL,
  lease_generation bigint NOT NULL CHECK(lease_generation>0),
  data_class varchar(64) NOT NULL CHECK(data_class ~ '^[A-Z][A-Z0-9_]{0,63}$'),
  action varchar(16) NOT NULL CHECK(action IN ('DELETE','REDACT','EXPIRE')),
  retention_days integer NOT NULL CHECK(retention_days>=0),
  cutoff timestamptz NOT NULL,
  affected_count integer NOT NULL CHECK(affected_count>=0),
  items_sha256 bytea NOT NULL CHECK(octet_length(items_sha256)=32),
  executed_at timestamptz NOT NULL,
  worker_id varchar(128) NOT NULL,
  PRIMARY KEY(tenant_id,proof_id),
  UNIQUE(tenant_id,job_id,data_class),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.retention_sweep(tenant_id,job_id)
);
CREATE INDEX retention_proof_recent ON impact.retention_proof(tenant_id,executed_at);

ALTER TABLE impact.privacy_export_package ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.privacy_export_package FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.privacy_export_package USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.privacy_export_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.privacy_export_access FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.privacy_export_access USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.retention_sweep ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.retention_sweep FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.retention_sweep USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.retention_proof ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.retention_proof FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.retention_proof USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

-- The original guard of 0003, plus the definer path described above.
CREATE OR REPLACE FUNCTION impact.guard_revision_removal() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE case_ref uuid;
BEGIN
 IF NOT (pg_has_role(current_user,'impact_privacy','USAGE')
         OR (current_user='impact_owner' AND current_setting('impact.privacy_executor',true)='privacy_remove_revisions')) THEN
   RAISE EXCEPTION 'immutable revision';
 END IF;
 case_ref := nullif(current_setting('impact.privacy_case_id',true),'')::uuid;
 IF case_ref IS NULL OR NEW.tenant_id<>impact.current_tenant() THEN RAISE EXCEPTION 'privacy context required'; END IF;
 IF (to_jsonb(OLD)-'payload'-'restriction_state') IS DISTINCT FROM (to_jsonb(NEW)-'payload'-'restriction_state') THEN RAISE EXCEPTION 'immutable metadata'; END IF;
 IF NEW.payload IS NOT NULL OR NEW.restriction_state<>'REMOVED' THEN RAISE EXCEPTION 'removal only'; END IF;
 IF EXISTS(SELECT 1 FROM impact.retention_hold WHERE tenant_id=OLD.tenant_id AND object_id=OLD.object_id AND released_at IS NULL) THEN RAISE EXCEPTION 'active hold'; END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=OLD.tenant_id AND case_id=case_ref AND object_id=OLD.object_id AND store='DATABASE' AND action='DELETE' AND state='EXECUTING') THEN RAISE EXCEPTION 'approved executing plan required'; END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.deletion_ledger WHERE tenant_id=OLD.tenant_id AND case_id=case_ref AND object_id=OLD.object_id) THEN RAISE EXCEPTION 'durable ledger prerequisite'; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_revision_removal() FROM PUBLIC;

-- The upload guard of 0023, plus one transition: a declared file name may be cleared (never
-- changed) by impact.privacy_redact_uploads for an erasure case. Everything else is unchanged.
CREATE OR REPLACE FUNCTION impact.upload_session_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
  IF NEW.tenant_id<>OLD.tenant_id OR NEW.upload_id<>OLD.upload_id OR NEW.owner_id<>OLD.owner_id
     OR NEW.purpose<>OLD.purpose OR NEW.mode<>OLD.mode OR NEW.expected_bytes<>OLD.expected_bytes
     OR NEW.expected_digest<>OLD.expected_digest
     OR (NEW.filename IS DISTINCT FROM OLD.filename AND NOT (NEW.filename IS NULL AND current_user='impact_owner'
         AND current_setting('impact.privacy_executor',true)='privacy_redact_uploads'))
     OR NEW.media_type IS DISTINCT FROM OLD.media_type
     OR (OLD.blob_id IS NOT NULL AND NEW.blob_id IS DISTINCT FROM OLD.blob_id) THEN
    RAISE EXCEPTION 'upload_session declaration is immutable' USING ERRCODE='23514';
  END IF;
  IF OLD.state IN ('CLEAN','REJECTED','CANCELLED','EXPIRED') AND NEW.state<>OLD.state THEN
    RAISE EXCEPTION 'upload_session terminal state is final' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.upload_session_guard() FROM PUBLIC;

-- An erasure case that is approved (or executing) for the current tenant, or an exception.
CREATE FUNCTION impact.privacy_require_case(case_ref uuid) RETURNS void
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
  IF impact.current_tenant() IS NULL OR NOT EXISTS(
    SELECT 1 FROM impact.privacy_case_current p JOIN impact.object_registry r
      ON r.tenant_id=p.tenant_id AND r.object_id=p.object_id
     WHERE p.tenant_id=impact.current_tenant() AND p.object_id=case_ref AND p.request_type='ERASURE'
       AND p.approved_by IS NOT NULL AND r.lifecycle_state IN ('Approved','Executing')) THEN
    RAISE EXCEPTION 'approved erasure case required' USING ERRCODE='42501';
  END IF;
END $$;
REVOKE ALL ON FUNCTION impact.privacy_require_case(uuid) FROM PUBLIC;

-- Remove the payload of every revision of one object except keep_revision (the tombstone the
-- application has just written, or NULL to remove every revision), for an approved erasure case
-- whose plan names this object with an EXECUTING DATABASE/DELETE action. The deletion_ledger row is
-- written first (the guard requires it); the guard re-checks everything. Returns the number removed.
CREATE FUNCTION impact.privacy_remove_revisions(case_ref uuid, target uuid, keep_revision uuid) RETURNS integer
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE removed integer;
BEGIN
  PERFORM impact.privacy_require_case(case_ref);
  IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=impact.current_tenant()
      AND case_id=case_ref AND object_id=target AND store='DATABASE' AND action='DELETE' AND state='EXECUTING') THEN
    RAISE EXCEPTION 'approved executing plan required' USING ERRCODE='42501';
  END IF;
  INSERT INTO impact.deletion_ledger(tenant_id,entry_id,case_id,object_id,effective_at,disposition)
   SELECT impact.current_tenant(),gen_random_uuid(),case_ref,target,statement_timestamp(),
     CASE WHEN keep_revision IS NULL THEN 'ALL_REVISIONS_REMOVED' ELSE 'EARLIER_REVISIONS_REMOVED_TOMBSTONE_KEPT' END
   WHERE NOT EXISTS(SELECT 1 FROM impact.deletion_ledger WHERE tenant_id=impact.current_tenant()
     AND case_id=case_ref AND object_id=target);
  PERFORM set_config('impact.privacy_case_id',case_ref::text,true);
  PERFORM set_config('impact.privacy_executor','privacy_remove_revisions',true);
  UPDATE impact.object_revision SET payload=NULL,restriction_state='REMOVED'
   WHERE tenant_id=impact.current_tenant() AND object_id=target AND restriction_state<>'REMOVED'
     AND (keep_revision IS NULL OR revision_id<>keep_revision);
  GET DIAGNOSTICS removed = ROW_COUNT;
  PERFORM set_config('impact.privacy_executor','',true);
  RETURN removed;
END $$;
REVOKE ALL ON FUNCTION impact.privacy_remove_revisions(uuid,uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.privacy_remove_revisions(uuid,uuid,uuid) TO impact_app;

-- Clear the declared file name of the uploads one evidence object was built from, for an approved
-- erasure case whose plan names that evidence with an EXECUTING PROJECTION/REDACT action. Must run
-- before the evidence revisions are removed (it finds the uploads through their payloads).
CREATE FUNCTION impact.privacy_redact_uploads(case_ref uuid, target uuid) RETURNS integer
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE redacted integer;
BEGIN
  PERFORM impact.privacy_require_case(case_ref);
  IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=impact.current_tenant()
      AND case_id=case_ref AND object_id=target AND store='PROJECTION' AND action='REDACT' AND state='EXECUTING') THEN
    RAISE EXCEPTION 'approved executing plan required' USING ERRCODE='42501';
  END IF;
  PERFORM set_config('impact.privacy_executor','privacy_redact_uploads',true);
  UPDATE impact.upload_session u SET filename=NULL
   WHERE u.tenant_id=impact.current_tenant() AND u.filename IS NOT NULL AND u.upload_id IN (
     SELECT (v.payload->>'upload_id')::uuid FROM impact.object_revision v
      WHERE v.tenant_id=impact.current_tenant() AND v.object_id=target AND v.object_type='Evidence'
        AND v.payload ? 'upload_id');
  GET DIAGNOSTICS redacted = ROW_COUNT;
  PERFORM set_config('impact.privacy_executor','',true);
  RETURN redacted;
END $$;
REVOKE ALL ON FUNCTION impact.privacy_redact_uploads(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.privacy_redact_uploads(uuid,uuid) TO impact_app;

-- Supersede the open delivery intents that reference one object (an invitation or a notice of the
-- subject) and overwrite every sealed recipient address they carry, for an approved erasure case
-- whose plan names that reference with an EXECUTING OUTBOX/SUPERSEDE action. The lease generation
-- advances, so a worker holding one of these rows cannot record an outcome for it.
CREATE FUNCTION impact.privacy_supersede_deliveries(case_ref uuid, reference uuid) RETURNS integer
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE superseded integer; redacted integer;
BEGIN
  PERFORM impact.privacy_require_case(case_ref);
  IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=impact.current_tenant()
      AND case_id=case_ref AND object_id=reference AND store='OUTBOX' AND action='SUPERSEDE' AND state='EXECUTING') THEN
    RAISE EXCEPTION 'approved executing plan required' USING ERRCODE='42501';
  END IF;
  UPDATE impact.outbox_delivery SET state='SUPERSEDED',lease_owner=NULL,lease_expires_at=NULL,
    lease_generation=lease_generation+1,last_error_class='SUBJECT_ERASED',completed_at=statement_timestamp()
   WHERE tenant_id=impact.current_tenant() AND reference_id=reference AND channel IS NOT NULL
     AND state IN ('PENDING','LEASED');
  GET DIAGNOSTICS superseded = ROW_COUNT;
  UPDATE impact.outbox_delivery SET recipient_sealed=sha256(convert_to(gen_random_uuid()::text,'UTF8')),
    recipient_redacted_at=statement_timestamp()
   WHERE tenant_id=impact.current_tenant() AND reference_id=reference AND channel='EMAIL'
     AND recipient_redacted_at IS NULL;
  GET DIAGNOSTICS redacted = ROW_COUNT;
  RETURN superseded+redacted;
END $$;
REVOKE ALL ON FUNCTION impact.privacy_supersede_deliveries(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.privacy_supersede_deliveries(uuid,uuid) TO impact_app;

-- Retention definers for the worker, which holds no privilege on operation_receipt or
-- upload_session (0025). Each acts on the current tenant only, compares with the database clock
-- (never a cutoff the caller supplies) and returns the keys it affected, for the proof digest.
CREATE FUNCTION impact.retention_purge_receipts(max_rows integer) RETURNS TABLE(item text)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DELETE FROM impact.operation_receipt o USING (
  SELECT tenant_id,actor_id,command_type,operation_id FROM impact.operation_receipt
   WHERE tenant_id=impact.current_tenant() AND expires_at<=statement_timestamp()
   ORDER BY expires_at,operation_id LIMIT greatest(least(max_rows,5000),0)) d
 WHERE o.tenant_id=d.tenant_id AND o.actor_id=d.actor_id AND o.command_type=d.command_type
   AND o.operation_id=d.operation_id
 RETURNING o.actor_id::text||':'||o.command_type||':'||o.operation_id::text
$$;
REVOKE ALL ON FUNCTION impact.retention_purge_receipts(integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.retention_purge_receipts(integer) TO impact_worker;

CREATE FUNCTION impact.retention_expire_uploads(max_rows integer) RETURNS TABLE(item text)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
UPDATE impact.upload_session u SET state='EXPIRED' FROM (
  SELECT tenant_id,upload_id FROM impact.upload_session
   WHERE tenant_id=impact.current_tenant() AND state='OPEN' AND expires_at<=statement_timestamp()
   ORDER BY expires_at,upload_id LIMIT greatest(least(max_rows,5000),0)) d
 WHERE u.tenant_id=d.tenant_id AND u.upload_id=d.upload_id
 RETURNING u.upload_id::text
$$;
REVOKE ALL ON FUNCTION impact.retention_expire_uploads(integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.retention_expire_uploads(integer) TO impact_worker;

-- Schedule one RETENTION_SWEEP job for the current tenant when none is queued or running and none
-- completed within the interval. The requester is the tenant's SERVICE principal (no identity), the
-- scope its TENANT scope. Returns the new job, or NULL when nothing is due.
CREATE FUNCTION impact.worker_schedule_retention(service_principal uuid, interval_seconds integer) RETURNS uuid
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE v_tenant uuid := impact.current_tenant(); v_scope uuid; v_job uuid;
BEGIN
  IF v_tenant IS NULL OR interval_seconds<60 THEN RAISE EXCEPTION 'tenant context required' USING ERRCODE='42501'; END IF;
  IF NOT EXISTS(SELECT 1 FROM impact.tenant_principal p WHERE p.tenant_id=v_tenant AND p.principal_id=service_principal
      AND p.principal_kind='SERVICE' AND p.identity_id IS NULL) THEN
    RAISE EXCEPTION 'service principal required' USING ERRCODE='42501';
  END IF;
  IF EXISTS(SELECT 1 FROM impact.job j LEFT JOIN impact.retention_sweep s ON s.tenant_id=j.tenant_id AND s.job_id=j.job_id
      WHERE j.tenant_id=v_tenant AND j.job_class='RETENTION_SWEEP' AND (j.state IN ('Queued','Running')
        OR (s.completed_at IS NOT NULL AND s.completed_at>statement_timestamp()-make_interval(secs=>interval_seconds)))) THEN
    RETURN NULL;
  END IF;
  SELECT d.scope_id INTO v_scope FROM impact.scope_definition d WHERE d.tenant_id=v_tenant AND d.scope_type='TENANT'
   ORDER BY d.scope_id LIMIT 1;
  IF v_scope IS NULL THEN RETURN NULL; END IF;
  v_job := gen_random_uuid();
  INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest)
   VALUES(v_tenant,v_job,'RETENTION_SWEEP',service_principal,v_scope,'Queued',
     jsonb_build_object('scheduled_at',statement_timestamp(),'interval_seconds',interval_seconds));
  INSERT INTO impact.retention_sweep(tenant_id,job_id,next_attempt_at) VALUES(v_tenant,v_job,statement_timestamp());
  RETURN v_job;
END $$;
REVOKE ALL ON FUNCTION impact.worker_schedule_retention(uuid,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.worker_schedule_retention(uuid,integer) TO impact_worker;

-- Application: case packages, access log and read-only views of the sweep and its proof.
GRANT SELECT,INSERT ON impact.privacy_export_package TO impact_app;
GRANT SELECT,INSERT ON impact.privacy_export_access TO impact_app;
GRANT SELECT ON impact.retention_sweep,impact.retention_proof TO impact_app;
-- Worker: exactly what the RETENTION_SWEEP job class uses (worker.py). It already holds SELECT and
-- UPDATE on job, SELECT and INSERT on job_item (0024) and SELECT, INSERT and UPDATE on
-- outbox_delivery (0003/0018); receipts and uploads are reached only through the definers above.
GRANT SELECT,UPDATE ON impact.retention_sweep TO impact_worker;
GRANT SELECT,INSERT ON impact.retention_proof TO impact_worker;
GRANT SELECT,DELETE ON impact.privacy_export_package TO impact_worker;
COMMIT;
```

### 0028 usable staging

Source: infrastructure/migrations/0028_usable_staging.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Usable staging (v0.26a): governed operator onboarding, provider accounts created through the
-- control plane, and initial access whose delegation ceiling includes purpose-bound capabilities.
-- Every independence rule stays as it was: a nomination is accepted only by a different natural
-- person than the nominating operator, and activation still counts natural persons.
--
-- Control-plane events that belong to no tenant (operator onboarding, account provisioning by an
-- operator). Every tenant event keeps its tenant; only these actions may omit it.
ALTER TABLE impact.platform_event ALTER COLUMN tenant_id DROP NOT NULL;
ALTER TABLE impact.platform_event ADD CONSTRAINT platform_event_tenant_scope CHECK(
 tenant_id IS NOT NULL OR action IN ('operator-nominate','operator-cancel','operator-decline',
 'operator-accept','account-create','account-reissue'));

-- A nomination of one person (named by the SHA-256 of a normalised e-mail address) for the platform
-- operator role. The nominating operator never becomes the nominee: acceptance is by the person who
-- signs in with that verified address, through the definer below, and only by another natural
-- person. No clear address is stored.
CREATE TABLE impact.platform_operator_nomination(
 nomination_id uuid PRIMARY KEY, revision_id uuid NOT NULL,
 state varchar(20) NOT NULL CHECK(state IN ('Nominated','Accepted','Declined','Cancelled')),
 nominated_by uuid NOT NULL REFERENCES impact.auth_identity,
 email_hash bytea NOT NULL CHECK(octet_length(email_hash)=32),
 email_mask varchar(254) NOT NULL,
 reason varchar(1000) NOT NULL CHECK(length(trim(reason))>0),
 operator_expires_at timestamptz NOT NULL,
 expires_at timestamptz NOT NULL,
 nominator_auth_time timestamptz NOT NULL,
 nominee_identity_id uuid REFERENCES impact.auth_identity,
 accepted_at timestamptz, accepted_auth_time timestamptz,
 decided_by uuid REFERENCES impact.auth_identity, decision_reason varchar(1000),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 CHECK(operator_expires_at>created_at AND expires_at>created_at),
 CHECK((state='Accepted')=(accepted_at IS NOT NULL AND nominee_identity_id IS NOT NULL))
);
CREATE UNIQUE INDEX operator_nomination_one_open ON impact.platform_operator_nomination(email_hash)
 WHERE state='Nominated';
-- Only the definer may record an acceptance; the platform role may cancel or decline.
CREATE FUNCTION impact.guard_operator_nomination() RETURNS trigger LANGUAGE plpgsql
 SET search_path=pg_catalog,impact AS $$
BEGIN
 IF NEW.nomination_id<>OLD.nomination_id OR NEW.nominated_by<>OLD.nominated_by
  OR NEW.email_hash<>OLD.email_hash OR NEW.operator_expires_at<>OLD.operator_expires_at
  OR NEW.expires_at<>OLD.expires_at OR NEW.created_at<>OLD.created_at OR NEW.reason<>OLD.reason
  OR NEW.nominator_auth_time<>OLD.nominator_auth_time THEN
  RAISE EXCEPTION 'nomination is immutable' USING ERRCODE='42501';
 END IF;
 IF OLD.state<>'Nominated' AND NEW.state IS DISTINCT FROM OLD.state THEN
  RAISE EXCEPTION 'nomination is final' USING ERRCODE='42501';
 END IF;
 IF NEW.state='Accepted' AND OLD.state<>'Accepted' AND current_user<>'impact_owner' THEN
  RAISE EXCEPTION 'acceptance only through accept_operator_nomination' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER operator_nomination_guard BEFORE UPDATE ON impact.platform_operator_nomination
 FOR EACH ROW EXECUTE FUNCTION impact.guard_operator_nomination();

-- Identity-provider accounts created through the control plane (an operator, or a tenant owner for
-- a pending invitation of their tenant). Never a password: only who created which account for which
-- address hash, and how often a one-time credential was issued.
CREATE TABLE impact.provider_account(
 account_id uuid PRIMARY KEY, revision_id uuid NOT NULL,
 issuer text NOT NULL, provider_subject varchar(255) NOT NULL,
 email_hash bytea NOT NULL CHECK(octet_length(email_hash)=32),
 email_mask varchar(254) NOT NULL,
 created_by uuid NOT NULL REFERENCES impact.auth_identity,
 tenant_id uuid REFERENCES impact.tenant_root,
 nomination_id uuid REFERENCES impact.platform_operator_nomination,
 provider_created boolean NOT NULL,
 identity_id uuid REFERENCES impact.auth_identity,
 credentials_issued integer NOT NULL DEFAULT 0 CHECK(credentials_issued BETWEEN 0 AND 1000),
 last_issued_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(issuer,provider_subject)
);

-- The identity for a provisioned account: the existing (issuer, subject) identity, or a new one that is
-- its own natural person, exactly as scripts/bootstrap_operator.py `identity` registers one. Only for
-- the deployment's qualified issuer. Registration conveys no authority.
CREATE FUNCTION impact.register_provider_account_identity(requested uuid) RETURNS uuid
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE a impact.provider_account; ident uuid;
BEGIN
 SELECT * INTO a FROM impact.provider_account WHERE account_id=requested FOR UPDATE;
 IF NOT FOUND OR NOT EXISTS(SELECT 1 FROM impact.deployment_qualification
  WHERE active AND valid_until>now() AND issuer=a.issuer) THEN
  RAISE EXCEPTION 'account registration denied' USING ERRCODE='42501';
 END IF;
 SELECT identity_id INTO ident FROM impact.auth_identity WHERE issuer=a.issuer AND provider_subject=a.provider_subject;
 IF ident IS NULL THEN
  ident := gen_random_uuid();
  INSERT INTO impact.auth_identity(identity_id,issuer,provider_subject,natural_identity_id)
  VALUES(ident,a.issuer,a.provider_subject,gen_random_uuid());
 END IF;
 UPDATE impact.provider_account SET identity_id=ident,updated_at=now() WHERE account_id=requested;
 RETURN ident;
END $$;

-- Acceptance of a nomination by the nominee. Rechecked here, whatever the caller checked: an open,
-- unexpired nomination; the nominating operator still an active operator; the actor's verified
-- address is the nominated one; the actor is a different natural person from the nominating
-- operator and from every active operator. Fresh MFA is checked by the caller (tenant_lifecycle.py).
CREATE FUNCTION impact.accept_operator_nomination(requested uuid, actor uuid) RETURNS void
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE n impact.platform_operator_nomination;
BEGIN
 SELECT * INTO n FROM impact.platform_operator_nomination WHERE nomination_id=requested FOR UPDATE;
 IF NOT FOUND OR n.state<>'Nominated' OR n.expires_at<=now() OR n.operator_expires_at<=now()
  OR actor=n.nominated_by OR NOT impact.lock_platform_operator(n.nominated_by)
  OR NOT EXISTS(SELECT 1 FROM impact.identity_profile p WHERE p.identity_id=actor AND p.verified_email_hash=n.email_hash)
  OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
   WHERE a.identity_id=actor AND b.identity_id=n.nominated_by)
  OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
   JOIN impact.platform_operator o ON o.identity_id=b.identity_id
   WHERE a.identity_id=actor AND o.active AND o.expires_at>now())
 THEN RAISE EXCEPTION 'operator nomination acceptance denied' USING ERRCODE='42501'; END IF;
 INSERT INTO impact.platform_operator(identity_id,active,expires_at,authority_reference)
 VALUES(actor,true,n.operator_expires_at,'Accepted nomination '||n.nomination_id::text||' by operator '||n.nominated_by::text)
 ON CONFLICT(identity_id) DO UPDATE SET active=true,expires_at=EXCLUDED.expires_at,authority_reference=EXCLUDED.authority_reference;
 UPDATE impact.platform_operator_nomination SET state='Accepted',accepted_at=now(),nominee_identity_id=actor,
  decided_by=actor,updated_at=now() WHERE nomination_id=requested;
END $$;

-- Whether a tenant has a pending invitation for this address hash (a tenant owner may create a
-- sign-in account only for such an address). The tenant must be the transaction's tenant.
CREATE FUNCTION impact.tenant_pending_invitation(requested_tenant uuid, digest bytea) RETURNS boolean
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
BEGIN
 IF requested_tenant IS DISTINCT FROM impact.current_tenant() THEN
  RAISE EXCEPTION 'tenant denied' USING ERRCODE='42501';
 END IF;
 RETURN EXISTS(SELECT 1 FROM impact.member_invitation WHERE tenant_id=requested_tenant
  AND intended_email_hash=digest AND consumed_at IS NULL AND revoked_at IS NULL AND expires_at>now());
END $$;

-- Initial access (initial-access-v2): the delegation ceiling also covers the profile's purpose-bound
-- capabilities, which no role template carries; they are issued only as purpose-bound grants after an
-- independent review (purpose-grants). Every other condition is unchanged from 0014; a v1 manifest
-- has no purpose_bound list and is applied exactly as before.
CREATE OR REPLACE FUNCTION impact.apply_initial_authority(requested uuid) RETURNS void
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
 (SELECT DISTINCT jsonb_array_elements_text(value) AS cap FROM jsonb_each(r.manifest->'roles')
  UNION SELECT jsonb_array_elements_text(COALESCE(r.manifest->'purpose_bound','[]'::jsonb))) caps
 WHERE p.tenant_id=r.tenant_id AND p.active AND p.identity_id IN(r.owner_identity_id,r.second_identity_id);
END $$;

REVOKE ALL ON FUNCTION impact.register_provider_account_identity(uuid),impact.accept_operator_nomination(uuid,uuid),
 impact.tenant_pending_invitation(uuid,bytea),impact.guard_operator_nomination() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.register_provider_account_identity(uuid),impact.accept_operator_nomination(uuid,uuid),
 impact.tenant_pending_invitation(uuid,bytea) TO impact_platform;
-- The platform role records nominations and accounts; it never writes platform_operator itself.
GRANT SELECT,INSERT ON impact.platform_operator_nomination,impact.provider_account TO impact_platform;
GRANT UPDATE(state,revision_id,updated_at,decided_by,decision_reason) ON impact.platform_operator_nomination TO impact_platform;
GRANT UPDATE(revision_id,updated_at,credentials_issued,last_issued_at) ON impact.provider_account TO impact_platform;
COMMIT;
```

### 0029 operator lifecycle

Source: infrastructure/migrations/0029_operator_lifecycle.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Operator lifecycle (v0.27): renewal before expiry and deactivation of a platform operator, each by
-- a different active operator (a different natural person), with fresh assurance and a reason. The
-- platform role still never writes platform_operator: both changes go through the SECURITY DEFINER
-- apply_operator_change below, which rechecks every condition, and every applied change is one row
-- of the insert-only register platform_operator_change. The last active operator is never
-- deactivated (the actor must be another active operator, and the definer counts again).
--
-- An operator row now carries a revision, so a change names the exact state it saw
-- (expected_revision); the guard trigger refreshes it on every update and keeps the identity fixed.
ALTER TABLE impact.platform_operator ADD COLUMN revision_id uuid NOT NULL DEFAULT gen_random_uuid();
ALTER TABLE impact.platform_operator ADD COLUMN updated_at timestamptz NOT NULL DEFAULT now();
CREATE FUNCTION impact.guard_platform_operator() RETURNS trigger LANGUAGE plpgsql
 SET search_path=pg_catalog,impact AS $$
BEGIN
 IF NEW.identity_id<>OLD.identity_id THEN
  RAISE EXCEPTION 'operator identity is immutable' USING ERRCODE='42501';
 END IF;
 NEW.revision_id := gen_random_uuid();
 NEW.updated_at := now();
 RETURN NEW;
END $$;
CREATE TRIGGER platform_operator_guard BEFORE UPDATE ON impact.platform_operator
 FOR EACH ROW EXECUTE FUNCTION impact.guard_platform_operator();

-- Control-plane events of operator renewal and deactivation belong to no tenant, like onboarding.
ALTER TABLE impact.platform_event DROP CONSTRAINT platform_event_tenant_scope;
ALTER TABLE impact.platform_event ADD CONSTRAINT platform_event_tenant_scope CHECK(
 tenant_id IS NOT NULL OR action IN ('operator-nominate','operator-cancel','operator-decline',
 'operator-accept','account-create','account-reissue','operator-renew','operator-deactivate'));

-- Insert-only register of applied operator changes: who changed whose role, from what to what, why.
-- Written only by the definer; the platform role reads it.
CREATE TABLE impact.platform_operator_change(
 change_id uuid PRIMARY KEY,
 operator_identity_id uuid NOT NULL REFERENCES impact.platform_operator,
 action varchar(20) NOT NULL CHECK(action IN ('renew','deactivate')),
 actor_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 actor_auth_time timestamptz NOT NULL,
 reason varchar(1000) NOT NULL CHECK(length(trim(reason))>0),
 previous_revision_id uuid NOT NULL, revision_id uuid NOT NULL,
 previous_expires_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
 previous_active boolean NOT NULL, active boolean NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(actor_identity_id<>operator_identity_id),
 CHECK((action='renew' AND active AND previous_active AND expires_at>previous_expires_at)
  OR (action='deactivate' AND NOT active AND previous_active AND expires_at=previous_expires_at))
);

-- Renewal or deactivation of one operator by another. Rechecked here, whatever the caller checked:
-- the actor is an active, unexpired operator and not the subject, nor another identity of the
-- subject's natural person; the subject row is at the expected revision and still active and
-- unexpired (expired or deactivated authority is not renewed; a deactivated operator is not
-- deactivated again); a renewal moves the expiry later, at most 365 days ahead; a deactivation
-- leaves at least one other active operator. Fresh assurance is checked by the caller
-- (tenant_lifecycle.py) and its instant recorded here. Returns the subject's new revision.
CREATE FUNCTION impact.apply_operator_change(requested_change uuid, subject uuid, actor uuid,
 requested_action text, expected uuid, new_expiry timestamptz, actor_auth_time timestamptz, why text)
 RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE o impact.platform_operator; fresh uuid;
BEGIN
 IF requested_change IS NULL OR subject IS NULL OR actor IS NULL OR subject=actor
  OR requested_action NOT IN ('renew','deactivate') OR expected IS NULL OR actor_auth_time IS NULL
  OR why IS NULL OR length(trim(why))=0 OR NOT impact.lock_platform_operator(actor)
  OR EXISTS(SELECT 1 FROM impact.auth_identity a JOIN impact.auth_identity b ON a.natural_identity_id=b.natural_identity_id
   WHERE a.identity_id=actor AND b.identity_id=subject)
 THEN RAISE EXCEPTION 'operator change denied' USING ERRCODE='42501'; END IF;
 SELECT * INTO o FROM impact.platform_operator WHERE identity_id=subject FOR UPDATE;
 IF NOT FOUND OR o.revision_id<>expected OR NOT o.active OR o.expires_at<=now() THEN
  RAISE EXCEPTION 'operator change denied' USING ERRCODE='42501';
 END IF;
 IF requested_action='renew' THEN
  IF new_expiry IS NULL OR new_expiry<=o.expires_at OR new_expiry>now()+interval '365 days' THEN
   RAISE EXCEPTION 'operator change denied' USING ERRCODE='42501';
  END IF;
  UPDATE impact.platform_operator SET expires_at=new_expiry WHERE identity_id=subject;
 ELSE
  IF (SELECT count(*) FROM impact.platform_operator WHERE active AND expires_at>now() AND identity_id<>subject)<1 THEN
   RAISE EXCEPTION 'operator change denied' USING ERRCODE='42501';
  END IF;
  UPDATE impact.platform_operator SET active=false WHERE identity_id=subject;
 END IF;
 SELECT revision_id INTO fresh FROM impact.platform_operator WHERE identity_id=subject;
 INSERT INTO impact.platform_operator_change(change_id,operator_identity_id,action,actor_identity_id,actor_auth_time,
  reason,previous_revision_id,revision_id,previous_expires_at,expires_at,previous_active,active)
 VALUES(requested_change,subject,requested_action,actor,actor_auth_time,trim(why),o.revision_id,fresh,
  o.expires_at,CASE WHEN requested_action='renew' THEN new_expiry ELSE o.expires_at END,o.active,requested_action='renew');
 RETURN fresh;
END $$;

REVOKE ALL ON FUNCTION impact.apply_operator_change(uuid,uuid,uuid,text,uuid,timestamptz,timestamptz,text),
 impact.guard_platform_operator() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.apply_operator_change(uuid,uuid,uuid,text,uuid,timestamptz,timestamptz,text) TO impact_platform;
-- The platform role reads the register; only the definer writes it, and platform_operator stays unwritable.
GRANT SELECT ON impact.platform_operator_change TO impact_platform;
COMMIT;
```

### 0030 security privacy

Source: infrastructure/migrations/0030_security_privacy.sql

```sql
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
```

### 0031 theory of change

Source: infrastructure/migrations/0031_theory_of_change.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Theory of change, assumptions and status thresholds (v0.27 planning). Payload columns only: a
-- framework revision now carries typed relationships between its nodes (the 0002 column
-- `relationships`, written empty until this build) and the assumptions, risks and context records
-- its nodes rely on; a target carries the status thresholds its independent review approves, so the
-- band shown against an official number is the one pinned with that target at close. Additive: no
-- grant, policy, trigger or role change; both arrays and the object are JSON documents of the
-- revision payload, validated by the closed contract schemas before they are written.
ALTER TABLE impact.framework_current
 ADD COLUMN assumptions jsonb CHECK(assumptions IS NULL OR jsonb_typeof(assumptions)='array');
ALTER TABLE impact.target_current
 ADD COLUMN status_thresholds jsonb
  CHECK(status_thresholds IS NULL OR jsonb_typeof(status_thresholds)='object');
COMMIT;
```

### 0032 forms languages rounds

Source: infrastructure/migrations/0032_forms_languages_rounds.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Web forms, continued (v0.27): language versions inside the Form revision, the language a
-- response was presented in, the assignment a response fulfils, corrections of returned responses
-- and the unit a collection assignment covers. Additive only: new nullable projection columns for
-- payload properties the v0.27 contracts introduce. Collection rounds are a registry kind of 0002
-- ('CollectionRound') kept in object_registry/object_revision without a projection, like
-- CollectionPlan; no grant, role or policy changes.
--
-- Form: the language of the field definitions. The translations themselves are the existing
-- translation_versions array (empty before v0.27).
ALTER TABLE impact.form_current ADD COLUMN default_language varchar(16);
-- Submission: the language presented to the respondent, the assignment the response fulfils, and
-- for a correction the Submitted revision it supersedes with the stated reason.
ALTER TABLE impact.submission_current ADD COLUMN language varchar(16);
ALTER TABLE impact.submission_current ADD COLUMN correction_of_revision uuid;
ALTER TABLE impact.submission_current ADD COLUMN correction_reason text;
ALTER TABLE impact.submission_current ADD CONSTRAINT submission_assignment_kind
 FOREIGN KEY(tenant_id,assignment_id,assignment_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;
-- Assignment: the unit (the unit key an observation's source key starts with) the assignee is
-- expected to report for, and the history a reassignment leaves in the new revision.
ALTER TABLE impact.assignment_current ADD COLUMN unit_key varchar(100);
ALTER TABLE impact.assignment_current ADD COLUMN previous_assignee_id uuid;
ALTER TABLE impact.assignment_current ADD COLUMN reason text;
ALTER TABLE impact.assignment_current ADD CONSTRAINT assignment_round_kind
 FOREIGN KEY(tenant_id,round_id,round_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE impact.assignment_current ADD CONSTRAINT assignment_assignee
 FOREIGN KEY(tenant_id,assignee_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;
COMMIT;
```

### 0033 application executor

Source: infrastructure/migrations/0033_application_executor.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;

ALTER TABLE impact.import_job_current ADD COLUMN commit_request jsonb;

-- The application executor uses a separate LOGIN with membership in impact_app only. It never
-- receives the migration or worker role. This register tracks one governed import commit job.
CREATE TABLE impact.import_commit(
  tenant_id uuid NOT NULL,
  job_id uuid NOT NULL,
  import_id uuid NOT NULL,
  requested_by uuid NOT NULL,
  attempts integer NOT NULL DEFAULT 0 CHECK(attempts>=0),
  next_attempt_at timestamptz NOT NULL DEFAULT statement_timestamp(),
  lease_owner varchar(128) CHECK(lease_owner ~ '^[A-Za-z0-9._:-]{1,128}$'),
  last_attempt_at timestamptz,
  last_error_class varchar(64) CHECK(last_error_class ~ '^[A-Z0-9_]{1,64}$'),
  completed_at timestamptz,
  PRIMARY KEY(tenant_id,job_id),
  UNIQUE(tenant_id,import_id),
  FOREIGN KEY(tenant_id,job_id) REFERENCES impact.job(tenant_id,job_id),
  FOREIGN KEY(tenant_id,import_id) REFERENCES impact.import_job_current(tenant_id,object_id),
  FOREIGN KEY(tenant_id,requested_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX import_commit_due ON impact.import_commit(tenant_id,next_attempt_at)
  WHERE completed_at IS NULL;
ALTER TABLE impact.import_commit ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.import_commit FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.import_commit
  USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.import_commit TO impact_app;

-- The owner-side directory returns only identifiers for Active tenants with due application jobs.
-- Tenant rows and job payloads remain behind their forced RLS fences.
CREATE POLICY executor_import_directory ON impact.import_commit FOR SELECT TO impact_owner USING(true);
CREATE FUNCTION impact.executor_due_tenants(at timestamptz)
 RETURNS TABLE(tenant_id uuid) LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,impact AS $$
 SELECT DISTINCT t.tenant_id FROM impact.tenant_root t
 JOIN impact.job j ON j.tenant_id=t.tenant_id AND j.job_class='IMPORT_COMMIT'
 JOIN impact.import_commit i ON i.tenant_id=j.tenant_id AND i.job_id=j.job_id
 WHERE t.lifecycle_state='Active' AND
   ((j.state='Queued' AND j.cancellation_requested_at IS NULL AND i.next_attempt_at<=at)
    OR (j.state='Running' AND j.lease_expires_at<=at))
 ORDER BY t.tenant_id
$$;
REVOKE ALL ON FUNCTION impact.executor_due_tenants(timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.executor_due_tenants(timestamptz) TO impact_app;

-- Process health is operational metadata, never a tenant data read or an approval identity.
CREATE TABLE impact.executor_heartbeat(
 executor_id varchar(128) PRIMARY KEY CHECK(executor_id ~ '^[A-Za-z0-9._:-]{1,128}$'),
 build varchar(32) NOT NULL,
 state text NOT NULL CHECK(state IN ('RUNNING','STOPPING','STOPPED')),
 started_at timestamptz NOT NULL,
 beat_at timestamptz NOT NULL,
 stopped_at timestamptz,
 iterations bigint NOT NULL DEFAULT 0,
 succeeded bigint NOT NULL DEFAULT 0,
 failed bigint NOT NULL DEFAULT 0,
 failures bigint NOT NULL DEFAULT 0
);
GRANT SELECT,INSERT,UPDATE ON impact.executor_heartbeat TO impact_app;
GRANT SELECT ON impact.executor_heartbeat TO impact_platform;
COMMIT;
```

### 0034 AI advisory

Source: infrastructure/migrations/0034_ai_advisory.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Extend the current check, preserving kinds introduced by every prior migration.
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''AIAdvisoryRequest'')');
END $$;

CREATE TABLE impact.ai_advisory_request(
 tenant_id uuid NOT NULL,
 request_id uuid NOT NULL,
 object_id uuid NOT NULL,
 principal_id uuid NOT NULL,
 fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
 reserved_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,request_id),
 UNIQUE(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id) REFERENCES impact.object_registry(tenant_id,object_id),
 FOREIGN KEY(tenant_id,principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
CREATE INDEX ai_advisory_daily ON impact.ai_advisory_request(tenant_id,reserved_at);
CREATE TABLE impact.ai_advisory_result(
 tenant_id uuid NOT NULL,
 request_id uuid NOT NULL,
 sealed_output bytea,
 failure_reason text CHECK(failure_reason='AI_PROVIDER_UNAVAILABLE'),
 completed_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,request_id),
 FOREIGN KEY(tenant_id,request_id) REFERENCES impact.ai_advisory_request(tenant_id,request_id),
 CHECK((sealed_output IS NOT NULL) <> (failure_reason IS NOT NULL))
);
CREATE FUNCTION impact.guard_ai_advisory_insert_only() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
 BEGIN RAISE EXCEPTION 'AI advisory records are insert-only' USING ERRCODE='42501'; END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_advisory_insert_only() FROM PUBLIC;
CREATE TRIGGER ai_advisory_request_immutable BEFORE UPDATE OR DELETE ON impact.ai_advisory_request
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_advisory_insert_only();
CREATE TRIGGER ai_advisory_result_immutable BEFORE UPDATE OR DELETE ON impact.ai_advisory_result
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_advisory_insert_only();
ALTER TABLE impact.ai_advisory_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_advisory_request FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_advisory_request
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_advisory_result ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_advisory_result FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_advisory_result
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_advisory_request,impact.ai_advisory_result TO impact_app;
COMMIT;
```

## 0035_ai_adoption_plans.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Use existing forced-RLS registry/revisions/receipts; preserve every earlier kind.
DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''AIAdoptionPlan'')');
END $$;
COMMIT;
```

## 0036_reviewed_ceiling_widening.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;

-- Deployment metadata, not tenant-owned data. Only additive migrations may
-- register an exact generated profile. Runtime control-plane code can read
-- these immutable targets and cannot invent a wider profile for an old tenant.
CREATE TABLE impact.platform_access_profile(
 profile_hash varchar(64) PRIMARY KEY CHECK(profile_hash~'^[0-9a-f]{64}$'),
 manifest jsonb NOT NULL CHECK(jsonb_typeof(manifest)='object'),
 registered_at timestamptz NOT NULL DEFAULT now(), source_migration varchar(100) NOT NULL
);
GRANT SELECT ON impact.platform_access_profile TO impact_platform;
CREATE FUNCTION impact.guard_platform_access_profile() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 RAISE EXCEPTION 'registered access profile immutable' USING ERRCODE='42501';
END $$;
REVOKE ALL ON FUNCTION impact.guard_platform_access_profile() FROM PUBLIC;
CREATE TRIGGER platform_access_profile_guard BEFORE UPDATE OR DELETE ON impact.platform_access_profile
 FOR EACH ROW EXECUTE FUNCTION impact.guard_platform_access_profile();
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration) VALUES('48e75c64f1ea2ddceeadce089d1c3f2b056254f236060f1c7d4a18ff439183b0',$profile_0036${"purpose_bound":["audit.export","privacy-cases.draft.create","privacy-cases.draft.edit","privacy-cases.read","privacy.approve","privacy.execute","privacy.export"],"roles":{"ANALYST":["ai.enablement.read","calculated-results.read","dashboards.read","decisions.read","evidence.download","evidence.read","framework.export","frameworks.read","imports.read","indicator-definitions.read","indicator-instances.read","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"AUDIT_READER":["audit-events.read","notifications.read","uploads.read"],"AUTHOR":["ai.enablement.read","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","disclosure.request","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.draft.create","observations.draft.edit","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","report.submit","reporting-calendars.read","reports.draft.create","reports.draft.edit","reports.read","restatement-requests.read","snapshots.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"DATA_STEWARD":["ai.enablement.read","assignments.read","calculated-results.read","dashboards.read","decisions.read","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","forms.read","frameworks.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","notifications.read","observations.draft.create","observations.draft.edit","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","submissions.read","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflows.read"],"ENUMERATOR":["assignments.read","collection-rounds.read","forms.read","notifications.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","upload.create","upload.write","uploads.read"],"EXTERNAL":["calculated-results.read","dashboards.read","decisions.read","evidence.read","frameworks.read","indicator-definitions.read","indicator-instances.read","invitation.accept","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"MEL_ADMIN":["ai.advisory.request","ai.enablement.manage","ai.enablement.read","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","disclosures.read","evidence.read","form.publish","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.export","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.activate","indicator.calculate","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","report.publish","report.withdraw","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"PRIVACY":["disclosure.request","disclosures.read","notifications.read","publication.download","report.withdraw","reports.read","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","uploads.read"],"PROGRAMME_MANAGER":["ai.advisory.request","ai.enablement.manage","ai.enablement.read","assignment.reassign","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","evidence.read","form.submit","forms.read","framework.export","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","indicator.activate","indicator.calculate","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"REVIEWER":["ai.enablement.read","assignments.read","calculated-results.read","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","evidence.download","evidence.read","forms.read","frameworks.read","geographies.read","imports.read","indicator-definitions.read","indicator-instances.read","lineage-manifests.read","measurement-changes.read","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflow.approve","workflow.reject","workflow.return","workflows.read"],"TENANT_ADMIN":["access-denials.read","access-requests.read","access-scopes.create","access-scopes.read","ai.advisory.request","ai.enablement.manage","ai.enablement.read","connections.read","grant.approve","grant.request","grant.revoke","grants.read","groups.approve","groups.manage","groups.read","groups.request","member-invitations.read","member.invite","membership.reactivate","membership.renew.approve","membership.renew.request","membership.revoke","membership.suspend","memberships.read","notifications.read","organisation-units.manage","organisation-units.read","ownership.transfer","reference-data.manage","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","role-templates.read","roles.manage","uploads.read"]},"version":"initial-access-v2"}$profile_0036$::jsonb,'0036_reviewed_ceiling_widening.sql');

-- Existing applied profiles stay unchanged until the owner, named second
-- administrator and an independent active platform operator review an upgrade.
ALTER TABLE impact.tenant_access_bootstrap ADD CONSTRAINT access_bootstrap_tenant_request
 UNIQUE(tenant_id,request_id);

CREATE TABLE impact.tenant_access_upgrade(
 tenant_id uuid NOT NULL REFERENCES impact.tenant_onboarding,
 request_id uuid NOT NULL, revision_id uuid NOT NULL,
 state varchar(20) NOT NULL CHECK(state IN ('Requested','Accepted','Applied','Rejected','Cancelled')),
 bootstrap_request_id uuid NOT NULL,
 owner_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 second_identity_id uuid NOT NULL REFERENCES impact.auth_identity,
 tenant_revision uuid NOT NULL, owner_revision uuid NOT NULL,
 current_manifest jsonb NOT NULL CHECK(jsonb_typeof(current_manifest)='object'),
 authority_hash varchar(64) NOT NULL CHECK(authority_hash~'^[0-9a-f]{64}$'),
 profile_hash varchar(64) NOT NULL REFERENCES impact.platform_access_profile,
 target_manifest jsonb NOT NULL CHECK(jsonb_typeof(target_manifest)='object'),
 new_capabilities jsonb NOT NULL CHECK(jsonb_typeof(new_capabilities)='array'),
 review_expires_at timestamptz NOT NULL,
 owner_auth_time timestamptz NOT NULL, second_auth_time timestamptz,
 accepted_at timestamptz, approved_by uuid REFERENCES impact.auth_identity,
 approved_auth_time timestamptz, applied_at timestamptz,
 reason varchar(1000) NOT NULL CHECK(reason~'\S'),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant_id,request_id), UNIQUE(request_id),
 FOREIGN KEY(tenant_id,bootstrap_request_id) REFERENCES impact.tenant_access_bootstrap(tenant_id,request_id),
 CHECK(owner_identity_id<>second_identity_id),
 CHECK(review_expires_at>created_at AND review_expires_at<=created_at+interval '7 days'),
 CHECK((state IN ('Accepted','Applied'))=(accepted_at IS NOT NULL AND second_auth_time IS NOT NULL)
       OR state IN ('Rejected','Cancelled')),
 CHECK((state='Applied')=(approved_by IS NOT NULL AND approved_auth_time IS NOT NULL AND applied_at IS NOT NULL))
);
CREATE UNIQUE INDEX access_upgrade_one_live ON impact.tenant_access_upgrade(tenant_id)
 WHERE state IN ('Requested','Accepted');
ALTER TABLE impact.tenant_access_upgrade ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_access_upgrade FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_access_upgrade
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Only the owner-executed bounded inbox selector can discover tenant IDs
-- before transaction-local tenant context is known. Runtime roles stay fenced.
CREATE POLICY access_upgrade_owner_directory ON impact.tenant_access_upgrade TO impact_owner USING(true);
GRANT SELECT,INSERT,UPDATE ON impact.tenant_access_upgrade TO impact_platform;

CREATE TABLE impact.tenant_access_upgrade_applied(
 tenant_id uuid NOT NULL, request_id uuid NOT NULL,
 applied_at timestamptz NOT NULL DEFAULT now(), authorities_added integer NOT NULL CHECK(authorities_added>=0),
 PRIMARY KEY(tenant_id,request_id),
 FOREIGN KEY(tenant_id,request_id) REFERENCES impact.tenant_access_upgrade(tenant_id,request_id)
);
ALTER TABLE impact.tenant_access_upgrade_applied ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.tenant_access_upgrade_applied FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.tenant_access_upgrade_applied
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT ON impact.tenant_access_upgrade_applied TO impact_platform;

CREATE FUNCTION impact.access_upgrade_refs(viewer uuid, after_request uuid)
 RETURNS TABLE(tenant_id uuid,request_id uuid)
 LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT u.tenant_id,u.request_id FROM impact.tenant_access_upgrade u
 JOIN impact.tenant_onboarding o ON o.tenant_id=u.tenant_id
 WHERE (impact.lock_platform_operator(viewer)
        OR (viewer=o.owner_identity_id AND viewer=u.owner_identity_id)
        OR (viewer=u.second_identity_id AND EXISTS(
            SELECT 1 FROM impact.auth_identity i JOIN impact.identity_profile p USING(identity_id)
            WHERE i.identity_id=viewer AND p.verified_email_hash IS NOT NULL)))
 AND (after_request IS NULL OR u.request_id>after_request)
 ORDER BY u.request_id LIMIT 51
$$;
REVOKE ALL ON FUNCTION impact.access_upgrade_refs(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.access_upgrade_refs(uuid,uuid) TO impact_platform;

-- Principal epochs are metadata about the viewer only. The existing
-- principal_identity_directory owner policy supports this global visibility
-- fingerprint without granting any cross-tenant runtime table access.
CREATE FUNCTION impact.access_upgrade_visibility(viewer uuid) RETURNS jsonb
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE previous_context text:=current_setting('impact.tenant_id',true); person record;
 principals jsonb:='[]'::jsonb; members jsonb; authorities jsonb;
BEGIN
 FOR person IN SELECT p.* FROM impact.tenant_principal p WHERE p.identity_id=viewer ORDER BY p.tenant_id,p.principal_id LOOP
  PERFORM set_config('impact.tenant_id',person.tenant_id::text,true);
  SELECT COALESCE(jsonb_agg(jsonb_build_object('member',m.object_id,'revision',h.head_revision,
    'state',h.lifecycle_state,'status',m.status,'expiry',m.expires_at,
    'unexpired',m.expires_at IS NULL OR m.expires_at>now()) ORDER BY m.object_id),'[]'::jsonb)
    INTO members FROM impact.membership_current m JOIN impact.object_registry h
    ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
    WHERE m.tenant_id=person.tenant_id AND m.identity_id=viewer;
  SELECT COALESCE(jsonb_agg(jsonb_build_object('authority',a.authority_id,'capability',a.capability,
    'scope',a.scope_id,'expiry',a.expires_at) ORDER BY a.authority_id),'[]'::jsonb)
    INTO authorities FROM impact.grant_authority a WHERE a.tenant_id=person.tenant_id
    AND a.principal_id=person.principal_id AND a.expires_at>now();
  principals:=principals||jsonb_build_array(jsonb_build_object('tenant',person.tenant_id,
    'principal',person.principal_id,'active',person.active,'epoch',person.subject_epoch,
    'cutoff',person.auth_not_before,'members',members,'authorities',authorities));
 END LOOP;
 PERFORM set_config('impact.tenant_id',COALESCE(previous_context,''),true);
 RETURN jsonb_build_object(
  'operator',(SELECT to_jsonb(o) FROM impact.platform_operator o WHERE o.identity_id=viewer),
  'operator_current',impact.lock_platform_operator(viewer),
  'identity_cutoff',(SELECT s.auth_not_before FROM impact.identity_security_state s WHERE s.identity_id=viewer),
  'principals',principals);
END $$;
REVOKE ALL ON FUNCTION impact.access_upgrade_visibility(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.access_upgrade_visibility(uuid) TO impact_platform;

CREATE FUNCTION impact.guard_access_upgrade() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'access upgrade immutable' USING ERRCODE='42501'; END IF;
 IF TG_OP='INSERT' THEN
  IF NEW.state<>'Requested' OR NEW.accepted_at IS NOT NULL OR NEW.second_auth_time IS NOT NULL
  OR NEW.approved_by IS NOT NULL OR NEW.applied_at IS NOT NULL THEN
   RAISE EXCEPTION 'access upgrade must start requested' USING ERRCODE='42501';
  END IF;
  RETURN NEW;
 END IF;
 IF OLD.state IN ('Applied','Rejected','Cancelled') THEN
  RAISE EXCEPTION 'access upgrade final' USING ERRCODE='42501';
 END IF;
 IF (to_jsonb(NEW)-ARRAY['state','revision_id','updated_at','second_auth_time','accepted_at',
                       'approved_by','approved_auth_time','applied_at'])
 IS DISTINCT FROM
 (to_jsonb(OLD)-ARRAY['state','revision_id','updated_at','second_auth_time','accepted_at',
                       'approved_by','approved_auth_time','applied_at']) THEN
  RAISE EXCEPTION 'access upgrade identity immutable' USING ERRCODE='42501';
 END IF;
 IF NOT ((OLD.state='Requested' AND NEW.state IN ('Accepted','Rejected','Cancelled'))
      OR (OLD.state='Accepted' AND NEW.state IN ('Applied','Rejected','Cancelled'))) THEN
  RAISE EXCEPTION 'invalid access upgrade transition' USING ERRCODE='42501';
 END IF;
 IF NEW.state='Applied' AND current_user<>'impact_owner' THEN
  RAISE EXCEPTION 'access upgrade applicator required' USING ERRCODE='42501';
 END IF;
 IF OLD.state='Accepted' AND (NEW.second_auth_time IS DISTINCT FROM OLD.second_auth_time
                             OR NEW.accepted_at IS DISTINCT FROM OLD.accepted_at) THEN
  RAISE EXCEPTION 'access upgrade consent immutable' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_access_upgrade() FROM PUBLIC;
CREATE TRIGGER access_upgrade_guard BEFORE INSERT OR UPDATE OR DELETE ON impact.tenant_access_upgrade
 FOR EACH ROW EXECUTE FUNCTION impact.guard_access_upgrade();

CREATE FUNCTION impact.guard_access_upgrade_applied() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 RAISE EXCEPTION 'access upgrade applied marker immutable' USING ERRCODE='42501';
END $$;
REVOKE ALL ON FUNCTION impact.guard_access_upgrade_applied() FROM PUBLIC;
CREATE TRIGGER access_upgrade_applied_guard BEFORE UPDATE OR DELETE ON impact.tenant_access_upgrade_applied
 FOR EACH ROW EXECUTE FUNCTION impact.guard_access_upgrade_applied();

-- Fixed search path, tenant-scoped selector, exact pre-change ceiling and
-- consent checks, one-use marker. No runtime role receives INSERT on ceilings.
CREATE FUNCTION impact.apply_access_upgrade(tenant uuid, requested uuid, approver uuid, authenticated timestamptz)
 RETURNS integer LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE r impact.tenant_access_upgrade; p jsonb; item jsonb; added integer:=0;
 expected integer; actual integer; principal uuid; scope uuid; expiry timestamptz;
 cap text; owner_person uuid; second_person uuid; approver_person uuid;
BEGIN
 IF tenant IS DISTINCT FROM impact.current_tenant() THEN
  RAISE EXCEPTION 'access upgrade denied' USING ERRCODE='42501';
 END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(tenant::text,0));
 SELECT * INTO r FROM impact.tenant_access_upgrade WHERE tenant_id=tenant AND request_id=requested FOR UPDATE;
 IF NOT FOUND OR r.state<>'Accepted' OR r.accepted_at IS NULL OR r.second_auth_time IS NULL
 OR r.review_expires_at<=now() OR r.review_expires_at>r.created_at+interval '7 days'
 OR authenticated IS NULL OR authenticated<=now()-interval '300 seconds' OR authenticated>now()
 OR NOT impact.lock_platform_operator(approver)
 OR EXISTS(SELECT 1 FROM impact.tenant_access_upgrade_applied WHERE tenant_id=tenant AND request_id=requested)
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_root WHERE tenant_id=tenant AND lifecycle_state='Active')
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_onboarding WHERE tenant_id=tenant
               AND revision_id=r.tenant_revision AND owner_identity_id=r.owner_identity_id)
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_access_bootstrap_applied
               WHERE tenant_id=tenant AND request_id=r.bootstrap_request_id)
 OR NOT EXISTS(SELECT 1 FROM impact.platform_access_profile p
               WHERE p.profile_hash=r.profile_hash AND p.manifest=r.target_manifest)
 OR EXISTS(SELECT 1 FROM impact.tenant_authority_renewal WHERE tenant_id=tenant AND state IN ('Requested','Accepted'))
 THEN RAISE EXCEPTION 'access upgrade denied' USING ERRCODE='42501'; END IF;

 SELECT natural_identity_id INTO owner_person FROM impact.auth_identity WHERE identity_id=r.owner_identity_id;
 SELECT natural_identity_id INTO second_person FROM impact.auth_identity WHERE identity_id=r.second_identity_id;
 SELECT natural_identity_id INTO approver_person FROM impact.auth_identity WHERE identity_id=approver;
 IF owner_person IS NULL OR second_person IS NULL OR approver_person IS NULL
 OR owner_person=second_person OR approver_person IN(owner_person,second_person)
 OR EXISTS(SELECT 1 FROM impact.identity_security_state s WHERE
           (s.identity_id=r.owner_identity_id AND r.owner_auth_time<=s.auth_not_before)
        OR (s.identity_id=r.second_identity_id AND r.second_auth_time<=s.auth_not_before)
        OR (s.identity_id=approver AND authenticated<=s.auth_not_before))
 OR NOT EXISTS(SELECT 1 FROM impact.tenant_custody t JOIN impact.membership_current m
               ON m.tenant_id=t.tenant_id AND m.object_id=t.owner_membership_id
               JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
               JOIN impact.tenant_principal o ON o.tenant_id=m.tenant_id AND o.identity_id=m.identity_id
               WHERE t.tenant_id=tenant AND m.identity_id=r.owner_identity_id AND h.head_revision=r.owner_revision
               AND h.lifecycle_state='Active' AND o.active AND (m.expires_at IS NULL OR m.expires_at>now())
               AND (o.auth_not_before IS NULL OR r.owner_auth_time>o.auth_not_before))
 THEN RAISE EXCEPTION 'access upgrade consent denied' USING ERRCODE='42501'; END IF;

 IF jsonb_array_length(r.current_manifest->'principals')<>2 THEN
  RAISE EXCEPTION 'access upgrade principals denied' USING ERRCODE='42501';
 END IF;
 SELECT count(*) INTO expected FROM jsonb_array_elements(r.current_manifest->'authority_rows');
 SELECT count(*) INTO actual FROM impact.grant_authority a
 WHERE a.tenant_id=tenant AND a.expires_at>now() AND a.principal_id IN
 (SELECT (v->>'principal_id')::uuid FROM jsonb_array_elements(r.current_manifest->'principals') v);
 IF expected<>actual THEN RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501'; END IF;
 FOR item IN SELECT value FROM jsonb_array_elements(r.current_manifest->'authority_rows') LOOP
  IF NOT EXISTS(SELECT 1 FROM impact.grant_authority a WHERE a.tenant_id=tenant
    AND a.authority_id=(item->>'authority_id')::uuid AND a.principal_id=(item->>'principal_id')::uuid
    AND a.capability=item->>'capability' AND a.scope_id=(item->>'scope_id')::uuid
    AND a.expires_at=(item->>'expires_at')::timestamptz AND a.expires_at>now()) THEN
   RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501';
  END IF;
 END LOOP;
 FOR item IN SELECT value FROM jsonb_array_elements(r.current_manifest->'grant_revisions')
 UNION ALL SELECT value FROM jsonb_array_elements(r.current_manifest->'membership_revisions') LOOP
  IF NOT EXISTS(SELECT 1 FROM impact.object_registry h JOIN impact.object_revision v
    ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision
    WHERE h.tenant_id=tenant AND h.object_id=(item->>'object_id')::uuid
    AND h.head_revision=(item->>'revision_id')::uuid AND h.lifecycle_state='Active'
    AND encode(v.payload_sha256,'hex')=item->>'payload_sha256') THEN
   RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501';
  END IF;
 END LOOP;
 FOR item IN SELECT value FROM jsonb_array_elements(r.current_manifest->'managed_roles') LOOP
  IF NOT EXISTS(SELECT 1 FROM impact.object_registry h JOIN impact.object_revision v
    ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision
    WHERE h.tenant_id=tenant AND h.object_id=(item->>'object_id')::uuid
    AND h.head_revision=(item->>'revision_id')::uuid AND h.lifecycle_state=item->>'state'
    AND encode(v.payload_sha256,'hex')=item->>'payload_sha256') THEN
   RAISE EXCEPTION 'AUTHORITY_CHANGED' USING ERRCODE='42501';
  END IF;
 END LOOP;
 -- Source baseline is an immutable applied manifest; revoked baseline
 -- capabilities cannot be classified as new and silently resurrected.
 IF (r.current_manifest->>'source_request_id')::uuid IS DISTINCT FROM COALESCE(
  (SELECT u.request_id FROM impact.tenant_access_upgrade u WHERE u.tenant_id=tenant AND u.state='Applied'
   ORDER BY u.applied_at DESC,u.request_id DESC LIMIT 1),r.bootstrap_request_id) THEN
  RAISE EXCEPTION 'access upgrade source stale' USING ERRCODE='42501';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.tenant_access_upgrade u WHERE u.tenant_id=tenant AND u.state='Applied'
               AND u.request_id=(r.current_manifest->>'source_request_id')::uuid
               AND u.target_manifest=r.current_manifest->'source_manifest')
 AND NOT EXISTS(SELECT 1 FROM impact.tenant_access_bootstrap b WHERE b.tenant_id=tenant AND b.state='Applied'
                AND b.request_id=r.bootstrap_request_id AND b.request_id=(r.current_manifest->>'source_request_id')::uuid
                AND b.manifest=r.current_manifest->'source_manifest') THEN
  RAISE EXCEPTION 'access upgrade source denied' USING ERRCODE='42501';
 END IF;
 IF EXISTS(SELECT 1 FROM jsonb_each(r.current_manifest->'source_manifest'->'roles') source
  WHERE NOT (r.target_manifest->'roles' ? source.key)
  OR NOT (r.target_manifest->'roles'->source.key @> source.value))
 OR NOT (COALESCE(r.target_manifest->'purpose_bound','[]'::jsonb)
         @> COALESCE(r.current_manifest->'source_manifest'->'purpose_bound','[]'::jsonb)) THEN
  RAISE EXCEPTION 'access upgrade profile not monotonic' USING ERRCODE='42501';
 END IF;
 IF r.new_capabilities IS DISTINCT FROM COALESCE((SELECT jsonb_agg(delta.cap ORDER BY delta.cap)
  FROM (SELECT jsonb_array_elements_text(value) AS cap FROM jsonb_each(r.target_manifest->'roles')
        UNION SELECT jsonb_array_elements_text(COALESCE(r.target_manifest->'purpose_bound','[]'::jsonb))
        EXCEPT (SELECT jsonb_array_elements_text(value) FROM jsonb_each(r.current_manifest->'source_manifest'->'roles')
                UNION SELECT jsonb_array_elements_text(COALESCE(r.current_manifest->'source_manifest'->'purpose_bound','[]'::jsonb)))) delta),'[]'::jsonb) THEN
  RAISE EXCEPTION 'access upgrade delta denied' USING ERRCODE='42501';
 END IF;
 IF EXISTS(SELECT 1 FROM jsonb_array_elements_text(r.new_capabilities) n
  WHERE n.value IN(SELECT jsonb_array_elements_text(value) FROM jsonb_each(r.current_manifest->'source_manifest'->'roles')
                   UNION SELECT jsonb_array_elements_text(COALESCE(r.current_manifest->'source_manifest'->'purpose_bound','[]'::jsonb))))
 OR EXISTS(SELECT 1 FROM jsonb_array_elements_text(r.new_capabilities) n
  WHERE n.value NOT IN(SELECT jsonb_array_elements_text(value) FROM jsonb_each(r.target_manifest->'roles')
                       UNION SELECT jsonb_array_elements_text(COALESCE(r.target_manifest->'purpose_bound','[]'::jsonb)))) THEN
  RAISE EXCEPTION 'access upgrade delta denied' USING ERRCODE='42501';
 END IF;

 FOR p IN SELECT value FROM jsonb_array_elements(r.current_manifest->'principals') LOOP
  principal:=(p->>'principal_id')::uuid; scope:=(p->>'scope_id')::uuid;
  IF (p->>'identity_id')::uuid NOT IN(r.owner_identity_id,r.second_identity_id)
  OR NOT EXISTS(SELECT 1 FROM impact.tenant_principal t WHERE t.tenant_id=tenant AND t.principal_id=principal
                AND t.identity_id=(p->>'identity_id')::uuid AND t.active
                AND (t.auth_not_before IS NULL OR
                     CASE WHEN t.identity_id=r.owner_identity_id THEN r.owner_auth_time ELSE r.second_auth_time END>t.auth_not_before))
  OR NOT EXISTS(SELECT 1 FROM impact.membership_current m JOIN impact.object_registry h
                ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
                WHERE m.tenant_id=tenant AND m.object_id=(p->>'membership_id')::uuid
                AND m.identity_id=(p->>'identity_id')::uuid AND h.lifecycle_state='Active'
                AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now()))
  THEN RAISE EXCEPTION 'access upgrade membership denied' USING ERRCODE='42501'; END IF;
  SELECT min(a.expires_at) INTO expiry FROM impact.grant_authority a
   WHERE a.tenant_id=tenant AND a.principal_id=principal AND a.expires_at>now();
  IF expiry IS NULL OR expiry<r.review_expires_at THEN
   RAISE EXCEPTION 'access upgrade expiry denied' USING ERRCODE='42501';
  END IF;
  FOR cap IN SELECT value FROM jsonb_array_elements_text(r.new_capabilities) LOOP
   IF NOT EXISTS(SELECT 1 FROM impact.grant_authority a WHERE a.tenant_id=tenant
                  AND a.principal_id=principal AND a.capability=cap AND a.scope_id=scope AND a.expires_at>now()) THEN
    INSERT INTO impact.grant_authority(tenant_id,authority_id,principal_id,capability,scope_id,expires_at)
     VALUES(tenant,gen_random_uuid(),principal,cap,scope,expiry);
    added:=added+1;
   END IF;
  END LOOP;
 END LOOP;
 INSERT INTO impact.tenant_access_upgrade_applied(tenant_id,request_id,authorities_added) VALUES(tenant,requested,added);
 UPDATE impact.tenant_access_upgrade SET state='Applied',approved_by=approver,approved_auth_time=authenticated,
  applied_at=now(),updated_at=now(),revision_id=gen_random_uuid() WHERE tenant_id=tenant AND request_id=requested;
 RETURN added;
END $$;
REVOKE ALL ON FUNCTION impact.apply_access_upgrade(uuid,uuid,uuid,timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.apply_access_upgrade(uuid,uuid,uuid,timestamptz) TO impact_platform;
COMMIT;
```

## 0037_ai_content_snapshots.sql

```sql
BEGIN;
SET LOCAL ROLE impact_owner;
-- Editorial guidance is captured only when a new adoption-plan revision is saved.
-- No old revision is backfilled from current content or re-pointed to another edition.
CREATE TABLE impact.ai_content_snapshot(
 tenant_id uuid NOT NULL,
 snapshot_id uuid NOT NULL,
 schema_version varchar(64) NOT NULL CHECK(schema_version='nonprofit-ai-guidance-v1'),
 payload jsonb NOT NULL CHECK(jsonb_typeof(payload)='object'),
 payload_sha256 bytea NOT NULL CHECK(octet_length(payload_sha256)=32),
 captured_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,snapshot_id),
 UNIQUE(tenant_id,payload_sha256),
 FOREIGN KEY(tenant_id) REFERENCES impact.tenant_root(tenant_id)
);
-- A bundle can legitimately share unchanged components with other bundles.
-- Under the tenant write lock the server checks a component edition's exact words;
-- these non-unique indexes support that bounded lookup without cross-tenant reads.
CREATE INDEX ai_content_catalog_edition ON impact.ai_content_snapshot
 (tenant_id,(payload->'catalog'->>'content_version'));
CREATE INDEX ai_content_solutions_edition ON impact.ai_content_snapshot
 (tenant_id,(payload->'solutions'->>'content_version'));
CREATE INDEX ai_content_practice_edition ON impact.ai_content_snapshot
 (tenant_id,(payload->'practice'->>'content_version'));
CREATE TABLE impact.ai_plan_content_binding(
 tenant_id uuid NOT NULL,
 object_id uuid NOT NULL,
 revision_id uuid NOT NULL,
 revision_kind text GENERATED ALWAYS AS ('AIAdoptionPlan') STORED,
 snapshot_id uuid NOT NULL,
 PRIMARY KEY(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,object_id,revision_id)
   REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,revision_id,revision_kind)
   REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,snapshot_id)
   REFERENCES impact.ai_content_snapshot(tenant_id,snapshot_id)
);
CREATE FUNCTION impact.guard_ai_content_insert_only() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
 BEGIN RAISE EXCEPTION 'AI content archives are insert-only' USING ERRCODE='42501'; END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_content_insert_only() FROM PUBLIC;
CREATE TRIGGER ai_content_snapshot_immutable BEFORE UPDATE OR DELETE ON impact.ai_content_snapshot
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_content_insert_only();
CREATE TRIGGER ai_plan_content_binding_immutable BEFORE UPDATE OR DELETE ON impact.ai_plan_content_binding
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_content_insert_only();
ALTER TABLE impact.ai_content_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_content_snapshot FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_content_snapshot
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_plan_content_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_plan_content_binding FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_plan_content_binding
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_content_snapshot,impact.ai_plan_content_binding TO impact_app;
COMMIT;
```


## 0038_human_advice_cases.sql

Source: infrastructure/migrations/0038_human_advice_cases.sql. SHA-256: `ace70f9e77a2636df7e0cf5f85f5ffd29de74af8efa94df6e5804077e5331e00`.

Registered local build 0.33 candidate, not merged or deployed. The integrator copied the exact reviewed isolated draft into migration 0038 after disposable PostgreSQL 17.11 SQL/helper/RLS qualification (68 checks; `docs/evidence/sprint-0.33-human-advice-scratch-native.json`). That proof used existing checksum-ledgered schema 37 plus the explicitly unledgered draft, with a fixture superuser assuming non-owner runtime roles. It is not a schema-38 application/native-login/acceptance run. The original draft-provenance comments are retained in the frozen SQL below. Registered migrations0038/0039 and the participant API now pass the source-bound122-check PGlite focus (`docs/evidence/sprint-0.33-human-advice-pglite-tests.xml`), with six explicit native-only skips and actual schema39 checksum ledger. Focused actual PostgreSQL17.11 native-login qualification subsequently passes142 checks with no failures/errors/skips (`docs/evidence/sprint-0.33-human-advice-native-tests.xml`), actual39-migration checksum ledger and unchanged171-source proof. The six synthetic NOINHERIT login topologies are verified, including executor privacy. The authorised persisted map was applied once to owned synthetic cluster logins; later runs reuse it. Browser/full-release restart/restore/upgrade/acceptance qualification is still pending.

Advice is from an existing organisation member with current scoped AI read/manage on an exact saved AI adoption plan; membership is not employment, certification, availability or supplier onboarding. The new `HumanAdviceCase` kind is excluded from generic entity/API dispatch. Both new tables use tenant-qualified primary and foreign keys, ENABLE/FORCE RLS and `tenant_fence`.

| Table | Column | Type/nullability/default | Constraint or purpose |
|---|---|---|---|
| human_advice_case_current | tenant_id | uuid NOT NULL | Composite primary key and every foreign key; transaction-local current tenant fence |
| human_advice_case_current | object_id | uuid NOT NULL | Composite primary key; typed HumanAdviceCase registry FK, deferred until commit |
| human_advice_case_current | revision_id | uuid NOT NULL | Tenant/object/revision FK, deferred until commit; final current head consistency |
| human_advice_case_current | object_type | text NOT NULL DEFAULT HumanAdviceCase | CHECK constant; typed registry FK |
| human_advice_case_current | context_plan_id | uuid NOT NULL | Typed tenant/object/AIAdoptionPlan registry FK; immutable plan selector |
| human_advice_case_current | context_plan_revision | uuid NOT NULL | Tenant/object/revision FK; immutable exact plan revision consent anchor |
| human_advice_case_current | context_plan_type | text NOT NULL DEFAULT AIAdoptionPlan | CHECK constant for typed plan FK |
| human_advice_case_current | requester_principal_id | uuid NOT NULL | Tenant-qualified principal FK; immutable named participant |
| human_advice_case_current | requester_membership_id | uuid NOT NULL | Tenant-qualified membership FK; current active/expiry proof |
| human_advice_case_current | requester_natural_id | uuid NOT NULL | Immutable server-resolved natural-person pin; current identity proof guard |
| human_advice_case_current | adviser_principal_id | uuid NOT NULL | Tenant-qualified principal FK; differs from requester |
| human_advice_case_current | adviser_membership_id | uuid NOT NULL | Tenant-qualified membership FK; current active/expiry proof |
| human_advice_case_current | adviser_natural_id | uuid NOT NULL | Immutable server-resolved natural-person pin; differs from requester |
| human_advice_case_current | case_state | text NOT NULL | Open, Assigned, AwaitingInput, AdviceDraft, Closed or Cancelled; terminal immutable |
| human_advice_private_brief | tenant_id | uuid NOT NULL | Composite primary key and participant projection FK; current tenant fence |
| human_advice_private_brief | object_id | uuid NOT NULL | Composite primary key and tenant-qualified projection FK |
| human_advice_private_brief | problem | text NOT NULL | Nonblank, 1–4000 characters; immutable private brief |
| human_advice_private_brief | problem_sha256 | bytea NOT NULL | Exactly 32 bytes; shared stored payload contains only the salted hex integrity digest |
| human_advice_private_brief | brief_nonce | uuid NOT NULL | Private random salt; never included in shared invitation payload |

`impact_app` has SELECT/INSERT/UPDATE on the participant projection and SELECT/INSERT on the immutable private brief. The requester retains current-authorised access to terminal records; the adviser loses case/history/receipt access immediately at Closed/Cancelled and sees the brief only after explicit assignment. Owner-definer helpers with fixed `pg_catalog,impact` search paths prove current active selected membership, expiry, natural person, available plan and current scoped AI read. A transaction-local principal GUC is server-resolved after application authentication; it guards missing/mis-scoped application context and does not authenticate a human against a compromised database login.

The additive restrictive policies also protect case-related generic registry/revision, natural author, audit projection, operation receipt, outbox event, delivery and consumer receipt pointers. Other runtime roles cannot read these rows. Standard case outbox intent has no delivery channel; it grants no worker delivery authority. Deferred tenant-qualified FKs and final-head/private-brief consistency seal the participant-first creation transaction. Material plan consent, conflict declaration, assignment, complete action acknowledgement and fresh writes are application checks; no new database-role privilege or provider/disclosure authority is implied. Dedicated brief retention/removal and an operated external adviser service remain future work.

```sql
-- Isolated 0.33 candidate; intentionally outside the applied migration directory.
-- The integrator assigns its contiguous migration number after the 0.32 checkpoint.
BEGIN;
SET LOCAL ROLE impact_owner;

DO $$ DECLARE original_check text;
BEGIN
 SELECT pg_get_constraintdef(oid) INTO STRICT original_check FROM pg_constraint
 WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check';
 ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
 EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
   || regexp_replace(original_check, '\)$', ' OR object_type = ''HumanAdviceCase'')');
END $$;

CREATE TABLE impact.human_advice_case_current(
 tenant_id uuid NOT NULL, object_id uuid NOT NULL, revision_id uuid NOT NULL,
 object_type text NOT NULL DEFAULT 'HumanAdviceCase' CHECK(object_type='HumanAdviceCase'),
 context_plan_id uuid NOT NULL, context_plan_revision uuid NOT NULL,
 context_plan_type text NOT NULL DEFAULT 'AIAdoptionPlan' CHECK(context_plan_type='AIAdoptionPlan'),
 requester_principal_id uuid NOT NULL, requester_membership_id uuid NOT NULL, requester_natural_id uuid NOT NULL,
 adviser_principal_id uuid NOT NULL, adviser_membership_id uuid NOT NULL, adviser_natural_id uuid NOT NULL,
 case_state text NOT NULL CHECK(case_state IN ('Open','Assigned','AwaitingInput','AdviceDraft','Closed','Cancelled')),
 PRIMARY KEY(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id,object_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,object_id,revision_id) REFERENCES impact.object_revision(tenant_id,object_id,revision_id) DEFERRABLE INITIALLY DEFERRED,
 FOREIGN KEY(tenant_id,context_plan_id,context_plan_type) REFERENCES impact.object_registry(tenant_id,object_id,object_type),
 FOREIGN KEY(tenant_id,context_plan_id,context_plan_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,requester_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,adviser_principal_id) REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,requester_membership_id) REFERENCES impact.membership_current(tenant_id,object_id),
 FOREIGN KEY(tenant_id,adviser_membership_id) REFERENCES impact.membership_current(tenant_id,object_id),
 CHECK(requester_principal_id<>adviser_principal_id AND requester_natural_id<>adviser_natural_id)
);
ALTER TABLE impact.human_advice_case_current ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.human_advice_case_current FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.human_advice_case_current
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT,UPDATE ON impact.human_advice_case_current TO impact_app;

CREATE TABLE impact.human_advice_private_brief(
 tenant_id uuid NOT NULL,object_id uuid NOT NULL,
 problem text NOT NULL CHECK(length(problem) BETWEEN 1 AND 4000 AND problem ~ '\S'),
 problem_sha256 bytea NOT NULL CHECK(octet_length(problem_sha256)=32),
 brief_nonce uuid NOT NULL,
 PRIMARY KEY(tenant_id,object_id),
 FOREIGN KEY(tenant_id,object_id) REFERENCES impact.human_advice_case_current(tenant_id,object_id)
);
ALTER TABLE impact.human_advice_private_brief ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.human_advice_private_brief FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.human_advice_private_brief
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.human_advice_private_brief TO impact_app;

-- The application sets this only after resolving the authenticated current member,
-- transaction-locally. A writable GUC guards uncertain/missing application context;
-- it does not authenticate a human against a compromised impact_app database login.
CREATE FUNCTION impact.human_advice_principal() RETURNS uuid
 LANGUAGE sql STABLE SET search_path=pg_catalog,impact AS $$
 SELECT nullif(current_setting('impact.human_advice_principal',true),'')::uuid
$$;
REVOKE ALL ON FUNCTION impact.human_advice_principal() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_principal() TO impact_app;

CREATE FUNCTION impact.human_advice_read_scope(principal uuid,membership uuid,anchor uuid) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(SELECT 1 FROM (
  SELECT g.capability,g.scope_id,s.scope_type FROM impact.grant_current g
  JOIN impact.object_registry h ON h.tenant_id=g.tenant_id AND h.object_id=g.object_id
  JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id
  WHERE g.tenant_id=impact.current_tenant() AND g.subject_id=principal AND g.purpose IS NULL
    AND h.lifecycle_state='Active' AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now())
  UNION ALL SELECT e.capability,e.scope_id,s.scope_type FROM impact.group_entitlement e
  JOIN impact.object_registry h ON h.tenant_id=e.tenant_id AND h.object_id=e.group_id
  JOIN impact.scope_definition s ON s.tenant_id=e.tenant_id AND s.scope_id=e.scope_id
  WHERE e.tenant_id=impact.current_tenant() AND e.membership_id=membership
    AND e.expires_at>now() AND h.lifecycle_state='Active'
 ) g WHERE g.capability='ai.enablement.read' AND (g.scope_type='TENANT'
   OR EXISTS(SELECT 1 FROM impact.scope_member sm WHERE sm.tenant_id=impact.current_tenant()
             AND sm.scope_id=g.scope_id AND sm.object_id=anchor)))
$$;
REVOKE ALL ON FUNCTION impact.human_advice_read_scope(uuid,uuid,uuid) FROM PUBLIC;

CREATE FUNCTION impact.human_advice_participant(target uuid,material boolean DEFAULT false) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(
  SELECT 1 FROM impact.human_advice_case_current c
  JOIN impact.tenant_principal p ON p.tenant_id=c.tenant_id AND p.principal_id=impact.human_advice_principal()
  JOIN impact.auth_identity i ON i.identity_id=p.identity_id
  JOIN impact.membership_current m ON m.tenant_id=c.tenant_id AND m.identity_id=p.identity_id
  JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
  JOIN impact.object_registry plan ON plan.tenant_id=c.tenant_id AND plan.object_id=c.context_plan_id
  JOIN impact.object_revision plan_head ON plan_head.tenant_id=plan.tenant_id
    AND plan_head.object_id=plan.object_id AND plan_head.revision_id=plan.head_revision
  WHERE c.tenant_id=impact.current_tenant() AND c.object_id=target AND p.active
  AND plan.object_type='AIAdoptionPlan' AND plan.classification<>'RESTRICTED'
  AND plan_head.restriction_state='AVAILABLE'
  AND impact.human_advice_read_scope(p.principal_id,m.object_id,c.context_plan_id)
  AND h.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active')
  AND (m.expires_at IS NULL OR m.expires_at>now())
  AND ((p.principal_id=c.requester_principal_id AND m.object_id=c.requester_membership_id AND i.natural_identity_id=c.requester_natural_id)
       OR (p.principal_id=c.adviser_principal_id AND m.object_id=c.adviser_membership_id AND i.natural_identity_id=c.adviser_natural_id
           AND c.case_state NOT IN ('Closed','Cancelled')
           AND (NOT material OR c.case_state IN ('Assigned','AwaitingInput','AdviceDraft'))))
 )
$$;
REVOKE ALL ON FUNCTION impact.human_advice_participant(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_participant(uuid,boolean) TO impact_app;

CREATE FUNCTION impact.human_advice_auth_cutoff(target uuid) RETURNS timestamptz
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT greatest(p.auth_not_before,s.auth_not_before) FROM impact.tenant_principal p
 LEFT JOIN impact.identity_security_state s ON s.identity_id=p.identity_id
 WHERE p.tenant_id=impact.current_tenant() AND p.principal_id=target
$$;
REVOKE ALL ON FUNCTION impact.human_advice_auth_cutoff(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_auth_cutoff(uuid) TO impact_app;

-- Case-related audit metadata must not reveal a hidden case's identity, actor
-- or existence through ordinary audit lists/search/exports. Other audit rows
-- retain their existing policy. The incomplete AuditEvent header is visible
-- only during its own atomic creation, before its deferred revision FK seals.
CREATE FUNCTION impact.human_advice_record_visible(kind text,target uuid,participants boolean) RETURNS boolean
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE p jsonb;
BEGIN
 IF kind='HumanAdviceCase' THEN
  RETURN participants AND impact.human_advice_participant(target,false);
 END IF;
 IF kind<>'AuditEvent' THEN RETURN true; END IF;
 SELECT v.payload INTO p FROM impact.object_registry h JOIN impact.object_revision v
 ON v.tenant_id=h.tenant_id AND v.object_id=h.object_id AND v.revision_id=h.head_revision
 WHERE h.tenant_id=impact.current_tenant() AND h.object_id=target AND h.object_type='AuditEvent';
 IF p IS NULL THEN RETURN true; END IF;
 IF COALESCE(p->>'action_type','') ~ '^(human_advice_|create_human_advice_case$)' THEN
  RETURN participants AND impact.human_advice_participant((p->>'object_reference')::uuid,false);
 END IF;
 RETURN true;
END $$;
REVOKE ALL ON FUNCTION impact.human_advice_record_visible(text,uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_record_visible(text,uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;

CREATE POLICY participant_context ON impact.human_advice_case_current AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_participant(object_id,false))
 WITH CHECK(requester_principal_id=impact.human_advice_principal()
   OR (adviser_principal_id=impact.human_advice_principal() AND case_state NOT IN ('Closed','Cancelled')));
CREATE POLICY participant_material ON impact.human_advice_private_brief AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_participant(object_id,true))
 WITH CHECK(EXISTS(SELECT 1 FROM impact.human_advice_case_current c
   WHERE c.tenant_id=human_advice_private_brief.tenant_id AND c.object_id=human_advice_private_brief.object_id
   AND c.requester_principal_id=impact.human_advice_principal()));
CREATE POLICY human_advice_registry_participants ON impact.object_registry AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_record_visible(object_type,object_id,true))
 WITH CHECK(impact.human_advice_record_visible(object_type,object_id,true));
CREATE POLICY human_advice_revision_participants ON impact.object_revision AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_record_visible(object_type,object_id,true))
 WITH CHECK(impact.human_advice_record_visible(object_type,object_id,true));
CREATE POLICY human_advice_registry_no_other_runtime ON impact.object_registry AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_record_visible(object_type,object_id,false))
 WITH CHECK(impact.human_advice_record_visible(object_type,object_id,false));
CREATE POLICY human_advice_revision_no_other_runtime ON impact.object_revision AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_record_visible(object_type,object_id,false))
 WITH CHECK(impact.human_advice_record_visible(object_type,object_id,false));
CREATE FUNCTION impact.human_advice_object_visible(target uuid,participants boolean) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT COALESCE((SELECT impact.human_advice_record_visible(h.object_type,h.object_id,participants)
  FROM impact.object_registry h WHERE h.tenant_id=impact.current_tenant() AND h.object_id=target),false)
$$;
REVOKE ALL ON FUNCTION impact.human_advice_object_visible(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_object_visible(uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;
CREATE POLICY human_advice_authors_participants ON impact.object_natural_author AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_object_visible(object_id,true))
 WITH CHECK(impact.human_advice_object_visible(object_id,true));
CREATE POLICY human_advice_authors_no_other_runtime ON impact.object_natural_author AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_object_visible(object_id,false))
 WITH CHECK(impact.human_advice_object_visible(object_id,false));
CREATE POLICY human_advice_audit_participants ON impact.audit_event_current AS RESTRICTIVE TO impact_app
 USING(COALESCE(action_type,'') !~ '^(human_advice_|create_human_advice_case$)' OR impact.human_advice_participant(object_reference,false))
 WITH CHECK(COALESCE(action_type,'') !~ '^(human_advice_|create_human_advice_case$)' OR impact.human_advice_participant(object_reference,false));
CREATE POLICY human_advice_audit_no_other_runtime ON impact.audit_event_current AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(COALESCE(action_type,'') !~ '^(human_advice_|create_human_advice_case$)')
 WITH CHECK(COALESCE(action_type,'') !~ '^(human_advice_|create_human_advice_case$)');

CREATE POLICY human_advice_receipt_participants ON impact.operation_receipt AS RESTRICTIVE TO impact_app
 USING(COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)'
    OR impact.human_advice_participant((outcome->>'object_id')::uuid,false))
 WITH CHECK(COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)'
    OR (actor_id=impact.human_advice_principal() AND impact.human_advice_participant((outcome->>'object_id')::uuid,false)));
CREATE POLICY human_advice_receipt_no_other_runtime ON impact.operation_receipt AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)')
 WITH CHECK(COALESCE(command_type,'') !~ '^(human_advice_|create_human_advice_case$)');

CREATE FUNCTION impact.human_advice_event_visible(target uuid,participants boolean) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT COALESCE((SELECT CASE WHEN e.payload->>'aggregate_type'='HumanAdviceCase'
   THEN participants AND impact.human_advice_participant((e.payload->>'aggregate_id')::uuid,false)
   ELSE true END FROM impact.outbox_event e WHERE e.tenant_id=impact.current_tenant() AND e.event_id=target),false)
$$;
REVOKE ALL ON FUNCTION impact.human_advice_event_visible(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_event_visible(uuid,boolean)
 TO impact_app,impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy;
CREATE POLICY human_advice_outbox_participants ON impact.outbox_event AS RESTRICTIVE TO impact_app
 USING(COALESCE(payload->>'aggregate_type','')<>'HumanAdviceCase' OR impact.human_advice_participant((payload->>'aggregate_id')::uuid,false))
 WITH CHECK(COALESCE(payload->>'aggregate_type','')<>'HumanAdviceCase' OR impact.human_advice_participant((payload->>'aggregate_id')::uuid,false));
CREATE POLICY human_advice_outbox_no_other_runtime ON impact.outbox_event AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(COALESCE(payload->>'aggregate_type','')<>'HumanAdviceCase')
 WITH CHECK(COALESCE(payload->>'aggregate_type','')<>'HumanAdviceCase');
CREATE POLICY human_advice_delivery_participants ON impact.outbox_delivery AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_event_visible(event_id,true))
 WITH CHECK(impact.human_advice_event_visible(event_id,true));
CREATE POLICY human_advice_delivery_no_other_runtime ON impact.outbox_delivery AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_event_visible(event_id,false))
 WITH CHECK(impact.human_advice_event_visible(event_id,false));
CREATE POLICY human_advice_consumer_participants ON impact.consumer_receipt AS RESTRICTIVE TO impact_app
 USING(impact.human_advice_event_visible(event_id,true))
 WITH CHECK(impact.human_advice_event_visible(event_id,true));
CREATE POLICY human_advice_consumer_no_other_runtime ON impact.consumer_receipt AS RESTRICTIVE
 TO impact_worker,impact_identity,impact_platform,impact_observer,impact_sensitive,impact_privacy
 USING(impact.human_advice_event_visible(event_id,false))
 WITH CHECK(impact.human_advice_event_visible(event_id,false));

CREATE FUNCTION impact.guard_human_advice_projection() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
DECLARE person record; who text;
BEGIN
 IF TG_OP='UPDATE' THEN
  IF (to_jsonb(NEW)-ARRAY['revision_id','case_state'])<>(to_jsonb(OLD)-ARRAY['revision_id','case_state']) THEN
   RAISE EXCEPTION 'human advice participants and scope immutable' USING ERRCODE='42501';
  END IF;
  IF OLD.case_state IN ('Closed','Cancelled') THEN
   RAISE EXCEPTION 'human advice terminal immutable' USING ERRCODE='42501';
  END IF;
  IF NEW.case_state IN ('Closed','Cancelled') AND impact.human_advice_principal()<>NEW.requester_principal_id THEN
   RAISE EXCEPTION 'requester closure required' USING ERRCODE='42501';
  END IF;
 ELSE
  IF NEW.case_state<>'Open' OR NEW.requester_principal_id<>impact.human_advice_principal() THEN
   RAISE EXCEPTION 'requester opening required' USING ERRCODE='42501';
  END IF;
 END IF;
 FOREACH who IN ARRAY ARRAY['requester','adviser'] LOOP
  SELECT p.principal_id,m.object_id AS membership_id,impact.member_natural_identity(p.tenant_id,p.principal_id) AS natural_id
  INTO person FROM impact.tenant_principal p JOIN impact.membership_current m
    ON m.tenant_id=p.tenant_id AND m.identity_id=p.identity_id
  JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
  WHERE p.tenant_id=NEW.tenant_id AND p.principal_id=(to_jsonb(NEW)->>(who||'_principal_id'))::uuid
    AND m.object_id=(to_jsonb(NEW)->>(who||'_membership_id'))::uuid AND p.active
    AND h.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active')
    AND (m.expires_at IS NULL OR m.expires_at>now());
  -- Requester can always cancel after counterpart expiry; no other mutation may.
  IF (person IS NULL OR person.natural_id IS NULL OR person.natural_id<>(to_jsonb(NEW)->>(who||'_natural_id'))::uuid)
    AND NOT(TG_OP='UPDATE' AND NEW.case_state='Cancelled' AND who='adviser') THEN
   RAISE EXCEPTION 'current human advice participant required' USING ERRCODE='42501';
  END IF;
 END LOOP;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION impact.guard_human_advice_projection() FROM PUBLIC;
CREATE TRIGGER human_advice_projection_guard BEFORE INSERT OR UPDATE ON impact.human_advice_case_current
 FOR EACH ROW EXECUTE FUNCTION impact.guard_human_advice_projection();

CREATE FUNCTION impact.check_human_advice_head() RETURNS trigger
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
DECLARE p impact.human_advice_case_current; r record; b record; who text;
BEGIN
 SELECT * INTO STRICT p FROM impact.human_advice_case_current WHERE tenant_id=NEW.tenant_id AND object_id=NEW.object_id;
 SELECT h.head_revision,h.lifecycle_state,v.payload INTO STRICT r
 FROM impact.object_registry h JOIN impact.object_revision v
 ON v.tenant_id=h.tenant_id AND v.object_id=h.object_id AND v.revision_id=h.head_revision
 WHERE h.tenant_id=p.tenant_id AND h.object_id=p.object_id AND h.object_type='HumanAdviceCase';
 SELECT * INTO STRICT b FROM impact.human_advice_private_brief WHERE tenant_id=p.tenant_id AND object_id=p.object_id;
 IF p.revision_id IS DISTINCT FROM r.head_revision OR p.case_state IS DISTINCT FROM r.lifecycle_state
    OR r.payload->>'state' IS DISTINCT FROM p.case_state OR r.payload IS NULL
    OR r.payload->>'context_plan_id' IS DISTINCT FROM p.context_plan_id::text
    OR r.payload->>'context_plan_revision' IS DISTINCT FROM p.context_plan_revision::text
    OR r.payload->>'problem_sha256' IS DISTINCT FROM encode(b.problem_sha256,'hex') OR r.payload ? 'problem' THEN
  RAISE EXCEPTION 'human advice head and private brief must agree' USING ERRCODE='23514';
 END IF;
 FOREACH who IN ARRAY ARRAY['requester','adviser'] LOOP
  IF r.payload->>(who||'_principal_id') IS DISTINCT FROM (to_jsonb(p)->>(who||'_principal_id'))
     OR r.payload->>(who||'_membership_id') IS DISTINCT FROM (to_jsonb(p)->>(who||'_membership_id'))
     OR r.payload->>(who||'_natural_id') IS DISTINCT FROM (to_jsonb(p)->>(who||'_natural_id')) THEN
   RAISE EXCEPTION 'human advice participant proof differs' USING ERRCODE='23514';
  END IF;
 END LOOP;
 RETURN NULL;
END $$;
REVOKE ALL ON FUNCTION impact.check_human_advice_head() FROM PUBLIC;
CREATE CONSTRAINT TRIGGER human_advice_head_consistency AFTER INSERT OR UPDATE ON impact.human_advice_case_current
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION impact.check_human_advice_head();

CREATE FUNCTION impact.guard_human_advice_brief() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN RAISE EXCEPTION 'human advice brief immutable' USING ERRCODE='42501'; END $$;
REVOKE ALL ON FUNCTION impact.guard_human_advice_brief() FROM PUBLIC;
CREATE TRIGGER human_advice_brief_immutable BEFORE UPDATE OR DELETE ON impact.human_advice_private_brief
 FOR EACH ROW EXECUTE FUNCTION impact.guard_human_advice_brief();

COMMIT;

```

## 0039_human_advice_anchor_availability.sql

Source: infrastructure/migrations/0039_human_advice_anchor_availability.sql. SHA-256: `12fb7073f1f841965f6e8c5874444b48ae2da0c39f0e93dae820e7fbedd5b0f0`.

Registered local build0.33 candidate, not merged or deployed. No new tables or columns, data mutation, FK/trigger relaxation or broader runtime privilege. Frozen0038 remains byte-for-byte unchanged. `CREATE OR REPLACE impact.human_advice_participant(uuid,boolean)` retains the owner-definer, fixed search path, current natural-person membership/expiry/read scope, material-sharing and terminal-adviser gates. It additionally joins the exact anchored AIAdoptionPlan revision by tenant/object/revision/type and requires AVAILABLE. Existing case, private brief, registry/revision, natural-author, audit, operation-receipt and outbox event/delivery/consumer policies inherit the same refusal, including list/cursor visibility. The API checks the exact pin before case resolve and creation receipt lookup as a separate defense.

The two before-fix diagnostics are retained in `docs/evidence/sprint-0.33-human-advice-anchor-before-observations.json` and the corresponding named tests/source-proof/applied-migration reports. They model RESTRICTED and REMOVED-at-insertion older pins with a readable new head through schema-valid append-only synthetic records; all FK/deferred/immutable guards remain enabled. They do not claim a supported API case-creation, retention or privacy-removal workflow. Before0039, both cases were visible via current/history/revision/list/replay and eleven pointer classes while direct old guidance was404. Actual registered0039 API/PGlite qualification passes both strict cases in the122-check focus (`docs/evidence/sprint-0.33-human-advice-pglite-tests.xml`): case/history/replay404, omitted list rows and all eleven pointer classes withheld. The actual schema39 ledger matches the frozen migration hash and captured source is unchanged during that run. Native pointer checks were subsequently refined to require the actual application login, retaining labelled fixture SET ROLE for PGlite; focused actual PostgreSQL17.11 native qualification now passes142 checks with no failures/errors/skips. Both exact-old-anchor observations explicitly use actual impact_app_login plus SET LOCAL ROLE impact_app (`docs/evidence/sprint-0.33-human-advice-native-anchor-observations.json`) and withhold all eleven pointer classes, list/history/replay. Final full-source PGlite and native restart/restore/upgrade regression, browser and acceptance remain pending.

```sql
-- Reviewed additive0039 candidate; integrator registers exact bytes after review.
-- Older unavailable plan pins end every case/pointer read through the central helper.
-- Keep frozen0038 unchanged; no new tables, data changes or broader runtime privileges.
BEGIN;
SET LOCAL ROLE impact_owner;

CREATE OR REPLACE FUNCTION impact.human_advice_participant(target uuid,material boolean DEFAULT false) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(
  SELECT 1 FROM impact.human_advice_case_current c
  JOIN impact.tenant_principal p ON p.tenant_id=c.tenant_id AND p.principal_id=impact.human_advice_principal()
  JOIN impact.auth_identity i ON i.identity_id=p.identity_id
  JOIN impact.membership_current m ON m.tenant_id=c.tenant_id AND m.identity_id=p.identity_id
  JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
  JOIN impact.object_registry plan ON plan.tenant_id=c.tenant_id AND plan.object_id=c.context_plan_id
  JOIN impact.object_revision plan_head ON plan_head.tenant_id=plan.tenant_id
    AND plan_head.object_id=plan.object_id AND plan_head.revision_id=plan.head_revision
  JOIN impact.object_revision plan_anchor ON plan_anchor.tenant_id=c.tenant_id
    AND plan_anchor.object_id=c.context_plan_id AND plan_anchor.revision_id=c.context_plan_revision
    AND plan_anchor.object_type='AIAdoptionPlan'
  WHERE c.tenant_id=impact.current_tenant() AND c.object_id=target AND p.active
  AND plan.object_type='AIAdoptionPlan' AND plan.classification<>'RESTRICTED'
  AND plan_head.restriction_state='AVAILABLE' AND plan_anchor.restriction_state='AVAILABLE'
  AND impact.human_advice_read_scope(p.principal_id,m.object_id,c.context_plan_id)
  AND h.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active')
  AND (m.expires_at IS NULL OR m.expires_at>now())
  AND ((p.principal_id=c.requester_principal_id AND m.object_id=c.requester_membership_id AND i.natural_identity_id=c.requester_natural_id)
       OR (p.principal_id=c.adviser_principal_id AND m.object_id=c.adviser_membership_id AND i.natural_identity_id=c.adviser_natural_id
           AND c.case_state NOT IN ('Closed','Cancelled')
           AND (NOT material OR c.case_state IN ('Assigned','AwaitingInput','AdviceDraft'))))
 )
$$;
REVOKE ALL ON FUNCTION impact.human_advice_participant(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_participant(uuid,boolean) TO impact_app;

COMMIT;

```
