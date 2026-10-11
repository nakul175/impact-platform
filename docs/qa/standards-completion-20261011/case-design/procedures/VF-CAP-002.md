## QA v1.3 — source-bound case design (proposed)

Story `VF-CAP-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-CAP-002-001` / `TC-IMPRANA-VF-CAP-002-001` | `REV_9d6bb3828414e4cc889b892fefa03b4ff13947be68748e42e45e53ab1b9922c5` / `REV_8a35ecf393c932122c4d0d59d0a52a3cbb8a4aa35092c5687bb82d79910c07a8` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-CAP-002-002` / `TC-IMPRANA-VF-CAP-002-002` | `REV_74c988c208c78e801b22d9f3363a16af25c289d89b4860eb53685906b6b15824` / `REV_2f5f7688460a427f7dd3f8ae5d40576d8fd2c1df4bdf6d56d4fb8696ddf4b623` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-CAP-002-003` / `TC-IMPRANA-VF-CAP-002-003` | `REV_564dada2017b75510a2cb33e9e2495563d29766bf7473c3462f968a4ce792fd2` / `REV_8fe5a8177c171e525778c7c7fc318500fe4c5ee7ffd72d4cfe6c1420a2b0cc03` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-CAP-002-001 — Burst load is handled predictably and recovers

Source persona: Platform Operator. Proposed fixture `FIX-VF-CAP-002-001` is not created. Verification duty `TASK-VF-CAP-002-02` (qualification); source `docs/backlog/backlog.csv` record 262, exact block `9d6bb3828414e4cc889b892fefa03b4ff13947be68748e42e45e53ab1b9922c5`.

**Original preconditions**

1. the baseline workload

**Original actions**

1. a five-minute twofold arrival burst is applied

**Exact source oracles — all required**

1. work is admitted, queued or limited predictably
2. queues stay bounded and the service recovers to baseline after the burst

Legacy same-requirement reuse candidates: `TC-VF-CAP-002`, `SEC-028`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-CAP-002-002 — Noisy tenant does not cause other tenants to miss targets

Source persona: Platform Operator. Proposed fixture `FIX-VF-CAP-002-002` is not created. Verification duty `TASK-VF-CAP-002-02` (qualification); source `docs/backlog/backlog.csv` record 262, exact block `74c988c208c78e801b22d9f3363a16af25c289d89b4860eb53685906b6b15824`.

**Original preconditions**

1. a noisy tenant running a large bulk import or AI job
2. representative other tenants saving and approving records

**Original actions**

1. the workloads run together

**Exact source oracles — all required**

1. the unrelated tenants continue to meet core service targets
2. queue depth, rejections and recovery to baseline are measured

Legacy same-requirement reuse candidates: `TC-VF-CAP-002`, `SEC-028`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-CAP-002-003 — Reject unbounded queues, starvation or hidden violations

Source persona: Platform Operator. Proposed fixture `FIX-VF-CAP-002-003` is not created. Verification duty `TASK-VF-CAP-002-02` (qualification); source `docs/backlog/backlog.csv` record 262, exact block `564dada2017b75510a2cb33e9e2495563d29766bf7473c3462f968a4ce792fd2`.

**Original preconditions**

1. results from the burst and noisy-tenant tests

**Original actions**

1. the results are reviewed

**Exact source oracles — all required**

1. unbounded queue growth fails the test
2. unexplained starvation fails the test
3. target violations hidden by service-wide averages fail the test

Legacy same-requirement reuse candidates: `TC-VF-CAP-002`, `SEC-028`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
