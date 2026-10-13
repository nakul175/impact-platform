## QA v1.3 — source-bound case design (proposed)

Story `FR-RPT-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-RPT-008-001` / `TC-IMPRANA-FR-RPT-008-001` | `REV_c50b5dac83100160f867aa58a1cafbaaf0610b619fb9c88f2da94f2a670b2979` / `REV_d0eaa4989150eb87944aeac1fa0f8731ea10a2089d080e7fd276ebda334df4e6` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-008-002` / `TC-IMPRANA-FR-RPT-008-002` | `REV_180e84ca7d5996ee49e0a311284c4a323b78cd305353cabcbef44ae583a29c71` / `REV_92ec01693cef81f588f4e9c00b13b83f3df69470d03f746290722824066d925d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-008-003` / `TC-IMPRANA-FR-RPT-008-003` | `REV_4f26d35caafb6f42d491a356aed755b450c07b0dea8e6037b8d9884504cea7ff` / `REV_bf8fbad905f448ad388e9112f3a7cde8ef5e1daca83bb502aa68473322b083ce` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-RPT-008-004` / `TC-IMPRANA-FR-RPT-008-004` | `REV_7de88119b6c81ac886d29d40bba0515ffaaf7642e48ff4658aa0e38dcc17b917` / `REV_c695a24433763f05b3ea79756e9f2d853dc42536bb0df27123ed1e458413e131` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-RPT-008-001 — Removed recipient receives nothing

Source persona: Programme Manager. Proposed fixture `FIX-FR-RPT-008-001` is not created. Verification duty `TASK-FR-RPT-008-03` (qualification); source `docs/backlog/backlog.csv` record 301, exact block `c50b5dac83100160f867aa58a1cafbaaf0610b619fb9c88f2da94f2a670b2979`.

**Original preconditions**

1. a delivery schedule with an artifact version or explicit latest-approved policy, three recipients, a cadence and an owner

**Original actions**

1. one recipient is removed after scheduling and the delivery runs

**Exact source oracles — all required**

1. notices are sent to the two eligible recipients
2. the removed recipient receives no protected artifact
3. the removed recipient is skipped with a permitted reason

Legacy same-requirement reuse candidates: `TC-RPT-008-01`, `TC-RPT-008-02`, `TC-AT13`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-008-002 — Sensitive delivery uses authenticated access

Source persona: Programme Manager. Proposed fixture `FIX-FR-RPT-008-002` is not created. Verification duty `TASK-FR-RPT-008-03` (qualification); source `docs/backlog/backlog.csv` record 301, exact block `180e84ca7d5996ee49e0a311284c4a323b78cd305353cabcbef44ae583a29c71`.

**Original preconditions**

1. a sensitive artifact is scheduled for delivery

**Original actions**

1. the delivery is sent

**Exact source oracles — all required**

1. recipients receive an authenticated access notice rather than an unprotected attachment

Legacy same-requirement reuse candidates: `TC-RPT-008-01`, `TC-RPT-008-02`, `TC-AT13`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-008-003 — Reject sending to recipients from a cached list

Source persona: Programme Manager. Proposed fixture `FIX-FR-RPT-008-003` is not created. Verification duty `TASK-FR-RPT-008-03` (qualification); source `docs/backlog/backlog.csv` record 301, exact block `4f26d35caafb6f42d491a356aed755b450c07b0dea8e6037b8d9884504cea7ff`.

**Original preconditions**

1. a recipient's access has been revoked

**Original actions**

1. the delivery runs

**Exact source oracles — all required**

1. recipient membership, purpose, artifact approval and disclosure are rechecked
2. the revoked recipient is not silently retained from a cached list

Legacy same-requirement reuse candidates: `TC-RPT-008-01`, `TC-RPT-008-02`, `TC-AT13`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-RPT-008-004 — Reject treating an unresolved timeout as delivered

Source persona: Programme Manager. Proposed fixture `FIX-FR-RPT-008-004` is not created. Verification duty `TASK-FR-RPT-008-03` (qualification); source `docs/backlog/backlog.csv` record 301, exact block `7de88119b6c81ac886d29d40bba0515ffaaf7642e48ff4658aa0e38dcc17b917`.

**Original preconditions**

1. a delivery attempt ended in an unresolved provider timeout

**Original actions**

1. the delivery status is checked or the delivery is retried

**Exact source oracles — all required**

1. the attempt is tracked as unknown until reconciled
2. any retry uses the delivery identity

Legacy same-requirement reuse candidates: `TC-RPT-008-01`, `TC-RPT-008-02`, `TC-AT13`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
