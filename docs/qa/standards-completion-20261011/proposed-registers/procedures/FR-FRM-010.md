## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-010` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-010-001` / `TC-IMPRANA-FR-FRM-010-001` | `REV_fc274a73400be941c08aa05afa536671ef02f75e15cc45a5ff8e222d47018a73` / `REV_9c5b7ea2acd790bc496c6fb287f3050e01135a9bfdff94a80af9af41a10d141f` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-010-002` / `TC-IMPRANA-FR-FRM-010-002` | `REV_3fe75df7b21ee12dbbcfc6761d55ee65ec12497ae09837d61dcafaba3ea6f2e7` / `REV_e3e4d4956a3488eb0438cbae1d9fd538d3d23cab464bdb74e4fdf527cf7c010f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-010-003` / `TC-IMPRANA-FR-FRM-010-003` | `REV_1f4cdfd027a0c75c03540e73bee682eefa638189b0ee051e8009ad7e82d328d9` / `REV_aeb659e87e985ecbd95232eabfdb079afb7a1aca29a918452aa5660f7b4ff03d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-010-004` / `TC-IMPRANA-FR-FRM-010-004` | `REV_4b41186fa3b339f69724452f89f766a69d166c5b5217b2e3a257a7ccbf740311` / `REV_f5f91fcff046397984c097a9109bf46364d94a9e571ab6df4c5d45d0c22db381` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-010-001 — Testing reports branch coverage

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-010-001` is not created. Verification duty `TASK-FR-FRM-010-03` (qualification); source `docs/backlog/backlog.csv` record 235, exact block `fc274a73400be941c08aa05afa536671ef02f75e15cc45a5ff8e222d47018a73`.

**Original preconditions**

1. a form with skip branches and a repeat group

**Original actions**

1. two skip branches and one repeat boundary are exercised with synthetic submissions

**Exact source oracles — all required**

1. results identify any unvisited logic branches and validation failures

Legacy same-requirement reuse candidates: `TC-FRM-010-01`, `TC-FRM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-010-002 — Synthetic responses stay out of production after publishing

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-010-002` is not created. Verification duty `TASK-FR-FRM-010-03` (qualification); source `docs/backlog/backlog.csv` record 235, exact block `3fe75df7b21ee12dbbcfc6761d55ee65ec12497ae09837d61dcafaba3ea6f2e7`.

**Original preconditions**

1. synthetic test responses exist for a form

**Original actions**

1. the form is published

**Exact source oracles — all required**

1. none of the synthetic responses appear in production counts or official datasets
2. no real respondent messages are triggered

Legacy same-requirement reuse candidates: `TC-FRM-010-01`, `TC-FRM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-010-003 — Reuse a pinned question library version

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-010-003` is not created. Verification duty `TASK-FR-FRM-010-03` (qualification); source `docs/backlog/backlog.csv` record 235, exact block `1f4cdfd027a0c75c03540e73bee682eefa638189b0ee051e8009ad7e82d328d9`.

**Original preconditions**

1. a question library

**Original actions**

1. questions are copied into a form

**Exact source oracles — all required**

1. the selected library version is pinned
2. permitted local adaptation is allowed

Legacy same-requirement reuse candidates: `TC-FRM-010-01`, `TC-FRM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-010-004 — Reject publishing without passing checks

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-010-004` is not created. Verification duty `TASK-FR-FRM-010-03` (qualification); source `docs/backlog/backlog.csv` record 235, exact block `4b41186fa3b339f69724452f89f766a69d166c5b5217b2e3a257a7ccbf740311`.

**Original preconditions**

1. mandatory path checks have not passed or independent instrument review is incomplete

**Original actions**

1. publishing is attempted

**Exact source oracles — all required**

1. publishing is blocked

Legacy same-requirement reuse candidates: `TC-FRM-010-01`, `TC-FRM-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
