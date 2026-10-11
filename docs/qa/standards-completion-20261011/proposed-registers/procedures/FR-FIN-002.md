## QA v1.3 — source-bound case design (proposed)

Story `FR-FIN-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FIN-002-001` / `TC-IMPRANA-FR-FIN-002-001` | `REV_5b259d5f131c4eaff53feb4912028ab0aaa66c088860ad0330c3ef1c8fd327b5` / `REV_97abcca23c508dc7c871249e18735967872c5ab6d356725340922ae93e28a6ca` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-002-002` / `TC-IMPRANA-FR-FIN-002-002` | `REV_cea5d0521801dc93ca90e07277e7b5bc80546f07fd7b6da2744ef5b88d395528` / `REV_553a691bb535890678eb81b62d8493fee5045b252c1ffb94972669b4748f40ba` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-002-003` / `TC-IMPRANA-FR-FIN-002-003` | `REV_139b2400cc227e47a9359650e7234d5f2270f677dc1070e4621c7080a2f9d73e` / `REV_1edba0831f2966c997fe82773a2ca2f653f43d9ba50ba445977556de0acf0030` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FIN-002-001 — Raise an approved budget

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-002-001` is not created. Verification duty `TASK-FR-FIN-002-03` (qualification); source `docs/backlog/backlog.csv` record 339, exact block `5b259d5f131c4eaff53feb4912028ab0aaa66c088860ad0330c3ef1c8fd327b5`.

**Original preconditions**

1. an approved budget of 100

**Original actions**

1. the Finance Officer revises it to 120 and the revision is approved

**Exact source oracles — all required**

1. the original comparison remains available
2. imported actual spending stays unchanged

Legacy same-requirement reuse candidates: `TC-FIN-002-01`, `TC-FIN-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-002-002 — Draft revisions compare against baselines

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-002-002` is not created. Verification duty `TASK-FR-FIN-002-03` (qualification); source `docs/backlog/backlog.csv` record 339, exact block `cea5d0521801dc93ca90e07277e7b5bc80546f07fd7b6da2744ef5b88d395528`.

**Original preconditions**

1. a draft budget revision with lines by activity, category, partner and period with currency

**Original actions**

1. the Finance Officer reviews it

**Exact source oracles — all required**

1. it is compared against the original and current baseline
2. approval pins the budget and its rate assumptions

Legacy same-requirement reuse candidates: `TC-FIN-002-01`, `TC-FIN-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-002-003 — Reject budget changes that alter actuals or history

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-002-003` is not created. Verification duty `TASK-FR-FIN-002-03` (qualification); source `docs/backlog/backlog.csv` record 339, exact block `139b2400cc227e47a9359650e7234d5f2270f677dc1070e4621c7080a2f9d73e`.

**Original preconditions**

1. an approved budget with imported actual expenditure and previously reported variance

**Original actions**

1. the budget is changed

**Exact source oracles — all required**

1. transaction amounts are not altered
2. historically reported variance is not altered

Legacy same-requirement reuse candidates: `TC-FIN-002-01`, `TC-FIN-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
