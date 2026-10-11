## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-007-001` / `TC-IMPRANA-FR-INT-007-001` | `REV_0ee26c8d4a693e308b7e9257f4e7ff771dd49618fbab7e34334ec978770a16f1` / `REV_32b459e29512082a15be5647aeaf815ac4ca2310341d30041a18a85534c12a71` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-007-002` / `TC-IMPRANA-FR-INT-007-002` | `REV_f74826752479614a2b95cf726c453a52717e13bc9383ea4a8584fb486a78dd29` / `REV_9d01829e6a78a2f01cde8a4c405ad2d4d7125ef4a1c1276d4e7a8622257b1bea` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-007-003` / `TC-IMPRANA-FR-INT-007-003` | `REV_f23ae60003227538430cb939f3f30acc9fcdafece9a2f3efa0129aa01610db8a` / `REV_356ec9035dd52a5f3f8d5121c6e2ec26fd9a81ff69105a24edb3432173cc7592` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-007-004` / `TC-IMPRANA-FR-INT-007-004` | `REV_e2569dd177490e3766905a2caf9b4a259713a3ce3ccac0d1179466d855274af3` / `REV_7d21a58a481eb0ae90412510ad4a804ae934488be30ca71341d0f0110fedfff4` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-007-001 — Limits are visible before activation

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-007-001` is not created. Verification duty `TASK-FR-INT-007-03` (qualification); source `docs/backlog/backlog.csv` record 250, exact block `0ee26c8d4a693e308b7e9257f4e7ff771dd49618fbab7e34334ec978770a16f1`.

**Original preconditions**

1. an Integration Developer preparing to activate a connection

**Original actions**

1. they review the connection before activation

**Exact source oracles — all required**

1. the limits for the tenant, credential and job class are displayed

Legacy same-requirement reuse candidates: `TC-INT-007-01`, `TC-INT-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-007-002 — Exceeded admission limit returns safe retry guidance

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-007-002` is not created. Verification duty `TASK-FR-INT-007-03` (qualification); source `docs/backlog/backlog.csv` record 250, exact block `f74826752479614a2b95cf726c453a52717e13bc9383ea4a8584fb486a78dd29`.

**Original preconditions**

1. a connector that has reached its admission limit

**Original actions**

1. it submits another job

**Exact source oracles — all required**

1. the request is refused with LIMIT_EXCEEDED and safe retry guidance
2. jobs already approved show their queue position class and a cancellation option

Legacy same-requirement reuse candidates: `TC-INT-007-01`, `TC-INT-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-007-003 — Unrelated tenants are unaffected by one tenant's full bulk queue

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-007-003` is not created. Verification duty `TASK-FR-INT-007-03` (qualification); source `docs/backlog/backlog.csv` record 250, exact block `f23ae60003227538430cb939f3f30acc9fcdafece9a2f3efa0129aa01610db8a`.

**Original preconditions**

1. one tenant's bulk queue has been exceeded

**Original actions**

1. unrelated tenants save records and submit approvals

**Exact source oracles — all required**

1. those saves and approvals continue within their qualified targets
2. interactive approvals keep their own capacity protection

Legacy same-requirement reuse candidates: `TC-INT-007-01`, `TC-INT-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-007-004 — Reject unlimited pending jobs and early retries

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-007-004` is not created. Verification duty `TASK-FR-INT-007-03` (qualification); source `docs/backlog/backlog.csv` record 250, exact block `e2569dd177490e3766905a2caf9b4a259713a3ce3ccac0d1179466d855274af3`.

**Original preconditions**

1. a noisy connector that has exceeded its limit

**Original actions**

1. it keeps submitting jobs or retries earlier than the indicated window

**Exact source oracles — all required**

1. it cannot accumulate unlimited pending jobs
2. the early retry neither expands its quota nor starves other tenants

Legacy same-requirement reuse candidates: `TC-INT-007-01`, `TC-INT-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
