## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-010` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-010-001` / `TC-IMPRANA-FR-ANA-010-001` | `REV_31d956ec4376b2cb96e2bef6d07e812d721ddc912542ea57d6ed03a706259846` / `REV_98d3043541e6c0864d365392b1dc0442116681e49b51f4fb6e196c6463cb4338` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-010-002` / `TC-IMPRANA-FR-ANA-010-002` | `REV_d96cf0281658ae262f21760e6decd4a47d9db263a788fc595201874698dc9e9a` / `REV_24d5a511996491f99279a3a8fba1905b917e8d6837824755f81012db07f19ac5` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-010-003` / `TC-IMPRANA-FR-ANA-010-003` | `REV_1171f8f4b05bffd158ed759fcaaca198759ba846f0d6883045ae84b45a452918` / `REV_0461f9c7e1bf4b819e8b40c100516955634fd0eac9cff12424206ed32e923cbe` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-010-004` / `TC-IMPRANA-FR-ANA-010-004` | `REV_c23f4ddbf4ba63b48ab58f2a72f57fae917726928c8dc27453775e91d64d9802` / `REV_4dc8a039db5c48c3ea106b9d359c52245ddb6759c61ca0cd713c7ebaa15018b2` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-010-001 — Create a governed BI connection

Source persona: Data Steward. Proposed fixture `FIX-FR-ANA-010-001` is not created. Verification duty `TASK-FR-ANA-010-03` (qualification); source `docs/backlog/backlog.csv` record 329, exact block `31d956ec4376b2cb96e2bef6d07e812d721ddc912542ea57d6ed03a706259846`.

**Original preconditions**

1. the Data Steward selects governed datasets and field scope

**Original actions**

1. a BI connection is created

**Exact source oracles — all required**

1. a service identity is issued
2. the external destination and reuse terms are recorded
3. the data package includes definitions, units, value states and freshness

Legacy same-requirement reuse candidates: `TC-ANA-010-01`, `TC-ANA-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-010-002 — Revoked service identity cannot refresh

Source persona: Data Steward. Proposed fixture `FIX-FR-ANA-010-002` is not created. Verification duty `TASK-FR-ANA-010-03` (qualification); source `docs/backlog/backlog.csv` record 329, exact block `d96cf0281658ae262f21760e6decd4a47d9db263a788fc595201874698dc9e9a`.

**Original preconditions**

1. a BI connection with a successful prior extract

**Original actions**

1. the Data Steward revokes the BI service identity

**Exact source oracles — all required**

1. subsequent refresh fails
2. the register identifies the last successful external extract

Legacy same-requirement reuse candidates: `TC-ANA-010-01`, `TC-ANA-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-010-003 — Reject refresh without current authority

Source persona: Data Steward. Proposed fixture `FIX-FR-ANA-010-003` is not created. Verification duty `TASK-FR-ANA-010-03` (qualification); source `docs/backlog/backlog.csv` record 329, exact block `1171f8f4b05bffd158ed759fcaaca198759ba846f0d6883045ae84b45a452918`.

**Original preconditions**

1. a refresh request whose credential or object authority is no longer current

**Original actions**

1. the refresh runs

**Exact source oracles — all required**

1. no data is retrieved

Legacy same-requirement reuse candidates: `TC-ANA-010-01`, `TC-ANA-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-010-004 — Reject claims of remote erasure or unrestricted access

Source persona: Data Steward. Proposed fixture `FIX-FR-ANA-010-004` is not created. Verification duty `TASK-FR-ANA-010-03` (qualification); source `docs/backlog/backlog.csv` record 329, exact block `c23f4ddbf4ba63b48ab58f2a72f57fae917726928c8dc27453775e91d64d9802`.

**Original preconditions**

1. data has already been extracted to an external tool

**Original actions**

1. access is revoked

**Exact source oracles — all required**

1. the external copies remain tracked as disclosures
2. they are not represented as remotely erased
3. no unrestricted database connection is implied

Legacy same-requirement reuse candidates: `TC-ANA-010-01`, `TC-ANA-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
