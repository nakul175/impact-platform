## QA v1.3 — source-bound case design (proposed)

Story `FR-MIG-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-MIG-008-001` / `TC-IMPRANA-FR-MIG-008-001` | `REV_73db02d788d2de7c7d03e31b05027f9314882a8573f7eab0a8fa528886ca4aff` / `REV_9d74954dbbb95c0787f16036185d23bcc5037bddfcd68c7d46d612fc45795eea` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-008-002` / `TC-IMPRANA-FR-MIG-008-002` | `REV_52176bef15efaa8cc0835710ba28e14f6a9e8ea71ba56b2787d15286898abd21` / `REV_aff086948fa3542f8809d588b7f2eaec87fd041b3939544595e29c4c896d060a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-008-003` / `TC-IMPRANA-FR-MIG-008-003` | `REV_379e1c82683bcc20ca35bc2a02e2404447cacad37105a11f533a07dac4a57abe` / `REV_9f1f253c3b7f53e673a7dfc96cad9092bc5e0e5c3c133595c018ac83c6f3e2bf` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-008-004` / `TC-IMPRANA-FR-MIG-008-004` | `REV_028dd4700d01fc0e8c85e1c05ada5332b18d211f9396149d0ee7ddedc7f5f84f` / `REV_cf9e2787c344bfe93eebb8e44d5cc07b620a5731e3c3e1492465011d9c276405` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-MIG-008-001 — Close a tenant after confirmed export

Source persona: Executive Director. Proposed fixture `FIX-FR-MIG-008-001` is not created. Verification duty `TASK-FR-MIG-008-04` (qualification); source `docs/backlog/backlog.csv` record 258, exact block `73db02d788d2de7c7d03e31b05027f9314882a8573f7eab0a8fa528886ca4aff`.

**Original preconditions**

1. a tenant with a confirmed export and one held item

**Original actions**

1. the tenant is closed

**Exact source oracles — all required**

1. live credentials and deliveries stop
2. the outcome record identifies the held item and its review date

Legacy same-requirement reuse candidates: `TC-MIG-008-01`, `TC-MIG-008-02`, `TC-AT20`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-008-002 — Outcome record shows closure evidence

Source persona: Executive Director. Proposed fixture `FIX-FR-MIG-008-002` is not created. Verification duty `TASK-FR-MIG-008-04` (qualification); source `docs/backlog/backlog.csv` record 258, exact block `52176bef15efaa8cc0835710ba28e14f6a9e8ea71ba56b2787d15286898abd21`.

**Original preconditions**

1. a closed tenant

**Original actions**

1. the Executive Director opens the outcome record

**Exact source oracles — all required**

1. it shows access termination, completed deletion, backup expiry and outstanding lawful retention

Legacy same-requirement reuse candidates: `TC-MIG-008-01`, `TC-MIG-008-02`, `TC-AT20`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-008-003 — Reject a closure shortcut that bypasses holds or the window

Source persona: Executive Director. Proposed fixture `FIX-FR-MIG-008-003` is not created. Verification duty `TASK-FR-MIG-008-04` (qualification); source `docs/backlog/backlog.csv` record 258, exact block `379e1c82683bcc20ca35bc2a02e2404447cacad37105a11f533a07dac4a57abe`.

**Original preconditions**

1. a tenant with a hold or unexported data within the agreed retrieval window

**Original actions**

1. a closure shortcut is attempted

**Exact source oracles — all required**

1. the hold is not bypassed
2. unexported data is not erased before the agreed window ends

Legacy same-requirement reuse candidates: `TC-MIG-008-01`, `TC-MIG-008-02`, `TC-AT20`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-008-004 — Reject ordinary reopen after irreversible deletion

Source persona: Executive Director. Proposed fixture `FIX-FR-MIG-008-004` is not created. Verification duty `TASK-FR-MIG-008-04` (qualification); source `docs/backlog/backlog.csv` record 258, exact block `028dd4700d01fc0e8c85e1c05ada5332b18d211f9396149d0ee7ddedc7f5f84f`.

**Original preconditions**

1. irreversible deletion has completed for a closed tenant

**Original actions**

1. reactivation is requested

**Exact source oracles — all required**

1. it is not offered as an ordinary reopen

Legacy same-requirement reuse candidates: `TC-MIG-008-01`, `TC-MIG-008-02`, `TC-AT20`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
