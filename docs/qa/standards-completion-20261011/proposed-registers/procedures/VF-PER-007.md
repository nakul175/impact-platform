## QA v1.3 — source-bound case design (proposed)

Story `VF-PER-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PER-007-001` / `TC-IMPRANA-VF-PER-007-001` | `REV_52ce0e9141dcbd67583b8a9bf8cfd4534754a07579ea00ca8175fbb350e7597e` / `REV_fd72ca1224ec9ea09b04c07f6daa34f0a91689682350d2650ee4d2f32f2320db` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-007-002` / `TC-IMPRANA-VF-PER-007-002` | `REV_be0650742de1ab1d4d146b43e24f93ef5f1306c875ed105f2a710be569217568` / `REV_eead9ad15c16c66e42222307692609ac55b9eb3ca372361b28a6273e17a7e196` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-007-003` / `TC-IMPRANA-VF-PER-007-003` | `REV_784cf5b20ad0c1a3825d95824211b9721bbff7b5ed54cd57cd292734586e71eb` / `REV_c3ef91f2eacc55e9b6ee08b3c90fe467c0bc22055370eea13d49ecf3d816f8ff` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-007-004` / `TC-IMPRANA-VF-PER-007-004` | `REV_06e3c66baf23aa08337e31b7f0d27bcf0e497b97813cf3229c148efabae1b7cf` / `REV_4167324dc8a5157dcab05b093be27f095b47c1839524919de96833d665998244` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PER-007-001 — Interactive evidence question meets response targets

Source persona: MEL Manager. Proposed fixture `FIX-VF-PER-007-001` is not created. Verification duty `TASK-VF-PER-007-02` (qualification); source `docs/backlog/backlog.csv` record 270, exact block `52ce0e9141dcbd67583b8a9bf8cfd4534754a07579ea00ca8175fbb350e7597e`.

**Original preconditions**

1. a representative supported question set for a use case and model configuration

**Original actions**

1. the MEL Manager asks an interactive evidence question

**Exact source oracles — all required**

1. the question is acknowledged within 2 seconds
2. a first useful response arrives within 15 seconds at p95
3. a completed standard answer arrives within 45 seconds at p95, including policy checks and numeric tools

Legacy same-requirement reuse candidates: `TC-VF-PER-007`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-007-002 — Long tasks run as visible asynchronous jobs

Source persona: MEL Manager. Proposed fixture `FIX-VF-PER-007-002` is not created. Verification duty `TASK-VF-PER-007-02` (qualification); source `docs/backlog/backlog.csv` record 270, exact block `be0650742de1ab1d4d146b43e24f93ef5f1306c875ed105f2a710be569217568`.

**Original preconditions**

1. a long extraction or reporting task

**Original actions**

1. the MEL Manager starts it

**Exact source oracles — all required**

1. it runs as a visible asynchronous job
2. the job can be cancelled and has a declared timeout

Legacy same-requirement reuse candidates: `TC-VF-PER-007`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-007-003 — Reject a generic waiting message as a useful response

Source persona: MEL Manager. Proposed fixture `FIX-VF-PER-007-003` is not created. Verification duty `TASK-VF-PER-007-03` (qualification); source `docs/backlog/backlog.csv` record 270, exact block `784cf5b20ad0c1a3825d95824211b9721bbff7b5ed54cd57cd292734586e71eb`.

**Original preconditions**

1. an interactive evidence question is in progress

**Original actions**

1. only a generic waiting message is shown

**Exact source oracles — all required**

1. it does not count as a first useful response

Legacy same-requirement reuse candidates: `TC-VF-PER-007`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-007-004 — Reject losing the question or an unapproved fallback on provider timeout

Source persona: MEL Manager. Proposed fixture `FIX-VF-PER-007-004` is not created. Verification duty `TASK-VF-PER-007-03` (qualification); source `docs/backlog/backlog.csv` record 270, exact block `06e3c66baf23aa08337e31b7f0d27bcf0e497b97813cf3229c148efabae1b7cf`.

**Original preconditions**

1. the AI provider times out on a question

**Original actions**

1. the failure is handled

**Exact source oracles — all required**

1. the question is preserved and the manual route is offered
2. no unapproved fallback is used

Legacy same-requirement reuse candidates: `TC-VF-PER-007`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
