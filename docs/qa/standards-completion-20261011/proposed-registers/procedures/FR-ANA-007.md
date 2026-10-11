## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-007-001` / `TC-IMPRANA-FR-ANA-007-001` | `REV_e70dbf57c0bf3e59dece335ad912a8579e06ac7d88361f41b3b9bc8705807ff9` / `REV_ecae9b63724a30ac4cfdd4bd1f5291e432e040f7fb0bfb6ad7abed3ed5057b66` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-007-002` / `TC-IMPRANA-FR-ANA-007-002` | `REV_38a00cf9142a0101a463ab8c0cf223d54f7fbdff32a24281ece502fbddb0ee52` / `REV_7dc499daa93ce839ea0f220e8be9ca83ab8f597ea5e9d89880e270373689da5a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-007-003` / `TC-IMPRANA-FR-ANA-007-003` | `REV_a819df6d03736149938112e23f578aaf4ea9783151b1bc9300a061f7fb012c19` / `REV_a51832e6d6a469551ddb8e7a2e6d0a26ed4cf32eb8b8be473051e84112be2602` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-007-004` / `TC-IMPRANA-FR-ANA-007-004` | `REV_81621a85e6d19c033baba1b8515bfed44b8c8b0b35136acbd435302dd32934a8` / `REV_dffb108b22da23483f4344e54832877b917019e204f5f57b4871fba945369b55` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-007-001 — Compatible measures grouped and mismatches flagged

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-ANA-007-001` is not created. Verification duty `TASK-FR-ANA-007-03` (qualification); source `docs/backlog/backlog.csv` record 210, exact block `e70dbf57c0bf3e59dece335ad912a8579e06ac7d88361f41b3b9bc8705807ff9`.

**Original preconditions**

1. the Funder Portfolio Manager selects indicator definitions, periods and coverage thresholds for a portfolio comparison

**Original actions**

1. the comparison is displayed

**Exact source oracles — all required**

1. compatible measures are grouped
2. mismatches are flagged

Legacy same-requirement reuse candidates: `TC-ANA-007-01`, `TC-ANA-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-007-002 — Reviewed comparability required before a league table

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-ANA-007-002` is not created. Verification duty `TASK-FR-ANA-007-03` (qualification); source `docs/backlog/backlog.csv` record 210, exact block `38a00cf9142a0101a463ab8c0cf223d54f7fbdff32a24281ece502fbddb0ee52`.

**Original preconditions**

1. two completion rates with different eligible populations

**Original actions**

1. the Funder Portfolio Manager requests a ranking

**Exact source oracles — all required**

1. an unqualified league table is presented only after comparability has been reviewed
2. otherwise the ranking carries a clear qualified comparison method

Legacy same-requirement reuse candidates: `TC-ANA-007-01`, `TC-ANA-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-007-003 — Reject a raw ranking of non-equivalent measures

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-ANA-007-003` is not created. Verification duty `TASK-FR-ANA-007-03` (qualification); source `docs/backlog/backlog.csv` record 210, exact block `a819df6d03736149938112e23f578aaf4ea9783151b1bc9300a061f7fb012c19`.

**Original preconditions**

1. measures with different denominators, currencies or observation windows

**Original actions**

1. a ranking is requested without an approved comparable set

**Exact source oracles — all required**

1. no raw ranking treating them as equivalent is produced

Legacy same-requirement reuse candidates: `TC-ANA-007-01`, `TC-ANA-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-007-004 — Reject exposing hidden portfolio members

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-ANA-007-004` is not created. Verification duty `TASK-FR-ANA-007-03` (qualification); source `docs/backlog/backlog.csv` record 210, exact block `81621a85e6d19c033baba1b8515bfed44b8c8b0b35136acbd435302dd32934a8`.

**Original preconditions**

1. some portfolio members are outside the Funder Portfolio Manager's permissions

**Original actions**

1. the results are permission filtered

**Exact source oracles — all required**

1. the visible scope is stated
2. hidden members are not exposed

Legacy same-requirement reuse candidates: `TC-ANA-007-01`, `TC-ANA-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
