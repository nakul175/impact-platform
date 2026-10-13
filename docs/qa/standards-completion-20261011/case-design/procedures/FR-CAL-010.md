## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-010` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-010-001` / `TC-IMPRANA-FR-CAL-010-001` | `REV_b47063c4cc298a9abc1bc42926de3cd162d13be5ef4b64bc8edce9a8353bb6d3` / `REV_182f10844afa5a452bd5a8b9c6f6936bff36fa4a3a44b06cc2e658f14cb82f9f` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-010-002` / `TC-IMPRANA-FR-CAL-010-002` | `REV_bf5f5b5faca54ff10d8070a6c577425a26cdd3a3400b746167a3deaf091ee39f` / `REV_39de5c312de6a5580cf2f2c426747950045f3a33deca8614c2c77dfea9c6ba69` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-010-003` / `TC-IMPRANA-FR-CAL-010-003` | `REV_9cffa268de2186efbef00c5225116ba0ff78048fa379188e640ba06c2d8470b1` / `REV_26f7d1f84f5c387b0474e6121b250f8438909a3fe1eb039f3e534aea99d4b88d` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-010-004` / `TC-IMPRANA-FR-CAL-010-004` | `REV_3e5151c2b7c67a11f7f560acaf297f8b22d2d4eb33270627a509eb50f62dafcc` / `REV_b928f8cf24223d780a9b08649b48eeff085d330e9a3414ce8556057fb7de12be` | unit → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-010-001 — Zero denominator returns undefined with a reason

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-010-001` is not created. Verification duty `TASK-FR-CAL-010-03` (qualification); source `docs/backlog/backlog.csv` record 60, exact block `b47063c4cc298a9abc1bc42926de3cd162d13be5ef4b64bc8edce9a8353bb6d3`.

**Original preconditions**

1. a ratio indicator

**Original actions**

1. 5 is divided by 0

**Exact source oracles — all required**

1. the result is UNDEFINED with a stated reason
2. it is not displayed as a successful zero

Legacy same-requirement reuse candidates: `TC-CAL-010-01`, `TC-CAL-010-02`, `TC-AT09`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-010-002 — Negative adjustment through an approved measure

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-010-002` is not created. Verification duty `TASK-FR-CAL-010-03` (qualification); source `docs/backlog/backlog.csv` record 60, exact block `bf5f5b5faca54ff10d8070a6c577425a26cdd3a3400b746167a3deaf091ee39f`.

**Original preconditions**

1. an approved adjustment measure or correction contract

**Original actions**

1. a negative adjustment is submitted under it

**Exact source oracles — all required**

1. the adjustment is accepted for calculation

Legacy same-requirement reuse candidates: `TC-CAL-010-01`, `TC-CAL-010-02`, `TC-AT09`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-010-003 — Reject invalid inputs before calculation

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-010-003` is not created. Verification duty `TASK-FR-CAL-010-03` (qualification); source `docs/backlog/backlog.csv` record 60, exact block `9cffa268de2186efbef00c5225116ba0ff78048fa379188e640ba06c2d8470b1`.

**Original preconditions**

1. a submission of negative two participants

**Original actions**

1. validation runs before calculation

**Exact source oracles — all required**

1. the value is rejected as invalid and not displayed as a successful zero
2. nonfinite inputs, impossible dates and incompatible sign conventions are also rejected

Legacy same-requirement reuse candidates: `TC-CAL-010-01`, `TC-CAL-010-02`, `TC-AT09`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-010-004 — Reject negative counts and automatic clipping

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-010-004` is not created. Verification duty `TASK-FR-CAL-010-03` (qualification); source `docs/backlog/backlog.csv` record 60, exact block `3e5151c2b7c67a11f7f560acaf297f8b22d2d4eb33270627a509eb50f62dafcc`.

**Original preconditions**

1. a spreadsheet containing a refund-like negative value for an eligible count
2. no approved adjustment measure or correction contract applies

**Original actions**

1. the data is calculated

**Exact source oracles — all required**

1. the eligible count does not become negative
2. a percentage outside its bounds is not automatically clipped without explicit valid semantics

Legacy same-requirement reuse candidates: `TC-CAL-010-01`, `TC-CAL-010-02`, `TC-AT09`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
