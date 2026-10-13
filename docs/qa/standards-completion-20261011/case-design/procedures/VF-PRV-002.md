## QA v1.3 — source-bound case design (proposed)

Story `VF-PRV-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PRV-002-001` / `TC-IMPRANA-VF-PRV-002-001` | `REV_f73b7a46a284d5077e7954e53aec415f31b33af63fd757a6db5a80374429de10` / `REV_f95b5343481d6c744c5f3d319698d142360235388ed4fa2dddab18bba40eda9c` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PRV-002-002` / `TC-IMPRANA-VF-PRV-002-002` | `REV_bf0eb2a95fe208e4a6f7b2dccb012808ba872e18af2ce4de155de5aad1fb88b5` / `REV_7fa30ca2b66f67233902834932c5458485e9b5c6d4c2c5aa6bd5a94342afe5e5` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PRV-002-003` / `TC-IMPRANA-VF-PRV-002-003` | `REV_5c213daa2b27fab65df44683a4ae9572e8d1e711a32b86870d666cd29cbc4782` / `REV_da9687e3fa5002a1dff9a7d6d03111b7c4d95a2e6738f6f6f9e681855eea41b1` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PRV-002-001 — Retention policies are approved before collection

Source persona: Privacy Officer. Proposed fixture `FIX-VF-PRV-002-001` is not created. Verification duty `TASK-VF-PRV-002-03` (qualification); source `docs/backlog/backlog.csv` record 136, exact block `f73b7a46a284d5077e7954e53aec415f31b33af63fd757a6db5a80374429de10`.

**Original preconditions**

1. a production tenant

**Original actions**

1. real data collection is about to start

**Exact source oracles — all required**

1. approved record and evidence retention policies are already in place

Legacy same-requirement reuse candidates: `TC-VF-PRV-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PRV-002-002 — Default retention periods are applied

Source persona: Privacy Officer. Proposed fixture `FIX-VF-PRV-002-002` is not created. Verification duty `TASK-VF-PRV-002-03` (qualification); source `docs/backlog/backlog.csv` record 136, exact block `bf0eb2a95fe208e4a6f7b2dccb012808ba872e18af2ce4de155de5aad1fb88b5`.

**Original preconditions**

1. synthetic objects in each retention class

**Original actions**

1. qualified expiry conditions are advanced

**Exact source oracles — all required**

1. diagnostic logs are kept for 90 days or less by default
2. retained AI prompt and response content is kept for 30 days or less unless a justified policy specifies otherwise
3. scheduled action receipts, holds and exceptions are recorded

Legacy same-requirement reuse candidates: `TC-VF-PRV-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PRV-002-003 — Reject shared schedules or hidden copies

Source persona: Privacy Officer. Proposed fixture `FIX-VF-PRV-002-003` is not created. Verification duty `TASK-VF-PRV-002-03` (qualification); source `docs/backlog/backlog.csv` record 136, exact block `5c213daa2b27fab65df44683a4ae9572e8d1e711a32b86870d666cd29cbc4782`.

**Original preconditions**

1. AI content, diagnostic logs, security metadata and business evidence

**Original actions**

1. retention schedules are inspected

**Exact source oracles — all required**

1. each class has its own distinct schedule
2. any hidden orphan copy fails the gate

Legacy same-requirement reuse candidates: `TC-VF-PRV-002`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
