## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-012` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-012-001` / `TC-IMPRANA-FR-SEC-012-001` | `REV_458981a298ed71c80cc25fe82e612b60879d0875cbdef4509c5c1c44228863a8` / `REV_606371c9a6c67daffaae01685148f001341b6fb242781d5bf1477bfd4a2fbc6f` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-012-002` / `TC-IMPRANA-FR-SEC-012-002` | `REV_d2b84d439feb51052e5064a9bf651363dc4162d18fdb89e42aae5321d656393f` / `REV_27d62a185111f508ec660e28cffcb90d1855af19090b897cb7b73189dc03d64d` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-012-003` / `TC-IMPRANA-FR-SEC-012-003` | `REV_9043cd1201770b42beb490b1d26bbe203c69c7a0a7772e1cafd91c32a465a76c` / `REV_1f079c74c78b15c3a5d4330c33f38c5395e5a936a6474769af81f92bea1919c1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-012-004` / `TC-IMPRANA-FR-SEC-012-004` | `REV_af8be3ad90a32454b8eb29114789c2b0a48de6b7a87b7938ed1052c152ff6847` / `REV_c5dd5bc6387daf26f47176f3e73c4ff2873f8f43bd515e5dfc24e3af622633ea` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-012-001 — Environment identity is visible

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-012-001` is not created. Verification duty `TASK-FR-SEC-012-03` (qualification); source `docs/backlog/backlog.csv` record 156, exact block `458981a298ed71c80cc25fe82e612b60879d0875cbdef4509c5c1c44228863a8`.

**Original preconditions**

1. a Platform Operator or Integration Developer

**Original actions**

1. they work in any environment

**Exact source oracles — all required**

1. the environment identity is visible

Legacy same-requirement reuse candidates: `TC-SEC-012-01`, `TC-SEC-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-012-002 — Lower environments use synthetic data

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-012-002` is not created. Verification duty `TASK-FR-SEC-012-03` (qualification); source `docs/backlog/backlog.csv` record 156, exact block `d2b84d439feb51052e5064a9bf651363dc4162d18fdb89e42aae5321d656393f`.

**Original preconditions**

1. a lower environment

**Original actions**

1. it is provisioned

**Exact source oracles — all required**

1. synthetic data is the default
2. any exceptional production sample requires approved minimisation and expiry

Legacy same-requirement reuse candidates: `TC-SEC-012-01`, `TC-SEC-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-012-003 — Reject cross environment credentials and copied schedules

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-012-003` is not created. Verification duty `TASK-FR-SEC-012-03` (qualification); source `docs/backlog/backlog.csv` record 156, exact block `9043cd1201770b42beb490b1d26bbe203c69c7a0a7772e1cafd91c32a465a76c`.

**Original preconditions**

1. a test credential and a sandbox with copied configuration

**Original actions**

1. the credential is used against production and copied report schedules are activated in the sandbox

**Exact source oracles — all required**

1. both are prevented
2. the copied configuration omits production secrets, external recipients and active schedules

Legacy same-requirement reuse candidates: `TC-SEC-012-01`, `TC-SEC-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-012-004 — Reject hidden bypasses

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-012-004` is not created. Verification duty `TASK-FR-SEC-012-03` (qualification); source `docs/backlog/backlog.csv` record 156, exact block `af8be3ad90a32454b8eb29114789c2b0a48de6b7a87b7938ed1052c152ff6847`.

**Original preconditions**

1. the production environment

**Original actions**

1. its accounts and roles are reviewed

**Exact source oracles — all required**

1. no hidden production test users or bypass roles exist

Legacy same-requirement reuse candidates: `TC-SEC-012-01`, `TC-SEC-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
