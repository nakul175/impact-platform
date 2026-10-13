## QA v1.3 — source-bound case design (proposed)

Story `FR-MIG-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-MIG-005-001` / `TC-IMPRANA-FR-MIG-005-001` | `REV_62f44b2aa53c9b03b74e85e9f49ad1336464a95685e0158ffca2dc30cfa3f910` / `REV_463e278473b0d1824c7ca6b7013228db71a4548af950473933afc605496574f9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-005-002` / `TC-IMPRANA-FR-MIG-005-002` | `REV_d623f5182f9ba7d871c0b8f61bcedc3e2bd1828cde51ce8fb828d1ab8a7a9673` / `REV_47ce95d2453e93f0b86caf90c19da2c852a2eb0dba788cedb44dd649f4ce7365` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-005-003` / `TC-IMPRANA-FR-MIG-005-003` | `REV_6b6f906fc35b3e204322066228234b9055d44b95fcee8cc4ee099e9aa63026fb` / `REV_e89e07b9b50bce113a3648be12ded44287f48119c29511dd41646711e2f02c7e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-005-004` / `TC-IMPRANA-FR-MIG-005-004` | `REV_e0a9f14db989c876ee3ded779f6a414dc2052977a04617d1da8e96b3f97f36fc` / `REV_c94c0cc6a1877f744055cc69a38c41e740a0ddac21e7a3c8bd91d2e799e5ac5f` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-MIG-005-001 — Late source update is captured

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-005-001` is not created. Verification duty `TASK-FR-MIG-005-04` (qualification); source `docs/backlog/backlog.csv` record 256, exact block `62f44b2aa53c9b03b74e85e9f49ad1336464a95685e0158ffca2dc30cfa3f910`.

**Original preconditions**

1. the final transfer is in progress

**Original actions**

1. one source record is updated

**Exact source oracles — all required**

1. the update receives a stable key
2. it is captured in the final delta or reported as a controlled exclusion requiring resolution

Legacy same-requirement reuse candidates: `TC-MIG-005-01`, `TC-MIG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-005-002 — Rollback identifies destination writes

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-005-002` is not created. Verification duty `TASK-FR-MIG-005-04` (qualification); source `docs/backlog/backlog.csv` record 256, exact block `d623f5182f9ba7d871c0b8f61bcedc3e2bd1828cde51ce8fb828d1ab8a7a9673`.

**Original preconditions**

1. destination writes have begun after authority switched

**Original actions**

1. the rollback trigger fires

**Exact source oracles — all required**

1. destination writes needing safe replay or reconciliation are identified

Legacy same-requirement reuse candidates: `TC-MIG-005-01`, `TC-MIG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-005-003 — Reject destination writes before the authority switch

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-005-003` is not created. Verification duty `TASK-FR-MIG-005-04` (qualification); source `docs/backlog/backlog.csv` record 256, exact block `6b6f906fc35b3e204322066228234b9055d44b95fcee8cc4ee099e9aa63026fb`.

**Original preconditions**

1. authority has not yet switched to the destination

**Original actions**

1. a destination write is attempted

**Exact source oracles — all required**

1. the write is refused

Legacy same-requirement reuse candidates: `TC-MIG-005-01`, `TC-MIG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-005-004 — Reject both systems publishing the same period

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-005-004` is not created. Verification duty `TASK-FR-MIG-005-04` (qualification); source `docs/backlog/backlog.csv` record 256, exact block `e0a9f14db989c876ee3ded779f6a414dc2052977a04617d1da8e96b3f97f36fc`.

**Original preconditions**

1. the source and destination systems during cutover

**Original actions**

1. both attempt to publish the same official period independently

**Exact source oracles — all required**

1. the duplicate publication is prevented

Legacy same-requirement reuse candidates: `TC-MIG-005-01`, `TC-MIG-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
