## QA v1.3 — source-bound case design (proposed)

Story `VF-SEC-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-SEC-001-001` / `TC-IMPRANA-VF-SEC-001-001` | `REV_a945748d8464dc01642d6cf490bde2ff4aff372acaf1254d2d445ac03bb032c9` / `REV_9030f8de09d151a18db87f4427961d1465913b62f7bf93da65b2cdbb4191f046` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-SEC-001-002` / `TC-IMPRANA-VF-SEC-001-002` | `REV_3422234c3640b51408e4db1e369e55ffdd26e4a3bea7dd2b8a2374d27c303c80` / `REV_ea81beffbcd161fdd87511abcdda27f135af31435cdd93b8bd975b359f415191` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-SEC-001-003` / `TC-IMPRANA-VF-SEC-001-003` | `REV_418aebd7c07cc1c402a31dd2e418a77bcea95871cea9d193cdc0a280080d4c1a` / `REV_11053a39f3f4369101c876a887e584eb2e1ff10df4a8b3a105d83b4ea9935da3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-SEC-001-001 — Release proceeds with complete security evidence

Source persona: Platform Operator. Proposed fixture `FIX-VF-SEC-001-001` is not created. Verification duty `TASK-VF-SEC-001-02` (qualification); source `docs/backlog/backlog.csv` record 159, exact block `a945748d8464dc01642d6cf490bde2ff4aff372acaf1254d2d445ac03bb032c9`.

**Original preconditions**

1. passing evidence for all applicable baseline security controls
2. independent assessment, retest evidence and scoped mitigation records

**Original actions**

1. the release gate is evaluated

**Exact source oracles — all required**

1. the release may proceed

Legacy same-requirement reuse candidates: `TC-VF-SEC-001`, `SEC-045`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-SEC-001-002 — Finding with an effective verified mitigation does not block release

Source persona: Platform Operator. Proposed fixture `FIX-VF-SEC-001-002` is not created. Verification duty `TASK-VF-SEC-001-02` (qualification); source `docs/backlog/backlog.csv` record 159, exact block `3422234c3640b51408e4db1e369e55ffdd26e4a3bea7dd2b8a2374d27c303c80`.

**Original preconditions**

1. a critical or high vulnerability with an effective verified mitigation

**Original actions**

1. the release gate is evaluated

**Exact source oracles — all required**

1. that finding does not block the release

Legacy same-requirement reuse candidates: `TC-VF-SEC-001`, `SEC-045`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-SEC-001-003 — Reject release with an unmitigated exposure

Source persona: Platform Operator. Proposed fixture `FIX-VF-SEC-001-003` is not created. Verification duty `TASK-VF-SEC-001-02` (qualification); source `docs/backlog/backlog.csv` record 159, exact block `418aebd7c07cc1c402a31dd2e418a77bcea95871cea9d193cdc0a280080d4c1a`.

**Original preconditions**

1. an unresolved critical or high vulnerability affecting confidentiality, integrity or access without an effective verified mitigation

**Original actions**

1. the release gate is evaluated

**Exact source oracles — all required**

1. the release is blocked
2. neither a product priority waiver nor functional parity can override the gate

Legacy same-requirement reuse candidates: `TC-VF-SEC-001`, `SEC-045`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
