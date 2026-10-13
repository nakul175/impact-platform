## QA v1.3 — source-bound case design (proposed)

Story `FR-EVD-003` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-EVD-003-001` / `TC-IMPRANA-FR-EVD-003-001` | `REV_5cb16435208d34819f636b6eae7f1db05183a9bc883752271ea0c8e9a574dc31` / `REV_dd7b7cc88d231dfd93bfe29fd0608734975755cb981be039eb96c4fc2de7432f` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-003-002` / `TC-IMPRANA-FR-EVD-003-002` | `REV_18bf89f698884373799eb240e16072833ca3c76355381d7d6d036394e74a81d2` / `REV_3ecc98a367ff5123834e30a9563a635fa3b8340915f425e6807a09d2fe344a6d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-EVD-003-003` / `TC-IMPRANA-FR-EVD-003-003` | `REV_881a59d91af7477a4edd370fc4e2927be42bcbc1eb009495cd14fd978b669194` / `REV_fbcc235796250e5c78bcca60ca97eaca0a153eb703c0f8ffddcd2e0df1edd2db` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-EVD-003-001 — Search with filters

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-003-001` is not created. Verification duty `TASK-FR-EVD-003-03` (qualification); source `docs/backlog/backlog.csv` record 227, exact block `5cb16435208d34819f636b6eae7f1db05183a9bc883752271ea0c8e9a574dc31`.

**Original preconditions**

1. indexed evidence

**Original actions**

1. an Analyst searches using source, type, date and permitted classification filters

**Exact source oracles — all required**

1. permission and purpose filters are applied before result counts and snippets are produced
2. indexed text shows its source version and extraction status
3. unsupported content shows metadata only

Legacy same-requirement reuse candidates: `TC-EVD-003-01`, `TC-EVD-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-003-002 — Reject revealing restricted content in search

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-003-002` is not created. Verification duty `TASK-FR-EVD-003-03` (qualification); source `docs/backlog/backlog.csv` record 227, exact block `18bf89f698884373799eb240e16072833ca3c76355381d7d6d036394e74a81d2`.

**Original preconditions**

1. a phrase that appears only in a restricted report

**Original actions**

1. an unprivileged user searches for that phrase

**Exact source oracles — all required**

1. they receive no matching snippet or citation
2. no count or facet reveals the restricted report

Legacy same-requirement reuse candidates: `TC-EVD-003-01`, `TC-EVD-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-EVD-003-003 — Reject access after revocation or deletion

Source persona: Analyst. Proposed fixture `FIX-FR-EVD-003-003` is not created. Verification duty `TASK-FR-EVD-003-03` (qualification); source `docs/backlog/backlog.csv` record 227, exact block `881a59d91af7477a4edd370fc4e2927be42bcbc1eb009495cd14fd978b669194`.

**Original preconditions**

1. a document whose access was revoked or which was deleted

**Original actions**

1. users search, view suggested queries or use AI retrieval

**Exact source oracles — all required**

1. the document is not reachable through the index, snippets, suggested queries or AI retrieval

Legacy same-requirement reuse candidates: `TC-EVD-003-01`, `TC-EVD-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
