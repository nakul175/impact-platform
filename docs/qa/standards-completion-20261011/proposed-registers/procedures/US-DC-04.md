## QA v1.3 — source-bound case design (proposed)

Story `US-DC-04` · 2 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-DC-04-001` / `TC-IMPRANA-US-DC-04-001` | `REV_986229fbfd6a0427a215e226d57cf948d1109957cd9b8685728519d9f53d9892` / `REV_36fbf00aed57265934a173dc07c25a457990d0d8a2060bf149ddec3f0300c1b2` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DC-04-002` / `TC-IMPRANA-US-DC-04-002` | `REV_f19596546250bd32b534c0be500610e8e02293faf24d72c6ebbde82ce81c4f5d` / `REV_06741e45860a0df431487429f478a90a28a121c34bab90447b15d25a178c7cc3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-DC-04-001 — Disclosure label on every listing

Source persona: Executive Director. Proposed fixture `FIX-US-DC-04-001` is not created. Verification duty `TASK-US-DC-04-03` (qualification); source `docs/backlog/backlog.csv` record 42, exact block `986229fbfd6a0427a215e226d57cf948d1109957cd9b8685728519d9f53d9892`.

**Original preconditions**

1. any solution listing

**Original actions**

1. the Executive Director views it

**Exact source oracles — all required**

1. it carries a disclosure label stating any commercial relationship with the solution

**Inspected source assertion candidates — not verified binding**

- `qualification/test_ai_solutions_catalog.py::test_every_listing_carries_a_valid_commercial_disclosure` lines 200–222: Checks actual disclosure fields for every catalogue item; candidate for the source requirement that each listing carries its commercial disclosure. Gap: Does not by itself prove the Executive Director browser viewing path or all live publication paths. Editorial confirmation and actual independent review remain unestablished.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DC-04-002 — Reject a listing without a disclosure label

Source persona: Executive Director. Proposed fixture `FIX-US-DC-04-002` is not created. Verification duty `TASK-US-DC-04-03` (qualification); source `docs/backlog/backlog.csv` record 42, exact block `f19596546250bd32b534c0be500610e8e02293faf24d72c6ebbde82ce81c4f5d`.

**Original preconditions**

1. a solution listing with no disclosure label

**Original actions**

1. it is published to the catalogue

**Exact source oracles — all required**

1. publication is refused

**Inspected source assertion candidates — not verified binding**

- `qualification/test_ai_solutions_catalog.py::test_a_listing_without_a_valid_disclosure_fails_validation_and_the_catalogue_is_not_served` lines 294–317: Exercises invalid/missing disclosure validation and refusal to serve the altered catalogue; candidate for refusing a listing without disclosure. Gap: Requires inspection of all current publication paths and authentic current run evidence.
- `qualification/test_ai_solutions_catalog.py::test_a_new_listing_built_without_a_disclosure_is_never_given_one_by_default` lines 336–354: Missing commercial disclosure is not silently defaulted for a new listing. Gap: A source assertion about construction is not a complete catalogue-publication workflow binding.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
