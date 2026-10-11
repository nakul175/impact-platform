## QA v1.3 — source-bound case design (proposed)

Story `FR-MIG-003` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-MIG-003-001` / `TC-IMPRANA-FR-MIG-003-001` | `REV_0842b7d6db88b7324ecfa53842c66dff588d5e18b874860cd8d1b444660c9c41` / `REV_e9efb37518c92e5508be3ecdd1d404385692e5b40ebf6081d0905fdeffd9b98c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-003-002` / `TC-IMPRANA-FR-MIG-003-002` | `REV_1064f3028c7fe28f49def9586d46586faac9eba4cd22ee86f6152d2f7fa033fa` / `REV_962b63fb6f134c3fb4ff8d81beb6686c3dcb528036d229174719b26328211b5e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-003-003` / `TC-IMPRANA-FR-MIG-003-003` | `REV_04ce4fd1c137de503f569516c4fda8d32f7cbce013a8e492eab59353d2de11f8` / `REV_70c85a457f9c3b01fb4378ea4074114cbc12ffc509e1983be054e79096a3e39e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-MIG-003-001 — Pooled percentage and cumulative series are recomputed

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-003-001` is not created. Verification duty `TASK-FR-MIG-003-03` (governance); source `docs/backlog/backlog.csv` record 254, exact block `0842b7d6db88b7324ecfa53842c66dff588d5e18b874860cd8d1b444660c9c41`.

**Original preconditions**

1. a migrated pooled percentage and a migrated cumulative series

**Original actions**

1. both are independently recomputed

**Exact source oracles — all required**

1. semantic differences are resolved before signoff

Legacy same-requirement reuse candidates: `TC-MIG-003-01`, `TC-MIG-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-003-002 — Each variance is recorded with a decision

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-003-002` is not created. Verification duty `TASK-FR-MIG-003-03` (governance); source `docs/backlog/backlog.csv` record 254, exact block `1064f3028c7fe28f49def9586d46586faac9eba4cd22ee86f6152d2f7fa033fa`.

**Original preconditions**

1. a variance found during reconciliation

**Original actions**

1. it is recorded

**Exact source oracles — all required**

1. it captures source value, destination value, cause, severity and decision
2. accepted differences remain visible in migration metadata and, where material, in user-facing limitations

Legacy same-requirement reuse candidates: `TC-MIG-003-01`, `TC-MIG-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-003-003 — Reject cutover with critical unexplained differences

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-003-003` is not created. Verification duty `TASK-FR-MIG-003-03` (governance); source `docs/backlog/backlog.csv` record 254, exact block `04ce4fd1c137de503f569516c4fda8d32f7cbce013a8e492eab59353d2de11f8`.

**Original preconditions**

1. a critical unexplained result difference

**Original actions**

1. cutover is requested

**Exact source oracles — all required**

1. cutover is blocked
2. record count agreement alone does not satisfy reconciliation

Legacy same-requirement reuse candidates: `TC-MIG-003-01`, `TC-MIG-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
