## QA v1.3 — source-bound case design (proposed)

Story `FR-UX-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-UX-001-001` / `TC-IMPRANA-FR-UX-001-001` | `REV_dc80d5ac34004253b1f1b213ef2a9cdb5c7f842b3b498eefd99c76b2969cb768` / `REV_86e3e2cba2db1405680ac9f245d3bf00f807c3a9acfc10b542df9bc8e2d07541` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-001-002` / `TC-IMPRANA-FR-UX-001-002` | `REV_33555bc58009bf276bfafa3827d3e6b238012bab3f21e59b6117fa16ac5990a1` / `REV_17949d8600ef51f8f39e559c4dda86aafe229d2f90be7e25ef74e0a5dfaef86b` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-001-003` / `TC-IMPRANA-FR-UX-001-003` | `REV_29f91ea5048c3d841466acdd04b5f47f6fcd6c708184cd85d3761ab4ca5f7aba` / `REV_622f1989dd10fe056c0ea03d801b0a09d361aedd41f95f18a6f583b334448263` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-001-004` / `TC-IMPRANA-FR-UX-001-004` | `REV_eb064c326461c48b33a9dab1c50badf0ed76dbaa4e250b572e917027d76655e6` / `REV_284c365e79b437f5d281d8a5a9a257a0f351034a37795d7cc809f65d29bc63cf` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-UX-001-001 — New enumerator opens an assigned form

Source persona: Field Data Collector. Proposed fixture `FIX-FR-UX-001-001` is not created. Verification duty `TASK-FR-UX-001-03` (qualification); source `docs/backlog/backlog.csv` record 169, exact block `dc80d5ac34004253b1f1b213ef2a9cdb5c7f842b3b498eefd99c76b2969cb768`.

**Original preconditions**

1. a new Field Data Collector with an assigned form

**Original actions**

1. they open their landing workspace

**Exact source oracles — all required**

1. they can open the assigned form in two primary navigation actions
2. they see its due time, save status and sync requirement

Legacy same-requirement reuse candidates: `TC-UX-001-01`, `TC-UX-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-001-002 — Landing workspace follows effective role

Source persona: Field Data Collector. Proposed fixture `FIX-FR-UX-001-002` is not created. Verification duty `TASK-FR-UX-001-03` (qualification); source `docs/backlog/backlog.csv` record 169, exact block `33555bc58009bf276bfafa3827d3e6b238012bab3f21e59b6117fa16ac5990a1`.

**Original preconditions**

1. users with different effective roles

**Original actions**

1. each user signs in

**Exact source oracles — all required**

1. collectors see assignments, reviewers see queues, managers see obligations and viewers see disclosed results
2. each user can switch among their permitted workspaces

Legacy same-requirement reuse candidates: `TC-UX-001-01`, `TC-UX-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-001-003 — Reject technical administration as a prerequisite for collection

Source persona: Field Data Collector. Proposed fixture `FIX-FR-UX-001-003` is not created. Verification duty `TASK-FR-UX-001-03` (qualification); source `docs/backlog/backlog.csv` record 169, exact block `29f91ea5048c3d841466acdd04b5f47f6fcd6c708184cd85d3761ab4ca5f7aba`.

**Original preconditions**

1. a Field Data Collector with an assigned form

**Original actions**

1. they start collecting data

**Exact source oracles — all required**

1. no technical administration step is required or shown as a prerequisite

Legacy same-requirement reuse candidates: `TC-UX-001-01`, `TC-UX-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-001-004 — Reject stale private links after a role change

Source persona: Field Data Collector. Proposed fixture `FIX-FR-UX-001-004` is not created. Verification duty `TASK-FR-UX-001-03` (qualification); source `docs/backlog/backlog.csv` record 169, exact block `eb064c326461c48b33a9dab1c50badf0ed76dbaa4e250b572e917027d76655e6`.

**Original preconditions**

1. a user whose role has changed

**Original actions**

1. navigation is recomposed

**Exact source oracles — all required**

1. no stale private links from the previous role remain

Legacy same-requirement reuse candidates: `TC-UX-001-01`, `TC-UX-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
