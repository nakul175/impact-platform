## QA v1.3 — source-bound case design (proposed)

Story `VF-CAP-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-CAP-001-001` / `TC-IMPRANA-VF-CAP-001-001` | `REV_68a0264a3f125dd4a70861ddd29fb589aa6b2e9356dc73259861fe5a2e893b87` / `REV_d4512823cbf8d63880d2308f64ed57f67db2b131d79ab963900b205dff1fad02` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-CAP-001-002` / `TC-IMPRANA-VF-CAP-001-002` | `REV_a60aa045682bd550a1fde7e786ba51caa30c0d7569461a033788444cbc8a36d4` / `REV_91f154b2a7eb64319c01e768795ddf00f8aa3dd88014e70aa595bae1777c60a5` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-CAP-001-003` / `TC-IMPRANA-VF-CAP-001-003` | `REV_8d7d7b9070e53faccec876c7f1a9702ce433ce8f7c2e3c222e4a7f6ce8dccdc9` / `REV_15abf9630eb4ec5c3e565725b00f743dd2e7ae70987d82691ae4633a3a4b12ea` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-CAP-001-004` / `TC-IMPRANA-VF-CAP-001-004` | `REV_eaa51c426ce9e40485f13e5f61d42b30964828b9755356a79018bba00ed56f75` / `REV_abe4085c269e7e67f69c3ef707e413401321890b03b42a679cb6bfb6353cd839` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-CAP-001-001 — Form limits are qualified at their boundaries

Source persona: Data Steward. Proposed fixture `FIX-VF-CAP-001-001` is not created. Verification duty `TASK-VF-CAP-001-04` (qualification); source `docs/backlog/backlog.csv` record 261, exact block `68a0264a3f125dd4a70861ddd29fb589aa6b2e9356dc73259861fe5a2e893b87`.

**Original preconditions**

1. forms with 199, 200 and 201 questions and with 99, 100 and 101 repeat entries

**Original actions**

1. they are tested

**Exact source oracles — all required**

1. forms with 200 questions and 100 repeat entries are supported
2. existing drafts are preserved

Legacy same-requirement reuse candidates: `TC-VF-CAP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-CAP-001-002 — File and import limits are qualified

Source persona: Data Steward. Proposed fixture `FIX-VF-CAP-001-002` is not created. Verification duty `TASK-VF-CAP-001-04` (qualification); source `docs/backlog/backlog.csv` record 261, exact block `a60aa045682bd550a1fde7e786ba51caa30c0d7569461a033788444cbc8a36d4`.

**Original preconditions**

1. source files at the 100 MB boundary, media files at the 25 MB boundary and an import of one million rows

**Original actions**

1. they are processed

**Exact source oracles — all required**

1. source files up to 100 MB and media files up to 25 MB are accepted
2. the one million-row import completes through an asynchronous path

Legacy same-requirement reuse candidates: `TC-VF-CAP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-CAP-001-003 — Limits are visible before work begins

Source persona: Data Steward. Proposed fixture `FIX-VF-CAP-001-003` is not created. Verification duty `TASK-VF-CAP-001-04` (qualification); source `docs/backlog/backlog.csv` record 261, exact block `8d7d7b9070e53faccec876c7f1a9702ce433ce8f7c2e3c222e4a7f6ce8dccdc9`.

**Original preconditions**

1. a Data Steward is about to start a form, upload or import

**Original actions**

1. the work is set up

**Exact source oracles — all required**

1. the limits and supported combinations are visible before work begins

Legacy same-requirement reuse candidates: `TC-VF-CAP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-CAP-001-004 — Reject undocumented units or frontend constraints

Source persona: Data Steward. Proposed fixture `FIX-VF-CAP-001-004` is not created. Verification duty `TASK-VF-CAP-001-04` (qualification); source `docs/backlog/backlog.csv` record 261, exact block `eaa51c426ce9e40485f13e5f61d42b30964828b9755356a79018bba00ed56f75`.

**Original preconditions**

1. the advertised object limits

**Original actions**

1. qualification is assessed

**Exact source oracles — all required**

1. it fails if decimal versus binary file size units were not documented beforehand
2. it fails if an undocumented frontend constraint reduces any advertised limit

Legacy same-requirement reuse candidates: `TC-VF-CAP-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
