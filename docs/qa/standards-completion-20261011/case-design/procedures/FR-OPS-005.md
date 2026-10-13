## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-005-001` / `TC-IMPRANA-FR-OPS-005-001` | `REV_5dd8a1e3ecab9dc605840701097f6aa3e69bd089b502f7d5d025351eae984b76` / `REV_e6d3f8d03690d165e409ffb027dd10ef74bebc3389d805cbc94ef023c17fc251` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-005-002` / `TC-IMPRANA-FR-OPS-005-002` | `REV_a70de07e466f5e457689c5a7587fb2243e58bbd3bfaf0f7d6e23f7e4fc1888b5` / `REV_273cb2ee3d1aea6c40318f9a5cd7b68014c74ef22873a1072c73cbbde7a8ada7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-005-003` / `TC-IMPRANA-FR-OPS-005-003` | `REV_3be95e694b3a9a42e1d61ea72f42e7cfba8929d895fc040af5115fe1f8c4ede6` / `REV_c863449100c94c3e2b39ebdd164f07d663e160bf4af21c3dc3e80b45592e02dd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-005-004` / `TC-IMPRANA-FR-OPS-005-004` | `REV_c7498740fef1a96bcb75ba5220d45e979174d58b220de63aa18d9e521867ef30` / `REV_3b85450271ffe273de0b31ad31cca878fcb9848b1a6fbbdfc1d06e71baff7cc1` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-005-001 — Connector fails while the core is healthy

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-005-001` is not created. Verification duty `TASK-FR-OPS-005-03` (qualification); source `docs/backlog/backlog.csv` record 162, exact block `5dd8a1e3ecab9dc605840701097f6aa3e69bd089b502f7d5d025351eae984b76`.

**Original preconditions**

1. the core service is healthy

**Original actions**

1. a connector fails

**Exact source oracles — all required**

1. the health view shows integration delay and stale results
2. programme operations are not declared unavailable

Legacy same-requirement reuse candidates: `TC-OPS-005-01`, `TC-OPS-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-005-002 — Incidents link function and owner

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-005-002` is not created. Verification duty `TASK-FR-OPS-005-03` (qualification); source `docs/backlog/backlog.csv` record 162, exact block `a70de07e466f5e457689c5a7587fb2243e58bbd3bfaf0f7d6e23f7e4fc1888b5`.

**Original preconditions**

1. an incident is raised

**Original actions**

1. it is recorded

**Exact source oracles — all required**

1. it links the affected function and owner
2. health is monitored by permitted tenant cohort

Legacy same-requirement reuse candidates: `TC-OPS-005-01`, `TC-OPS-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-005-003 — Reject misleading health status

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-005-003` is not created. Verification duty `TASK-FR-OPS-005-03` (qualification); source `docs/backlog/backlog.csv` record 162, exact block `3be95e694b3a9a42e1d61ea72f42e7cfba8929d895fc040af5115fe1f8c4ede6`.

**Original preconditions**

1. one model provider has failed

**Original actions**

1. health status is computed

**Exact source oracles — all required**

1. a core outage is not reported solely because of that failure
2. healthy data freshness is not reported solely because the web interface is responsive

Legacy same-requirement reuse candidates: `TC-OPS-005-01`, `TC-OPS-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-005-004 — Reject irrelevant incident details in tenant views

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-005-004` is not created. Verification duty `TASK-FR-OPS-005-03` (qualification); source `docs/backlog/backlog.csv` record 162, exact block `c7498740fef1a96bcb75ba5220d45e979174d58b220de63aa18d9e521867ef30`.

**Original preconditions**

1. an incident affecting another tenant

**Original actions**

1. an Organisation Administrator views their tenant's status

**Exact source oracles — all required**

1. only incident details relevant to their tenant are shown

Legacy same-requirement reuse candidates: `TC-OPS-005-01`, `TC-OPS-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
