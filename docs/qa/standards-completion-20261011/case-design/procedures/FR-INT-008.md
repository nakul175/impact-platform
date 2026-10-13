## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-008` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-008-001` / `TC-IMPRANA-FR-INT-008-001` | `REV_500256eece662813cbd3cd795a71e247323700a98aa89ccfcd48c1f8152a371d` / `REV_633361bc85b754f6aea8055ce36a3878d0db42aed17b14b8898ce59662752774` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-008-002` / `TC-IMPRANA-FR-INT-008-002` | `REV_39f7541aea83b66ce57c94ff26f4d7df7ab1bce6a48099c2a65b327e4e282baa` / `REV_6736127baddc49ac476755ff324b6207da029c28b7fcf25b3773afcdf187a94a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-008-003` / `TC-IMPRANA-FR-INT-008-003` | `REV_c2d7b0988c9b18ac74d831b06bca35728c3349e23315da8f3799ea601a0f92fb` / `REV_ab9cc43ebeb261e7d15e9317f166fe727bd48c8c8921714de03b3e86185be372` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-008-001 — Exchange mapping declares the standard and its conventions

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-008-001` is not created. Verification duty `TASK-FR-INT-008-03` (qualification); source `docs/backlog/backlog.csv` record 348, exact block `500256eece662813cbd3cd795a71e247323700a98aa89ccfcd48c1f8152a371d`.

**Original preconditions**

1. an exchange mapping for a sector standard

**Original actions**

1. the Data Steward reviews it

**Exact source oracles — all required**

1. it identifies the standard version, code lists, units, locale, date representation and information loss

Legacy same-requirement reuse candidates: `TC-INT-008-01`, `TC-INT-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-008-002 — Multilingual record round trips with a manifest

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-008-002` is not created. Verification duty `TASK-FR-INT-008-03` (qualification); source `docs/backlog/backlog.csv` record 348, exact block `39f7541aea83b66ce57c94ff26f4d7df7ab1bce6a48099c2a65b327e4e282baa`.

**Original preconditions**

1. a multilingual record containing currency, unit and geography codes

**Original actions**

1. it is exported and imported again through the exchange mapping

**Exact source oracles — all required**

1. import and export both validate against the mapping
2. a manifest accounts for every intentionally transformed or unsupported field
3. codes remain stable and separate from display translations

Legacy same-requirement reuse candidates: `TC-INT-008-01`, `TC-INT-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-008-003 — Reject unknown codes

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-008-003` is not created. Verification duty `TASK-FR-INT-008-03` (qualification); source `docs/backlog/backlog.csv` record 348, exact block `c2d7b0988c9b18ac74d831b06bca35728c3349e23315da8f3799ea601a0f92fb`.

**Original preconditions**

1. an import containing a code that is not in the mapping's code lists

**Original actions**

1. the import is validated

**Exact source oracles — all required**

1. the code is quarantined or rejected
2. it is not automatically matched to a similar label

Legacy same-requirement reuse candidates: `TC-INT-008-01`, `TC-INT-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
