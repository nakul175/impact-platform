## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-009` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-009-001` / `TC-IMPRANA-FR-OPS-009-001` | `REV_9f96a6a5f68a6c6a53bd15eba3b034357bb3d826c083bd500e39e7b769effd5b` / `REV_8c51c92ae95cabfe517b17892dad8ccd12163bfdcccc7e94a81f5c6398736f0d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-009-002` / `TC-IMPRANA-FR-OPS-009-002` | `REV_f133108dd3967db478c3cdc61cb117b7779155a0ab56ac5e32f4c6b01d36a63a` / `REV_3c7e322b1ba4081b98d9901cf529e9d07ba22637f2ae1a6318b5aaa3b9c51a17` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-009-003` / `TC-IMPRANA-FR-OPS-009-003` | `REV_31576b6290f25ab8430a3a940cbe2e6b3165a89401d9037df8ff5baaf8505bf4` / `REV_6d7086fe2a9cee78602a74bdfdb134c35f284e33b118291e20529e87bef6fcc5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-009-004` / `TC-IMPRANA-FR-OPS-009-004` | `REV_a3a3b9c3ce7f0feb0aa1a3b1962abf61a26cad754f055ab325bc47ad5a9561a2` / `REV_83e19fa7b7aae3d7fa371bef9cc9973b8c8f255672862e4dd994b4e7b6a9ea57` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-009-001 — Retry a partially failed retention run

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-009-001` is not created. Verification duty `TASK-FR-OPS-009-03` (qualification); source `docs/backlog/backlog.csv` record 360, exact block `9f96a6a5f68a6c6a53bd15eba3b034357bb3d826c083bd500e39e7b769effd5b`.

**Original preconditions**

1. a retention run that partially failed

**Original actions**

1. the Platform Operator retries it

**Exact source oracles — all required**

1. eligible work resumes under current policy
2. held evidence remains intact
3. already sent notifications are not duplicated

Legacy same-requirement reuse candidates: `TC-OPS-009-01`, `TC-OPS-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-009-002 — Run manifest records item outcomes

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-009-002` is not created. Verification duty `TASK-FR-OPS-009-03` (qualification); source `docs/backlog/backlog.csv` record 360, exact block `f133108dd3967db478c3cdc61cb117b7779155a0ab56ac5e32f4c6b01d36a63a`.

**Original preconditions**

1. an operational job run

**Original actions**

1. the run finishes

**Exact source oracles — all required**

1. the run manifest records completed, held, skipped and failed items

Legacy same-requirement reuse candidates: `TC-OPS-009-01`, `TC-OPS-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-009-003 — Reject destructive execution without a fresh hold check

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-009-003` is not created. Verification duty `TASK-FR-OPS-009-03` (qualification); source `docs/backlog/backlog.csv` record 360, exact block `31576b6290f25ab8430a3a940cbe2e6b3165a89401d9037df8ff5baaf8505bf4`.

**Original preconditions**

1. a destructive task scheduled before a hold was placed

**Original actions**

1. the task executes

**Exact source oracles — all required**

1. holds are rechecked immediately before execution
2. the held items are not destroyed

Legacy same-requirement reuse candidates: `TC-OPS-009-01`, `TC-OPS-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-009-004 — Reject treating a stopped schedule as a reversal

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-009-004` is not created. Verification duty `TASK-FR-OPS-009-03` (qualification); source `docs/backlog/backlog.csv` record 360, exact block `a3a3b9c3ce7f0feb0aa1a3b1962abf61a26cad754f055ab325bc47ad5a9561a2`.

**Original preconditions**

1. a schedule stopped after some actions completed

**Original actions**

1. the stop is recorded

**Exact source oracles — all required**

1. the completed actions are not presented as reversed

Legacy same-requirement reuse candidates: `TC-OPS-009-01`, `TC-OPS-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
