## QA v1.3 — source-bound case design (proposed)

Story `VF-MNT-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-MNT-001-001` / `TC-IMPRANA-VF-MNT-001-001` | `REV_82b1b2757b5ec3a60b0b1a73e53764d677c3c1c1686413b0bebc8db794b68657` / `REV_225890184d0ef0580f0e2db401662a016e21c1bc6d0618f757fbec622bb228a8` | regression → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-MNT-001-002` / `TC-IMPRANA-VF-MNT-001-002` | `REV_c538e942829313356ab762b00c9d22c40df25d31ea44795f43d764592cab3319` / `REV_16476adff2e086378d81432b3f9fb56dce0ede7d466c8ec94d8a04ff7b4e384c` | regression → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-MNT-001-003` / `TC-IMPRANA-VF-MNT-001-003` | `REV_5b9c7deb33b658e40a8a80fcb92728b7a4d72f88f45b878e067a22a2820554eb` / `REV_87c5eea278cf564b3b470faff6ef91f7cc189539558474f665c64824b22b89be` | regression → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-MNT-001-001 — Different programmes are configured through supported settings

Source persona: Product Owner. Proposed fixture `FIX-VF-MNT-001-001` is not created. Verification duty `TASK-VF-MNT-001-03` (qualification); source `docs/backlog/backlog.csv` record 265, exact block `82b1b2757b5ec3a60b0b1a73e53764d677c3c1c1686413b0bebc8db794b68657`.

**Original preconditions**

1. two different programme templates

**Original actions**

1. they are configured

**Exact source oracles — all required**

1. ordinary supported settings are sufficient without a customer-specific code fork

Legacy same-requirement reuse candidates: `TC-VF-MNT-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-MNT-001-002 — Rule changes are traceable to requirements and tests

Source persona: Product Owner. Proposed fixture `FIX-VF-MNT-001-002` is not created. Verification duty `TASK-VF-MNT-001-03` (qualification); source `docs/backlog/backlog.csv` record 265, exact block `c538e942829313356ab762b00c9d22c40df25d31ea44795f43d764592cab3319`.

**Original preconditions**

1. a material rule amendment

**Original actions**

1. it is traced

**Exact source oracles — all required**

1. it links through requirements, the data dictionary, the interface contract and regression evidence
2. each of these is documented and version controlled

Legacy same-requirement reuse candidates: `TC-VF-MNT-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-MNT-001-003 — Reject code forks and unmanaged breaking changes

Source persona: Product Owner. Proposed fixture `FIX-VF-MNT-001-003` is not created. Verification duty `TASK-VF-MNT-001-03` (qualification); source `docs/backlog/backlog.csv` record 265, exact block `5b9c7deb33b658e40a8a80fcb92728b7a4d72f88f45b878e067a22a2820554eb`.

**Original preconditions**

1. a routine tenant configuration need

**Original actions**

1. it can only be met by a customer-specific code fork

**Exact source oracles — all required**

1. the requirement is not satisfied
2. a breaking change that bypasses the published compatibility process is rejected

Legacy same-requirement reuse candidates: `TC-VF-MNT-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
