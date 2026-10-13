## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-008` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-008-001` / `TC-IMPRANA-FR-SEC-008-001` | `REV_c565fb4e46b73bbf7707f0e4dbb16f4a24e4b19459790eaab930f757e9687ee1` / `REV_da277b69da036730828e87126394c3e66c499c9f469edf20e41c298ca15b8659` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-008-002` / `TC-IMPRANA-FR-SEC-008-002` | `REV_f68862930ff9b257415315ae451c41107f76f275ecaa14b862469bf566ffe8e8` / `REV_9231404dc4d7e31b14c94339d0db7b56a02047edbb472ff39189bed6029221ee` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-008-003` / `TC-IMPRANA-FR-SEC-008-003` | `REV_3924489715bacb274879cf83939898c8e9e095b53a339c0e7fccb990210cb495` / `REV_54d85647f1c3202a07dfe616b642c1db16d8a325fd405dae4eb4af53ba8198a2` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-008-001 — Release record links its evidence

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-008-001` is not created. Verification duty `TASK-FR-SEC-008-03` (qualification); source `docs/backlog/backlog.csv` record 2, exact block `c565fb4e46b73bbf7707f0e4dbb16f4a24e4b19459790eaab930f757e9687ee1`.

**Original preconditions**

1. a release

**Original actions**

1. its record is created

**Exact source oracles — all required**

1. it links requirement and specification changes, reviewed code, dependency and licence inventory, security checks, migration results and approvers
2. security relevant changes identify their affected threat and regression cases

Legacy same-requirement reuse candidates: `TC-SEC-008-01`, `TC-SEC-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-008-002 — Trace a changed rule in production

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-008-002` is not created. Verification duty `TASK-FR-SEC-008-03` (qualification); source `docs/backlog/backlog.csv` record 2, exact block `f68862930ff9b257415315ae451c41107f76f275ecaa14b862469bf566ffe8e8`.

**Original preconditions**

1. a production version with a changed export rule

**Original actions**

1. the Platform Operator traces it

**Exact source oracles — all required**

1. they reach its FSD parent, reviewed change, negative tests and release approval

Legacy same-requirement reuse candidates: `TC-SEC-008-01`, `TC-SEC-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-008-003 — Reject promotion without gate evidence

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-008-003` is not created. Verification duty `TASK-FR-SEC-008-03` (qualification); source `docs/backlog/backlog.csv` record 2, exact block `3924489715bacb274879cf83939898c8e9e095b53a339c0e7fccb990210cb495`.

**Original preconditions**

1. a release missing declared gate evidence

**Original actions**

1. production promotion is attempted

**Exact source oracles — all required**

1. promotion is blocked
2. a feature flag is not accepted as a security exemption
3. an unsupported dependency requires an owned risk and resolution decision

Legacy same-requirement reuse candidates: `TC-SEC-008-01`, `TC-SEC-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
