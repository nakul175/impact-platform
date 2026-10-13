## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-009` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-009-001` / `TC-IMPRANA-FR-IND-009-001` | `REV_3dfb287ce9f2fc7391eafc82d879f807cc106583d264992bee438edd972e68c5` / `REV_046f0fcf6abea3c0b6364a6b86260eb873ec39d89111e3e2078ca450de9d51b1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-009-002` / `TC-IMPRANA-FR-IND-009-002` | `REV_ad2460c64ec4fd89430de5a0ace5f94566eb078ba0d279eda083ba51cc820a4e` / `REV_1796718dea32dced1c5e8dcde2c1131888687b5ad2b0d8769b10e538e6aa5a6c` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-009-003` / `TC-IMPRANA-FR-IND-009-003` | `REV_ed2668829e3542b628535b91202efa7588ca96c009a8589d258496aeba912fe9` / `REV_4b0b1294228b0da4e3786acac62843d009ae6fd594089458af2eb5ebd57b0290` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-009-001 — Instantiate a library indicator

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-009-001` is not created. Verification duty `TASK-FR-IND-009-03` (qualification); source `docs/backlog/backlog.csv` record 243, exact block `3dfb287ce9f2fc7391eafc82d879f807cc106583d264992bee438edd972e68c5`.

**Original preconditions**

1. a library indicator

**Original actions**

1. the MEL Manager instantiates it in a project

**Exact source oracles — all required**

1. the parent definition version is pinned
2. local applicability, collection roles and permitted overrides are recorded

Legacy same-requirement reuse candidates: `TC-IND-009-01`, `TC-IND-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-009-002 — Mixed versions are flagged

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-009-002` is not created. Verification duty `TASK-FR-IND-009-03` (qualification); source `docs/backlog/backlog.csv` record 243, exact block `ad2460c64ec4fd89430de5a0ace5f94566eb078ba0d279eda083ba51cc820a4e`.

**Original preconditions**

1. two projects pinned to version 1

**Original actions**

1. only one adopts version 2 with a changed denominator after previewing comparability and reporting impact

**Exact source oracles — all required**

1. the portfolio flags the mixed comparison

Legacy same-requirement reuse candidates: `TC-IND-009-01`, `TC-IND-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-009-003 — Reject local changes that claim exact equivalence

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-009-003` is not created. Verification duty `TASK-FR-IND-009-03` (qualification); source `docs/backlog/backlog.csv` record 243, exact block `ed2668829e3542b628535b91202efa7588ca96c009a8589d258496aeba912fe9`.

**Original preconditions**

1. a project instance of a library indicator

**Original actions**

1. a locked semantic field is changed locally

**Exact source oracles — all required**

1. a distinct reviewed definition is created
2. the instance does not claim exact standard equivalence

Legacy same-requirement reuse candidates: `TC-IND-009-01`, `TC-IND-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
