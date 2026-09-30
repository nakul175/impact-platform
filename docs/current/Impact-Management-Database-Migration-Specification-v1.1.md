# Impact Management Database Migration Specification

Version 1.1   27 September 2026

This specification defines the physical database baseline, reference integrity, role privileges and migration procedure for PostgreSQL 17. The accompanying SQL replaces the earlier design blueprint. It is intended for database and backend engineers implementing the FSD. The SQL has a repeatable migration runner and structural validation; live PostgreSQL execution remains a qualification step recorded separately.

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

Build 0.13.0 increment (28 September 2026): the current schema is sixteen migrations; 0016_authority_renewal.sql is additive (SHA-256 2c95596d9088fb2ec025266cffed824a787ec8df3d3dd4021fefe19cb09290cc, recorded in CURRENT-DATA-DICTIONARY.md) and migrations 0001 through 0015 are unchanged. It creates tenant_authority_renewal, readable and writable only by impact_platform, with a partial unique index allowing one Requested or Accepted request per tenant, and apply_authority_renewal, a fixed-search-path SECURITY DEFINER function revoked from PUBLIC and granted only to impact_platform; it re-dates exactly the pinned grant_authority and member_role_assignment rows of an Applied, independently approved request for an Active tenant whose bootstrap marker is the pinned one, and aborts with 42501 otherwise. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.14.0 increment (29 September 2026): no migration was added; the schema remains sixteen migrations whose ledgered SHA-256 values were verified three times on native PostgreSQL — by the migrator session of the qualification run, by the restore drill on a restored copy, and by the upgrade check after applying 0016 to a populated schema-15 database (2 tenants, 507 revisions preserved). scripts/migrate.py is now the only migration runner for PGlite and native alike (--until N, --fixture-if-empty, --json); a superuser runs the files as written and any other session must be impact_owner or a member of it and runs as impact_owner, which is what the provisioned impact_migrator login does. Login roles and credentials are provisioned outside the migration set by scripts/provision_logins.py (impact_owner receives CREATE on the database so that a non-superuser migration session can create the schema of migration 0001). Fixture targets now include impact_test_<suffix>. The upgrade check covers only 0015 → 0016, which adds a table and a function and alters no populated table. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.15.0 increment (29 September 2026): migration 0017_provider_logout.sql (SHA-256 4378cafe2bacbf6266e0d18f5886966a29c0a53b2ba51566b7afc4c04c9c000b) adds the nullable columns web_session.provider_sid (with a partial index) and web_session.provider_logout_hint (bytea, 29–16,412 bytes) and the identity table oidc_logout_token(issuer, jti, expires_at, accepted_at) with primary key (issuer, jti), granted SELECT, INSERT and DELETE to impact_identity only and, like the other identity tables, without tenant_id or RLS. It is additive and follows the BEGIN / SET LOCAL ROLE impact_owner / COMMIT convention; readiness requires schema 17. All seventeen checksums were verified by the native run, the restore drill and the upgrade check, which now migrates a populated schema-16 database (2 tenants, 507 revisions, 1 session) to 17 and confirms the new columns and table with the data preserved; this is the first upgrade check that alters a populated table (by adding nullable columns), and it is still not evidence for a migration that rewrites data. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.16.0 increment (29 September 2026): migration 0018_worker_delivery.sql (SHA-256 bd2defdfb56f3332f0cdb1706fd330893497cc3eeb8f45f4277922f0eca9e8b7) alters the populated outbox_delivery table with nullable or defaulted dispatch columns (channel, template, reference, sealed recipient, state, lease owner/generation/expiry, next and last attempt, error class, completion), four CHECK constraints and two partial indexes, and revokes UPDATE on it from impact_app; adds notification_delivery, recovery_channel_challenge and authority_reminder (each tenant-keyed with ENABLE and FORCE ROW LEVEL SECURITY and tenant_fence), worker_heartbeat (no tenant data), recovery-contact channel columns with UNIQUE(tenant_id, contact_id), the SECURITY DEFINER functions enqueue_recovery_channel_delivery and worker_tenants (fixed search_path, REVOKE FROM PUBLIC, one grantee) with owner-only SELECT policies serving the latter, worker grants, and a replaced tenant_work_impact. It is additive and follows the BEGIN / SET LOCAL ROLE impact_owner / COMMIT convention; readiness requires schema 18. All eighteen checksums were verified by the native run, the restore drill (156 tables, 31,235 rows) and the upgrade check, which migrates a populated schema-17 database (2 tenants, 507 revisions, 1 session, 1 outbox delivery) to 18 with the data preserved. The next migration number on this line is 0019. Edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current schema and source preservation

