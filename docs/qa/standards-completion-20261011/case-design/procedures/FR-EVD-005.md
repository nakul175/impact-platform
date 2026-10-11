## QA v1.3 — source-bound case design (proposed)

Story `FR-EVD-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-EVD-005-001` / `TC-IMPRANA-FR-EVD-005-001` | `REV_48418f397b885f4de0bbda4dc655839b20a8fa4637961760438c1e068b8cc115` / `REV_87e0f901c0750efa7c457c1df83d5691c6c172c5988b69e4690d67ae8b52756e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-005-002` / `TC-IMPRANA-FR-EVD-005-002` | `REV_f96eafaca5ec9592767646876daa2f241183075df33633cbe565dfa18b48f7af` / `REV_892a52445ca23bbc9bbd2842b7d23128096412d0fd9755bdf73aa2609d16c52c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-005-003` / `TC-IMPRANA-FR-EVD-005-003` | `REV_a6e5b8d84ac6ddbaac42d779536c76e3aceee4b0ed30f3f1db868ee6ee0e495b` / `REV_4c7f1a69f2d3296606e61c50c144b1ebac2c3cdb1ddee4e9e7de61c6d53a23cf` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-005-004` / `TC-IMPRANA-FR-EVD-005-004` | `REV_c373fff2f3d35f9664c9a473fd5542bc33961a27b1d514237bf259b04186ef11` / `REV_d14bfe8d36a693064acba29b122d6ddc56acc0514d3759f2b60a49b3de6fad17` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-EVD-005-001 — Maintain a versioned codebook

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-005-001` is not created. Verification duty `TASK-FR-EVD-005-03` (qualification); source `docs/backlog/backlog.csv` record 336, exact block `48418f397b885f4de0bbda4dc655839b20a8fa4637961760438c1e068b8cc115`.

**Original preconditions**

1. a codebook

**Original actions**

1. codes are defined

**Exact source oracles — all required**

1. each code has a stable identity, meaning, and inclusion and exclusion examples
2. the codebook has a version

Legacy same-requirement reuse candidates: `TC-EVD-005-01`, `TC-EVD-005-02`, `TC-AT29`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-005-002 — Adjudicate a coding disagreement

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-005-002` is not created. Verification duty `TASK-FR-EVD-005-03` (qualification); source `docs/backlog/backlog.csv` record 336, exact block `f96eafaca5ec9592767646876daa2f241183075df33633cbe565dfa18b48f7af`.

**Original preconditions**

1. two coders label the same transcript differently

**Original actions**

1. the comparison shows the disagreement and an adjudicator records the final interpretation

**Exact source oracles — all required**

1. both coders' assignments remain
2. the adjudication records its rationale and codebook version

Legacy same-requirement reuse candidates: `TC-EVD-005-01`, `TC-EVD-005-02`, `TC-AT29`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-005-003 — Reject invalid agreement or consensus

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-005-003` is not created. Verification duty `TASK-FR-EVD-005-03` (qualification); source `docs/backlog/backlog.csv` record 336, exact block `a6e5b8d84ac6ddbaac42d779536c76e3aceee4b0ed30f3f1db868ee6ee0e495b`.

**Original preconditions**

1. coded excerpts from two coders

**Original actions**

1. agreement is calculated or consensus is recorded

**Exact source oracles — all required**

1. unmatched units are not used to calculate agreement
2. consensus cannot be claimed by overwriting a coder's work

Legacy same-requirement reuse candidates: `TC-EVD-005-01`, `TC-EVD-005-02`, `TC-AT29`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-005-004 — Reject excerpts losing source restrictions

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-005-004` is not created. Verification duty `TASK-FR-EVD-005-03` (qualification); source `docs/backlog/backlog.csv` record 336, exact block `c373fff2f3d35f9664c9a473fd5542bc33961a27b1d514237bf259b04186ef11`.

**Original preconditions**

1. a restricted source transcript

**Original actions**

1. excerpts and themes are created from it

**Exact source oracles — all required**

1. they inherit the source restrictions

Legacy same-requirement reuse candidates: `TC-EVD-005-01`, `TC-EVD-005-02`, `TC-AT29`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
