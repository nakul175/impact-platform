## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-010` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-010-001` / `TC-IMPRANA-FR-INT-010-001` | `REV_0ec0365e0ea8b9463afa6ca2e9a803f137eaac4fc35b095403ff2e96ba0133e9` / `REV_885f421411676b794e94f63c1f916784cd512eb24fd540be025df9dbeab38d03` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-010-002` / `TC-IMPRANA-FR-INT-010-002` | `REV_523dbe18d56c3164477c311779a547cb169c519f20e433a1013176317e0ee428` / `REV_3cbde647d92d6a651f980cb5be59a5afec7b3f33dcb14b8332435f9c7c88fd98` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-010-003` / `TC-IMPRANA-FR-INT-010-003` | `REV_dce30bdb61167b237d3dbf097bd0a4a6adc90256ac8aab34d83b9e8ff4c931f7` / `REV_3fea54d02bed8fe237cd1f5ad3b96af8b386f4314ddf0737134d290e3cf325e1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-010-004` / `TC-IMPRANA-FR-INT-010-004` | `REV_17773ed370abc1c7d5c862e5fb9a7f7227bea8e0a97ee81bca7125c16e6cd0b6` / `REV_30b970f36b6f93b4cee4d1d32c0c5dad53ebda3f65458aac444a914707a1225a` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-010-001 — Developer workspace provides isolated test assets

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-010-001` is not created. Verification duty `TASK-FR-INT-010-03` (qualification); source `docs/backlog/backlog.csv` record 349, exact block `0ec0365e0ea8b9463afa6ca2e9a803f137eaac4fc35b095403ff2e96ba0133e9`.

**Original preconditions**

1. an Integration Developer with a developer workspace

**Original actions**

1. they open it

**Exact source oracles — all required**

1. versioned sample contracts, synthetic fixtures and test credentials with isolated tenant scope are available
2. production secrets and personal data are excluded by default

Legacy same-requirement reuse candidates: `TC-INT-010-01`, `TC-INT-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-010-002 — Qualification precedes production eligibility

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-010-002` is not created. Verification duty `TASK-FR-INT-010-03` (qualification); source `docs/backlog/backlog.csv` record 349, exact block `523dbe18d56c3164477c311779a547cb169c519f20e433a1013176317e0ee428`.

**Original preconditions**

1. a connector under development

**Original actions**

1. the Integration Developer runs the connector test end to end

**Exact source oracles — all required**

1. qualification exercises full update, retry and failure behaviour
2. a production connection becomes eligible only after qualification

Legacy same-requirement reuse candidates: `TC-INT-010-01`, `TC-INT-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-010-003 — Reject test credential access to production

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-010-003` is not created. Verification duty `TASK-FR-INT-010-03` (qualification); source `docs/backlog/backlog.csv` record 349, exact block `dce30bdb61167b237d3dbf097bd0a4a6adc90256ac8aab34d83b9e8ff4c931f7`.

**Original preconditions**

1. a test credential from the developer workspace

**Original actions**

1. it is used to enumerate or mutate a production project

**Exact source oracles — all required**

1. both actions are denied

Legacy same-requirement reuse candidates: `TC-INT-010-01`, `TC-INT-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-010-004 — Reject debug payload access as a developer entitlement

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-010-004` is not created. Verification duty `TASK-FR-INT-010-03` (qualification); source `docs/backlog/backlog.csv` record 349, exact block `17773ed370abc1c7d5c862e5fb9a7f7227bea8e0a97ee81bca7125c16e6cd0b6`.

**Original preconditions**

1. an Integration Developer without a support grant

**Original actions**

1. they request debug payload access

**Exact source oracles — all required**

1. access is denied
2. debug payloads are available only through a separate time bounded support grant

Legacy same-requirement reuse candidates: `TC-INT-010-01`, `TC-INT-010-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
