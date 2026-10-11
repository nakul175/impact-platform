## QA v1.3 — source-bound case design (proposed)

Story `FR-OFF-003` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OFF-003-001` / `TC-IMPRANA-FR-OFF-003-001` | `REV_571cae2aae0e68cd5a4019767e51976509376f0ec60ec5dd15838a549965d7bc` / `REV_0dfa46570bb06486ecc331365d72c302fd49ea08954ecb0b2bebb789182cce59` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-003-002` / `TC-IMPRANA-FR-OFF-003-002` | `REV_5a3c642b7020d09354ea128c6dc04ba0d3218c89aeaac2672fc3702255c43499` / `REV_b6ddc78e8e13384d337f0dd7af7f9d90ace25ed381699ebcea3fc37a0a8f836f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-003-003` / `TC-IMPRANA-FR-OFF-003-003` | `REV_286cf7170c8f30da449c231590a6857fb33e173bfcf956df60f1faa931d938a7` / `REV_c7e83b0117676a9f701e473cf2546f45f4a027793a5669383a13bf32bb26d3a4` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OFF-003-001 — Per-item sync outcomes

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-003-001` is not created. Verification duty `TASK-FR-OFF-003-03` (qualification); source `docs/backlog/backlog.csv` record 273, exact block `571cae2aae0e68cd5a4019767e51976509376f0ec60ec5dd15838a549965d7bc`.

**Original preconditions**

1. a batch of submissions with identity, base revision, form version, grant context and media manifest

**Original actions**

1. it is synchronised

**Exact source oracles — all required**

1. the server returns accepted, duplicate, conflict, quarantined or rejected for each item

Legacy same-requirement reuse candidates: `TC-OFF-003-01`, `TC-OFF-003-02`, `TC-AT21`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-003-002 — Interrupted batch resolves to one identity per submission

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-003-002` is not created. Verification duty `TASK-FR-OFF-003-03` (qualification); source `docs/backlog/backlog.csv` record 273, exact block `5a3c642b7020d09354ea128c6dc04ba0d3218c89aeaac2672fc3702255c43499`.

**Original preconditions**

1. the same batch is interrupted five times

**Original actions**

1. synchronisation completes

**Exact source oracles — all required**

1. each intended submission has one identity
2. media chunks resume independently
3. missing media remains visibly incomplete

Legacy same-requirement reuse candidates: `TC-OFF-003-01`, `TC-OFF-003-02`, `TC-AT21`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-003-003 — Reject duplicate server objects or premature completion

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-003-003` is not created. Verification duty `TASK-FR-OFF-003-03` (qualification); source `docs/backlog/backlog.csv` record 273, exact block `286cf7170c8f30da449c231590a6857fb33e173bfcf956df60f1faa931d938a7`.

**Original preconditions**

1. an identical submission is repeated after ordinary interactive operation receipts have expired

**Original actions**

1. it is synchronised

**Exact source oracles — all required**

1. it resolves to the same server object
2. the local receipt is retained until server reconciliation completes
3. the submission is not marked complete until required files and checks finish

Legacy same-requirement reuse candidates: `TC-OFF-003-01`, `TC-OFF-003-02`, `TC-AT21`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
