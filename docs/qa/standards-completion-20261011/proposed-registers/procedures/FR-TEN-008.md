## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-008-001` / `TC-IMPRANA-FR-TEN-008-001` | `REV_3cf93d6cfbaffe85d270fa571e88439890e50b62ba92c203805dbf0a8f778926` / `REV_158cd7290d9d5d1820b1604946df8eddaee5f214bdeeb4646e1725bea27c9f81` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-008-002` / `TC-IMPRANA-FR-TEN-008-002` | `REV_57eb77101399d2ab24b3999f82ff30f5a619d11cf480438b15f083c7322c8396` / `REV_80d3f8a5b9879bd9f917887459d4029fd99949bd7755c0ce7e96554b37d6e8d1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-008-003` / `TC-IMPRANA-FR-TEN-008-003` | `REV_a8f49191781c5bf11242fe54b5a4af812ec642a7efdd673bd26bf7c48dc9a536` / `REV_d8acc8bd3038474e55373185b3faf7157cb9dc3c2eb50be0f77d438e1234e5b5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-008-004` / `TC-IMPRANA-FR-TEN-008-004` | `REV_b0e1cef17ddd31a57ce71b14f971b50112ba3251b1d4410ce5345cda1f6e949f` / `REV_f5fa1833b36830a7ce0ac1401cdcbd1a517cad0defd48d30204db744cadf679a` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-008-001 — Copy configuration to a test workspace

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-008-001` is not created. Verification duty `TASK-FR-TEN-008-03` (qualification); source `docs/backlog/backlog.csv` record 362, exact block `3cf93d6cfbaffe85d270fa571e88439890e50b62ba92c203805dbf0a8f778926`.

**Original preconditions**

1. an Organisation Administrator

**Original actions**

1. they copy configuration and synthetic fixtures into an isolated test workspace

**Exact source oracles — all required**

1. production credentials and personal records are not copied by default

Legacy same-requirement reuse candidates: `TC-TEN-008-01`, `TC-TEN-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-008-002 — Promote an approved package

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-008-002` is not created. Verification duty `TASK-FR-TEN-008-03` (qualification); source `docs/backlog/backlog.csv` record 362, exact block `57eb77101399d2ab24b3999f82ff30f5a619d11cf480438b15f083c7322c8396`.

**Original preconditions**

1. a configuration package in the test workspace

**Original actions**

1. promotion compares versions, dependencies and validation results
2. an eligible Reviewer approves the complete package

**Exact source oracles — all required**

1. the production application records the exact promoted versions and affected future objects

Legacy same-requirement reuse candidates: `TC-TEN-008-01`, `TC-TEN-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-008-003 — Roll back a promoted collection rule

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-008-003` is not created. Verification duty `TASK-FR-TEN-008-03` (qualification); source `docs/backlog/backlog.csv` record 362, exact block `a8f49191781c5bf11242fe54b5a4af812ec642a7efdd673bd26bf7c48dc9a536`.

**Original preconditions**

1. a new collection rule was promoted and production submissions were accepted under it

**Original actions**

1. the Organisation Administrator rolls it back

**Exact source oracles — all required**

1. compatible configuration references are restored
2. sample records never appear in production
3. accepted production submissions keep their original rule references

Legacy same-requirement reuse candidates: `TC-TEN-008-01`, `TC-TEN-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-008-004 — Reject rollback that erases intervening writes

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-008-004` is not created. Verification duty `TASK-FR-TEN-008-03` (qualification); source `docs/backlog/backlog.csv` record 362, exact block `b0e1cef17ddd31a57ce71b14f971b50112ba3251b1d4410ce5345cda1f6e949f`.

**Original preconditions**

1. writes were made under an intervening configuration version

**Original actions**

1. a rollback is attempted without an explicit migration

**Exact source oracles — all required**

1. those writes are not erased or altered

Legacy same-requirement reuse candidates: `TC-TEN-008-01`, `TC-TEN-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
