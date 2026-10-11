## QA v1.3 — source-bound case design (proposed)

Story `US-CM-08` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-CM-08-001` / `TC-IMPRANA-US-CM-08-001` | `REV_e015ef2d3ccfbdc279b2471aed2bd4f3ddcb22d6379e93ca58f170504bb90fed` / `REV_48ecdd6b5423b47f8fa02aeba167116d80c1be43eed8e3c6e33cafe9883472c1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-08-002` / `TC-IMPRANA-US-CM-08-002` | `REV_07d1e6eb4daa20b673cff23d5fd59fee56cac501862fc2b7ab4b5e83fe5bf84a` / `REV_0afb018a92bb71266208ae357737f88876e85d3b5c5c0459b74457271545ad96` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-08-003` / `TC-IMPRANA-US-CM-08-003` | `REV_02ac649d659259e508c34a81a547fc8065fc151d5c1a0dc066c61689b4b72d49` / `REV_6f4c4890e56e7877bc1e052c678f8d28408e514959fdd6dd4765f751e0f3a685` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-CM-08-001 — Invoice in INR with GST at launch

Source persona: Operations Head. Proposed fixture `FIX-US-CM-08-001` is not created. Verification duty `TASK-US-CM-08-03` (qualification); source `docs/backlog/backlog.csv` record 208, exact block `e015ef2d3ccfbdc279b2471aed2bd4f3ddcb22d6379e93ca58f170504bb90fed`.

**Original preconditions**

1. an organisation invoiced in INR at launch

**Original actions**

1. an invoice is issued

**Exact source oracles — all required**

1. the invoice is in INR
2. GST is applied and shown on the invoice

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-08-002 — Other currencies added per market

Source persona: Operations Head. Proposed fixture `FIX-US-CM-08-002` is not created. Verification duty `TASK-US-CM-08-03` (qualification); source `docs/backlog/backlog.csv` record 208, exact block `07d1e6eb4daa20b673cff23d5fd59fee56cac501862fc2b7ab4b5e83fe5bf84a`.

**Original preconditions**

1. a new market has been added with its local currency

**Original actions**

1. an invoice is issued to an organisation in that market

**Exact source oracles — all required**

1. the invoice is in that market's local currency

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-08-003 — Reject an INR invoice without GST

Source persona: Operations Head. Proposed fixture `FIX-US-CM-08-003` is not created. Verification duty `TASK-US-CM-08-03` (qualification); source `docs/backlog/backlog.csv` record 208, exact block `02ac649d659259e508c34a81a547fc8065fc151d5c1a0dc066c61689b4b72d49`.

**Original preconditions**

1. an organisation invoiced in INR

**Original actions**

1. an invoice is issued without GST

**Exact source oracles — all required**

1. the invoice is not accepted
2. no invoice is issued in a currency whose market has not been added

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
