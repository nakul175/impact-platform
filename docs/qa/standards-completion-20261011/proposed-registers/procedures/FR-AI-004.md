## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-004-001` / `TC-IMPRANA-FR-AI-004-001` | `REV_1adc7b0bc50d837a5144ac6aafc41b8c74dcfb695f8e2e583f75cf597724e105` / `REV_c08a34d268bd80f576fa80e4af973bb3af4821d5dd31b910fecd76eec3f76b4a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-004-002` / `TC-IMPRANA-FR-AI-004-002` | `REV_f5a6b097da0688a869dd592c0e9e81086d19f29d170f0a2d57220db67a11e9e2` / `REV_05288c668348345cb521205734eef08da8997abe2c4f88e8b9563b9fa9832b54` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-004-003` / `TC-IMPRANA-FR-AI-004-003` | `REV_58ff0ea7b3abf4a6886b1c7e1235348559e61cacab7a9820b58b3d3961ea7120` / `REV_2ed37d0055a7aaff4042bf5982988fbab0b2baff8a7805ce98e6f9451d9d65e0` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-004-004` / `TC-IMPRANA-FR-AI-004-004` | `REV_7e0266ae88c5b5f42828145a5c838dca5f4dba847920df9d6246f61ee8b460c6` / `REV_e5cc70e17a76450372a4596732832394fe31186a49dc41f95903f2c1d31563ca` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-004-001 — Review mapping proposals with a diff

Source persona: Data Steward. Proposed fixture `FIX-FR-AI-004-001` is not created. Verification duty `TASK-FR-AI-004-03` (interface); source `docs/backlog/backlog.csv` record 184, exact block `1adc7b0bc50d837a5144ac6aafc41b8c74dcfb695f8e2e583f75cf597724e105`.

**Original preconditions**

1. an import with mapping assistance enabled

**Original actions**

1. the assistant returns proposals

**Exact source oracles — all required**

1. each shows the proposed link or deterministic transformation with affected sample rows
2. the Data Steward sees the exact mapping diff before accepting

Legacy same-requirement reuse candidates: `TC-AI-004-01`, `TC-AI-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-004-002 — Apply only approved deterministic changes

Source persona: Data Steward. Proposed fixture `FIX-FR-AI-004-002` is not created. Verification duty `TASK-FR-AI-004-03` (interface); source `docs/backlog/backlog.csv` record 184, exact block `f5a6b097da0688a869dd592c0e9e81086d19f29d170f0a2d57220db67a11e9e2`.

**Original preconditions**

1. a date normalisation suggestion and a name-based participant merge suggestion

**Original actions**

1. the Data Steward accepts the date normalisation and rejects the merge

**Exact source oracles — all required**

1. only the date conversion is applied, as a mapping draft or reviewed transformation version

Legacy same-requirement reuse candidates: `TC-AI-004-01`, `TC-AI-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-004-003 — Reject destructive AI actions

Source persona: Data Steward. Proposed fixture `FIX-FR-AI-004-003` is not created. Verification duty `TASK-FR-AI-004-03` (interface); source `docs/backlog/backlog.csv` record 184, exact block `58ff0ea7b3abf4a6886b1c7e1235348559e61cacab7a9820b58b3d3961ea7120`.

**Original preconditions**

1. AI mapping assistance

**Original actions**

1. it attempts to delete raw rows, merge identities or overwrite approved actuals

**Exact source oracles — all required**

1. the action is refused

Legacy same-requirement reuse candidates: `TC-AI-004-01`, `TC-AI-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-004-004 — Reject auto-selection of ambiguous mappings

Source persona: Data Steward. Proposed fixture `FIX-FR-AI-004-004` is not created. Verification duty `TASK-FR-AI-004-03` (interface); source `docs/backlog/backlog.csv` record 184, exact block `7e0266ae88c5b5f42828145a5c838dca5f4dba847920df9d6246f61ee8b460c6`.

**Original preconditions**

1. a low confidence or ambiguous mapping proposal

**Original actions**

1. proposals are presented

**Exact source oracles — all required**

1. it remains unselected until explicitly resolved

Legacy same-requirement reuse candidates: `TC-AI-004-01`, `TC-AI-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
