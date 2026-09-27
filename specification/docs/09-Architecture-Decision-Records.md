# Impact Management Architecture Decision Records

These records capture the implementation choices underlying the HLD, LLD and completed specification package. Their status is Specified for implementation. They identify accountable roles and verification required before release; they do not claim an organisational signoff or a production deployment. A later decision supersedes a record explicitly and retains the original reasoning.

## 1 Modular domain core

ADR01. Owner Technical lead. The initial backend is a modular Python domain core with separate API and worker processes. The product has tightly coupled revision, approval, audit and calculation invariants that benefit from local transactions. Module-owned repositories and import checks preserve boundaries. This avoids introducing distributed commit protocols before measured scaling requires a split. A future service extraction must preserve operation receipts, policy checks and event compatibility. Verify import boundaries and package ownership in CI.

## 2 Web and Android clients

ADR02. Owner Client leads. Use React with TypeScript for the same-origin web application and native Kotlin for qualified Android offline collection. Web analytics and field-device custody have different interaction and persistence requirements. Share contracts and golden semantic vectors rather than assuming one UI runtime satisfies both. Device encryption, trusted expiry, process-death recovery and shared-device handling require actual Android qualification. A browser-only offline shortcut cannot claim those guarantees.

## 3 PostgreSQL and tenant isolation

ADR03. Owner Database and security leads. Use PostgreSQL 17 with tenant-keyed tables, forced RLS, nonowner runtime roles and composite foreign keys. App policy adds programme, assignment, field and purpose restrictions. Direct partitions, arbitrary SQL and migration authority remain unavailable to runtime identities. Verify the actual role and context-reset behaviour. The compatibility baseline is separate from the chosen maintained patch and immutable image digest.

## 4 Immutable revisions and projections

ADR04. Owner Domain lead. Keep an object registry, immutable revisions, typed current projections and immutable workflow candidates. Preserve official snapshots and decision provenance while allowing corrections to create new versions. Current privacy restrictions can withhold retained content without rewriting an earlier calculation. Storage and migration costs are higher than in-place editing; retention and indexing must be measured. Verify registry-head atomicity and restoration of historic meaning.

## 5 Decimal arithmetic

ADR05. Owner Measurement lead. Carry numbers as decimal strings, calculate with at least 50-digit intermediate precision and store NUMERIC(38,12). Display uses explicit half-up rounding at zero to six places. Preserve numerator, denominator, contribution identity and missingness. Reject excess precision and incompatible units at the boundary. This prevents binary-float and mean-of-percentages errors. Golden examples and independent reconciliation are mandatory for every released calculation rule.

## 6 Durable operation identity

ADR06. Owner Backend lead. A logical mutation has a client-generated operation ID, canonical payload hash, expected revision and durable receipt. Persist receipt, domain effects, audit and outbox in one transaction. Exact replay returns the original receipt after current access is checked. Source identities remain durable beyond the seven-day interactive receipt window. Verify lost-response recovery, changed-payload conflict and racing commands against the actual database.

## 7 Outbox and job leases

ADR07. Owner Platform lead. Use a transactional outbox with at-least-once transport and consumer receipts. Workers claim bounded leases with increasing generations. Every output update checks the current generation; external effects have stable business identity and reconciliation. Queue ordering is not assumed. Aggregate sequence identifies gaps and older events. Verify interruption and lease-takeover boundaries; avoid claims of exactly-once transport.

## 8 Identity and domain authority

ADR08. Owner Identity lead. Keycloak supplies OIDC identity and federation. Domain grants, scope, independence and purpose remain in the application policy layer. Web sessions use code with PKCE and secure cookies; bearer clients have qualified flows. No provider role claim automatically grants tenant-wide data authority. Verify issuer, audience, token confusion, invitation exception and session revocation end to end.

## 9 Bounded offline access

