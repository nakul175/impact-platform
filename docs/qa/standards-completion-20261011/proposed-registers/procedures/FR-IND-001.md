## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-001-001` / `TC-IMPRANA-FR-IND-001-001` | `REV_43dbaf4800220051afff93a03b0c57d7a9bdb76b24d4ad455301c4f1be401db6` / `REV_1b65e3dfb1c12a43c0f28797f4ee9e7f0b934f39fcdea19c366a47c24873bace` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-001-002` / `TC-IMPRANA-FR-IND-001-002` | `REV_515c2914ec513ef28113a040fa0360fdbfc6ec812b8e0181e4e28500b1c8807c` / `REV_8e0356f4715d2a40891373af84889e12bda4f3cf7d2ba3755ab040e1af6971ee` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-001-003` / `TC-IMPRANA-FR-IND-001-003` | `REV_0cf0ffbaa7bfa8aecc503a0b3cade05954b430e7c1550f4bd5d7ee7f5dddac05` / `REV_9220c3485a1dca291d3b750ba1780ed3b25d6cda14fccfefeb55bee9239d2895` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-001-001 — Complete measurement contract shown for review

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-001-001` is not created. Verification duty `TASK-FR-IND-001-03` (qualification); source `docs/backlog/backlog.csv` record 91, exact block `43dbaf4800220051afff93a03b0c57d7a9bdb76b24d4ad455301c4f1be401db6`.

**Original preconditions**

1. a MEL Manager defining an indicator

**Original actions**

1. they provide code, name, type, unit, population, inclusion and exclusion rules, method, source mode, time semantic, frequency, owner and limitations
2. the numerator, denominator, multiplier, direction and aggregation rule required by the type

**Exact source oracles — all required**

1. review displays a complete measurement contract

Legacy same-requirement reuse candidates: `TC-IND-001-01`, `TC-IND-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-001-002 — Missing denominator blocks approval

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-001-002` is not created. Verification duty `TASK-FR-IND-001-03` (qualification); source `docs/backlog/backlog.csv` record 91, exact block `515c2914ec513ef28113a040fa0360fdbfc6ec812b8e0181e4e28500b1c8807c`.

**Original preconditions**

1. a percentage indicator with a numerator but no eligible denominator

**Original actions**

1. the MEL Manager validates it

**Exact source oracles — all required**

1. validation links directly to the missing denominator meaning
2. approval remains unavailable

Legacy same-requirement reuse candidates: `TC-IND-001-01`, `TC-IND-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-001-003 — Reject a label-only or defaulted definition

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-001-003` is not created. Verification duty `TASK-FR-IND-001-03` (qualification); source `docs/backlog/backlog.csv` record 91, exact block `0cf0ffbaa7bfa8aecc503a0b3cade05954b430e7c1550f4bd5d7ee7f5dddac05`.

**Original preconditions**

1. an indicator with only a label, missing conditional fields, or an undefined population or unit

**Original actions**

1. it is submitted

**Exact source oracles — all required**

1. submission is blocked
2. no undocumented default is supplied for the population or unit

Legacy same-requirement reuse candidates: `TC-IND-001-01`, `TC-IND-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
