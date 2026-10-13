## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-013` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-013-001` / `TC-IMPRANA-FR-CAL-013-001` | `REV_2692715f28f274e5850d516297fa6be3240f88f45e8825d529d187504129b1d4` / `REV_c8853a831cf90b7f7ab53b147f2845a0b5dfe1539a6e456cd48763de10f2dc72` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-013-002` / `TC-IMPRANA-FR-CAL-013-002` | `REV_b1cfc01d85662342afadf9b71f47940772f268adc6c4d9988b045b6d94cc599e` / `REV_6d4d4ff2e15fea88dcf4face693e4f09772c63bb2f9af95e11fbc39b5c9f397f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-013-003` / `TC-IMPRANA-FR-CAL-013-003` | `REV_b10983be3842c2a102540c9cc828ba2d3310006ba5c99351ad44c9694e4b0fff` / `REV_7f07c25de41d998727419b8dcb9c3ed5a149d9a1f3e4e079326beb0decd66454` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-013-001 — Weighted composite score is calculated

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-013-001` is not created. Verification duty `TASK-FR-CAL-013-03` (qualification); source `docs/backlog/backlog.csv` record 324, exact block `2692715f28f274e5850d516297fa6be3240f88f45e8825d529d187504129b1d4`.

**Original preconditions**

1. a normalised weighted mean with component scores 60 and 80
2. weights 0.4 and 0.6

**Original actions**

1. the composite is calculated

**Exact source oracles — all required**

1. the score is 72
2. the preview shows each component's contribution and sensitivity to proposed weights

Legacy same-requirement reuse candidates: `TC-CAL-013-01`, `TC-CAL-013-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-013-002 — Changing weights creates a new version

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-013-002` is not created. Verification duty `TASK-FR-CAL-013-03` (qualification); source `docs/backlog/backlog.csv` record 324, exact block `b1cfc01d85662342afadf9b71f47940772f268adc6c4d9988b045b6d94cc599e`.

**Original preconditions**

1. an approved composite configuration pinned with its source versions

**Original actions**

1. the weights are changed

**Exact source oracles — all required**

1. a new version is created
2. the old score remains reproducible

Legacy same-requirement reuse candidates: `TC-CAL-013-01`, `TC-CAL-013-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-013-003 — Reject invalid weights or missing required components

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-013-003` is not created. Verification duty `TASK-FR-CAL-013-03` (qualification); source `docs/backlog/backlog.csv` record 324, exact block `b10983be3842c2a102540c9cc828ba2d3310006ba5c99351ad44c9694e4b0fff`.

**Original preconditions**

1. a normalised weighted mean whose weights do not sum to one

**Original actions**

1. the configuration is validated

**Exact source oracles — all required**

1. it is rejected
2. a missing required component blocks the score or returns an explicitly incomplete score
3. renormalisation is applied only when the approved rule declares it

Legacy same-requirement reuse candidates: `TC-CAL-013-01`, `TC-CAL-013-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
