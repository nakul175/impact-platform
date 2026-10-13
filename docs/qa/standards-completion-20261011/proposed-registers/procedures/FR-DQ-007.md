## QA v1.3 — source-bound case design (proposed)

Story `FR-DQ-007` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DQ-007-001` / `TC-IMPRANA-FR-DQ-007-001` | `REV_29b9daf7995f1af5b5b7523b55da8e2feebff82e08a2b7a663fe7b390fd663a9` / `REV_6542f2ea5b0fe0cbbb1bde65310e7753f38e9607f7b770ac70c6d0e87c89d758` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-007-002` / `TC-IMPRANA-FR-DQ-007-002` | `REV_6a79ae98456cb7fc721b916b22536caafe5120b213ee4cd17cb4ec241b8ea778` / `REV_a1067620b82868ec7a97e1759d6c854c38eb6275861f15240e98cafad26c48a3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-007-003` / `TC-IMPRANA-FR-DQ-007-003` | `REV_9403af8e98eaed6ead49499fd05147c76f03639d130d2b27007d220b3ffa820b` / `REV_962ad8d4a71cf036e677a84e23803f5944a80b0cd1f448ec9f2add6b2da5e5d3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DQ-007-001 — Anomaly run records its context and suggests findings

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-007-001` is not created. Verification duty `TASK-FR-DQ-007-03` (qualification); source `docs/backlog/backlog.csv` record 330, exact block `29b9daf7995f1af5b5b7523b55da8e2feebff82e08a2b7a663fe7b390fd663a9`.

**Original preconditions**

1. eligible data for an anomaly run

**Original actions**

1. the anomaly run executes

**Exact source oracles — all required**

1. it records the method version, eligible data, comparison window and explanation
2. its findings enter a suggested state with severity and owner

Legacy same-requirement reuse candidates: `TC-DQ-007-01`, `TC-DQ-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-007-002 — Seasonal spike reviewed as expected

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-007-002` is not created. Verification duty `TASK-FR-DQ-007-03` (qualification); source `docs/backlog/backlog.csv` record 330, exact block `6a79ae98456cb7fc721b916b22536caafe5120b213ee4cd17cb4ec241b8ea778`.

**Original preconditions**

1. an anomaly run flags a seasonal spike

**Original actions**

1. a Data Steward reviews it as expected and dismisses it with a reason

**Exact source oracles — all required**

1. the underlying data is retained unchanged
2. the dismissed suggestion remains distinct from a confirmed quality defect
3. the false positive evidence is retained under the minimised policy to inform later evaluated model changes

Legacy same-requirement reuse candidates: `TC-DQ-007-01`, `TC-DQ-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-007-003 — Reject a flag that changes data or labels a person

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-007-003` is not created. Verification duty `TASK-FR-DQ-007-03` (qualification); source `docs/backlog/backlog.csv` record 330, exact block `9403af8e98eaed6ead49499fd05147c76f03639d130d2b27007d220b3ffa820b`.

**Original preconditions**

1. an anomaly finding has been raised

**Original actions**

1. it is suggested, confirmed, dismissed or deferred

**Exact source oracles — all required**

1. it never modifies the underlying data
2. it never labels a person as fraudulent

Legacy same-requirement reuse candidates: `TC-DQ-007-01`, `TC-DQ-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
