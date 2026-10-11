## QA v1.3 — source-bound case design (proposed)

Story `FR-UX-009` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-UX-009-001` / `TC-IMPRANA-FR-UX-009-001` | `REV_2614666488da5153c5508c67afd33f26fa57c745983019223ad14e4bd318ade8` / `REV_6dc87d8870aa5692e7bdef5888ed0fbc49b3c8bd060144e127df378a5351d3a3` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-009-002` / `TC-IMPRANA-FR-UX-009-002` | `REV_3bcdf899356ccf3a38ed4f96b2ec58bd88efa4372c3d7a99207ec094b6052a6d` / `REV_a18fa8ff8db7dd92496b84f836f21ab8daf31b9173239dcc1e2eec0613c3f160` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-009-003` / `TC-IMPRANA-FR-UX-009-003` | `REV_c1de4a83de06d379571ad30f8504e11ddef47fa339fc8cdbc801dbdffd6718ee` / `REV_7f880023c9bbdccb6a280c033eb427eac7c158daea18c004e55525dae064bb70` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-UX-009-001 — Large file shows separate processing stages

Source persona: Data Author. Proposed fixture `FIX-FR-UX-009-001` is not created. Verification duty `TASK-FR-UX-009-03` (qualification); source `docs/backlog/backlog.csv` record 174, exact block `2614666488da5153c5508c67afd33f26fa57c745983019223ad14e4bd318ade8`.

**Original preconditions**

1. a Data Author submits a large file

**Original actions**

1. it is processed

**Exact source oracles — all required**

1. separate receipt, validation, review and calculation stages are shown
2. no published result appears prematurely

Legacy same-requirement reuse candidates: `TC-UX-009-01`, `TC-UX-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-009-002 — Job receipt shows the current stage

Source persona: Data Author. Proposed fixture `FIX-FR-UX-009-002` is not created. Verification duty `TASK-FR-UX-009-03` (qualification); source `docs/backlog/backlog.csv` record 174, exact block `3bcdf899356ccf3a38ed4f96b2ec58bd88efa4372c3d7a99207ec094b6052a6d`.

**Original preconditions**

1. a background job in progress

**Original actions**

1. the Data Author views its receipt

**Exact source oracles — all required**

1. the receipt names the current stage
2. it shows complete only after the actual completion event

Legacy same-requirement reuse candidates: `TC-UX-009-01`, `TC-UX-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-009-003 — Reject success cues that overstate status

Source persona: Data Author. Proposed fixture `FIX-FR-UX-009-003` is not created. Verification duty `TASK-FR-UX-009-03` (qualification); source `docs/backlog/backlog.csv` record 174, exact block `c1de4a83de06d379571ad30f8504e11ddef47fa339fc8cdbc801dbdffd6718ee`.

**Original preconditions**

1. an action that was saved but not approved or externally delivered

**Original actions**

1. its outcome is shown

**Exact source oracles — all required**

1. a generic green success banner does not imply approval or external delivery
2. numeric badges include text equivalents and uncertainty states

Legacy same-requirement reuse candidates: `TC-UX-009-01`, `TC-UX-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
