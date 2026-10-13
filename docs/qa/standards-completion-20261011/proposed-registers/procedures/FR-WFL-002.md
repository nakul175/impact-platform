## QA v1.3 — source-bound case design (proposed)

Story `FR-WFL-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-WFL-002-001` / `TC-IMPRANA-FR-WFL-002-001` | `REV_f774729833a0fa3e42d0417092ce161cfff08c43568f3213727fbff8841c36a9` / `REV_02aba99bc5c15e628c98f4e747e0c89975256985ce4da25799a97ab8594cb850` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-002-002` / `TC-IMPRANA-FR-WFL-002-002` | `REV_e872fb3018f8779284ef29943c7287dd2048ef54f599946082d61c0df49abb6c` / `REV_abd5f6eb7616ef1c1b0391d34b24a220c5832103d2d99805d220571da06916b5` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-002-003` / `TC-IMPRANA-FR-WFL-002-003` | `REV_f3c4e58694921eda948176326f88b9c605188faa38562758dd8d310eaed24406` / `REV_cdb2631cfa7a93fc6ac61e813730e6d4a796112a55c7c62a8535f370fd749890` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-WFL-002-001 — Approve a current candidate

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-002-001` is not created. Verification duty `TASK-FR-WFL-002-03` (qualification); source `docs/backlog/backlog.csv` record 177, exact block `f774729833a0fa3e42d0417092ce161cfff08c43568f3213727fbff8841c36a9`.

**Original preconditions**

1. a Reviewer opens an immutable candidate with its change summary and evidence

**Original actions**

1. they approve it

**Exact source oracles — all required**

1. the approval submits the candidate revision and the Reviewer's current identity
2. commit rechecks membership, scope, independence, assurance and workflow stage

Legacy same-requirement reuse candidates: `TC-WFL-002-01`, `TC-WFL-002-02`, `TC-AT12`, `TC-AT27`, `SEC-019`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-002-002 — Reject approval of a stale candidate

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-002-002` is not created. Verification duty `TASK-FR-WFL-002-03` (qualification); source `docs/backlog/backlog.csv` record 177, exact block `e872fb3018f8779284ef29943c7287dd2048ef54f599946082d61c0df49abb6c`.

**Original preconditions**

1. a Reviewer has opened a submission

**Original actions**

1. the submission or its evidence changes before they approve

**Exact source oracles — all required**

1. their old approve command fails
2. a fresh review is required

Legacy same-requirement reuse candidates: `TC-WFL-002-01`, `TC-WFL-002-02`, `TC-AT12`, `TC-AT27`, `SEC-019`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-002-003 — Reject independent approval after a Reviewer edits content

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-002-003` is not created. Verification duty `TASK-FR-WFL-002-03` (qualification); source `docs/backlog/backlog.csv` record 177, exact block `f3c4e58694921eda948176326f88b9c605188faa38562758dd8d310eaed24406`.

**Original preconditions**

1. a Reviewer edits content in a candidate

**Original actions**

1. they try to approve the resulting revision

**Exact source oracles — all required**

1. the edit is recorded as a new revision authored by them
2. they are not eligible to independently approve that revision

Legacy same-requirement reuse candidates: `TC-WFL-002-01`, `TC-WFL-002-02`, `TC-AT12`, `TC-AT27`, `SEC-019`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
