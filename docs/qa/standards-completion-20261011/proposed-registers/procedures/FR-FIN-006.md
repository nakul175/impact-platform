## QA v1.3 — source-bound case design (proposed)

Story `FR-FIN-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FIN-006-001` / `TC-IMPRANA-FR-FIN-006-001` | `REV_e23cbcf7126202850b96e6b4ff875d5864517c150e7d42c9ec1724b49d8b2919` / `REV_186290aa736f9deb9769ecd3934797c42d34672c39ee8afbac3b95da10b4d479` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-006-002` / `TC-IMPRANA-FR-FIN-006-002` | `REV_a71d83be806cf54cc3cced6f7ec22eacd1cea3a50b9ce44468d837bbea6bacfb` / `REV_5bdc5321a84f167359e687437159be8b6117f1c4281f830e1e25f9e001a7bae9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-006-003` / `TC-IMPRANA-FR-FIN-006-003` | `REV_3011e15042fe1ec885431334489b6662c9a8252cefad67e11d917b02e7457df3` / `REV_0b60e5c657ecf0c8de4101149fdc18703289a67e8d5b392391c668e5b3778ba9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-006-004` / `TC-IMPRANA-FR-FIN-006-004` | `REV_b31e59dee93f88feffdfc7d806ad6dfc3eba2cea6280ea6d271108f4de1065fb` / `REV_37b99fe4f11ef3712b7f0c144799c218aa271bd3ea3199be81a92a616b5d64e3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FIN-006-001 — Allocate 100 at 60 and 40 percent

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-006-001` is not created. Verification duty `TASK-FR-FIN-006-03` (qualification); source `docs/backlog/backlog.csv` record 342, exact block `e23cbcf7126202850b96e6b4ff875d5864517c150e7d42c9ec1724b49d8b2919`.

**Original preconditions**

1. a shared cost of 100 and an allocation rule of 60 and 40 percent

**Original actions**

1. the Finance Officer previews and approves the allocation

**Exact source oracles — all required**

1. the two outputs sum to 100
2. the approved rule is fixed for the relevant snapshot

Legacy same-requirement reuse candidates: `TC-FIN-006-01`, `TC-FIN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-006-002 — Rounding remainder assigned deterministically

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-006-002` is not created. Verification duty `TASK-FR-FIN-006-03` (qualification); source `docs/backlog/backlog.csv` record 342, exact block `a71d83be806cf54cc3cced6f7ec22eacd1cea3a50b9ce44468d837bbea6bacfb`.

**Original preconditions**

1. an allocation that leaves a residual rounding unit

**Original actions**

1. the allocation is previewed

**Exact source oracles — all required**

1. the remainder is reconciled and assigned by a deterministic stated rule

Legacy same-requirement reuse candidates: `TC-FIN-006-01`, `TC-FIN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-006-003 — Reject weights that do not reconcile

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-006-003` is not created. Verification duty `TASK-FR-FIN-006-03` (qualification); source `docs/backlog/backlog.csv` record 342, exact block `3011e15042fe1ec885431334489b6662c9a8252cefad67e11d917b02e7457df3`.

**Original preconditions**

1. an allocation rule whose weights do not reconcile to the declared total

**Original actions**

1. the Finance Officer attempts to approve it

**Exact source oracles — all required**

1. approval is refused

Legacy same-requirement reuse candidates: `TC-FIN-006-01`, `TC-FIN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-006-004 — Reject repeated or double allocation

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-006-004` is not created. Verification duty `TASK-FR-FIN-006-03` (qualification); source `docs/backlog/backlog.csv` record 342, exact block `b31e59dee93f88feffdfc7d806ad6dfc3eba2cea6280ea6d271108f4de1065fb`.

**Original preconditions**

1. an allocation has been made for an imported cost

**Original actions**

1. the same import is repeated

**Exact source oracles — all required**

1. no additional allocation is created
2. no cost is double charged across overlapping views

Legacy same-requirement reuse candidates: `TC-FIN-006-01`, `TC-FIN-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
