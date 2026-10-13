## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-007-001` / `TC-IMPRANA-FR-OPS-007-001` | `REV_b377a6d5cddd3945842651463b6c04e80bdbed44a1cff902d0a9b25598a56717` / `REV_ee78af53fc10ce46cd186c7bbf8ff5d4be0979875c5b9a1d93bacb99dca1939e` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-007-002` / `TC-IMPRANA-FR-OPS-007-002` | `REV_d381f988f7862b9b353d1c6a27ad0b6f3ac9443ec0b47751de6c647f5cdb5c72` / `REV_4ce0713378c7e7808c64437b4ba00374d017eb3b65aaa6b85e30b9c62e976a29` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-007-003` / `TC-IMPRANA-FR-OPS-007-003` | `REV_8f6991697538926695ca7d25c30895fd12a071a22cdf86df6e47d0e9174048a7` / `REV_1d9205846f8332d263af8ba0d19bd6444c5f2816aee5c129ab441c5e764d57ba` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-007-004` / `TC-IMPRANA-FR-OPS-007-004` | `REV_8e5a368fa7809882d188d822e54c7501077c0f6d3c4f7c18c43fef9d75906fb7` / `REV_9be70d33493671406920612139046ee2b3edee509ffff0d72f000c399088f11c` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-007-001 — Failed release keeps accepted submissions

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-007-001` is not created. Verification duty `TASK-FR-OPS-007-03` (qualification); source `docs/backlog/backlog.csv` record 164, exact block `b377a6d5cddd3945842651463b6c04e80bdbed44a1cff902d0a9b25598a56717`.

**Original preconditions**

1. valid submissions were accepted under a new release

**Original actions**

1. the release fails

**Exact source oracles — all required**

1. expansion stops
2. the rehearsed recovery path executes
3. the accepted submissions remain accounted for under the recovery plan

Legacy same-requirement reuse candidates: `TC-OPS-007-01`, `TC-OPS-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-007-002 — Controlled exposure is recorded

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-007-002` is not created. Verification duty `TASK-FR-OPS-007-03` (qualification); source `docs/backlog/backlog.csv` record 164, exact block `d381f988f7862b9b353d1c6a27ad0b6f3ac9443ec0b47751de6c647f5cdb5c72`.

**Original preconditions**

1. release preparation has validated compatibility, data migration, required gates and the rollback or roll-forward path

**Original actions**

1. the release is exposed to a cohort

**Exact source oracles — all required**

1. the cohort and feature configuration are recorded

Legacy same-requirement reuse candidates: `TC-OPS-007-01`, `TC-OPS-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-007-003 — Reject rollback that discards writes or reverts deletions

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-007-003` is not created. Verification duty `TASK-FR-OPS-007-03` (qualification); source `docs/backlog/backlog.csv` record 164, exact block `8f6991697538926695ca7d25c30895fd12a071a22cdf86df6e47d0e9174048a7`.

**Original preconditions**

1. accepted writes and a completed privacy deletion since the last release

**Original actions**

1. rollback executes

**Exact source oracles — all required**

1. no accepted write is silently discarded
2. the privacy deletion is not reverted

Legacy same-requirement reuse candidates: `TC-OPS-007-01`, `TC-OPS-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-007-004 — Reject irreversible migration without forward recovery

Source persona: Platform Operator. Proposed fixture `FIX-FR-OPS-007-004` is not created. Verification duty `TASK-FR-OPS-007-03` (qualification); source `docs/backlog/backlog.csv` record 164, exact block `8e5a368fa7809882d188d822e54c7501077c0f6d3c4f7c18c43fef9d75906fb7`.

**Original preconditions**

1. a release containing an irreversible migration

**Original actions**

1. it has no approved forward recovery procedure

**Exact source oracles — all required**

1. release preparation fails

Legacy same-requirement reuse candidates: `TC-OPS-007-01`, `TC-OPS-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
