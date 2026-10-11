## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-007-001` / `TC-IMPRANA-FR-SEC-007-001` | `REV_bafb7de439420c18ca182266bc899710a1ff68d1751c0b1f6979c67499358c42` / `REV_67f8ff471cae68a4b5f25cf91b8368518df5d35bd94c53874f66d7440bd12527` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-007-002` / `TC-IMPRANA-FR-SEC-007-002` | `REV_d7f954b97fa22c1ef57d3668560984303a4efd840906b0eebc11862eb43d0c69` / `REV_8164a812d08571d8f51a25e06b0d703596e73c41be2868dbe909afb466d9bab8` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-007-003` / `TC-IMPRANA-FR-SEC-007-003` | `REV_a3996a919cca62e6bf9567d3df6d9facd0f96b07a111b9f0c0f7ae36ddfbe7a3` / `REV_fd16a72da23e978c8e4a2bc098e9950f7099c7ea4c49440c12a7085b511d62fa` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-007-004` / `TC-IMPRANA-FR-SEC-007-004` | `REV_fc48451ad6b7b72d9f9cf00ccc70f663b4dea60232532905895aad1d0e78a08f` / `REV_466d18c9de4a716d6b55ce802cb7b4c15f22265408b637a9b17bb31e30e89941` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-007-001 — Audit events are complete

Source persona: Executive Director. Proposed fixture `FIX-FR-SEC-007-001` is not created. Verification duty `TASK-FR-SEC-007-03` (qualification); source `docs/backlog/backlog.csv` record 153, exact block `bafb7de439420c18ca182266bc899710a1ff68d1751c0b1f6979c67499358c42`.

**Original preconditions**

1. an action covered by the event catalogue, including privileged reads and decisions

**Original actions**

1. it occurs

**Exact source oracles — all required**

1. an audit event records real actor, delegated capacity, tenant, action, object version, outcome, time and correlation

Legacy same-requirement reuse candidates: `TC-SEC-007-01`, `TC-SEC-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-007-002 — Audit access is scoped

Source persona: Executive Director. Proposed fixture `FIX-FR-SEC-007-002` is not created. Verification duty `TASK-FR-SEC-007-03` (qualification); source `docs/backlog/backlog.csv` record 153, exact block `d7f954b97fa22c1ef57d3668560984303a4efd840906b0eebc11862eb43d0c69`.

**Original preconditions**

1. a user searching or exporting audit events

**Original actions**

1. they run the search or export

**Exact source oracles — all required**

1. results are restricted to their authorised audit scopes

Legacy same-requirement reuse candidates: `TC-SEC-007-01`, `TC-SEC-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-007-003 — Corrections are additional events

Source persona: Executive Director. Proposed fixture `FIX-FR-SEC-007-003` is not created. Verification duty `TASK-FR-SEC-007-03` (qualification); source `docs/backlog/backlog.csv` record 153, exact block `a3996a919cca62e6bf9567d3df6d9facd0f96b07a111b9f0c0f7ae36ddfbe7a3`.

**Original preconditions**

1. an audit event that needs correction

**Original actions**

1. it is corrected

**Exact source oracles — all required**

1. the correction is recorded as an additional event
2. the original event is unchanged

Legacy same-requirement reuse candidates: `TC-SEC-007-01`, `TC-SEC-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-007-004 — Reject editing past audit history

Source persona: Executive Director. Proposed fixture `FIX-FR-SEC-007-004` is not created. Verification duty `TASK-FR-SEC-007-03` (qualification); source `docs/backlog/backlog.csv` record 153, exact block `fc48451ad6b7b72d9f9cf00ccc70f663b4dea60232532905895aad1d0e78a08f`.

**Original preconditions**

1. an approval event

**Original actions**

1. an administrator attempts to change or erase it through ordinary administration

**Exact source oracles — all required**

1. the attempt fails
2. both the attempt and the original decision remain attributable

Legacy same-requirement reuse candidates: `TC-SEC-007-01`, `TC-SEC-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
