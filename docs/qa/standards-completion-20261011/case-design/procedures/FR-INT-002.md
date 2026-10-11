## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-002-001` / `TC-IMPRANA-FR-INT-002-001` | `REV_76aaebc8bd45867bac817299abfcf6da48e36b3de1ebc87ac03d3fa29a920078` / `REV_d73e87bd731cd30860c476196e4362c21d025c9f7b415b332d410d8d444670ca` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-002-002` / `TC-IMPRANA-FR-INT-002-002` | `REV_10d4858f476da1e36e5ebb876b6ba9c9467382b59e5fac18f8a34ee30687a7b9` / `REV_7b75d94be9f81f254577a66e9e7deccc2bdaefae8b4a15f957d3c0a248a13f03` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-002-003` / `TC-IMPRANA-FR-INT-002-003` | `REV_b08f25413ad99b44efd52148dd729739824cf502aa31ca969c561bcfa9b79618` / `REV_457b471caebc36466ac728f98f0c94f7404c29168639ec0bc53a8d3c25fa4243` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-002-001 — Set up and activate a connection

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-002-001` is not created. Verification duty `TASK-FR-INT-002-03` (qualification); source `docs/backlog/backlog.csv` record 102, exact block `76aaebc8bd45867bac817299abfcf6da48e36b3de1ebc87ac03d3fa29a920078`.

**Original preconditions**

1. the Data Steward is the connection owner

**Original actions**

1. they enter credentials through the protected flow, select a bounded scope and test the connection

**Exact source oracles — all required**

1. the test uses a minimal sample and displays safe identity and permission results
2. activation records expiry, cadence, mapping and a responsible backup owner

Legacy same-requirement reuse candidates: `TC-INT-002-01`, `TC-INT-002-02`, `TC-AT14`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-002-002 — Reject continuing a queued run after revocation

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-002-002` is not created. Verification duty `TASK-FR-INT-002-03` (qualification); source `docs/backlog/backlog.csv` record 102, exact block `10d4858f476da1e36e5ebb876b6ba9c9467382b59e5fac18f8a34ee30687a7b9`.

**Original preconditions**

1. a run is queued

**Original actions**

1. upstream authorisation is revoked

**Exact source oracles — all required**

1. the run reports credential unavailable
2. it does not continue under another person's token or any hidden fallback account
3. future jobs stop and the old credentials are invalidated

Legacy same-requirement reuse candidates: `TC-INT-002-01`, `TC-INT-002-02`, `TC-AT14`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-002-003 — Reject reading back stored secrets

Source persona: Data Steward. Proposed fixture `FIX-FR-INT-002-003` is not created. Verification duty `TASK-FR-INT-002-03` (qualification); source `docs/backlog/backlog.csv` record 102, exact block `b08f25413ad99b44efd52148dd729739824cf502aa31ca969c561bcfa9b79618`.

**Original preconditions**

1. credentials have been entered for a connection

**Original actions**

1. anyone attempts to view them

**Exact source oracles — all required**

1. the secrets are not displayed

Legacy same-requirement reuse candidates: `TC-INT-002-01`, `TC-INT-002-02`, `TC-AT14`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
