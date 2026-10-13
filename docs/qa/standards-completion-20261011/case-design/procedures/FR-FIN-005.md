## QA v1.3 — source-bound case design (proposed)

Story `FR-FIN-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FIN-005-001` / `TC-IMPRANA-FR-FIN-005-001` | `REV_01fa969c455a213f2b4b9841a4ae2fe616c4178217877766ac28da3b145d0ae7` / `REV_9dcdb3f0d3487c0c3a03dc89081fc39dff2e38fb33f9ec21e8ff3928ea2666ca` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-005-002` / `TC-IMPRANA-FR-FIN-005-002` | `REV_161e7a8a81685fd9f3671c97c22c534203cc25e9ebba5f49da1795127ae4c4c9` / `REV_cbe3ba83cfbdc94f0ce8e9d730a1f23984d6947672a6ac9dccbb9d312248c16a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-005-003` / `TC-IMPRANA-FR-FIN-005-003` | `REV_b7c8c5171b11731cefe507fb4bf2e377a4f21eae28e27cf9660c7627b628aea4` / `REV_745b8368229d9d9bd15e59e34bffcde83973f8ac165715770c9405bd3dbb5521` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-005-004` / `TC-IMPRANA-FR-FIN-005-004` | `REV_12bc21e401d8238eb4985a48248d4ffb6a6b653bf43bcfec638ccd6db953b857` / `REV_fe3dcd394cd34e82ab1fe30820af317f35caf3d3508402b1c7a47ff359011a45` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FIN-005-001 — Show unspent budget and forecast overrun as separate facts

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-005-001` is not created. Verification duty `TASK-FR-FIN-005-03` (qualification); source `docs/backlog/backlog.csv` record 341, exact block `01fa969c455a213f2b4b9841a4ae2fe616c4178217877766ac28da3b145d0ae7`.

**Original preconditions**

1. a budget of 100, recorded spending of 60 and a forecast total of 110

**Original actions**

1. the Finance Officer opens the variance view

**Exact source oracles — all required**

1. it shows 40 currently unspent
2. it shows a forecast overrun of ten as a separate fact
3. the sign convention is labelled

Legacy same-requirement reuse candidates: `TC-FIN-005-01`, `TC-FIN-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-005-002 — Forecast assumptions recorded separately

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-005-002` is not created. Verification duty `TASK-FR-FIN-005-03` (qualification); source `docs/backlog/backlog.csv` record 341, exact block `161e7a8a81685fd9f3671c97c22c534203cc25e9ebba5f49da1795127ae4c4c9`.

**Original preconditions**

1. a variance view with a selected budget version, actual cutoff, commitments and forecast method

**Original actions**

1. a forecast is saved

**Exact source oracles — all required**

1. its assumptions and author or method version are recorded separately from actuals

Legacy same-requirement reuse candidates: `TC-FIN-005-01`, `TC-FIN-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-005-003 — Reject treating missing spending as underspend

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-005-003` is not created. Verification duty `TASK-FR-FIN-005-03` (qualification); source `docs/backlog/backlog.csv` record 341, exact block `b7c8c5171b11731cefe507fb4bf2e377a4f21eae28e27cf9660c7627b628aea4`.

**Original preconditions**

1. spending data is missing for a period

**Original actions**

1. variance is calculated

**Exact source oracles — all required**

1. the missing data is not shown as underspend

Legacy same-requirement reuse candidates: `TC-FIN-005-01`, `TC-FIN-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-005-004 — Reject forecasts entering actual expenditure

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-005-004` is not created. Verification duty `TASK-FR-FIN-005-03` (qualification); source `docs/backlog/backlog.csv` record 341, exact block `12bc21e401d8238eb4985a48248d4ffb6a6b653bf43bcfec638ccd6db953b857`.

**Original preconditions**

1. a forecast exists

**Original actions**

1. actual expenditure is displayed or reported

**Exact source oracles — all required**

1. the forecast does not enter the actual expenditure series
2. it does not imply programme impact success

Legacy same-requirement reuse candidates: `TC-FIN-005-01`, `TC-FIN-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
