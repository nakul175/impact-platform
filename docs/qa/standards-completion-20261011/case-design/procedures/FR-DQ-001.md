## QA v1.3 — source-bound case design (proposed)

Story `FR-DQ-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DQ-001-001` / `TC-IMPRANA-FR-DQ-001-001` | `REV_38475510e59bc983b025e7401017e8dcdb09c51b13954f2d8554ee1d43511638` / `REV_b8814e0a92de514d66c47a2d04794edaa4ba511f60f81430f34cef5f6e0b47a9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-001-002` / `TC-IMPRANA-FR-DQ-001-002` | `REV_8fbddf8ae5530ac162c8ce62db009053aa78e25c0642a1efe9c185654fe24c17` / `REV_b7cef04e215353b889d33d02f38a824ba0c874fc62eed952939654d2946b1eda` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-001-003` / `TC-IMPRANA-FR-DQ-001-003` | `REV_e5b0060b6aa52973a2e3600ce0e303a4b70eea2738d3614c75880d3b60b4a39e` / `REV_7058b8990ba415c86bc0e24b87c7e6849e1896541996026de27274c470ce2982` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-001-004` / `TC-IMPRANA-FR-DQ-001-004` | `REV_f5306d6a95550c4f1a3f2874dfb2a0f5724f5226e7fced4875e2a355f3100485` / `REV_d53ef2cc74225b548365df023083f584efbbe0c0cc4639da17f9cc619b43d4a4` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DQ-001-001 — Define and preview a quality rule before activation

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-001-001` is not created. Verification duty `TASK-FR-DQ-001-03` (interface); source `docs/backlog/backlog.csv` record 220, exact block `38475510e59bc983b025e7401017e8dcdb09c51b13954f2d8554ee1d43511638`.

**Original preconditions**

1. a Data Steward in the quality editor

**Original actions**

1. they define a rule with rule type, target fields, scope, severity, owner and effective version
2. they preview it against a permitted sample

**Exact source oracles — all required**

1. the preview reports the failures the rule would raise before the rule is activated

**Separate existing supplemental plan oracle (unapproved)**

1. they preview it against a permitted sample

Legacy same-requirement reuse candidates: `TC-DQ-001-01`, `TC-DQ-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-001-002 — Inspect a failing record for a date cross-field check

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-001-002` is not created. Verification duty `TASK-FR-DQ-001-03` (interface); source `docs/backlog/backlog.csv` record 220, exact block `8fbddf8ae5530ac162c8ce62db009053aa78e25c0642a1efe9c185654fe24c17`.

**Original preconditions**

1. a Data Steward has activated a "visit date after birth date" check

**Original actions**

1. a record has a visit date that is not after its birth date

**Exact source oracles — all required**

1. the failing record shows the exact rule version that failed
2. it shows a safe field message

Legacy same-requirement reuse candidates: `TC-DQ-001-01`, `TC-DQ-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-001-003 — Rule updates apply prospectively

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-001-003` is not created. Verification duty `TASK-FR-DQ-001-03` (interface); source `docs/backlog/backlog.csv` record 220, exact block `e5b0060b6aa52973a2e3600ce0e303a4b70eea2738d3614c75880d3b60b4a39e`.

**Original preconditions**

1. an active quality rule

**Original actions**

1. the Data Steward updates the rule without requesting a reviewed revalidation job

**Exact source oracles — all required**

1. the updated rule applies prospectively only
2. existing records are revalidated only when a reviewed revalidation job is requested

Legacy same-requirement reuse candidates: `TC-DQ-001-01`, `TC-DQ-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-001-004 — Reject a rule reading a field outside its authorised scope

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-001-004` is not created. Verification duty `TASK-FR-DQ-001-03` (interface); source `docs/backlog/backlog.csv` record 220, exact block `f5306d6a95550c4f1a3f2874dfb2a0f5724f5226e7fced4875e2a355f3100485`.

**Original preconditions**

1. a Data Steward defining a quality rule

**Original actions**

1. the rule targets a field outside its authorised processing scope

**Exact source oracles — all required**

1. the system refuses to let the rule read that field

Legacy same-requirement reuse candidates: `TC-DQ-001-01`, `TC-DQ-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
