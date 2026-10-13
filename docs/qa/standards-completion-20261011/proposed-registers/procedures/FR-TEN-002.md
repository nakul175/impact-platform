## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-002-001` / `TC-IMPRANA-FR-TEN-002-001` | `REV_b43f51abe1bfa211140f7a450f23c17e02b848608364501cd765e32c78103057` / `REV_33d7e82e5501673410ad00ffffc8bb8ee65f14f722ca11cc3b36dd9bdf6b9117` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-002-002` / `TC-IMPRANA-FR-TEN-002-002` | `REV_c7f8b09e5a1aeeb0a8271f06459502e6726845c3811649bc68c0059b3f366412` / `REV_798d82984795bebbaa30ef56225f68f0d49b1a285bd3d1ec23df58c9b0738b6a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-002-003` / `TC-IMPRANA-FR-TEN-002-003` | `REV_a676a2d1d6706de4af106e5898e30f4dddf44ced32e834693e4ff60cbc31085f` / `REV_2c1b29cb1879da67301fa2ed6a5cb7fb1c8ed1b422c61b364977a4f873d1d128` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-002-004` / `TC-IMPRANA-FR-TEN-002-004` | `REV_0c955ef825a965e6bb33a2aa799889ca95e02fa355715c8bf3f48f5c763b42a8` / `REV_128a6fa46d2149e16bcc3df84ef55c08647db8b2052261b6ae96f09feda06692` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-002-001 — Create a unit

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-002-001` is not created. Verification duty `TASK-FR-TEN-002-03` (interface); source `docs/backlog/backlog.csv` record 166, exact block `b43f51abe1bfa211140f7a450f23c17e02b848608364501cd765e32c78103057`.

**Original preconditions**

1. an Organisation Administrator

**Original actions**

1. they create a unit with a stable code and an optional parent

**Exact source oracles — all required**

1. the unit is created with that code and parent

Legacy same-requirement reuse candidates: `TC-TEN-002-01`, `TC-TEN-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-002-002 — Move a project with a preview and effective date

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-002-002` is not created. Verification duty `TASK-FR-TEN-002-03` (interface); source `docs/backlog/backlog.csv` record 166, exact block `c7f8b09e5a1aeeb0a8271f06459502e6726845c3811649bc68c0059b3f366412`.

**Original preconditions**

1. project P belongs to office East

**Original actions**

1. the Organisation Administrator previews moving project P to office West effective 1 July
2. they confirm the move

**Exact source oracles — all required**

1. the preview shows the reporting membership, every explicit access grant that would change and future obligations
2. the change applies from 1 July and the old parent East is recorded
3. June reporting retains East as its organisational context

Legacy same-requirement reuse candidates: `TC-TEN-002-01`, `TC-TEN-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-002-003 — Reject self parenting and descendant cycles

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-002-003` is not created. Verification duty `TASK-FR-TEN-002-03` (interface); source `docs/backlog/backlog.csv` record 166, exact block `a676a2d1d6706de4af106e5898e30f4dddf44ced32e834693e4ff60cbc31085f`.

**Original preconditions**

1. unit U has a descendant unit D

**Original actions**

1. the Organisation Administrator sets U as its own parent or sets D as the parent of U

**Exact source oracles — all required**

1. the change is rejected

Legacy same-requirement reuse candidates: `TC-TEN-002-01`, `TC-TEN-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-002-004 — Reject implicit changes to existing grants

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-002-004` is not created. Verification duty `TASK-FR-TEN-002-03` (interface); source `docs/backlog/backlog.csv` record 166, exact block `0c955ef825a965e6bb33a2aa799889ca95e02fa355715c8bf3f48f5c763b42a8`.

**Original preconditions**

1. a confirmed move would affect existing access grants

**Original actions**

1. the move is applied

**Exact source oracles — all required**

1. existing grants change only through an explicit reviewed access change
2. historical reports retain their original organisational context

Legacy same-requirement reuse candidates: `TC-TEN-002-01`, `TC-TEN-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
