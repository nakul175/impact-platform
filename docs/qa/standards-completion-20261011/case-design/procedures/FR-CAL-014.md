## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-014` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-014-001` / `TC-IMPRANA-FR-CAL-014-001` | `REV_63e991e0ed2513c36b20ddd6d3c60c5818de015e7d19d975022252a236276a76` / `REV_d376d0965cf733836a03c45861827b4a8859949d02da4bbb6d0ae2c8c9c57559` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-014-002` / `TC-IMPRANA-FR-CAL-014-002` | `REV_6ff7490086ede40f3dc4b473267402e56f29569b70a13437df6d2b7c93b53c4c` / `REV_390c4b42de57498ee2f2b0fc5f873a6fef48304eadf04bdf14ac252de44dc275` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-014-003` / `TC-IMPRANA-FR-CAL-014-003` | `REV_9f55063fc358d4c3ef86fbe1d2aa47f7c4492d6355ea4c47965a938e059d9a3e` / `REV_1ba005a59e8453970fa22f091202d3f1977f600dc21a1806c74c5f88249f3325` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-014-001 — Project in multiple portfolios is counted once organisation-wide

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-CAL-014-001` is not created. Verification duty `TASK-FR-CAL-014-03` (qualification); source `docs/backlog/backlog.csv` record 203, exact block `63e991e0ed2513c36b20ddd6d3c60c5818de015e7d19d975022252a236276a76`.

**Original preconditions**

1. project P belongs to the health and education portfolios

**Original actions**

1. each portfolio and the organisation-wide count are viewed

**Exact source oracles — all required**

1. each portfolio may show P
2. the organisation unique project count stays one

Legacy same-requirement reuse candidates: `TC-CAL-014-01`, `TC-CAL-014-02`, `TC-AT06`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-014-002 — Allocation view applies approved attribution shares

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-CAL-014-002` is not created. Verification duty `TASK-FR-CAL-014-03` (qualification); source `docs/backlog/backlog.csv` record 203, exact block `6ff7490086ede40f3dc4b473267402e56f29569b70a13437df6d2b7c93b53c4c`.

**Original preconditions**

1. separately approved attribution shares with a declared basis and remainder policy

**Original actions**

1. the allocation view is displayed

**Exact source oracles — all required**

1. results are allocated according to those shares

Legacy same-requirement reuse candidates: `TC-CAL-014-01`, `TC-CAL-014-02`, `TC-AT06`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-014-003 — Reject shares exceeding the source total

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-FR-CAL-014-003` is not created. Verification duty `TASK-FR-CAL-014-03` (qualification); source `docs/backlog/backlog.csv` record 203, exact block `9f55063fc358d4c3ef86fbe1d2aa47f7c4492d6355ea4c47965a938e059d9a3e`.

**Original preconditions**

1. attribution shares that exceed the source total

**Original actions**

1. the allocation view is saved

**Exact source oracles — all required**

1. it is rejected unless the view is explicitly nonadditive and labelled
2. a funding share is never presented as causal impact ownership

Legacy same-requirement reuse candidates: `TC-CAL-014-01`, `TC-CAL-014-02`, `TC-AT06`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
