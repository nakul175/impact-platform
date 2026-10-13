## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-005-001` / `TC-IMPRANA-FR-PRV-005-001` | `REV_3e3b0c92931aac427da7e866a4787cdba38ed06eaaef67ef4f967ee9ddc84353` / `REV_966d7e244bcaf0b9dd2c83dd9b452287654ba035c4cd0b06579b2591a9b3c369` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-005-002` / `TC-IMPRANA-FR-PRV-005-002` | `REV_fc0be95b5a1489025967167e9dc0bc161ab9488b7bc9fc269a52c91584cd54b4` / `REV_fd83a1f1319ff289778db5738e520d98b09a0a47792e025671d15f30c1b1f732` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-005-003` / `TC-IMPRANA-FR-PRV-005-003` | `REV_08bb5368df20a85ae58a47ecbcaf88d8e05a8f9a0a5448e015710b0d284135c9` / `REV_d0e5b9eb6ddd94c477ee4b700355baa468d502d9a527b9e2d3bfc9f1502bc8de` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-005-004` / `TC-IMPRANA-FR-PRV-005-004` | `REV_22db87808f7c824f2980b402176fb67f88ba33599a8f28af343ba830bde5ef63` / `REV_27e0a6b6d18fdedbc9e0168c26323b20da69de51ac9788fa155cb7db50694533` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-005-001 — Delete a participant record with a held attachment

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-005-001` is not created. Verification duty `TASK-FR-PRV-005-04` (qualification); source `docs/backlog/backlog.csv` record 130, exact block `3e3b0c92931aac427da7e866a4787cdba38ed06eaaef67ef4f967ee9ddc84353`.

**Original preconditions**

1. a participant record with one attachment under a hold

**Original actions**

1. a Privacy Officer executes an authorised deletion request

**Exact source oracles — all required**

1. the active data disappears within the target
2. the case explicitly reports the held item and its review date

Legacy same-requirement reuse candidates: `TC-PRV-005-01`, `TC-PRV-005-02`, `TC-AT15`, `SEC-037`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-005-002 — Deletion enumerates copies and records per-store outcomes

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-005-002` is not created. Verification duty `TASK-FR-PRV-005-04` (qualification); source `docs/backlog/backlog.csv` record 130, exact block `fc0be95b5a1489025967167e9dc0bc161ab9488b7bc9fc269a52c91584cd54b4`.

**Original preconditions**

1. an authorised deletion request

**Original actions**

1. it executes

**Exact source oracles — all required**

1. eligible content is first restricted where needed
2. primary records, derivatives, indexes, generated artifacts and disclosures are enumerated
3. each store's outcome, hold, retry and completion time is recorded
4. any anonymisation is verified as a separate transformation

Legacy same-requirement reuse candidates: `TC-PRV-005-01`, `TC-PRV-005-02`, `TC-AT15`, `SEC-037`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-005-003 — Reject completion while accessible copies remain

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-005-003` is not created. Verification duty `TASK-FR-PRV-005-04` (qualification); source `docs/backlog/backlog.csv` record 130, exact block `08bb5368df20a85ae58a47ecbcaf88d8e05a8f9a0a5448e015710b0d284135c9`.

**Original preconditions**

1. a deletion request where an active accessible copy still exists

**Original actions**

1. the handler tries to mark the deletion complete

**Exact source oracles — all required**

1. completion is refused

Legacy same-requirement reuse candidates: `TC-PRV-005-01`, `TC-PRV-005-02`, `TC-AT15`, `SEC-037`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-005-004 — Reject general operational use of held content

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-005-004` is not created. Verification duty `TASK-FR-PRV-005-04` (qualification); source `docs/backlog/backlog.csv` record 130, exact block `22db87808f7c824f2980b402176fb67f88ba33599a8f28af343ba830bde5ef63`.

**Original preconditions**

1. content held for an approved purpose

**Original actions**

1. a user attempts general operational use of it

**Exact source oracles — all required**

1. access is refused because held content is isolated to the approved purpose

Legacy same-requirement reuse candidates: `TC-PRV-005-01`, `TC-PRV-005-02`, `TC-AT15`, `SEC-037`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
