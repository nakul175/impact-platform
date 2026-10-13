## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-005-001` / `TC-IMPRANA-FR-FRM-005-001` | `REV_ba57906f894ba8feff16cebd6e3e204b97bcefe7591d0ba8f9bb5e8649163b15` / `REV_058b7791b81bb78926c4a1a6f61c33c1091dbc35c7b63ca41a421c4e3a9c1620` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-005-002` / `TC-IMPRANA-FR-FRM-005-002` | `REV_a5e59e6c2d82680303b1973b65aa8a8272644432fe37cb2e03e5fc85a8d94ff5` / `REV_84b6cca798836dc63afddc7d244aa8a35c8f958d453d68e88ee48cb2093e3094` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-005-003` / `TC-IMPRANA-FR-FRM-005-003` | `REV_0ea2b299566ebd9f36f00183e237aecd421d87064db74430dffdfbc103e09124` / `REV_c7519c8e2d8a1cef2615ac3b949d95f657f71d9d6a4d7292839eee265761bf6a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-005-004` / `TC-IMPRANA-FR-FRM-005-004` | `REV_caa390dfd110418f3ecf41dbe6c80ae2824d54c2b9677d218b96301992a1bd6b` / `REV_b5629ab7985b2cffe987bf5c842a1c190784a4f4f618702ee806f2f02d170ccc` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-005-001 — Round creates one stable assignment per sampled unit and visit

Source persona: Programme Manager. Proposed fixture `FIX-FR-FRM-005-001` is not created. Verification duty `TASK-FR-FRM-005-03` (qualification); source `docs/backlog/backlog.csv` record 79, exact block `ba57906f894ba8feff16cebd6e3e204b97bcefe7591d0ba8f9bb5e8649163b15`.

**Original preconditions**

1. a round with an eligible frame, form version, dates and expected assignments

**Original actions**

1. tasks are created

**Exact source oracles — all required**

1. exactly one stable assignment exists per sampled unit and visit

Legacy same-requirement reuse candidates: `TC-FRM-005-01`, `TC-FRM-005-02`, `SEC-032`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-005-002 — Reassignment keeps history without extra completions

Source persona: Programme Manager. Proposed fixture `FIX-FR-FRM-005-002` is not created. Verification duty `TASK-FR-FRM-005-03` (qualification); source `docs/backlog/backlog.csv` record 79, exact block `a5e59e6c2d82680303b1973b65aa8a8272644432fe37cb2e03e5fc85a8d94ff5`.

**Original preconditions**

1. a household visit assigned to collector A

**Original actions**

1. it is reassigned to collector B and B submits

**Exact source oracles — all required**

1. the assignee change is recorded in history
2. the old assignment cannot produce an extra eligible completed visit

Legacy same-requirement reuse candidates: `TC-FRM-005-01`, `TC-FRM-005-02`, `SEC-032`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-005-003 — Sample replacement records original and substitute

Source persona: Programme Manager. Proposed fixture `FIX-FR-FRM-005-003` is not created. Verification duty `TASK-FR-FRM-005-03` (qualification); source `docs/backlog/backlog.csv` record 79, exact block `0ea2b299566ebd9f36f00183e237aecd421d87064db74430dffdfbc103e09124`.

**Original preconditions**

1. a sampled unit is replaced

**Original actions**

1. the replacement is recorded

**Exact source oracles — all required**

1. the original and substitute are recorded with a reason
2. the original nonresponse remains recorded

Legacy same-requirement reuse candidates: `TC-FRM-005-01`, `TC-FRM-005-02`, `SEC-032`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-005-004 — Reject silent expansion of the sample or denominator

Source persona: Programme Manager. Proposed fixture `FIX-FR-FRM-005-004` is not created. Verification duty `TASK-FR-FRM-005-03` (qualification); source `docs/backlog/backlog.csv` record 79, exact block `caa390dfd110418f3ecf41dbe6c80ae2824d54c2b9677d218b96301992a1bd6b`.

**Original preconditions**

1. an assigned sample for a round

**Original actions**

1. tasks are generated or a unit is replaced

**Exact source oracles — all required**

1. assignments are not automatically expanded to the full registry
2. the intended denominator does not increase silently

Legacy same-requirement reuse candidates: `TC-FRM-005-01`, `TC-FRM-005-02`, `SEC-032`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
