## QA v1.3 — source-bound case design (proposed)

Story `US-CM-05` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-CM-05-001` / `TC-IMPRANA-US-CM-05-001` | `REV_5a944a454bf5b6efad8471e3290cff747dddddfc56812698b2da2bc67cdff381` / `REV_038798729270433135fce84a830551c8cfb99075497586ef5bdd19bcc3e5fd52` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-05-002` / `TC-IMPRANA-US-CM-05-002` | `REV_1e4e184fdfb0d41b72037d4310d0d4480dd5db9264d917d73733791fc9210deb` / `REV_8c55a28ff30f0c52be0abf79aa552940b444765344847ab6a430da9649b2400d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-05-003` / `TC-IMPRANA-US-CM-05-003` | `REV_17234c301b8ff046f40ab8b2de709f97b753dc94c5de7abbe1edbbed89809661` / `REV_71f3b23dc3a6eb17b3b8cefbfe69a6c775964a15a57f9fc6b86c4a4728973d6d` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-CM-05-001 — See AI credit balance and usage by user

Source persona: Operations Head. Proposed fixture `FIX-US-CM-05-001` is not created. Verification duty `TASK-US-CM-05-06` (qualification); source `docs/backlog/backlog.csv` record 64, exact block `5a944a454bf5b6efad8471e3290cff747dddddfc56812698b2da2bc67cdff381`.

**Original preconditions**

1. an organisation with AI usage credits

**Original actions**

1. the Operations Head opens the AI usage view

**Exact source oracles — all required**

1. the remaining credit balance and the limit are shown
2. usage is shown by user

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Daily advisory limits are not authoritative budget-ledger usage or independent alerts; source requires the actual governed usage contract.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-05-002 — Alerts at 80% and 100% of the limit

Source persona: Operations Head. Proposed fixture `FIX-US-CM-05-002` is not created. Verification duty `TASK-US-CM-05-06` (qualification); source `docs/backlog/backlog.csv` record 64, exact block `1e4e184fdfb0d41b72037d4310d0d4480dd5db9264d917d73733791fc9210deb`.

**Original preconditions**

1. an organisation's AI usage is approaching its limit

**Original actions**

1. usage reaches 80% of the limit

**Exact source oracles — all required**

1. the Operations Head is alerted
2. when usage reaches 100% of the limit the Operations Head is alerted again

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Daily advisory limits are not authoritative budget-ledger usage or independent alerts; source requires the actual governed usage contract.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-05-003 — Reject a threshold crossed without an alert

Source persona: Operations Head. Proposed fixture `FIX-US-CM-05-003` is not created. Verification duty `TASK-US-CM-05-06` (qualification); source `docs/backlog/backlog.csv` record 64, exact block `17234c301b8ff046f40ab8b2de709f97b753dc94c5de7abbe1edbbed89809661`.

**Original preconditions**

1. an organisation's AI usage has reached 80% or 100% of its limit

**Original actions**

1. the Operations Head has received no alert for that threshold

**Exact source oracles — all required**

1. the usage alerting counts as failed

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Specific reuse gap: Daily advisory limits are not authoritative budget-ledger usage or independent alerts; source requires the actual governed usage contract.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
