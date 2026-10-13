## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-004` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-004-001` / `TC-IMPRANA-FR-PRV-004-001` | `REV_37ab5d35f002bb0efc63a92d2acc6a6f4cf545b5b18ddbdb0a91ed42e16646ae` / `REV_628b6eaca3d54e3382d4bb531fcc21a142241f904eea3df09ccb58a27e1714b3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-004-002` / `TC-IMPRANA-FR-PRV-004-002` | `REV_f588ca5d01554c13813fd3a55ed695c839c938559938bdc11804aa20a8dd532a` / `REV_fb046765fb46c979a283d675aa4bbe92196e929f914de2064fe8bbae45cae08d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-004-003` / `TC-IMPRANA-FR-PRV-004-003` | `REV_635772e345d1dded8bcb21a9f6bbc42309a81800ba773e945472477d373253f6` / `REV_2f4d64113f40ab5b449b4b013dfb2ed67077788a5ed5dbbc52e30bfeba1660ed` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-004-004` / `TC-IMPRANA-FR-PRV-004-004` | `REV_cce025a33f2673eab1b3791ccc27bed8342714363f035884c76d21c35339cb7a` / `REV_392a039731b65027e0ced0fa0aa2744e168d5fdd36a904037d8617d57b36a33e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-004-005` / `TC-IMPRANA-FR-PRV-004-005` | `REV_41db408ce0112095f290797b1f6eb411f8ce5eb81562f5afcd935c4a8fd2b40a` / `REV_5c616853d43a7b38ccdea9528704c3b38ef4d1b52b1c275156e91f10a1087265` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-004-001 — Each data class expires on its own schedule

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-004-001` is not created. Verification duty `TASK-FR-PRV-004-04` (qualification); source `docs/backlog/backlog.csv` record 129, exact block `37ab5d35f002bb0efc63a92d2acc6a6f4cf545b5b18ddbdb0a91ed42e16646ae`.

**Original preconditions**

1. a retention policy of 90 days for diagnostic logs
2. a separate approved retention term for evidence

**Original actions**

1. each schedule reaches its expiry

**Exact source oracles — all required**

1. each class expires through its own schedule
2. any exceptions are recorded with an accountable owner

Legacy same-requirement reuse candidates: `TC-PRV-004-01`, `TC-PRV-004-02`, `SEC-004`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-004-002 — Preview shows affected objects and holds

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-004-002` is not created. Verification duty `TASK-FR-PRV-004-04` (qualification); source `docs/backlog/backlog.csv` record 129, exact block `f588ca5d01554c13813fd3a55ed695c839c938559938bdc11804aa20a8dd532a`.

**Original preconditions**

1. a Privacy Officer drafting a retention policy with data class, purpose, trigger, duration, expiry action and owner

**Original actions**

1. they preview the policy

**Exact source oracles — all required**

1. the preview calculates the affected objects and holds

Legacy same-requirement reuse candidates: `TC-PRV-004-01`, `TC-PRV-004-02`, `SEC-004`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-004-003 — Collection activation requires approved policies

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-004-003` is not created. Verification duty `TASK-FR-PRV-004-04` (qualification); source `docs/backlog/backlog.csv` record 129, exact block `635772e345d1dded8bcb21a9f6bbc42309a81800ba773e945472477d373253f6`.

**Original preconditions**

1. a collection without approved record and evidence retention policies

**Original actions**

1. a Programme Manager tries to activate the collection

**Exact source oracles — all required**

1. activation is blocked until those policies are approved
2. operational defaults inherit the BRD bounds

Legacy same-requirement reuse candidates: `TC-PRV-004-01`, `TC-PRV-004-02`, `SEC-004`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-004-004 — Reject a generic retention value covering every class

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-004-004` is not created. Verification duty `TASK-FR-PRV-004-04` (qualification); source `docs/backlog/backlog.csv` record 129, exact block `cce025a33f2673eab1b3791ccc27bed8342714363f035884c76d21c35339cb7a`.

**Original preconditions**

1. a single generic tenant retention value

**Original actions**

1. it would apply to every data class without a class-specific policy

**Exact source oracles — all required**

1. it is refused as a policy for every class

Legacy same-requirement reuse candidates: `TC-PRV-004-01`, `TC-PRV-004-02`, `SEC-004`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-004-005 — Reject a policy change that hides impact or drops holds

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-004-005` is not created. Verification duty `TASK-FR-PRV-004-04` (qualification); source `docs/backlog/backlog.csv` record 129, exact block `41db408ce0112095f290797b1f6eb411f8ce5eb81562f5afcd935c4a8fd2b40a`.

**Original preconditions**

1. an approved retention policy with valid holds

**Original actions**

1. the Privacy Officer changes the policy

**Exact source oracles — all required**

1. the earlier or later deletion impact is disclosed before approval
2. valid holds are preserved

Legacy same-requirement reuse candidates: `TC-PRV-004-01`, `TC-PRV-004-02`, `SEC-004`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
