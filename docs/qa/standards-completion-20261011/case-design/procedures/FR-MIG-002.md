## QA v1.3 — source-bound case design (proposed)

Story `FR-MIG-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-MIG-002-001` / `TC-IMPRANA-FR-MIG-002-001` | `REV_8b4f705b0ad20ee90db83394bff7ed6607d12f640a3af1f7cf9ba69132d690a1` / `REV_f4e945563d63e4b1ce2384245855b26c4926a8fce765309c9376a27b112a54fc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-002-002` / `TC-IMPRANA-FR-MIG-002-002` | `REV_f0f74cc1735dbc97003f106b9af263cea0557fa3a22ff6b89b137f257b5be93a` / `REV_cc064b926d9efed5c3cc61296b4489316b4a79d0857c651a64c04250e10e61d3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-MIG-002-003` / `TC-IMPRANA-FR-MIG-002-003` | `REV_4ec41ac141b4c97a4de4e2508052ac3ae12e47fdd548d2d88d3a034b37b25960` / `REV_3c8974f4cbffd2db3cd274a28cb653f6d3b124def189f0781d0311314be64031` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-MIG-002-001 — Two identical trials are compared

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-002-001` is not created. Verification duty `TASK-FR-MIG-002-03` (qualification); source `docs/backlog/backlog.csv` record 253, exact block `8b4f705b0ad20ee90db83394bff7ed6607d12f640a3af1f7cf9ba69132d690a1`.

**Original preconditions**

1. the same source snapshot and mapping version

**Original actions**

1. the Data Steward runs two identical trials into a clean or keyed trial

**Exact source oracles — all required**

1. intended records, errors and totals are compared
2. no duplicate achievements occur
3. no real recipient receives a message

Legacy same-requirement reuse candidates: `TC-MIG-002-01`, `TC-MIG-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-002-002 — Reject side effects from trial data

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-002-002` is not created. Verification duty `TASK-FR-MIG-002-03` (qualification); source `docs/backlog/backlog.csv` record 253, exact block `f0f74cc1735dbc97003f106b9af263cea0557fa3a22ff6b89b137f257b5be93a`.

**Original preconditions**

1. a trial migration in an isolated tenant context

**Original actions**

1. trial data would trigger a live notification, payment action, connector write or public report

**Exact source oracles — all required**

1. the action is blocked

Legacy same-requirement reuse candidates: `TC-MIG-002-01`, `TC-MIG-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-MIG-002-003 — Reject trial credentials in production

Source persona: Data Steward. Proposed fixture `FIX-FR-MIG-002-003` is not created. Verification duty `TASK-FR-MIG-002-03` (qualification); source `docs/backlog/backlog.csv` record 253, exact block `4ec41ac141b4c97a4de4e2508052ac3ae12e47fdd548d2d88d3a034b37b25960`.

**Original preconditions**

1. credentials issued for a trial

**Original actions**

1. they are used against production

**Exact source oracles — all required**

1. access is refused

Legacy same-requirement reuse candidates: `TC-MIG-002-01`, `TC-MIG-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
