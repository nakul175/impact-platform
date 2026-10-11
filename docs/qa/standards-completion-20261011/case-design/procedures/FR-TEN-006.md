## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-006-001` / `TC-IMPRANA-FR-TEN-006-001` | `REV_1c82d627fe92fed7aa3b1468a6a621c5e307833cfffc97d88ac57ea5f1f77582` / `REV_01b1bb742d609b6e39d77895ac17c97bdf95d19382f741cf8ccc94a8871e6045` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-006-002` / `TC-IMPRANA-FR-TEN-006-002` | `REV_fbc75f8d9f932be4f4dcc71b3a03e4205af19e9b05ab8d5e88eeb2924f459764` / `REV_11a43fd8ea7f66c997917c9cdb2c0b3b7d95e91cfb2298db5da8c25a52050502` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-006-003` / `TC-IMPRANA-FR-TEN-006-003` | `REV_f1ca263ed20c6108c066773c24b7cc568c3640dac67e0c33b0eb8973c5241785` / `REV_e344c27f0111b417f458f139d434492302791adf38b19cdc50225dc6c838fd4b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-006-004` / `TC-IMPRANA-FR-TEN-006-004` | `REV_ce738d5914471d1041caf22b5638e9b4b23bff968b92a2c0e2b570f20ef7a4a9` / `REV_bb90d66c6ecbee3809fd6e09ec587e8804af1226e7aecf3214ad1c7681fdf8a1` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-006-001 — Create a partner agreement

Source persona: Programme Manager. Proposed fixture `FIX-FR-TEN-006-001` is not created. Verification duty `TASK-FR-TEN-006-03` (qualification); source `docs/backlog/backlog.csv` record 312, exact block `1c82d627fe92fed7aa3b1468a6a621c5e307833cfffc97d88ac57ea5f1f77582`.

**Original preconditions**

1. a Programme Manager

**Original actions**

1. they create a partner agreement naming projects, shared artifacts, allowed actions, purpose, dates and owner

**Exact source oracles — all required**

1. the agreement is recorded
2. it grants no tenant membership by itself

Legacy same-requirement reuse candidates: `TC-TEN-006-01`, `TC-TEN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-006-002 — Exchange an artifact across tenants

Source persona: Programme Manager. Proposed fixture `FIX-FR-TEN-006-002` is not created. Verification duty `TASK-FR-TEN-006-03` (qualification); source `docs/backlog/backlog.csv` record 312, exact block `fbc75f8d9f932be4f4dcc71b3a03e4205af19e9b05ab8d5e88eeb2924f459764`.

**Original preconditions**

1. an active partner agreement

**Original actions**

1. an artifact is exchanged across tenants under it

**Exact source oracles — all required**

1. an explicit destination copy is created with the source version and agreement reference
2. the transfer is recorded in the sharing register

Legacy same-requirement reuse candidates: `TC-TEN-006-01`, `TC-TEN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-006-003 — Share one indicator definition with two partners

Source persona: Programme Manager. Proposed fixture `FIX-FR-TEN-006-003` is not created. Verification duty `TASK-FR-TEN-006-03` (qualification); source `docs/backlog/backlog.csv` record 312, exact block `f1ca263ed20c6108c066773c24b7cc568c3640dac67e0c33b0eb8973c5241785`.

**Original preconditions**

1. an approved indicator definition shared with partners X and Y

**Original actions**

1. each partner submits data against it

**Exact source oracles — all required**

1. each partner sees only its own submissions
2. neither receives the other's completion statistics unless explicitly disclosed

Legacy same-requirement reuse candidates: `TC-TEN-006-01`, `TC-TEN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-006-004 — Reject transfers after the agreement expires

Source persona: Programme Manager. Proposed fixture `FIX-FR-TEN-006-004` is not created. Verification duty `TASK-FR-TEN-006-03` (qualification); source `docs/backlog/backlog.csv` record 312, exact block `ce738d5914471d1041caf22b5638e9b4b23bff968b92a2c0e2b570f20ef7a4a9`.

**Original preconditions**

1. a partner agreement has expired

**Original actions**

1. a new transfer is attempted under it

**Exact source oracles — all required**

1. the transfer is refused
2. live access is revoked
3. the agreed restriction or deletion process for retained copies starts, with external completion tracked separately

Legacy same-requirement reuse candidates: `TC-TEN-006-01`, `TC-TEN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
