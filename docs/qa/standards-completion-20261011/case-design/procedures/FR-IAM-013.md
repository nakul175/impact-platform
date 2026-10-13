## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-013` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-013-001` / `TC-IMPRANA-FR-IAM-013-001` | `REV_7d2b37fb6e5cfdf86b9209065998577e1ec1d0acebde9bf389878e9e1c1a360a` / `REV_fa8ff788c707230687f339bf1295205ea448f85418251e4a8cc312010b7a54d3` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-013-002` / `TC-IMPRANA-FR-IAM-013-002` | `REV_2c06c57df5dc24eed07414227939265c04cb2938dc528150441e73d15a55525d` / `REV_feeb6383031bf40ad99b4b5f0e21709b7a7eb2f9a023ffb47f2ca7ed2af2fbe8` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-013-003` / `TC-IMPRANA-FR-IAM-013-003` | `REV_02dc331a0651284503357fbaaddf30636b15a9ad0927a3864289944a07aff4bd` / `REV_195f41d74929427916f114c120fe2a6ce9569a92519c60d5db9c1c6f6c24a796` | regression → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-013-004` / `TC-IMPRANA-FR-IAM-013-004` | `REV_46b2de096b7e9704ac4fb706aed5dfb8bafce1b539c20cb165d6578d0efbf57c` / `REV_8a041e729342cb918a329cf395f711fcb8ff7f5cb1717e4309072bd10d30ef35` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-013-001 — Change profile preferences

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-013-001` is not created. Verification duty `TASK-FR-IAM-013-03` (qualification); source `docs/backlog/backlog.csv` record 242, exact block `7d2b37fb6e5cfdf86b9209065998577e1ec1d0acebde9bf389878e9e1c1a360a`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a Data Author changes their display name, interface language, reporting preferences, time zone or accessibility choices

**Exact source oracles — all required**

1. a preview shows the resulting date and number display
2. stored values are not changed

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-013-01`, `TC-IAM-013-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-013-002 — Show directory-controlled fields as read only

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-013-002` is not created. Verification duty `TASK-FR-IAM-013-03` (qualification); source `docs/backlog/backlog.csv` record 242, exact block `2c06c57df5dc24eed07414227939265c04cb2938dc528150441e73d15a55525d`.

**Original preconditions**

1. a profile field controlled by the directory

**Original actions**

1. the Data Author views their profile

**Exact source oracles — all required**

1. the field is read only and labelled with its source

Legacy same-requirement reuse candidates: `TC-IAM-013-01`, `TC-IAM-013-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-013-003 — Keep attribution stable

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-013-003` is not created. Verification duty `TASK-FR-IAM-013-03` (qualification); source `docs/backlog/backlog.csv` record 242, exact block `02dc331a0651284503357fbaaddf30636b15a9ad0927a3864289944a07aff4bd`.

**Original preconditions**

1. a member recorded an approval

**Original actions**

1. they change their display name and time zone

**Exact source oracles — all required**

1. the approval still resolves to the same actor and original absolute timestamp

Legacy same-requirement reuse candidates: `TC-IAM-013-01`, `TC-IAM-013-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-013-004 — Reject preferences that suppress notices or override calendars

Source persona: Data Author. Proposed fixture `FIX-FR-IAM-013-004` is not created. Verification duty `TASK-FR-IAM-013-03` (qualification); source `docs/backlog/backlog.csv` record 242, exact block `46b2de096b7e9704ac4fb706aed5dfb8bafce1b539c20cb165d6578d0efbf57c`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a Data Author sets a preference that would suppress mandatory security notices or override the organisation reporting calendar

**Exact source oracles — all required**

1. the preference does not take effect

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-013-01`, `TC-IAM-013-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
