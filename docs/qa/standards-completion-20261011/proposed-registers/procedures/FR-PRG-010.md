## QA v1.3 — source-bound case design (proposed)

Story `FR-PRG-010` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRG-010-001` / `TC-IMPRANA-FR-PRG-010-001` | `REV_35875bb0a175d12e280b64a127c188642701fb15c55a90200e58dc13471d4740` / `REV_4810b285487d2fc665848e171e8c3cf8bdf3d79bbcaa32846b50dcdfc3deb085` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-010-002` / `TC-IMPRANA-FR-PRG-010-002` | `REV_19d7e14ae22df17910b8ce848d631160507226ef02ed1938a3e0c96a0429bfb0` / `REV_51009f52be9b52286e5917eba6c88c4148f4db3093b92e52a58d9c245f26d05f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-010-003` / `TC-IMPRANA-FR-PRG-010-003` | `REV_8b44bf3f15b7af514b4d12701196a3cebcb7e263e39c9f7ef450365801c0f521` / `REV_4c1769f644972558b6df93e69537757d4febefcd673203e5e9bd1948a01b7e33` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-010-004` / `TC-IMPRANA-FR-PRG-010-004` | `REV_d3d6e224683b0a96cbbb7007b32cfd3a353a06db6344db3c052472f6f6af5fd1` / `REV_d60159b889536e91710c982edbdaa616cdc8804758a55db7adf3d06fc607039d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-010-005` / `TC-IMPRANA-FR-PRG-010-005` | `REV_cfe2a5542f964fbe746026a81dd5bdb63a3b411ac27bbdd90b75e2d17848ca1f` / `REV_3573293447e9566cb0a3d9941e533bf60eed80af8164518654bc77c3b6c46c8e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRG-010-001 — Preview a bulk operation

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-PRG-010-001` is not created. Verification duty `TASK-FR-PRG-010-03` (qualification); source `docs/backlog/backlog.csv` record 355, exact block `35875bb0a175d12e280b64a127c188642701fb15c55a90200e58dc13471d4740`.

**Original preconditions**

1. an Organisation Administrator who selects a set of objects and one operation

**Original actions**

1. the preview runs

**Exact source oracles — all required**

1. every object's current revision and scope are validated
2. candidates are shown as valid, skipped or blocked

Legacy same-requirement reuse candidates: `TC-PRG-010-01`, `TC-PRG-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-010-002 — Execute with mixed candidates

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-PRG-010-002` is not created. Verification duty `TASK-FR-PRG-010-03` (qualification); source `docs/backlog/backlog.csv` record 355, exact block `19d7e14ae22df17910b8ce848d631160507226ef02ed1938a3e0c96a0429bfb0`.

**Original preconditions**

1. ten projects selected for reassignment, with two outside scope and one at a stale revision

**Original actions**

1. the Organisation Administrator executes the operation

**Exact source oracles — all required**

1. seven commit
2. three report safe reasons
3. an item manifest is returned

Legacy same-requirement reuse candidates: `TC-PRG-010-01`, `TC-PRG-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-010-003 — Retry has no new effect

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-PRG-010-003` is not created. Verification duty `TASK-FR-PRG-010-03` (qualification); source `docs/backlog/backlog.csv` record 355, exact block `8b44bf3f15b7af514b4d12701196a3cebcb7e263e39c9f7ef450365801c0f521`.

**Original preconditions**

1. a completed bulk template instantiation

**Original actions**

1. it is retried with the same operation identity

**Exact source oracles — all required**

1. no duplicate template instances are created

Legacy same-requirement reuse candidates: `TC-PRG-010-01`, `TC-PRG-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-010-004 — Reject mass approval

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-PRG-010-004` is not created. Verification duty `TASK-FR-PRG-010-03` (qualification); source `docs/backlog/backlog.csv` record 355, exact block `d3d6e224683b0a96cbbb7007b32cfd3a353a06db6344db3c052472f6f6af5fd1`.

**Original preconditions**

1. items awaiting approval

**Original actions**

1. a user tries to approve them through bulk administration

**Exact source oracles — all required**

1. the operation is refused

Legacy same-requirement reuse candidates: `TC-PRG-010-01`, `TC-PRG-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-010-005 — Reject changed candidates without refreshed review

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-PRG-010-005` is not created. Verification duty `TASK-FR-PRG-010-03` (qualification); source `docs/backlog/backlog.csv` record 355, exact block `cfe2a5542f964fbe746026a81dd5bdb63a3b411ac27bbdd90b75e2d17848ca1f`.

**Original preconditions**

1. a candidate that changed after the preview

**Original actions**

1. execution runs

**Exact source oracles — all required**

1. it is not committed until a refreshed review

Legacy same-requirement reuse candidates: `TC-PRG-010-01`, `TC-PRG-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