The executed application schema contains eighteen additive migrations in infrastructure/migrations (as of build 0.16.0). The original specification database with three migrations remains a historical design asset. CURRENT-DATA-DICTIONARY.md records the current migration inventory, table definitions, columns and constraints from the executable SQL, including later ALTER statements. Do not provision the current application from the historical three-file design alone.

The current series adds application sessions and receipts, access administration, measurement configuration and amendments, period governance, report packages, work invalidation, controlled publication, workspace administration, managed tenants, initial access and recovery contacts. Original migrations 0001 through 0014 are unchanged by v0.12.

## Privileged control plane

tenant_onboarding and its events and receipts separate managed-tenant control from business access. Initial access persists reviewed proposal pins and a one-time applied marker. Migration 0015 adds tenant_recovery_contact with unique partial indexes for one Active and one pending record per tenant. Contact records preserve custody, identity, profile hash, expiry and replacement revisions.

The contact table is restricted to the platform role. A fixed-search-path SECURITY DEFINER function locks the relevant identity, profile and cutoff rows without granting general identity mutation or read access. PUBLIC cannot execute it. Replacement, events and receipts commit or roll back together. Application roles cannot manufacture custody or delegation ceilings, modify immutable history or read another tenant through a permitted role path.

## Migration qualification boundary

The local runner has exercised SQL, constraints, roles, RLS and rollback in PGlite 17.5. Serialized embedded execution does not establish native PostgreSQL scheduling, process separation, persistence or upgrades. The CI native job remains an unexecuted gate in this saved evidence. A production candidate requires separate runtime identities, a migration identity, tested grants, upgrade rehearsal, restore validation and approved region and key custody.

Before upgrade, back up and verify the current schema version and migration checksums. Apply additions in order. If a migration is already recorded with a different checksum, stop and investigate; never rewrite recorded migration history. Destructive rollback requires a rehearsed repair or restore plan and remains outside the qualified local workflow.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

## 1 Physical model

The domain uses a tenant root, tenant principals, an object registry, immutable object revisions and typed current projections. Registry identity is tenant_id plus object_id. Revisions add revision_id, object type, predecessor, schema version, payload digest, author and timestamp. A monotonically increasing revision_number is unique within a tenant and object. The current head and new revision are committed together with audit, operation receipt and outbox intent.

| Storage item | Count | Reference |
| --- | --- | --- |
| Tenant tables including partitions | 113 | database/catalogue.json |
| Observation partitions | 32 | 0002_domain.sql |
| Typed current projections | 49 | 0002_domain.sql |
| Classified domain UUID fields | 101 | database/reference-map.json |
| Migration files | 3 | database/migrations |

The database catalogue names every table, role and registry kind. The reference map classifies each scalar UUID as a global identity, tenant principal, tenant object, immutable revision, support-table reference or opaque business identity. Opaque IDs, such as a submission business key or correlation ID, are deliberately not foreign keys. Structured references inside JSON follow the closed DTO and domain validators; scalar foreign keys remain database enforced.

Each entity's current table has a generated object_type and a composite foreign key to the registry. A Programme reference also carries a generated Programme kind so it cannot point to a valid Evidence UUID. Revision references bind tenant, revision and required kind. Workflow candidate and quality-issue object/revision pairs additionally prove that both references describe the same object.

## 2 Schema and storage rules

Use NUMERIC(38,12) for stored measurement and finance values. Reject excess precision at the API and ingestion boundary before assigning into a scale-constrained database column. Text source identifiers retain their original string form. UTC instants use timestamptz, while source and reporting zones remain explicit domain fields. Present, missing, invalid and undefined numeric states remain distinct.

