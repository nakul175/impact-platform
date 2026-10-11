## QA v1.3 — source-bound case design (proposed)

Story `FR-FRM-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-FRM-008-001` / `TC-IMPRANA-FR-FRM-008-001` | `REV_6e53afa5a302131387d60e5d17f0ba622b37af447b3633950970e8b36ec2228f` / `REV_21eef44109327109975661fbb043a3cb93390d8300bfd861b1200d9220274f6d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-008-002` / `TC-IMPRANA-FR-FRM-008-002` | `REV_ba9f8ca3eba18d9988499d798cecf9643e353d74051ceab000f102bd9af6799d` / `REV_3f664d8d8f5edb32ad91feca34bbf15c5e4cc38a218060ab1bc686e01655a489` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-008-003` / `TC-IMPRANA-FR-FRM-008-003` | `REV_c3360cb3db3e5d33b9314ae945a19ac9bb94ed520abb979a75c87013925ffb7d` / `REV_d6afd9efaa5245fe8b8cec87a248642a6a455d4c7fb54b74cfdeeb302329a37d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-FRM-008-004` / `TC-IMPRANA-FR-FRM-008-004` | `REV_49d6b34485083c8292f5e7ccc6b4b7ee3439d554630dc3b5a41072efc0c7a923` / `REV_3510a73724a96d94ed1a83f435cb40fd7f83cab7695358527065c89671138d33` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-FRM-008-001 — Submit once with a scoped token

Source persona: Programme Participant. Proposed fixture `FIX-FR-FRM-008-001` is not created. Verification duty `TASK-FR-FRM-008-03` (qualification); source `docs/backlog/backlog.csv` record 343, exact block `6e53afa5a302131387d60e5d17f0ba622b37af447b3633950970e8b36ec2228f`.

**Original preconditions**

1. a Programme Participant has a single response token with notice and expiry

**Original actions**

1. they submit the form

**Exact source oracles — all required**

1. a receipt confirms successful submission
2. the receipt contains no other respondents' details

Legacy same-requirement reuse candidates: `TC-FRM-008-01`, `TC-FRM-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-008-002 — Resume a draft before expiry

Source persona: Programme Participant. Proposed fixture `FIX-FR-FRM-008-002` is not created. Verification duty `TASK-FR-FRM-008-03` (qualification); source `docs/backlog/backlog.csv` record 343, exact block `ba9f8ca3eba18d9988499d798cecf9643e353d74051ceab000f102bd9af6799d`.

**Original preconditions**

1. draft resume is permitted for the token

**Original actions**

1. the participant returns before expiry, authenticated or with the bound token

**Exact source oracles — all required**

1. their draft is restored

Legacy same-requirement reuse candidates: `TC-FRM-008-01`, `TC-FRM-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-008-003 — Reject token replay and access to other responses

Source persona: Programme Participant. Proposed fixture `FIX-FR-FRM-008-003` is not created. Verification duty `TASK-FR-FRM-008-03` (qualification); source `docs/backlog/backlog.csv` record 343, exact block `c3360cb3db3e5d33b9314ae945a19ac9bb94ed520abb979a75c87013925ffb7d`.

**Original preconditions**

1. a token already used for a final submission

**Original actions**

1. it is replayed and a different response ID is requested

**Exact source oracles — all required**

1. the replay is idempotent or unavailable and creates no duplicate result
2. the other response is never shown

Legacy same-requirement reuse candidates: `TC-FRM-008-01`, `TC-FRM-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-FRM-008-004 — Reject abuse and directory exposure

Source persona: Programme Participant. Proposed fixture `FIX-FR-FRM-008-004` is not created. Verification duty `TASK-FR-FRM-008-03` (qualification); source `docs/backlog/backlog.csv` record 343, exact block `49d6b34485083c8292f5e7ccc6b4b7ee3439d554630dc3b5a41072efc0c7a923`.

**Original preconditions**

1. submissions arriving beyond the rate limits

**Original actions**

1. further requests are made to the form

**Exact source oracles — all required**

1. accessible abuse controls and rate limits are applied
2. no participant directory is exposed

Legacy same-requirement reuse candidates: `TC-FRM-008-01`, `TC-FRM-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
