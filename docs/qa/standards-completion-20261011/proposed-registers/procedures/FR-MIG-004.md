## QA v1.3 — source-bound case design (proposed)

Story `FR-MIG-004` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-MIG-004-001` / `TC-IMPRANA-FR-MIG-004-001` | `REV_7694d907987a16a8c898e96ca955e1fd42c3bda5a9e17abcc3cd0020597ed091` / `REV_b12844b1101efeaaca7c80715ee56ffaa3eb50896fb7712fcc3d18c3f0d89168` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-004-002` / `TC-IMPRANA-FR-MIG-004-002` | `REV_e04c141648f68cce92fe17d47c5e53f5365475ac4343f42437b602a03ad77486` / `REV_51961d0c4203686ab890a5d0f547b63ed7a049a615573846adabfe6318ed4aa1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-004-003` / `TC-IMPRANA-FR-MIG-004-003` | `REV_110c6b0056a907a5ce85d821b4d27e7926a2caaed9cb34c799a6a70133685348` / `REV_00a3769159f45f50a427b8a18b0432290d3e5650c8d78897fb20d38561a40b92` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-MIG-004-001 — Identify the nature of a migrated approval

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-004-001` is not created. Verification duty `TASK-FR-MIG-004-03` (qualification); source `docs/backlog/backlog.csv` record 255, exact block `7694d907987a16a8c898e96ca955e1fd42c3bda5a9e17abcc3cd0020597ed091`.

**Original preconditions**

1. a migrated report approval

**Original actions**

1. the Data Steward inspects it

**Exact source oracles — all required**

1. it is identified as a preserved source record, verified evidence or a new destination decision

Legacy same-requirement reuse candidates: `TC-MIG-004-01`, `TC-MIG-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-004-002 — Destination decisions carry real actors

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-004-002` is not created. Verification duty `TASK-FR-MIG-004-03` (qualification); source `docs/backlog/backlog.csv` record 255, exact block `e04c141648f68cce92fe17d47c5e53f5365475ac4343f42437b602a03ad77486`.

**Original preconditions**

1. a decision made in the destination after migration

**Original actions**

1. it is recorded

**Exact source oracles — all required**

1. it carries the real current actor and timestamp
2. unverified source decisions are labelled imported assertions

Legacy same-requirement reuse candidates: `TC-MIG-004-01`, `TC-MIG-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-004-003 — Reject fabricated history

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-004-003` is not created. Verification duty `TASK-FR-MIG-004-03` (qualification); source `docs/backlog/backlog.csv` record 255, exact block `110c6b0056a907a5ce85d821b4d27e7926a2caaed9cb34c799a6a70133685348`.

**Original preconditions**

1. source history with a missing approval

**Original actions**

1. it is migrated

**Exact source oracles — all required**

1. no approval is fabricated
2. migration time is not used as the original event date
3. the missing history is represented as unavailable

Legacy same-requirement reuse candidates: `TC-MIG-004-01`, `TC-MIG-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
