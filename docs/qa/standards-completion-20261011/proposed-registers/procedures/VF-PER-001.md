## QA v1.3 — source-bound case design (proposed)

Story `VF-PER-001` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PER-001-001` / `TC-IMPRANA-VF-PER-001-001` | `REV_af0185b75affcbd4e9ae3aafbbc8799d7608a31295e018a22d5c4aeae9167733` / `REV_e2effbab78450bdbbe12f12368f025b2cc3e1f05af179f2cfd8d6a89fc91197d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-001-002` / `TC-IMPRANA-VF-PER-001-002` | `REV_46ea9cda98d12d3e0b01058224ad2078b4d71c1f162fb715590a10d8ca8da3ce` / `REV_497220572c9a34a093a8daa61d17c4af109934c6b62c9c45a6a225334135a395` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-001-003` / `TC-IMPRANA-VF-PER-001-003` | `REV_cdaa1586e4a2af99270bc6dfd250b443bae8436dc73d1fb9d5b1abdc2151799d` / `REV_096a6c60cba9931fb6b243522eceba4cd05ec02502c996d47313dbe5edc9055c` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PER-001-001 — Interactive actions meet response targets

Source persona: Data Author. Proposed fixture `FIX-VF-PER-001-001` is not created. Verification duty `TASK-VF-PER-001-03` (qualification); source `docs/backlog/backlog.csv` record 114, exact block `af0185b75affcbd4e9ae3aafbbc8799d7608a31295e018a22d5c4aeae9167733`.

**Original preconditions**

1. the standard workload with concurrent background work
2. action start, usable response and durable confirmation are instrumented separately for reads, 100-row lists, saves and approvals

**Original actions**

1. the complete peak and soak profile is run

**Exact source oracles — all required**

1. each action class completes at p95 within 2 seconds and p99 within 5 seconds from user action to usable confirmed response
2. per-tenant p95, p99, timeout and error counts are reported

Legacy same-requirement reuse candidates: `TC-VF-PER-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-001-002 — Long jobs are excluded only when asynchronous

Source persona: Data Author. Proposed fixture `FIX-VF-PER-001-002` is not created. Verification duty `TASK-VF-PER-001-03` (qualification); source `docs/backlog/backlog.csv` record 114, exact block `46ea9cda98d12d3e0b01058224ad2078b4d71c1f162fb715590a10d8ca8da3ce`.

**Original preconditions**

1. a long job

**Original actions**

1. it is excluded from the interactive targets

**Exact source oracles — all required**

1. it is explicitly routed asynchronously

Legacy same-requirement reuse candidates: `TC-VF-PER-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-001-003 — Reject any action class or tenant cohort outside its bound

Source persona: Data Author. Proposed fixture `FIX-VF-PER-001-003` is not created. Verification duty `TASK-VF-PER-001-03` (qualification); source `docs/backlog/backlog.csv` record 114, exact block `cdaa1586e4a2af99270bc6dfd250b443bae8436dc73d1fb9d5b1abdc2151799d`.

**Original preconditions**

1. the measured results

**Original actions**

1. any action class or material tenant cohort exceeds p95 2 seconds or p99 5 seconds

**Exact source oracles — all required**

1. the verification fails
2. fast reads are not combined with slow approvals to hide a failure

Legacy same-requirement reuse candidates: `TC-VF-PER-001`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_native_concurrency.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
