## QA v1.3 — source-bound case design (proposed)

Story `VF-PER-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-PER-003-001` / `TC-IMPRANA-VF-PER-003-001` | `REV_0e4ded64c323030695e7d4655bce211f9bdf02df626754abfa713216f493b6d3` / `REV_04d6846168ce779aee7f350432f85d2dbc8a93bbe7fae28da3c084ccec2c6c21` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-003-002` / `TC-IMPRANA-VF-PER-003-002` | `REV_66683cb885ce4f7da6c79080ce716c693adf8e2a6a77d4428b354724aeb43f3b` / `REV_3166ec119e081ba76e35656b0c45be54e1d8a08c0572fd90ef1fa3e5c5d3a4db` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-003-003` / `TC-IMPRANA-VF-PER-003-003` | `REV_7ef5fd0a3952611c31421b08b9e67b87a47ae9e2433d672c9d04ec3de74bed2c` / `REV_a778a7fc2410c49d0bba6310cb12be7c154037fad1c60a8c8fec6c2368a7006d` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-VF-PER-003-004` / `TC-IMPRANA-VF-PER-003-004` | `REV_c0942ecc522dce7ab18b2686563844491fd78b6858aa8105f834e1c1c1419d9d` / `REV_bbf0f4488c6bf0960ab094aa3a28e485de0adf30b691aa323398ca95dffa783b` | native → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-PER-003-001 — Search meets response targets

Source persona: Data Author. Proposed fixture `FIX-VF-PER-003-001` is not created. Verification duty `TASK-VF-PER-003-02` (qualification); source `docs/backlog/backlog.csv` record 267, exact block `0e4ded64c323030695e7d4655bce211f9bdf02df626754abfa713216f493b6d3`.

**Original preconditions**

1. a synthetic corpus under the standard profile

**Original actions**

1. permission-filtered metadata and indexed document searches retrieve the first 50 permitted results

**Exact source oracles — all required**

1. results return at p95 within 3 seconds and p99 within 8 seconds
2. timing covers the complete first usable page including policy filtering

Legacy same-requirement reuse candidates: `TC-VF-PER-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-003-002 — Restricted, multilingual and empty searches stay confidential

Source persona: Data Author. Proposed fixture `FIX-VF-PER-003-002` is not created. Verification duty `TASK-VF-PER-003-02` (qualification); source `docs/backlog/backlog.csv` record 267, exact block `66683cb885ce4f7da6c79080ce716c693adf8e2a6a77d4428b354724aeb43f3b`.

**Original preconditions**

1. restricted, multilingual and empty-result queries

**Original actions**

1. counts, suggestions and snippets are inspected

**Exact source oracles — all required**

1. no hidden marker appears

Legacy same-requirement reuse candidates: `TC-VF-PER-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-003-003 — Reject permission leakage regardless of latency

Source persona: Data Author. Proposed fixture `FIX-VF-PER-003-003` is not created. Verification duty `TASK-VF-PER-003-02` (qualification); source `docs/backlog/backlog.csv` record 267, exact block `7ef5fd0a3952611c31421b08b9e67b87a47ae9e2433d672c9d04ec3de74bed2c`.

**Original preconditions**

1. a search that meets its latency targets

**Original actions**

1. any count, suggestion or snippet reveals a hidden marker

**Exact source oracles — all required**

1. the verification fails

Legacy same-requirement reuse candidates: `TC-VF-PER-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-PER-003-004 — Reject searches outside the bound

Source persona: Data Author. Proposed fixture `FIX-VF-PER-003-004` is not created. Verification duty `TASK-VF-PER-003-02` (qualification); source `docs/backlog/backlog.csv` record 267, exact block `c0942ecc522dce7ab18b2686563844491fd78b6858aa8105f834e1c1c1419d9d`.

**Original preconditions**

1. the measured results including policy filtering

**Original actions**

1. p95 exceeds 3 seconds or p99 exceeds 8 seconds

**Exact source oracles — all required**

1. the verification fails

Legacy same-requirement reuse candidates: `TC-VF-PER-003`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
