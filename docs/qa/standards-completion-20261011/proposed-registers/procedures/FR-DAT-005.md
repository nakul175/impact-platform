## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-005` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-005-001` / `TC-IMPRANA-FR-DAT-005-001` | `REV_fc58a5befb51f00398eabb89f2fd2692b33ec1b75a5842c4553dd639aa151417` / `REV_a54be5829507f361eeaad5543509b8cc80f32420aeafdcacd86146b2d917351c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-005-002` / `TC-IMPRANA-FR-DAT-005-002` | `REV_b72aec45f65189f12579be01eedf3be13649c4e0cb1644a6ab5c304057f9d5f3` / `REV_ca47b8cbd0136a888c1f0a8fd3eb4e7bd699c051f19e224c20ba1404c740bddd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-005-003` / `TC-IMPRANA-FR-DAT-005-003` | `REV_d3b8a8b7891ad82a19effe8eac31c1d76bf2054d29f35ba27ad75001089a4a70` / `REV_f867c8f24fb532074b0816b31fc5687969facb9bd6a836bb3b51fe8178f5ea9e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-005-001 — Trace a corrected date to its raw source

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-005-001` is not created. Verification duty `TASK-FR-DAT-005-03` (qualification); source `docs/backlog/backlog.csv` record 213, exact block `fc58a5befb51f00398eabb89f2fd2692b33ec1b75a5842c4553dd639aa151417`.

**Original preconditions**

1. an imported date whose interpretation was corrected

**Original actions**

1. the Data Steward traces the result

**Exact source oracles — all required**

1. lineage resolves to the source file, sheet and row key with the unchanged raw text
2. the mapping version that produced each interpretation is shown

Legacy same-requirement reuse candidates: `TC-DAT-005-01`, `TC-DAT-005-02`, `SEC-022`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-005-002 — Receipt records source details

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-005-002` is not created. Verification duty `TASK-FR-DAT-005-03` (qualification); source `docs/backlog/backlog.csv` record 213, exact block `b72aec45f65189f12579be01eedf3be13649c4e0cb1644a6ab5c304057f9d5f3`.

**Original preconditions**

1. a source file

**Original actions**

1. it is received

**Exact source oracles — all required**

1. its integrity reference, receipt time, source owner and import settings are recorded

Legacy same-requirement reuse candidates: `TC-DAT-005-01`, `TC-DAT-005-02`, `SEC-022`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-005-003 — Reject broad access or retention exemptions for raw data

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-005-003` is not created. Verification duty `TASK-FR-DAT-005-03` (qualification); source `docs/backlog/backlog.csv` record 213, exact block `d3b8a8b7891ad82a19effe8eac31c1d76bf2054d29f35ba27ad75001089a4a70`.

**Original preconditions**

1. raw values subject to privacy deletion or retention

**Original actions**

1. the policy applies

**Exact source oracles — all required**

1. raw storage is not exempt
2. restricted previews inherit the source classification and access
3. original files are not broadly downloadable

Legacy same-requirement reuse candidates: `TC-DAT-005-01`, `TC-DAT-005-02`, `SEC-022`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
