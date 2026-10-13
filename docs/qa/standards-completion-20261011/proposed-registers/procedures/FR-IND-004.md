## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-004` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-004-001` / `TC-IMPRANA-FR-IND-004-001` | `REV_b7e90d3f7256244809fce41976490e2353814fabf84f418206e9be33d4cafa87` / `REV_482815538af894d626e0e4e3e4fd00c9f9fd0f786e6315db6bb7e8ed99c357ad` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-004-002` / `TC-IMPRANA-FR-IND-004-002` | `REV_b965fc64516768bcb4a84fe73b3ed90297326a3b03c7eebfb18c775053876df4` / `REV_ccfb377a4832b58bc8c500909fa6490fc430c8ac8f61b25d782b7d3cad0a5aac` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-004-003` / `TC-IMPRANA-FR-IND-004-003` | `REV_6a36845045ff6cd2e4b8c87e22e523076fecbc1d9921ee93e2d5eeaa491ad4c8` / `REV_628a6e4678f94c7df2091f7e3f266e07947fe0158e2cd86d55ccb5ad09e6487b` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-004-001 — Review a target amendment

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-004-001` is not created. Verification duty `TASK-FR-IND-004-03` (qualification); source `docs/backlog/backlog.csv` record 94, exact block `b7e90d3f7256244809fce41976490e2353814fabf84f418206e9be33d4cafa87`.

**Original preconditions**

1. a proposed target amendment with reason, effective date and affected periods

**Original actions**

1. a Reviewer opens it

**Exact source oracles — all required**

1. the review compares original, currently effective and proposed values
2. approval retains all earlier versions and identifies any explicit restatement request

Legacy same-requirement reuse candidates: `TC-IND-004-01`, `TC-IND-004-02`, `TC-AT05`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-004-002 — Amend a target after lock

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-004-002` is not created. Verification duty `TASK-FR-IND-004-03` (qualification); source `docs/backlog/backlog.csv` record 94, exact block `b965fc64516768bcb4a84fe73b3ed90297326a3b03c7eebfb18c775053876df4`.

**Original preconditions**

1. a quarter target of 1000 and a locked report for that quarter

**Original actions**

1. the target is changed to 800 and approved

**Exact source oracles — all required**

1. the original report remains against 1000
2. a restated comparison is distinctly labelled

Legacy same-requirement reuse candidates: `TC-IND-004-01`, `TC-IND-004-02`, `TC-AT05`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-004-003 — Reject retrospective changes to a frozen report

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-004-003` is not created. Verification duty `TASK-FR-IND-004-03` (qualification); source `docs/backlog/backlog.csv` record 94, exact block `6a36845045ff6cd2e4b8c87e22e523076fecbc1d9921ee93e2d5eeaa491ad4c8`.

**Original preconditions**

1. a target amendment effective after a locked quarter

**Original actions**

1. it is approved without a separately approved restatement

**Exact source oracles — all required**

1. it applies only prospectively
2. the frozen report is unchanged

Legacy same-requirement reuse candidates: `TC-IND-004-01`, `TC-IND-004-02`, `TC-AT05`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
