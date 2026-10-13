## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-009` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-009-001` / `TC-IMPRANA-FR-CAL-009-001` | `REV_8115f5927c5178d978de74a9dba2ca3e663486bfe774d68af1423a35eafea288` / `REV_15eb56aa7552d528dbc1fe52b4961bf68e1d717cd3f7e15da7a3fb41b9b1ff99` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-009-002` / `TC-IMPRANA-FR-CAL-009-002` | `REV_c8f9282f3dcc7cc007ebc7ad77655300caf93c1b989ecd68bcde3ce9f28a6f9d` / `REV_0b2817d04edc1d834c26caafc7427654c35373e2f22cd2d106727a0e779a88e1` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-009-003` / `TC-IMPRANA-FR-CAL-009-003` | `REV_beba7a52a10df4e17ff07f11d7ec92a18dbc761ac8f2fb72ef137e72b6093727` / `REV_5c1ac236bc7525d7d601631433f9d8f9f031703d18037120681a5e68648a071f` | unit → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-009-001 — Round only at the output boundary

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-009-001` is not created. Verification duty `TASK-FR-CAL-009-03` (qualification); source `docs/backlog/backlog.csv` record 59, exact block `8115f5927c5178d978de74a9dba2ca3e663486bfe774d68af1423a35eafea288`.

**Original preconditions**

1. a rule that rounds half up to two decimals at output
2. three input values of 0.335

**Original actions**

1. the values are summed

**Exact source oracles — all required**

1. the unrounded total is 1.005
2. the displayed result is 1.01
3. the rule documentation explains why summing the rounded components would give a different total

Legacy same-requirement reuse candidates: `TC-CAL-009-01`, `TC-CAL-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-009-002 — Export carries the raw decimal and display metadata

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-009-002` is not created. Verification duty `TASK-FR-CAL-009-03` (qualification); source `docs/backlog/backlog.csv` record 59, exact block `c8f9282f3dcc7cc007ebc7ad77655300caf93c1b989ecd68bcde3ce9f28a6f9d`.

**Original preconditions**

1. a rounded result

**Original actions**

1. it is exported

**Exact source oracles — all required**

1. the export contains the raw decimal string
2. display metadata where applicable

Legacy same-requirement reuse candidates: `TC-CAL-009-01`, `TC-CAL-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-009-003 — Reject rounded inputs and unsafe numeric conversion

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-009-003` is not created. Verification duty `TASK-FR-CAL-009-03` (qualification); source `docs/backlog/backlog.csv` record 59, exact block `beba7a52a10df4e17ff07f11d7ec92a18dbc761ac8f2fb72ef137e72b6093727`.

**Original preconditions**

1. a display-rounded value, a large identifier and a count beyond the qualified numeric range

**Original actions**

1. each is submitted to a calculation

**Exact source oracles — all required**

1. the display-rounded value is refused as a new source input
2. the large identifier is kept as text and never converted to a number
3. the out-of-range count produces an explicit limit error

Legacy same-requirement reuse candidates: `TC-CAL-009-01`, `TC-CAL-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
