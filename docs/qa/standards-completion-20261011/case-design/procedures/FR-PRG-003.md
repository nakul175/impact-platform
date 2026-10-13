## QA v1.3 — source-bound case design (proposed)

Story `FR-PRG-003` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRG-003-001` / `TC-IMPRANA-FR-PRG-003-001` | `REV_55306edf101ceba6811312687c9162b886551e79e500030b110e900663739a0f` / `REV_4ffa26f32081d2065d2b6827794bfc2d4999c7dce553e81ae41c3834259e69aa` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-003-002` / `TC-IMPRANA-FR-PRG-003-002` | `REV_20d1351da6d4c35946a87d8d5d223d5864ac876067538c79a426ba5e41856eed` / `REV_e690da10b78c4cfcc74a48d00d7c7a200c7cc1802e54e788364c8d086713b1b6` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-003-003` / `TC-IMPRANA-FR-PRG-003-003` | `REV_a2d6b53608036aa4d3a828916f828f50f11625b013232cadd2a815b4f78352a0` / `REV_ecbc97138bf1551c70c766f904905be392820d7f7ac49aa5175cff0904d3da90` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-003-004` / `TC-IMPRANA-FR-PRG-003-004` | `REV_7071b5fda5897770c79854544f80c4a04edb6243efcda8a1affffeee5ab61d66` / `REV_85c06005f7d7a2604d3aaf4fb169b0b7a7ccb476907a8147253e266d382872e3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-003-005` / `TC-IMPRANA-FR-PRG-003-005` | `REV_479d3bbcc2f91b87645f3ef402c7ad93b6386e6765207f39d3014fea009f0525` / `REV_9dabfb84e338380985743b5d584a368fc60b570faf85ca8dd6a0e7e81e6dc8e4` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRG-003-001 — View tasks in the viewer's zone

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-003-001` is not created. Verification duty `TASK-FR-PRG-003-03` (qualification); source `docs/backlog/backlog.csv` record 292, exact block `55306edf101ceba6811312687c9162b886551e79e500030b110e900663739a0f`.

**Original preconditions**

1. programme and reporting tasks with a governing deadline zone

**Original actions**

1. a Programme Manager opens the calendar

**Exact source oracles — all required**

1. tasks are shown in the viewer's zone
2. the governing deadline zone is available

Legacy same-requirement reuse candidates: `TC-PRG-003-01`, `TC-PRG-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-003-002 — Preview and apply a reschedule

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-003-002` is not created. Verification duty `TASK-FR-PRG-003-03` (qualification); source `docs/backlog/backlog.csv` record 292, exact block `20d1351da6d4c35946a87d8d5d223d5864ac876067538c79a426ba5e41856eed`.

**Original preconditions**

1. a programme with future tasks and a locked quarterly deadline

**Original actions**

1. the Programme Manager moves the programme end by one month

**Exact source oracles — all required**

1. the preview lists future tasks and affected recipients
2. only eligible future tasks shift
3. the locked quarterly deadline stays unchanged

Legacy same-requirement reuse candidates: `TC-PRG-003-01`, `TC-PRG-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-003-003 — Recurrence uses the working calendar

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-003-003` is not created. Verification duty `TASK-FR-PRG-003-03` (qualification); source `docs/backlog/backlog.csv` record 292, exact block `a2d6b53608036aa4d3a828916f828f50f11625b013232cadd2a815b4f78352a0`.

**Original preconditions**

1. a recurring obligation

**Original actions**

1. instances are generated across a daylight saving change

**Exact source oracles — all required**

1. stable obligation instances are created using the working calendar
2. each deadline resolves to one declared instant

Legacy same-requirement reuse candidates: `TC-PRG-003-01`, `TC-PRG-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-003-004 — Reject duplicate tasks

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-003-004` is not created. Verification duty `TASK-FR-PRG-003-03` (qualification); source `docs/backlog/backlog.csv` record 292, exact block `7071b5fda5897770c79854544f80c4a04edb6243efcda8a1affffeee5ab61d66`.

**Original preconditions**

1. an obligation instance that already exists

**Original actions**

1. recurrence generation runs again

**Exact source oracles — all required**

1. no duplicate task is created for that obligation identity

Legacy same-requirement reuse candidates: `TC-PRG-003-01`, `TC-PRG-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-003-005 — Reject changes to locked deadlines

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-003-005` is not created. Verification duty `TASK-FR-PRG-003-03` (qualification); source `docs/backlog/backlog.csv` record 292, exact block `479d3bbcc2f91b87645f3ef402c7ad93b6386e6765207f39d3014fea009f0525`.

**Original preconditions**

1. a locked period deadline

**Original actions**

1. a reschedule is applied

**Exact source oracles — all required**

1. the locked deadline remains unchanged in history

Legacy same-requirement reuse candidates: `TC-PRG-003-01`, `TC-PRG-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