The observation current table has 32 hash partitions by tenant. Queries include tenant_id and an indexed indicator/event range. Runtime access uses the parent table; direct partition privileges are absent. Reassess this physical choice against the FSD's 100 million total observations, 20 million largest-tenant cohort and skewed load before production. Partitioning is a measured implementation choice, not a substitute for query plans and retention design.

JSONB stores closed domain payloads, workflow manifests and bounded nested structures. Validate their schemas before SQL and revalidate retained schema versions during migrations. JSONB type checks catch array/object mismatches. They do not prove cross-field meaning, referential integrity inside arrays, expression safety or policy authority. Domain handlers own those checks and their negative tests.

Direct participant identifiers do not enter participant_current.direct_identifiers; a CHECK requires that projection field to remain null. The authorised API projects decrypted values from participant_private after purpose and field checks. That table contains ciphertext and a key reference and is accessible only through a separate sensitive-data database identity. Envelope keys and secret locators are governed independently from ordinary domain projections. The immutable participant payload must also exclude plaintext direct identifiers.

## 3 Migration inventory

| Migration | Contents | Transaction |
| --- | --- | --- |
| 0001 roles | Nonlogin privilege roles, owned schema, migration ledger and schema access | Atomic bootstrap |
| 0002 domain | Core and current tables, supporting tables, partitions, typed foreign keys and indexes | Atomic schema baseline |
| 0003 security | Forced RLS, grants, private-table isolation and revision-removal guard | Atomic policy baseline |

The migration runner takes a session advisory lock, checks PostgreSQL 17, validates every retained checksum, and applies each missing file with its ledger entry in one transaction. A crash before commit leaves neither change nor ledger success. Rerunning an applied version requires an identical hash. A changed applied file is an error; add a new migration for a repair.

Use a deployment administrator authorised to create the nonlogin roles. Supply credentials through IMPACT_MIGRATION_DSN without logging its value. The API never receives that credential. Create actual login identities through environment provisioning and grant each only its declared nonlogin role. Do not grant impact_owner or migration privileges to an application, worker, support user or developer service account in production.

## 4 Role and privilege model

| Role | Authority | Boundary |
| --- | --- | --- |
| impact_owner | Owns schema and objects; NOLOGIN | Migration session only; no application membership |
| impact_app | Tenant-scoped domain reads and permitted inserts or updates | No history update/delete, private identifiers, TRUNCATE or direct partitions |
| impact_worker | Tenant-scoped jobs and ordinary worker effects | Fresh domain authority and lease fencing remain mandatory |
| impact_identity | Global identity and protected session or invitation tables | Separate credential from ordinary request persistence |
| impact_sensitive | Encrypted participant private store | Application purpose/field policy and key custody required |
| impact_privacy | Approved revision payload removal and store ledger work | Separate plan, hold and trigger checks |
| impact_observer | Tenant service metadata | No participant or ordinary business-content access |

Every tenant table enables and forces row-level security. Its policy compares tenant_id with a transaction-local tenant setting. Missing context returns no rows. Set the tenant using a parameterised set_config call with the local flag true, immediately after beginning the transaction. Reset or discard uncertain pooled connections. A user-controlled SQL console is outside the application design: a session setting alone cannot protect a database from a party permitted to issue arbitrary SQL.

The runtime is a nonowner without BYPASSRLS, CREATE, TRUNCATE or direct partition privileges. Revisions, decisions, snapshots, lineage, immutable receipts and audit records receive SELECT and INSERT only. Mutable delivery state is stored separately from immutable outbox payloads. Query restrictions at the application layer additionally enforce programme, assignment, purpose, field and current disclosure scope.

## 5 Referential and domain constraints

Foreign keys include tenant_id for tenant-owned relationships. Reference-map.json records the exact target and revision semantics. Constraints are deferred where registry head and first revision must be inserted together. Ordinary reference existence and kind checks still occur before transaction commit. Map database constraint failures to safe domain errors rather than exposing another tenant's identifiers through detail strings.

