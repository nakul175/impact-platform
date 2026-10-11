## QA v1.3 — source-bound case design (proposed)

Story `FR-PLN-004` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PLN-004-001` / `TC-IMPRANA-FR-PLN-004-001` | `REV_8fb19a80a06c02bf823b16bbc932eb2d775c5e63404d21da26d2515211d63372` / `REV_88c2e484c202474c44aea4f820eaeb9efcbc69d86611b4270b5213019621c432` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-004-002` / `TC-IMPRANA-FR-PLN-004-002` | `REV_84df8c15e106bcc307b56932db735e0c9f7eaa1cf3fbade59af779c9c1bcae06` / `REV_2d51f044179b0ad3399141a3b5df1f209a3347b43ddc209a1dfec6376b8f6ae8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-004-003` / `TC-IMPRANA-FR-PLN-004-003` | `REV_55da929dfc682ea109b280f360e47ad9ef3adaf096c0eb1881f6be5bd41a5525` / `REV_911ffe9108af19becb22e164b52974c03ad8f7428f7469af85f094836d1de5c4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-004-004` / `TC-IMPRANA-FR-PLN-004-004` | `REV_45798891d6e6667e4c0d9596dd5698f9f82243b36564456d3df0699c2039e058` / `REV_454e9f84882f329495968052ac2fb3bce41398e543c693973be7741c63ea1977` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PLN-004-005` / `TC-IMPRANA-FR-PLN-004-005` | `REV_20f61be177350aadd0cfa827afe63ba58af26cbee11e86967484f93138fed59c` / `REV_e028a422432456b99bc538ae7a155fa241135912c60dc082c3799f9691156cc6` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PLN-004-001 — Publish a library version with governance details

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-004-001` is not created. Verification duty `TASK-FR-PLN-004-03` (qualification); source `docs/backlog/backlog.csv` record 303, exact block `8fb19a80a06c02bf823b16bbc932eb2d775c5e63404d21da26d2515211d63372`.

**Original preconditions**

1. a MEL Manager curating a reusable library

**Original actions**

1. they publish a library version

**Exact source oracles — all required**

1. the version records applicability, owner, review date and permitted override fields

Legacy same-requirement reuse candidates: `TC-PLN-004-01`, `TC-PLN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-004-002 — Consuming projects stay on their version until they adopt a reviewed revision

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-004-002` is not created. Verification duty `TASK-FR-PLN-004-03` (qualification); source `docs/backlog/backlog.csv` record 303, exact block `84df8c15e106bcc307b56932db735e0c9f7eaa1cf3fbade59af779c9c1bcae06`.

**Original preconditions**

1. two projects that consume the same library template

**Original actions**

1. the MEL Manager updates the template denominator and publishes a new version

**Exact source oracles — all required**

1. each project receives an update notice showing the semantic differences and affected local changes
2. both projects remain on their existing versions
3. each project moves to the revised version only when it adopts the reviewed revision

Legacy same-requirement reuse candidates: `TC-PLN-004-01`, `TC-PLN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-004-003 — Project declines a library update

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-004-003` is not created. Verification duty `TASK-FR-PLN-004-03` (qualification); source `docs/backlog/backlog.csv` record 303, exact block `55da929dfc682ea109b280f360e47ad9ef3adaf096c0eb1881f6be5bd41a5525`.

**Original preconditions**

1. a project with a pending library update

**Original actions**

1. the Programme Manager rejects the update with a reason

**Exact source oracles — all required**

1. the project stays on its existing version
2. the reason is recorded

Legacy same-requirement reuse candidates: `TC-PLN-004-01`, `TC-PLN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-004-004 — Reject automatic update of approved definitions

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-004-004` is not created. Verification duty `TASK-FR-PLN-004-03` (qualification); source `docs/backlog/backlog.csv` record 303, exact block `45798891d6e6667e4c0d9596dd5698f9f82243b36564456d3df0699c2039e058`.

**Original preconditions**

1. a project that consumes a library template as a managed instance with an approved definition

**Original actions**

1. a new library version is published

**Exact source oracles — all required**

1. the approved definition is not updated automatically

Legacy same-requirement reuse candidates: `TC-PLN-004-01`, `TC-PLN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PLN-004-005 — Reject new use of a retired library

Source persona: MEL Manager. Proposed fixture `FIX-FR-PLN-004-005` is not created. Verification duty `TASK-FR-PLN-004-03` (qualification); source `docs/backlog/backlog.csv` record 303, exact block `20f61be177350aadd0cfa827afe63ba58af26cbee11e86967484f93138fed59c`.

**Original preconditions**

1. a library that has been retired

**Original actions**

1. a user tries to instantiate it in a project

**Exact source oracles — all required**

1. the instantiation is refused
2. existing reports that used the library remain valid

Legacy same-requirement reuse candidates: `TC-PLN-004-01`, `TC-PLN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
