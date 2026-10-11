## QA v1.3 — source-bound case design (proposed)

Story `FR-WFL-004` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-WFL-004-001` / `TC-IMPRANA-FR-WFL-004-001` | `REV_6a4bb24ed55087376097d2d7f3d1de16b055f6087c588b1ea719df6d93f4b510` / `REV_6ab40adbe5b95bdf14b49d97bff1da1d40fda9ba9b71eec0ed18fd267c77e96a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-004-002` / `TC-IMPRANA-FR-WFL-004-002` | `REV_12cdf2883b1763f1d392f78bdf16d6ac0393ebbd5bf2f062d6ae04b320499d0e` / `REV_d2349d3e7d54f08694c38aa4b5ea452033c09660c7cc2ba01844a06e8d21d5a4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-004-003` / `TC-IMPRANA-FR-WFL-004-003` | `REV_83ec0d42cb6580543a8e26538ff8b5eb3626fde4eac5447f5bc57163a3607361` / `REV_2a40ade61a9af90503b31ffc0db90b0826370f796b845af5f6b138391a29230e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-004-004` / `TC-IMPRANA-FR-WFL-004-004` | `REV_c5f1b2c43715ac8a2018be4d0f21766338b40515e8d786352e7612d43b4c4bfa` / `REV_e9559ab1d735f7f8f09b58421641454c140a2dc51158e2bb34192ddbd02f1267` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-004-005` / `TC-IMPRANA-FR-WFL-004-005` | `REV_bb5b90b0ecb615b54d3d35d02253d81776fac58dd998c278b7565ca5a313ffd6` / `REV_5214eb8a9c133f531bf80def66f2980a65171260104c167d7b84f2a867bd515f` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-WFL-004-001 — Delegate review work

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-004-001` is not created. Verification duty `TASK-FR-WFL-004-03` (qualification); source `docs/backlog/backlog.csv` record 318, exact block `6a4bb24ed55087376097d2d7f3d1de16b055f6087c588b1ea719df6d93f4b510`.

**Original preconditions**

1. a Reviewer sets a delegation with scope, start, end, delegate and reason

**Original actions**

1. work is routed during the delegation period

**Exact source oracles — all required**

1. the system verifies the delegate's eligibility and independence before routing

Legacy same-requirement reuse candidates: `TC-WFL-004-01`, `TC-WFL-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-004-002 — Escalate when the only reviewer is removed

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-004-002` is not created. Verification duty `TASK-FR-WFL-004-03` (qualification); source `docs/backlog/backlog.csv` record 318, exact block `12cdf2883b1763f1d392f78bdf16d6ac0393ebbd5bf2f062d6ae04b320499d0e`.

**Original preconditions**

1. the only assigned reviewer during period close

**Original actions**

1. that reviewer is removed

**Exact source oracles — all required**

1. an eligible backup is selected with attribution
2. the original reviewer receives no new protected task

Legacy same-requirement reuse candidates: `TC-WFL-004-01`, `TC-WFL-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-004-003 — Escalate on a missed deadline

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-004-003` is not created. Verification duty `TASK-FR-WFL-004-03` (qualification); source `docs/backlog/backlog.csv` record 318, exact block `83ec0d42cb6580543a8e26538ff8b5eb3626fde4eac5447f5bc57163a3607361`.

**Original preconditions**

1. a review task with a deadline

**Original actions**

1. the deadline passes

**Exact source oracles — all required**

1. the task escalates to a named backup or manager

Legacy same-requirement reuse candidates: `TC-WFL-004-01`, `TC-WFL-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-004-004 — Reject a delegate approving the delegator's own change

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-004-004` is not created. Verification duty `TASK-FR-WFL-004-03` (qualification); source `docs/backlog/backlog.csv` record 318, exact block `c5f1b2c43715ac8a2018be4d0f21766338b40515e8d786352e7612d43b4c4bfa`.

**Original preconditions**

1. a delegate acting for a Reviewer

**Original actions**

1. the delegate tries to approve a change authored by the delegator where independence is lost

**Exact source oracles — all required**

1. the approval is refused

Legacy same-requirement reuse candidates: `TC-WFL-004-01`, `TC-WFL-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-004-005 — Reject automatic approval when no replacement exists

Source persona: Reviewer. Proposed fixture `FIX-FR-WFL-004-005` is not created. Verification duty `TASK-FR-WFL-004-03` (qualification); source `docs/backlog/backlog.csv` record 318, exact block `bb5b90b0ecb615b54d3d35d02253d81776fac58dd998c278b7565ca5a313ffd6`.

**Original preconditions**

1. no eligible replacement reviewer exists

**Original actions**

1. escalation runs

**Exact source oracles — all required**

1. the work is marked Blocked and a management task is created
2. it is never automatically approved

Legacy same-requirement reuse candidates: `TC-WFL-004-01`, `TC-WFL-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
