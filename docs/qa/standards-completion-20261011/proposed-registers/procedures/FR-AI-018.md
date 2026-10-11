## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-018` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-018-001` / `TC-IMPRANA-FR-AI-018-001` | `REV_73a1aed2cd96a2cb02cfd4e5e20de60e8801d4f3b06b890bc45dc513955fff84` / `REV_d80e28a30f1456d4a4162048424d1d1eb5b29d5ceb5409f9129cffb830fc7c72` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-018-002` / `TC-IMPRANA-FR-AI-018-002` | `REV_fb09b48e532ac97342749170c0412cabcd25bcc41a7ad81c95b8166e2170ec05` / `REV_f6b54d7b6a92d567f57bd482fc358a6112d25f95b056920f1489589e7f09faa0` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-018-003` / `TC-IMPRANA-FR-AI-018-003` | `REV_a1cf6a0573cfcb0e423734aee33a9efe17f6c05bbbe699c9866c6e96b94497a4` / `REV_3e920e9c2fed2f9fcda3b66673f1fe63e6f6e07441cef3fe338bbba6561e1eda` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-018-004` / `TC-IMPRANA-FR-AI-018-004` | `REV_b9ec8dde8392ebce44e9a687b02d8a06492058d397c9fefd906a744992aa3f8c` / `REV_83a14640907b1c38a90a4b46f3c8c095f2962aac7d6b718cc2c2756f8a849bec` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-018-001 — Capture safety feedback

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-018-001` is not created. Verification duty `TASK-FR-AI-018-03` (qualification); source `docs/backlog/backlog.csv` record 18, exact block `73a1aed2cd96a2cb02cfd4e5e20de60e8801d4f3b06b890bc45dc513955fff84`.

**Original preconditions**

1. an AI output with a safety concern

**Original actions**

1. a user submits feedback

**Exact source oracles — all required**

1. it captures the affected output, category, safe supporting detail and reviewer

Legacy same-requirement reuse candidates: `TC-AI-018-01`, `TC-AI-018-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-018-002 — Shut down an affected use case

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-018-002` is not created. Verification duty `TASK-FR-AI-018-03` (qualification); source `docs/backlog/backlog.csv` record 18, exact block `fb09b48e532ac97342749170c0412cabcd25bcc41a7ad81c95b8166e2170ec05`.

**Original preconditions**

1. a simulated exposed sensitive citation

**Original actions**

1. the Organisation Administrator disables the use case

**Exact source oracles — all required**

1. new affected jobs stop immediately
2. queued work is identified
3. every affected saved answer and generated artifact is listed for review
4. manual report workflows continue

Legacy same-requirement reuse candidates: `TC-AI-018-01`, `TC-AI-018-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-018-003 — Reject reenable without fix evidence

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-018-003` is not created. Verification duty `TASK-FR-AI-018-03` (qualification); source `docs/backlog/backlog.csv` record 18, exact block `a1cf6a0573cfcb0e423734aee33a9efe17f6c05bbbe699c9866c6e96b94497a4`.

**Original preconditions**

1. a disabled use case

**Original actions**

1. someone attempts to reenable it without fix evidence and regression approval

**Exact source oracles — all required**

1. reenable is refused

Legacy same-requirement reuse candidates: `TC-AI-018-01`, `TC-AI-018-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-018-004 — Reject retained payloads and lost core workflows

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-018-004` is not created. Verification duty `TASK-FR-AI-018-03` (qualification); source `docs/backlog/backlog.csv` record 18, exact block `b9ec8dde8392ebce44e9a687b02d8a06492058d397c9fefd906a744992aa3f8c`.

**Original preconditions**

1. an AI incident

**Original actions**

1. incident evidence is preserved and AI is disabled

**Exact source oracles — all required**

1. prohibited source payloads are not retained
2. independent core workflows are not disabled

Legacy same-requirement reuse candidates: `TC-AI-018-01`, `TC-AI-018-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
