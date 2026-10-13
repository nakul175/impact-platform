## QA v1.3 — source-bound case design (proposed)

Story `FR-IAM-011` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-IAM-011-001` / `TC-IMPRANA-FR-IAM-011-001` | `REV_5755c1660546635ab56a8aa52385805ad60cefee31dea97894c22bcb203c77dd` / `REV_ca3cd2b91544cd733c3a01b24b60b4bdf5bb553bdf482a6258cb3e152eb259f8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-011-002` / `TC-IMPRANA-FR-IAM-011-002` | `REV_72a596e6447400d4f2242de07a70c2a65ecd69af119ac160c79baad85ba14640` / `REV_561725be9b2c5dd4576fa232acf2ac4f8b4ae284eddb9d5848213f105ecdceb1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-011-003` / `TC-IMPRANA-FR-IAM-011-003` | `REV_7a420985008d1e23c24c0bd8f1705b1e8cb5062ef4d48967d58bac07f940fe5c` / `REV_97d661b3eabce0e160acc62cec1a8feb3b3fb82421ea883ffbc941d96e4d87fc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-011-004` / `TC-IMPRANA-FR-IAM-011-004` | `REV_d445bd2d5ed64a8d2128b8e1238e5c5c1344413464c4fa331b75d02c94aca514` / `REV_bcf1bab6696cc683691fa4368a6b18d15451ba22dd88b6dbece8e00aeb98366d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-IAM-011-005` / `TC-IMPRANA-FR-IAM-011-005` | `REV_bc75da9ece0b36a7e16ec3df11f60738a0afcc6612a49b0a4bea0a47f9dcb093` / `REV_de06944106308a250799fdfdf7146a3dd8eb70c37896ba68a3dd9df11d0670d0` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-IAM-011-001 — Start an access review

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-011-001` is not created. Verification duty `TASK-FR-IAM-011-03` (qualification); source `docs/backlog/backlog.csv` record 346, exact block `5755c1660546635ab56a8aa52385805ad60cefee31dea97894c22bcb203c77dd`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. the Organisation Administrator starts an access review for selected scopes and a snapshot date

**Exact source oracles — all required**

1. reviewers see each grant's subject, source of grant, sensitive capabilities, expiry, owner and last relevant activity

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-011-01`, `TC-IAM-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-011-002 — Decide each grant

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-011-002` is not created. Verification duty `TASK-FR-IAM-011-03` (qualification); source `docs/backlog/backlog.csv` record 346, exact block `72a596e6447400d4f2242de07a70c2a65ecd69af119ac160c79baad85ba14640`.

**Original preconditions**

(Absent in original source; unresolved context is recorded separately.)

**Original actions**

1. a reviewer retains, narrows or revokes a grant

**Exact source oracles — all required**

1. a reason is recorded
2. unreviewed grants remain flagged overdue

**Separate proposed missing context (unapproved)**

1. given

Legacy same-requirement reuse candidates: `TC-IAM-011-01`, `TC-IAM-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-011-003 — Review a service identity whose owner has left

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-011-003` is not created. Verification duty `TASK-FR-IAM-011-03` (qualification); source `docs/backlog/backlog.csv` record 346, exact block `7a420985008d1e23c24c0bd8f1705b1e8cb5062ef4d48967d58bac07f940fe5c`.

**Original preconditions**

1. a service identity whose owner has left

**Original actions**

1. the reviewer assigns a new owner or revokes it

**Exact source oracles — all required**

1. the review decision and execution receipt are retained

Legacy same-requirement reuse candidates: `TC-IAM-011-01`, `TC-IAM-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-011-004 — Reject exposure of protected record content

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-011-004` is not created. Verification duty `TASK-FR-IAM-011-03` (qualification); source `docs/backlog/backlog.csv` record 346, exact block `d445bd2d5ed64a8d2128b8e1238e5c5c1344413464c4fa331b75d02c94aca514`.

**Original preconditions**

1. a reviewer is performing an access review

**Original actions**

1. they inspect a grant

**Exact source oracles — all required**

1. they see entitlement metadata only and no protected record content

Legacy same-requirement reuse candidates: `TC-IAM-011-01`, `TC-IAM-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-IAM-011-005 — Reject stale review execution

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-IAM-011-005` is not created. Verification duty `TASK-FR-IAM-011-03` (qualification); source `docs/backlog/backlog.csv` record 346, exact block `bc75da9ece0b36a7e16ec3df11f60738a0afcc6612a49b0a4bea0a47f9dcb093`.

**Original preconditions**

1. a grant was replaced after the review decision was made

**Original actions**

1. the revocation decision is executed

**Exact source oracles — all required**

1. the current grant revision is rechecked
2. the unrelated replacement grant is not revoked

Legacy same-requirement reuse candidates: `TC-IAM-011-01`, `TC-IAM-011-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
