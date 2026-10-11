## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-004` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-004-001` / `TC-IMPRANA-FR-IAM-004-001` | `REV_979ef7ac1692476b088fcaa10778662cf332a5a9841c9096513576bb738112d7` / `REV_bb36c7b0bc15b7bb9b7552632b5fa960457458b0ff6799d9f22dc945b85ba0c6` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-004-002` / `TC-IMPRANA-FR-IAM-004-002` | `REV_85c32cf0334b1fd22bf693f397061a2bd9702598f4fb3057848aafd9eb9c2a81` / `REV_078dd73330c4bebc68fa457722f83407410b80659d22ab1b36c30e585945ca51` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-004-003` / `TC-IMPRANA-FR-IAM-004-003` | `REV_f79e0fde430c76200dbfcb89d006f360296b41224695f32cf530cbd4b34ca865` / `REV_07ef3ec16590b30eab7803bd8a2ceacbfa53db763baeb762011debe72cd1ba8e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-004-004` / `TC-IMPRANA-FR-IAM-004-004` | `REV_51828078461b474edb862a6a3eacd2d3ac8dbaec24774b87877f88e323a8f713` / `REV_ce15dfa0ea34405679ec9f76730618c7cb3e12a50eac1888cd084afe1afe6762` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-004-001 — Set a local password

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-004-001` is not created. Verification duty `TASK-FR-IAM-004-03` (qualification); source `docs/backlog/backlog.csv` record 238, exact block `979ef7ac1692476b088fcaa10778662cf332a5a9841c9096513576bb738112d7`.

**Original preconditions**

1. a Data Author is setting up a local account

**Original actions**

1. they paste a password from a password manager

**Exact source oracles — all required**

1. the paste is accepted
2. the effective password policy is displayed
3. the password is checked against known compromised values

Legacy same-requirement reuse candidates: `TC-IAM-004-01`, `TC-IAM-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-004-002 — Reset a password

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-004-002` is not created. Verification duty `TASK-FR-IAM-004-03` (qualification); source `docs/backlog/backlog.csv` record 238, exact block `85c32cf0334b1fd22bf693f397061a2bd9702598f4fb3057848aafd9eb9c2a81`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a Data Author requests a password reset
2. they complete a successful reset

**Exact source oracles — all required**

1. a neutral acknowledgement is returned
2. a single use recovery link with a 30 minute expiry is issued
3. prior recovery tokens and sessions are revoked according to policy

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-004-01`, `TC-IAM-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-004-003 — Reject token replay and secret leakage

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-004-003` is not created. Verification duty `TASK-FR-IAM-004-03` (qualification); source `docs/backlog/backlog.csv` record 238, exact block `f79e0fde430c76200dbfcb89d006f360296b41224695f32cf530cbd4b34ca865`.

**Original preconditions**

1. a reset token has already been used

**Original actions**

1. the same token is submitted again

**Exact source oracles — all required**

1. the replay fails
2. after a failed password attempt neither the password nor the token is recoverable from logs or diagnostics

Legacy same-requirement reuse candidates: `TC-IAM-004-01`, `TC-IAM-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-004-004 — Reject account enumeration and unbounded retries

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-004-004` is not created. Verification duty `TASK-FR-IAM-004-03` (qualification); source `docs/backlog/backlog.csv` record 238, exact block `51828078461b474edb862a6a3eacd2d3ac8dbaec24774b87877f88e323a8f713`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a reset is requested for an address that is not registered

**Exact source oracles — all required**

1. the response does not reveal whether the address is registered
2. repeated attempts are subject to bounded retry and abuse controls
3. password text is never exposed to telemetry or normal administrators

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-004-01`, `TC-IAM-004-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
