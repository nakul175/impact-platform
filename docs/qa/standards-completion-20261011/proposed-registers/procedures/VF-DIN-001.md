## QA v1.3 — source-bound case design (proposed)

Story `VF-DIN-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-DIN-001-001` / `TC-IMPRANA-VF-DIN-001-001` | `REV_4280215aacf9863452c45f274629347cd85b347f2857a3cb3f68d9e21d97ce83` / `REV_b3dfae66c959a1430dd3b7b6cc981a793a613aba173230f09ae3945d0da837eb` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DIN-001-002` / `TC-IMPRANA-VF-DIN-001-002` | `REV_c0a6244e14ba212d6488d8355dfaede3d3b25e4fa33ce036fab653cc2a523973` / `REV_36a44c245a806fa0109a1331ba872fc618d83f1c8ca0345fc923ff9951e82322` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DIN-001-003` / `TC-IMPRANA-VF-DIN-001-003` | `REV_6094f63d9c65d7a46075cbc0e1ffe96f0a72531e5efd63a239e89d24f7c022f5` / `REV_5d730d61da7d138457661b2f86e23bf393c772f8b97815ff5872f8eb3e54f80d` | unit → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-DIN-001-001 — Golden corpus passes exactly before release

Source persona: MEL Manager. Proposed fixture `FIX-VF-DIN-001-001` is not created. Verification duty `TASK-VF-DIN-001-03` (qualification); source `docs/backlog/backlog.csv` record 111, exact block `4280215aacf9863452c45f274629347cd85b347f2857a3cb3f68d9e21d97ce83`.

**Original preconditions**

1. the approved deterministic golden corpus CAL01 through CAL20 with version, correction, missingness and permission variants

**Original actions**

1. it is run against independently prepared expected results

**Exact source oracles — all required**

1. every case passes exactly at the defined precision
2. raw and displayed decimals and report bindings match

Legacy same-requirement reuse candidates: `TC-VF-DIN-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Calculation-method file presence is not all golden corpus gate assertions or refusal of release on a failure; inspect the actual independent oracle/gate evidence.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DIN-001-002 — Corpus covers the required calculation semantics

Source persona: MEL Manager. Proposed fixture `FIX-VF-DIN-001-002` is not created. Verification duty `TASK-VF-DIN-001-03` (qualification); source `docs/backlog/backlog.csv` record 111, exact block `c0a6244e14ba212d6488d8355dfaede3d3b25e4fa33ce036fab653cc2a523973`.

**Original preconditions**

1. the approved golden corpus

**Original actions**

1. its coverage is reviewed

**Exact source oracles — all required**

1. it covers pooled ratios, distinct counts, period semantics, dimensions, corrections, rounding, missingness, cycles and permissions

Legacy same-requirement reuse candidates: `TC-VF-DIN-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Calculation-method file presence is not all golden corpus gate assertions or refusal of release on a failure; inspect the actual independent oracle/gate evidence.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DIN-001-003 — Reject release with an unexplained discrepancy

Source persona: MEL Manager. Proposed fixture `FIX-VF-DIN-001-003` is not created. Verification duty `TASK-VF-DIN-001-03` (qualification); source `docs/backlog/backlog.csv` record 111, exact block `6094f63d9c65d7a46075cbc0e1ffe96f0a72531e5efd63a239e89d24f7c022f5`.

**Original preconditions**

1. an unexplained difference between an official result and its expected result

**Original actions**

1. the release gate is evaluated

**Exact source oracles — all required**

1. the release is blocked
2. a numerical tolerance is applied only where the approved calculation contract defines it

Legacy same-requirement reuse candidates: `TC-VF-DIN-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Calculation-method file presence is not all golden corpus gate assertions or refusal of release on a failure; inspect the actual independent oracle/gate evidence.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
