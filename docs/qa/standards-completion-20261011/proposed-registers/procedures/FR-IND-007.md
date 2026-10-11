## QA v1.3 — source-bound case design (proposed)

Story `FR-IND-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IND-007-001` / `TC-IMPRANA-FR-IND-007-001` | `REV_0cec4222d55e12d62737ebc67dd7a4c2da261659d92f377fbea706d722d97195` / `REV_c12f9a7d68237d883285d03e39f0df7548923dc75bd0837431e04eca4929b06d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-007-002` / `TC-IMPRANA-FR-IND-007-002` | `REV_8e58ffaf550f52b2b23f3042d4061e953e7218c06ca49b80335735604c8fa39a` / `REV_b58018dcf7cdf57f33c608606103619823a8d0155dda925a90d2ee9faf10172e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-007-003` / `TC-IMPRANA-FR-IND-007-003` | `REV_275ac4bf2fcf8e4dc7cdd4275d22280be5733a9ff4cd3ea4843c085de468ff75` / `REV_7ad3dfe4b2038a03e1392c5ebe9fe43839bdb31f1acd4a68cab7c96604f69284` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IND-007-004` / `TC-IMPRANA-FR-IND-007-004` | `REV_0193cd4514b74d6baa9f4a4ef17db4709e738e722346335db127e89ec4594df7` / `REV_65d9357d85f59cadce2cec7fb199171d55fb780410b712f6e84664884ab0e409` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IND-007-001 — Record a reason for a non-numeric state

Source persona: Data Author. Proposed fixture `FIX-FR-IND-007-001` is not created. Verification duty `TASK-FR-IND-007-03` (qualification); source `docs/backlog/backlog.csv` record 97, exact block `0cec4222d55e12d62737ebc67dd7a4c2da261659d92f377fbea706d722d97195`.

**Original preconditions**

1. a Data Author entering or importing a value

**Original actions**

1. they mark it not collected or not applicable

**Exact source oracles — all required**

1. they must choose a reason
2. the value state is stored separately from numeric value, workflow status and disclosure status
3. eligibility rules govern whether it is removed from the denominator

Legacy same-requirement reuse candidates: `TC-IND-007-01`, `TC-IND-007-02`, `TC-AT09`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-007-002 — Export distinct value states

Source persona: Data Author. Proposed fixture `FIX-FR-IND-007-002` is not created. Verification duty `TASK-FR-IND-007-03` (qualification); source `docs/backlog/backlog.csv` record 97, exact block `8e58ffaf550f52b2b23f3042d4061e953e7218c06ca49b80335735604c8fa39a`.

**Original preconditions**

1. rows that are zero, missing, not applicable, invalid and pending

**Original actions**

1. they are exported

**Exact source oracles — all required**

1. each has a distinct machine code and matching human label
2. views apply the value state matrix in section 4.2

Legacy same-requirement reuse candidates: `TC-IND-007-01`, `TC-IND-007-02`, `TC-AT09`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-007-003 — Reject blanks as zero

Source persona: Data Author. Proposed fixture `FIX-FR-IND-007-003` is not created. Verification duty `TASK-FR-IND-007-03` (qualification); source `docs/backlog/backlog.csv` record 97, exact block `275ac4bf2fcf8e4dc7cdd4275d22280be5733a9ff4cd3ea4843c085de468ff75`.

**Original preconditions**

1. a blank cell in entry or import

**Original actions**

1. it is saved

**Exact source oracles — all required**

1. it does not become zero

Legacy same-requirement reuse candidates: `TC-IND-007-01`, `TC-IND-007-02`, `TC-AT09`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IND-007-004 — Reject suppressed or pending values in results

Source persona: Data Author. Proposed fixture `FIX-FR-IND-007-004` is not created. Verification duty `TASK-FR-IND-007-03` (qualification); source `docs/backlog/backlog.csv` record 97, exact block `0193cd4514b74d6baa9f4a4ef17db4709e738e722346335db127e89ec4594df7`.

**Original preconditions**

1. a suppressed value and a value pending approval

**Original actions**

1. results are disclosed and official totals computed

**Exact source oracles — all required**

1. the suppressed numeric payload is removed from the disclosed result
2. the pending value is excluded from official totals

Legacy same-requirement reuse candidates: `TC-IND-007-01`, `TC-IND-007-02`, `TC-AT09`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_measurement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
