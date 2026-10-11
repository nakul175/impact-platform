## QA v1.3 — source-bound case design (proposed)

Story `US-CM-06` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-CM-06-001` / `TC-IMPRANA-US-CM-06-001` | `REV_6ea33333d296b7c04fc3929083686c042798eb3511309a3fbcc31c49f9390a2f` / `REV_290c73d7adbb54e5368ee24db52c62e066053cc23927d8eb13e0521dba7c4b43` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-06-002` / `TC-IMPRANA-US-CM-06-002` | `REV_1b95893d87c61b4fa9448bcaab73f0ede5822659a834a6bcc15d2879d18b4ecc` / `REV_55aacc5091d35ea82bc5019df03d3d6f188cd29b717d208d4c01b34ecbc2700b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-06-003` / `TC-IMPRANA-US-CM-06-003` | `REV_cca60a4f0afa9158ad053329bde7a8ed0ece55ed3012c68b4ec894a855d2f5be` / `REV_38284dd83e13f6cdb4f72a1809852f8943c9ea42c82d311080424c73e61106fe` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-CM-06-001 — Service packages listed with scope and price

Source persona: Operations Head. Proposed fixture `FIX-US-CM-06-001` is not created. Verification duty `TASK-US-CM-06-03` (qualification); source `docs/backlog/backlog.csv` record 206, exact block `6ea33333d296b7c04fc3929083686c042798eb3511309a3fbcc31c49f9390a2f`.

**Original preconditions**

1. fixed-fee service packages are offered

**Original actions**

1. the Operations Head views the service packages

**Exact source oracles — all required**

1. each package is listed with its scope and price

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-06-002 — Package added to the subscription invoice

Source persona: Operations Head. Proposed fixture `FIX-US-CM-06-002` is not created. Verification duty `TASK-US-CM-06-03` (qualification); source `docs/backlog/backlog.csv` record 206, exact block `1b95893d87c61b4fa9448bcaab73f0ede5822659a834a6bcc15d2879d18b4ecc`.

**Original preconditions**

1. an organisation with a subscription

**Original actions**

1. the Operations Head buys a fixed-fee service package

**Exact source oracles — all required**

1. the package is added to the same invoice as the subscription

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-06-003 — Reject a separate invoice or an unpriced package

Source persona: Operations Head. Proposed fixture `FIX-US-CM-06-003` is not created. Verification duty `TASK-US-CM-06-03` (qualification); source `docs/backlog/backlog.csv` record 206, exact block `cca60a4f0afa9158ad053329bde7a8ed0ece55ed3012c68b4ec894a855d2f5be`.

**Original preconditions**

1. an organisation with a subscription

**Original actions**

1. a service package is bought

**Exact source oracles — all required**

1. no separate invoice is raised for the package
2. a package without a stated scope or price is not offered

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