Unique source identity applies to imported finance transactions, service events and submission business IDs. Source-key and source-revision receipts retain durable replay information. Workflow decisions are unique by workflow, stage, natural person and candidate revision. Independent author checks use verified natural identity rather than membership aliases. The handler must enforce author independence under the same candidate lock as the decision write.

Database checks cover period order, nonnegative rates and ceilings, supported numeric value states, scale-bounded typed storage, upload sizes, hash lengths, explicit job states and expiry ordering. Activation profiles still enforce the full entity requirements, such as completed hosting policy before tenant activation and a complete measurement contract before programme activation. Draft nullability is deliberate and must never be interpreted as permission to activate an incomplete object.

## 6 Transactions and locks

Acquire locks in this order: tenant policy, subject epoch, operation receipt, object heads in UUID order, then workflow or job state. Recheck current permission and expected revisions inside the transaction. Read a matching completed operation receipt before rejecting the stale expected revision of an exact retry. Keep the canonical payload hash and outcome in the same transaction as its effects.

Worker lease_generation increases on each claim. Every result update predicates on the current generation and permitted state. External effects require their own durable business identity and reconciliation; a database transaction cannot make an arbitrary provider call exactly once. Import item outcomes reconcile accepted, rejected, skipped and cancelled rows even after a worker interruption.

Read queries use bounded pagination and declared indexes. Add indexes from measured access paths and inspect execution plans for the largest tenant. Avoid broad JSON scans in interactive list views. Backfills write bounded tenant batches with progress receipts and impose queue limits so they do not consume ordinary request capacity.

## 7 Privacy execution and immutable history

Privacy execution has its own role and approved store plan. It cannot modify ordinary revision metadata. A removal of a revision payload requires the matching tenant context, executing DATABASE action, recorded deletion ledger and no active hold. The trigger permits only a null payload with restriction_state REMOVED and leaves identifying record IDs, digest and revision metadata unchanged subject to their own retention policy.

The deletion ledger must be copied to independently durable governed storage before any deletion becomes irreversible. A row in the same database alone does not prove disaster recovery durability. The executor records completion per store, including blob, search, AI cache, exports and device revocation. Current-table projections containing personal fields require the store executor's documented restriction/removal action as well; deleting only the revision payload does not complete the privacy case.

Holds are released by a separately authorised decision. Backup restore runs closed, replays the current deletion ledger and revoked identities, rebuilds safe projections, and only then enables workers and traffic. Aggregate mathematics and historical provenance remain interpretable without re-exposing lawfully removed personal content.

## 8 Upgrade rollback and recovery

Use expand, backfill, switch and contract phases for future migrations. Add compatible fields and indexes before deploying writers; backfill with receipts; switch reads only after reconciliation; remove old fields after the supported-client and rollback windows. Preserve previous calculation and form schema readers while old immutable revisions remain retained.

The baseline has no automatic destructive down migration. For a failed fresh installation, rollback the transaction. For an incompatible production change, prefer a forward repair or the rehearsed restore procedure. Deleting the schema is a disposable development action and is not packaged as a production rollback command.

## 9 Database qualification

Run a fresh install, checksum-preserving rerun, upgrade from the last released schema and controlled interrupted migration. Execute the supplied runtime-role tests for missing context, tenant isolation, wrong object kinds, cross-tenant foreign keys, direct partitions, private identifiers, immutable revision updates, audit deletion, TRUNCATE and pooled context reset.

Add real concurrent tests for conflicting edits, duplicate operation receipts, role revocation racing with publication, close racing with correction, outbox redelivery and worker lease takeover. Verify restore and hold-aware deletion under actual runtime and privacy identities. Parser success establishes SQL syntax only; it is not evidence that PostgreSQL executed these migrations or that application policies are correct.

## 10 Technical references

PostgreSQL 17 row security behaviour: https://www.postgresql.org/docs/17/ddl-rowsecurity.html. PostgreSQL version and security maintenance information: https://www.postgresql.org/support/versioning/ and https://www.postgresql.org/support/security/17/. The initial development image is 17.11; the deployment pipeline records a verified image digest and checks maintenance advisories before release.
