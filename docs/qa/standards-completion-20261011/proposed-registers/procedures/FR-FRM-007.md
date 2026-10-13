## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-007-001` / `TC-IMPRANA-FR-FRM-007-001` | `REV_ec5a208cb69c7c3d3d778297c3874118faac22f5d9b6738e1dce65eb683797a4` / `REV_06f4e36f383b77afc859116082aec57233a9f7da23e1128b5381af1674f95735` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-007-002` / `TC-IMPRANA-FR-FRM-007-002` | `REV_3f177e211e0fb9682a568e330e02c752818a8177820e34f2e55c689886555670` / `REV_720e2e884ecec02a50f46b3e1a8d5e1e20b013b65ce15e5c4042798f57c1327a` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-007-003` / `TC-IMPRANA-FR-FRM-007-003` | `REV_d2273ec11ac304c67cec6c661ae8eaf94fce2320db295ccb185e1ab58149867c` / `REV_831d13176c26dfe087d583afcff82871627096fbc5f661e396c211adc206bd64` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-007-004` / `TC-IMPRANA-FR-FRM-007-004` | `REV_0291fe421ab96dbca98d58d7c13019e8d55cedf2113309591f5c70b256dcd918` / `REV_bdeb230500b834eff024735ce86e6c6839be06dd6791a9ddf1a2039691ffd18d` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-007-001 — Capture shows necessity, consent and limits

Source persona: Privacy Officer. Proposed fixture `FIX-FR-FRM-007-001` is not created. Verification duty `TASK-FR-FRM-007-03` (qualification); source `docs/backlog/backlog.csv` record 234, exact block `ec5a208cb69c7c3d3d778297c3874118faac22f5d9b6738e1dce65eb683797a4`.

**Original preconditions**

1. a form field requiring media capture

**Original actions**

1. the collector starts recording

**Exact source oracles — all required**

1. necessity, consent and size limits are displayed before recording
2. each attachment shows upload progress, safety state and evidence requirement

Legacy same-requirement reuse candidates: `TC-FRM-007-01`, `TC-FRM-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-007-002 — Optional GPS refusal is recorded

Source persona: Privacy Officer. Proposed fixture `FIX-FR-FRM-007-002` is not created. Verification duty `TASK-FR-FRM-007-03` (qualification); source `docs/backlog/backlog.csv` record 234, exact block `3f177e211e0fb9682a568e330e02c752818a8177820e34f2e55c689886555670`.

**Original preconditions**

1. an optional GPS field

**Original actions**

1. location is unavailable or declined

**Exact source oracles — all required**

1. the field records unavailable or declined
2. mandatory justified GPS follows the explicit exception path

Legacy same-requirement reuse candidates: `TC-FRM-007-01`, `TC-FRM-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-007-003 — Reject disclosure of prohibited location metadata

Source persona: Privacy Officer. Proposed fixture `FIX-FR-FRM-007-003` is not created. Verification duty `TASK-FR-FRM-007-03` (qualification); source `docs/backlog/backlog.csv` record 234, exact block `d2273ec11ac304c67cec6c661ae8eaf94fce2320db295ccb185e1ab58149867c`.

**Original preconditions**

1. a photo with embedded coordinates and location disclosure is prohibited

**Original actions**

1. the photo is disclosed externally

**Exact source oracles — all required**

1. the external artifact contains no recoverable coordinate metadata
2. permitted source provenance is retained

Legacy same-requirement reuse candidates: `TC-FRM-007-01`, `TC-FRM-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-007-004 — Reject incomplete or unsafe files as evidence

Source persona: Privacy Officer. Proposed fixture `FIX-FR-FRM-007-004` is not created. Verification duty `TASK-FR-FRM-007-03` (qualification); source `docs/backlog/backlog.csv` record 234, exact block `0291fe421ab96dbca98d58d7c13019e8d55cedf2113309591f5c70b256dcd918`.

**Original preconditions**

1. an attachment whose scanning is incomplete or that is found unsafe

**Original actions**

1. evidence completeness or approval is assessed

**Exact source oracles — all required**

1. the evidence is not complete and approval is prevented

Legacy same-requirement reuse candidates: `TC-FRM-007-01`, `TC-FRM-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
