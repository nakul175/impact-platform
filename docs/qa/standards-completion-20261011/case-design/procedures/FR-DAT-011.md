## QA v1.3 — source-bound case design (proposed)

Story `FR-DAT-011` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DAT-011-001` / `TC-IMPRANA-FR-DAT-011-001` | `REV_faa1fc9ff13b0715cddaa0d052ff7e115ec10531b7a5fbde92b02103c0af7cf2` / `REV_9d9ae0363c4ee4359851f6e84ad36ef60233973c9b2ecfc4d344c26f6d23973e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-011-002` / `TC-IMPRANA-FR-DAT-011-002` | `REV_2ec9f9d8eef0c84cbca9b6d90631a937e8f19a49899b5a224941720a0d1b013e` / `REV_c48a12af1ee00754b8282c3f30d685ac3157ddbc397f6989a99f1c42b33ece8d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DAT-011-003` / `TC-IMPRANA-FR-DAT-011-003` | `REV_6f30d8c0992909cdc1d263df484899f995e70e6c57dbd1c3c37236389b46d6e4` / `REV_ceafce4557513575e1a4f0910ede3b72bb4576ea1cf290851e3fa83a9dd11eae` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DAT-011-001 — Export includes semantic metadata

Source persona: Analyst. Proposed fixture `FIX-FR-DAT-011-001` is not created. Verification duty `TASK-FR-DAT-011-03` (qualification); source `docs/backlog/backlog.csv` record 218, exact block `faa1fc9ff13b0715cddaa0d052ff7e115ec10531b7a5fbde92b02103c0af7cf2`.

**Original preconditions**

1. authorised rows and fields are selected

**Original actions**

1. the Analyst exports them

**Exact source oracles — all required**

1. the export includes stable IDs, type dictionary, code lists, units, time zone, source versions and value states
2. large exports follow job and revocation controls

Legacy same-requirement reuse candidates: `TC-DAT-011-01`, `TC-DAT-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-011-002 — Formula-like text and leading-zero IDs are safe

Source persona: Analyst. Proposed fixture `FIX-FR-DAT-011-002` is not created. Verification duty `TASK-FR-DAT-011-03` (qualification); source `docs/backlog/backlog.csv` record 218, exact block `2ec9f9d8eef0c84cbca9b6d90631a937e8f19a49899b5a224941720a0d1b013e`.

**Original preconditions**

1. data containing text beginning with an equals sign and a leading-zero ID

**Original actions**

1. the exported file is opened

**Exact source oracles — all required**

1. no formula executes
2. the ID remains text
3. the safe export encoding is documented

Legacy same-requirement reuse candidates: `TC-DAT-011-01`, `TC-DAT-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DAT-011-003 — Reject leaking unselected or private data

Source persona: Analyst. Proposed fixture `FIX-FR-DAT-011-003` is not created. Verification duty `TASK-FR-DAT-011-03` (qualification); source `docs/backlog/backlog.csv` record 218, exact block `6f30d8c0992909cdc1d263df484899f995e70e6c57dbd1c3c37236389b46d6e4`.

**Original preconditions**

1. an export of selected columns

**Original actions**

1. the file and its metadata are inspected

**Exact source oracles — all required**

1. no hidden unselected columns or private raw values are present
2. formula-like text is neutralised without silently changing its represented meaning

Legacy same-requirement reuse candidates: `TC-DAT-011-01`, `TC-DAT-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
