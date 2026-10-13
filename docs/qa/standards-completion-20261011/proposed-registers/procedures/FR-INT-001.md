## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-001-001` / `TC-IMPRANA-FR-INT-001-001` | `REV_c957f688930f19105171e7baffd68b7926cfbaba7a1d3cc9d6c1598214c1bc99` / `REV_105e5617263781ef867e51aab86293152d3070f99d08d3103ad5ba0ba02d2adf` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-001-002` / `TC-IMPRANA-FR-INT-001-002` | `REV_302b62290c8211699c03822552ab791b70f73137a045b5e5c94bc582fa7ca6d6` / `REV_862d74263a3cfe0530c792cb1bc5df28f9acf259a7962d111b875b3f7e8845e8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-001-003` / `TC-IMPRANA-FR-INT-001-003` | `REV_486f08dd0bee2367d65adf2a181103f0bc0571c1a0ebecb3a962e99a8c1efe07` / `REV_f51e345cc3c06877201b07aa0fdaa8a154c226cbb95570211d7c85af3c052cf6` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-001-001 — Qualify a connector

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-001-001` is not created. Verification duty `TASK-FR-INT-001-03` (qualification); source `docs/backlog/backlog.csv` record 101, exact block `c957f688930f19105171e7baffd68b7926cfbaba7a1d3cc9d6c1598214c1bc99`.

**Original preconditions**

1. a connector with a qualification profile naming supported objects, direction, upstream version, keys, pagination, updates, deletions, attachments, limits and authoritative fields

**Original actions**

1. create, update, delete, replay and attachment cases are exercised

**Exact source oracles — all required**

1. source and destination counts reconcile
2. every unsupported field is recorded in a qualification manifest
3. unsupported upstream capabilities are declared on the configuration screen

Legacy same-requirement reuse candidates: `TC-INT-001-01`, `TC-INT-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-001-002 — Reject activation without a passing fixture or approved mapping

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-001-002` is not created. Verification duty `TASK-FR-INT-001-03` (qualification); source `docs/backlog/backlog.csv` record 101, exact block `302b62290c8211699c03822552ab791b70f73137a045b5e5c94bc582fa7ca6d6`.

**Original preconditions**

1. a connector without a passing fixture or approved mapping for the selected scope

**Original actions**

1. the Data Steward attempts to activate it

**Exact source oracles — all required**

1. activation is refused

Legacy same-requirement reuse candidates: `TC-INT-001-01`, `TC-INT-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-001-003 — Reject destructive deletion propagation

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-001-003` is not created. Verification duty `TASK-FR-INT-001-03` (qualification); source `docs/backlog/backlog.csv` record 101, exact block `486f08dd0bee2367d65adf2a181103f0bc0571c1a0ebecb3a962e99a8c1efe07`.

**Original preconditions**

1. a record is deleted in the source system

**Original actions**

1. no reviewed deletion contract exists

**Exact source oracles — all required**

1. the deletion is not propagated as a destructive action

Legacy same-requirement reuse candidates: `TC-INT-001-01`, `TC-INT-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
