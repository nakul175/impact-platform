## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-003-001` / `TC-IMPRANA-FR-ANA-003-001` | `REV_16f2b3a5a4e483dd6166bcc465004ec170aa7340f4dc6ff33b3ba7486d8ff4ac` / `REV_285f6c9eafe4c61fd725beffde98711a0257ab2bde42fe883d3e8ad482721c60` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-003-002` / `TC-IMPRANA-FR-ANA-003-002` | `REV_4d3916218dc4256b1333ae5f46a5ad41c98775746e16267f5f6130e930bba495` / `REV_05db87ae3d5fb6de558a77357b5e3205b8e07c8d555caca8ca1bcd342b2e2dc1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-003-003` / `TC-IMPRANA-FR-ANA-003-003` | `REV_88a0b2ecc580b956f25042638d96b26bf4fdb11950531aaaff161e6d07874b01` / `REV_d4a07e7efc8faa696061eba12359767ec817bf8ccbf791f62faaa83b8ea310c0` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-003-004` / `TC-IMPRANA-FR-ANA-003-004` | `REV_64115e2e24472e354ef7fe7b04365676654718a89c4ff5fe2013d8e3f403eaa3` / `REV_22ea7e31781002baad680eb85de67a25416db9368dbd3ae6a88200d090556c0a` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-003-001 — Lower-is-better target shown correctly

Source persona: Programme Manager. Proposed fixture `FIX-FR-ANA-003-001` is not created. Verification duty `TASK-FR-ANA-003-03` (qualification); source `docs/backlog/backlog.csv` record 67, exact block `16f2b3a5a4e483dd6166bcc465004ec170aa7340f4dc6ff33b3ba7486d8ff4ac`.

**Original preconditions**

1. an indicator with a lower-is-better target of ten
2. an actual value of eight

**Original actions**

1. the comparison widget is displayed

**Exact source oracles — all required**

1. it shows the correct status and declared deviation
2. it does not give an inverted success interpretation

Legacy same-requirement reuse candidates: `TC-ANA-003-01`, `TC-ANA-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-003-002 — Labels, scales and overachievement are explicit

Source persona: Programme Manager. Proposed fixture `FIX-FR-ANA-003-002` is not created. Verification duty `TASK-FR-ANA-003-03` (qualification); source `docs/backlog/backlog.csv` record 67, exact block `4d3916218dc4256b1333ae5f46a5ad41c98775746e16267f5f6130e930bba495`.

**Original preconditions**

1. a comparison widget bound to actual, baseline and a selected target version with direction and time semantic

**Original actions**

1. it is displayed

**Exact source oracles — all required**

1. labels identify whether the target is original or revised and its applicable period
2. axis scales and percentage calculations are explicit
3. overachievement remains visible

Legacy same-requirement reuse candidates: `TC-ANA-003-01`, `TC-ANA-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-003-003 — Reject comparing incompatible time semantics

Source persona: Programme Manager. Proposed fixture `FIX-FR-ANA-003-003` is not created. Verification duty `TASK-FR-ANA-003-03` (qualification); source `docs/backlog/backlog.csv` record 67, exact block `88a0b2ecc580b956f25042638d96b26bf4fdb11950531aaaff161e6d07874b01`.

**Original preconditions**

1. a cumulative actual curve and a monthly flow target

**Original actions**

1. no approved conversion exists

**Exact source oracles — all required**

1. the comparison is blocked

Legacy same-requirement reuse candidates: `TC-ANA-003-01`, `TC-ANA-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-003-004 — Reject an infinite trend from a zero baseline

Source persona: Programme Manager. Proposed fixture `FIX-FR-ANA-003-004` is not created. Verification duty `TASK-FR-ANA-003-03` (qualification); source `docs/backlog/backlog.csv` record 67, exact block `64115e2e24472e354ef7fe7b04365676654718a89c4ff5fe2013d8e3f403eaa3`.

**Original preconditions**

1. a baseline of zero

**Original actions**

1. percentage change is calculated

**Exact source oracles — all required**

1. the result is undefined
2. no infinite trend is shown

Legacy same-requirement reuse candidates: `TC-ANA-003-01`, `TC-ANA-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
