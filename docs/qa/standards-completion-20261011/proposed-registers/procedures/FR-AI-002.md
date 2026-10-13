## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-002-001` / `TC-IMPRANA-FR-AI-002-001` | `REV_36f9d4aa1893da9a7d9bb3c91b366b98ec16cb1332cb8f0b5cf46e2c9fc86a75` / `REV_dbce38b81c8d9c29e211b6a727e1381d8276592c202e605f13186e8ba91387d7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-002-002` / `TC-IMPRANA-FR-AI-002-002` | `REV_262ee14068afa9891bb4d65547071f4002a90826b74f70b44afc6be298032f53` / `REV_58ed4c384aa3206f6b58bc701f4b2a57140221e01e7f2c5bacab47861c78b2ee` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-002-003` / `TC-IMPRANA-FR-AI-002-003` | `REV_f5cc1570c215cec176e80c4b252d8689feb4df774f299bb83256366e986ed222` / `REV_14b86228017f73fba687d8ec91523640570e87793a86ffcb5a649b67b7d2b405` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-002-004` / `TC-IMPRANA-FR-AI-002-004` | `REV_20bb38a78d66b6761e992f24630a6aa1c0cdc9ee3c78d833fb78b2a6e0a0c010` / `REV_f7335f295b3b6f5da85f330395c930de1fd151f0a7769cf2deecc193c06ef99c` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-002-001 — Extraction returns traceable proposals

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-002-001` is not created. Verification duty `TASK-FR-AI-002-03` (interface); source `docs/backlog/backlog.csv` record 182, exact block `36f9d4aa1893da9a7d9bb3c91b366b98ec16cb1332cb8f0b5cf46e2c9fc86a75`.

**Original preconditions**

1. permitted proposal and logframe files selected for extraction

**Original actions**

1. extraction runs

**Exact source oracles — all required**

1. each proposed entity and field shows source version, page or section and evidence span
2. each is classified as extracted, inferred or suggested

Legacy same-requirement reuse candidates: `TC-AI-002-01`, `TC-AI-002-02`, `TC-AT25`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-002-002 — Selective acceptance in the review panel

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-002-002` is not created. Verification duty `TASK-FR-AI-002-03` (interface); source `docs/backlog/backlog.csv` record 182, exact block `262ee14068afa9891bb4d65547071f4002a90826b74f70b44afc6be298032f53`.

**Original preconditions**

1. extraction results in the review panel

**Original actions**

1. the MEL Manager accepts some proposals

**Exact source oracles — all required**

1. only the accepted proposals are applied
2. unresolved ambiguities are retained

Legacy same-requirement reuse candidates: `TC-AI-002-01`, `TC-AI-002-02`, `TC-AT25`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-002-003 — Conflicting and missing values are flagged

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-002-003` is not created. Verification duty `TASK-FR-AI-002-03` (interface); source `docs/backlog/backlog.csv` record 182, exact block `f5cc1570c215cec176e80c4b252d8689feb4df774f299bb83256366e986ed222`.

**Original preconditions**

1. a proposal with two end dates and no population

**Original actions**

1. it is extracted

**Exact source oracles — all required**

1. both end dates are presented separately and flagged
2. the population field remains missing and flagged
3. activation remains blocked until they are reviewed

Legacy same-requirement reuse candidates: `TC-AI-002-01`, `TC-AI-002-02`, `TC-AT25`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-002-004 — Reject unsupported commitments

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-002-004` is not created. Verification duty `TASK-FR-AI-002-03` (interface); source `docs/backlog/backlog.csv` record 182, exact block `20bb38a78d66b6761e992f24630a6aa1c0cdc9ee3c78d833fb78b2a6e0a0c010`.

**Original preconditions**

1. a date, target or population commitment with no direct source support

**Original actions**

1. extraction completes

**Exact source oracles — all required**

1. the value stays missing unless a human adds it explicitly
2. contradictory sources are not merged into a single value

Legacy same-requirement reuse candidates: `TC-AI-002-01`, `TC-AI-002-02`, `TC-AT25`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
