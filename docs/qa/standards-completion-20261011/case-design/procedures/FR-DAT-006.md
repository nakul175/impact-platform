## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-006` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-006-001` / `TC-IMPRANA-FR-DAT-006-001` | `REV_406947f790e32ce0d22f922718b83c4ccc33a2e225995aceb44ae4f3a7f61b3f` / `REV_a891f617390b80373fa8b58fb1a3dd89206e5592a3ca01956a112dd12864a5ae` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-006-002` / `TC-IMPRANA-FR-DAT-006-002` | `REV_043c334f55c5a399b73ac08b89f9e030fe7bd0d6e8c9f6e058ddc92cebe1babd` / `REV_c076568e1aa06253ac729911c70695715e62bcbb5ae0369d7ee8d7ee91dab75e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-006-003` / `TC-IMPRANA-FR-DAT-006-003` | `REV_513193e96a9b277220d96cd1516619dd3dcf07467e6c4c9773c673ec2030e0e2` / `REV_81da24a42adee4e076667df6081684eb3f663f263f24f28ac2e15926d5a0d522` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-006-001 — Join preview prevents reach inflation

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-006-001` is not created. Verification duty `TASK-FR-DAT-006-03` (qualification); source `docs/backlog/backlog.csv` record 214, exact block `406947f790e32ce0d22f922718b83c4ccc33a2e225995aceb44ae4f3a7f61b3f`.

**Original preconditions**

1. one participant linked to three visits

**Original actions**

1. a one to many join is previewed

**Exact source oracles — all required**

1. the preview shows three output rows and a distinct participant count of one
2. it reports input and output counts, unmatched keys and duplicates

Legacy same-requirement reuse candidates: `TC-DAT-006-01`, `TC-DAT-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-006-002 — Publishing pins versions

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-006-002` is not created. Verification duty `TASK-FR-DAT-006-03` (qualification); source `docs/backlog/backlog.csv` record 214, exact block `043c334f55c5a399b73ac08b89f9e030fe7bd0d6e8c9f6e058ddc92cebe1babd`.

**Original preconditions**

1. a previewed transformation

**Original actions**

1. it is published

**Exact source oracles — all required**

1. its rule and source versions are pinned

Legacy same-requirement reuse candidates: `TC-DAT-006-01`, `TC-DAT-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-006-003 — Reject undeclared joins and code execution

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-006-003` is not created. Verification duty `TASK-FR-DAT-006-03` (qualification); source `docs/backlog/backlog.csv` record 214, exact block `513193e96a9b277220d96cd1516619dd3dcf07467e6c4c9773c673ec2030e0e2`.

**Original preconditions**

1. a join without declared one to one, one to many or many to one intent

**Original actions**

1. it is saved

**Exact source oracles — all required**

1. it is rejected
2. a many to many join without explicit reviewed justification is rejected
3. expressions cannot execute unrestricted code

Legacy same-requirement reuse candidates: `TC-DAT-006-01`, `TC-DAT-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