ADR09. Owner Mobile security lead. Offline packages are signed and bound to person, tenant, device, form revisions and scope. Ordinary leases last at most 24 hours and restricted leases eight hours. A trusted time anchor and monotonic continuity govern local unlock. Lost continuity locks sensitive data pending renewal. This accepts a bounded residual exposure on a disconnected device. Verify on real devices; Keystore alone does not establish trusted expiry.

## 10 Resumable media

ADR10. Owner Collection lead. Use 1 MiB numbered parts, per-part digests, immutable part receipts and a sealed ordered manifest. Completion assembles, verifies and scans before any usable evidence link exists. Current authority is checked on every part and recovery request. Multipart adds storage cleanup and state complexity but makes weak-link recovery explicit. Supersedes the whole-object-only portion of LLD section 16. Verify missing, changed, duplicate and interrupted parts.

## 11 Mediated downloads

ADR11. Owner Security lead. Reports, evidence and exports are delivered through an authorising service that checks current scope and restrictions, including ranges and bounded stream intervals. Do not expose long-lived raw object-store access. The service bears streaming and caching costs; capacity tests include large artifacts. Revocation limits future controlled access but cannot recall externally delivered bytes. Verify access loss during a stream and after approval changes.

## 12 Privacy and restore

ADR12. Owner Privacy engineering lead. Use approved store plans, independent durable deletion ledger, hold checks and per-store outcomes. Restore begins closed and replays current deletion and identity restrictions before traffic or workers resume. Active-store removal or effective restriction is due within 24 hours once executable; backup retention follows the configured baseline, initially 35 days. Verify a deleted participant and revoked identity still present in an old backup cannot reappear.

## 13 AI as bounded assistance

ADR13. Owner AI lead. AI retrieves only eligible sources, returns cited claims and typed draft proposals, and uses deterministic result bindings for official numbers. Confirmation reloads the exact sources and target revisions and applies a bounded diff through normal commands. Proposals expire within 30 minutes or on material change. AI has no approve, publish, grant or delete tool. Provider and use-case evaluation are release gates. Verify prompt injection, stale proposals, disclosure and budget boundaries.

## 14 Reference infrastructure

ADR14. Owner Platform lead. The HLD reference uses AWS ECS Fargate, RDS, S3, SQS, KMS and Secrets Manager. Deployment must supply an allowed region set and supported provider configuration. No jurisdiction is presumed in this package. Equivalent infrastructure requires a recorded decision preserving availability, recovery, isolation, custody and audit controls. Verify configuration and disaster recovery in the permitted regions before production.

## 15 API closure and explicit workflow commands

ADR15. Owner API lead. OpenAPI 3.1.1 is the normative transport schema. Objects are closed; dynamic maps have bounded typed values. Draft PATCH is a shallow merge with complete replacement of supplied nested values. Workflow lifecycle changes use explicit commands and cannot be assigned through a generic patch. This adds schema maintenance but makes generated clients and negative tests reliable. Verify malformed and forbidden fields as well as successful examples.

## 16 Physical observation partitioning

ADR16. Owner Database lead. Start with 32 hash partitions by tenant for observation current data. Preserve tenant predicates and a bounded index set. This is a capacity hypothesis to qualify against the FSD's largest tenant, retention and load skew. It is not a guarantee of a speedup. Change the partition layout only with measured plans, migration rehearsal and a demonstrated reason.

## 17 Qualification and release evidence

ADR17. Owner QA lead. Preparation tests, deployed functional tests, database tests, browser checks, Android checks, load tests, restore drills and independent security assessment remain separate evidence categories. A blocked suite is not a pass. Release evidence pins artifact, configuration, schema, policy and fixture versions. This increases explicit reporting but prevents reference examples from being mistaken for product readiness.

## 18 Development and production separation

ADR18. Owner Platform security lead. Development uses synthetic data, loopback service exposure and a clearly isolated identity realm. Production requires secret references, HTTPS origins, immutable image digests, declared regions and on-call routing. The fixture loader refuses existing data and nondevelopment database names. The release build excludes test-clock control from public APIs. Verify the separation in deployment configuration and admission checks.
