## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-003` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-003-001` / `TC-IMPRANA-FR-FRM-003-001` | `REV_b2f359ffd9e544ef38d60131117d775613dcff699a84d2feb43fecbaa6fd1f3a` / `REV_785d88112382192898ea46568c5da8d73f148c990df3173594e9e46ae886238c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-003-002` / `TC-IMPRANA-FR-FRM-003-002` | `REV_fabd1eb5eecddc566f40817515d3ea95744d14184dd07d9fb005b6e0fb548113` / `REV_f50e3ba33bfda7335182f62b8c502a02deb4755745086b4df7bfc85cd859e518` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-003-003` / `TC-IMPRANA-FR-FRM-003-003` | `REV_741a535a3daeca57819067dbe024c70c4db214cf2313603e93a33b8ee7d0c43d` / `REV_c67fec549ed433eaff71916b0dbcc97b3b15230735f8ddf67dbdcd8be9434824` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-003-001 — Older offline submission is quarantined after a mandatory change

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-003-001` is not created. Verification duty `TASK-FR-FRM-003-03` (qualification); source `docs/backlog/backlog.csv` record 78, exact block `b2f359ffd9e544ef38d60131117d775613dcff699a84d2feb43fecbaa6fd1f3a`.

**Original preconditions**

1. a form package is offline on an older version
2. a new version adding a mandatory question is published

**Original actions**

1. the device reconnects and submits

**Exact source oracles — all required**

1. the original submission is preserved with the exact form and translation version used at capture
2. it is quarantined for reviewed mapping rather than having the answer invented

Legacy same-requirement reuse candidates: `TC-FRM-003-01`, `TC-FRM-003-02`, `TC-AT22`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-003-002 — Additive optional change accepts older versions

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-003-002` is not created. Verification duty `TASK-FR-FRM-003-03` (qualification); source `docs/backlog/backlog.csv` record 78, exact block `fabd1eb5eecddc566f40817515d3ea95744d14184dd07d9fb005b6e0fb548113`.

**Original preconditions**

1. a new version with only additive optional changes declared compatible with earlier versions

**Original actions**

1. a submission on an older version arrives before the acceptance cutoff

**Exact source oracles — all required**

1. it is accepted

Legacy same-requirement reuse candidates: `TC-FRM-003-01`, `TC-FRM-003-02`, `TC-AT22`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-003-003 — Reject a revoked unsafe form

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-003-003` is not created. Verification duty `TASK-FR-FRM-003-03` (qualification); source `docs/backlog/backlog.csv` record 78, exact block `741a535a3daeca57819067dbe024c70c4db214cf2313603e93a33b8ee7d0c43d`.

**Original preconditions**

1. a form version revoked as unsafe

**Original actions**

1. it is used for live collection

**Exact source oracles — all required**

1. it is rejected as a live collection instrument

Legacy same-requirement reuse candidates: `TC-FRM-003-01`, `TC-FRM-003-02`, `TC-AT22`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
