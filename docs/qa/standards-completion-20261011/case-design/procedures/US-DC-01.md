## QA v1.3 — source-bound case design (proposed)

Story `US-DC-01` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-DC-01-001` / `TC-IMPRANA-US-DC-01-001` | `REV_3143d799d3354a919aab032d91705d7a3c82e209df1f5a11ec3a0365b78ffcf3` / `REV_9acd3b268c14674cd8c8ea4d3b92a8b8ddb25bfae4eb2b0edf1a49d090d16357` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DC-01-002` / `TC-IMPRANA-US-DC-01-002` | `REV_0debbb4122971bf0e3b99c376d67141bb58300c68e82b9de663713a2c4c5eb06` / `REV_bfb45002e238cf08cfdcaaef5296b64eca9bac02dfb56f46a3673dfa3b40db29` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DC-01-003` / `TC-IMPRANA-US-DC-01-003` | `REV_123c2cacad1c8b457121e663cfe630525399390c8dfebd669b2c95c15d903e36` / `REV_c08e9e472f6f0982b88ba1e3eb972d509ea718b5a4c0f1ab1ff5e40c157b8d00` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-DC-01-001 — Default view shows at most 3 options

Source persona: Executive Director. Proposed fixture `FIX-US-DC-01-001` is not created. Verification duty `TASK-US-DC-01-03` (qualification); source `docs/backlog/backlog.csv` record 39, exact block `3143d799d3354a919aab032d91705d7a3c82e209df1f5a11ec3a0365b78ffcf3`.

**Original preconditions**

1. an opportunity with more than 3 vetted options

**Original actions**

1. the Executive Director opens the opportunity

**Exact source oracles — all required**

1. at most 3 options are shown

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_solutions_catalog.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DC-01-002 — More options only on request

Source persona: Executive Director. Proposed fixture `FIX-US-DC-01-002` is not created. Verification duty `TASK-US-DC-01-03` (qualification); source `docs/backlog/backlog.csv` record 39, exact block `0debbb4122971bf0e3b99c376d67141bb58300c68e82b9de663713a2c4c5eb06`.

**Original preconditions**

1. the default view of an opportunity with more than 3 vetted options

**Original actions**

1. the Executive Director asks to see more options

**Exact source oracles — all required**

1. the remaining vetted options are shown

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_solutions_catalog.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DC-01-003 — Reject more than 3 options by default

Source persona: Executive Director. Proposed fixture `FIX-US-DC-01-003` is not created. Verification duty `TASK-US-DC-01-03` (qualification); source `docs/backlog/backlog.csv` record 39, exact block `123c2cacad1c8b457121e663cfe630525399390c8dfebd669b2c95c15d903e36`.

**Original preconditions**

1. an opportunity with more than 3 vetted options

**Original actions**

1. the default view loads without a request for more

**Exact source oracles — all required**

1. no more than 3 options are shown
2. no unvetted option is shown

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_solutions_catalog.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
