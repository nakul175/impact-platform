## QA v1.3 — source-bound case design (proposed)

Story `FR-FIN-001` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FIN-001-001` / `TC-IMPRANA-FR-FIN-001-001` | `REV_dabe3a226ee87f093ad2e78262b3207e547509624e332f83eecad37ee996fa26` / `REV_ed054a8a4974dbd8ff99084e92bba08f4f733c8820d79a5b85d1d10816e4ace4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-001-002` / `TC-IMPRANA-FR-FIN-001-002` | `REV_fbc9f60ae8a1d9b57b0bbb248adfc3b88d6144aa865366ff0d9de19dd0f5c01c` / `REV_382cef463fcf9e8e6efd5629281d8feb441ff32895d7a666e89a4ee9c7c90fe7` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-001-003` / `TC-IMPRANA-FR-FIN-001-003` | `REV_4c837f2337c3c5a1dbc4abb5e83ecb75258365d18873d048c31ad84827e5f938` / `REV_3d1bd7790274b6d914f6674e925b71c55eacd755353d0a498c4154925997a880` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FIN-001-004` / `TC-IMPRANA-FR-FIN-001-004` | `REV_3c08a7c7e2657c2af540a0a16b66fbb53e1d7b0aa6f1c021f75fda100912729a` / `REV_198b823cdffe233faa81949bc30e0d0ef4c7f63701fdf906ecfaaf0eab79cc09` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FIN-001-001 — Record a funding agreement

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-001-001` is not created. Verification duty `TASK-FR-FIN-001-03` (qualification); source `docs/backlog/backlog.csv` record 230, exact block `dabe3a226ee87f093ad2e78262b3207e547509624e332f83eecad37ee996fa26`.

**Original preconditions**

1. a new funding agreement

**Original actions**

1. the Finance Officer records it

**Exact source oracles — all required**

1. it captures agreement identity, funder, programme links, amount, currency, dates, amendments and reporting obligations
2. confidential clauses and attachments use separate field permissions
3. any subgrant relationship preserves its own agreement version

Legacy same-requirement reuse candidates: `TC-FIN-001-01`, `TC-FIN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-001-002 — Two donors linked to one project see only their own view

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-001-002` is not created. Verification duty `TASK-FR-FIN-001-03` (qualification); source `docs/backlog/backlog.csv` record 230, exact block `fbc9f60ae8a1d9b57b0bbb248adfc3b88d6144aa865366ff0d9de19dd0f5c01c`.

**Original preconditions**

1. two donors are linked to one project

**Original actions**

1. each donor's external user accesses the project

**Exact source oracles — all required**

1. each sees only their approved report view
2. neither has automatic access to the other's agreement

Legacy same-requirement reuse candidates: `TC-FIN-001-01`, `TC-FIN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-001-003 — Reject access or ownership created by a funder relation

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-001-003` is not created. Verification duty `TASK-FR-FIN-001-03` (qualification); source `docs/backlog/backlog.csv` record 230, exact block `4c837f2337c3c5a1dbc4abb5e83ecb75258365d18873d048c31ad84827e5f938`.

**Original preconditions**

1. a funder is linked to a project

**Original actions**

1. the relation is saved

**Exact source oracles — all required**

1. no user grant or ownership share in outcomes is created

Legacy same-requirement reuse candidates: `TC-FIN-001-01`, `TC-FIN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FIN-001-004 — Reject amount changes without amendment history

Source persona: Finance Officer. Proposed fixture `FIX-FR-FIN-001-004` is not created. Verification duty `TASK-FR-FIN-001-03` (qualification); source `docs/backlog/backlog.csv` record 230, exact block `3c08a7c7e2657c2af540a0a16b66fbb53e1d7b0aa6f1c021f75fda100912729a`.

**Original preconditions**

1. a recorded funding agreement

**Original actions**

1. its amount is changed without an amendment

**Exact source oracles — all required**

1. the change is refused

Legacy same-requirement reuse candidates: `TC-FIN-001-01`, `TC-FIN-001-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
