## QA v1.3 — source-bound case design (proposed)

Story `FR-EVD-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-EVD-006-001` / `TC-IMPRANA-FR-EVD-006-001` | `REV_7bb3ac32642ea78606bf288c337fe5536bdd701f4931c5772a53fc1e8aa700da` / `REV_b315d5ec9493fbfa51b4578ee652a837c5e80e71842f55ef8cbe309ed993f587` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-006-002` / `TC-IMPRANA-FR-EVD-006-002` | `REV_517c6487e7ffe610e2a9865fbb7437bf2f46d33f8d9bccc458eda7e7a16dc7b7` / `REV_698b770193fee948869fefb6a407b13c4e02e0e3ca9a4d7bc2c7ddfdc1e11801` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-006-003` / `TC-IMPRANA-FR-EVD-006-003` | `REV_5f33c0434726b2f3694da6a92d1847f2ad5d70c6513ef83e3872cc0b28006da8` / `REV_bda743c7c614600769f0eeb0651ee51a7d17ec8d186d6756552d5f46af2f0047` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-006-004` / `TC-IMPRANA-FR-EVD-006-004` | `REV_4b41e47d2fc117af538ad7b93178bd620a1371836326dd0230b3819ad61dc844` / `REV_cc8b716705a3b79e96d4cd78e88f698ce6036dad87e6b36031bd5531de279400` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-EVD-006-001 — Request a transcript or translation

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-006-001` is not created. Verification duty `TASK-FR-EVD-006-03` (qualification); source `docs/backlog/backlog.csv` record 337, exact block `7bb3ac32642ea78606bf288c337fe5536bdd701f4931c5772a53fc1e8aa700da`.

**Original preconditions**

1. a recording

**Original actions**

1. an Analyst requests processing with an approved destination, language and permitted task

**Exact source oracles — all required**

1. the generated transcript or translation is a new labelled artifact
2. it is linked to offsets in the original recording

Legacy same-requirement reuse candidates: `TC-EVD-006-01`, `TC-EVD-006-02`, `TC-AT29`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-006-002 — Correct a translated segment used in a quotation

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-006-002` is not created. Verification duty `TASK-FR-EVD-006-03` (qualification); source `docs/backlog/backlog.csv` record 337, exact block `517c6487e7ffe610e2a9865fbb7437bf2f46d33f8d9bccc458eda7e7a16dc7b7`.

**Original preconditions**

1. a translated phrase at minute 03:12 is used in a report quotation

**Original actions**

1. the Analyst corrects the phrase

**Exact source oracles — all required**

1. the quotation resolves to the corrected segment and the original recording
2. the original automated output is retained according to policy
3. quotation use requires review of the original meaning

Legacy same-requirement reuse candidates: `TC-EVD-006-01`, `TC-EVD-006-02`, `TC-AT29`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-006-003 — Reject inventing speakers or timings

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-006-003` is not created. Verification duty `TASK-FR-EVD-006-03` (qualification); source `docs/backlog/backlog.csv` record 337, exact block `5f33c0434726b2f3694da6a92d1847f2ad5d70c6513ef83e3872cc0b28006da8`.

**Original preconditions**

1. a segment where the speaker or timing is uncertain

**Original actions**

1. the transcript is generated

**Exact source oracles — all required**

1. the speaker or timing is marked unknown
2. it is not invented

Legacy same-requirement reuse candidates: `TC-EVD-006-01`, `TC-EVD-006-02`, `TC-AT29`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-006-004 — Reject fallback to an unapproved provider

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-006-004` is not created. Verification duty `TASK-FR-EVD-006-03` (qualification); source `docs/backlog/backlog.csv` record 337, exact block `4b41e47d2fc117af538ad7b93178bd620a1371836326dd0230b3819ad61dc844`.

**Original preconditions**

1. a sensitive recording

**Original actions**

1. the approved processing destination is unavailable

**Exact source oracles — all required**

1. processing does not fall back to an unapproved provider

Legacy same-requirement reuse candidates: `TC-EVD-006-01`, `TC-EVD-006-02`, `TC-AT29`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
