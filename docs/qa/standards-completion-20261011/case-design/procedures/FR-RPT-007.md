## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-007` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-007-001` / `TC-IMPRANA-FR-RPT-007-001` | `REV_a29dbbb21ef85589ca62781c054336cf42c7a623094e0dfbc7affcf0eadfd4bd` / `REV_06796ef0aa9ad358a2776861e60836d934a43dcdd580fcccc2ea0b18d19999d6` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-007-002` / `TC-IMPRANA-FR-RPT-007-002` | `REV_54ae4a04f9bae49fb59f34486c6dc76fefd08d1a3a61cdf7403d9a32cf831870` / `REV_f7b7d487de5c94b9fd65a6ae7eb6459065cd53cb8770366a6a5f8fb0f57691ba` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-007-003` / `TC-IMPRANA-FR-RPT-007-003` | `REV_35124f2d66d3bcd5c5fefee2c33f8f6af3a6b6e9e4fd26d65bf4443f423fae5a` / `REV_07076cde21f723186a5504cce30e3127ee7fb966bb61eb2007253d60867a384a` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-007-001 — Publish an approved version to a funder

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-007-001` is not created. Verification duty `TASK-FR-RPT-007-03` (qualification); source `docs/backlog/backlog.csv` record 140, exact block `a29dbbb21ef85589ca62781c054336cf42c7a623094e0dfbc7affcf0eadfd4bd`.

**Original preconditions**

1. a report version has been approved and any required privacy review is complete
2. the MEL Manager is an authorised publisher with current assurance

**Original actions**

1. the MEL Manager reviews the preview of version, audience, disclosure checks and expiry and confirms publication to a funder

**Exact source oracles — all required**

1. a disclosure record and a stable versioned reference are created
2. only the eligible funder can access the published artifact

Legacy same-requirement reuse candidates: `TC-RPT-007-01`, `TC-RPT-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-007-002 — Reject access to a draft by guessed URL

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-007-002` is not created. Verification duty `TASK-FR-RPT-007-03` (qualification); source `docs/backlog/backlog.csv` record 140, exact block `54ae4a04f9bae49fb59f34486c6dc76fefd08d1a3a61cdf7403d9a32cf831870`.

**Original preconditions**

1. a draft report that has not been published

**Original actions**

1. someone guesses its URL or filename

**Exact source oracles — all required**

1. the draft content is not accessible
2. it is not exposed through search indexing

Legacy same-requirement reuse candidates: `TC-RPT-007-01`, `TC-RPT-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-007-003 — Reject broadening the audience by a link toggle

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-007-003` is not created. Verification duty `TASK-FR-RPT-007-03` (qualification); source `docs/backlog/backlog.csv` record 140, exact block `35124f2d66d3bcd5c5fefee2c33f8f6af3a6b6e9e4fd26d65bf4443f423fae5a`.

**Original preconditions**

1. a report published to a funder

**Original actions**

1. a user attempts to make it available to a broader audience by toggling a link

**Exact source oracles — all required**

1. the change is refused until a new disclosure decision is made

Legacy same-requirement reuse candidates: `TC-RPT-007-01`, `TC-RPT-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
