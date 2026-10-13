## QA v1.3 — source-bound case design (proposed)

Story `FR-FIN-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FIN-004-001` / `TC-IMPRANA-FR-FIN-004-001` | `REV_3d1e846af726ccacd6675bd565728feea5d28b6acf5f4ef8762806b97d88b84c` / `REV_f354ae007561814fa89ed373c7b949d692c088fd34a5ef86a0c2c3cf52a25051` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-004-002` / `TC-IMPRANA-FR-FIN-004-002` | `REV_e883162a8b8682387c9e56a44ded3d905f567d1f038b79ea66d926b032a7872c` / `REV_8024a9828d5d6b51b1ce6d2247f789fdb36b919c02a3a38577e20ee4b00a3713` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-004-003` / `TC-IMPRANA-FR-FIN-004-003` | `REV_785f9a27a655da36883399ca114dfba80b3b4703a3cdee122a35666759ef29c3` / `REV_b77de21219c15c12e4b9279ed3048d248ae15ee6c5a93bf32b3f001922e5ec16` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-004-004` / `TC-IMPRANA-FR-FIN-004-004` | `REV_90191a6410bdd78adf77fd12c9d47d79b02556236032b8cfea66f7de71f4b7f0` / `REV_2ddc1cb3fe8e729be799a175a924e485e06472cde226536afc5cc8a448323e27` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FIN-004-001 — Convert and pin a rate

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-004-001` is not created. Verification duty `TASK-FR-FIN-004-03` (qualification); source `docs/backlog/backlog.csv` record 231, exact block `3d1e846af726ccacd6675bd565728feea5d28b6acf5f4ef8762806b97d88b84c`.

**Original preconditions**

1. a transaction of USD 100 and a rate of 83 INR per USD

**Original actions**

1. the Finance Officer converts it to INR

**Exact source oracles — all required**

1. the converted value is INR 8300
2. the report snapshot pins the rate, source, effective date and rate direction
3. the original transaction remains in USD

Legacy same-requirement reuse candidates: `TC-FIN-004-01`, `TC-FIN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-004-002 — A later rate creates a new view

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-004-002` is not created. Verification duty `TASK-FR-FIN-004-03` (qualification); source `docs/backlog/backlog.csv` record 231, exact block `e883162a8b8682387c9e56a44ded3d905f567d1f038b79ea66d926b032a7872c`.

**Original preconditions**

1. a published report shows INR 8300 converted at 83

**Original actions**

1. a later rate of 84 is applied

**Exact source oracles — all required**

1. a new analytical view or restatement is created
2. the published historical value remains 8300

Legacy same-requirement reuse candidates: `TC-FIN-004-01`, `TC-FIN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-004-003 — Reject silent current-rate conversion of history

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-004-003` is not created. Verification duty `TASK-FR-FIN-004-03` (qualification); source `docs/backlog/backlog.csv` record 231, exact block `785f9a27a655da36883399ca114dfba80b3b4703a3cdee122a35666759ef29c3`.

**Original preconditions**

1. a historical publication with pinned conversion values

**Original actions**

1. the current rate changes

**Exact source oracles — all required**

1. the publication is not silently converted at the current rate

Legacy same-requirement reuse candidates: `TC-FIN-004-01`, `TC-FIN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-004-004 — Reject zero or parity for missing rates

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-004-004` is not created. Verification duty `TASK-FR-FIN-004-03` (qualification); source `docs/backlog/backlog.csv` record 231, exact block `90191a6410bdd78adf77fd12c9d47d79b02556236032b8cfea66f7de71f4b7f0`.

**Original preconditions**

1. no rate exists for the required currency pair and date

**Original actions**

1. conversion is requested

**Exact source oracles — all required**

1. the converted value is unavailable
2. it is not shown as zero or assumed parity

Legacy same-requirement reuse candidates: `TC-FIN-004-01`, `TC-FIN-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
