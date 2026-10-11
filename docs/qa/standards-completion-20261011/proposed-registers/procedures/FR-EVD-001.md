## QA v1.3 — source-bound case design (proposed)

Story `FR-EVD-001` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-EVD-001-001` / `TC-IMPRANA-FR-EVD-001-001` | `REV_344479beaf7eb679f41d4f3a485f3f1bf1e4fdc6346f401a6e17ea1f13c46c1e` / `REV_758af10d24d165c541e4848d0fce3b09fa85af5db0f00759f5e92092ef54df77` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-001-002` / `TC-IMPRANA-FR-EVD-001-002` | `REV_429e45c0dbfef5bdd3e6dba6012acda89e4391090e294f9246a04f831bd08e09` / `REV_62c655db2e199d822c8fb52e5032fb9b5d787f8d8d6b707947d79d7660c3f720` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-001-003` / `TC-IMPRANA-FR-EVD-001-003` | `REV_862c318f27dc5f79503437c42e1308b52fbc987fcdd2d8c9e369039e9735b0c2` / `REV_55bd6b402888ca3afc319da176198cd51528b9551fea27873d8c874392a72e9f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-001-004` / `TC-IMPRANA-FR-EVD-001-004` | `REV_6bd85ddb922908bb1b9031854c277fe32140e425805758a4fa78e467bad7dd79` / `REV_c49cbc84652059001dc3fbbf7b640ac21e7c002481c37cbbf151154b7d2de30a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-001-005` / `TC-IMPRANA-FR-EVD-001-005` | `REV_f3cf2ae53e56b92f210ae188f44e6d295aba6d3830f4fbaf2eecf90eb9002283` / `REV_3098a70ae8bac6cb1ca8c3f56ca19940dfe8cbd889339be5bed95bf3f4f4b719` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-EVD-001-001 — Upload evidence with metadata and safety status

Source persona: MEL Manager. Proposed fixture `FIX-FR-EVD-001-001` is not created. Verification duty `TASK-FR-EVD-001-03` (qualification); source `docs/backlog/backlog.csv` record 75, exact block `344479beaf7eb679f41d4f3a485f3f1bf1e4fdc6346f401a6e17ea1f13c46c1e`.

**Original preconditions**

1. a user uploading evidence

**Original actions**

1. they provide type, source, date, owner, sensitivity and retention

**Exact source oracles — all required**

1. the evidence is stored and receives a safety status

Legacy same-requirement reuse candidates: `TC-EVD-001-01`, `TC-EVD-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_evidence.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-001-002 — Earlier citation stays on its version

Source persona: MEL Manager. Proposed fixture `FIX-FR-EVD-001-002` is not created. Verification duty `TASK-FR-EVD-001-03` (qualification); source `docs/backlog/backlog.csv` record 75, exact block `429e45c0dbfef5bdd3e6dba6012acda89e4391090e294f9246a04f831bd08e09`.

**Original preconditions**

1. version 1 of a survey is linked to an achievement

**Original actions**

1. version 2 of the survey is uploaded

**Exact source oracles — all required**

1. the earlier achievement still cites version 1

Legacy same-requirement reuse candidates: `TC-EVD-001-01`, `TC-EVD-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_evidence.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-001-003 — Search exposes only authorised evidence

Source persona: MEL Manager. Proposed fixture `FIX-FR-EVD-001-003` is not created. Verification duty `TASK-FR-EVD-001-03` (qualification); source `docs/backlog/backlog.csv` record 75, exact block `862c318f27dc5f79503437c42e1308b52fbc987fcdd2d8c9e369039e9735b0c2`.

**Original preconditions**

1. evidence with different permissions in the repository

**Original actions**

1. a user searches the repository

**Exact source oracles — all required**

1. only authorised metadata and content are exposed

Legacy same-requirement reuse candidates: `TC-EVD-001-01`, `TC-EVD-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_evidence.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-001-004 — Reject overwriting a published citation

Source persona: MEL Manager. Proposed fixture `FIX-FR-EVD-001-004` is not created. Verification duty `TASK-FR-EVD-001-03` (qualification); source `docs/backlog/backlog.csv` record 75, exact block `6bd85ddb922908bb1b9031854c277fe32140e425805758a4fa78e467bad7dd79`.

**Original preconditions**

1. a file cited by a published result

**Original actions**

1. the file is replaced

**Exact source oracles — all required**

1. a new version is created
2. the published citation is never overwritten

Legacy same-requirement reuse candidates: `TC-EVD-001-01`, `TC-EVD-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_evidence.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-001-005 — Reject presenting a source URL as archived

Source persona: MEL Manager. Proposed fixture `FIX-FR-EVD-001-005` is not created. Verification duty `TASK-FR-EVD-001-03` (qualification); source `docs/backlog/backlog.csv` record 75, exact block `f3cf2ae53e56b92f210ae188f44e6d295aba6d3830f4fbaf2eecf90eb9002283`.

**Original preconditions**

1. evidence recorded as a source URL

**Original actions**

1. it is displayed

**Exact source oracles — all required**

1. it is shown as an external reference with its last checked status
2. it is not presented as an archived guarantee

Legacy same-requirement reuse candidates: `TC-EVD-001-01`, `TC-EVD-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_evidence.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
