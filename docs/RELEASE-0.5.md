# Release 0.5.0 — programme-period close and restatement

Build 0.5.0 · API 1.6.0 · additive migration 0008 · 26 September 2026.

## Delivered behavior

The **Period close** workspace presents reporting status by programme and calendar period. A close request generates its preview on the server and pins the programme, period revision, approved collection-plan revision, active indicator/definition revisions, every source revision, source digest, coverage result and current provisional-result revision. The candidate exposes exact blockers for pending, missing, invalid/rejected, or unplanned values, missing approved plans and stale or absent calculations.

An independent reviewer decides the immutable preview. Approval re-runs the preview under a tenant write lock. Any input, plan or result change invalidates the fingerprint and requires a new preview. A blocker prevents approval without partially creating official data. A successful close creates new OFFICIAL result revisions, copies exact lineage edges, records a transactional close job and output manifest, creates a locked snapshot and advances an append-only `(programme, period)` snapshot version. Provisional results and earlier snapshots are never overwritten.

Calendar Period records remain reusable definitions. Operational lock state is stored by `(tenant, programme, period)`, avoiding the defect where closing one programme could lock the same calendar quarter for all programmes. Source submission, governed correction and recalculation check this scoped state. Ordinary late writes are blocked after close.

A restatement request starts from the latest locked programme-period snapshot, names only approved source objects included in that snapshot, gives a reason and expires within seven days. Independent approval opens correction only for those sources. A new provisional calculation and second close create a replacement official snapshot with `supersedes_snapshot_id`; the original remains immutable. Closing revokes the effective restatement state even when its original time window has not elapsed.

## Architecture and security delta

- `period_contracts.py` adds closed close/restatement command contracts and typed review candidates.
- `period_governance.py` owns preview, fingerprint, blocker, workflow, official-result, snapshot and restatement rules.
- Migration 0008 adds programme-period state, snapshot bindings, official-result membership and source-specific restatement permission tables. All tenant tables have forced RLS. The application role has no update/delete authority on immutable snapshot membership.
- The Snapshot projection gains an explicit programme reference while retaining its access-scope reference. This separates business ownership from authorization scope.
- Close and restatement still require explicit capabilities and fresh authentication where configured. Candidate/content authors cannot approve. Cross-tenant objects remain indistinguishable from missing objects.
- The browser derives programme-period status from snapshot/restatement records and never treats the reusable Period lifecycle as a programme lock.

## Qualification and limits

Five focused live cases cover successful close, immutable official lineage, blocked close, source drift after preview, locked correction denial, scoped restatement, new snapshot supersession, unrelated-source rejection and RLS isolation. The scenarios also verify that newly submitted data cannot enter a locked period.

This is a bounded manual-measurement profile. Reviewed exclusions, optional-late-source policy, automated close schedules, notification delivery, distributed-artifact inventories, annual/YTD regeneration, bulk restatement, privacy withdrawal and configurable multi-stage close policies remain open. Native PostgreSQL concurrency and workload qualification remain release gates.
