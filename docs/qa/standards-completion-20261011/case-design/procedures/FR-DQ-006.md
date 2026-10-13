## QA v1.3 — source-bound case design (proposed)

Story `FR-DQ-006` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DQ-006-001` / `TC-IMPRANA-FR-DQ-006-001` | `REV_45e2807b5711254602c6c8108e973561a5842d449f0d08a77fccd9ba2dc64fe5` / `REV_b5cf8b6349db6409c9b9fcf57bdc56757d1fc7566d3e1df3000ed3966a4bece6` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-006-002` / `TC-IMPRANA-FR-DQ-006-002` | `REV_d3fe8a63116f28a95be8b46df90fd53e9702175715a3fb14d290d806827947bb` / `REV_6e7f9a68312f0324a6c8e0cc92f8ad08159ca7c2f79fef0b105e25d7df5fb9cc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-006-003` / `TC-IMPRANA-FR-DQ-006-003` | `REV_33ff4e07a86a69d436a8272aa4a53c0ca3f0c949877492ad6293dc6dc88cedf7` / `REV_7fe44149b509994bbc452cbd69f7101c2feae012189df68a6c6ed01606a4454a` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-006-004` / `TC-IMPRANA-FR-DQ-006-004` | `REV_8a001acd11022780e80a1a746b7e458a53fe859dd2d363bcd1d640ee072abadb` / `REV_e529e0462f9922661accc52727398fc0445317d8f85027d31e6847b005adc8a7` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DQ-006-001 — Completeness view distinguishes submission states

Source persona: MEL Manager. Proposed fixture `FIX-FR-DQ-006-001` is not created. Verification duty `TASK-FR-DQ-006-03` (qualification); source `docs/backlog/backlog.csv` record 74, exact block `45e2807b5711254602c6c8108e973561a5842d449f0d08a77fccd9ba2dc64fe5`.

**Original preconditions**

1. a period with an obligation snapshot

**Original actions**

1. a MEL Manager opens the completeness view

**Exact source oracles — all required**

1. it distinguishes expected, received, valid, approved, late and excepted submissions
2. each percentage shows its numerator and denominator
3. lateness uses first valid receipt or approval according to the declared metric

Legacy same-requirement reuse candidates: `TC-DQ-006-01`, `TC-DQ-006-02`, `TC-AT04`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-006-002 — Retired partner keeps its historic obligations

Source persona: MEL Manager. Proposed fixture `FIX-FR-DQ-006-002` is not created. Verification duty `TASK-FR-DQ-006-03` (qualification); source `docs/backlog/backlog.csv` record 74, exact block `d3fe8a63116f28a95be8b46df90fd53e9702175715a3fb14d290d806827947bb`.

**Original preconditions**

1. a partner with a missing June submission

**Original actions**

1. the partner is retired in July

**Exact source oracles — all required**

1. the missing June submission remains counted
2. no August obligation is created for that partner

Legacy same-requirement reuse candidates: `TC-DQ-006-01`, `TC-DQ-006-02`, `TC-AT04`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-006-003 — Reject rewriting older obligation denominators

Source persona: MEL Manager. Proposed fixture `FIX-FR-DQ-006-003` is not created. Verification duty `TASK-FR-DQ-006-03` (qualification); source `docs/backlog/backlog.csv` record 74, exact block `33ff4e07a86a69d436a8272aa4a53c0ca3f0c949877492ad6293dc6dc88cedf7`.

**Original preconditions**

1. past periods with obligation snapshots

**Original actions**

1. current partner membership changes

**Exact source oracles — all required**

1. the older obligation denominators are not rewritten

Legacy same-requirement reuse candidates: `TC-DQ-006-01`, `TC-DQ-006-02`, `TC-AT04`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-006-004 — Reject an unapproved obligation cancellation

Source persona: MEL Manager. Proposed fixture `FIX-FR-DQ-006-004` is not created. Verification duty `TASK-FR-DQ-006-03` (qualification); source `docs/backlog/backlog.csv` record 74, exact block `8a001acd11022780e80a1a746b7e458a53fe859dd2d363bcd1d640ee072abadb`.

**Original preconditions**

1. an obligation in a period

**Original actions**

1. it is cancelled without approved effective dates and a reason

**Exact source oracles — all required**

1. the cancellation is refused

Legacy same-requirement reuse candidates: `TC-DQ-006-01`, `TC-DQ-006-02`, `TC-AT04`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_forms_rounds.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
