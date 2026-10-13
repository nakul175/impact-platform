## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-009` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-009-001` / `TC-IMPRANA-FR-RPT-009-001` | `REV_062480a3951a33f011bf05e301879bae9329454649943313062b46a741bfbafe` / `REV_b1a5747fcdd8643586b4fb285a588080efe557c0f87fecb664b3e6350c3d1a44` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-009-002` / `TC-IMPRANA-FR-RPT-009-002` | `REV_ce48ce3922ee92dba4216b03d2c6f14025963451be6e07ac67982f9f1b7b967f` / `REV_6baa472fc22f1d6a12d207b1119cab210c004cfa8129a757f7fe57c041366fe9` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-009-003` / `TC-IMPRANA-FR-RPT-009-003` | `REV_706916b659cb6052c3461b09143a838e65325b3ded8322ecf2f53f10f07c5107` / `REV_c20d1a5111bf693079920c4341952e405ebbd4222afacd5613ad87166698617c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-009-004` / `TC-IMPRANA-FR-RPT-009-004` | `REV_450b2f27024599e715ce8c8c4fad50597d9c4cccf039a08d9f79ca935d17e0ed` / `REV_aae6068db3ea0c00666b7fa4c79ffdaeab379ce076d05b7c44e65811b33d8904` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-009-001 — Supersede report v1 with v2

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-009-001` is not created. Verification duty `TASK-FR-RPT-009-03` (qualification); source `docs/backlog/backlog.csv` record 141, exact block `062480a3951a33f011bf05e301879bae9329454649943313062b46a741bfbafe`.

**Original preconditions**

1. report v1 has been published and distributed
2. a separately approved replacement v2 exists

**Original actions**

1. the MEL Manager supersedes v1 with v2

**Exact source oracles — all required**

1. old links to v1 expose only the permitted supersession status
2. the distribution log identifies the v1 recipients

Legacy same-requirement reuse candidates: `TC-RPT-009-01`, `TC-RPT-009-02`, `TC-AT07`, `SEC-020`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-009-002 — Withdraw a published report

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-009-002` is not created. Verification duty `TASK-FR-RPT-009-03` (qualification); source `docs/backlog/backlog.csv` record 141, exact block `ce48ce3922ee92dba4216b03d2c6f14025963451be6e07ac67982f9f1b7b967f`.

**Original preconditions**

1. a published report

**Original actions**

1. the MEL Manager withdraws it with a reason, authority and impact review

**Exact source oracles — all required**

1. the live publication becomes unavailable or displays an approved withdrawal notice without protected content

Legacy same-requirement reuse candidates: `TC-RPT-009-01`, `TC-RPT-009-02`, `TC-AT07`, `SEC-020`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-009-003 — Reject withdrawal without reason or authority

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-009-003` is not created. Verification duty `TASK-FR-RPT-009-03` (qualification); source `docs/backlog/backlog.csv` record 141, exact block `706916b659cb6052c3461b09143a838e65325b3ded8322ecf2f53f10f07c5107`.

**Original preconditions**

1. a published report

**Original actions**

1. a user attempts to withdraw it without a reason, current authority or impact review

**Exact source oracles — all required**

1. the withdrawal is refused

Legacy same-requirement reuse candidates: `TC-RPT-009-01`, `TC-RPT-009-02`, `TC-AT07`, `SEC-020`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-009-004 — Reject claims of recalling downloaded copies

Source persona: MEL Manager. Proposed fixture `FIX-FR-RPT-009-004` is not created. Verification duty `TASK-FR-RPT-009-03` (qualification); source `docs/backlog/backlog.csv` record 141, exact block `450b2f27024599e715ce8c8c4fad50597d9c4cccf039a08d9f79ca935d17e0ed`.

**Original preconditions**

1. recipients have already downloaded v1

**Original actions**

1. v1 is withdrawn or superseded

**Exact source oracles — all required**

1. the downloaded copies remain recorded as external disclosures
2. notices refer to the obsolete version and corrective action
3. the system never claims recall of already downloaded bytes

Legacy same-requirement reuse candidates: `TC-RPT-009-01`, `TC-RPT-009-02`, `TC-AT07`, `SEC-020`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
