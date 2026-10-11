## QA v1.3 — source-bound case design (proposed)

Story `FR-PLN-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PLN-006-001` / `TC-IMPRANA-FR-PLN-006-001` | `REV_56ce459a7908fbd26377085fe631eabc033b79078becb918b2f0c49d367eee3b` / `REV_3f681be24c4bc24cb742a8a9fa2f2976d3146fd914e1380e16954ea4ce5f454b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-006-002` / `TC-IMPRANA-FR-PLN-006-002` | `REV_18c4894ba3ffce3c8a6f989952d1133eb4faaf314b578796986142931b3392e6` / `REV_7d50346f0f172c5fd15277e489c5085f99428390dd08db3f03d700b3371fc3f9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-006-003` / `TC-IMPRANA-FR-PLN-006-003` | `REV_40c7959056e892379ef234d71795bdb7b077404bfacaa6d9755cd34ed140a544` / `REV_a2a74f9b6717699959680128ed909d89c91257862508f0d3232562f91fc1d7d1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-006-004` / `TC-IMPRANA-FR-PLN-006-004` | `REV_df3152075fae5026ab54843fc0f7c5a615bea32feb55bfa98db53a13a6a97038` / `REV_e827b3b74a28f4e2a41cedaa35418230fb31a419d198fd11858239cd800a7845` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PLN-006-001 — Completeness check creates remediation items

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-006-001` is not created. Verification duty `TASK-FR-PLN-006-03` (interface); source `docs/backlog/backlog.csv` record 145, exact block `56ce459a7908fbd26377085fe631eabc033b79078becb918b2f0c49d367eee3b`.

**Original preconditions**

1. a measurement plan in which an active indicator lacks source mode, method, collection owner, reviewer, calendar, coverage or evidence rule

**Original actions**

1. the MEL Manager runs activation

**Exact source oracles — all required**

1. the completeness check lists each gap
2. an assigned remediation item is created for each gap

Legacy same-requirement reuse candidates: `TC-PLN-006-01`, `TC-PLN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-006-002 — Activation shows the exact missing fields

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-006-002` is not created. Verification duty `TASK-FR-PLN-006-03` (interface); source `docs/backlog/backlog.csv` record 145, exact block `18c4894ba3ffce3c8a6f989952d1133eb4faaf314b578796986142931b3392e6`.

**Original preconditions**

1. a measurement plan with an unassigned reviewer and a missing denominator method

**Original actions**

1. the MEL Manager attempts to move the plan from Ready to Active

**Exact source oracles — all required**

1. both exact fields are shown
2. the plan cannot move from Ready to Active until both are resolved

Legacy same-requirement reuse candidates: `TC-PLN-006-01`, `TC-PLN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-006-003 — Reject an ineligible or non-independent collector and reviewer

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-006-003` is not created. Verification duty `TASK-FR-PLN-006-03` (interface); source `docs/backlog/backlog.csv` record 145, exact block `40c7959056e892379ef234d71795bdb7b077404bfacaa6d9755cd34ed140a544`.

**Original preconditions**

1. an indicator where collector and reviewer independence is required

**Original actions**

1. an ineligible person, or the collector, is assigned as reviewer

**Exact source oracles — all required**

1. the assignment is refused

Legacy same-requirement reuse candidates: `TC-PLN-006-01`, `TC-PLN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-006-004 — Reject a default zero series for a missing source binding

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-006-004` is not created. Verification duty `TASK-FR-PLN-006-03` (interface); source `docs/backlog/backlog.csv` record 145, exact block `df3152075fae5026ab54843fc0f7c5a615bea32feb55bfa98db53a13a6a97038`.

**Original preconditions**

1. an active indicator with no source binding

**Original actions**

1. activation runs

**Exact source oracles — all required**

1. no default zero series is substituted
2. the missing binding is reported as a gap

Legacy same-requirement reuse candidates: `TC-PLN-006-01`, `TC-PLN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
