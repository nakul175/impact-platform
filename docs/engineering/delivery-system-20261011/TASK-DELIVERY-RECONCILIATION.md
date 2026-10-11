# US-DX-01a — task delivery and status reconciliation

Read-only task inspection on 11 October 2026, candidate `cc8b1c001f1f878ad7f1f5835a3d6eb89ad1d772`. This is a root-agent advisory, not human review, accepted scope, an approved workflow transition or completed delivery. All six native task statuses and APL-361 remain Backlog. The owner's status-sync question is awaiting a direct answer; a scheduled heartbeat is not that answer. No issue description, criterion, hierarchy, priority or release allocation changed.

## Proposed transitions for owner review

| Native issue | Candidate evidence | Remaining before completion | Proposed status, not applied |
| --- | --- | --- | --- |
| APL-361 — story | Manual diagnosis editor/API and source-bound local qualification | Required container/exact-head hosted CI, human security/accessibility/owner acceptance, existing-tenant access review and task scope reconciliation | In Progress |
| APL-665 — contract | Stable UUID problems, closed DTOs, bounds, incomplete draft/complete/correction behavior and read/manage matrix in implementation contract | Review of recommended cardinality/limits/manual evidence model and its agreement with the broader proposed task; agent design is not owner/engineer signoff | In Review |
| APL-666 — persistence | Additive0044 reuses forced-RLS registry/revisions, registers new kind/profile; native app/platform tests and populated40-to44 upgrade passed at pinned checkpoints | Proposed task asks for malformed-order/problem-ID database constraints and no unintended worker/identity access. This slice validates problem JSON in the API, without diagnosis-specific SQL payload constraints. Inherited worker registry/revision access is not isolated; broad task coverage is not established | In Progress |
| APL-669 — atomic commands | Edit/reorder/complete/revise, receipt, rollback, native stale-writer, queued authority and concurrent same-operation cases qualified | Human code/security review and required exact-head delivery checks; projected-grant narrowing tests do not qualify the governed revocation workflow | In Review |
| APL-671 — visibility/permissions | Bounded plain-text notes, closed fields, tenant/current-capability fences, generated profile and terminal UI access loss | Protected evidence selectors/revision-status checks are explicitly absent from manual-notes scope, so the broader proposed selector criteria are unqualified. Existing-tenant ceiling upgrade requires governed review. No scope waiver inferred | In Progress |
| APL-675 — UI | Nine actual Chrome groups, keyboard controls, saved ordering, named refusals, stale/uncertain retry and bounded axe checks | Human accessibility/security review and owner acceptance; automated axe and local browser success do not establish complete accessibility | In Review |
| APL-678 — qualification | Source-bound two-criterion supplement, unit/API/browser/reference/native/provider/recovery receipts with preserved failures and source pins | Container deployment path, required exact-head hosted CI, human reviews/owner demo and reconciled scope; previous full-suite runs are historical, not current-head green CI | In Progress |

No proposed transition is Done. These recommendations preserve the distinction between an implemented local candidate and an accepted task. Do not remove Needs refinement labels, change task scope or substitute new acceptance criteria based on this advisory.

## Source and evidence boundaries

The two original story criteria retain Gherkin SHA256 `6568f4b80844144e6398bde82db86533faaa15862a1d9e54e2dbf9df79b59d73`. The task proposals are broader than those two criteria. Their references to proposed test filenames, selected protected evidence and reviewed model choices are planning duties; they are not silently fulfilled by manual notes or a different test filename. [Implementation contract](US-DX-01a-IMPLEMENTATION.md) explicitly excludes protected source selectors and records inherited worker access as a limit.

Migration0044 adds the kind and generated profile; it does not add SQL checks over individual JSON problem IDs/order. The closed API validates those properties. Migrations0003/0024 retain worker SELECT/INSERT privileges on registry/revisions;0025 narrows other tables and registry UPDATE. This is a source-level observation, not a newly executed worker exploit or proof that tenant RLS failed. The native identity-role suite separately refuses registry/revision table reads; do not conflate it with worker isolation.

