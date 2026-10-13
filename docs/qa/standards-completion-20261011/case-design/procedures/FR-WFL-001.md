## QA v1.3 — source-bound case design (proposed)

Story `FR-WFL-001` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-WFL-001-001` / `TC-IMPRANA-FR-WFL-001-001` | `REV_1fbc16535327689bca610c36e7e915fd3eca3a6fd3ff48e31f0357eb5c637e59` / `REV_92c59d266c79095f687737457ce5d62df0060dc9fb575c74f6efaab9ebcaac22` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-001-002` / `TC-IMPRANA-FR-WFL-001-002` | `REV_206c46f0e8f05b0ce4752c9d708fccdab8ae469a7782b84863acd8712ec18201` / `REV_bec3638b9e892470ffe31fe14c0c39b04488b2987b157e358a1a596b9e8d76ab` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-001-003` / `TC-IMPRANA-FR-WFL-001-003` | `REV_c3912c69daf4b638df8cd319880239ab9ac45307e27b6e8a2439a3cb654720fc` / `REV_54801635083b8e4823d8a7f62610313a7c283164059e88ac8f5647d229aee549` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-001-004` / `TC-IMPRANA-FR-WFL-001-004` | `REV_699e038e8541bce7c715143e6140541017d1210d49a854e5aa10eff4c9a1c65e` / `REV_dded1056cf6519d1accc7fdadfcf2368653ba70632fbc1140922c4086d4abd03` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-WFL-001-005` / `TC-IMPRANA-FR-WFL-001-005` | `REV_129cc70b4f2f4afac8b683bdce52fbc876a066d94b74784e7134bbb5c3a5e90f` / `REV_7aad834cc9396e2c7cb385d3405e3d47bd1608f0a1ce54d5f79a1aa2e0572675` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-WFL-001-001 — Publish a workflow version

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-WFL-001-001` is not created. Verification duty `TASK-FR-WFL-001-03` (interface); source `docs/backlog/backlog.csv` record 176, exact block `1fbc16535327689bca610c36e7e915fd3eca3a6fd3ff48e31f0357eb5c637e59`.

**Original preconditions**

1. a workflow defining object type, sequential or parallel stages, reviewer eligibility, mandatory reviewers, quorum, thresholds and deadlines

**Original actions**

1. the Organisation Administrator publishes it

**Exact source oracles — all required**

1. the workflow version is pinned
2. new instances use it

Legacy same-requirement reuse candidates: `TC-WFL-001-01`, `TC-WFL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-001-002 — Running instance keeps its original route

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-WFL-001-002` is not created. Verification duty `TASK-FR-WFL-001-03` (interface); source `docs/backlog/backlog.csv` record 176, exact block `206c46f0e8f05b0ce4752c9d708fccdab8ae469a7782b84863acd8712ec18201`.

**Original preconditions**

1. a candidate is underway in a two-stage review

**Original actions**

1. the two-stage review is changed

**Exact source oracles — all required**

1. the candidate retains its original route

Legacy same-requirement reuse candidates: `TC-WFL-001-01`, `TC-WFL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-001-003 — Migrate a running instance

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-WFL-001-003` is not created. Verification duty `TASK-FR-WFL-001-03` (interface); source `docs/backlog/backlog.csv` record 176, exact block `c3912c69daf4b638df8cd319880239ab9ac45307e27b6e8a2439a3cb654720fc`.

**Original preconditions**

1. a candidate underway on an earlier workflow version

**Original actions**

1. an authorised migration is applied

**Exact source oracles — all required**

1. the affected stages restart
2. affected decisions are invalidated with the impact shown

Legacy same-requirement reuse candidates: `TC-WFL-001-01`, `TC-WFL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-001-004 — Reject a workflow without an independent reviewer

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-WFL-001-004` is not created. Verification duty `TASK-FR-WFL-001-03` (interface); source `docs/backlog/backlog.csv` record 176, exact block `699e038e8541bce7c715143e6140541017d1210d49a854e5aa10eff4c9a1c65e`.

**Original preconditions**

1. a workflow being designed

**Original actions**

1. it would leave no independent reviewer

**Exact source oracles — all required**

1. publishing the workflow is refused

Legacy same-requirement reuse candidates: `TC-WFL-001-01`, `TC-WFL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-WFL-001-005 — Reject a quorum bypassing mandatory review

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-WFL-001-005` is not created. Verification duty `TASK-FR-WFL-001-03` (interface); source `docs/backlog/backlog.csv` record 176, exact block `129cc70b4f2f4afac8b683bdce52fbc876a066d94b74784e7134bbb5c3a5e90f`.

**Original preconditions**

1. a workflow with a mandatory privacy or security review

**Original actions**

1. the quorum is reached without that review

**Exact source oracles — all required**

1. the approval does not complete

Legacy same-requirement reuse candidates: `TC-WFL-001-01`, `TC-WFL-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
