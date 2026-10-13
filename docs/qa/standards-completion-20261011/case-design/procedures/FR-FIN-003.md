## QA v1.3 — source-bound case design (proposed)

Story `FR-FIN-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FIN-003-001` / `TC-IMPRANA-FR-FIN-003-001` | `REV_6c62bf0b854c100bf5199a1d0a9ae97ad615b728343766561bd6639f64da8b20` / `REV_5d17b45e1836b176972841d6efef794e6898aff45b8dbeffe59e027b2853b072` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-003-002` / `TC-IMPRANA-FR-FIN-003-002` | `REV_5f5495872443e382a452ba6aa5e09b7b6fb07a08185a10abd17b792e9b9ad11d` / `REV_9e262bedd1fb8a2a0821d8a13fb7aa7d6decd3ef630014b4809b894152437f2f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-003-003` / `TC-IMPRANA-FR-FIN-003-003` | `REV_665f3953c9f3771de233053ce762ffd2a597e083784864a0175ae57c997d6fba` / `REV_153c706c78669a958af9fbf4d641cc83d8910ac89633deb16d9a6c5f5271e064` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-003-004` / `TC-IMPRANA-FR-FIN-003-004` | `REV_0b7e4a13874d1e37291f839f4dc0d858654fa017aea62f7d054589f2d158d4e6` / `REV_7a6ee1fcbe7db30acd8eaa8552c3a54fcf869d91daf18725a7b94623f55a6690` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FIN-003-001 — Import an amended transaction file twice

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-003-001` is not created. Verification duty `TASK-FR-FIN-003-03` (qualification); source `docs/backlog/backlog.csv` record 340, exact block `6c62bf0b854c100bf5199a1d0a9ae97ad615b728343766561bd6639f64da8b20`.

**Original preconditions**

1. an amended transaction file

**Original actions**

1. the Finance Officer imports it twice

**Exact source oracles — all required**

1. only the intended corrected expenditure balance contributes to analysis
2. unchanged records are reconciled rather than duplicated

Legacy same-requirement reuse candidates: `TC-FIN-003-01`, `TC-FIN-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-003-002 — Mapping validates control totals and adjustments

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-003-002` is not created. Verification duty `TASK-FR-FIN-003-03` (qualification); source `docs/backlog/backlog.csv` record 340, exact block `5f5495872443e382a452ba6aa5e09b7b6fb07a08185a10abd17b792e9b9ad11d`.

**Original preconditions**

1. an expenditure file with source transaction key, posting and event dates, amount, currency, category and funding allocation

**Original actions**

1. it is mapped

**Exact source oracles — all required**

1. control totals and adjustment semantics are validated
2. reversals and replacements are treated as separate transaction semantics

Legacy same-requirement reuse candidates: `TC-FIN-003-01`, `TC-FIN-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-003-003 — Reject counting the same expense again

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-003-003` is not created. Verification duty `TASK-FR-FIN-003-03` (qualification); source `docs/backlog/backlog.csv` record 340, exact block `665f3953c9f3771de233053ce762ffd2a597e083784864a0175ae57c997d6fba`.

**Original preconditions**

1. a file has already been imported

**Original actions**

1. the same file is uploaded again

**Exact source oracles — all required**

1. the same expense is not counted again

Legacy same-requirement reuse candidates: `TC-FIN-003-01`, `TC-FIN-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-003-004 — Reject approval of unbalanced source totals

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-003-004` is not created. Verification duty `TASK-FR-FIN-003-03` (qualification); source `docs/backlog/backlog.csv` record 340, exact block `0b7e4a13874d1e37291f839f4dc0d858654fa017aea62f7d054589f2d158d4e6`.

**Original preconditions**

1. a source file whose totals do not balance

**Original actions**

1. approval is requested

**Exact source oracles — all required**

1. approval is blocked unless an explicit permitted exception is recorded

Legacy same-requirement reuse candidates: `TC-FIN-003-01`, `TC-FIN-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
