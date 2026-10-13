## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-004-001` / `TC-IMPRANA-FR-INT-004-001` | `REV_5de9e62628204f13808f16436e652e8de62af2c2fb6f1081b051df598027dd48` / `REV_bb7947c23e76e32d583af4838d51e528a21e1446b1c6f58b36319f7c0a60d547` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-004-002` / `TC-IMPRANA-FR-INT-004-002` | `REV_89995c29f116bae85bda60c8f73cfb20a3a9acf8a2bb5f196a68e2b45730b162` / `REV_23d0fa6b157ce4440b18f761a106c4af36e87d2689154d7930aa21283cf19e6e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-004-003` / `TC-IMPRANA-FR-INT-004-003` | `REV_a91663a95033de8525133296ebed2db0ef095455abc0179f507818d9394b6726` / `REV_0ce9f91bde731fa37cbc47cebe9ec87a7780ddd5cd80c0e05e620187d122b1d8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-004-004` / `TC-IMPRANA-FR-INT-004-004` | `REV_606741f43bf6b64d4bfdd4fdea3952a4cc20b885ccdf314d21a05b5d68903736` / `REV_4b7535b185db954db73a7b0e2d34dd620152e3503c42d1a8c95d06e4272b5cd8` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-004-001 — API responses are consistent

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-004-001` is not created. Verification duty `TASK-FR-INT-004-03` (qualification); source `docs/backlog/backlog.csv` record 248, exact block `5de9e62628204f13808f16436e652e8de62af2c2fb6f1081b051df598027dd48`.

**Original preconditions**

1. a resource in the business API catalogue

**Original actions**

1. the Integration Developer retrieves or lists it

**Exact source oracles — all required**

1. responses include stable ID, revision, business state and permitted metadata
2. lists support stable pagination, documented filters and explicit projection of allowed fields

Legacy same-requirement reuse candidates: `TC-INT-004-01`, `TC-INT-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-004-002 — Reject self-approval through the API

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-004-002` is not created. Verification duty `TASK-FR-INT-004-03` (qualification); source `docs/backlog/backlog.csv` record 248, exact block `89995c29f116bae85bda60c8f73cfb20a3a9acf8a2bb5f196a68e2b45730b162`.

**Original preconditions**

1. the Integration Developer has created a draft indicator through the API and submitted it

**Original actions**

1. they attempt direct approval as its author

**Exact source oracles — all required**

1. the same independence rule as the interface blocks the approval

Legacy same-requirement reuse candidates: `TC-INT-004-01`, `TC-INT-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-004-003 — Reject bypassing interface checks

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-004-003` is not created. Verification duty `TASK-FR-INT-004-03` (qualification); source `docs/backlog/backlog.csv` record 248, exact block `a91663a95033de8525133296ebed2db0ef095455abc0179f507818d9394b6726`.

**Original preconditions**

1. an API request

**Original actions**

1. it attempts to bypass interface validation, hidden fields, workflow or publication checks

**Exact source oracles — all required**

1. the request is refused

Legacy same-requirement reuse candidates: `TC-INT-004-01`, `TC-INT-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-004-004 — Reject cross tenant signals in bulk requests

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-004-004` is not created. Verification duty `TASK-FR-INT-004-03` (qualification); source `docs/backlog/backlog.csv` record 248, exact block `606741f43bf6b64d4bfdd4fdea3952a4cc20b885ccdf314d21a05b5d68903736`.

**Original preconditions**

1. a bulk request that references items from another tenant

**Original actions**

1. it is processed

**Exact source oracles — all required**

1. each item returns a safe per item outcome
2. no cross tenant existence is signalled

Legacy same-requirement reuse candidates: `TC-INT-004-01`, `TC-INT-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
