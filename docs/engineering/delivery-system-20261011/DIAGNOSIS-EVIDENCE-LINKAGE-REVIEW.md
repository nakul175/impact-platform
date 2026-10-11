# Diagnosis Evidence linkage: storage preparation

Inspected source: `829983fdcbf579dd28be84f1672353c98eb47646`, schema46, domain API1.30. Active story US-DX-01a/APL-361 only. This is a concrete engineering recommendation, not an applied migration, accepted criterion, SQL test pass or human signoff. No schema47 file is registered by this record. Earlier migrations and revision payloads stay byte-exact.

## Proposed relation and invariants

Use a separate revision binding, not a mutable current-source projection. Each row carries tenant_id, diagnosis object_id and revision_id, stable problem_id, reference_position (1–5), Evidence object_id and revision_id. Primary key includes tenant_id, diagnosis object/revision, problem and position. A second unique key forbids a duplicate source pair within that problem. The same source may support another problem without being silently deduplicated or reordered.

Four foreign keys must carry tenant_id: diagnosis object/revision triple; diagnosis revision plus generated kind AIDiagnosis; source object/revision triple; source revision plus generated kind Evidence. Together these reject a valid revision attached to a different object, another kind, missing revision and cross-tenant selector. Do not FK only revision_id, select the latest source edition, or infer a source link from supporting notes. Keep exact source revision references across later corrections and source restriction changes.

ENABLE and FORCE RLS with tenant_fence are required before runtime grants. Worker, identity and platform get no new table privilege. The runtime needs only bounded insert/read access if actual application use requires it; no public function execution or UPDATE/DELETE grant. Direct table reads are not user-facing authority: the diagnosis API must retain its fresh current diagnosis/Evidence checks. Do not let a new table create a path around the0045 worker diagnosis fence or expose removed source metadata.

## Integrity and atomicity

A pure immutable payload predicate should validate optional reference arrays before casts: at most5, closed object keys, canonical UUID strings, no duplicates, and absent field compatible. Existing0046 already validates problem identities and order, but its predicate deliberately does not validate the new references. Preserve its bytes; add a new constraint. Governed REMOVED SQL NULL payloads remain admissible. Validation must inspect historical revisions too and refuse an invalid upgrade atomically, without deleting or normalising history.

Binding population and diagnosis revision must commit in the existing head/revision/audit/outbox/receipt transaction. A database insertion trigger can derive exact problem/position/reference tuples, preventing API omission and preserving direct SQL writer invariants. A binding insert guard must verify the tuple exists in that exact diagnosis JSON; FK existence alone would allow an extra valid source pair. No external call and no new uncertain-operation retry identity. Empty/absent references create no binding rows. Existing unrelated revision writers must not need a new data grant or execute an unguarded source-read trigger.

Do not register a migration until the all-tenant backfill is proven through the restricted migration login. Both tenant_root and object_revision have forced RLS; an owner-role SELECT without transaction-local tenant context can silently see no rows. A trusted tenant inventory and per-tenant set_config loop must cover all historical tenants, including any legacy onboarding gap, with explicit pre/post counts and exact revision hashes. Do not disable forced RLS or use an owner/superuser run as proof that the deployed migrator can perform this upgrade.

## Privacy and source availability

Current API privacy execution takes the tenant advisory lock. The existing privacy_remove_revisions function independently checks the approved executing plan, durable deletion ledger and revision-removal trigger; it does not acquire that lock itself. A SQL owner/fixture update is not a governed privacy execution test. CLEAN upload/blob checks in the resolver currently have no added row locks; inspect all scanner/purge writers and qualify their actual ordering separately.

Existing source erasure removes payload while retaining immutable revision identity. A source FK therefore should not block legitimate Evidence removal. The API must still refuse disclosure/replay/completion of linked unavailable sources, even though structural linkage remains valid. Binding rows must never copy title, source URL, notes or file bytes. Historical diagnosis JSON and source identifiers cannot be automatically rewritten when a source becomes unavailable.

If a diagnosis revision itself undergoes governed removal, retaining a separate copy of its links could leave a new privacy store. Ordinary app deletion must stay refused; any cleanup hook must run only after the existing approved revision-removal guard succeeds and remove only that tenant/object/revision's bindings. No independently callable bypass or broad privacy authority. The currently implemented privacy plan targets declared Evidence/import and member stores; adding diagnosis as a privacy target is a separate governed scope, not implied by this binding design. Resolve and test the store lifecycle before registering a relation. No new privacy target, repair flow, waiver or human approval is supplied here.

## Required proof before delivery

1. Native restricted app SQL: valid exact links; wrong tenant/object/revision/kind; malformed arrays/keys/UUIDs/duplicates/position; missing and extra bindings; zero effects on refusal.
2. Actual worker/platform/identity access refusal, unset/foreign tenant, immutable UPDATE/DELETE denial, old notes-only and unrelated revision writer compatibility.
3. Populated46-to47 restricted-migrator upgrade: multiple tenants, old notes and linked revisions, exact history and ledger; malformed historical source shape refuses and rolls back; retry is no-op.
4. Actual current source-grant/restriction/cleanup races, source removal and diagnosis-store lifecycle without metadata leakage, hold bypass or history rewriting.
5. Exact command retries and corrections across real API restart and pg_dump restore, including preserved binding rows and worker fences.
6. Accessible selector UI and browser source-selection/refusal/late-response clearing; then integrated native/provider/browser and required exact-head hosted/container/release checks.

Current queued source-grant tests are separate supporting evidence. They establish fresh authority after an actual lock wait, not binding integrity, privacy-removal workflow, storage upgrade/recovery or story acceptance. Delivery remains0/50 until actual declared gates are met.
