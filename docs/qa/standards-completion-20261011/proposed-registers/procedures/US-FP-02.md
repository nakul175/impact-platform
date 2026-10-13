## QA v1.3 — source-bound case design (proposed)

Story `US-FP-02` · 2 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-FP-02-001` / `TC-IMPRANA-US-FP-02-001` | `REV_9eabe6e921f86ff15847137f88ff0e339c14d33b444475cec942fbc25ab0d7b0` / `REV_b5472ff729e7fc7f7e2ab9d1fd539c18a7beb5d629717743428c1ce1d94d500d` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-FP-02-002` / `TC-IMPRANA-US-FP-02-002` | `REV_251bebf18ce0405e2de612a2fac5e303c4577cf7604ea4073640147731421e93` / `REV_433f20a550d5810c7c6bfbbf3e543cdf98a114f528c5e2ee5a33302d4594a28c` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-FP-02-001 — Portfolio view aggregated by default

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-FP-02-001` is not created. Verification duty `TASK-US-FP-02-03` (qualification); source `docs/backlog/backlog.csv` record 236, exact block `9eabe6e921f86ff15847137f88ff0e339c14d33b444475cec942fbc25ab0d7b0`.

**Original preconditions**

1. a cohort of grantees who share metrics

**Original actions**

1. the Funder Portfolio Manager opens the portfolio view

**Exact source oracles — all required**

1. progress, adoption and ROI are shown aggregated across grantees by default

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-FP-02-002 — Reject metrics grantees have not agreed to share

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-FP-02-002` is not created. Verification duty `TASK-US-FP-02-03` (qualification); source `docs/backlog/backlog.csv` record 236, exact block `251bebf18ce0405e2de612a2fac5e303c4577cf7604ea4073640147731421e93`.

**Original preconditions**

1. a grantee who has not agreed to share a metric

**Original actions**

1. the Funder Portfolio Manager views the portfolio

**Exact source oracles — all required**

1. that metric is not shown for that grantee
2. it is not included in any aggregate

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
