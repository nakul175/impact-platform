## QA v1.3 — source-bound case design (proposed)

Story `FR-OFF-002` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OFF-002-001` / `TC-IMPRANA-FR-OFF-002-001` | `REV_7ee0f84da36fe4460156e48888069c16cbe5a341a5990526d46f55538c3ca110` / `REV_3158f6404d5f681ab9e299e4cdc4a2fd60f7eee7d099ee3519e641af2b4d9cc7` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-002-002` / `TC-IMPRANA-FR-OFF-002-002` | `REV_81c113a928ea2abbd396f69c740ab93cc34cfe2bd8f56bd8f864132ec0787a45` / `REV_bfd15ba728c9b1543619b68c4848b89844263caed1b32def5a1e6a441cde9688` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-002-003` / `TC-IMPRANA-FR-OFF-002-003` | `REV_fbae71beec992779305b255a89ad8050b89673fbc003ff280c4927e9bbb4fd53` / `REV_664ecadea840f7ffbf7b217594c0a6b764fcd9ac0436aaea0e6e91668bf046a7` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-002-004` / `TC-IMPRANA-FR-OFF-002-004` | `REV_22a757ead39d5bbbcd649dc7dbbea10fd62592902a4ea18087e62de0122c9d8d` / `REV_deb5bedf8ad49f4bad49c864b07be8acbb3bb3a769926cbc1e7fd4287242d0a5` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OFF-002-001 — Local save returns a device receipt

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-002-001` is not created. Verification duty `TASK-FR-OFF-002-03` (qualification); source `docs/backlog/backlog.csv` record 272, exact block `7ee0f84da36fe4460156e48888069c16cbe5a341a5990526d46f55538c3ca110`.

**Original preconditions**

1. a collector capturing data offline

**Original actions**

1. they save

**Exact source oracles — all required**

1. a device receipt and safe status are shown
2. drafts, stable IDs and attachment references persist

Legacy same-requirement reuse candidates: `TC-OFF-002-01`, `TC-OFF-002-02`, `TC-AT21`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-002-002 — Restart during an attachment save

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-002-002` is not created. Verification duty `TASK-FR-OFF-002-03` (qualification); source `docs/backlog/backlog.csv` record 272, exact block `81c113a928ea2abbd396f69c740ab93cc34cfe2bd8f56bd8f864132ec0787a45`.

**Original preconditions**

1. the device restarts during an attachment save

**Original actions**

1. the app reopens

**Exact source oracles — all required**

1. the saved answers survive and recovered work is listed
2. the incomplete file is flagged
3. no false server received status appears

Legacy same-requirement reuse candidates: `TC-OFF-002-01`, `TC-OFF-002-02`, `TC-AT21`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-002-003 — Storage warning before capture becomes unsafe

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-002-003` is not created. Verification duty `TASK-FR-OFF-002-03` (qualification); source `docs/backlog/backlog.csv` record 272, exact block `fbae71beec992779305b255a89ad8050b89673fbc003ff280c4927e9bbb4fd53`.

**Original preconditions**

1. device storage is running low

**Original actions**

1. capture continues

**Exact source oracles — all required**

1. a storage warning appears before capture becomes unsafe

Legacy same-requirement reuse candidates: `TC-OFF-002-01`, `TC-OFF-002-02`, `TC-AT21`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-002-004 — Reject sensitive offline capture without qualified secure storage

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-002-004` is not created. Verification duty `TASK-FR-OFF-002-03` (qualification); source `docs/backlog/backlog.csv` record 272, exact block `22a757ead39d5bbbcd649dc7dbbea10fd62592902a4ea18087e62de0122c9d8d`.

**Original preconditions**

1. secure durable storage cannot be qualified on a client

**Original actions**

1. sensitive offline collection is attempted

**Exact source oracles — all required**

1. it is disabled and the supported alternative is shown
2. a local acknowledgement is never presented as server durability

Legacy same-requirement reuse candidates: `TC-OFF-002-01`, `TC-OFF-002-02`, `TC-AT21`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
