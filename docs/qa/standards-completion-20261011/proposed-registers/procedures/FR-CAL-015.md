## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-015` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-015-001` / `TC-IMPRANA-FR-CAL-015-001` | `REV_d0499fa7fa1472b37ed2698a8478f44b8dc08770365be9547a662a5e989fa429` / `REV_a139b5a951bd32413bd18161ae38c061c7283fe738916daa5b2b9aff0efccb1e` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-015-002` / `TC-IMPRANA-FR-CAL-015-002` | `REV_d12e80ff5b37ad1b6399e2cff9f325bb9255c2575aaff706d3a49924080915b2` / `REV_b6802e344baf13b7cb112ab061d5921743212fd0a6a0404af7e1db39bc06c8a1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-015-003` / `TC-IMPRANA-FR-CAL-015-003` | `REV_a02341c0b130bfb202eeaad8c8d24bbff5048ab2f91129bd24940816845cd060` / `REV_58aa62cdf3970433f2f210553f7844fb2176208ba7d71795531b7929f2459125` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-015-004` / `TC-IMPRANA-FR-CAL-015-004` | `REV_1434652af477e25bd88a25c2201978ea4caf3d87967fc917bc852d82c4d59e35` / `REV_6fedd06a6bdee3fb83c889926ece29bfa7437bb5b2e856141270449d4c1e0d71` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-015-001 — Explanation view shows how a result was produced

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-015-001` is not created. Verification duty `TASK-FR-CAL-015-03` (qualification); source `docs/backlog/backlog.csv` record 62, exact block `d0499fa7fa1472b37ed2698a8478f44b8dc08770365be9547a662a5e989fa429`.

**Original preconditions**

1. a calculated result

**Original actions**

1. the Analyst opens its explanation view

**Exact source oracles — all required**

1. it shows the rule version, source set, included and excluded counts, adjustments, coverage and approval

Legacy same-requirement reuse candidates: `TC-CAL-015-01`, `TC-CAL-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-015-002 — Run comparison separates the effect of each change

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-015-002` is not created. Verification duty `TASK-FR-CAL-015-03` (qualification); source `docs/backlog/backlog.csv` record 62, exact block `d12e80ff5b37ad1b6399e2cff9f325bb9255c2575aaff706d3a49924080915b2`.

**Original preconditions**

1. one source value and one filter have changed between two runs

**Original actions**

1. the runs are compared

**Exact source oracles — all required**

1. the effect of the source change and the effect of the filter change are identified and classified separately
2. no single unexplained total difference is reported

Legacy same-requirement reuse candidates: `TC-CAL-015-01`, `TC-CAL-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-015-003 — Reject inspection of restricted excluded records

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-015-003` is not created. Verification duty `TASK-FR-CAL-015-03` (qualification); source `docs/backlog/backlog.csv` record 62, exact block `a02341c0b130bfb202eeaad8c8d24bbff5048ab2f91129bd24940816845cd060`.

**Original preconditions**

1. a viewer without access to some excluded records

**Original actions**

1. they use reconciliation

**Exact source oracles — all required**

1. only permitted aggregates or withheld references are shown
2. the restricted excluded records cannot be inspected

Legacy same-requirement reuse candidates: `TC-CAL-015-01`, `TC-CAL-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-015-004 — Reject report approval with unreconciled differences

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-015-004` is not created. Verification duty `TASK-FR-CAL-015-03` (qualification); source `docs/backlog/backlog.csv` record 62, exact block `1434652af477e25bd88a25c2201978ea4caf3d87967fc917bc852d82c4d59e35`.

**Original preconditions**

1. numerical differences that do not reconcile to stated causes

**Original actions**

1. report approval is requested

**Exact source oracles — all required**

1. approval is blocked

Legacy same-requirement reuse candidates: `TC-CAL-015-01`, `TC-CAL-015-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
