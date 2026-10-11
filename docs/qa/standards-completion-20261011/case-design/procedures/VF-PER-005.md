## QA v1.3 — source-bound case design (proposed)

Story `VF-PER-005` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PER-005-001` / `TC-IMPRANA-VF-PER-005-001` | `REV_6cd91a8074da420f354465bef08c91b7555f8d34b832fa07007c93330066b6e1` / `REV_576e667b0f8bf8b79f5bbfd615b5d8cc04a03567f73b5932977a5baa5ce8d56b` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-005-002` / `TC-IMPRANA-VF-PER-005-002` | `REV_da3e09cd0bb172bcd835112be9d9a1fdd08bbd729ddf090eaf5a0d8984b2af33` / `REV_31348161b891783451047422db857e927853c980a48385dbe0fbb2339b5b969f` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-005-003` / `TC-IMPRANA-VF-PER-005-003` | `REV_37afb351312cc124e527e724199d7be26d42fea961348f2c4b2b8ecf3492cfc4` / `REV_472b848b819f49ffe622ca2c305445d65eb5b0afb08524fe7c68d244281cd297` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-005-004` / `TC-IMPRANA-VF-PER-005-004` | `REV_653245011ee4533ce8c380cb4028eaf1b45985686daaa2ac6cc6179ccdda3f7c` / `REV_0debf6c51dbd2b342397d3f9127eb4c3d4a2843402a7a836b086b48d54818163` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-005-005` / `TC-IMPRANA-VF-PER-005-005` | `REV_82834aa577be164d19a661fd7cf801048c5705bc8b0267bc3230ac5ff355f61b` / `REV_ffe8755008f929bd09395f71b7fe70a43fde8f4ea24e4a1a99c1cacd62792b47` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PER-005-001 — Standard export or report completes within 5 minutes at p95

Source persona: Analyst. Proposed fixture `FIX-VF-PER-005-001` is not created. Verification duty `TASK-VF-PER-005-02` (qualification); source `docs/backlog/backlog.csv` record 269, exact block `6cd91a8074da420f354465bef08c91b7555f8d34b832fa07007c93330066b6e1`.

**Original preconditions**

1. the service is under mixed load

**Original actions**

1. an Analyst requests a 100000-row data export or a 50-page report with up to 20 charts

**Exact source oracles — all required**

1. the finished artifact is available within 5 minutes at p95
2. its content is validated as complete

Legacy same-requirement reuse candidates: `TC-VF-PER-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-005-002 — Job acknowledges receipt, shows progress and can be cancelled

Source persona: Analyst. Proposed fixture `FIX-VF-PER-005-002` is not created. Verification duty `TASK-VF-PER-005-02` (qualification); source `docs/backlog/backlog.csv` record 269, exact block `da3e09cd0bb172bcd835112be9d9a1fdd08bbd729ddf090eaf5a0d8984b2af33`.

**Original preconditions**

1. an Analyst has submitted an export or report job

**Original actions**

1. the job is received

**Exact source oracles — all required**

1. receipt is acknowledged within 2 seconds
2. progress is visible while the job runs
3. the Analyst can cancel the job at any stage

Legacy same-requirement reuse candidates: `TC-VF-PER-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-005-003 — Larger jobs show estimated class and explicit limits

Source persona: Analyst. Proposed fixture `FIX-VF-PER-005-003` is not created. Verification duty `TASK-VF-PER-005-03` (qualification); source `docs/backlog/backlog.csv` record 269, exact block `37afb351312cc124e527e724199d7be26d42fea961348f2c4b2b8ecf3492cfc4`.

**Original preconditions**

1. a job larger than the standard export or report

**Original actions**

1. the Analyst requests it

**Exact source oracles — all required**

1. the estimated class and explicit limits are shown

Legacy same-requirement reuse candidates: `TC-VF-PER-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-005-004 — Reject a ready link to an incomplete artifact

Source persona: Analyst. Proposed fixture `FIX-VF-PER-005-004` is not created. Verification duty `TASK-VF-PER-005-03` (qualification); source `docs/backlog/backlog.csv` record 269, exact block `653245011ee4533ce8c380cb4028eaf1b45985686daaa2ac6cc6179ccdda3f7c`.

**Original preconditions**

1. an export or report job whose artifact is incomplete

**Original actions**

1. the job status is shown

**Exact source oracles — all required**

1. no ready link is offered
2. a ready link to an incomplete artifact counts as a failure

Legacy same-requirement reuse candidates: `TC-VF-PER-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-005-005 — Reject download after permission revocation

Source persona: Analyst. Proposed fixture `FIX-VF-PER-005-005` is not created. Verification duty `TASK-VF-PER-005-03` (qualification); source `docs/backlog/backlog.csv` record 269, exact block `82834aa577be164d19a661fd7cf801048c5705bc8b0267bc3230ac5ff355f61b`.

**Original preconditions**

1. an export completed within the performance targets
2. the Analyst's permission is revoked before download

**Original actions**

1. the Analyst tries to retrieve the artifact

**Exact source oracles — all required**

1. retrieval is refused

Legacy same-requirement reuse candidates: `TC-VF-PER-005`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
