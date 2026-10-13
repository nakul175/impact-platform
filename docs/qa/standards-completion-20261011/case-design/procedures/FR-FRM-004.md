## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-004-001` / `TC-IMPRANA-FR-FRM-004-001` | `REV_16972534bda78d8163d9d13f776f4654697a44cdaa16d67b8c09239304f1ec66` / `REV_938ef695ffff2d1401e1f5d4c73a786d5aa72fb2c49305f63cbf5c9a0d440cdb` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-004-002` / `TC-IMPRANA-FR-FRM-004-002` | `REV_451df9eabcae4baa32f9e9fc1c36d9d45af5ddd07951f9948cabfd91aae0000e` / `REV_6d8ebd3bacc10b7cf147fa86df745468c847d6f03c7ca96b6b7c693cf755dc48` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-004-003` / `TC-IMPRANA-FR-FRM-004-003` | `REV_6197d9c6ac44d013e1a5479778eabf3374b73c05dfaed9d4d38e081a836bc7ff` / `REV_ef5cd52dcc290ef618d43e5ce3da5327ba285c69ac48d8be48fa2729b89bdfc4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-004-004` / `TC-IMPRANA-FR-FRM-004-004` | `REV_6e66fc84ce78c3fd12dcac12534342c1bcfd5bd2b4e57c54dd6824b0a589df0c` / `REV_3687a42aeee9c268118ed652b6d26b79d36190e360d344806edf81a753093f56` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-004-001 — Same choice in different languages maps to one code

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-004-001` is not created. Verification duty `TASK-FR-FRM-004-03` (qualification); source `docs/backlog/backlog.csv` record 233, exact block `16972534bda78d8163d9d13f776f4654697a44cdaa16d67b8c09239304f1ec66`.

**Original preconditions**

1. a form released with an approved English and Hindi language set

**Original actions**

1. the same choice is submitted once in English and once in Hindi

**Exact source oracles — all required**

1. both map to one stable response code
2. each retains the language presented to the respondent

Legacy same-requirement reuse candidates: `TC-FRM-004-01`, `TC-FRM-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-004-002 — Translator sees gaps and proposals

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-004-002` is not created. Verification duty `TASK-FR-FRM-004-03` (qualification); source `docs/backlog/backlog.csv` record 233, exact block `451df9eabcae4baa32f9e9fc1c36d9d45af5ddd07951f9948cabfd91aae0000e`.

**Original preconditions**

1. a form with untranslated and machine-proposed labels

**Original actions**

1. the translator opens a language version

**Exact source oracles — all required**

1. missing and machine-proposed translations are shown
2. the language version is approved through review separately

Legacy same-requirement reuse candidates: `TC-FRM-004-01`, `TC-FRM-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-004-003 — Reject collection without approved consent translation

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-004-003` is not created. Verification duty `TASK-FR-FRM-004-03` (qualification); source `docs/backlog/backlog.csv` record 233, exact block `6197d9c6ac44d013e1a5479778eabf3374b73c05dfaed9d4d38e081a836bc7ff`.

**Original preconditions**

1. critical consent text lacks an approved translation in the selected collection language

**Original actions**

1. collection in that language is started

**Exact source oracles — all required**

1. collection in that language is blocked

Legacy same-requirement reuse candidates: `TC-FRM-004-01`, `TC-FRM-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-004-004 — Reject fallback that changes choice codes

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-004-004` is not created. Verification duty `TASK-FR-FRM-004-03` (qualification); source `docs/backlog/backlog.csv` record 233, exact block `6e66fc84ce78c3fd12dcac12534342c1bcfd5bd2b4e57c54dd6824b0a589df0c`.

**Original preconditions**

1. fallback text is used for a missing label

**Original actions**

1. a response is recorded

**Exact source oracles — all required**

1. the fallback is shown explicitly
2. the choice code is unchanged

Legacy same-requirement reuse candidates: `TC-FRM-004-01`, `TC-FRM-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
