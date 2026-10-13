## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-006-001` / `TC-IMPRANA-FR-FRM-006-001` | `REV_e76b07595d2bb424193a526427a5625be3be3cda5616a3f2d6c92ec3fb9af5cd` / `REV_c32b8bb55f4b575a6fe62fb2abb75856a64f6c444929a41e7b14807386fa4205` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-006-002` / `TC-IMPRANA-FR-FRM-006-002` | `REV_974e38cc167a7c90928bccef33049c39ca7feeaa67e12cfd2cc2c6740f0aceb5` / `REV_19a587ce631409ffb037e2c288f774d715921b065e2a7cb33f2c350eab1d8c3f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-006-003` / `TC-IMPRANA-FR-FRM-006-003` | `REV_deecfe07f772ec87784220ff085ad33f98f194d6ae97698549e694282525871c` / `REV_c991d32c4c6a0ba3a31ce636ba31a054ebb4cb33fc7ef0c23f367dc9a9bdc9de` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-006-004` / `TC-IMPRANA-FR-FRM-006-004` | `REV_202d229c292a0952c2dfb4b4c8f5aef06722b83189374038139da6fad7befc3f` / `REV_b4fcfedb7a2eb42de1a0c5bec0d6ead4e54ab877eca33637467bba3c8272a1f0` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-006-001 — Save and resume a draft

Source persona: Field Data Collector. Proposed fixture `FIX-FR-FRM-006-001` is not created. Verification duty `TASK-FR-FRM-006-03` (qualification); source `docs/backlog/backlog.csv` record 80, exact block `e76b07595d2bb424193a526427a5625be3be3cda5616a3f2d6c92ec3fb9af5cd`.

**Original preconditions**

1. a Field Data Collector has a form in progress

**Original actions**

1. they save a draft and later resume it

**Exact source oracles — all required**

1. they see whether the draft was saved locally or on the server
2. the same submission identity and form version are restored

Legacy same-requirement reuse candidates: `TC-FRM-006-01`, `TC-FRM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-006-002 — Interrupted final submit resolves to one submission

Source persona: Field Data Collector. Proposed fixture `FIX-FR-FRM-006-002` is not created. Verification duty `TASK-FR-FRM-006-03` (qualification); source `docs/backlog/backlog.csv` record 80, exact block `974e38cc167a7c90928bccef33049c39ca7feeaa67e12cfd2cc2c6740f0aceb5`.

**Original preconditions**

1. final submit is interrupted

**Original actions**

1. the collector reopens the form and retries

**Exact source oracles — all required**

1. the receipt resolves to one submission
2. the local draft remains until server acceptance is confirmed

Legacy same-requirement reuse candidates: `TC-FRM-006-01`, `TC-FRM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-006-003 — Returned work starts a linked correction

Source persona: Field Data Collector. Proposed fixture `FIX-FR-FRM-006-003` is not created. Verification duty `TASK-FR-FRM-006-03` (qualification); source `docs/backlog/backlog.csv` record 80, exact block `deecfe07f772ec87784220ff085ad33f98f194d6ae97698549e694282525871c`.

**Original preconditions**

1. a submitted form is returned for correction

**Original actions**

1. the collector opens it

**Exact source oracles — all required**

1. a linked correction revision is started

Legacy same-requirement reuse candidates: `TC-FRM-006-01`, `TC-FRM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-006-004 — Reject duplicate submissions and silent loss

Source persona: Field Data Collector. Proposed fixture `FIX-FR-FRM-006-004` is not created. Verification duty `TASK-FR-FRM-006-03` (qualification); source `docs/backlog/backlog.csv` record 80, exact block `202d229c292a0952c2dfb4b4c8f5aef06722b83189374038139da6fad7befc3f`.

**Original preconditions**

1. the collector taps submit repeatedly or the server times out

**Original actions**

1. the submission is processed

**Exact source oracles — all required**

1. repeated taps reuse the same operation identity
2. a timeout enters confirmation pending rather than creating a new submission
3. closing the browser with unsaved changes shows a warning

Legacy same-requirement reuse candidates: `TC-FRM-006-01`, `TC-FRM-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
