## QA v1.3 — source-bound case design (proposed)

Story `FR-UX-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-UX-006-001` / `TC-IMPRANA-FR-UX-006-001` | `REV_00d4871f3053f6af5cb71537d95ce68400901d1d6c8d0cff70d27f026c83206f` / `REV_46b7e33e0ae21c4ca2e079a74c452dbab7f3335cd951928b42b433cabe25813d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-006-002` / `TC-IMPRANA-FR-UX-006-002` | `REV_bc9a69a40735eacd9d4b446833ab4eb7ee0793c959fd21d663c06a14ebca9ed0` / `REV_7becf7ea0bbf9ca9ee224a94894bcb79aadc513550dcffa236dd9508db7c718a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-006-003` / `TC-IMPRANA-FR-UX-006-003` | `REV_d35d3840c964ffcaf64307b33a8c0fba433bdacb20769df0f36072368dcfdb22` / `REV_623dfbe90ba60056e988254d26d55374309088a56da86d911ba21e3091c745c6` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-UX-006-004` / `TC-IMPRANA-FR-UX-006-004` | `REV_bde46c12695716594c22cde721a97afdccb59e34a978828f605377ce4007812d` / `REV_89905faa0cffb41c4a5e825ae6a60cd01e64dcc653eb54f548988aaafe99c725` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-UX-006-001 — Decimal-comma value survives locale changes

Source persona: Data Author. Proposed fixture `FIX-FR-UX-006-001` is not created. Verification duty `TASK-FR-UX-006-03` (qualification); source `docs/backlog/backlog.csv` record 173, exact block `00d4871f3053f6af5cb71537d95ce68400901d1d6c8d0cff70d27f026c83206f`.

**Original preconditions**

1. an import of 1,25 under a decimal-comma locale

**Original actions**

1. it is viewed in a decimal-point locale and then exported

**Exact source oracles — all required**

1. the underlying value stays 1.25

Legacy same-requirement reuse candidates: `TC-UX-006-01`, `TC-UX-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-006-002 — Unicode content survives export and search

Source persona: Data Author. Proposed fixture `FIX-FR-UX-006-002` is not created. Verification duty `TASK-FR-UX-006-03` (qualification); source `docs/backlog/backlog.csv` record 173, exact block `bc9a69a40735eacd9d4b446833ab4eb7ee0793c959fd21d663c06a14ebca9ed0`.

**Original preconditions**

1. Unicode labels, names and codes

**Original actions**

1. they are exported and searched

**Exact source oracles — all required**

1. they are preserved unchanged

Legacy same-requirement reuse candidates: `TC-UX-006-01`, `TC-UX-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-006-003 — Reject ambiguous imports without explicit handling

Source persona: Data Author. Proposed fixture `FIX-FR-UX-006-003` is not created. Verification duty `TASK-FR-UX-006-03` (qualification); source `docs/backlog/backlog.csv` record 173, exact block `d35d3840c964ffcaf64307b33a8c0fba433bdacb20769df0f36072368dcfdb22`.

**Original preconditions**

1. an import with ambiguous date or decimal formats

**Original actions**

1. no explicit handling has been chosen

**Exact source oracles — all required**

1. the import does not proceed

Legacy same-requirement reuse candidates: `TC-UX-006-01`, `TC-UX-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-UX-006-004 — Reject recalculation on display language change

Source persona: Data Author. Proposed fixture `FIX-FR-UX-006-004` is not created. Verification duty `TASK-FR-UX-006-03` (qualification); source `docs/backlog/backlog.csv` record 173, exact block `bde46c12695716594c22cde721a97afdccb59e34a978828f605377ce4007812d`.

**Original preconditions**

1. recorded dates, amounts and period membership

**Original actions**

1. the Data Author changes display language

**Exact source oracles — all required**

1. none of them is recalculated
2. stable codes remain separate from translated labels

Legacy same-requirement reuse candidates: `TC-UX-006-01`, `TC-UX-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
