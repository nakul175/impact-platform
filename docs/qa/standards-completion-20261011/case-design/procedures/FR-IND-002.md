## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-002` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-002-001` / `TC-IMPRANA-FR-IND-002-001` | `REV_cad77f978fb829cbd8a75767c371a625b1105754a629e25ff31141b9f8f06da4` / `REV_5327159929c5c7d2e5dd33045991cb355c4850f028dfdd4f95f857ec360d0047` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-002-002` / `TC-IMPRANA-FR-IND-002-002` | `REV_8895f0df71e38a0348ecf864f75e6869ad9d381bdc15e6f6ffdcf7e6ec01fedd` / `REV_6187b745549eb65859ef0a74cd945620ce567ab000b40ac532b0b42088b4bd43` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-002-003` / `TC-IMPRANA-FR-IND-002-003` | `REV_43acbdb795fef5ea4226b67f054b8d0ca2d17b5f5e5b83117876c70614c02064` / `REV_600541a4db9799b7cc5d8a9f6f151cc5f5d03d852f20ffe55769a85fff2ae657` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-002-004` / `TC-IMPRANA-FR-IND-002-004` | `REV_3d8ab21a3c7ee0ee6d78a20528da48f77686b40e191fbb766bcdb0e39760087d` / `REV_374490ef2c8cdc3fca2c0a76fe1be28e69b496fb24832bd324329771f3180e71` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-002-005` / `TC-IMPRANA-FR-IND-002-005` | `REV_c4abc2326f969f61d2c2cd865f5f395ae98c0ff87abcdfbfd85e0ac058222bb6` / `REV_dcd231dc7ab8915819dc6119921217dc0b6a4c643ce7cf29feb97990f5b6b2b6` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-002-001 — Measurement type constrains inputs

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-002-001` is not created. Verification duty `TASK-FR-IND-002-03` (qualification); source `docs/backlog/backlog.csv` record 92, exact block `cad77f978fb829cbd8a75767c371a625b1105754a629e25ff31141b9f8f06da4`.

**Original preconditions**

1. a MEL Manager who selects a measurement type

**Original actions**

1. values and operators are configured

**Exact source oracles — all required**

1. counts accept integral eligible quantities
2. percentages use compatible quantities and a multiplier of 100
3. rates declare their multiplier
4. ordinal labels retain ordered codes

Legacy same-requirement reuse candidates: `TC-IND-002-01`, `TC-IND-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-002-002 — Import a reviewed external score

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-002-002` is not created. Verification duty `TASK-FR-IND-002-03` (qualification); source `docs/backlog/backlog.csv` record 92, exact block `8895f0df71e38a0348ecf864f75e6869ad9d381bdc15e6f6ffdcf7e6ec01fedd`.

**Original preconditions**

1. a reviewed external composite score with external method metadata

**Original actions**

1. it is imported

**Exact source oracles — all required**

1. its stated calculation source is retained

Legacy same-requirement reuse candidates: `TC-IND-002-01`, `TC-IND-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-002-003 — Reject ordinal codes in an additive aggregate

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-002-003` is not created. Verification duty `TASK-FR-IND-002-03` (qualification); source `docs/backlog/backlog.csv` record 92, exact block `43acbdb795fef5ea4226b67f054b8d0ca2d17b5f5e5b83117876c70614c02064`.

**Original preconditions**

1. an ordinal indicator

**Original actions**

1. a user enters an ordinal code into an additive aggregate

**Exact source oracles — all required**

1. the incompatibility is shown
2. the ordinal labels are not summed

Legacy same-requirement reuse candidates: `TC-IND-002-01`, `TC-IND-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-002-004 — Reject out-of-range bounded percentages

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-002-004` is not created. Verification duty `TASK-FR-IND-002-03` (qualification); source `docs/backlog/backlog.csv` record 92, exact block `3d8ab21a3c7ee0ee6d78a20528da48f77686b40e191fbb766bcdb0e39760087d`.

**Original preconditions**

1. a bounded percentage without an approved alternative interpretation

**Original actions**

1. a value outside zero to 100 is entered

**Exact source oracles — all required**

1. the value is rejected

Legacy same-requirement reuse candidates: `TC-IND-002-01`, `TC-IND-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-002-005 — Reject composite scores without method metadata

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-002-005` is not created. Verification duty `TASK-FR-IND-002-03` (qualification); source `docs/backlog/backlog.csv` record 92, exact block `c4abc2326f969f61d2c2cd865f5f395ae98c0ff87abcdfbfd85e0ac058222bb6`.

**Original preconditions**

1. an imported composite score in R1 with no external method metadata

**Original actions**

1. it is imported

**Exact source oracles — all required**

1. the import is refused

Legacy same-requirement reuse candidates: `TC-IND-002-01`, `TC-IND-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
