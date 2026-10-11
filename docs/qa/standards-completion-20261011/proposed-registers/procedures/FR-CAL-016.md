## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-016` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-016-001` / `TC-IMPRANA-FR-CAL-016-001` | `REV_523ee4059ca8aa08f12d4da7c54853aa24b1ae2baa257e5a5a49677a93692e04` / `REV_457e14d0cc566060b348bf01487e6a6a9d95c9fe5bce36ffc5d961384c74dbdc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-016-002` / `TC-IMPRANA-FR-CAL-016-002` | `REV_5a141828f78d8080adc6beaa31caf9a6cbb4bd391f0aba0703f19cf90d4ab5ce` / `REV_9039267ca275aec695b424a1f20e944e705f1d5927a754a1c7262f25587e2fd1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-016-003` / `TC-IMPRANA-FR-CAL-016-003` | `REV_88f276474fb55342b2f0831cc71f5a5026adceca79734a00903c77f3c482b7da` / `REV_e8413f0fc8b54e627749ca474d9446dad4e16299b8aa3cabf9ead9a5955795e3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-016-001 — Pooled median from raw values

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-016-001` is not created. Verification duty `TASK-FR-CAL-016-03` (qualification); source `docs/backlog/backlog.csv` record 325, exact block `523ee4059ca8aa08f12d4da7c54853aa24b1ae2baa257e5a5a49677a93692e04`.

**Original preconditions**

1. one group with raw values 1, 2 and 100 and another with raw values 3 and 4

**Original actions**

1. a pooled median is calculated

**Exact source oracles — all required**

1. the result is 3
2. the result package contains calculation metadata and limitations

Legacy same-requirement reuse candidates: `TC-CAL-016-01`, `TC-CAL-016-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-016-002 — Reject a pooled median from subgroup medians alone

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-016-002` is not created. Verification duty `TASK-FR-CAL-016-03` (qualification); source `docs/backlog/backlog.csv` record 325, exact block `5a141828f78d8080adc6beaa31caf9a6cbb4bd391f0aba0703f19cf90d4ab5ce`.

**Original preconditions**

1. only subgroup medians are available

**Original actions**

1. a pooled median is requested

**Exact source oracles — all required**

1. no pooled median claim is produced
2. any mean of medians is labelled as a mean of medians, never a pooled median

Legacy same-requirement reuse candidates: `TC-CAL-016-01`, `TC-CAL-016-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-016-003 — Reject sample estimates as population counts

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-016-003` is not created. Verification duty `TASK-FR-CAL-016-03` (qualification); source `docs/backlog/backlog.csv` record 325, exact block `88f276474fb55342b2f0831cc71f5a5026adceca79734a00903c77f3c482b7da`.

**Original preconditions**

1. a sample estimate without a reviewed expansion method

**Original actions**

1. it is reported

**Exact source oracles — all required**

1. it is not presented as a population count

Legacy same-requirement reuse candidates: `TC-CAL-016-01`, `TC-CAL-016-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
