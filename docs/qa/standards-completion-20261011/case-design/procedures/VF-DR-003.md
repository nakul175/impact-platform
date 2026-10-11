## QA v1.3 — source-bound case design (proposed)

Story `VF-DR-003` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-DR-003-001` / `TC-IMPRANA-VF-DR-003-001` | `REV_62631608edce2e7cc332ee6d16005a3208790ddb8346dbfbabb80fbbcd13168c` / `REV_6fc5938d8317c05e7f4fe593ee63b491907a92fc6b33b608bc04cc9684656a37` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-003-002` / `TC-IMPRANA-VF-DR-003-002` | `REV_a7104e7a6962b91bf42efb7033d5f415fb087b499899e6c2eeeafadfc1f849bd` / `REV_487f3c784d73bd9f8c217866dd4f31944b16aa8e63ea83815e00167126c69b9f` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-003-003` / `TC-IMPRANA-VF-DR-003-003` | `REV_6ce8c922595c8720347ea6c50067b5cb71ea076a90d08c7e62e2941a8770d8dc` / `REV_6e4b577317da9c55222c273d0d5d12de9c7454d2ce2e210196196611464b586b` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-003-004` / `TC-IMPRANA-VF-DR-003-004` | `REV_6e597fa59424f494ebb20a008231179a5d876d22f53e3cb667d6ff5bf00e5091` / `REV_c862bc3c1a6f0b22b71b47b1e4a37ef7cbb1bda580fbb5024388a0e2862352eb` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-DR-003-005` / `TC-IMPRANA-VF-DR-003-005` | `REV_44c584c80ded7a9ed6126435a12ca3447caed1cbe0d556d43a6c0b27eabecd75` / `REV_02f5c90b6e8a69b8e58c3e5a3a1ede8b2cafb91b455e1f91e4282d65d4bda22e` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-DR-003-001 — Backups are protected against alteration

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-003-001` is not created. Verification duty `TASK-VF-DR-003-03` (qualification); source `docs/backlog/backlog.csv` record 119, exact block `62631608edce2e7cc332ee6d16005a3208790ddb8346dbfbabb80fbbcd13168c`.

**Original preconditions**

1. backups of tenant data

**Original actions**

1. unauthorised alteration or use of compromised credentials is attempted

**Exact source oracles — all required**

1. the backups cannot be altered

Legacy same-requirement reuse candidates: `TC-VF-DR-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-003-002 — Restores and disaster recovery are tested on schedule

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-003-002` is not created. Verification duty `TASK-VF-DR-003-03` (qualification); source `docs/backlog/backlog.csv` record 119, exact block `a7104e7a6962b91bf42efb7033d5f415fb087b499899e6c2eeeafadfc1f849bd`.

**Original preconditions**

1. the backup schedule

**Original actions**

1. the monthly representative restore and quarterly disaster exercise are run

**Exact source oracles — all required**

1. protected backup access, attachment integrity, snapshot consistency, key recovery and deletion replay are tested before reopening

Legacy same-requirement reuse candidates: `TC-VF-DR-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-003-003 — Default backup retention is no more than 35 days

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-003-003` is not created. Verification duty `TASK-VF-DR-003-03` (qualification); source `docs/backlog/backlog.csv` record 119, exact block `6ce8c922595c8720347ea6c50067b5cb71ea076a90d08c7e62e2941a8770d8dc`.

**Original preconditions**

1. no approved contract or hold requires a different schedule

**Original actions**

1. backups age

**Exact source oracles — all required**

1. they are retained for no more than 35 days

Legacy same-requirement reuse candidates: `TC-VF-DR-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-003-004 — Reject an archive download as a completed restore

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-003-004` is not created. Verification duty `TASK-VF-DR-003-03` (qualification); source `docs/backlog/backlog.csv` record 119, exact block `6e597fa59424f494ebb20a008231179a5d876d22f53e3cb667d6ff5bf00e5091`.

**Original preconditions**

1. a backup archive has been downloaded successfully

**Original actions**

1. the restore test is assessed

**Exact source oracles — all required**

1. it is not recorded as a completed restore

Legacy same-requirement reuse candidates: `TC-VF-DR-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-DR-003-005 — Reject silent extension of backup retention

Source persona: Platform Operator. Proposed fixture `FIX-VF-DR-003-005` is not created. Verification duty `TASK-VF-DR-003-03` (qualification); source `docs/backlog/backlog.csv` record 119, exact block `44c584c80ded7a9ed6126435a12ca3447caed1cbe0d556d43a6c0b27eabecd75`.

**Original preconditions**

1. a backup retention exception

**Original actions**

1. the default window would be extended

**Exact source oracles — all required**

1. the exception and its owner are recorded
2. the default window is never extended silently

Legacy same-requirement reuse candidates: `TC-VF-DR-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
