## QA v1.3 — source-bound case design (proposed)

Story `FR-PRG-002` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRG-002-001` / `TC-IMPRANA-FR-PRG-002-001` | `REV_05791a2a64765eed1ac87a020b7fbade84f486f7ee7fefa821694154bceb7824` / `REV_c3e553e7e4e63f37dbeedc2d3da9fc7bd6202a9b9c3040a0b82f5a789dc4e93b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-002-002` / `TC-IMPRANA-FR-PRG-002-002` | `REV_40bee9028ea4205b041d0139ba7e9f33437180a7d6bd0ea3db27bf4097857b66` / `REV_80d4201e56d1b04a947aa214af3b7a82b84f1306372804e79c6c861eeff1da01` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-002-003` / `TC-IMPRANA-FR-PRG-002-003` | `REV_4d369ca5b6a99e07cb6e370eff028d590879deeff3db7bad09c79a82418e4133` / `REV_2b2cb6a424aab7436d23d3cf4e577fe7176acfbc10eaab5477df484592e841c4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-002-004` / `TC-IMPRANA-FR-PRG-002-004` | `REV_ad2cd3ae1d08a48941bc50aa4287df2c8bd0504b2158e87f907d707c47a5c835` / `REV_fd3f1704105ca0ed275f8530038bde6c180376341bd87e6637697c05fdbe6060` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-002-005` / `TC-IMPRANA-FR-PRG-002-005` | `REV_2e19662f6e32094cc83eeb48f0fa689e31545c34b4b989e442bb23e4bb4ea938` / `REV_52751969cc74f612365e925f35f84695ea3b67a075bda38374b5d9c0839c321f` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRG-002-001 — Define an activity

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-002-001` is not created. Verification duty `TASK-FR-PRG-002-03` (qualification); source `docs/backlog/backlog.csv` record 291, exact block `05791a2a64765eed1ac87a020b7fbade84f486f7ee7fefa821694154bceb7824`.

**Original preconditions**

1. a Programme Manager planning work

**Original actions**

1. they create an activity with assignee, start, due date, predecessor links, milestone evidence and framework reference

**Exact source oracles — all required**

1. the activity is saved
2. blocked and cancelled are available as explicit states

Legacy same-requirement reuse candidates: `TC-PRG-002-01`, `TC-PRG-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-002-002 — Complete an activity with evidence

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-002-002` is not created. Verification duty `TASK-FR-PRG-002-03` (qualification); source `docs/backlog/backlog.csv` record 291, exact block `40bee9028ea4205b041d0139ba7e9f33437180a7d6bd0ea3db27bf4097857b66`.

**Original preconditions**

1. an activity with declared deliverable evidence

**Original actions**

1. the assignee marks it complete

**Exact source oracles — all required**

1. completion requires the declared evidence or an authorised exception

Legacy same-requirement reuse candidates: `TC-PRG-002-01`, `TC-PRG-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-002-003 — Predecessor delay flags downstream risk

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-002-003` is not created. Verification duty `TASK-FR-PRG-002-03` (qualification); source `docs/backlog/backlog.csv` record 291, exact block `4d369ca5b6a99e07cb6e370eff028d590879deeff3db7bad09c79a82418e4133`.

**Original preconditions**

1. activity A precedes activity B

**Original actions**

1. activity A is delayed

**Exact source oracles — all required**

1. B shows dependency risk
2. B's approved due date is retained
3. no indicator achievement is invented

Legacy same-requirement reuse candidates: `TC-PRG-002-01`, `TC-PRG-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-002-004 — Reject a dependency cycle

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-002-004` is not created. Verification duty `TASK-FR-PRG-002-03` (qualification); source `docs/backlog/backlog.csv` record 291, exact block `ad2cd3ae1d08a48941bc50aa4287df2c8bd0504b2158e87f907d707c47a5c835`.

**Original preconditions**

1. activity A precedes activity B

**Original actions**

1. a user makes B a predecessor of A

**Exact source oracles — all required**

1. the link is rejected

Legacy same-requirement reuse candidates: `TC-PRG-002-01`, `TC-PRG-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-002-005 — Reject a due date before start

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-002-005` is not created. Verification duty `TASK-FR-PRG-002-03` (qualification); source `docs/backlog/backlog.csv` record 291, exact block `2e19662f6e32094cc83eeb48f0fa689e31545c34b4b989e442bb23e4bb4ea938`.

**Original preconditions**

1. an activity with a start date

**Original actions**

1. a user sets a due date before the start

**Exact source oracles — all required**

1. the date is rejected

Legacy same-requirement reuse candidates: `TC-PRG-002-01`, `TC-PRG-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
