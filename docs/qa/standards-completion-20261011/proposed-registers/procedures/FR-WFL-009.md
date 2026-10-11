## QA v1.3 — source-bound case design (proposed)

Story `FR-WFL-009` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-WFL-009-001` / `TC-IMPRANA-FR-WFL-009-001` | `REV_a5c60f6632ddf418a0be1d4c9ff8daab9f755266d746a021596cfa6cb72e1853` / `REV_1cbe23112d94a23e524feb2e76762e40d97e855af7dac6a0fb917bd277f4869f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-009-002` / `TC-IMPRANA-FR-WFL-009-002` | `REV_4effcb0b2532d3053997cfced2a3182b4ad4344dbd7bbbc684ea5265e83ab564` / `REV_ff20bf11c161ddec2b1a3b11b5a4e740746955e189addda28f1e0b0055e78409` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-009-003` / `TC-IMPRANA-FR-WFL-009-003` | `REV_a1cde8b0669de2331c2d44830d62e5aa24832a7b5eb827ed274ab49a7408197d` / `REV_7748bc5ebf1b67b7918847c11b2010e60617ab54f8a6575de1825ad6dba79726` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-009-004` / `TC-IMPRANA-FR-WFL-009-004` | `REV_c770f2317ca5c8e277db3ee8e278b3bac5291a50b08b45cfc04bf59b833a1480` / `REV_4e0f9ae5ee560bde397e260580c15b6aef73e66735f004c7a7270d9248ec798c` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-WFL-009-001 — Overdue reminder rule updates one task

Source persona: Programme Manager. Proposed fixture `FIX-FR-WFL-009-001` is not created. Verification duty `TASK-FR-WFL-009-03` (qualification); source `docs/backlog/backlog.csv` record 365, exact block `a5c60f6632ddf418a0be1d4c9ff8daab9f755266d746a021596cfa6cb72e1853`.

**Original preconditions**

1. the Programme Manager has created an overdue reminder rule with an event trigger, conditions, a task update action, owner, scope and retry policy
2. the rule has been previewed against synthetic or permitted sample events

**Original actions**

1. the same overdue event occurs repeatedly

**Exact source oracles — all required**

1. exactly one task is produced
2. each execution records the input event and action receipt

Legacy same-requirement reuse candidates: `TC-WFL-009-01`, `TC-WFL-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-009-002 — Disabling a rule stops future actions

Source persona: Programme Manager. Proposed fixture `FIX-FR-WFL-009-002` is not created. Verification duty `TASK-FR-WFL-009-03` (qualification); source `docs/backlog/backlog.csv` record 365, exact block `4effcb0b2532d3053997cfced2a3182b4ad4344dbd7bbbc684ea5265e83ab564`.

**Original preconditions**

1. an active automation rule that has already committed actions

**Original actions**

1. the Programme Manager disables the rule

**Exact source oracles — all required**

1. no further actions are taken
2. the already committed actions are identified

Legacy same-requirement reuse candidates: `TC-WFL-009-01`, `TC-WFL-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-009-003 — Reject recursive unlimited reminders

Source persona: Programme Manager. Proposed fixture `FIX-FR-WFL-009-003` is not created. Verification duty `TASK-FR-WFL-009-03` (qualification); source `docs/backlog/backlog.csv` record 365, exact block `a1cde8b0669de2331c2d44830d62e5aa24832a7b5eb827ed274ab49a7408197d`.

**Original preconditions**

1. an automation rule whose action could re-trigger the rule

**Original actions**

1. the loop depth or frequency limit is reached

**Exact source oracles — all required**

1. no further reminders are created

Legacy same-requirement reuse candidates: `TC-WFL-009-01`, `TC-WFL-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-009-004 — Reject automation acting beyond its authority

Source persona: Programme Manager. Proposed fixture `FIX-FR-WFL-009-004` is not created. Verification duty `TASK-FR-WFL-009-03` (qualification); source `docs/backlog/backlog.csv` record 365, exact block `c770f2317ca5c8e277db3ee8e278b3bac5291a50b08b45cfc04bf59b833a1480`.

**Original preconditions**

1. an active automation rule

**Original actions**

1. it attempts to approve an object it generated, publish without approval or expand permissions

**Exact source oracles — all required**

1. the action is blocked

Legacy same-requirement reuse candidates: `TC-WFL-009-01`, `TC-WFL-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
