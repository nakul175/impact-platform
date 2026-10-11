## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-010` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-010-001` / `TC-IMPRANA-FR-DAT-010-001` | `REV_375fcdb0c9a7b554cabd6f4cd0e1779e09d4c8377d8ea0bd5014c34cc7aeb827` / `REV_619d0c3120bdb9d1b463dff77ab195fe257849805295b11b8d3f0e8ed6d67882` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-010-002` / `TC-IMPRANA-FR-DAT-010-002` | `REV_2d2a18588aa07da90084c33a176fb713a07be83760663aa7332e22b689111a4f` / `REV_84436f4cb2a88e382fd1e0b91c673a5be8f6c3fd83bb45c7393cdc6ee3caec5e` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-010-003` / `TC-IMPRANA-FR-DAT-010-003` | `REV_70b8e2ca6a7929b3248d22aeb2f796cdd619dd0ee1c286438692b5d3b727b83b` / `REV_472a0eef2db4b341a4ee7b431fb4f52f9cfb1ee354032ff24e94b67398040c39` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-010-001 — Source records schedule and freshness stages

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-010-001` is not created. Verification duty `TASK-FR-DAT-010-03` (qualification); source `docs/backlog/backlog.csv` record 217, exact block `375fcdb0c9a7b554cabd6f4cd0e1779e09d4c8377d8ea0bd5014c34cc7aeb827`.

**Original preconditions**

1. a scheduled source

**Original actions**

1. its health is viewed

**Exact source oracles — all required**

1. cadence, zone, next run, last received, last validated and last approved data times are shown
2. schedule changes preview the affected runs

Legacy same-requirement reuse candidates: `TC-DAT-010-01`, `TC-DAT-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-010-002 — Fetch succeeds but validation fails

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-010-002` is not created. Verification duty `TASK-FR-DAT-010-03` (qualification); source `docs/backlog/backlog.csv` record 217, exact block `2d2a18588aa07da90084c33a176fb713a07be83760663aa7332e22b689111a4f`.

**Original preconditions**

1. a refresh where the fetch succeeds and validation fails

**Original actions**

1. source health and dependent dashboards are viewed

**Exact source oracles — all required**

1. source health distinguishes the successful fetch from the failed validation
2. dependent dashboards do not show a fresh approved result

Legacy same-requirement reuse candidates: `TC-DAT-010-01`, `TC-DAT-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-010-003 — Reject clearing the last known result on failure

Source persona: Data Steward. Proposed fixture `FIX-FR-DAT-010-003` is not created. Verification duty `TASK-FR-DAT-010-03` (qualification); source `docs/backlog/backlog.csv` record 217, exact block `70b8e2ca6a7929b3248d22aeb2f796cdd619dd0ee1c286438692b5d3b727b83b`.

**Original preconditions**

1. a missed or failed refresh

**Original actions**

1. dependent results are viewed

**Exact source oracles — all required**

1. the last known result is not cleared
2. it is labelled stale with a link to the authorised failure owner
3. overlapping scheduled runs follow one declared checkpoint sequence

Legacy same-requirement reuse candidates: `TC-DAT-010-01`, `TC-DAT-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
