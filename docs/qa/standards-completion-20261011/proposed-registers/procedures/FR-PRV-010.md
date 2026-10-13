## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-010` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-010-001` / `TC-IMPRANA-FR-PRV-010-001` | `REV_7082368f8a422a344c9c2fd003e60caa89a002ee837dd92f18d5a87e6efc91de` / `REV_b90856438f7855b48b8eb61ed826f95f73243fca5c32f8146f7807fdb95cedba` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-010-002` / `TC-IMPRANA-FR-PRV-010-002` | `REV_f6207e75c71e7f506daeccf0816ae93a1255eb8248b8524e3f0de153ee8c512c` / `REV_95ba9b02c270054dd6e59d770a2cce0153db157cb76ea6fc7851ffa05a7739cd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-010-003` / `TC-IMPRANA-FR-PRV-010-003` | `REV_a3f599fd9cc945b7e116725a714edeb46a3ef0c50bc7234a66d0ef1dc11aafb9` / `REV_94ee47439f363663148702e8df381283891c49a655c8f709a21912851f401e60` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-010-004` / `TC-IMPRANA-FR-PRV-010-004` | `REV_0f9941f7ed7ee4ffff26d9a50fbfbebfdf359f2f388e693f39c45d6c62bf94d9` / `REV_e5c910463955063c5c9f0ad53d816f31de9755db7448f3e0bd6d27123d83719f` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-010-001 — Synthetic personal markers do not reach general logs

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-010-001` is not created. Verification duty `TASK-FR-PRV-010-04` (qualification); source `docs/backlog/backlog.csv` record 134, exact block `7082368f8a422a344c9c2fd003e60caa89a002ee837dd92f18d5a87e6efc91de`.

**Original preconditions**

1. import and AI failures containing synthetic personal markers

**Original actions**

1. the failures are logged

**Exact source oracles — all required**

1. none of the markers appears in general traces or analytics events

Legacy same-requirement reuse candidates: `TC-PRV-010-01`, `TC-PRV-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-010-002 — Telemetry is limited to permitted fields

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-010-002` is not created. Verification duty `TASK-FR-PRV-010-04` (qualification); source `docs/backlog/backlog.csv` record 134, exact block `f6207e75c71e7f506daeccf0816ae93a1255eb8248b8524e3f0de153ee8c512c`.

**Original preconditions**

1. the telemetry schema

**Original actions**

1. telemetry events are emitted

**Exact source oracles — all required**

1. they contain only correlation, error category, timings and bounded operational metadata
2. sensitive payload fields, credentials and unrestricted document text are excluded or redacted before general logging

Legacy same-requirement reuse candidates: `TC-PRV-010-01`, `TC-PRV-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-010-003 — Product analytics follow tenant opt-in or approved policy

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-010-003` is not created. Verification duty `TASK-FR-PRV-010-04` (qualification); source `docs/backlog/backlog.csv` record 134, exact block `a3f599fd9cc945b7e116725a714edeb46a3ef0c50bc7234a66d0ef1dc11aafb9`.

**Original preconditions**

1. a tenant without analytics opt-in or an approved policy

**Original actions**

1. product analytics would be collected

**Exact source oracles — all required**

1. no product analytics are collected for that tenant

Legacy same-requirement reuse candidates: `TC-PRV-010-01`, `TC-PRV-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-010-004 — Reject diagnostics or evaluation samples taken from routine logging

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-010-004` is not created. Verification duty `TASK-FR-PRV-010-04` (qualification); source `docs/backlog/backlog.csv` record 134, exact block `0f9941f7ed7ee4ffff26d9a50fbfbebfdf359f2f388e693f39c45d6c62bf94d9`.

**Original preconditions**

1. routine operational logging is enabled

**Original actions**

1. support diagnostics or model evaluation samples are needed

**Exact source oracles — all required**

1. support diagnostics are provided only as a separate controlled export with expiry
2. model evaluation samples do not inherit permission from routine operational logging

Legacy same-requirement reuse candidates: `TC-PRV-010-01`, `TC-PRV-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
