## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-002-001` / `TC-IMPRANA-FR-ANA-002-001` | `REV_3d317b72f48876e630aefefd8175b97e70b65f6204b45e2f836c681e2846c4be` / `REV_4f5dd31d0ea310d601c05f1527d3fe10cbd684d0034210336a6a9cc51880d176` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-002-002` / `TC-IMPRANA-FR-ANA-002-002` | `REV_4dadc928329672530b968f20905d5ac25a8783a7b6e04905536211949caabe51` / `REV_281c5add40acd5a01a1a6e3907e0d43bbb8627d42b35e02ee8ec7d93caf1a14b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-002-003` / `TC-IMPRANA-FR-ANA-002-003` | `REV_e108a43269e319aaecc3129f81db75c30f66b6457043761bbdbafcef507b9722` / `REV_8804e05f461cff6cf7d14b1f835e19e0bb26b5dd45a91af233ab572ddeae6b28` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-002-004` / `TC-IMPRANA-FR-ANA-002-004` | `REV_40013e66d92af070888f2acd2d9f4136c9cef4c416990d8948137e426e706f27` / `REV_7f5e05a6ac2c49b580f20fbe98c016479204d683d116a302641e29f053ae3514` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-002-001 — Filter by partner and drill to programme data

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-002-001` is not created. Verification duty `TASK-FR-ANA-002-03` (qualification); source `docs/backlog/backlog.csv` record 66, exact block `3d317b72f48876e630aefefd8175b97e70b65f6204b45e2f836c681e2846c4be`.

**Original preconditions**

1. a dashboard covering partner A and partner B

**Original actions**

1. the Analyst selects partner A and drills down to programme data

**Exact source oracles — all required**

1. the filter shows its current value
2. drill down follows only permitted hierarchy levels and approved disclosure slices
3. the restricted participant level remains unavailable

Legacy same-requirement reuse candidates: `TC-ANA-002-01`, `TC-ANA-002-02`, `TC-AT16`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-002-002 — Non-applicable filter is visibly identified

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-002-002` is not created. Verification duty `TASK-FR-ANA-002-03` (qualification); source `docs/backlog/backlog.csv` record 66, exact block `4dadc928329672530b968f20905d5ac25a8783a7b6e04905536211949caabe51`.

**Original preconditions**

1. a filter that is not applicable to a widget

**Original actions**

1. the filter is applied

**Exact source oracles — all required**

1. the widget is visibly identified as not affected by the filter

Legacy same-requirement reuse candidates: `TC-ANA-002-01`, `TC-ANA-002-02`, `TC-AT16`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-002-003 — Saved view handles a changed binding

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-002-003` is not created. Verification duty `TASK-FR-ANA-002-03` (qualification); source `docs/backlog/backlog.csv` record 66, exact block `e108a43269e319aaecc3129f81db75c30f66b6457043761bbdbafcef507b9722`.

**Original preconditions**

1. a saved view whose binding has changed

**Original actions**

1. the Analyst opens the saved view

**Exact source oracles — all required**

1. it uses its pinned definitions or displays a reviewed migration notice

Legacy same-requirement reuse candidates: `TC-ANA-002-01`, `TC-ANA-002-02`, `TC-AT16`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-002-004 — Reject leakage through filtering and totals

Source persona: Analyst. Proposed fixture `FIX-FR-ANA-002-004` is not created. Verification duty `TASK-FR-ANA-002-03` (qualification); source `docs/backlog/backlog.csv` record 66, exact block `40013e66d92af070888f2acd2d9f4136c9cef4c416990d8948137e426e706f27`.

**Original preconditions**

1. partner A is selected

**Original actions**

1. the summary totals are displayed

**Exact source oracles — all required**

1. they do not leak partner B data
2. no suppressed cells or hidden source counts are revealed

Legacy same-requirement reuse candidates: `TC-ANA-002-01`, `TC-ANA-002-02`, `TC-AT16`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_dashboards.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
