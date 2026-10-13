## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-005-001` / `TC-IMPRANA-FR-SEC-005-001` | `REV_99e7799669adb6aff3fd257424543bd0f9c47f7a0a8f9c8427ff5801d5287e0f` / `REV_232d5c52f777627d7891f3022bc3f89ffa1d11037575af0ccf24fafd06d0cbd7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-005-002` / `TC-IMPRANA-FR-SEC-005-002` | `REV_8652d0f21af5a98e669881ace8a58f8ea7d7db4ca5d76bf80066e1633e1e8800` / `REV_60eb439ccb3bc9499e9ee2c59bb31d779c3dba7d28a36ae8298addf6032d5e1c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-005-003` / `TC-IMPRANA-FR-SEC-005-003` | `REV_45c62a46c98ed7e4d51eed29d0a814408bac96696918992386d2302c11757f9c` / `REV_1485895425fbaea1576532512e038099203d9d82744da927d5cc54b8efd3a72c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-005-004` / `TC-IMPRANA-FR-SEC-005-004` | `REV_0f3aa048ad69db74e9bda561b063ecfd0029bbbfd104f9205d94b1237ad0832f` / `REV_881bb81f394f856f11afe16623a15d445e6969f44c16c8d47b22bbdae8db02ca` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-005-001 — Files are quarantined until checks complete

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-005-001` is not created. Verification duty `TASK-FR-SEC-005-03` (qualification); source `docs/backlog/backlog.csv` record 151, exact block `99e7799669adb6aff3fd257424543bd0f9c47f7a0a8f9c8427ff5801d5287e0f`.

**Original preconditions**

1. a received file

**Original actions**

1. it is processed

**Exact source oracles — all required**

1. its actual content type, size, expansion limits and permitted processing are identified
2. it remains quarantined until checks complete
3. previews execute no active content

Legacy same-requirement reuse candidates: `TC-SEC-005-01`, `TC-SEC-005-02`, `SEC-014`, `SEC-015`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-005-002 — Hostile uploads are blocked

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-005-002` is not created. Verification duty `TASK-FR-SEC-005-03` (qualification); source `docs/backlog/backlog.csv` record 151, exact block `8652d0f21af5a98e669881ace8a58f8ea7d7db4ca5d76bf80066e1633e1e8800`.

**Original preconditions**

1. a misleading extension, a malicious document and an archive expansion fixture

**Original actions**

1. each is uploaded

**Exact source oracles — all required**

1. none reaches normal preview
2. none satisfies mandatory evidence requirements

Legacy same-requirement reuse candidates: `TC-SEC-005-01`, `TC-SEC-005-02`, `SEC-014`, `SEC-015`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-005-003 — External fetches are validated

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-005-003` is not created. Verification duty `TASK-FR-SEC-005-03` (qualification); source `docs/backlog/backlog.csv` record 151, exact block `45c62a46c98ed7e4d51eed29d0a814408bac96696918992386d2302c11757f9c`.

**Original preconditions**

1. an external fetch

**Original actions**

1. it is requested

**Exact source oracles — all required**

1. the destination is validated before the request and after redirects

Legacy same-requirement reuse candidates: `TC-SEC-005-01`, `TC-SEC-005-02`, `SEC-014`, `SEC-015`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-005-004 — Reject excluded and unscannable files

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-005-004` is not created. Verification duty `TASK-FR-SEC-005-03` (qualification); source `docs/backlog/backlog.csv` record 151, exact block `0f3aa048ad69db74e9bda561b063ecfd0029bbbfd104f9205d94b1237ad0832f`.

**Original preconditions**

1. an executable, a macro enabled document or a password protected unscannable file in R1

**Original actions**

1. it is uploaded

**Exact source oracles — all required**

1. executables and macro enabled documents are rejected
2. password protected unscannable files remain quarantined or are rejected
3. archives are accepted only under a specifically qualified bounded profile

Legacy same-requirement reuse candidates: `TC-SEC-005-01`, `TC-SEC-005-02`, `SEC-014`, `SEC-015`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
