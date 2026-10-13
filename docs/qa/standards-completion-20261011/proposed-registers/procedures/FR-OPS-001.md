## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-001-001` / `TC-IMPRANA-FR-OPS-001-001` | `REV_1bc843201a10bda988363f1c842f5eb1feeb8c3d85be63016852d27a6b22fa7f` / `REV_2d8a7ec29611317eabd2e7037bc325080c4503c1c374d34ec181c0046c2eb338` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-001-002` / `TC-IMPRANA-FR-OPS-001-002` | `REV_d7d4024b5b2b6d3ad70c2b8904f677eb390345e666cf488d0e686cf857babf5e` / `REV_1e89a14caa22407aeb96ae6a13d7001d0688b6f2a3f93cf83680e29f1671a783` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-001-003` / `TC-IMPRANA-FR-OPS-001-003` | `REV_b7100139b41dfdfa8ec6e986b1fb4a96976a7fd398d86623277b662516512eb3` / `REV_c4b997ddc9e304c39e0f4f0c65ef797cdb4f373e49a3b241f847076ddecf737c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-001-004` / `TC-IMPRANA-FR-OPS-001-004` | `REV_83812f68b2cdbccc7801730ea660f0f0431eb5d85afac4b868ebfccc8b15a3c1` / `REV_9c9b50c02c2a3903ea8899ab58e3c5eae23317aa9c986933367eb3c39a844e58` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-001-001 — Suspend the intended tenant after preview

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-001-001` is not created. Verification duty `TASK-FR-OPS-001-03` (qualification); source `docs/backlog/backlog.csv` record 161, exact block `1bc843201a10bda988363f1c842f5eb1feeb8c3d85be63016852d27a6b22fa7f`.

**Original preconditions**

1. a synthetic tenant selected in the operations console

**Original actions**

1. the Platform Operator previews suspension and confirms it with a reason and the required assurance

**Exact source oracles — all required**

1. the preview shows the exact tenant and effect
2. only that tenant's permitted lifecycle effects occur
3. an operation receipt is recorded

Legacy same-requirement reuse candidates: `TC-OPS-001-01`, `TC-OPS-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-001-002 — Console shows operational data without programme content

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-001-002` is not created. Verification duty `TASK-FR-OPS-001-03` (qualification); source `docs/backlog/backlog.csv` record 161, exact block `d7d4024b5b2b6d3ad70c2b8904f677eb390345e666cf488d0e686cf857babf5e`.

**Original preconditions**

1. a tenant in the operations console

**Original actions**

1. the Platform Operator opens it

**Exact source oracles — all required**

1. tenant identity, lifecycle, plan, health and limits are shown
2. no programme content is shown

Legacy same-requirement reuse candidates: `TC-OPS-001-01`, `TC-OPS-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-001-003 — Reject participant names in metadata search

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-001-003` is not created. Verification duty `TASK-FR-OPS-001-03` (qualification); source `docs/backlog/backlog.csv` record 161, exact block `b7100139b41dfdfa8ec6e986b1fb4a96976a7fd398d86623277b662516512eb3`.

**Original preconditions**

1. operational metadata search in the console

**Original actions**

1. the Platform Operator searches using a participant's name

**Exact source oracles — all required**

1. no participant name is revealed

Legacy same-requirement reuse candidates: `TC-OPS-001-01`, `TC-OPS-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-001-004 — Reject cross-tenant effects of suspension

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-001-004` is not created. Verification duty `TASK-FR-OPS-001-03` (qualification); source `docs/backlog/backlog.csv` record 161, exact block `83812f68b2cdbccc7801730ea660f0f0431eb5d85afac4b868ebfccc8b15a3c1`.

**Original preconditions**

1. two active tenants

**Original actions**

1. one tenant is suspended

**Exact source oracles — all required**

1. the other tenant's access and jobs are unchanged

Legacy same-requirement reuse candidates: `TC-OPS-001-01`, `TC-OPS-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
