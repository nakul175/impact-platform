## QA v1.3 — source-bound case design (proposed)

Story `FR-OFF-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OFF-008-001` / `TC-IMPRANA-FR-OFF-008-001` | `REV_acd4a274aab230a9722e1667d257ad8ef79c25458de0644a396a41f6659e747b` / `REV_75beeb2d9411f6c8566354865534a550be9e8595269c7adcd18dfff5cfb9b775` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-008-002` / `TC-IMPRANA-FR-OFF-008-002` | `REV_21191465691317da6b6eeb370722ecce9c9f4f0ea65278be9b280605707f7c93` / `REV_971fa9760edd965c65ce32255158927ab31d464e37a07e9e9a6e9e5dee50d2c9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-008-003` / `TC-IMPRANA-FR-OFF-008-003` | `REV_ec4ddee9b577cb21a049269d95151971c800d5618d91497c1e8de8a3176517ad` / `REV_3de99363bac406757baefa8e6d28b581a9ca7795fd6db1b5f31573072e5fa783` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-008-004` / `TC-IMPRANA-FR-OFF-008-004` | `REV_49eea386232170a390ec9500f56a89ca33db4d299aa820795fc06048120b1cd3` / `REV_6a502197bfae0e6be0ab20235921e818b4a76804c5cda719cfb7c21dc5c155d3` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OFF-008-001 — Complete a form on a weak connection

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-008-001` is not created. Verification duty `TASK-FR-OFF-008-03` (qualification); source `docs/backlog/backlog.csv` record 278, exact block `acd4a274aab230a9722e1667d257ad8ef79c25458de0644a396a41f6659e747b`.

**Original preconditions**

1. approved languages, reference lists and form logic were downloaded before departure
2. the connection is under 1 Mbps with intermittent loss

**Original actions**

1. the collector completes a form

**Exact source oracles — all required**

1. the answers persist
2. permitted delayed media upload does not create a false complete submission

Legacy same-requirement reuse candidates: `TC-OFF-008-01`, `TC-OFF-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-008-002 — Manual text-first sync

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-008-002` is not created. Verification duty `TASK-FR-OFF-008-03` (qualification); source `docs/backlog/backlog.csv` record 278, exact block `21191465691317da6b6eeb370722ecce9c9f4f0ea65278be9b280605707f7c93`.

**Original preconditions**

1. policy permits deferred media transfer

**Original actions**

1. the collector syncs manually

**Exact source oracles — all required**

1. text is uploaded first and media transfer is deferred

Legacy same-requirement reuse candidates: `TC-OFF-008-01`, `TC-OFF-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-008-003 — Reject automatic large downloads on constrained connections

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-008-003` is not created. Verification duty `TASK-FR-OFF-008-03` (qualification); source `docs/backlog/backlog.csv` record 278, exact block `ec4ddee9b577cb21a049269d95151971c800d5618d91497c1e8de8a3176517ad`.

**Original preconditions**

1. a constrained connection and large media available for download

**Original actions**

1. the client prepares downloads

**Exact source oracles — all required**

1. large media is not downloaded automatically
2. large downloads require size disclosure and user control

Legacy same-requirement reuse candidates: `TC-OFF-008-01`, `TC-OFF-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-008-004 — Reject online-only logic shown as offline capable

Source persona: Field Data Collector. Proposed fixture `FIX-FR-OFF-008-004` is not created. Verification duty `TASK-FR-OFF-008-03` (qualification); source `docs/backlog/backlog.csv` record 278, exact block `49eea386232170a390ec9500f56a89ca33db4d299aa820795fc06048120b1cd3`.

**Original preconditions**

1. form logic that requires a live external lookup

**Original actions**

1. the form is packaged for offline use

**Exact source oracles — all required**

1. it is labelled online only and not presented as offline capable

Legacy same-requirement reuse candidates: `TC-OFF-008-01`, `TC-OFF-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
