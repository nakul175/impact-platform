## QA v1.3 — source-bound case design (proposed)

Story `FR-TEN-007` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-TEN-007-001` / `TC-IMPRANA-FR-TEN-007-001` | `REV_f93c5436c6ce8a16cad069732a4bc5839a7422b28ec8465967fd8d808fe2de1a` / `REV_8487d009260a06495d74ae7793eee3ba9e11d34d0e7ec23fe9f7f0ada76c93f1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-007-002` / `TC-IMPRANA-FR-TEN-007-002` | `REV_b384314f06f1d0dafdd7d905023c5cb404c9b74c88aac17eb96cf43afd428b60` / `REV_6316612cb28325ea7aa5f7f102b7199ffb6109d5b2bf8f5e1e0d647b14e5c6be` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-007-003` / `TC-IMPRANA-FR-TEN-007-003` | `REV_7bcb68b8080823e4804ae24f167d52da5f1fae0a3b6177172f3f4629a0089af8` / `REV_9442324561f026e1bf81f1a85e30ef40fe32a4ea80e93837eeef64152c216efb` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-007-004` / `TC-IMPRANA-FR-TEN-007-004` | `REV_179825c75599bc523f74fbd9b0915db29d7856b6c60cdbd082fa89234a16f23d` / `REV_75a93e6c8548995103456bd2f7f037141620f99dc2ceb459b4c38dcb4d46ea98` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-TEN-007-005` / `TC-IMPRANA-FR-TEN-007-005` | `REV_b3f8a7f328b9fb0c1b457b403e819d44fe23810f2b120ec27d9f9972be85f805` / `REV_d9acaf2fc625f5b846ffe54100c4b92a3c0882f00286315f052d7d4cad975322` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-TEN-007-001 — Inspect effective policy

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-007-001` is not created. Verification duty `TASK-FR-TEN-007-03` (qualification); source `docs/backlog/backlog.csv` record 313, exact block `f93c5436c6ce8a16cad069732a4bc5839a7422b28ec8465967fd8d808fe2de1a`.

**Original preconditions**

1. a project that inherits tenant policies

**Original actions**

1. the Organisation Administrator opens the policy editor

**Exact source oracles — all required**

1. it shows the effective tenant and project rules with the source of each restriction

Legacy same-requirement reuse candidates: `TC-TEN-007-01`, `TC-TEN-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-007-002 — Tighten a policy

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-007-002` is not created. Verification duty `TASK-FR-TEN-007-03` (qualification); source `docs/backlog/backlog.csv` record 313, exact block `b384314f06f1d0dafdd7d905023c5cb404c9b74c88aac17eb96cf43afd428b60`.

**Original preconditions**

1. the Organisation Administrator tightens a rule

**Original actions**

1. the impact is shown and they confirm it

**Exact source oracles — all required**

1. the tighter rule is applied

Legacy same-requirement reuse candidates: `TC-TEN-007-01`, `TC-TEN-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-007-003 — Request a permitted relaxation

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-007-003` is not created. Verification duty `TASK-FR-TEN-007-03` (qualification); source `docs/backlog/backlog.csv` record 313, exact block `7bcb68b8080823e4804ae24f167d52da5f1fae0a3b6177172f3f4629a0089af8`.

**Original preconditions**

1. a relaxation that policy permits

**Original actions**

1. the Organisation Administrator requests it

**Exact source oracles — all required**

1. an exception request is opened specifying scope, reason, compensating control, independent approver and expiry
2. when the exception expires the stricter rule is restored and dependent jobs are rechecked

Legacy same-requirement reuse candidates: `TC-TEN-007-01`, `TC-TEN-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-007-004 — Reject overriding a tenant prohibition

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-007-004` is not created. Verification duty `TASK-FR-TEN-007-03` (qualification); source `docs/backlog/backlog.csv` record 313, exact block `179825c75599bc523f74fbd9b0915db29d7856b6c60cdbd082fa89234a16f23d`.

**Original preconditions**

1. the tenant prohibits public raw participant exports
2. a project administrator owns the dataset

**Original actions**

1. an attempt is made to enable public raw participant exports for that dataset

**Exact source oracles — all required**

1. the platform rejects it

Legacy same-requirement reuse candidates: `TC-TEN-007-01`, `TC-TEN-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-TEN-007-005 — Reject forbidden exceptions and unresolved policy

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-TEN-007-005` is not created. Verification duty `TASK-FR-TEN-007-03` (qualification); source `docs/backlog/backlog.csv` record 313, exact block `b3f8a7f328b9fb0c1b457b403e819d44fe23810f2b120ec27d9f9972be85f805`.

**Original preconditions**

1. an exception that would permit cross tenant access, self approval or unsupported arithmetic, or a policy that is unknown, or an exception that has expired

**Original actions**

1. sensitive work is attempted under it

**Exact source oracles — all required**

1. the work is denied

Legacy same-requirement reuse candidates: `TC-TEN-007-01`, `TC-TEN-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
