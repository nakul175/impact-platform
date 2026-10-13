## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-008-001` / `TC-IMPRANA-FR-OPS-008-001` | `REV_3ae4627dd65fcc6b165655379af1bb19b082c02f12473fc49154b4fb4b74d0df` / `REV_e21b9c0c0ec798a523de0a68ec9aa7333daa12ca70e3cffbbcdd305ad72249e7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-008-002` / `TC-IMPRANA-FR-OPS-008-002` | `REV_29acd756de1c2041d2d154603b00f1f6c9d38905b43e4a9d18dc6ddc46a4e723` / `REV_84b566488d858047a3286f3b32cfdf676bc6a14fc2f2365fca4355a0a0e43fd6` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-008-003` / `TC-IMPRANA-FR-OPS-008-003` | `REV_a7f66178008d9185892135d51dd2cf0618a514e2eb556b0a34c39e43d6ff7e27` / `REV_e22bc4deb6dc2a327166545a0e782b2d87d8b95fcfa5117b1e5b13a669645876` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-008-004` / `TC-IMPRANA-FR-OPS-008-004` | `REV_8fbf7b282c9cfa050921af402c1ad05be5fe2c397f9fbeec87ea692bbf904480` / `REV_441fa2e8118f3c19edc57d4a2b7c371f7d391a24206c9a57eabcb1e2fc3653b6` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-008-001 — Expensive AI workload reaches its allowance

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-008-001` is not created. Verification duty `TASK-FR-OPS-008-03` (qualification); source `docs/backlog/backlog.csv` record 309, exact block `3ae4627dd65fcc6b165655379af1bb19b082c02f12473fc49154b4fb4b74d0df`.

**Original preconditions**

1. an expensive AI workload

**Original actions**

1. it runs to its allowance

**Exact source oracles — all required**

1. queuing is bounded
2. usage is attributed to the workload
3. ordinary approvals are unaffected

Legacy same-requirement reuse candidates: `TC-OPS-008-01`, `TC-OPS-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-008-002 — Usage views and thresholds without payloads

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-008-002` is not created. Verification duty `TASK-FR-OPS-008-03` (qualification); source `docs/backlog/backlog.csv` record 309, exact block `29acd756de1c2041d2d154603b00f1f6c9d38905b43e4a9d18dc6ddc46a4e723`.

**Original preconditions**

1. tenants with active workloads

**Original actions**

1. the Platform Operator opens usage views

**Exact source oracles — all required**

1. admitted work, completed jobs, storage, source runs and model consumption are shown without payloads
2. thresholds identify projected capacity pressure and expensive workloads

Legacy same-requirement reuse candidates: `TC-OPS-008-01`, `TC-OPS-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-008-003 — Cleanup only after dependency and retention checks

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-008-003` is not created. Verification duty `TASK-FR-OPS-008-03` (qualification); source `docs/backlog/backlog.csv` record 309, exact block `a7f66178008d9185892135d51dd2cf0618a514e2eb556b0a34c39e43d6ff7e27`.

**Original preconditions**

1. temporary or orphan objects

**Original actions**

1. cleanup runs

**Exact source oracles — all required**

1. objects are removed only after dependency and retention checks pass

Legacy same-requirement reuse candidates: `TC-OPS-008-01`, `TC-OPS-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-008-004 — Reject cancelling another tenant's critical jobs

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-008-004` is not created. Verification duty `TASK-FR-OPS-008-03` (qualification); source `docs/backlog/backlog.csv` record 309, exact block `8fbf7b282c9cfa050921af402c1ad05be5fe2c397f9fbeec87ea692bbf904480`.

**Original preconditions**

1. one tenant has a cost spike

**Original actions**

1. the Platform Operator manages capacity

**Exact source oracles — all required**

1. another tenant's critical jobs are not cancelled to hide the spike
2. approved budgets and operational limits are visible before any restrictive change

Legacy same-requirement reuse candidates: `TC-OPS-008-01`, `TC-OPS-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
