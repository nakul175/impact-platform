## QA v1.3 — source-bound case design (proposed)

Story `FR-UX-007` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-UX-007-001` / `TC-IMPRANA-FR-UX-007-001` | `REV_bdb94ad4866c903fa06b163651a6372446e4d85a7b12a8acffc7a2d554b9b053` / `REV_d713a3db0055748ea175f856f952dfbf8a583c33be99d8800461b299e1bde969` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-007-002` / `TC-IMPRANA-FR-UX-007-002` | `REV_c6c630de5f42b4afc6fd24ba6c23f12edf43b3e26b3764a3dc097866666f786a` / `REV_5f59e56f0b638af169f48048ee5cdd24dd17b582c41c7bf78de01e660d224a45` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-007-003` / `TC-IMPRANA-FR-UX-007-003` | `REV_3d5c1502c9fac4fde6ee1c63543daa97704bd572094c0c35f02c70bd2abe375e` / `REV_60dcc920acfee60f609e78477b39a62851faae91293c359cf2f44ae62fe039a8` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-UX-007-001 — Core workflow works in each released language

Source persona: Data Author. Proposed fixture `FIX-FR-UX-007-001` is not created. Verification duty `TASK-FR-UX-007-03` (qualification); source `docs/backlog/backlog.csv` record 364, exact block `bdb94ad4866c903fa06b163651a6372446e4d85a7b12a8acffc7a2d554b9b053`.

**Original preconditions**

1. each released language

**Original actions**

1. a Data Author completes the same core workflow in it

**Exact source oracles — all required**

1. no untranslated blocking message or reversed layout obscures an action
2. right-to-left presentation is qualified where relevant

Legacy same-requirement reuse candidates: `TC-UX-007-01`, `TC-UX-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-007-002 — Reject release with incomplete translation

Source persona: Data Author. Proposed fixture `FIX-FR-UX-007-002` is not created. Verification duty `TASK-FR-UX-007-03` (qualification); source `docs/backlog/backlog.csv` record 364, exact block `c6c630de5f42b4afc6fd24ba6c23f12edf43b3e26b3764a3dc097866666f786a`.

**Original preconditions**

1. a language whose core workflow translation is incomplete

**Original actions**

1. release is requested

**Exact source oracles — all required**

1. release of the affected core workflows is blocked
2. machine translation alone is not accepted as a completed interface qualification

Legacy same-requirement reuse candidates: `TC-UX-007-01`, `TC-UX-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-007-003 — Reject fallback that changes stored meaning

Source persona: Data Author. Proposed fixture `FIX-FR-UX-007-003` is not created. Verification duty `TASK-FR-UX-007-03` (qualification); source `docs/backlog/backlog.csv` record 364, exact block `3d5c1502c9fac4fde6ee1c63543daa97704bd572094c0c35f02c70bd2abe375e`.

**Original preconditions**

1. a missing translation

**Original actions**

1. fallback language is used

**Exact source oracles — all required**

1. the fallback is explicit
2. stored codes and numeric semantics do not change

Legacy same-requirement reuse candidates: `TC-UX-007-01`, `TC-UX-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
