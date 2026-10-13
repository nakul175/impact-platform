## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-007-001` / `TC-IMPRANA-FR-PRV-007-001` | `REV_d288adda2bf105344ded19a48c55ff5abea9074c8c1b8b1809cc859fea18f788` / `REV_ac6646d8cd4befb77f1b22eaf24c2b7793632786eba8535b906c5c5f6d2fe3d1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-007-002` / `TC-IMPRANA-FR-PRV-007-002` | `REV_a20dedb7305b48492e9efb170d83c2678dc2b2d7bce08d9465e75492ca31a12e` / `REV_dbdf5d8b2b0a21b2a773e27f7c541c1e03843a4087a10ca84d27c0171e8350f1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-007-003` / `TC-IMPRANA-FR-PRV-007-003` | `REV_a8e0548a411a334e3e9de372980a68df4b0e4b3d2dd655bf061ffad0d8067e09` / `REV_d9d1fcf94d6ca7acd02d9e5b08583b6fb472962d66c3e52628218bab84c942e4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-007-004` / `TC-IMPRANA-FR-PRV-007-004` | `REV_9c632dc5f3ea36b3621497ba45ced89f31c9f888dc530ab90b3732c5c57ede8d` / `REV_ad0643810ffc34d11d5bd847532020a7c28cdef8a29c45c0ed4f94f66f67bddf` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-007-001 — Household member access request

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-007-001` is not created. Verification duty `TASK-FR-PRV-007-04` (qualification); source `docs/backlog/backlog.csv` record 132, exact block `d288adda2bf105344ded19a48c55ff5abea9074c8c1b8b1809cc859fea18f788`.

**Original preconditions**

1. a privacy case for one household member's access request with verified subject scope

**Original actions**

1. the authorised handler prepares the response

**Exact source oracles — all required**

1. only that member's permitted information is delivered
2. another household member's confidential answers are excluded

Legacy same-requirement reuse candidates: `TC-PRV-007-01`, `TC-PRV-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-007-002 — Case outcome is recorded with reason

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-007-002` is not created. Verification duty `TASK-FR-PRV-007-04` (qualification); source `docs/backlog/backlog.csv` record 132, exact block `a20dedb7305b48492e9efb170d83c2678dc2b2d7bce08d9465e75492ca31a12e`.

**Original preconditions**

1. a privacy case with request type, verified subject scope, deadline policy and authorised handler

**Original actions**

1. the handler closes the case

**Exact source oracles — all required**

1. the outcome is recorded as completed, partially completed, rejected or on hold with a reason and review evidence

Legacy same-requirement reuse candidates: `TC-PRV-007-01`, `TC-PRV-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-007-003 — Reject a single hardcoded response deadline

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-007-003` is not created. Verification duty `TASK-FR-PRV-007-04` (qualification); source `docs/backlog/backlog.csv` record 132, exact block `a8e0548a411a334e3e9de372980a68df4b0e4b3d2dd655bf061ffad0d8067e09`.

**Original preconditions**

1. privacy cases under different jurisdictions

**Original actions**

1. the response deadline is set

**Exact source oracles — all required**

1. it comes from the selected deadline policy
2. no single jurisdiction's deadline is applied as universal

Legacy same-requirement reuse candidates: `TC-PRV-007-01`, `TC-PRV-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-007-004 — Reject a public participant lookup

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-007-004` is not created. Verification duty `TASK-FR-PRV-007-04` (qualification); source `docs/backlog/backlog.csv` record 132, exact block `9c632dc5f3ea36b3621497ba45ced89f31c9f888dc530ab90b3732c5c57ede8d`.

**Original preconditions**

1. subject verification for a privacy case

**Original actions**

1. verification evidence is collected

**Exact source oracles — all required**

1. only minimal evidence is requested
2. no public participant lookup is created

Legacy same-requirement reuse candidates: `TC-PRV-007-01`, `TC-PRV-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
