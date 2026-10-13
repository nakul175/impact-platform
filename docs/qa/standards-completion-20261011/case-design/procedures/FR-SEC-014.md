## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-014` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-014-001` / `TC-IMPRANA-FR-SEC-014-001` | `REV_5e1a7dc726ff8fb5a530e596af51de975c6b43182d288a6c22ef27fdf0dc2801` / `REV_258a71246bb76eb33f00d6f7893a2f8b675327fedcb60cb83875e120d9dce171` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-014-002` / `TC-IMPRANA-FR-SEC-014-002` | `REV_4d5764618c59e665e36a448f2af0baf22047ae2a25c45f04d2328654809e4efb` / `REV_32ca8ed171e9b80426a32f124fd53f3aa22edae75b16f0481a83f6e5dad8783e` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-014-003` / `TC-IMPRANA-FR-SEC-014-003` | `REV_cb38287a92e8d6c4d39ac05a0cb151457951fa3b9949aa0b44a941fe5f310ce0` / `REV_9a315268077d5df6fa8ee83c62b25042ab9635b018a862a2081a59d709ea3fc0` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-014-001 — Separate controls with safe recovery

Source persona: Data Author. Proposed fixture `FIX-FR-SEC-014-001` is not created. Verification duty `TASK-FR-SEC-014-03` (qualification); source `docs/backlog/backlog.csv` record 158, exact block `5e1a7dc726ff8fb5a530e596af51de975c6b43182d288a6c22ef27fdf0dc2801`.

**Original preconditions**

1. abuse controls for login, public collection, search, exports and AI

**Original actions**

1. a user is limited

**Exact source oracles — all required**

1. they see a safe wait or recovery route
2. accessible challenges and assisted recovery are available where needed

Legacy same-requirement reuse candidates: `TC-SEC-014-01`, `TC-SEC-014-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-014-002 — Burst on one form is contained

Source persona: Data Author. Proposed fixture `FIX-FR-SEC-014-002` is not created. Verification duty `TASK-FR-SEC-014-03` (qualification); source `docs/backlog/backlog.csv` record 158, exact block `4d5764618c59e665e36a448f2af0baf22047ae2a25c45f04d2328654809e4efb`.

**Original preconditions**

1. a burst of traffic on one public form

**Original actions**

1. limits apply

**Exact source oracles — all required**

1. rejection is bounded to that form
2. other tenants continue collecting and approving records

Legacy same-requirement reuse candidates: `TC-SEC-014-01`, `TC-SEC-014-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-014-003 — Reject indiscriminate lockout and disclosure

Source persona: Data Author. Proposed fixture `FIX-FR-SEC-014-003` is not created. Verification duty `TASK-FR-SEC-014-03` (qualification); source `docs/backlog/backlog.csv` record 158, exact block `cb38287a92e8d6c4d39ac05a0cb151457951fa3b9949aa0b44a941fe5f310ce0`.

**Original preconditions**

1. an abusive source

**Original actions**

1. denial controls respond

**Exact source oracles — all required**

1. unrelated organisations are not locked out
2. responses do not expose account existence or participant lookup results

Legacy same-requirement reuse candidates: `TC-SEC-014-01`, `TC-SEC-014-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
