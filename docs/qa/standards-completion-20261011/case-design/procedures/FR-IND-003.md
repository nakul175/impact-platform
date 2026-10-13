## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-003-001` / `TC-IMPRANA-FR-IND-003-001` | `REV_a8d25c6ef12cb0f7381a983dc04631d3a2f5fecdd6947218a13cb1c5ca76714a` / `REV_fd157f78858e802c6e45973f8d4c96f388d9b8286da468419da54614bbb69ec3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-003-002` / `TC-IMPRANA-FR-IND-003-002` | `REV_f79988f1d22eba683780e209539ad0e07d982fc6ae5056da2bc4f0c1777bff0d` / `REV_54affbbce3fbe2458bfb6bfda4ece8ad45ae97ff46464d209b57d1dcd2ee7484` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-003-003` / `TC-IMPRANA-FR-IND-003-003` | `REV_a7f3c7fe841d9aac5abbbaaf05630ce9d9b6013ad476e2d31ceef7cb80b344ce` / `REV_f85531a3d8721a9abb5d86bc3f579c96a0efc2ae2e5e80f12f48a8b5f9d475dd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-003-004` / `TC-IMPRANA-FR-IND-003-004` | `REV_607dcf87d4afa2d75f5a32ce9825b45953f1575d79847da134d6a6054426ac6b` / `REV_28dc000862891dd6a26352206619fcf8bcb88fe2bb29332370bf61da067e2901` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-003-001 — Record a baseline or target

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-003-001` is not created. Verification duty `TASK-FR-IND-003-03` (qualification); source `docs/backlog/backlog.csv` record 93, exact block `a8d25c6ef12cb0f7381a983dc04631d3a2f5fecdd6947218a13cb1c5ca76714a`.

**Original preconditions**

1. a MEL Manager defining a target

**Original actions**

1. they set measurement date or period, target kind, value, unit, direction and version
2. choose higher, lower, within range or milestone interpretation

**Exact source oracles — all required**

1. progress uses the declared formula
2. shows whether the original or revised target is selected

Legacy same-requirement reuse candidates: `TC-IND-003-01`, `TC-IND-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-003-002 — Overachievement against a higher target

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-003-002` is not created. Verification duty `TASK-FR-IND-003-03` (qualification); source `docs/backlog/backlog.csv` record 93, exact block `f79988f1d22eba683780e209539ad0e07d982fc6ae5056da2bc4f0c1777bff0d`.

**Original preconditions**

1. a higher target of 100

**Original actions**

1. the actual is 120

**Exact source oracles — all required**

1. attainment displays 120 percent
2. it is not capped

Legacy same-requirement reuse candidates: `TC-IND-003-01`, `TC-IND-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-003-003 — Lower target achieved

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-003-003` is not created. Verification duty `TASK-FR-IND-003-03` (qualification); source `docs/backlog/backlog.csv` record 93, exact block `a7f3c7fe841d9aac5abbbaaf05630ce9d9b6013ad476e2d31ceef7cb80b344ce`.

**Original preconditions**

1. a lower target of 10

**Original actions**

1. the actual is 8

**Exact source oracles — all required**

1. the result shows achieved and the defined deviation

Legacy same-requirement reuse candidates: `TC-IND-003-01`, `TC-IND-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-003-004 — Reject dividing by a zero target

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-003-004` is not created. Verification duty `TASK-FR-IND-003-03` (qualification); source `docs/backlog/backlog.csv` record 93, exact block `607dcf87d4afa2d75f5a32ce9825b45953f1575d79847da134d6a6054426ac6b`.

**Original preconditions**

1. a zero target

**Original actions**

1. progress is calculated

**Exact source oracles — all required**

1. milestone or reviewed difference logic is used rather than dividing by zero
2. an undefined target ratio displays as undefined

Legacy same-requirement reuse candidates: `TC-IND-003-01`, `TC-IND-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
