## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-004-001` / `TC-IMPRANA-FR-ANA-004-001` | `REV_ec2b41347460a43269408909249b743b6b6a68b9e85391461d1785b28fdf4668` / `REV_af7c358c137b293ae286631f352cba4ee645afc91c8af1645d5b8a23ab8758f5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-004-002` / `TC-IMPRANA-FR-ANA-004-002` | `REV_c57ae6caf3387e23259fcb9fef2a3f34c1bd7d174209c342164a07c52ca122ba` / `REV_7c72a38459143a3d79c302f1e7c0a8aa4f4a24f44a93d16fc2bd4aa2bc617f8e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-004-003` / `TC-IMPRANA-FR-ANA-004-003` | `REV_ec4a8fbbaa2b34e13770ff8e1b72adbfbea4d4c61289ffc93225233237744d60` / `REV_301a1db2a6deea13754e28759c49e9894a90f91429d351518d146111348ed37c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-004-004` / `TC-IMPRANA-FR-ANA-004-004` | `REV_261bc417b05f626e405b56a4121268584e5a7de92e34a015562a03e09913bc91` / `REV_b0d643f0475f5519018f4fd725af2a670c385a34e545e75052f31c3ad69bb594` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-004-001 — Widget shows approval state and freshness context

Source persona: Executive Director. Proposed fixture `FIX-FR-ANA-004-001` is not created. Verification duty `TASK-FR-ANA-004-03` (qualification); source `docs/backlog/backlog.csv` record 68, exact block `ec2b41347460a43269408909249b743b6b6a68b9e85391461d1785b28fdf4668`.

**Original preconditions**

1. a dashboard with result widgets

**Original actions**

1. the Executive Director views it

**Exact source oracles — all required**

1. each widget is labelled live approved, provisional or snapshot
2. its context shows last source success, approval cutoff, calculation time and coverage

Legacy same-requirement reuse candidates: `TC-ANA-004-01`, `TC-ANA-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-004-002 — Failed refresh remains stale in an export

Source persona: Executive Director. Proposed fixture `FIX-FR-ANA-004-002` is not created. Verification duty `TASK-FR-ANA-004-03` (qualification); source `docs/backlog/backlog.csv` record 68, exact block `c57ae6caf3387e23259fcb9fef2a3f34c1bd7d174209c342164a07c52ca122ba`.

**Original preconditions**

1. a source refresh has failed

**Original actions**

1. the dashboard is exported

**Exact source oracles — all required**

1. the exported result is marked stale with the last valid data time
2. the export embeds a concise version of the material context

Legacy same-requirement reuse candidates: `TC-ANA-004-01`, `TC-ANA-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-004-003 — Reject treating a successful fetch as fresh data

Source persona: Executive Director. Proposed fixture `FIX-FR-ANA-004-003` is not created. Verification duty `TASK-FR-ANA-004-03` (qualification); source `docs/backlog/backlog.csv` record 68, exact block `ec4a8fbbaa2b34e13770ff8e1b72adbfbea4d4c61289ffc93225233237744d60`.

**Original preconditions**

1. the source refresh has failed

**Original actions**

1. the dashboard fetch succeeds

**Exact source oracles — all required**

1. the source is not shown as fresh

Legacy same-requirement reuse candidates: `TC-ANA-004-01`, `TC-ANA-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-004-004 — Reject unlabelled provisional content

Source persona: Executive Director. Proposed fixture `FIX-FR-ANA-004-004` is not created. Verification duty `TASK-FR-ANA-004-03` (qualification); source `docs/backlog/backlog.csv` record 68, exact block `261bc417b05f626e405b56a4121268584e5a7de92e34a015562a03e09913bc91`.

**Original preconditions**

1. a dashboard where some widgets are approved and one is provisional

**Original actions**

1. it is viewed or exported

**Exact source oracles — all required**

1. the provisional widget remains labelled provisional

Legacy same-requirement reuse candidates: `TC-ANA-004-01`, `TC-ANA-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
