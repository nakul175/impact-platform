## QA v1.3 — source-bound case design (proposed)

Story `FR-PRV-008` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-PRV-008-001` / `TC-IMPRANA-FR-PRV-008-001` | `REV_a2c2e83129fe4fc9bef62ba1ebf7cbadaf4cff50a292c09a08783a57b163e6ed` / `REV_6a2ae851aff5b176cd6d95dc80e154a6a5c79d3e985cef4d7f7b553720f066a7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-008-002` / `TC-IMPRANA-FR-PRV-008-002` | `REV_4c81b512591260a8e583ac897fce06d1b73e13833e68cb1060aab0b23e2a1a67` / `REV_5d0a2e8ff1d174631a9710b717583e897215a0dd29cb7645cceb47b0fde1273c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-PRV-008-003` / `TC-IMPRANA-FR-PRV-008-003` | `REV_4e381f50cc4cc17bfa623f122b515204c7d0a31ed2a20d54d9f8ca4b33a517ba` / `REV_82f2e49bec5b213a29a34145046723eacacc560a69d0aa1e6a131b1800a75241` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-PRV-008-001 — Correct a shared dataset

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-008-001` is not created. Verification duty `TASK-FR-PRV-008-03` (qualification); source `docs/backlog/backlog.csv` record 290, exact block `a2c2e83129fe4fc9bef62ba1ebf7cbadaf4cff50a292c09a08783a57b163e6ed`.

**Original preconditions**

1. a dataset with two partner disclosures in the sharing register

**Original actions**

1. the Privacy Officer corrects the dataset

**Exact source oracles — all required**

1. both partner disclosures are identified
2. live access is revoked where required
3. each correction notice outcome is recorded

Legacy same-requirement reuse candidates: `TC-PRV-008-01`, `TC-PRV-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-008-002 — List active disclosures for a source

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-008-002` is not created. Verification duty `TASK-FR-PRV-008-03` (qualification); source `docs/backlog/backlog.csv` record 290, exact block `4c81b512591260a8e583ac897fce06d1b73e13833e68cb1060aab0b23e2a1a67`.

**Original preconditions**

1. disclosures recorded with recipient, purpose, source or artifact version, allowed reuse, expiry and owner

**Original actions**

1. the Privacy Officer selects a source

**Exact source oracles — all required**

1. its active disclosures within authorised scope are listed

Legacy same-requirement reuse candidates: `TC-PRV-008-01`, `TC-PRV-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-PRV-008-003 — Reject asserting external deletion from a notice alone

Source persona: Privacy Officer. Proposed fixture `FIX-FR-PRV-008-003` is not created. Verification duty `TASK-FR-PRV-008-03` (qualification); source `docs/backlog/backlog.csv` record 290, exact block `4e381f50cc4cc17bfa623f122b515204c7d0a31ed2a20d54d9f8ca4b33a517ba`.

**Original preconditions**

1. a withdrawal notice sent to a recipient holding an external copy

**Original actions**

1. the disclosure status is updated

**Exact source oracles — all required**

1. external deletion is not asserted solely because the notice was sent
2. the live platform grant and the retained external copy have separate statuses

Legacy same-requirement reuse candidates: `TC-PRV-008-01`, `TC-PRV-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
