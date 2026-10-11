## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-010` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-010-001` / `TC-IMPRANA-FR-IND-010-001` | `REV_d06ea4b1bb834e5eb736d98efdffe716646f39d778817d765e781ca8d0f54d8a` / `REV_e6357e7f79955c6dbfa6f4d3f85fc8f638edd8da27d60c64fef171ac951a3d2b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-010-002` / `TC-IMPRANA-FR-IND-010-002` | `REV_b2c51748e4998c290565a363ef6ae523a17920c5806a29b16ea4e9e4f5f5de2c` / `REV_22ea66db9b09993b01ccc90d0949d9e7d92042c558dd86d9f5849ad38d4a45b1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-010-003` / `TC-IMPRANA-FR-IND-010-003` | `REV_8f3dff6bd4b550fe4dad03fa344d5f6fec1662896ff173b21274206f410fa97b` / `REV_567a80d35bcd994c4ed1be20d66e34c86c4e8a0f2c1dbe16695bcdaef3b8ca9c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-010-004` / `TC-IMPRANA-FR-IND-010-004` | `REV_d89edcbf21aa9589d1ad8fc4c4925d0c020633427c82c2a8cde8c0143a03687e` / `REV_115a26b12bb5431aad68229a8e51e76e18fab5a2daab2ab788cb02c38f0e17d1` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-010-001 — Change of actual mode requires approval

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-010-001` is not created. Verification duty `TASK-FR-IND-010-03` (qualification); source `docs/backlog/backlog.csv` record 99, exact block `d06ea4b1bb834e5eb736d98efdffe716646f39d778817d765e781ca8d0f54d8a`.

**Original preconditions**

1. an indicator whose actual mode is calculated

**Original actions**

1. a user changes it to entered

**Exact source oracles — all required**

1. a new approved measurement version or amendment is required

Legacy same-requirement reuse candidates: `TC-IND-010-01`, `TC-IND-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-010-002 — Override a computed value

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-010-002` is not created. Verification duty `TASK-FR-IND-010-03` (qualification); source `docs/backlog/backlog.csv` record 99, exact block `b2c51748e4998c290565a363ef6ae523a17920c5806a29b16ea4e9e4f5f5de2c`.

**Original preconditions**

1. a computed value of 94

**Original actions**

1. an override to 90 is proposed with period and reason and approved by an independent Reviewer

**Exact source oracles — all required**

1. the report records the override and explanation
2. retains the calculation of 94
3. views show both values with the official selection

Legacy same-requirement reuse candidates: `TC-IND-010-01`, `TC-IND-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-010-003 — Remove an override

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-010-003` is not created. Verification duty `TASK-FR-IND-010-03` (qualification); source `docs/backlog/backlog.csv` record 99, exact block `8f3dff6bd4b550fe4dad03fa344d5f6fec1662896ff173b21274206f410fa97b`.

**Original preconditions**

1. an approved override

**Original actions**

1. it is removed through another attributable decision

**Exact source oracles — all required**

1. the approved calculation is restored

Legacy same-requirement reuse candidates: `TC-IND-010-01`, `TC-IND-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-010-004 — Reject import or API overwrite of calculated results

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-010-004` is not created. Verification duty `TASK-FR-IND-010-03` (qualification); source `docs/backlog/backlog.csv` record 99, exact block `d89edcbf21aa9589d1ad8fc4c4925d0c020633427c82c2a8cde8c0143a03687e`.

**Original preconditions**

1. a calculated result field

**Original actions**

1. an import or API client sends a value for it

**Exact source oracles — all required**

1. the write is refused

Legacy same-requirement reuse candidates: `TC-IND-010-01`, `TC-IND-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
