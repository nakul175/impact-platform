## QA v1.3 — source-bound case design (proposed)

Story `FR-EVA-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-EVA-003-001` / `TC-IMPRANA-FR-EVA-003-001` | `REV_51ff9bc785a752aebe28313f2fbbd58d03dfabfe6c2666f8fe00f9a233888ee2` / `REV_6a233f6634b4e178742240b7d42a133291291dcde27250b338f2657cb24539c4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVA-003-002` / `TC-IMPRANA-FR-EVA-003-002` | `REV_66c0d66084a35544d440876fd327d188ee80638d9e4f4e98794cfd9de4707899` / `REV_34e49445d4639a56b0ddfbfd601c5239cab5169b8da045bbaba9ff263b0e27f9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVA-003-003` / `TC-IMPRANA-FR-EVA-003-003` | `REV_57d89246ac1d5a7ffed1635014b0ae5c9584cd31798da5c735e949019825866d` / `REV_9bb63cfd1880a272ddcfce32e6bb0d8a4ab472e25490941d627f7070e0fd4c6a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVA-003-004` / `TC-IMPRANA-FR-EVA-003-004` | `REV_478e461529c858f88331392ea00c47638aafdb2843ca81418744d7bfcc66fc1f` / `REV_273ba29bd8e433c41dbe2760399af4fd07cf22239a4582eed3acad66af2add7b` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-EVA-003-001 — Create a frozen extract

Source persona: Analyst. Proposed fixture `FIX-FR-EVA-003-001` is not created. Verification duty `TASK-FR-EVA-003-03` (qualification); source `docs/backlog/backlog.csv` record 333, exact block `51ff9bc785a752aebe28313f2fbbd58d03dfabfe6c2666f8fe00f9a233888ee2`.

**Original preconditions**

1. approved sources

**Original actions**

1. an Analyst creates an extract with selected variables, filters, dictionary and integrity manifest

**Exact source oracles — all required**

1. the extract is frozen
2. reviewed scripts and notebooks can be attached as evidence
3. results reference the extract and method versions

Legacy same-requirement reuse candidates: `TC-EVA-003-01`, `TC-EVA-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVA-003-002 — Reproduce a result after live records change

Source persona: Analyst. Proposed fixture `FIX-FR-EVA-003-002` is not created. Verification duty `TASK-FR-EVA-003-03` (qualification); source `docs/backlog/backlog.csv` record 333, exact block `66c0d66084a35544d440876fd327d188ee80638d9e4f4e98794cfd9de4707899`.

**Original preconditions**

1. a submitted result based on a pinned extract

**Original actions**

1. live records are later corrected

**Exact source oracles — all required**

1. the extract is not altered
2. the result can be reproduced from the pinned extract
3. the original analysis remains reconcilable

Legacy same-requirement reuse candidates: `TC-EVA-003-01`, `TC-EVA-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVA-003-003 — Reject executing uploaded code

Source persona: Analyst. Proposed fixture `FIX-FR-EVA-003-003` is not created. Verification duty `TASK-FR-EVA-003-03` (qualification); source `docs/backlog/backlog.csv` record 333, exact block `57d89246ac1d5a7ffed1635014b0ae5c9584cd31798da5c735e949019825866d`.

**Original preconditions**

1. a script or notebook uploaded as an ordinary upload

**Original actions**

1. it is stored in the product

**Exact source oracles — all required**

1. it is not executed in the product

Legacy same-requirement reuse candidates: `TC-EVA-003-01`, `TC-EVA-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVA-003-004 — Reject export without the export capability

Source persona: Analyst. Proposed fixture `FIX-FR-EVA-003-004` is not created. Verification duty `TASK-FR-EVA-003-03` (qualification); source `docs/backlog/backlog.csv` record 333, exact block `478e461529c858f88331392ea00c47638aafdb2843ca81418744d7bfcc66fc1f`.

**Original preconditions**

1. a user with analysis access but without the separate export capability

**Original actions**

1. they try to export the extract

**Exact source oracles — all required**

1. the export is refused

Legacy same-requirement reuse candidates: `TC-EVA-003-01`, `TC-EVA-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
