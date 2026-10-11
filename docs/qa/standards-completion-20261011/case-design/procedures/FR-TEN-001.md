## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-001-001` / `TC-IMPRANA-FR-TEN-001-001` | `REV_f49abec595f9e5a1922c23ea0c4eb6338e493a90936c8212cbbb53f0433146fe` / `REV_825b9197c95f69eae244de84d81b0ba27bfb518b5cdef85390e62f1a8cd1e736` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-001-002` / `TC-IMPRANA-FR-TEN-001-002` | `REV_8d848d7cdbda3d055c38a98a38be5591a172a95a98bea76f3e1b0db1aa32925c` / `REV_a31a4853a74855c4fd84328cc780850100b5fa5163fc2e8fe77d7646e92bf694` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-001-003` / `TC-IMPRANA-FR-TEN-001-003` | `REV_3512ac05c5f75e5d5a6d8f0ae06e47eaf7df11acede2c6597a0fc7ebcd0d6137` / `REV_4cb019b41506786cfb9818429c1c166129712275b0f8785f8dee0be58d24da0d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-001-004` / `TC-IMPRANA-FR-TEN-001-004` | `REV_3d40dab5407ef12f6b857c0bb23866712820c0039700fe91738dafaef8970e8f` / `REV_53d35404b102a662abab018593b094f1c7ac9cdec572aec444bfba321a2f9f42` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-001-001 — Create and activate a requested tenant

Source persona: Platform Operator. Proposed fixture `FIX-FR-TEN-001-001` is not created. Verification duty `TASK-FR-TEN-001-03` (qualification); source `docs/backlog/backlog.csv` record 165, exact block `f49abec595f9e5a1922c23ea0c4eb6338e493a90936c8212cbbb53f0433146fe`.

**Original preconditions**

1. a requested tenant with an owner invitation and a selected policy profile

**Original actions**

1. the Platform Operator activates the tenant

**Exact source oracles — all required**

1. activation checks for a verified owner, recovery contact, region, retention and identity settings
2. the tenant becomes active only when those checks pass

Legacy same-requirement reuse candidates: `TC-TEN-001-01`, `TC-TEN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-001-002 — Suspend a tenant with work in progress

Source persona: Platform Operator. Proposed fixture `FIX-FR-TEN-001-002` is not created. Verification duty `TASK-FR-TEN-001-03` (qualification); source `docs/backlog/backlog.csv` record 165, exact block `8d848d7cdbda3d055c38a98a38be5591a172a95a98bea76f3e1b0db1aa32925c`.

**Original preconditions**

1. tenant A has a running import and a report schedule
2. tenant B is active

**Original actions**

1. the Platform Operator reviews the preview of scheduled writes and suspends tenant A

**Exact source oracles — all required**

1. rows already accepted by the import remain recorded
2. future writes stop at the cancellation boundary
3. policy permitted support and exit access is preserved
4. tenant B continues normally

Legacy same-requirement reuse candidates: `TC-TEN-001-01`, `TC-TEN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-001-003 — Reject automatic replay of queued writes on reactivation

Source persona: Platform Operator. Proposed fixture `FIX-FR-TEN-001-003` is not created. Verification duty `TASK-FR-TEN-001-03` (qualification); source `docs/backlog/backlog.csv` record 165, exact block `3512ac05c5f75e5d5a6d8f0ae06e47eaf7df11acede2c6597a0fc7ebcd0d6137`.

**Original preconditions**

1. tenant A was suspended with queued writes

**Original actions**

1. the Platform Operator reactivates tenant A

**Exact source oracles — all required**

1. expired grants and source credentials are rechecked
2. the queued writes are not replayed automatically

Legacy same-requirement reuse candidates: `TC-TEN-001-01`, `TC-TEN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-001-004 — Reject closure that skips holds

Source persona: Platform Operator. Proposed fixture `FIX-FR-TEN-001-004` is not created. Verification duty `TASK-FR-TEN-001-03` (qualification); source `docs/backlog/backlog.csv` record 165, exact block `3d40dab5407ef12f6b857c0bb23866712820c0039700fe91738dafaef8970e8f`.

**Original preconditions**

1. tenant A is subject to a hold

**Original actions**

1. the Platform Operator attempts to close tenant A outside the exit workflow or without resolving the hold

**Exact source oracles — all required**

1. the closure is refused

Legacy same-requirement reuse candidates: `TC-TEN-001-01`, `TC-TEN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
