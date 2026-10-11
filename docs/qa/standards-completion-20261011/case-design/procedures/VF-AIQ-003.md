## QA v1.3 — source-bound case design (proposed)

Story `VF-AIQ-003` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-VF-AIQ-003-001` / `TC-IMPRANA-VF-AIQ-003-001` | `REV_86bd0de210d9c9ceef9fee3dfeb4f7afb26d86622e07c9417afabc5eeb052bf2` / `REV_42515ccc6157c40b24b934cb144c2ee85b611ac620d5beab18356c350ba8442f` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-AIQ-003-002` / `TC-IMPRANA-VF-AIQ-003-002` | `REV_6114329fb25e483dcbc6cd914f126f222502448145e2949ca2d0ac62ea63c6e6` / `REV_f8a5cebbf4b5f11d97606a6fb170df0cae6c4be07cdce3ee9d6e1750f06814cc` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-AIQ-003-003` / `TC-IMPRANA-VF-AIQ-003-003` | `REV_424e5e684037ab3a9d1794364c2f774c3c4a7e3b27f8b51f771cbff3c8633d23` / `REV_18bfca3d115cc7dc78df8e72963f74190714b087411a9694318e1b25c2349a2e` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-VF-AIQ-003-004` / `TC-IMPRANA-VF-AIQ-003-004` | `REV_77f9f1f94a5e84c978b80fd5333621b66fd05a18cf81d8a129dd87a906a397d3` / `REV_61a249282366726272a2bfcab139414ba54acae4f488f6ddc6e25e78df281c57` | manual → MANUAL recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-VF-AIQ-003-001 — Extraction meets precision and recall targets

Source persona: Data Author. Proposed fixture `FIX-VF-AIQ-003-001` is not created. Verification duty `TASK-VF-AIQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 259, exact block `86bd0de210d9c9ceef9fee3dfeb4f7afb26d86622e07c9417afabc5eeb052bf2`.

**Original preconditions**

1. independently labelled source documents

**Original actions**

1. fields are extracted

**Exact source oracles — all required**

1. field-level precision is at least 95 percent
2. recall on mandatory fields is at least 90 percent
3. results are calculated by field type and language

Legacy same-requirement reuse candidates: `TC-VF-AIQ-003`, `TC-AT26`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AIQ-003-002 — Unanswerable questions are correctly abstained

Source persona: Data Author. Proposed fixture `FIX-VF-AIQ-003-002` is not created. Verification duty `TASK-VF-AIQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 259, exact block `6114329fb25e483dcbc6cd914f126f222502448145e2949ca2d0ac62ea63c6e6`.

**Original preconditions**

1. designated unanswerable questions

**Original actions**

1. they are asked

**Exact source oracles — all required**

1. the system abstains or requests clarification in at least 95 percent of cases

Legacy same-requirement reuse candidates: `TC-VF-AIQ-003`, `TC-AT26`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AIQ-003-003 — False abstention on answerable questions stays low

Source persona: Data Author. Proposed fixture `FIX-VF-AIQ-003-003` is not created. Verification duty `TASK-VF-AIQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 259, exact block `424e5e684037ab3a9d1794364c2f774c3c4a7e3b27f8b51f771cbff3c8633d23`.

**Original preconditions**

1. designated answerable questions

**Original actions**

1. they are asked

**Exact source oracles — all required**

1. incorrect abstention is at or below 10 percent

Legacy same-requirement reuse candidates: `TC-VF-AIQ-003`, `TC-AT26`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-VF-AIQ-003-004 — Reject scoring only emitted fields

Source persona: Data Author. Proposed fixture `FIX-VF-AIQ-003-004` is not created. Verification duty `TASK-VF-AIQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 259, exact block `77f9f1f94a5e84c978b80fd5333621b66fd05a18cf81d8a129dd87a906a397d3`.

**Original preconditions**

1. an extraction evaluation run

**Original actions**

1. results are scored

**Exact source oracles — all required**

1. missing mandatory fields and correction time are reported
2. scoring only the fields the model chose to emit is rejected

Legacy same-requirement reuse candidates: `TC-VF-AIQ-003`, `TC-AT26`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
