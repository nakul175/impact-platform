## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-006-001` / `TC-IMPRANA-FR-IND-006-001` | `REV_d4d4cbac572bdb33cdadc0480429cb6b92df8adb28fea59fb28b468b48e585f1` / `REV_bee489b3ddf78474629f58e7b89b4f450d39e8c42cff5e4b78698baa3e9f862d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-006-002` / `TC-IMPRANA-FR-IND-006-002` | `REV_127d41fa8262715f5a4d842c52f5581f97a80682c757472e0d34743ccbe29f0c` / `REV_2fc6797b5697ba83e8e9755a8c64d84a741eb3ef46aec69fb8535625d7b32b84` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-006-003` / `TC-IMPRANA-FR-IND-006-003` | `REV_20e561be4486b922030582061ebf4f86cb0d7c96acc167d8333a55ddbe3d850b` / `REV_02327c10f118014efc084c23cf34183603157f0aea253b2e920f757660e76cc0` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-006-004` / `TC-IMPRANA-FR-IND-006-004` | `REV_df48d90033576f389ce1899a6cdc10aae255a383c41f5a2034a4764e39ac68a6` / `REV_1d7f6e08720ebfd4cf803a9076476d0f922fe8caf90e2f91a295369def50766e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-006-001 — Define a dimension

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-006-001` is not created. Verification duty `TASK-FR-IND-006-03` (qualification); source `docs/backlog/backlog.csv` record 96, exact block `d4d4cbac572bdb33cdadc0480429cb6b92df8adb28fea59fb28b468b48e585f1`.

**Original preconditions**

1. a MEL Manager setting up a dimension

**Original actions**

1. they define codes, labels, applicability, exclusivity and exhaustiveness

**Exact source oracles — all required**

1. missing, unknown and declined are available as explicit codes where appropriate
2. submissions store the dimension version and codes

Legacy same-requirement reuse candidates: `TC-IND-006-01`, `TC-IND-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-006-002 — Multiselect categories keep unique totals

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-006-002` is not created. Verification duty `TASK-FR-IND-006-03` (qualification); source `docs/backlog/backlog.csv` record 96, exact block `127d41fa8262715f5a4d842c52f5581f97a80682c757472e0d34743ccbe29f0c`.

**Original preconditions**

1. one participant who selects two service types

**Original actions**

1. results are aggregated

**Exact source oracles — all required**

1. both categories count the event as defined
2. the unique participant total remains one
3. the category sum is labelled nonadditive

Legacy same-requirement reuse candidates: `TC-IND-006-01`, `TC-IND-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-006-003 — Changed scheme uses a crosswalk

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-006-003` is not created. Verification duty `TASK-FR-IND-006-03` (qualification); source `docs/backlog/backlog.csv` record 96, exact block `20e561be4486b922030582061ebf4f86cb0d7c96acc167d8333a55ddbe3d850b`.

**Original preconditions**

1. a category scheme that has changed

**Original actions**

1. data across scheme versions is aligned

**Exact source oracles — all required**

1. a reviewed crosswalk is used

Legacy same-requirement reuse candidates: `TC-IND-006-01`, `TC-IND-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-006-004 — Reject forcing overlapping categories to reconcile

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-006-004` is not created. Verification duty `TASK-FR-IND-006-03` (qualification); source `docs/backlog/backlog.csv` record 96, exact block `df48d90033576f389ce1899a6cdc10aae255a383c41f5a2034a4764e39ac68a6`.

**Original preconditions**

1. multiselect categories

**Original actions**

1. a view tries to reconcile the category sum to unique reach

**Exact source oracles — all required**

1. the reconciliation is refused

Legacy same-requirement reuse candidates: `TC-IND-006-01`, `TC-IND-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
