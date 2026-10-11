## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-006-001` / `TC-IMPRANA-FR-SEC-006-001` | `REV_ce9a11ea0407a4eef051dab767e086784e76ff5ca2f38ab07005d1b5954d9c5a` / `REV_90dcaf36ab1c3fd1888ed12699931895ddbb6d9d155d8f237583954b87fe910b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-006-002` / `TC-IMPRANA-FR-SEC-006-002` | `REV_281db67e4ff6c2f55507c75788bed32976b05da9351f3c39d7b25b1c5619e3f9` / `REV_23822a59cfa30e85058b4fb886b5cec169044df59af82fbdc10fc6ead3ea86ae` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-006-003` / `TC-IMPRANA-FR-SEC-006-003` | `REV_560bf0a9032c8ae89944721619b3c5ce3999e711a25b236740b0a90e0000ec8d` / `REV_01222d0ea587e92f9bbf420dc8dc38e7f3021d045a08a12235626b8179346301` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-006-004` / `TC-IMPRANA-FR-SEC-006-004` | `REV_afbebf6d675407110f99d2afb3c78f7a79a05a6d3041244d00d13f42f889eeb1` / `REV_98b953ef107634199653491309b28e386198e81004a26c0c4bcd7c8e1325921b` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-006-001 — Secret entry returns only a reference

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-SEC-006-001` is not created. Verification duty `TASK-FR-SEC-006-03` (qualification); source `docs/backlog/backlog.csv` record 152, exact block `ce9a11ea0407a4eef051dab767e086784e76ff5ca2f38ab07005d1b5954d9c5a`.

**Original preconditions**

1. an Organisation Administrator entering a connector secret

**Original actions**

1. it is saved

**Exact source oracles — all required**

1. only a credential reference and safe fingerprint are returned

Legacy same-requirement reuse candidates: `TC-SEC-006-01`, `TC-SEC-006-02`, `IT-012`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-006-002 — Rotation and revocation are audited operations

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-SEC-006-002` is not created. Verification duty `TASK-FR-SEC-006-03` (qualification); source `docs/backlog/backlog.csv` record 152, exact block `281db67e4ff6c2f55507c75788bed32976b05da9351f3c39d7b25b1c5619e3f9`.

**Original preconditions**

1. a stored connector credential

**Original actions**

1. it is rotated or revoked

**Exact source oracles — all required**

1. the operation records owner, scope and audit
2. the old credential is rejected after rotation

Legacy same-requirement reuse candidates: `TC-SEC-006-01`, `TC-SEC-006-02`, `IT-012`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-006-003 — Configuration export omits secrets

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-SEC-006-003` is not created. Verification duty `TASK-FR-SEC-006-03` (qualification); source `docs/backlog/backlog.csv` record 152, exact block `560bf0a9032c8ae89944721619b3c5ce3999e711a25b236740b0a90e0000ec8d`.

**Original preconditions**

1. a connection configuration

**Original actions**

1. it is exported and then imported

**Exact source oracles — all required**

1. secret values are omitted from the export
2. the import marks required reconfiguration

Legacy same-requirement reuse candidates: `TC-SEC-006-01`, `TC-SEC-006-02`, `IT-012`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-006-004 — Reject secret exposure

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-SEC-006-004` is not created. Verification duty `TASK-FR-SEC-006-03` (qualification); source `docs/backlog/backlog.csv` record 152, exact block `afbebf6d675407110f99d2afb3c78f7a79a05a6d3041244d00d13f42f889eeb1`.

**Original preconditions**

1. a rotated connector credential

**Original actions**

1. its configuration export and permitted logs are inspected

**Exact source oracles — all required**

1. neither the old nor the new secret is present
2. secrets do not appear in ordinary admin views, client storage, generated reports or diagnostics

Legacy same-requirement reuse candidates: `TC-SEC-006-01`, `TC-SEC-006-02`, `IT-012`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
