## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-006-001` / `TC-IMPRANA-FR-OPS-006-001` | `REV_b9d93dba696143143eb1179bc6aefd02026e840052248cba27ece700265cdb76` / `REV_a3c1ba77740502f6f06c74bb25ad9913f58662e1af0083b7c60d9c77acb7707f` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-006-002` / `TC-IMPRANA-FR-OPS-006-002` | `REV_ccdb0deafebdb8b02979d5212bbaa275a4caa24cdba2798db6e1317ee2f3654d` / `REV_3ebc6d9c4ea3819047802ca8e15e87395696d867a5d59364718682319a955455` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-006-003` / `TC-IMPRANA-FR-OPS-006-003` | `REV_ad868fcfbd98b69ce7af15cac39826473aee3ace3d5b08975ce3cd7329d8a74a` / `REV_bdce33ab78973c65951cea6c5bb11569e5ce50647d797d87f6d4dd2e8fe563d8` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-006-004` / `TC-IMPRANA-FR-OPS-006-004` | `REV_343435607cf89a3640ba0b9a6060aecabd884c277ca4e05721da68f460c59dd6` / `REV_aff9510de4d49f35bc61f4ba57edaa68c3828e21d72f4da98620dcff2ae3b18e` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-006-001 — Recover a representative tenant

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-006-001` is not created. Verification duty `TASK-FR-OPS-006-03` (qualification); source `docs/backlog/backlog.csv` record 163, exact block `b9d93dba696143143eb1179bc6aefd02026e840052248cba27ece700265cdb76`.

**Original preconditions**

1. a representative tenant with a recovery inventory

**Original actions**

1. the Platform Operator recovers it

**Exact source oracles — all required**

1. structured records, attachment integrity, report snapshots and effective grants are compared
2. normal access is allowed only after the comparison passes

Legacy same-requirement reuse candidates: `TC-OPS-006-01`, `TC-OPS-006-02`, `TC-AT19`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-006-002 — Restore reapplies restrictions and reconciles writes

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-006-002` is not created. Verification duty `TASK-FR-OPS-006-03` (qualification); source `docs/backlog/backlog.csv` record 163, exact block `ccdb0deafebdb8b02979d5212bbaa275a4caa24cdba2798db6e1317ee2f3654d`.

**Original preconditions**

1. a restore from a validated mutually consistent checkpoint

**Original actions**

1. the restore runs

**Exact source oracles — all required**

1. current restrictions are reapplied
2. accepted writes are reconciled before controlled reopening

Legacy same-requirement reuse candidates: `TC-OPS-006-01`, `TC-OPS-006-02`, `TC-AT19`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-006-003 — Reject declaring an incomplete restore

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-006-003` is not created. Verification duty `TASK-FR-OPS-006-03` (qualification); source `docs/backlog/backlog.csv` record 163, exact block `ad868fcfbd98b69ce7af15cac39826473aee3ace3d5b08975ce3cd7329d8a74a`.

**Original preconditions**

1. a restore missing required evidence files or governance state

**Original actions**

1. the Platform Operator attempts to declare it complete

**Exact source oracles — all required**

1. the declaration is refused

Legacy same-requirement reuse candidates: `TC-OPS-006-01`, `TC-OPS-006-02`, `TC-AT19`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-006-004 — Reject recovery outside region or key policy

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-006-004` is not created. Verification duty `TASK-FR-OPS-006-03` (qualification); source `docs/backlog/backlog.csv` record 163, exact block `343435607cf89a3640ba0b9a6060aecabd884c277ca4e05721da68f460c59dd6`.

**Original preconditions**

1. the tenant's recovery region and key policy

**Original actions**

1. recovery targets a region or key outside that policy

**Exact source oracles — all required**

1. the recovery is blocked

Legacy same-requirement reuse candidates: `TC-OPS-006-01`, `TC-OPS-006-02`, `TC-AT19`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
