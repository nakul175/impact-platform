## QA v1.3 — source-bound case design (proposed)

Story `FR-DQ-002` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DQ-002-001` / `TC-IMPRANA-FR-DQ-002-001` | `REV_c3169414f6131af5632b384f62d57601162b6480c32e45d77ee1e3512d62046f` / `REV_38057d4d17ddef9fa8da8ba9e1c40727e68c0b470c9f9e6f806b37e09febbed2` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-002-002` / `TC-IMPRANA-FR-DQ-002-002` | `REV_ecf82705b646093d7a0a9aa4569e4e730db6937cfb2c4fe93798f104a4e7f999` / `REV_efb1eadbaabeeb03249bd0b88940ecb4f2fd5036b1bc5a4c7f15ee353c31c24e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-002-003` / `TC-IMPRANA-FR-DQ-002-003` | `REV_c4c32968e65cb343ae3567d998c686c5ca06324a21e64c68d43761459dd3058a` / `REV_41766ae9272a57a189d4186d3ed49f4fa6bf89534fbad059f0b916d862a35702` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-002-004` / `TC-IMPRANA-FR-DQ-002-004` | `REV_90a0fe91f4e7547e8dd19193f0feac213ccfe0550d3c0bf341988e73dd4f2f64` / `REV_e9cf3a21c9f7006c5e66aa3816b04ebc7810350a5412e3a8ba7b2646554e2428` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-002-005` / `TC-IMPRANA-FR-DQ-002-005` | `REV_34c250fe4b63a924bf7b72fa4d23afefcaa918a657d253c8940c072f7571bd51` / `REV_9625df13afd471eb7039d585e8816f462991f316b6acaf21922bdd2bba411a26` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DQ-002-001 — Blocking error stays blocked until corrected

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-002-001` is not created. Verification duty `TASK-FR-DQ-002-03` (qualification); source `docs/backlog/backlog.csv` record 221, exact block `c3169414f6131af5632b384f62d57601162b6480c32e45d77ee1e3512d62046f`.

**Original preconditions**

1. a submission with a blocking duplicate event

**Original actions**

1. a Reviewer attempts to approve it

**Exact source oracles — all required**

1. the approval is blocked
2. it stays blocked until the duplicate is corrected

Legacy same-requirement reuse candidates: `TC-DQ-002-01`, `TC-DQ-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-002-002 — Permitted warning proceeds only with its recorded exception

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-002-002` is not created. Verification duty `TASK-FR-DQ-002-03` (qualification); source `docs/backlog/backlog.csv` record 221, exact block `ecf82705b646093d7a0a9aa4569e4e730db6937cfb2c4fe93798f104a4e7f999`.

**Original preconditions**

1. a submission with a review warning that policy permits to be excepted

**Original actions**

1. an exception request is recorded with the rule, affected revision, reason, authority and expiry

**Exact source oracles — all required**

1. the submission can proceed with that exception recorded
2. it cannot proceed without an explicit disposition of the warning

Legacy same-requirement reuse candidates: `TC-DQ-002-01`, `TC-DQ-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-002-003 — Informational findings do not block

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-002-003` is not created. Verification duty `TASK-FR-DQ-002-03` (qualification); source `docs/backlog/backlog.csv` record 221, exact block `c4c32968e65cb343ae3567d998c686c5ca06324a21e64c68d43761459dd3058a`.

**Original preconditions**

1. a submission with only informational findings

**Original actions**

1. it is progressed

**Exact source oracles — all required**

1. the findings do not block progression

Legacy same-requirement reuse candidates: `TC-DQ-002-01`, `TC-DQ-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-002-004 — Reject dismissing a notification as a resolution

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-002-004` is not created. Verification duty `TASK-FR-DQ-002-03` (qualification); source `docs/backlog/backlog.csv` record 221, exact block `90a0fe91f4e7547e8dd19193f0feac213ccfe0550d3c0bf341988e73dd4f2f64`.

**Original preconditions**

1. a submission with a blocking error or review warning

**Original actions**

1. a user dismisses the notification about it

**Exact source oracles — all required**

1. the underlying issue remains unresolved

Legacy same-requirement reuse candidates: `TC-DQ-002-01`, `TC-DQ-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-002-005 — Reject waiving non-waivable conditions

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-002-005` is not created. Verification duty `TASK-FR-DQ-002-03` (qualification); source `docs/backlog/backlog.csv` record 221, exact block `34c250fe4b63a924bf7b72fa4d23afefcaa918a657d253c8940c072f7571bd51`.

**Original preconditions**

1. a finding caused by a security restriction, an impossible calculation or self approval

**Original actions**

1. an exception is requested for it

**Exact source oracles — all required**

1. the exception is refused

Legacy same-requirement reuse candidates: `TC-DQ-002-01`, `TC-DQ-002-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
