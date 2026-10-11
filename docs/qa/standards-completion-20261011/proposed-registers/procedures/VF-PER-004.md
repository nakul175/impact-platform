## QA v1.3 — source-bound case design (proposed)

Story `VF-PER-004` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PER-004-001` / `TC-IMPRANA-VF-PER-004-001` | `REV_e530784d4f04d0878ec1366c675bc0950f7f69027241e67663df0c5293f62776` / `REV_151d0ae30a36e974c363cf2e1d613493cc496360063cc505f3b3b22b053c6524` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-004-002` / `TC-IMPRANA-VF-PER-004-002` | `REV_1aeb8f04a08242c9724e3a23d3430c406b76463449281fa1ac53b14dcefb28b2` / `REV_349a90322f0c2c7079eb69e7778c0e500f314faf643f30a5240738f2c65cd96d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-004-003` / `TC-IMPRANA-VF-PER-004-003` | `REV_e351779fee887fc3b21840805527089b4d1eb237840d570a7981ba9f100822e2` / `REV_973484636457a925ccafdc25340b732ad41802ce8b50e6c0f3084fa7ba3acda5` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PER-004-001 — Standard import completes validation and ingestion within 10 minutes at p95

Source persona: Data Steward. Proposed fixture `FIX-VF-PER-004-001` is not created. Verification duty `TASK-VF-PER-004-02` (qualification); source `docs/backlog/backlog.csv` record 268, exact block `e530784d4f04d0878ec1366c675bc0950f7f69027241e67663df0c5293f62776`.

**Original preconditions**

1. a standard import of 100000 rows and 30 simple fields with configured deterministic checks
2. the import contains updates, duplicates and rejected rows

**Original actions**

1. the import is run repeatedly

**Exact source oracles — all required**

1. validation and ingestion complete within 10 minutes at p95
2. human approval and external source transfer time are excluded from the measurement

Legacy same-requirement reuse candidates: `TC-VF-PER-004`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-004-002 — Resulting recalculation completes within 5 additional minutes at p95

Source persona: Data Steward. Proposed fixture `FIX-VF-PER-004-002` is not created. Verification duty `TASK-VF-PER-004-02` (qualification); source `docs/backlog/backlog.csv` record 268, exact block `1aeb8f04a08242c9724e3a23d3430c406b76463449281fa1ac53b14dcefb28b2`.

**Original preconditions**

1. eligible ingestion of the standard import has finished

**Original actions**

1. the resulting bounded 1000-indicator recalculation runs

**Exact source oracles — all required**

1. it completes within 5 additional minutes at p95
2. the duration of each stage is recorded separately

Legacy same-requirement reuse candidates: `TC-VF-PER-004`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-004-003 — Reject a throughput result that excludes queuing or retries

Source persona: Data Steward. Proposed fixture `FIX-VF-PER-004-003` is not created. Verification duty `TASK-VF-PER-004-02` (qualification); source `docs/backlog/backlog.csv` record 268, exact block `e351779fee887fc3b21840805527089b4d1eb237840d570a7981ba9f100822e2`.

**Original preconditions**

1. a standard 100000-row, 30-field import run

**Original actions**

1. throughput results are reported

**Exact source oracles — all required**

1. human approval and external transfer are reported separately as exclusions
2. validation, internal queuing and ordinary retries are not excluded from the measured time
3. the target fails if measured validation and ingestion exceed 10 minutes at p95

Legacy same-requirement reuse candidates: `TC-VF-PER-004`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
