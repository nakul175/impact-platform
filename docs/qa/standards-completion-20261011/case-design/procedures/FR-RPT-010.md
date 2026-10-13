## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-010` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-010-001` / `TC-IMPRANA-FR-RPT-010-001` | `REV_941b6c4a060ba81feb82079f6ca49c4e05a913e2ba7e34f070f5f27e17612398` / `REV_55e59527a926cb5c50ef90bf750a10a266f27cb651b61a7b2d74a404367951b3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-010-002` / `TC-IMPRANA-FR-RPT-010-002` | `REV_f5533ec8b6edc37eb451c39f2a2d3e28d11fcd5712c2ee81498b63916ef4127e` / `REV_5ded439cccbfc8cce927b59e6b17770d9fa551e437705ce3e6ab64874853419a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-010-003` / `TC-IMPRANA-FR-RPT-010-003` | `REV_f9c958921d8faf35a2ffeab650a0f993ca981d65f52b1131c2215151b27ad5f0` / `REV_15d884285a441044026cda2bebe89835c7afe7a241395bf4172f89c4bc5ae462` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-010-004` / `TC-IMPRANA-FR-RPT-010-004` | `REV_4c671e6b7f8d8fac34fe0876d7b144f33cbd8e910cbe1b79171a1c57181fcf6a` / `REV_17ce9cfa6c0f330ddd2a36141728275c9bac73a6dc71ca09e906e6aaa01f3335` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-010-001 — Identify every location affected by a metric change

Source persona: Reviewer. Proposed fixture `FIX-FR-RPT-010-001` is not created. Verification duty `TASK-FR-RPT-010-03` (qualification); source `docs/backlog/backlog.csv` record 142, exact block `941b6c4a060ba81feb82079f6ca49c4e05a913e2ba7e34f070f5f27e17612398`.

**Original preconditions**

1. one approved metric used in a report has changed

**Original actions**

1. preapproval reconciliation runs on the new report candidate

**Exact source oracles — all required**

1. every affected narrative and chart location is identified before approval

Legacy same-requirement reuse candidates: `TC-RPT-010-01`, `TC-RPT-010-02`, `TC-AT01`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-010-002 — Version comparison separates change types

Source persona: Reviewer. Proposed fixture `FIX-FR-RPT-010-002` is not created. Verification duty `TASK-FR-RPT-010-03` (qualification); source `docs/backlog/backlog.csv` record 142, exact block `f5533ec8b6edc37eb451c39f2a2d3e28d11fcd5712c2ee81498b63916ef4127e`.

**Original preconditions**

1. two versions of a report

**Original actions**

1. the Reviewer compares them

**Exact source oracles — all required**

1. source, definition, target, calculation, period and narrative changes are shown separately

Legacy same-requirement reuse candidates: `TC-RPT-010-01`, `TC-RPT-010-02`, `TC-AT01`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-010-003 — Reject unexplained official numeric differences

Source persona: Reviewer. Proposed fixture `FIX-FR-RPT-010-003` is not created. Verification duty `TASK-FR-RPT-010-03` (qualification); source `docs/backlog/backlog.csv` record 142, exact block `f9c958921d8faf35a2ffeab650a0f993ca981d65f52b1131c2215151b27ad5f0`.

**Original preconditions**

1. a report candidate with an official number that differs from the snapshot without explanation

**Original actions**

1. the Reviewer attempts to approve it

**Exact source oracles — all required**

1. approval is blocked

Legacy same-requirement reuse candidates: `TC-RPT-010-01`, `TC-RPT-010-02`, `TC-AT01`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-010-004 — Reject unbound manually written numbers

Source persona: Reviewer. Proposed fixture `FIX-FR-RPT-010-004` is not created. Verification duty `TASK-FR-RPT-010-03` (qualification); source `docs/backlog/backlog.csv` record 142, exact block `4c671e6b7f8d8fac34fe0876d7b144f33cbd8e910cbe1b79171a1c57181fcf6a`.

**Original preconditions**

1. a manually written number in a report candidate

**Original actions**

1. it has neither an explicit source binding nor a reviewed non-result classification such as a date or section number

**Exact source oracles — all required**

1. the candidate cannot pass review

Legacy same-requirement reuse candidates: `TC-RPT-010-01`, `TC-RPT-010-02`, `TC-AT01`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
