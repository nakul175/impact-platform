## QA v1.3 — source-bound case design (proposed)

Story `US-DC-03` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-DC-03-001` / `TC-IMPRANA-US-DC-03-001` | `REV_017cfb32fa55d983e7b2597856c59988aeef492f7018f1faacbf2a61529755a7` / `REV_1e6ed52f9c1c152a8818a53c4bc3edf5a371a78fc4a51cab3be28ccd72da0e3e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DC-03-002` / `TC-IMPRANA-US-DC-03-002` | `REV_c2d39202da307db3482f6ec17cb22696016be065f7b83702a99f8ca60a2c0916` / `REV_a6f8b55d8b0618199fd478589cc38ee8833fbcf58435a6d7cc410d400c2cfb2d` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DC-03-003` / `TC-IMPRANA-US-DC-03-003` | `REV_1e03ad91bfff19d56abf5ff8008ebbba4372776021866d4077e5a0ed9fb88771` / `REV_1cfab5bd4ca1fa9d607e22cd15a37feaceb1870fc98fcb43a48ab687f53da65a` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-DC-03-001 — Public vetting criteria page

Source persona: Executive Director. Proposed fixture `FIX-US-DC-03-001` is not created. Verification duty `TASK-US-DC-03-03` (qualification); source `docs/backlog/backlog.csv` record 41, exact block `017cfb32fa55d983e7b2597856c59988aeef492f7018f1faacbf2a61529755a7`.

**Original preconditions**

1. the published vetting criteria

**Original actions**

1. anyone opens the criteria page

**Exact source oracles — all required**

1. the vetting criteria are shown

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_solutions_catalog.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DC-03-002 — Status and last-review date on every listing

Source persona: Executive Director. Proposed fixture `FIX-US-DC-03-002` is not created. Verification duty `TASK-US-DC-03-03` (qualification); source `docs/backlog/backlog.csv` record 41, exact block `c2d39202da307db3482f6ec17cb22696016be065f7b83702a99f8ca60a2c0916`.

**Original preconditions**

1. the solution catalogue

**Original actions**

1. the Executive Director views any listing

**Exact source oracles — all required**

1. the listing shows its vetting status and last-review date

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_solutions_catalog.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DC-03-003 — Reject a listing without status or review date

Source persona: Executive Director. Proposed fixture `FIX-US-DC-03-003` is not created. Verification duty `TASK-US-DC-03-03` (qualification); source `docs/backlog/backlog.csv` record 41, exact block `1e03ad91bfff19d56abf5ff8008ebbba4372776021866d4077e5a0ed9fb88771`.

**Original preconditions**

1. a solution listing with no vetting status or no last-review date

**Original actions**

1. it is published to the catalogue

**Exact source oracles — all required**

1. publication is refused

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_solutions_catalog.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
