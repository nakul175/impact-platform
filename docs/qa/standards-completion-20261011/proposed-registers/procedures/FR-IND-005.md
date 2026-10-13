## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-005-001` / `TC-IMPRANA-FR-IND-005-001` | `REV_871b148424226a86f65e75f002cf025799f5ce24e453cd9849c8dab8c604d432` / `REV_81bf49cceed7e7b8c7a54baecd95542c3a90503889e9cdc8a80b58d57825daa8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-005-002` / `TC-IMPRANA-FR-IND-005-002` | `REV_47cba044ffd645cb343631018ec179f7d25abfbc19166c7beca88de826a4d052` / `REV_7837cfec1937440218e8f2196cfcef1d62f03270a2d7876959eee78eda4c4b8b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-005-003` / `TC-IMPRANA-FR-IND-005-003` | `REV_a07bb5ce79f719ac06ab640ccbb80a5b9c7fb8555e86c7789900927833a52d54` / `REV_b569decd6d03e225e4d1df005e79594a7b43ff2bff50c48adf5309861a1efe33` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-005-004` / `TC-IMPRANA-FR-IND-005-004` | `REV_13ddbe9ef4c924844880b1108cf2f909a11ecd3bb3dc40153fa6583cb07b501d` / `REV_f20ab3240d82f0787d06941590a3e2850c75610b55528496dc8918be9f264a5e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-005-001 — Boundary event belongs to the new quarter

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-005-001` is not created. Verification duty `TASK-FR-IND-005-03` (qualification); source `docs/backlog/backlog.csv` record 95, exact block `871b148424226a86f65e75f002cf025799f5ce24e453cd9849c8dab8c604d432`.

**Original preconditions**

1. quarters with inclusive start and exclusive end in the reporting zone

**Original actions**

1. an event occurs exactly at midnight on the new quarter boundary and is uploaded two days later

**Exact source oracles — all required**

1. it belongs only to the new quarter

Legacy same-requirement reuse candidates: `TC-IND-005-01`, `TC-IND-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-005-002 — Receipt time sets timeliness only

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-005-002` is not created. Verification duty `TASK-FR-IND-005-03` (qualification); source `docs/backlog/backlog.csv` record 95, exact block `47cba044ffd645cb343631018ec179f7d25abfbc19166c7beca88de826a4d052`.

**Original preconditions**

1. a measurement contract that does not use receipt time

**Original actions**

1. an observation is received late

**Exact source oracles — all required**

1. period membership follows the event date
2. the late entry is flagged

Legacy same-requirement reuse candidates: `TC-IND-005-01`, `TC-IND-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-005-003 — Late entry for a locked period

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-005-003` is not created. Verification duty `TASK-FR-IND-005-03` (qualification); source `docs/backlog/backlog.csv` record 95, exact block `a07bb5ce79f719ac06ab640ccbb80a5b9c7fb8555e86c7789900927833a52d54`.

**Original preconditions**

1. a locked period

**Original actions**

1. a late observation for that period arrives

**Exact source oracles — all required**

1. it is routed to restatement review

Legacy same-requirement reuse candidates: `TC-IND-005-01`, `TC-IND-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-005-004 — Reject summing overlapping windows as official periods

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-005-004` is not created. Verification duty `TASK-FR-IND-005-03` (qualification); source `docs/backlog/backlog.csv` record 95, exact block `13ddbe9ef4c924844880b1108cf2f909a11ecd3bb3dc40153fa6583cb07b501d`.

**Original preconditions**

1. overlapping analytical windows that reuse observations

**Original actions**

1. a user sums them as disjoint official periods

**Exact source oracles — all required**

1. the sum is refused

Legacy same-requirement reuse candidates: `TC-IND-005-01`, `TC-IND-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
