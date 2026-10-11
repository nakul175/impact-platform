## QA v1.3 — source-bound case design (proposed)

Story `FR-OPS-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OPS-003-001` / `TC-IMPRANA-FR-OPS-003-001` | `REV_c859131b901f7a8637090614bf3228461f039d7592a8480b3a194893c3df8062` / `REV_82327faf7fd8081fe3c2a62b763a43f52ef1261dcfe9d6ed1f163154ba49c4a8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-003-002` / `TC-IMPRANA-FR-OPS-003-002` | `REV_ff9293a61821fb3be4ef411b7d2e0361a667d972d15180175aa526ec963df124` / `REV_4a887cfa3dad7e70366a31937043e73d7eafc6ec619a1ed4e2a169386079702a` | native → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-003-003` / `TC-IMPRANA-FR-OPS-003-003` | `REV_b64a93ef4b4b3db088d5377ff90421cfc4bc3feb56b498ce9077f02ddbcec85b` / `REV_7903a9c3acdd9cc683e62d1cfe2739a22cde711d34a8ca17cec2a07c834881b3` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OPS-003-004` / `TC-IMPRANA-FR-OPS-003-004` | `REV_2c0c70b415b96775cb7d8d3d1f0d22edb21a64d03a2dda832c291a47815672cb` / `REV_16d2b38e82efe17e413969db4451dc063d696ce1f22eb48ecf1c55a25f121b10` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OPS-003-001 — Preview a subscription change

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OPS-003-001` is not created. Verification duty `TASK-FR-OPS-003-03` (qualification); source `docs/backlog/backlog.csv` record 307, exact block `c859131b901f7a8637090614bf3228461f039d7592a8480b3a194893c3df8062`.

**Original preconditions**

1. an active subscription

**Original actions**

1. the Organisation Administrator selects a different plan

**Exact source oracles — all required**

1. the preview shows plan limits, overage, renewal date and affected optional capabilities

Legacy same-requirement reuse candidates: `TC-OPS-003-01`, `TC-OPS-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-003-002 — Downgrade below current project count

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OPS-003-002` is not created. Verification duty `TASK-FR-OPS-003-03` (qualification); source `docs/backlog/backlog.csv` record 307, exact block `ff9293a61821fb3be4ef411b7d2e0361a667d972d15180175aa526ec963df124`.

**Original preconditions**

1. a tenant with more projects than the new plan allows

**Original actions**

1. the Organisation Administrator downgrades

**Exact source oracles — all required**

1. existing records remain readable
2. creation beyond the new limit is controlled
3. a resolution plan with grace terms drawn from the contract is created

Legacy same-requirement reuse candidates: `TC-OPS-003-01`, `TC-OPS-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-003-003 — Reject payment failure affecting results or closing the tenant

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OPS-003-003` is not created. Verification duty `TASK-FR-OPS-003-03` (qualification); source `docs/backlog/backlog.csv` record 307, exact block `b64a93ef4b4b3db088d5377ff90421cfc4bc3feb56b498ce9077f02ddbcec85b`.

**Original preconditions**

1. a payment provider failure

**Original actions**

1. the failure is processed

**Exact source oracles — all required**

1. approved results are not altered
2. the tenant is not closed or deleted outside its own authorised workflow
3. no payment secret is retained unnecessarily

Legacy same-requirement reuse candidates: `TC-OPS-003-01`, `TC-OPS-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OPS-003-004 — Reject billing contacts gaining programme administration

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-OPS-003-004` is not created. Verification duty `TASK-FR-OPS-003-03` (qualification); source `docs/backlog/backlog.csv` record 307, exact block `2c0c70b415b96775cb7d8d3d1f0d22edb21a64d03a2dda832c291a47815672cb`.

**Original preconditions**

1. a billing contact added to the subscription

**Original actions**

1. their access is evaluated

**Exact source oracles — all required**

1. they do not become a programme administrator

Legacy same-requirement reuse candidates: `TC-OPS-003-01`, `TC-OPS-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
