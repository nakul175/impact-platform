## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-009` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-009-001` / `TC-IMPRANA-FR-INT-009-001` | `REV_59b8c9366762b59b204c3f30377fac016de443aa72f29c21423b404c2b9c1419` / `REV_09a00dd403a7f1508b81ac8c8410421909ca583198c2f75f3b18638dbcb48324` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-009-002` / `TC-IMPRANA-FR-INT-009-002` | `REV_45751540be51c28ae372225952a6d1c4eac4d7b420d84359158f361904c4e7dd` / `REV_373346d700f904091e6f7804eecaaadfd1b66f6a044ea473a1e8a4f3f4151346` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-009-003` / `TC-IMPRANA-FR-INT-009-003` | `REV_5dc723eee808fcb1c1a9e6c5c99ef611637f0d19913f12df536ee4e47d7c7ad3` / `REV_1b9516276349b914c9e396246b46c79bcc18edf0a77b822db6163da15c2028fa` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-009-004` / `TC-IMPRANA-FR-INT-009-004` | `REV_b8d3d585722b760f53ac65d4a3e022f4cf9ab2daf49015c384c06ed00c3e999c` / `REV_c9e66cffb8aa46f73067739431fb589644e64056b650d0ef90de29a67117a5fd` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-009-001 — Connection health is displayed

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-009-001` is not created. Verification duty `TASK-FR-INT-009-03` (qualification); source `docs/backlog/backlog.csv` record 251, exact block `59b8c9366762b59b204c3f30377fac016de443aa72f29c21423b404c2b9c1419`.

**Original preconditions**

1. a connected integration

**Original actions**

1. the Data Steward opens its connection health

**Exact source oracles — all required**

1. it shows last contact, last successful validated run, backlog, source drift and per item counts
2. error details use safe field references and correlation IDs

Legacy same-requirement reuse candidates: `TC-INT-009-01`, `TC-INT-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-009-002 — Fix a renamed column and replay only failed records

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-009-002` is not created. Verification duty `TASK-FR-INT-009-03` (qualification); source `docs/backlog/backlog.csv` record 251, exact block `45751540be51c28ae372225952a6d1c4eac4d7b420d84359158f361904c4e7dd`.

**Original preconditions**

1. a run that failed because a source column was renamed

**Original actions**

1. the Data Steward diagnoses the drift, publishes the mapping fix and replays the failures

**Exact source oracles — all required**

1. only the failed records are replayed
2. the original failure manifest is retained

Legacy same-requirement reuse candidates: `TC-INT-009-01`, `TC-INT-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-009-003 — Reject unsafe diagnostic exposure

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-009-003` is not created. Verification duty `TASK-FR-INT-009-03` (qualification); source `docs/backlog/backlog.csv` record 251, exact block `5dc723eee808fcb1c1a9e6c5c99ef611637f0d19913f12df536ee4e47d7c7ad3`.

**Original preconditions**

1. a failed integration run

**Original actions**

1. a user views its diagnostics

**Exact source oracles — all required**

1. tokens, unrestricted raw payloads and other tenants' source identities are never displayed
2. a bounded diagnostic sample is shown only to a user with appropriate content rights

Legacy same-requirement reuse candidates: `TC-INT-009-01`, `TC-INT-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-009-004 — Reject retry without the resolving mapping version

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-009-004` is not created. Verification duty `TASK-FR-INT-009-03` (qualification); source `docs/backlog/backlog.csv` record 251, exact block `b8d3d585722b760f53ac65d4a3e022f4cf9ab2daf49015c384c06ed00c3e999c`.

**Original preconditions**

1. failed records awaiting retry

**Original actions**

1. a retry is requested without the reviewed mapping version that resolved the issue

**Exact source oracles — all required**

1. the retry is refused

Legacy same-requirement reuse candidates: `TC-INT-009-01`, `TC-INT-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
