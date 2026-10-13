## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-002-001` / `TC-IMPRANA-FR-OPS-002-001` | `REV_3286a7dc2ebe386299da19eaa93ef4f0d15c78d32f10ee808e357b71d2f3c043` / `REV_0e9756fd89b1b9eb3ee9410b41be321fe68b0a40c751f09e5f1293caf761a758` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-002-002` / `TC-IMPRANA-FR-OPS-002-002` | `REV_79be1aa872e14f52ea27539faf83e1efbcae01c9a90c33ddb9c50cd06ad903a2` / `REV_eccf06d355a87709e6bc05e2aacb601ee1a59989a9f158fc58e06043b5185cce` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-002-003` / `TC-IMPRANA-FR-OPS-002-003` | `REV_4f1b0a91700e6154971b0eb4cfdc75b98d2cad50f30e6a2e17f04e6265b73d2e` / `REV_23b282a242b5fa2554a399d667c3ed72853e2aaf107b89dea44c9f7894a43c50` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-002-001 — Warning at 80 percent of an allowance

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OPS-002-001` is not created. Verification duty `TASK-FR-OPS-002-03` (qualification); source `docs/backlog/backlog.csv` record 306, exact block `3286a7dc2ebe386299da19eaa93ef4f0d15c78d32f10ee808e357b71d2f3c043`.

**Original preconditions**

1. a finite allowance for storage, seats, projects, connectors, API workload or AI budget

**Original actions**

1. usage reaches 80 percent of that allowance

**Exact source oracles — all required**

1. a warning is shown with the usage basis

Legacy same-requirement reuse candidates: `TC-OPS-002-01`, `TC-OPS-002-02`, `TC-AT18`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-002-002 — Full storage blocks uploads but not export

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OPS-002-002` is not created. Verification duty `TASK-FR-OPS-002-03` (qualification); source `docs/backlog/backlog.csv` record 306, exact block `79be1aa872e14f52ea27539faf83e1efbcae01c9a90c33ddb9c50cd06ad903a2`.

**Original preconditions**

1. the storage allowance is full

**Original actions**

1. a Data Author attempts a new media upload
2. the Organisation Administrator exports existing data

**Exact source oracles — all required**

1. the upload is blocked safely
2. the permitted export remains available

Legacy same-requirement reuse candidates: `TC-OPS-002-01`, `TC-OPS-002-02`, `TC-AT18`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-002-003 — Reject limit enforcement that weakens security or data

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OPS-002-003` is not created. Verification duty `TASK-FR-OPS-002-03` (qualification); source `docs/backlog/backlog.csv` record 306, exact block `4f1b0a91700e6154971b0eb4cfdc75b98d2cad50f30e6a2e17f04e6265b73d2e`.

**Original preconditions**

1. a tenant at the limit of an allowance

**Original actions**

1. entitlement enforcement applies

**Exact source oracles — all required**

1. MFA is not removed, stored data is not deleted and protected information is not exposed
2. security repairs and privacy obligations remain executable
3. the commercial quota is not treated as a data permission

Legacy same-requirement reuse candidates: `TC-OPS-002-01`, `TC-OPS-002-02`, `TC-AT18`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
