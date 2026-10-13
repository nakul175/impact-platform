## QA v1.3 — source-bound case design (proposed)

Story `VF-AVL-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-AVL-001-001` / `TC-IMPRANA-VF-AVL-001-001` | `REV_dc727283e5b4604d49c88b984677e7369d7ee55972945f0ef5ef9c12b26d73ca` / `REV_70f7071e761bd17ee7b902fcb3f11cc89a4d146283078ae810b60fae9a22b860` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-AVL-001-002` / `TC-IMPRANA-VF-AVL-001-002` | `REV_86f3f46a580909121625f5583caa0c4ec6b5af0ca9497ff82e38509daac2e4fd` / `REV_48fee1a2df7b00118dda228928b5e0e1f9b56c3a32b17aaae2249fca7c0bb88e` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-AVL-001-003` / `TC-IMPRANA-VF-AVL-001-003` | `REV_f19f94bf64f3f368ebb7fd2610a0e1369b34f8a199748c39ba4b7c29f59777bf` / `REV_68f23f0b26ac127ce004232a1cdf56b189694675007c0c27ec930249b453055c` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-AVL-001-001 — Each critical journey meets 99.9 percent monthly availability

Source persona: Data Author. Proposed fixture `FIX-VF-AVL-001-001` is not created. Verification duty `TASK-VF-AVL-001-03` (qualification); source `docs/backlog/backlog.csv` record 109, exact block `dc727283e5b4604d49c88b984677e7369d7ee55972945f0ef5ef9c12b26d73ca`.

**Original preconditions**

1. synthetic journeys for authentication, read, submission, approval and report access

**Original actions**

1. monthly availability is measured

**Exact source oracles — all required**

1. each journey achieves at least 99.9 percent availability for each material tenant cohort

Legacy same-requirement reuse candidates: `TC-VF-AVL-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AVL-001-002 — Planned maintenance counts against the objective

Source persona: Data Author. Proposed fixture `FIX-VF-AVL-001-002` is not created. Verification duty `TASK-VF-AVL-001-03` (qualification); source `docs/backlog/backlog.csv` record 109, exact block `86f3f46a580909121625f5583caa0c4ec6b5af0ca9497ff82e38509daac2e4fd`.

**Original preconditions**

1. planned maintenance or a platform-dependent outage affects a critical journey

**Original actions**

1. monthly bad minutes are calculated

**Exact source oracles — all required**

1. those minutes count against the 99.9 percent internal objective

Legacy same-requirement reuse candidates: `TC-VF-AVL-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AVL-001-003 — Reject a single aggregate availability figure

Source persona: Data Author. Proposed fixture `FIX-VF-AVL-001-003` is not created. Verification duty `TASK-VF-AVL-001-03` (qualification); source `docs/backlog/backlog.csv` record 109, exact block `f19f94bf64f3f368ebb7fd2610a0e1369b34f8a199748c39ba4b7c29f59777bf`.

**Original preconditions**

1. monthly availability results

**Original actions**

1. only a single aggregate availability number is reported

**Exact source oracles — all required**

1. the evidence is rejected as insufficient
2. excluding planned maintenance or platform-dependent outages from bad minutes is rejected

Legacy same-requirement reuse candidates: `TC-VF-AVL-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_status.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
