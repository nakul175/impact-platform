## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-009` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-009-001` / `TC-IMPRANA-FR-ANA-009-001` | `REV_6985421fe587572e9d88e219eb6c6246f23fd09ce79582e53274f8b4c9197bb1` / `REV_3b210265cade782dc797b5cb5302cda530ed496dcb464880a734be3756e0f154` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-009-002` / `TC-IMPRANA-FR-ANA-009-002` | `REV_0f92874a575994ec2d00a5450d0bef279afe167e11fd972bbf08aa27a814db18` / `REV_167affd4bb0f4f6087d6a76cb72e029f079bc2dbb68f92dc88c161ec0153f46c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-009-003` / `TC-IMPRANA-FR-ANA-009-003` | `REV_6390cb85c8e9450dcc8b8eda392b4eab1c04ed5ad1301ab538974b6b13f49bd5` / `REV_504be6f6431ebd79d0f8570afc98a378d84d0fcc5c2343df5637954f10053018` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-009-004` / `TC-IMPRANA-FR-ANA-009-004` | `REV_f818113f3840887dd8263ab49817c9f366a04c265d9ea4044d5ac53c0a550596` / `REV_bf31028ca2d969f1ddb7527fa5e91a119684af45f04c2c358ca13921f8e517e4` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-009-001 — Missed monthly submission raises a missingness alert

Source persona: Programme Manager. Proposed fixture `FIX-FR-ANA-009-001` is not created. Verification duty `TASK-FR-ANA-009-03` (qualification); source `docs/backlog/backlog.csv` record 328, exact block `6985421fe587572e9d88e219eb6c6246f23fd09ce79582e53274f8b4c9197bb1`.

**Original preconditions**

1. an alert declaring measure, condition, minimum coverage, freshness, evaluation cadence, recipients and cooldown

**Original actions**

1. a monthly submission is missed

**Exact source oracles — all required**

1. a missingness alert is generated

Legacy same-requirement reuse candidates: `TC-ANA-009-01`, `TC-ANA-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-009-002 — Approved performance decline raises a separate threshold alert

Source persona: Programme Manager. Proposed fixture `FIX-FR-ANA-009-002` is not created. Verification duty `TASK-FR-ANA-009-03` (qualification); source `docs/backlog/backlog.csv` record 328, exact block `0f92874a575994ec2d00a5450d0bef279afe167e11fd972bbf08aa27a814db18`.

**Original preconditions**

1. the same alert configuration

**Original actions**

1. an approved result shows a performance decline that meets the condition

**Exact source oracles — all required**

1. a threshold alert is generated separately from any missingness alert
2. the triggered alert records the exact evaluated result version

Legacy same-requirement reuse candidates: `TC-ANA-009-01`, `TC-ANA-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-009-003 — Reject treating an absent value as zero

Source persona: Programme Manager. Proposed fixture `FIX-FR-ANA-009-003` is not created. Verification duty `TASK-FR-ANA-009-03` (qualification); source `docs/backlog/backlog.csv` record 328, exact block `6390cb85c8e9450dcc8b8eda392b4eab1c04ed5ad1301ab538974b6b13f49bd5`.

**Original preconditions**

1. a value is absent for the evaluation period

**Original actions**

1. the alert is evaluated

**Exact source oracles — all required**

1. no deterioration alert is raised by treating the absent value as zero

Legacy same-requirement reuse candidates: `TC-ANA-009-01`, `TC-ANA-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-009-004 — Reject separate alerts during cooldown

Source persona: Programme Manager. Proposed fixture `FIX-FR-ANA-009-004` is not created. Verification duty `TASK-FR-ANA-009-03` (qualification); source `docs/backlog/backlog.csv` record 328, exact block `f818113f3840887dd8263ab49817c9f366a04c265d9ea4044d5ac53c0a550596`.

**Original preconditions**

1. an alert has triggered and is within its cooldown

**Original actions**

1. the condition repeats

**Exact source oracles — all required**

1. one incident or digest is updated according to policy

Legacy same-requirement reuse candidates: `TC-ANA-009-01`, `TC-ANA-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
