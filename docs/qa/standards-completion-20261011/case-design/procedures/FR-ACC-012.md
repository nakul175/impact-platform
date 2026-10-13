## QA v1.3 — source-bound case design (proposed)

Story `FR-ACC-012` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ACC-012-001` / `TC-IMPRANA-FR-ACC-012-001` | `REV_4a69991e832316acd4171d3914c889762ace036969a6b085fa70ddb72b53d422` / `REV_c9096fcbffb530ab1522844437b5b1a7c2c87e475fa1d6fd4db145721c9755df` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-012-002` / `TC-IMPRANA-FR-ACC-012-002` | `REV_b473cb85566346667b46095eac46d1108d4774fe17cea9422c8d33ae8de56c79` / `REV_4f7bd131cd4787f783adca533b094858c5eff7db2e7570d965943a125e6665c7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-012-003` / `TC-IMPRANA-FR-ACC-012-003` | `REV_9bab601d6b76691eaa0c7a88a966707bba22a64e15ca483ab1eb6ed0789a5b25` / `REV_bd8d1a3c8264265c18ab975ad20dc4a8b369c9a774b56f55f1b83c4a37aa2026` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ACC-012-004` / `TC-IMPRANA-FR-ACC-012-004` | `REV_72cf53d5dcaac605fd358a39fa86d517d2253451eae2d04e7286224a54002727` / `REV_0ed4cd5de04ec178467fd188f06eed602ea22fb87beccc15011f9201ccaa9e7e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ACC-012-001 — Simulate an access change

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-012-001` is not created. Verification duty `TASK-FR-ACC-012-03` (qualification); source `docs/backlog/backlog.csv` record 323, exact block `4a69991e832316acd4171d3914c889762ace036969a6b085fa70ddb72b53d422`.

**Original preconditions**

1. an Organisation Administrator drafts an access change and chooses representative subjects

**Original actions**

1. they preview it

**Exact source oracles — all required**

1. gained and lost capabilities, affected restricted classes, links and schedules are calculated

Legacy same-requirement reuse candidates: `TC-ACC-012-01`, `TC-ACC-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-012-002 — Approve a sensitive expansion

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-012-002` is not created. Verification duty `TASK-FR-ACC-012-03` (qualification); source `docs/backlog/backlog.csv` record 323, exact block `b473cb85566346667b46095eac46d1108d4774fe17cea9422c8d33ae8de56c79`.

**Original preconditions**

1. the change expands sensitive access

**Original actions**

1. it is executed

**Exact source oracles — all required**

1. a second eligible Reviewer must approve it
2. a current policy comparison is made at execution

Legacy same-requirement reuse candidates: `TC-ACC-012-01`, `TC-ACC-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-012-003 — Reject execution on a stale preview

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-012-003` is not created. Verification duty `TASK-FR-ACC-012-03` (qualification); source `docs/backlog/backlog.csv` record 323, exact block `9bab601d6b76691eaa0c7a88a966707bba22a64e15ca483ab1eb6ed0789a5b25`.

**Original preconditions**

1. an Organisation Administrator previewed expanding a group to a new programme

**Original actions**

1. the group's membership changes before execution

**Exact source oracles — all required**

1. execution requires a fresh preview

Legacy same-requirement reuse candidates: `TC-ACC-012-01`, `TC-ACC-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ACC-012-004 — Reject simulation side effects or overexposure

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-ACC-012-004` is not created. Verification duty `TASK-FR-ACC-012-03` (qualification); source `docs/backlog/backlog.csv` record 323, exact block `72cf53d5dcaac605fd358a39fa86d517d2253451eae2d04e7286224a54002727`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator runs a simulation

**Exact source oracles — all required**

1. nothing is changed
2. no data beyond their review scope is revealed, with counts or redacted scope labels used only when permitted

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-ACC-012-01`, `TC-ACC-012-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
