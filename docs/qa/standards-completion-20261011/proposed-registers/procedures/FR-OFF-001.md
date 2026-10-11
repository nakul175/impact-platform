## QA v1.3 — source-bound case design (proposed)

Story `FR-OFF-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OFF-001-001` / `TC-IMPRANA-FR-OFF-001-001` | `REV_3bde9e198689e0e85698e1f2d5d6c19d992bc456664f30033a8b8c5352d5648f` / `REV_de3c409bee9abc9e6b7481c3fd6bbd6a579f11643262d7b68f9eea5c15cc5de7` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-001-002` / `TC-IMPRANA-FR-OFF-001-002` | `REV_88c21920116c36b663dae6865c97541562bc98aa19dac4901e64c2fc5ef9c49e` / `REV_5970c3e6c4bae4e9bc2aa28d2262ba7a023c96253729718a4e8aa2233b5e8ba6` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-001-003` / `TC-IMPRANA-FR-OFF-001-003` | `REV_456116ca84635d66fb62661e97b4ae5689afbd60c49aff18706b46177012a313` / `REV_6078fb2bf794d1bf1678fae8525473837392396226da49929327e7285b9f2653` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-001-004` / `TC-IMPRANA-FR-OFF-001-004` | `REV_70872ea9a4885f2dfc33bda58d87434d3b0a176abafcb7382c68e009d281c8f0` / `REV_33bd37489c1bf56f0821160f0722e4eceb6c250ca99973e0ca37de9f1f9fe989` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OFF-001-001 — Package assigned work for offline use

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-001-001` is not created. Verification duty `TASK-FR-OFF-001-03` (qualification); source `docs/backlog/backlog.csv` record 271, exact block `3bde9e198689e0e85698e1f2d5d6c19d992bc456664f30033a8b8c5352d5648f`.

**Original preconditions**

1. an authenticated Field Data Collector with three assigned households

**Original actions**

1. they preview and download the package

**Exact source oracles — all required**

1. the preview lists form versions, minimal reference fields, media size and expiry
2. the package is bound to the actor, tenant, device workspace and policy version
3. successful local preparation is confirmed before field departure

Legacy same-requirement reuse candidates: `TC-OFF-001-01`, `TC-OFF-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-001-002 — Complete assigned forms offline

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-001-002` is not created. Verification duty `TASK-FR-OFF-001-03` (qualification); source `docs/backlog/backlog.csv` record 271, exact block `88c21920116c36b663dae6865c97541562bc98aa19dac4901e64c2fc5ef9c49e`.

**Original preconditions**

1. the package is downloaded and the device is offline

**Original actions**

1. the collector opens their work

**Exact source oracles — all required**

1. they can complete forms for the three assigned households

Legacy same-requirement reuse candidates: `TC-OFF-001-01`, `TC-OFF-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-001-003 — Reject access beyond assigned work

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-001-003` is not created. Verification duty `TASK-FR-OFF-001-03` (qualification); source `docs/backlog/backlog.csv` record 271, exact block `456116ca84635d66fb62661e97b4ae5689afbd60c49aff18706b46177012a313`.

**Original preconditions**

1. the collector is offline with a package of three assigned households

**Original actions**

1. they try to browse a fourth unassigned household

**Exact source oracles — all required**

1. it is not available
2. no full project registry was downloaded by default

Legacy same-requirement reuse candidates: `TC-OFF-001-01`, `TC-OFF-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-001-004 — Reject expired assignments and offline renewal

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-001-004` is not created. Verification duty `TASK-FR-OFF-001-03` (qualification); source `docs/backlog/backlog.csv` record 271, exact block `70872ea9a4885f2dfc33bda58d87434d3b0a176abafcb7382c68e009d281c8f0`.

**Original preconditions**

1. an assignment has expired but is still visible in an old task list

**Original actions**

1. a package is prepared or renewed

**Exact source oracles — all required**

1. the expired assignment is excluded
2. renewal requires online policy verification

Legacy same-requirement reuse candidates: `TC-OFF-001-01`, `TC-OFF-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
