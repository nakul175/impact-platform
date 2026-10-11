## QA v1.3 — source-bound case design (proposed)

Story `VF-CMP-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-CMP-001-001` / `TC-IMPRANA-VF-CMP-001-001` | `REV_c3fe085147dd8980858fbaa9e28d72247bf709cf76aabbde6dccf8c637a43a25` / `REV_0cda6dd2045e64545d484dbee6577d939517d47dc24ed4e3d7636f0cb3311c5d` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-CMP-001-002` / `TC-IMPRANA-VF-CMP-001-002` | `REV_0ee669eebad43ee05d14220567d39c9907abdef1c53d82c1447b1d0b2197ac23` / `REV_5498c767ac40fa877d012e3873a5dff63d0ec6701b3e56aec9a6e43ed063721e` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-CMP-001-003` / `TC-IMPRANA-VF-CMP-001-003` | `REV_53db262358a42d6e1aab80c8a8f8c028737b19008d17fce5bbdbd9558e093042` / `REV_a2c5d089dfd06c382f1248e0518e27372173c9596126ce53a400c627a72dde7f` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-CMP-001-001 — Current and previous browser versions are qualified

Source persona: Field Data Collector. Proposed fixture `FIX-VF-CMP-001-001` is not created. Verification duty `TASK-VF-CMP-001-02` (qualification); source `docs/backlog/backlog.csv` record 263, exact block `c3fe085147dd8980858fbaa9e28d72247bf709cf76aabbde6dccf8c637a43a25`.

**Original preconditions**

1. the current and previous major versions of Chrome, Edge, Firefox and Safari at release and the stated mobile OS and client profiles

**Original actions**

1. federation, file handling, accessibility, capture and recovery are tested in each declared supported combination

**Exact source oracles — all required**

1. each combination passes
2. the actual browser versions and qualified desktop, mobile and offline profiles are recorded

Legacy same-requirement reuse candidates: `TC-VF-CMP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-CMP-001-002 — Browser changes trigger regression checks

Source persona: Field Data Collector. Proposed fixture `FIX-VF-CMP-001-002` is not created. Verification duty `TASK-VF-CMP-001-02` (qualification); source `docs/backlog/backlog.csv` record 263, exact block `0ee669eebad43ee05d14220567d39c9907abdef1c53d82c1447b1d0b2197ac23`.

**Original preconditions**

1. a supported browser releases a change

**Original actions**

1. the change is identified

**Exact source oracles — all required**

1. regression checks are run

Legacy same-requirement reuse candidates: `TC-VF-CMP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-CMP-001-003 — Reject silent acceptance of work on unsupported clients

Source persona: Field Data Collector. Proposed fixture `FIX-VF-CMP-001-003` is not created. Verification duty `TASK-VF-CMP-001-02` (qualification); source `docs/backlog/backlog.csv` record 263, exact block `53db262358a42d6e1aab80c8a8f8c028737b19008d17fce5bbdbd9558e093042`.

**Original preconditions**

1. an unsupported browser or device

**Original actions**

1. a Field Data Collector tries to work on it

**Exact source oracles — all required**

1. clear guidance is shown
2. the client does not silently accept work it cannot preserve
3. offline support is not promised for a browser merely because online viewing works

Legacy same-requirement reuse candidates: `TC-VF-CMP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
