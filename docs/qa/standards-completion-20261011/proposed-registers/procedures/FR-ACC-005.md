## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-005-001` / `TC-IMPRANA-FR-ACC-005-001` | `REV_c353e0443d0c40f2a15e283128d2b95cfa19eb9a69582b79cd6f433069c71190` / `REV_cd313714cbbd717d59832b3366dec34e3c16021bc6d1d397a6e4a4335680d9ca` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-005-002` / `TC-IMPRANA-FR-ACC-005-002` | `REV_1af8af0ee54b1ed8b9fd2829b010a5e37e3a7fbac51e2f0d8391c067971be2c4` / `REV_90ffb2ca96ac24d3fd0e5256b169dca9a57006baa1e63afb3f39c218d4cfc667` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-005-003` / `TC-IMPRANA-FR-ACC-005-003` | `REV_0470053278db04c7c413c5859683dda67808c95c7497beaf97d14997df33496d` / `REV_974011c5d37d48aff5fb0082d453fb6b833300e77a13e28909202270bbf3dade` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-005-004` / `TC-IMPRANA-FR-ACC-005-004` | `REV_b34ab9bf0ee317b8244acd38b5a6f304aa556b3b00cf61967ddb2a5562285b9f` / `REV_1ed6584140e6ef2981389fb7999c654dd67186daee9e852ae7da7ddab59f3480` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-005-001 — Recheck source restrictions on read

Source persona: Analyst. Proposed fixture `FIX-FR-ACC-005-001` is not created. Verification duty `TASK-FR-ACC-005-03` (qualification); source `docs/backlog/backlog.csv` record 23, exact block `c353e0443d0c40f2a15e283128d2b95cfa19eb9a69582b79cd6f433069c71190`.

**Original preconditions**

1. a private derivative records its source restriction dependencies

**Original actions**

1. a dashboard, search result, saved analysis or AI answer is read

**Exact source oracles — all required**

1. those dependencies are rechecked for the reader

Legacy same-requirement reuse candidates: `TC-ACC-005-01`, `TC-ACC-005-02`, `SEC-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-005-002 — Serve an approved public aggregate

Source persona: Analyst. Proposed fixture `FIX-FR-ACC-005-002` is not created. Verification duty `TASK-FR-ACC-005-03` (qualification); source `docs/backlog/backlog.csv` record 23, exact block `1af8af0ee54b1ed8b9fd2829b010a5e37e3a7fbac51e2f0d8391c067971be2c4`.

**Original preconditions**

1. an approved public aggregate

**Original actions**

1. it is viewed

**Exact source oracles — all required**

1. it is served from a separate disclosure artifact with fixed approved content
2. no private drill down is available

Legacy same-requirement reuse candidates: `TC-ACC-005-01`, `TC-ACC-005-02`, `SEC-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-005-003 — Reject leaking a restricted metric through a copy

Source persona: Analyst. Proposed fixture `FIX-FR-ACC-005-003` is not created. Verification duty `TASK-FR-ACC-005-03` (qualification); source `docs/backlog/backlog.csv` record 23, exact block `0470053278db04c7c413c5859683dda67808c95c7497beaf97d14997df33496d`.

**Original preconditions**

1. a restricted dashboard

**Original actions**

1. an Analyst copies it to a partner workspace

**Exact source oracles — all required**

1. a new governed object is created that preserves the restrictions
2. the restricted metric remains unavailable until a valid substitute or disclosure is approved

Legacy same-requirement reuse candidates: `TC-ACC-005-01`, `TC-ACC-005-02`, `SEC-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-005-004 — Reject treating mixed sources as public

Source persona: Analyst. Proposed fixture `FIX-FR-ACC-005-004` is not created. Verification duty `TASK-FR-ACC-005-03` (qualification); source `docs/backlog/backlog.csv` record 23, exact block `b34ab9bf0ee317b8244acd38b5a6f304aa556b3b00cf61967ddb2a5562285b9f`.

**Original preconditions**

1. a result combines one public and one restricted source

**Original actions**

1. its visibility is determined

**Exact source oracles — all required**

1. the result is not treated as public

Legacy same-requirement reuse candidates: `TC-ACC-005-01`, `TC-ACC-005-02`, `SEC-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_roles.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
