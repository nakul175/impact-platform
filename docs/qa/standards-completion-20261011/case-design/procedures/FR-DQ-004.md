## QA v1.3 — source-bound case design (proposed)

Story `FR-DQ-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DQ-004-001` / `TC-IMPRANA-FR-DQ-004-001` | `REV_992cc988483f3c9665cbd2e773b937e8f76fd0d71716753dc1f5aa830c02de8f` / `REV_736c4a11ccca4cac409f455522ab8fb79cf64eed31a3cb0b00a379da8967c321` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-004-002` / `TC-IMPRANA-FR-DQ-004-002` | `REV_07c7c02c7f7937c2ccf635eb4956fb0be5079c986dfe84b230d8e8389f2ee806` / `REV_67d2519f6052e20c7c5876915498afde1904e1d9b13b5de1f9cf19223e7b3b2a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-004-003` / `TC-IMPRANA-FR-DQ-004-003` | `REV_241038fcfa5a051e66d5b3095184b3e3f60065c2789410ffc82474fa68f8ddb8` / `REV_eb82f50ea5f35e1d54918bbf4ad75b26a02b14deb0093e0ab12ae4c0b31d96b2` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-004-004` / `TC-IMPRANA-FR-DQ-004-004` | `REV_94b9e6d6290b416f02b855d5042f487d7b246b83b5104ebece4298389ca30cc9` / `REV_c1da6b411997f2f04e855d460c7f129c6b60b59b753e2bccb4236650f729d2d9` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DQ-004-001 — Exclusive components reconcile to the total

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-004-001` is not created. Verification duty `TASK-FR-DQ-004-03` (qualification); source `docs/backlog/backlog.csv` record 222, exact block `992cc988483f3c9665cbd2e773b937e8f76fd0d71716753dc1f5aa830c02de8f`.

**Original preconditions**

1. a reconciliation rule for an exclusive exhaustive breakdown
2. a total of ten with components six and four

**Original actions**

1. the check compares the component sum to the total at the stated precision

**Exact source oracles — all required**

1. the check passes

Legacy same-requirement reuse candidates: `TC-DQ-004-01`, `TC-DQ-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-004-002 — Overlapping categories are not forced to sum to the total

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-004-002` is not created. Verification duty `TASK-FR-DQ-004-03` (qualification); source `docs/backlog/backlog.csv` record 222, exact block `07c7c02c7f7937c2ccf635eb4956fb0be5079c986dfe84b230d8e8389f2ee806`.

**Original preconditions**

1. a reconciliation rule for overlapping service categories
2. a total of ten with two overlapping service categories of six and seven

**Original actions**

1. the check runs

**Exact source oracles — all required**

1. the categories are not required to sum to ten
2. the check compares distinct entities or uses a labelled nonadditive check

Legacy same-requirement reuse candidates: `TC-DQ-004-01`, `TC-DQ-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-004-003 — Missing components make the check incomplete

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-004-003` is not created. Verification duty `TASK-FR-DQ-004-03` (qualification); source `docs/backlog/backlog.csv` record 222, exact block `241038fcfa5a051e66d5b3095184b3e3f60065c2789410ffc82474fa68f8ddb8`.

**Original preconditions**

1. an exclusive breakdown with a missing component

**Original actions**

1. the check runs

**Exact source oracles — all required**

1. the check is marked incomplete
2. it is not automatically marked failed or passed

Legacy same-requirement reuse candidates: `TC-DQ-004-01`, `TC-DQ-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-004-004 — Reject exposing suppressed values in public reconciliation detail

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-004-004` is not created. Verification duty `TASK-FR-DQ-004-03` (qualification); source `docs/backlog/backlog.csv` record 222, exact block `94b9e6d6290b416f02b855d5042f487d7b246b83b5104ebece4298389ca30cc9`.

**Original preconditions**

1. a reconciliation that involves suppressed values

**Original actions**

1. the reconciliation detail is published

**Exact source oracles — all required**

1. the suppressed values may have been evaluated privately
2. they are never exposed in the public reconciliation detail

Legacy same-requirement reuse candidates: `TC-DQ-004-01`, `TC-DQ-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
