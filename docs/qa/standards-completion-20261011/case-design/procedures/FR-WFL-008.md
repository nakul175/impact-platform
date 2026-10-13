## QA v1.3 — source-bound case design (proposed)

Story `FR-WFL-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-WFL-008-001` / `TC-IMPRANA-FR-WFL-008-001` | `REV_d8d1e11c1425740e8e558f98c686b7e6d6a83cb080a37ca274bffdd8e6545067` / `REV_bfa24e2e6eb7aac181612d733fb1324409511e5d879c296a5290c742d731388d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-008-002` / `TC-IMPRANA-FR-WFL-008-002` | `REV_4da18bad51304322f0608c71883f38e3fd44cd0d680757e8f8cf62416e21a117` / `REV_83868582d2241994f19d76ea547ce9cc8eae9ff83911caf8ccbb264657dd4d3d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-008-003` / `TC-IMPRANA-FR-WFL-008-003` | `REV_5b55b8cbe2573e373f4233518900e45db02453787e503fedc1c5e7be088b4ac6` / `REV_0ef41d85eb1ebc3cf4a1a599ed520acbde8402851e1b124a41264bf4ef13f958` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-008-004` / `TC-IMPRANA-FR-WFL-008-004` | `REV_398f8f10b0c95bbe2ca8c2116bf9d4760537b0128fa5e6f4cf101542dfddbf32` / `REV_a12532d81a11f232f40efac85e89767537ac261aae897c41e828494dba1bbfcf` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-WFL-008-001 — Restate Q1 and regenerate year-to-date

Source persona: MEL Manager. Proposed fixture `FIX-FR-WFL-008-001` is not created. Verification duty `TASK-FR-WFL-008-03` (qualification); source `docs/backlog/backlog.csv` record 180, exact block `d8d1e11c1425740e8e558f98c686b7e6d6a83cb080a37ca274bffdd8e6545067`.

**Original preconditions**

1. Q1 has a locked snapshot and a distributed report

**Original actions**

1. the MEL Manager starts a restatement from the Q1 snapshot with a correction reason, changed sources, affected totals and previously distributed artifacts
2. a Reviewer compares the old and proposed new snapshots and approves

**Exact source oracles — all required**

1. a new locked Q1 version is created
2. correction notices are created for eligible recipients
3. the old Q1 remains available marked as superseded

**Separate existing supplemental plan oracle (unapproved)**

1. a Reviewer compares the old and proposed new snapshots and approves

Legacy same-requirement reuse candidates: `TC-WFL-008-01`, `TC-WFL-008-02`, `TC-AT05`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-008-002 — Annual package points to the new approved version

Source persona: MEL Manager. Proposed fixture `FIX-FR-WFL-008-002` is not created. Verification duty `TASK-FR-WFL-008-03` (qualification); source `docs/backlog/backlog.csv` record 180, exact block `4da18bad51304322f0608c71883f38e3fd44cd0d680757e8f8cf62416e21a117`.

**Original preconditions**

1. Q1 has been restated and the new version approved

**Original actions**

1. year-to-date and annual totals are regenerated

**Exact source oracles — all required**

1. the annual package points to the new approved Q1 version
2. the annual totals identify which Q1 version they use

Legacy same-requirement reuse candidates: `TC-WFL-008-01`, `TC-WFL-008-02`, `TC-AT05`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-008-003 — Reject overwriting the original snapshot or report

Source persona: MEL Manager. Proposed fixture `FIX-FR-WFL-008-003` is not created. Verification duty `TASK-FR-WFL-008-03` (qualification); source `docs/backlog/backlog.csv` record 180, exact block `5b55b8cbe2573e373f4233518900e45db02453787e503fedc1c5e7be088b4ac6`.

**Original preconditions**

1. a restatement of Q1 has been approved

**Original actions**

1. the original Q1 snapshot and report are accessed

**Exact source oracles — all required**

1. they are unchanged
2. they are marked as superseded

Legacy same-requirement reuse candidates: `TC-WFL-008-01`, `TC-WFL-008-02`, `TC-AT05`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-008-004 — Reject changes outside the reopened scope or time bound

Source persona: MEL Manager. Proposed fixture `FIX-FR-WFL-008-004` is not created. Verification duty `TASK-FR-WFL-008-03` (qualification); source `docs/backlog/backlog.csv` record 180, exact block `398f8f10b0c95bbe2ca8c2116bf9d4760537b0128fa5e6f4cf101542dfddbf32`.

**Original preconditions**

1. Q1 has been reopened for correction with a defined scope and time bound

**Original actions**

1. a user attempts a change outside that scope or after the time bound has passed

**Exact source oracles — all required**

1. the change is refused

Legacy same-requirement reuse candidates: `TC-WFL-008-01`, `TC-WFL-008-02`, `TC-AT05`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
