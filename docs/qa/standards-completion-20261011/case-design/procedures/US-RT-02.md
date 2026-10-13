## QA v1.3 — source-bound case design (proposed)

Story `US-RT-02` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-RT-02-001` / `TC-IMPRANA-US-RT-02-001` | `REV_94c05c04b74a74dc644a11151e0bb58a1193d8b4e02bd89f7732adad8e0d266f` / `REV_b508ec295f276520b31b220ee3e7945095787b9ac8f28bc26c47c007756114b6` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-US-RT-02-002` / `TC-IMPRANA-US-RT-02-002` | `REV_a5629343ea142fb8854d92355002a6c3b405da11cf1381001e993b7a68b6b712` / `REV_646ad2b22b18fa8a62be139c5644295548fdcef103ee4b543e69166743a30916` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-US-RT-02-003` / `TC-IMPRANA-US-RT-02-003` | `REV_e2c9b1e8273f3debde0831e18fcee04ef099422cdbe9d4160cfbc029fb9e89a5` / `REV_37ee7a3806a536f4cd8a1bd74a1ed886efd08ba7b5a62f9f8b4fd14648e4f1f7` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-RT-02-001 — Tag the current state

Source persona: Product Owner. Proposed fixture `FIX-US-RT-02-001` is not created. Verification duty `TASK-US-RT-02-03` (qualification); source `docs/backlog/backlog.csv` record 5, exact block `94c05c04b74a74dc644a11151e0bb58a1193d8b4e02bd89f7732adad8e0d266f`.

**Original preconditions**

1. the last Impact Platform commit

**Original actions**

1. the Product Owner checks the repository tags

**Exact source oracles — all required**

1. a tag marks that commit

Original proposed anchors (file/artifact candidates only): `scripts/package_source.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-RT-02-002 — Rename and rebrand as Imprana Commons

Source persona: Product Owner. Proposed fixture `FIX-US-RT-02-002` is not created. Verification duty `TASK-US-RT-02-03` (qualification); source `docs/backlog/backlog.csv` record 5, exact block `a5629343ea142fb8854d92355002a6c3b405da11cf1381001e993b7a68b6b712`.

**Original preconditions**

1. the repository has been renamed

**Original actions**

1. someone opens the old repository URL

**Exact source oracles — all required**

1. they are redirected to the renamed repository
2. the interface, README and docs say Imprana Commons

Original proposed anchors (file/artifact candidates only): `scripts/package_source.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-RT-02-003 — Reject an incomplete rebrand

Source persona: Product Owner. Proposed fixture `FIX-US-RT-02-003` is not created. Verification duty `TASK-US-RT-02-03` (qualification); source `docs/backlog/backlog.csv` record 5, exact block `e2c9b1e8273f3debde0831e18fcee04ef099422cdbe9d4160cfbc029fb9e89a5`.

**Original preconditions**

1. the rename and rebrand are done

**Original actions**

1. the old URL does not redirect, or the interface, README or docs still present the product as Impact Platform

**Exact source oracles — all required**

1. the rebrand is not accepted

Original proposed anchors (file/artifact candidates only): `scripts/package_source.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
