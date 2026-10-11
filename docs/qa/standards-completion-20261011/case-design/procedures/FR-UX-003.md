## QA v1.3 — source-bound case design (proposed)

Story `FR-UX-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-UX-003-001` / `TC-IMPRANA-FR-UX-003-001` | `REV_a7180086534d92da8e944cd82bedb4ddf0d037f529c84993124e89b2b11f1149` / `REV_032e18cef5417bc9b15e1451e23ad01fe06f4f329e2306c8b2a037df9da6d93a` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-003-002` / `TC-IMPRANA-FR-UX-003-002` | `REV_aeb5c4708a92bfbc17ff394c93eb482f6e13181da5d2ec74605c800621664e5a` / `REV_4de7c379e8f9a8dc6447cae8ea672dc93de2f044a80f500cf8e449a78d83fbfb` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-003-003` / `TC-IMPRANA-FR-UX-003-003` | `REV_c8066f94a99e856a045904da9d69bd2a06fa95bb2643aa820633e514d0c44b0d` / `REV_e1468412e08bc841b18fdb3c201b45014a5edfa765599bb40a28d6a9e7a7d9ee` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-003-004` / `TC-IMPRANA-FR-UX-003-004` | `REV_2f61b9b522352208117c59f1e569f3ac8956ce47b1b757d6777cb3e56fb0a429` / `REV_0a01ce15088fad7c7723e72a9040ef93920052f0a038427456b37afeabc51052` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-UX-003-001 — Recover an import receipt after a timeout

Source persona: Data Author. Proposed fixture `FIX-FR-UX-003-001` is not created. Verification duty `TASK-FR-UX-003-03` (qualification); source `docs/backlog/backlog.csv` record 170, exact block `a7180086534d92da8e944cd82bedb4ddf0d037f529c84993124e89b2b11f1149`.

**Original preconditions**

1. an import confirmation that timed out

**Original actions**

1. the Data Author reconnects

**Exact source oracles — all required**

1. the existing job receipt is recovered
2. no additional load is created

Legacy same-requirement reuse candidates: `TC-UX-003-01`, `TC-UX-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-003-002 — Destructive actions preview and reversible changes offer an inverse

Source persona: Data Author. Proposed fixture `FIX-FR-UX-003-002` is not created. Verification duty `TASK-FR-UX-003-03` (qualification); source `docs/backlog/backlog.csv` record 170, exact block `aeb5c4708a92bfbc17ff394c93eb482f6e13181da5d2ec74605c800621664e5a`.

**Original preconditions**

1. a destructive action

**Original actions**

1. the Data Author starts it

**Exact source oracles — all required**

1. the affected objects are previewed
2. reversible changes offer an explicit inverse operation where business semantics support it

Legacy same-requirement reuse candidates: `TC-UX-003-01`, `TC-UX-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-003-003 — Reject undo that rewrites history

Source persona: Data Author. Proposed fixture `FIX-FR-UX-003-003` is not created. Verification duty `TASK-FR-UX-003-03` (qualification); source `docs/backlog/backlog.csv` record 170, exact block `c8066f94a99e856a045904da9d69bd2a06fa95bb2643aa820633e514d0c44b0d`.

**Original preconditions**

1. a change that was audited, downloaded externally or lawfully deleted

**Original actions**

1. undo is used

**Exact source oracles — all required**

1. the audit is not erased
2. externally downloaded copies are not treated as unpublished
3. lawfully deleted data is not restored

Legacy same-requirement reuse candidates: `TC-UX-003-01`, `TC-UX-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-003-004 — Reject repeating a request with an unknown outcome

Source persona: Data Author. Proposed fixture `FIX-FR-UX-003-004` is not created. Verification duty `TASK-FR-UX-003-03` (qualification); source `docs/backlog/backlog.csv` record 170, exact block `2f61b9b522352208117c59f1e569f3ac8956ce47b1b757d6777cb3e56fb0a429`.

**Original preconditions**

1. a request whose outcome is unknown

**Original actions**

1. the Data Author tries to repeat it

**Exact source oracles — all required**

1. receipt reconciliation is required before the repeat proceeds

Legacy same-requirement reuse candidates: `TC-UX-003-01`, `TC-UX-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
