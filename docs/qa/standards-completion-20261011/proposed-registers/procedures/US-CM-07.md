## QA v1.3 — source-bound case design (proposed)

Story `US-CM-07` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-CM-07-001` / `TC-IMPRANA-US-CM-07-001` | `REV_74c348be32c807952700c442f0b30644cf0d6112b913a93b0e9ccc3024703f39` / `REV_63f8016a8db7e7cda2c0e4d73c68078e8a986d1af009160f71445e4db4c18ebb` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-07-002` / `TC-IMPRANA-US-CM-07-002` | `REV_d9a3224e7b8996c0780632a706952157c5c4bf2ec6730e6d25af87353a4d6436` / `REV_0eb75916c450c1caad0459b5476cc2749b7798e17b9da3302f1ba3ead86be25d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-07-003` / `TC-IMPRANA-US-CM-07-003` | `REV_8d11a238a951fa244260060a1e2b812bf8493934debbcc6f070e30ebc8181be9` / `REV_22b87de17988196e78539e00cba68d27ff02e9bfd985b4af0ae496ed8d2c5f62` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-CM-07-001 — Monthly statement per partner

Source persona: Platform Operator. Proposed fixture `FIX-US-CM-07-001` is not created. Verification duty `TASK-US-CM-07-03` (qualification); source `docs/backlog/backlog.csv` record 207, exact block `74c348be32c807952700c442f0b30644cf0d6112b913a93b0e9ccc3024703f39`.

**Original preconditions**

1. revenue was sourced through a partner during a month

**Original actions**

1. the monthly statements are produced

**Exact source oracles — all required**

1. a statement is produced for that partner showing the revenue sourced through it that month

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-07-002 — Statement reconciled to invoices

Source persona: Platform Operator. Proposed fixture `FIX-US-CM-07-002` is not created. Verification duty `TASK-US-CM-07-03` (qualification); source `docs/backlog/backlog.csv` record 207, exact block `d9a3224e7b8996c0780632a706952157c5c4bf2ec6730e6d25af87353a4d6436`.

**Original preconditions**

1. a partner's monthly statement

**Original actions**

1. the Platform Operator reconciles it

**Exact source oracles — all required**

1. every amount on the statement matches the related invoices

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-07-003 — Reject an unreconciled statement

Source persona: Platform Operator. Proposed fixture `FIX-US-CM-07-003` is not created. Verification duty `TASK-US-CM-07-03` (qualification); source `docs/backlog/backlog.csv` record 207, exact block `8d11a238a951fa244260060a1e2b812bf8493934debbcc6f070e30ebc8181be9`.

**Original preconditions**

1. a partner statement whose amounts do not match the related invoices

**Original actions**

1. the Platform Operator tries to settle the revenue share

**Exact source oracles — all required**

1. the statement is not used for settlement until it is reconciled

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
