## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-004-001` / `TC-IMPRANA-FR-OPS-004-001` | `REV_8281ea6489749ea9ae809be3e8fb994196aa0c9e38511ae707db08bf42ca3857` / `REV_8b5304e31df6b201fdd60491328080d5b593e56c62f2c62e4ca70c6924d6bd9a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-004-002` / `TC-IMPRANA-FR-OPS-004-002` | `REV_23422bcd2254c8c7206b9a1e23c22583ab9f4f0d4787755de19275d8cfb3eebf` / `REV_13af9ecd401e95d7b5859fc4097db5a34b0e7c07736167fa3d9ec3994265d2c0` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-004-003` / `TC-IMPRANA-FR-OPS-004-003` | `REV_82a04d068cfbb1c035fcbcc94787536ef66f911d6d0b0a3d6f04038bfbec7697` / `REV_9ee24bf5cc4d8928ba87749b0e80ca20460b5751996af0996e2e192a9ede5ecc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-004-004` / `TC-IMPRANA-FR-OPS-004-004` | `REV_02a74bebf4cc90ac8e11d241bd1e26bd8296895cace67ac4641085fc2c47f936` / `REV_dc3ca7f95f488c073388cd189da76bb5c8d3a477dae69af3286b2bf7ff760c6a` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-004-001 — Resolve a failed import with safe error references

Source persona: Support Agent. Proposed fixture `FIX-FR-OPS-004-001` is not created. Verification duty `TASK-FR-OPS-004-03` (qualification); source `docs/backlog/backlog.csv` record 308, exact block `8281ea6489749ea9ae809be3e8fb994196aa0c9e38511ae707db08bf42ca3857`.

**Original preconditions**

1. a support case for a failed import with safe correlation IDs

**Original actions**

1. the Support Agent investigates

**Exact source oracles — all required**

1. the problem can be resolved using safe error references
2. attached diagnostics show their classification and scope

Legacy same-requirement reuse candidates: `TC-OPS-004-01`, `TC-OPS-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-004-002 — Content inspection uses a separate approved session

Source persona: Support Agent. Proposed fixture `FIX-FR-OPS-004-002` is not created. Verification duty `TASK-FR-OPS-004-03` (qualification); source `docs/backlog/backlog.csv` record 308, exact block `23422bcd2254c8c7206b9a1e23c22583ab9f4f0d4787755de19275d8cfb3eebf`.

**Original preconditions**

1. content inspection becomes necessary on a case

**Original actions**

1. the Support Agent requests content access

**Exact source oracles — all required**

1. a separate approved support session starts
2. the case retains the explicit approved access grant and its expiry

Legacy same-requirement reuse candidates: `TC-OPS-004-01`, `TC-OPS-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-004-003 — Reject content browsing on the strength of a ticket

Source persona: Support Agent. Proposed fixture `FIX-FR-OPS-004-003` is not created. Verification duty `TASK-FR-OPS-004-03` (qualification); source `docs/backlog/backlog.csv` record 308, exact block `82a04d068cfbb1c035fcbcc94787536ef66f911d6d0b0a3d6f04038bfbec7697`.

**Original preconditions**

1. an open support case without an approved support session

**Original actions**

1. the Support Agent attempts to browse tenant data

**Exact source oracles — all required**

1. access is refused

Legacy same-requirement reuse candidates: `TC-OPS-004-01`, `TC-OPS-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-004-004 — Reject retaining closed case attachments

Source persona: Support Agent. Proposed fixture `FIX-FR-OPS-004-004` is not created. Verification duty `TASK-FR-OPS-004-03` (qualification); source `docs/backlog/backlog.csv` record 308, exact block `02a74bebf4cc90ac8e11d241bd1e26bd8296895cace67ac4641085fc2c47f936`.

**Original preconditions**

1. a closed case with attachments

**Original actions**

1. the applicable retention period ends

**Exact source oracles — all required**

1. the attachments expire

Legacy same-requirement reuse candidates: `TC-OPS-004-01`, `TC-OPS-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
