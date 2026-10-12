# Release 0.41 candidate — locked problem baselines

Status: **coding-only candidate; untested, unreviewed, unmerged and undeployed**.

## Delivered in code

US-DX-03 / APL-364 adds a separate tenant-scoped `AIProblemBaseline` resource bound to an exact
completed diagnosis revision and stable priority-problem ID. Drafts can hold partial metric entry.
Locking requires time, cost, quality and reach and adds server-owned actor/time metadata. Locked
records refuse edits and retain their exact source diagnosis/problem selectors.

Each metric carries an exact decimal string, explicit unit, basis or denominator, and observation
window. A measured zero is therefore distinct from a missing metric. This is a self-reported
adoption baseline, not an official MEL result, independent approval, ROI claim or causal result.

The web panel selects a completed diagnosis and priority problem, preserves draft fields after a
refusal, and presents locked values as read-only with the server-set date.

## Contract and persistence

- Domain API candidate 1.32.
- Additive migration 0048 creates the forced-RLS, insert-only `problem_baseline_lock` register.
- New read/manage capabilities remain TENANT_ADMIN-scoped and do not widen existing tenant
  ceilings automatically.
- Earlier migrations, diagnosis revisions, criteria and evidence remain byte-exact.
- Correction/supersession is deferred: a locked baseline cannot be reopened or changed.

## Limits

Contracts, the implemented API inventory and the onboarding profile were regenerated. No test,
lint, browser run, native PostgreSQL qualification, independent security review, CI, merge or
deployment was performed at the owner's request to defer testing until the combined story train.
No story status or acceptance state changes.

## Integration notes

This candidate is stacked on APL-361 commit `732de5c9897865c5681648b1d5ba7dcbe1539f45`.
Before merge, verify regenerated contracts/profiles, perform code/security/accessibility review,
exercise native role/RLS and concurrent lock/edit behavior, run the complete required CI matrix,
and resolve the broader product decisions retained in APL-682 through APL-692.
