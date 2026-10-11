## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-005-001` / `TC-IMPRANA-FR-ANA-005-001` | `REV_659bf24af4ef4eead5a32576dc66b6504a9b5777ec749dbd064bc06e88cf93d3` / `REV_660e4f29e841e12af4f5b4fb2a4c40d41f7fe3389c4e3ec85ef1c2ccd9330316` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-005-002` / `TC-IMPRANA-FR-ANA-005-002` | `REV_9a8525f4f9c0870d4b1e9da57967d95476c1a6f9202df02b8763ac1581ee1dcb` / `REV_8687cdef0c9b081d90fd0029eeb5734b372b568e155c1234c55510b579696bc0` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-005-003` / `TC-IMPRANA-FR-ANA-005-003` | `REV_033c4ecc83830a7ba1771b26f26dc302b2cf6dd31cc78950b4a8ccc918d24ad8` / `REV_88e089571795c7980bc327ca41d9dac54ce9825b38911db83c5cfb518f4a1560` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-005-004` / `TC-IMPRANA-FR-ANA-005-004` | `REV_88d3a86307303ec2ab98f610b2f4390bf1e044f4884652d51d89770a80805b63` / `REV_7bc54cb77f63b53c4130a524beee2ca5d0398a6ed9f58fb62f26b65191ec69a2` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-005-001 — Pivot participants by a multiselect service type

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-005-001` is not created. Verification duty `TASK-FR-ANA-005-03` (qualification); source `docs/backlog/backlog.csv` record 326, exact block `659bf24af4ef4eead5a32576dc66b6504a9b5777ec749dbd064bc06e88cf93d3`.

**Original preconditions**

1. participants have a multiselect service type

**Original actions**

1. the Analyst pivots participants by service type

**Exact source oracles — all required**

1. category totals may exceed the distinct grand total
2. that difference is explained
3. the grand total is recalculated from eligible source semantics rather than summed from displayed cells

Legacy same-requirement reuse candidates: `TC-ANA-005-01`, `TC-ANA-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-005-002 — Large pivot runs as a cancellable job

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-005-002` is not created. Verification duty `TASK-FR-ANA-005-03` (qualification); source `docs/backlog/backlog.csv` record 326, exact block `9a8525f4f9c0870d4b1e9da57967d95476c1a6f9202df02b8763ac1581ee1dcb`.

**Original preconditions**

1. a pivot whose preview estimates a large cardinality

**Original actions**

1. the Analyst runs it

**Exact source oracles — all required**

1. the request is routed to a cancellable job

Legacy same-requirement reuse candidates: `TC-ANA-005-01`, `TC-ANA-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-005-003 — Reject breaching disclosure policy in a pivot

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-005-003` is not created. Verification duty `TASK-FR-ANA-005-03` (qualification); source `docs/backlog/backlog.csv` record 326, exact block `033c4ecc83830a7ba1771b26f26dc302b2cf6dd31cc78950b4a8ccc918d24ad8`.

**Original preconditions**

1. a pivot that includes suppressed cells or nonadditive dimensions

**Original actions**

1. the pivot is displayed

**Exact source oracles — all required**

1. the suppressed cells and nonadditive dimensions retain their disclosure policy

Legacy same-requirement reuse candidates: `TC-ANA-005-01`, `TC-ANA-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-005-004 — Reject unsupported statistics

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-005-004` is not created. Verification duty `TASK-FR-ANA-005-03` (qualification); source `docs/backlog/backlog.csv` record 326, exact block `88d3a86307303ec2ab98f610b2f4390bf1e044f4884652d51d89770a80805b63`.

**Original preconditions**

1. the Analyst selects a statistic that is not supported

**Original actions**

1. the pivot is requested

**Exact source oracles — all required**

1. the pivot is blocked or a distinctly labelled alternative is required

Legacy same-requirement reuse candidates: `TC-ANA-005-01`, `TC-ANA-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
