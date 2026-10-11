## QA v1.3 — source-bound case design (proposed)

Story `US-CM-04` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-CM-04-001` / `TC-IMPRANA-US-CM-04-001` | `REV_1d934932e675541da60ec444e321cb18c27179ad38c8bf20b8d1907de83457e3` / `REV_c37a5f68d6738c7e861901fd05d8e488521c8e60097aebc57be277a9a7777692` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-04-002` / `TC-IMPRANA-US-CM-04-002` | `REV_2804518bd9d21ea6fee92b6a9660c8b54ffff7b609f04afa6500226c2ec7bff0` / `REV_e159e880e92f9226cb6a9b4963cfd9b483f03ecef80d269dd961cfc688b6c390` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-04-003` / `TC-IMPRANA-US-CM-04-003` | `REV_1135c622c3c69548efd2d552053176741c1f455e7c14094086c5320dc34e775f` / `REV_ef382f09fc9aa744c2e702a8cc2121a989f752cd4a777be673418fe3447c8532` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-CM-04-001 — Data kept read-only after sponsorship ends

Source persona: Executive Director. Proposed fixture `FIX-US-CM-04-001` is not created. Verification duty `TASK-US-CM-04-03` (qualification); source `docs/backlog/backlog.csv` record 63, exact block `1d934932e675541da60ec444e321cb18c27179ad38c8bf20b8d1907de83457e3`.

**Original preconditions**

1. an organisation whose sponsorship has ended

**Original actions**

1. the Executive Director opens the workspace within 90 days of the end date

**Exact source oracles — all required**

1. all the organisation's data is available read-only

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-04-002 — One-step conversion to a direct subscription

Source persona: Executive Director. Proposed fixture `FIX-US-CM-04-002` is not created. Verification duty `TASK-US-CM-04-03` (qualification); source `docs/backlog/backlog.csv` record 63, exact block `2804518bd9d21ea6fee92b6a9660c8b54ffff7b609f04afa6500226c2ec7bff0`.

**Original preconditions**

1. an organisation whose sponsorship has ended

**Original actions**

1. the Executive Director converts to a direct subscription

**Exact source oracles — all required**

1. the conversion completes in one step
2. all the organisation's existing data is available under the direct subscription

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-04-003 — Reject data loss when sponsorship ends

Source persona: Executive Director. Proposed fixture `FIX-US-CM-04-003` is not created. Verification duty `TASK-US-CM-04-03` (qualification); source `docs/backlog/backlog.csv` record 63, exact block `1135c622c3c69548efd2d552053176741c1f455e7c14094086c5320dc34e775f`.

**Original preconditions**

1. an organisation whose sponsorship ended fewer than 90 days ago

**Original actions**

1. any retention or clean-up process runs

**Exact source oracles — all required**

1. none of the organisation's data is deleted or made unavailable

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
