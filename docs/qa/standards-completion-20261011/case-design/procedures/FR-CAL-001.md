## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-001-001` / `TC-IMPRANA-FR-CAL-001-001` | `REV_72fa7e6448689a655f7800e7b9518f1bef577a3d1353b6a91b5e255f06782d20` / `REV_4b65cd8dcee30150a30ca41750048169feee8eb3d8f25a0ac733f8b30c29b745` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-001-002` / `TC-IMPRANA-FR-CAL-001-002` | `REV_abebe7399a37126636fc6278c05c50fcb05e8da6c9c45a465e66b37715745534` / `REV_d13c7f812f8793f42dbaca0b084cece4f06e1325ac6afcf66c0e19fd5fea790d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-001-003` / `TC-IMPRANA-FR-CAL-001-003` | `REV_6cb1f753bc873b723f7fc30d7b827ea1ce7f483be689795d262ef6f88762f672` / `REV_2bd215b87067639e8142a8b784db4334dff551b1834649a1043834e1f6795645` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-001-004` / `TC-IMPRANA-FR-CAL-001-004` | `REV_9fbe6edfb24f98638edf725431ae3ee8468fc6beccec9b3f2b8cd39972334188` / `REV_ec795213b6f009b9927b818bd509934c2c92f4a1c180a2b56769dc965a5faaa2` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-001-001 — Run a calculation

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-001-001` is not created. Verification duty `TASK-FR-CAL-001-03` (qualification); source `docs/backlog/backlog.csv` record 54, exact block `72fa7e6448689a655f7800e7b9518f1bef577a3d1353b6a91b5e255f06782d20`.

**Original preconditions**

1. approved rule and source versions

**Original actions**

1. a calculation run executes

**Exact source oracles — all required**

1. an input manifest is created and the deterministic dependency graph is evaluated
2. the result stores value state, precision, filters, coverage and execution identity
3. explanations resolve each contributing result to its original source

Legacy same-requirement reuse candidates: `TC-CAL-001-01`, `TC-CAL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-001-002 — Reproduce a frozen ratio

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-001-002` is not created. Verification duty `TASK-FR-CAL-001-03` (qualification); source `docs/backlog/backlog.csv` record 54, exact block `abebe7399a37126636fc6278c05c50fcb05e8da6c9c45a465e66b37715745534`.

**Original preconditions**

1. a frozen ratio with exported inputs and the recorded formula

**Original actions**

1. the Analyst recomputes it

**Exact source oracles — all required**

1. the raw decimal and displayed rounded output match exactly

Legacy same-requirement reuse candidates: `TC-CAL-001-01`, `TC-CAL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-001-003 — Reject AI-supplied values

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-001-003` is not created. Verification duty `TASK-FR-CAL-001-03` (qualification); source `docs/backlog/backlog.csv` record 54, exact block `6cb1f753bc873b723f7fc30d7b827ea1ce7f483be689795d262ef6f88762f672`.

**Original preconditions**

1. a calculation result

**Original actions**

1. an AI message proposes a value

**Exact source oracles — all required**

1. it is not used as the authoritative value

Legacy same-requirement reuse candidates: `TC-CAL-001-01`, `TC-CAL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-001-004 — Reject zero after a failed run

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-001-004` is not created. Verification duty `TASK-FR-CAL-001-03` (qualification); source `docs/backlog/backlog.csv` record 54, exact block `9fbe6edfb24f98638edf725431ae3ee8468fc6beccec9b3f2b8cd39972334188`.

**Original preconditions**

1. a prior calculation result

**Original actions**

1. a new run fails

**Exact source oracles — all required**

1. the prior result is labelled stale
2. the failure is exposed
3. the result is not overwritten with zero

Legacy same-requirement reuse candidates: `TC-CAL-001-01`, `TC-CAL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
