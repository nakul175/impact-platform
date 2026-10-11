## QA v1.3 — source-bound case design (proposed)

Story `FR-UX-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-UX-005-001` / `TC-IMPRANA-FR-UX-005-001` | `REV_7fd343ff5cf946811761aa1da8085dee1f702f9de6881db5e0fa87ecda42462a` / `REV_e6c86ba8d9fd15735fae724c6bbcadc694fca13272aacff370b4954978a7ba4c` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-005-002` / `TC-IMPRANA-FR-UX-005-002` | `REV_1478698d07dcba7f6bb226f31649210667cf35cee77f1d6154ef4f062066af1f` / `REV_c31ab71ed350be6058fc34fcf14a98ed8fb337483c270b6b29e7d76272438cce` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-005-003` / `TC-IMPRANA-FR-UX-005-003` | `REV_5566ac8dbe05a3b213996846473e6b0c9918ecb04e6f2d8dde90830ac297f97c` / `REV_91bf27ea7357667d96ffd61eab43451f5f222af34e309c516a206a7ce7a0077b` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-005-004` / `TC-IMPRANA-FR-UX-005-004` | `REV_c3903cf835d07ac7ef35496379bad6b6f4e2a76b4fec1fdb861d2cc1e39b8d61` / `REV_0d4dda6f471865cf0b0721df945ec3f28cd929aa85c973627ca166b0468686f3` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-UX-005-001 — Complete core tasks on the supported mobile profile

Source persona: Field Data Collector. Proposed fixture `FIX-FR-UX-005-001` is not created. Verification duty `TASK-FR-UX-005-03` (qualification); source `docs/backlog/backlog.csv` record 172, exact block `7fd343ff5cf946811761aa1da8085dee1f702f9de6881db5e0fa87ecda42462a`.

**Original preconditions**

1. the supported mobile profile at 360 CSS pixel width

**Original actions**

1. a user completes a form, reviews evidence and returns a submission

**Exact source oracles — all required**

1. ordinary fields do not depend on horizontal scrolling

Legacy same-requirement reuse candidates: `TC-UX-005-01`, `TC-UX-005-02`, `TC-AT30`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-005-002 — Wide tables and dense configuration on mobile

Source persona: Field Data Collector. Proposed fixture `FIX-FR-UX-005-002` is not created. Verification duty `TASK-FR-UX-005-03` (qualification); source `docs/backlog/backlog.csv` record 172, exact block `1478698d07dcba7f6bb226f31649210667cf35cee77f1d6154ef4f062066af1f`.

**Original preconditions**

1. a wide analysis table and a dense configuration screen

**Original actions**

1. they are opened on mobile

**Exact source oracles — all required**

1. the table offers labelled scrolling or a simplified view without hiding critical meaning
2. the configuration screen declares its desktop requirement before editing begins

Legacy same-requirement reuse candidates: `TC-UX-005-01`, `TC-UX-005-02`, `TC-AT30`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-005-003 — Reject hover-only or clipped actions

Source persona: Field Data Collector. Proposed fixture `FIX-FR-UX-005-003` is not created. Verification duty `TASK-FR-UX-005-03` (qualification); source `docs/backlog/backlog.csv` record 172, exact block `5566ac8dbe05a3b213996846473e6b0c9918ecb04e6f2d8dde90830ac297f97c`.

**Original preconditions**

1. any core mobile screen

**Original actions**

1. it is used on the supported mobile profile

**Exact source oracles — all required**

1. no essential action is hover-only
2. no submit button is clipped

Legacy same-requirement reuse candidates: `TC-UX-005-01`, `TC-UX-005-02`, `TC-AT30`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-005-004 — Reject state loss on orientation change

Source persona: Field Data Collector. Proposed fixture `FIX-FR-UX-005-004` is not created. Verification duty `TASK-FR-UX-005-03` (qualification); source `docs/backlog/backlog.csv` record 172, exact block `c3903cf835d07ac7ef35496379bad6b6f4e2a76b4fec1fdb861d2cc1e39b8d61`.

**Original preconditions**

1. a draft in progress with a pending confirmation

**Original actions**

1. the device orientation changes

**Exact source oracles — all required**

1. the draft, focus context and confirmation state are preserved

Legacy same-requirement reuse candidates: `TC-UX-005-01`, `TC-UX-005-02`, `TC-AT30`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
