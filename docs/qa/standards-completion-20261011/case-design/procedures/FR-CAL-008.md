## QA v1.3 — source-bound case design (proposed)

Story `FR-CAL-008` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-CAL-008-001` / `TC-IMPRANA-FR-CAL-008-001` | `REV_2e70606a2961cc22134cb6a4719524a5192e197d92a5710fb9dae0d1cd6599be` / `REV_184bb75ba2d0eab6221642bcc16f14965c95dafc6ec23e7dce2544d3686b20dd` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-008-002` / `TC-IMPRANA-FR-CAL-008-002` | `REV_e01412a110abde713f5e8a9d256ae0ca80856e7fd9c23ad14da4b0b8538c0047` / `REV_862076d02079183e636ac204e331220118e9e5a41ad9dfa3cfef9192022a669c` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-CAL-008-003` / `TC-IMPRANA-FR-CAL-008-003` | `REV_066bb6d3dcd122114fe4760f2514a6142bb5dcef1f0a86d577af48a52aed1e38` / `REV_1c7dd8779bd946e57fce24fb7e995253ef475be62a06753ec27213740b317a8e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-CAL-008-001 — Coverage distinguishes approved, pending and missing contributors

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-008-001` is not created. Verification duty `TASK-FR-CAL-008-03` (qualification); source `docs/backlog/backlog.csv` record 58, exact block `2e70606a2961cc22134cb6a4719524a5192e197d92a5710fb9dae0d1cd6599be`.

**Original preconditions**

1. the obligation snapshot for the period expects five partners
2. three partners have approved values, one is pending and one is missing

**Original actions**

1. the result is calculated

**Exact source oracles — all required**

1. approval coverage is 60 percent
2. the pending count and the missing count are shown separately

Legacy same-requirement reuse candidates: `TC-CAL-008-01`, `TC-CAL-008-02`, `TC-AT04`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-008-002 — Official sum is partial when a mandatory contributor is absent

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-008-002` is not created. Verification duty `TASK-FR-CAL-008-03` (qualification); source `docs/backlog/backlog.csv` record 58, exact block `e01412a110abde713f5e8a9d256ae0ca80856e7fd9c23ad14da4b0b8538c0047`.

**Original preconditions**

1. a mandatory contributor has no approved value for the period

**Original actions**

1. the official sum is calculated

**Exact source oracles — all required**

1. it uses only approved eligible values
2. the result carries partial status

Legacy same-requirement reuse candidates: `TC-CAL-008-01`, `TC-CAL-008-02`, `TC-AT04`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-CAL-008-003 — Reject removing an expected contributor without approved eligibility evidence

Source persona: MEL Manager. Proposed fixture `FIX-FR-CAL-008-003` is not created. Verification duty `TASK-FR-CAL-008-03` (qualification); source `docs/backlog/backlog.csv` record 58, exact block `066bb6d3dcd122114fe4760f2514a6142bb5dcef1f0a86d577af48a52aed1e38`.

**Original preconditions**

1. a partner retired today whose obligation was active in a prior period

**Original actions**

1. the prior period result is calculated

**Exact source oracles — all required**

1. the partner remains in the expected contributor set for that period
2. an attempt to mark its obligation not applicable without approved eligibility evidence is refused

Legacy same-requirement reuse candidates: `TC-CAL-008-01`, `TC-CAL-008-02`, `TC-AT04`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_calculation_methods.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
