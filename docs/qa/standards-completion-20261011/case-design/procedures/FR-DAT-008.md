## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-008` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-008-001` / `TC-IMPRANA-FR-DAT-008-001` | `REV_55eb5d7e3c718f8d106e6ccc1c3cf814793f2b6c90f06ffa436b12c43691ce71` / `REV_c92d2d741c60f7ae3b6ca96ff61a7e644fd185f4f7c689a784e538cb3d4ecce3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-008-002` / `TC-IMPRANA-FR-DAT-008-002` | `REV_1f79f4a3027f240b147ef55082d724463455cd387f8f1febccb820117398e79d` / `REV_288966788940589027a859801a5fcf6c53245fecd5bfd2f3119d1ad0b12af64d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-008-003` / `TC-IMPRANA-FR-DAT-008-003` | `REV_e65ef771eab4d64f190687d6089236f7b5f38f93b66ed4f696c41439a2ff364b` / `REV_e0fca28e15f4c663cccef8e3cb9cf4a1ab27bf771aa76ce2d5726d23e9a271af` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-008-001 — Identify affected reports for a stale dataset

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-008-001` is not created. Verification duty `TASK-FR-DAT-008-03` (qualification); source `docs/backlog/backlog.csv` record 216, exact block `55eb5d7e3c718f8d106e6ccc1c3cf814793f2b6c90f06ffa436b12c43691ce71`.

**Original preconditions**

1. a stale dataset consumed by authorised reports and by a restricted programme

**Original actions**

1. the Data Steward inspects its impact

**Exact source oracles — all required**

1. the affected authorised reports are identified
2. the restricted programme is not exposed

Legacy same-requirement reuse candidates: `TC-DAT-008-01`, `TC-DAT-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-008-002 — Catalogue entries show permitted metadata

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-008-002` is not created. Verification duty `TASK-FR-DAT-008-03` (qualification); source `docs/backlog/backlog.csv` record 216, exact block `1f79f4a3027f240b147ef55082d724463455cd387f8f1febccb820117398e79d`.

**Original preconditions**

1. a dataset the user may access

**Original actions**

1. it appears in catalogue results

**Exact source oracles — all required**

1. its permitted name, owner, purpose, schema, coverage, classification, quality and freshness are shown

Legacy same-requirement reuse candidates: `TC-DAT-008-01`, `TC-DAT-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-008-003 — Reject disclosure through lineage edges

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-008-003` is not created. Verification duty `TASK-FR-DAT-008-03` (qualification); source `docs/backlog/backlog.csv` record 216, exact block `e65ef771eab4d64f190687d6089236f7b5f38f93b66ed4f696c41439a2ff364b`.

**Original preconditions**

1. a hidden source in a lineage path

**Original actions**

1. lineage is traversed

**Exact source oracles — all required**

1. the hidden source name and counts are not revealed
2. a permitted derivative may show a withheld source reference under its disclosure contract

Legacy same-requirement reuse candidates: `TC-DAT-008-01`, `TC-DAT-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
