# Impact Management Database Migration Specification

This specification defines the physical database baseline, reference integrity, role privileges and migration procedure for PostgreSQL 17. The accompanying SQL replaces the earlier design blueprint. It is intended for database and backend engineers implementing the FSD. The SQL has a repeatable migration runner and structural validation; live PostgreSQL execution remains a qualification step recorded separately.

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
