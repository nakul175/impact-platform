## QA v1.3 — source-bound case design (proposed)

Story `FR-PRG-001` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRG-001-001` / `TC-IMPRANA-FR-PRG-001-001` | `REV_4f973a901d9d17d88e1ee888d6d45a5fbcd4eb0a7e033c454e159a9399d4c068` / `REV_9cd9a6761f1cc5a866556b2224581e6a692150aa76b7e062d00fbab48090d4e1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-001-002` / `TC-IMPRANA-FR-PRG-001-002` | `REV_7fe8188350664f0a0951a5c3bc36604a4e7d2433766bca5db8a3b36ae70d92ac` / `REV_ed2608c356aadc81653cdb2b440fc6c86d70ce754d89bc21210e8f2089026696` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-001-003` / `TC-IMPRANA-FR-PRG-001-003` | `REV_d0fd1c9b8036620f3f0178257aa6a8b4e414632ff7e3e3ea34ecf35c0acfd16d` / `REV_b51378b9ca8649695d4101b7471404233924a286d7fbe0f0e3fe258021e13891` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-001-004` / `TC-IMPRANA-FR-PRG-001-004` | `REV_fb7f188c5fc4ea50228a8a104905a4bf8cb5b68f329bf95ecd40f4fc8b7dce60` / `REV_e0ccb107dba0b8bbfa9a582b49116a2134cc18335a0a23e3b0f634b97e6f9052` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRG-001-005` / `TC-IMPRANA-FR-PRG-001-005` | `REV_95f4ddc8977b433c28d54bcbdc0b0a76aa0edbaa716b187168bea4e06c90d678` / `REV_a592f8f3ac51c2e0e4b8602dafd0325e8352d19e479739c005e7e034375776b3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRG-001-001 — Create a programme with validated details

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-001-001` is not created. Verification duty `TASK-FR-PRG-001-04` (qualification); source `docs/backlog/backlog.csv` record 137, exact block `4f973a901d9d17d88e1ee888d6d45a5fbcd4eb0a7e033c454e159a9399d4c068`.

**Original preconditions**

1. a Programme Manager creating a programme

**Original actions**

1. they enter a code, title, dates, owner, geography and reporting calendar

**Exact source oracles — all required**

1. the code is validated as unique within the tenant
2. the programme is created

Legacy same-requirement reuse candidates: `TC-PRG-001-01`, `TC-PRG-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-001-002 — One project in two portfolios

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-001-002` is not created. Verification duty `TASK-FR-PRG-001-04` (qualification); source `docs/backlog/backlog.csv` record 137, exact block `7fe8188350664f0a0951a5c3bc36604a4e7d2433766bca5db8a3b36ae70d92ac`.

**Original preconditions**

1. project P

**Original actions**

1. it is added to two thematic portfolios with effective dates

**Exact source oracles — all required**

1. the organisation registry contains one project identity and two memberships

Legacy same-requirement reuse candidates: `TC-PRG-001-01`, `TC-PRG-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-001-003 — Registry respects access

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-001-003` is not created. Verification duty `TASK-FR-PRG-001-04` (qualification); source `docs/backlog/backlog.csv` record 137, exact block `d0fd1c9b8036620f3f0178257aa6a8b4e414632ff7e3e3ea34ecf35c0acfd16d`.

**Original preconditions**

1. a user with access to only some projects

**Original actions**

1. they filter the registry

**Exact source oracles — all required**

1. access is applied before counts are shown
2. archive or reopen is available only through lifecycle actions

Legacy same-requirement reuse candidates: `TC-PRG-001-01`, `TC-PRG-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-001-004 — Reject a duplicate code

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-001-004` is not created. Verification duty `TASK-FR-PRG-001-04` (qualification); source `docs/backlog/backlog.csv` record 137, exact block `fb7f188c5fc4ea50228a8a104905a4bf8cb5b68f329bf95ecd40f4fc8b7dce60`.

**Original preconditions**

1. an existing programme code in the tenant

**Original actions**

1. another programme is created with the same code

**Exact source oracles — all required**

1. creation is refused

Legacy same-requirement reuse candidates: `TC-PRG-001-01`, `TC-PRG-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRG-001-005 — Reject ordinary submissions to an archived project

Source persona: Programme Manager. Proposed fixture `FIX-FR-PRG-001-005` is not created. Verification duty `TASK-FR-PRG-001-04` (qualification); source `docs/backlog/backlog.csv` record 137, exact block `95f4ddc8977b433c28d54bcbdc0b0a76aa0edbaa716b187168bea4e06c90d678`.

**Original preconditions**

1. an archived project

**Original actions**

1. a user attempts an ordinary new submission

**Exact source oracles — all required**

1. the submission is refused
2. authorised auditors can still find the project in search

Legacy same-requirement reuse candidates: `TC-PRG-001-01`, `TC-PRG-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
