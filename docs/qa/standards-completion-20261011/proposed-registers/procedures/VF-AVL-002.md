## QA v1.3 — source-bound case design (proposed)

Story `VF-AVL-002` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-AVL-002-001` / `TC-IMPRANA-VF-AVL-002-001` | `REV_cb781683ff443605835a19e8b8f14b2b0781ce211afbd2e9314ed2a48918f92d` / `REV_e9c124a4093c4efbdfb7d7381e953502f54b015080aaee3f8ce4771ab30cf3d4` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-AVL-002-002` / `TC-IMPRANA-VF-AVL-002-002` | `REV_9601ee67186863eae08780f9a2d176698c4b650ce9e19c03538979cac018cabd` / `REV_5a0ed688d17bb9dce7467cef54edbe8e36c3de57e14a647e69653a70631cb059` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-AVL-002-003` / `TC-IMPRANA-VF-AVL-002-003` | `REV_1683317eb4746a1d4e37c4d597834b659d2d3e0b2aa01d64c74453706447db7f` / `REV_11ae3abb68633bc2f4e0d2316cdecdf71409fe6db190b2a0c66bef7f36993aa2` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-AVL-002-001 — Core manual workflows continue when an independent dependency fails

Source persona: Data Author. Proposed fixture `FIX-VF-AVL-002-001` is not created. Verification duty `TASK-VF-AVL-002-03` (qualification); source `docs/backlog/backlog.csv` record 110, exact block `cb781683ff443605835a19e8b8f14b2b0781ce211afbd2e9314ed2a48918f92d`.

**Original preconditions**

1. AI, email, the survey connector or BI retrieval has failed independently

**Original actions**

1. a Data Author performs manual entry, deterministic calculations and access to existing approved reports

**Exact source oracles — all required**

1. those core workflows remain available

Legacy same-requirement reuse candidates: `TC-VF-AVL-002`, `TC-AT28`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AVL-002-002 — Affected function, stale data and queued actions are shown

Source persona: Data Author. Proposed fixture `FIX-VF-AVL-002-002` is not created. Verification duty `TASK-VF-AVL-002-03` (qualification); source `docs/backlog/backlog.csv` record 110, exact block `9601ee67186863eae08780f9a2d176698c4b650ce9e19c03538979cac018cabd`.

**Original preconditions**

1. a dependency has failed

**Original actions**

1. a Data Author uses the platform

**Exact source oracles — all required**

1. the affected function is identified
2. stale data and queued actions are labelled

Legacy same-requirement reuse candidates: `TC-VF-AVL-002`, `TC-AT28`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AVL-002-003 — Reject false isolation claims

Source persona: Data Author. Proposed fixture `FIX-VF-AVL-002-003` is not created. Verification duty `TASK-VF-AVL-002-03` (qualification); source `docs/backlog/backlog.csv` record 110, exact block `1683317eb4746a1d4e37c4d597834b659d2d3e0b2aa01d64c74453706447db7f`.

**Original preconditions**

1. a failed dependency that is actually required for the tested journey

**Original actions**

1. isolation results are reported

**Exact source oracles — all required**

1. isolation is not claimed for that journey
2. the dependency is declared and the affected cohort is reported

Legacy same-requirement reuse candidates: `TC-VF-AVL-002`, `TC-AT28`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