Do not retrofit broad registry privilege changes into applied migrations. A proposed worker/job privilege change would need an additive migration, inventory of actual worker/report/privacy duties, meaningful regression, impact review and the actual applicable authority. No such migration, accepted exception or new scope is introduced here.

## Actual results at their source checkpoints

- Original implementation: 1,522 unit passed /62 skipped;136 affected API passed /12 skipped;57 new diagnosis API cases;9 Chrome groups;143 reference checks.
- Full application checkpoint:2,403 passed /101 skipped /one existing IT_018 deselection.
- Full native checkpoint:2,484 passed /26 skipped /one existing IT_018 deselection; generic restart/restore/populated upgrade passed.
- Exact diagnosis recovery: real API restart and restored-API exact history/receipt checks passed, bound to their separate affected-run source.
- Live native Keycloak checkpoint:18 passed, no failures/errors/skips, including17 prior provider cases plus diagnosis.
- Latest focused native checkpoint:25 passed, no failures/errors/skips, including14 queued-authority matrix cases and7 simultaneous operation cases. This is not the full native suite rerun.

Current receipt entry points are [release note](../../RELEASE-0.40-ai-diagnosis.md) and [handover](HANDOVER.md). Earlier receipts, original criteria and all applied migrations remain intact. Release review stays passed=false despite the structural checker passing. Container remains NOT RUN without an available local engine; no remote export/CI/spending/merge/deploy is authorised by this reconciliation.


## Superseding owner-approved status sync

On 11 October2026 the owner directly replied “han badal bhai” to the concrete seven-issue transition proposal above. Actual native updates and fresh readback verified: APL-361/APL-666/APL-671/APL-678 → In Progress; APL-665/APL-669/APL-675 → In Review. This supersedes the earlier Backlog/pending-status observation only. All descriptions, original criteria, labels, priority, estimate, hierarchy and milestone were verified unchanged. Approval covers these workflow transitions, not scope changes, Done, human security/release acceptance, spending or remote Git/deployment authority. Broader task gaps and release gates above remain held. Earlier planning/source/evidence receipts remain historical and byte-exact.


## Schema46 diagnosis storage guard — 11 October2026 local follow-up

Additive0046 validates diagnosis problem identity and priority order directly on immutable revision INSERTs: canonical unique IDs, bounded arrays, unique priorities drawn from the problem set and full nonempty coverage for Completed records. Empty/partial Draft remains valid. Existing SQL NULL removal shape stays valid; no removal guard or historical row is rewritten. A pure invoker predicate with fixed catalog search path grants no data authority. PostgreSQL requires helper execution for existing revision writers even when another record kind selects the other CHECK branch; the helper permits app/worker/platform/privacy execution while prior table/tenant fences remain unchanged. All0001–0045 byte-exact. Build0.40 unreleased candidate, derived schema46.

Actual focused native qualification:158 passed/one existing harness skip, zero failures/errors, including26 new storage/compatibility checks and unchanged diagnosis, native roles, reminders and exports. Initial33 failures (missing fixture timestamp, invalid privacy-context probe and helper privilege compatibility) and subsequent8 helper-privilege failures remain raw evidence; fixes did not weaken old tests. Version/access-upgrade unit checks:28 passed. Separate actual recovery run:56 passed/one restored-mode skip; restored-only API subsequently1 passed. Actual API restarts, native backup restore, restored diagnosis exact current/history/receipt replay, restricted restored-worker fence and generic populated45-to46 upgrade passed; services stopped. All271 application/test/migration source pins stable across successful runs.

[Constraint/recovery receipt](../../evidence/candidate-0.40/diagnosis-order-schema46-20261011/CONSTRAINT-RECEIPT.json) separates raw failures, source review and evidence review. Neither review phase is independent human approval. This guard covers selected IDs/order/state shape, not full stored JSON-schema/text/metadata authentication. The removed-payload probe tests SQL storage shape only, not a diagnosis privacy workflow. Existing generic upgrade fixture does not establish malformed legacy diagnosis migration behavior. Full schema46 regression/provider/browser/container/hosted qualification and protected selectors, existing-tenant/human/release acceptance gates remain before delivery. Zero verified deployed stories; no remote push/PR/merge, spending, new story or owner acceptance.
