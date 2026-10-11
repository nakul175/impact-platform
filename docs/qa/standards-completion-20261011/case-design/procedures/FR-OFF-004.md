## QA v1.3 — source-bound case design (proposed)

Story `FR-OFF-004` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OFF-004-001` / `TC-IMPRANA-FR-OFF-004-001` | `REV_3a749d2da8abfdcec0a1ca4800997cf5d87f8fd5e987c780220695e31cc0078c` / `REV_bfd39c794a5f377bb98c5f74bea673dc2df22c837445d48eb29652d3c42bcf55` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-004-002` / `TC-IMPRANA-FR-OFF-004-002` | `REV_f66d6f93f26b7f74bd3fd67c5f48da10c0df0dce9dfa786db7b02b49ec425b9c` / `REV_b33c7525a1dbe4ac101ac3b2ac1f14b20c017328249810ebe5cb9ec63f6dabd5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-004-003` / `TC-IMPRANA-FR-OFF-004-003` | `REV_0791a136a7a856c85a6231b03a85b685d16941ac547a22c821ad44e819bfba35` / `REV_491d026ac013d5b914835788bdf6e2a68d22281cbb024336b2e219e858830496` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OFF-004-001 — Both candidates are visible to the resolver

Source persona: Data Steward. Proposed fixture `FIX-FR-OFF-004-001` is not created. Verification duty `TASK-FR-OFF-004-03` (qualification); source `docs/backlog/backlog.csv` record 274, exact block `3a749d2da8abfdcec0a1ca4800997cf5d87f8fd5e987c780220695e31cc0078c`.

**Original preconditions**

1. two devices alter the same visit
2. one of them used an obsolete form

**Original actions**

1. the edits are synchronised

**Exact source oracles — all required**

1. the common base is identified
2. both candidate revisions remain visible to the resolver with their distinct versions

Legacy same-requirement reuse candidates: `TC-OFF-004-01`, `TC-OFF-004-02`, `TC-AT22`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-004-002 — Resolve and resubmit

Source persona: Data Steward. Proposed fixture `FIX-FR-OFF-004-002` is not created. Verification duty `TASK-FR-OFF-004-03` (qualification); source `docs/backlog/backlog.csv` record 274, exact block `f66d6f93f26b7f74bd3fd67c5f48da10c0df0dce9dfa786db7b02b49ec425b9c`.

**Original preconditions**

1. an authorised resolver comparing permitted fields

**Original actions**

1. they choose values or create a merged revision and supply a reason

**Exact source oracles — all required**

1. the resolution is resubmitted through validation and approval

Legacy same-requirement reuse candidates: `TC-OFF-004-01`, `TC-OFF-004-02`, `TC-AT22`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-004-003 — Reject last-device-wins and overwrites

Source persona: Data Steward. Proposed fixture `FIX-FR-OFF-004-003` is not created. Verification duty `TASK-FR-OFF-004-03` (qualification); source `docs/backlog/backlog.csv` record 274, exact block `0791a136a7a856c85a6231b03a85b685d16941ac547a22c821ad44e819bfba35`.

**Original preconditions**

1. conflicting edits from two devices

**Original actions**

1. they are synchronised

**Exact source oracles — all required**

1. neither is applied automatically as last device wins
2. identity duplicates, reassigned tasks and obsolete forms receive specific conflict categories
3. existing approved data is not overwritten

Legacy same-requirement reuse candidates: `TC-OFF-004-01`, `TC-OFF-004-02`, `TC-AT22`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
