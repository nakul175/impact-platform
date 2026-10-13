## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-008` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-008-001` / `TC-IMPRANA-FR-IND-008-001` | `REV_c28833353a573c2e3e5cd7fef7595d0a545111ace85fd49411f585060bfd5bcd` / `REV_e8996ee741b84b362b3e0f7cde1551509e93eeb4e7a79b76f505fa7b0f6eecc1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-008-002` / `TC-IMPRANA-FR-IND-008-002` | `REV_9a65a4fec6e71dced09c29d9acfea1f8d73a72fc1d57b1a0376ec80a9eaac4a7` / `REV_46554e4d026ffca2831be6a9a0e99637d0cdcd97175a2474d6a5f25fdb81eec1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-008-003` / `TC-IMPRANA-FR-IND-008-003` | `REV_3866d0f76114965ccbd231328a7637a77da8484560c6e934e1c24f878aeea74d` / `REV_56a182fb8829f89e6e94b327285584d956a92bb6e38db59c6e24f6c79408cdfd` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-008-001 — Material edit creates a child version

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-008-001` is not created. Verification duty `TASK-FR-IND-008-03` (qualification); source `docs/backlog/backlog.csv` record 98, exact block `c28833353a573c2e3e5cd7fef7595d0a545111ace85fd49411f585060bfd5bcd`.

**Original preconditions**

1. an approved indicator definition

**Original actions**

1. the MEL Manager makes a material edit

**Exact source oracles — all required**

1. a child version is created
2. a comparison report identifies unit, population, source, method, dimensions and aggregation changes
3. the Reviewer marks comparability as compatible, transformed by approved rule or broken

Legacy same-requirement reuse candidates: `TC-IND-008-01`, `TC-IND-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-008-002 — Cosmetic label correction

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-008-002` is not created. Verification duty `TASK-FR-IND-008-03` (qualification); source `docs/backlog/backlog.csv` record 98, exact block `9a65a4fec6e71dced09c29d9acfea1f8d73a72fc1d57b1a0376ec80a9eaac4a7`.

**Original preconditions**

1. an indicator label with a cosmetic error

**Original actions**

1. it is corrected

**Exact source oracles — all required**

1. semantic identity may be retained
2. the change is audited

Legacy same-requirement reuse candidates: `TC-IND-008-01`, `TC-IND-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-008-003 — Reject combining broken versions

Source persona: MEL Manager. Proposed fixture `FIX-FR-IND-008-003` is not created. Verification duty `TASK-FR-IND-008-03` (qualification); source `docs/backlog/backlog.csv` record 98, exact block `3866d0f76114965ccbd231328a7637a77da8484560c6e934e1c24f878aeea74d`.

**Original preconditions**

1. a definition changed from households to people

**Original actions**

1. a user requests a combined total

**Exact source oracles — all required**

1. the combined total is blocked until a justified conversion or separate series is selected
2. no continuous trend line or portfolio pool spans the broken versions without explicit qualified treatment

Legacy same-requirement reuse candidates: `TC-IND-008-01`, `TC-IND-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
