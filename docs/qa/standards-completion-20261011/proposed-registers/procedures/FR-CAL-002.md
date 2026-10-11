## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-002-001` / `TC-IMPRANA-FR-CAL-002-001` | `REV_735ca0ca3186c4cdfc6629f9fc708d6a951522d513384b3c287e5a40d6440a2d` / `REV_236fb91025fbae89d66e55bb6b884fcb8cd5a92d6a80b3cbd81e2f1c751c0ab7` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-002-002` / `TC-IMPRANA-FR-CAL-002-002` | `REV_eddf4fef3291e9d2743afbb0067472b56d39930f33efccc5527c9220deb4b2df` / `REV_4e72a014799304baf6ad8c59ca6f6bf71c62999f141c13072285b7004733894d` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-002-003` / `TC-IMPRANA-FR-CAL-002-003` | `REV_53ce4254d90ee6e969a9fcf2b2f1a00fec7519542378f75eb8afbcc97879edb3` / `REV_8bb21a48f8ed8bc1ba03f3bd5809bb05cdc8f38d283c10310f3df8aba428e70d` | unit → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-002-004` / `TC-IMPRANA-FR-CAL-002-004` | `REV_72602bc25cda1f4e502e6993644c1bb755aa0b434b6e68d6663cf9299bf1840b` / `REV_a5c6ec04de1929ff0d8a61109db53e809ede1641f07b6ea8e0c5fd26ec1694ef` | unit → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-002-001 — Type checking before execution

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-002-001` is not created. Verification duty `TASK-FR-CAL-002-03` (qualification); source `docs/backlog/backlog.csv` record 55, exact block `735ca0ca3186c4cdfc6629f9fc708d6a951522d513384b3c287e5a40d6440a2d`.

**Original preconditions**

1. a calculation ready to run

**Original actions**

1. execution starts

**Exact source oracles — all required**

1. measurement types, units, populations, period semantics, definitions and dimensions are compared first

Legacy same-requirement reuse candidates: `TC-CAL-002-01`, `TC-CAL-002-02`, `TC-AT08`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-002-002 — Combine with an approved conversion

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-002-002` is not created. Verification duty `TASK-FR-CAL-002-03` (qualification); source `docs/backlog/backlog.csv` record 55, exact block `eddf4fef3291e9d2743afbb0067472b56d39930f33efccc5527c9220deb4b2df`.

**Original preconditions**

1. values of 1 hectare and 1 acre and an approved conversion

**Original actions**

1. the Analyst combines them

**Exact source oracles — all required**

1. the conversion references an approved version, direction and precision
2. the preview shows original and converted inputs

Legacy same-requirement reuse candidates: `TC-CAL-002-01`, `TC-CAL-002-02`, `TC-AT08`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-002-003 — Reject people plus households

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-002-003` is not created. Verification duty `TASK-FR-CAL-002-03` (qualification); source `docs/backlog/backlog.csv` record 55, exact block `53ce4254d90ee6e969a9fcf2b2f1a00fec7519542378f75eb8afbcc97879edb3`.

**Original preconditions**

1. a people measure and a household measure with no justified conversion

**Original actions**

1. the Analyst combines them

**Exact source oracles — all required**

1. the total is rejected

Legacy same-requirement reuse candidates: `TC-CAL-002-01`, `TC-CAL-002-02`, `TC-AT08`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-002-004 — Reject compatibility from similar labels

Source persona: Analyst. Proposed fixture `FIX-FR-CAL-002-004` is not created. Verification duty `TASK-FR-CAL-002-03` (qualification); source `docs/backlog/backlog.csv` record 55, exact block `72602bc25cda1f4e502e6993644c1bb755aa0b434b6e68d6663cf9299bf1840b`.

**Original preconditions**

1. two measures with similar labels but no established compatibility

**Original actions**

1. they are combined

**Exact source oracles — all required**

1. the labels are not accepted as establishing compatibility

Legacy same-requirement reuse candidates: `TC-CAL-002-01`, `TC-CAL-002-02`, `TC-AT08`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
