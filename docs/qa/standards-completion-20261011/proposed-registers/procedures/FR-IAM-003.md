## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-003-001` / `TC-IMPRANA-FR-IAM-003-001` | `REV_ff15c390bcaca45a65b8734c923dcab630cfc582eedc1e05e3c58bd774afb79a` / `REV_fe73bcea0f5ef243ea9a460154d64b3a467c022ac1a30f1f082907dbe72bcbc0` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-003-002` / `TC-IMPRANA-FR-IAM-003-002` | `REV_9b242553b1e37c356a498b15c69e9ed25c09ec0e8a2e77f340c9b7263ce7d597` / `REV_b1c288f7779d1e51523dd004a91b4af94ac39651e4b3dd4df9970a096af08c92` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-003-003` / `TC-IMPRANA-FR-IAM-003-003` | `REV_2bbb06ec39c9d09902b34d18cdc5e996110b44055e8241f370ef2366c6247765` / `REV_0962fe1246dffc03c402e54ba67b32632c5208f0b61b90d2fe24691a80804c87` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-003-004` / `TC-IMPRANA-FR-IAM-003-004` | `REV_5b3c01e81540d2d08090150b2fff7ca19bed6879597a217b9a10dd7d5a7b6e11` / `REV_a856f2475c4beea2917d000de21cfb07320a7960f4ba1ac2262b3d8b403589a8` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-003-001 — Enrol a passkey

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-003-001` is not created. Verification duty `TASK-FR-IAM-003-03` (qualification); source `docs/backlog/backlog.csv` record 85, exact block `ff15c390bcaca45a65b8734c923dcab630cfc582eedc1e05e3c58bd774afb79a`.

**Original preconditions**

1. an Organisation Administrator has verified their existing identity

**Original actions**

1. they enrol a passkey or approved additional factor

**Exact source oracles — all required**

1. the factor is added to their enrolled assurance
2. the chosen authenticator discloses its device synchronisation behaviour

Legacy same-requirement reuse candidates: `TC-IAM-003-01`, `TC-IAM-003-02`, `SEC-011`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-003-002 — Step up for a sensitive action

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-003-002` is not created. Verification duty `TASK-FR-IAM-003-03` (qualification); source `docs/backlog/backlog.csv` record 85, exact block `9b242553b1e37c356a498b15c69e9ed25c09ec0e8a2e77f340c9b7263ce7d597`.

**Original preconditions**

1. an Organisation Administrator has signed in but not stepped up
2. a reviewed public publication is pending

**Original actions**

1. they attempt the publication
2. they complete a valid challenge within the five minute freshness window

**Exact source oracles — all required**

1. a step up challenge bound to them and to that action is required
2. only the reviewed pending action becomes eligible

Legacy same-requirement reuse candidates: `TC-IAM-003-01`, `TC-IAM-003-02`, `SEC-011`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-003-003 — Reject removing the last privileged factor

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-003-003` is not created. Verification duty `TASK-FR-IAM-003-03` (qualification); source `docs/backlog/backlog.csv` record 85, exact block `2bbb06ec39c9d09902b34d18cdc5e996110b44055e8241f370ef2366c6247765`.

**Original preconditions**

1. a privileged account with one qualifying factor

**Original actions**

1. the member attempts to remove it without verified recovery replacing it

**Exact source oracles — all required**

1. the removal is blocked

Legacy same-requirement reuse candidates: `TC-IAM-003-01`, `TC-IAM-003-02`, `SEC-011`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-003-004 — Reject weak or stale assurance

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-003-004` is not created. Verification duty `TASK-FR-IAM-003-03` (qualification); source `docs/backlog/backlog.csv` record 85, exact block `5b3c01e81540d2d08090150b2fff7ca19bed6879597a217b9a10dd7d5a7b6e11`.

**Original preconditions**

1. a privileged role activation or sensitive action

**Original actions**

1. the only factor presented is SMS, or the step up challenge has expired or is bound to a different action

**Exact source oracles — all required**

1. the activation or action is refused

Legacy same-requirement reuse candidates: `TC-IAM-003-01`, `TC-IAM-003-02`, `SEC-011`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_live_idp.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
