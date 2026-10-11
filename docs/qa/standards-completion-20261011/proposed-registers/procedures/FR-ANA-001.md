## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-001-001` / `TC-IMPRANA-FR-ANA-001-001` | `REV_58459147b3a1cb9d75a48c570ed8836c63516069462ce49cbab44c8e8588a052` / `REV_f03cbe79241b75a9f6b4b5509b42687b20e239de70a3660e8023af39b992ffc7` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-001-002` / `TC-IMPRANA-FR-ANA-001-002` | `REV_e96e8245d57222c3cbb97ba6181617d53b6892e9e55e66b54547efd4ddadc02f` / `REV_cb7e4105e16e88d1b5cc4020e14abd6bfd7252be99ecd0a769af7735d4766076` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-001-003` / `TC-IMPRANA-FR-ANA-001-003` | `REV_8961e856af61040c3dc413f03cc084cfbddcf8f23aa780ff4efd4d03f7ad7422` / `REV_a028339402555bfd82c17a3383229abe36b29a3840dd13aa85fc7ad795df9740` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-001-004` / `TC-IMPRANA-FR-ANA-001-004` | `REV_2929852b2432864e98d101f801c54b782f15e2fbbb10b6083d7a5b77dfeb2722` / `REV_c7f5b1c077c8c7665ac4abb8166b11a04af05be9b6f1656f0039fdd414c99c5b` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-001-001 — Build and preview a ten-widget dashboard at mobile width

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-001-001` is not created. Verification duty `TASK-FR-ANA-001-03` (qualification); source `docs/backlog/backlog.csv` record 209, exact block `58459147b3a1cb9d75a48c570ed8836c63516069462ce49cbab44c8e8588a052`.

**Original preconditions**

1. the Analyst has built a dashboard with ten permitted widgets, each declaring binding, view mode, period, dimensions and disclosure context

**Original actions**

1. the Analyst opens the preview at mobile width

**Exact source oracles — all required**

1. each chart has a readable labelled tabular equivalent
2. the tabular values are identical to the chart values

Legacy same-requirement reuse candidates: `TC-ANA-001-01`, `TC-ANA-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-001-002 — Dashboard copy starts as a private draft

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-001-002` is not created. Verification duty `TASK-FR-ANA-001-03` (qualification); source `docs/backlog/backlog.csv` record 209, exact block `e96e8245d57222c3cbb97ba6181617d53b6892e9e55e66b54547efd4ddadc02f`.

**Original preconditions**

1. an existing dashboard

**Original actions**

1. the Analyst copies it

**Exact source oracles — all required**

1. the copy begins as a private draft

Legacy same-requirement reuse candidates: `TC-ANA-001-01`, `TC-ANA-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-001-003 — Reject layout changes that hide quality context

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-001-003` is not created. Verification duty `TASK-FR-ANA-001-03` (qualification); source `docs/backlog/backlog.csv` record 209, exact block `8961e856af61040c3dc413f03cc084cfbddcf8f23aa780ff4efd4d03f7ad7422`.

**Original preconditions**

1. a widget with required quality context

**Original actions**

1. the Analyst changes the dashboard layout

**Exact source oracles — all required**

1. the required quality context cannot be hidden

Legacy same-requirement reuse candidates: `TC-ANA-001-01`, `TC-ANA-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-001-004 — Reject stale values for unavailable bindings

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-001-004` is not created. Verification duty `TASK-FR-ANA-001-03` (qualification); source `docs/backlog/backlog.csv` record 209, exact block `2929852b2432864e98d101f801c54b782f15e2fbbb10b6083d7a5b77dfeb2722`.

**Original preconditions**

1. a widget whose binding is unsupported or has been revoked

**Original actions**

1. the dashboard is viewed

**Exact source oracles — all required**

1. the widget shows unavailable
2. no stale private value is displayed

Legacy same-requirement reuse candidates: `TC-ANA-001-01`, `TC-ANA-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
