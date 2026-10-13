## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-008-001` / `TC-IMPRANA-FR-ACC-008-001` | `REV_49ece2303459dd4fcf0d0958601994a6d6180fe27b39f6adfcc49dde57237a07` / `REV_a3a422d30ed543c7c2460e75400925bf7495c485b19357da01426704f327ebb7` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-008-002` / `TC-IMPRANA-FR-ACC-008-002` | `REV_e5a67020efa8bbc984646072acef4a14e0e5ac3e1de5d64aa787ebbfc49f67c4` / `REV_fab974000938e314155b837e425b0b207ffab423d4155ed8f57d974fcea06f24` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-008-003` / `TC-IMPRANA-FR-ACC-008-003` | `REV_8f06b68da6754793a1b134cb618e1e1c7a3185fb1a5e095db0850906b0706460` / `REV_eec50cc8307bf9676993b00cc294c204b4493955b22917d1ddd26c59df63726f` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-008-004` / `TC-IMPRANA-FR-ACC-008-004` | `REV_29dae4dedc213ec1236f3bb74829cc5474c757b9ffeca549c7ff00f161ee4e72` / `REV_0b3bcc94ad59e02fa033391f5698016e567bcb30ce8d37711b1eeedd2bd7231f` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-008-001 — Open a support session

Source persona: Support Agent. Proposed fixture `FIX-FR-ACC-008-001` is not created. Verification duty `TASK-FR-ACC-008-03` (qualification); source `docs/backlog/backlog.csv` record 189, exact block `49ece2303459dd4fcf0d0958601994a6d6180fe27b39f6adfcc49dde57237a07`.

**Original preconditions**

1. a support case tied to the tenant consent policy, requested objects, purpose and duration

**Original actions**

1. the Support Agent accesses the tenant using their real identity and an active elevation grant

**Exact source oracles — all required**

1. every sensitive read and mutation is attributed to them

Legacy same-requirement reuse candidates: `TC-ACC-008-01`, `TC-ACC-008-02`, `TC-AT17`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-008-002 — Tenant ends support access

Source persona: Support Agent. Proposed fixture `FIX-FR-ACC-008-002` is not created. Verification duty `TASK-FR-ACC-008-03` (qualification); source `docs/backlog/backlog.csv` record 189, exact block `e5a67020efa8bbc984646072acef4a14e0e5ac3e1de5d64aa787ebbfc49f67c4`.

**Original preconditions**

1. an active support session

**Original actions**

1. the Organisation Administrator ends access

**Exact source oracles — all required**

1. the Support Agent's access ends immediately

Legacy same-requirement reuse candidates: `TC-ACC-008-01`, `TC-ACC-008-02`, `TC-AT17`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-008-003 — Reject operations outside the approved scope

Source persona: Support Agent. Proposed fixture `FIX-FR-ACC-008-003` is not created. Verification duty `TASK-FR-ACC-008-03` (qualification); source `docs/backlog/backlog.csv` record 189, exact block `8f06b68da6754793a1b134cb618e1e1c7a3185fb1a5e095db0850906b0706460`.

**Original preconditions**

1. a support session approved for one failed import

**Original actions**

1. the Support Agent reads the import diagnostics and then attempts an owner transfer

**Exact source oracles — all required**

1. the diagnostic read succeeds
2. the owner transfer is denied

Legacy same-requirement reuse candidates: `TC-ACC-008-01`, `TC-ACC-008-02`, `TC-AT17`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-008-004 — Reject hidden or excessive support access

Source persona: Support Agent. Proposed fixture `FIX-FR-ACC-008-004` is not created. Verification duty `TASK-FR-ACC-008-03` (qualification); source `docs/backlog/backlog.csv` record 189, exact block `29dae4dedc213ec1236f3bb74829cc5474c757b9ffeca549c7ff00f161ee4e72`.

**Original preconditions**

1. a support session without explicit download or participant identity scope

**Original actions**

1. the Support Agent attempts to download data, view participant identities, impersonate a user or use a universal support account

**Exact source oracles — all required**

1. each attempt is refused

Legacy same-requirement reuse candidates: `TC-ACC-008-01`, `TC-ACC-008-02`, `TC-AT17`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
