## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-001-001` / `TC-IMPRANA-FR-FRM-001-001` | `REV_078dade6384d4088b670aac00976b5cf8918b15e784306ea0fc82c9421802841` / `REV_370c98972c63badf798b622b88f0695a1df87d64a7ae701b90a8959387972ff8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-001-002` / `TC-IMPRANA-FR-FRM-001-002` | `REV_a642da558999484dd4a22d8ed3f65ac1f805c761d976cf8ac1b61313e77c4330` / `REV_207ae9a1e38a0c2bc65c2aa2c6e673b0ccf2d2fbc72f48ce5795d8c124580213` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-001-003` / `TC-IMPRANA-FR-FRM-001-003` | `REV_2af4761b50a99bc4300294ccf892afc9af9ed268aad8fe1b70e395fd69957b3f` / `REV_b529428dce07a83469d6650092e0aeaac095f2c1767d149204735af9225b0ef4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-001-004` / `TC-IMPRANA-FR-FRM-001-004` | `REV_84a4388b47615f57c177d9050ff59665d4088c5f15f4ee2c089691a05bbf51b9` / `REV_a112d5dd0fb76322381a6f90e8da00ce4c7183bc06c75049432045c477df8850` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-001-001 — Build a household form with a repeat group

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-001-001` is not created. Verification duty `TASK-FR-FRM-001-03` (qualification); source `docs/backlog/backlog.csv` record 76, exact block `078dade6384d4088b670aac00976b5cf8918b15e784306ea0fc82c9421802841`.

**Original preconditions**

1. a household form with a repeat group for members, an optional photo and a calculated age

**Original actions**

1. three members are entered and the form is submitted

**Exact source oracles — all required**

1. every child response retains its parent and its stable field code

Legacy same-requirement reuse candidates: `TC-FRM-001-01`, `TC-FRM-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-001-002 — Preview and submit for review

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-001-002` is not created. Verification duty `TASK-FR-FRM-001-03` (qualification); source `docs/backlog/backlog.csv` record 76, exact block `a642da558999484dd4a22d8ed3f65ac1f805c761d976cf8ac1b61313e77c4330`.

**Original preconditions**

1. a draft form

**Original actions**

1. the MEL Manager previews it on desktop and mobile and submits it for review

**Exact source oracles — all required**

1. the preview displays the effective form version
2. submission locks the schema and starts the approval workflow

Legacy same-requirement reuse candidates: `TC-FRM-001-01`, `TC-FRM-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-001-003 — Qualified form size is supported

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-001-003` is not created. Verification duty `TASK-FR-FRM-001-03` (qualification); source `docs/backlog/backlog.csv` record 76, exact block `2af4761b50a99bc4300294ccf892afc9af9ed268aad8fe1b70e395fd69957b3f`.

**Original preconditions**

1. a form with 200 questions and a repeat group

**Original actions**

1. a submission contains 100 repeat entries

**Exact source oracles — all required**

1. the form previews and the submission is accepted

Legacy same-requirement reuse candidates: `TC-FRM-001-01`, `TC-FRM-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-001-004 — Reject unsupported structures before publishing

Source persona: MEL Manager. Proposed fixture `FIX-FR-FRM-001-004` is not created. Verification duty `TASK-FR-FRM-001-03` (qualification); source `docs/backlog/backlog.csv` record 76, exact block `84a4388b47615f57c177d9050ff59665d4088c5f15f4ee2c089691a05bbf51b9`.

**Original preconditions**

1. a form whose groups are nested deeper than two levels or that uses another unsupported combination

**Original actions**

1. it is submitted for publishing

**Exact source oracles — all required**

1. it is rejected before publishing
2. a submission exceeding the declared repeat instance limit is refused

Legacy same-requirement reuse candidates: `TC-FRM-001-01`, `TC-FRM-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
