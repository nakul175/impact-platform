## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-003-001` / `TC-IMPRANA-FR-TEN-003-001` | `REV_bf803b2954a5c45d231f80d0af11c2da820cb3ecb6e0c4492bba32c9c7ac5161` / `REV_a305e40408900c12f7b4edffbd6da83ed6f0636b4e7cb04f516e0771a8d20a1f` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-003-002` / `TC-IMPRANA-FR-TEN-003-002` | `REV_b699350115aeacb24be2e85cbbd8d1c2ca8cbc51361bdface42cd4f2f5df4b95` / `REV_9e78ea4fde0b31b5483ef866e8953831629d2b7c926f2e609af56615e03ac278` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-003-003` / `TC-IMPRANA-FR-TEN-003-003` | `REV_ff3ae71aefd08531043799731bb4210df4aa019096763d6e6e195950134c4c6a` / `REV_43b3bfc5718c689051f5957bd3b41a419d8d0c454181d436d78dca5e48a5347f` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-003-004` / `TC-IMPRANA-FR-TEN-003-004` | `REV_2da3bde22ce3f2297fcb19c183222db6ab8205f05acb87be3d118e86dc443146` / `REV_46301dab5e4b88321d8c003701aba4f162909faaa99ee0af81690cb2458dbbaf` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-003-001 — List memberships and open a second tenant

Source persona: Reviewer. Proposed fixture `FIX-FR-TEN-003-001` is not created. Verification duty `TASK-FR-TEN-003-03` (qualification); source `docs/backlog/backlog.csv` record 167, exact block `bf803b2954a5c45d231f80d0af11c2da820cb3ecb6e0c4492bba32c9c7ac5161`.

**Original preconditions**

1. a Reviewer with active memberships in tenants A and B

**Original actions**

1. they open the tenant selector
2. they open tenant B in a new tab

**Exact source oracles — all required**

1. it lists their active memberships and display identities
2. existing tabs remain bound to tenant A

Legacy same-requirement reuse candidates: `TC-TEN-003-01`, `TC-TEN-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-003-002 — Switch tenant in the same tab

Source persona: Reviewer. Proposed fixture `FIX-FR-TEN-003-002` is not created. Verification duty `TASK-FR-TEN-003-03` (qualification); source `docs/backlog/backlog.csv` record 167, exact block `b699350115aeacb24be2e85cbbd8d1c2ca8cbc51361bdface42cd4f2f5df4b95`.

**Original preconditions**

1. a Reviewer is working in tenant A in a tab

**Original actions**

1. they switch that tab to tenant B

**Exact source oracles — all required**

1. tenant A scoped recent items and unsent AI context are cleared

Legacy same-requirement reuse candidates: `TC-TEN-003-01`, `TC-TEN-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-003-003 — Reject reuse of a permission from another tenant

Source persona: Reviewer. Proposed fixture `FIX-FR-TEN-003-003` is not created. Verification duty `TASK-FR-TEN-003-03` (qualification); source `docs/backlog/backlog.csv` record 167, exact block `ff3ae71aefd08531043799731bb4210df4aa019096763d6e6e195950134c4c6a`.

**Original preconditions**

1. a Reviewer holds reviewer rights in tenant A and collector rights in tenant B
2. they approve an item from a tenant A tab

**Original actions**

1. the tenant B tab attempts to reuse that permission or source reference

**Exact source oracles — all required**

1. the command is rejected because the resource belongs to another tenant

Legacy same-requirement reuse candidates: `TC-TEN-003-01`, `TC-TEN-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-003-004 — Reject restoring protected cached content on back navigation

Source persona: Reviewer. Proposed fixture `FIX-FR-TEN-003-004` is not created. Verification duty `TASK-FR-TEN-003-03` (qualification); source `docs/backlog/backlog.csv` record 167, exact block `2da3bde22ce3f2297fcb19c183222db6ab8205f05acb87be3d118e86dc443146`.

**Original preconditions**

1. a Reviewer has left a protected page

**Original actions**

1. they use browser back navigation to return to it

**Exact source oracles — all required**

1. the historic page is reauthorised
2. protected cached content is not restored without reauthorisation

Legacy same-requirement reuse candidates: `TC-TEN-003-01`, `TC-TEN-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
