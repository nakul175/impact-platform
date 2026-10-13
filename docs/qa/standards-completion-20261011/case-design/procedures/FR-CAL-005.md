## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-005` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-005-001` / `TC-IMPRANA-FR-CAL-005-001` | `REV_b9f2104b367b1b38eea50ac56cd814772194585ecfb1f25206629fd4957ab644` / `REV_d9cce8a7f5ef7530f52df4662c3bc224861063cc98eaf308d5ddd0a03673fc1f` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-005-002` / `TC-IMPRANA-FR-CAL-005-002` | `REV_e5672d5be64cd741c1f754a658d67b93187c0a5bdec8fa7519e2371f54b8d00b` / `REV_40dd6065864ef806dc9b9d11da2a03e430caba5f3904bc9d9c75cc684a35525b` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-005-003` / `TC-IMPRANA-FR-CAL-005-003` | `REV_0ba83296e8f8bdcb0c4a7a59d21395c5b3530424ce12a1c387b6623deaa69500` / `REV_4699545d5b974151e32f3d129cd271092bfe784180b1f518dcfe9437fbc0fa9d` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-005-004` / `TC-IMPRANA-FR-CAL-005-004` | `REV_4703f92b67a3f5d92a54f4452ccf06eb7c1bf0528db84870504bf7f90b055370` / `REV_d98b9d0c3f776f8619e653850c45840d5bbb95e9844158db3bfac76a421bc269` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-005-005` / `TC-IMPRANA-FR-CAL-005-005` | `REV_3d6c2c480fc44e7d584fd12aef659c403a8d092a44982d5a2db1fa65f74ebc71` / `REV_0805e0cf4d8607e1c532720085c5f8c090e40c195173358a86908d92f25b3a69` | unit → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-005-001 — Aggregate by time semantic

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-005-001` is not created. Verification duty `TASK-FR-CAL-005-03` (qualification); source `docs/backlog/backlog.csv` record 57, exact block `b9f2104b367b1b38eea50ac56cd814772194585ecfb1f25206629fd4957ab644`.

**Original preconditions**

1. an indicator

**Original actions**

1. the Analyst selects flow sum, latest eligible stock, event count or approved cumulative difference

**Exact source oracles — all required**

1. aggregation follows that semantic
2. snapshots specify maximum permissible age and tie resolution

Legacy same-requirement reuse candidates: `TC-CAL-005-01`, `TC-CAL-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-005-002 — Cumulative positions

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-005-002` is not created. Verification duty `TASK-FR-CAL-005-03` (qualification); source `docs/backlog/backlog.csv` record 57, exact block `e5672d5be64cd741c1f754a658d67b93187c0a5bdec8fa7519e2371f54b8d00b`.

**Original preconditions**

1. cumulative positions of 10, 15 and 20

**Original actions**

1. they are aggregated

**Exact source oracles — all required**

1. the end value reported is 20
2. increments of 10, 5 and 5 are reported only when a zero starting baseline is established

Legacy same-requirement reuse candidates: `TC-CAL-005-01`, `TC-CAL-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-005-003 — Cumulative decline needs a correction or reset

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-005-003` is not created. Verification duty `TASK-FR-CAL-005-03` (qualification); source `docs/backlog/backlog.csv` record 57, exact block `0ba83296e8f8bdcb0c4a7a59d21395c5b3530424ce12a1c387b6623deaa69500`.

**Original preconditions**

1. a cumulative series that declines

**Original actions**

1. it is processed

**Exact source oracles — all required**

1. a correction or reset event with defined treatment is required

Legacy same-requirement reuse candidates: `TC-CAL-005-01`, `TC-CAL-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-005-004 — Reject summing cumulative totals

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-005-004` is not created. Verification duty `TASK-FR-CAL-005-03` (qualification); source `docs/backlog/backlog.csv` record 57, exact block `4703f92b67a3f5d92a54f4452ccf06eb7c1bf0528db84870504bf7f90b055370`.

**Original preconditions**

1. monthly cumulative totals

**Original actions**

1. they are aggregated by default

**Exact source oracles — all required**

1. they are not summed

Legacy same-requirement reuse candidates: `TC-CAL-005-01`, `TC-CAL-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-005-005 — Reject exact increments without a starting value

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-005-005` is not created. Verification duty `TASK-FR-CAL-005-03` (qualification); source `docs/backlog/backlog.csv` record 57, exact block `3d6c2c480fc44e7d584fd12aef659c403a8d092a44982d5a2db1fa65f74ebc71`.

**Original preconditions**

1. a missing starting cumulative value

**Original actions**

1. an exact period increment is requested

**Exact source oracles — all required**

1. it is not produced unless the approved method supplies a justified baseline

Legacy same-requirement reuse candidates: `TC-CAL-005-01`, `TC-CAL-005-02`, `TC-AT03`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
