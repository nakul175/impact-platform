## QA v1.3 — source-bound case design (proposed)

Story `FR-ANA-008` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-ANA-008-001` / `TC-IMPRANA-FR-ANA-008-001` | `REV_e444dea6b736adf6a2ff4e92a1f0a77e367d9a4edb56b5ddc9f02051be8d71e7` / `REV_a8ca7e6af3af3be7e0f3dab0640985b28b809c3e12add66c97a868ca75385cbc` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-008-002` / `TC-IMPRANA-FR-ANA-008-002` | `REV_5bddc4207e40a6260ffb57c540333c04797807e5e57cdf7a6f10abc687c47139` / `REV_38e27f5e6c2db9307ec5b732f16663b68cb3a40270cc29869d0ba780d6f6ccd4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-008-003` / `TC-IMPRANA-FR-ANA-008-003` | `REV_c69f45992351d7f1b5fc2d4a777c93488cedbb86a50a83710fde86d0a333d7fe` / `REV_551258ed6a5ac8d621d9d7477cb3b55c242ab846049a5d9b78e2bec37148b702` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-ANA-008-004` / `TC-IMPRANA-FR-ANA-008-004` | `REV_6417c278ba69aca505f75419dad9b519e8de197140a095e0c86f6205a5b416c9` / `REV_e9a95b3c6536731b2ca89e94d66318c5564f77e9961299c7e22d1c900d684c48` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-ANA-008-001 — Publication pins dashboard configuration

Source persona: MEL Manager. Proposed fixture `FIX-FR-ANA-008-001` is not created. Verification duty `TASK-FR-ANA-008-03` (qualification); source `docs/backlog/backlog.csv` record 211, exact block `e444dea6b736adf6a2ff4e92a1f0a77e367d9a4edb56b5ddc9f02051be8d71e7`.

**Original preconditions**

1. a dashboard ready for publication

**Original actions**

1. the MEL Manager publishes it

**Exact source oracles — all required**

1. its layout, bindings, audience and expiry are pinned
2. any change of owner requires current authority

Legacy same-requirement reuse candidates: `TC-ANA-008-01`, `TC-ANA-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-008-002 — Copy to a funder workspace keeps restricted widgets unavailable

Source persona: MEL Manager. Proposed fixture `FIX-FR-ANA-008-002` is not created. Verification duty `TASK-FR-ANA-008-03` (qualification); source `docs/backlog/backlog.csv` record 211, exact block `5bddc4207e40a6260ffb57c540333c04797807e5e57cdf7a6f10abc687c47139`.

**Original preconditions**

1. an internal dashboard with restricted widgets

**Original actions**

1. the MEL Manager copies it to a funder workspace

**Exact source oracles — all required**

1. the copy is a draft with no new data grants
2. the sharing preview calculates the recipient's view and identifies unavailable bindings
3. restricted widgets remain unavailable until explicitly bound to approved disclosed metrics

Legacy same-requirement reuse candidates: `TC-ANA-008-01`, `TC-ANA-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-008-003 — Reject public dashboards on live private queries

Source persona: MEL Manager. Proposed fixture `FIX-FR-ANA-008-003` is not created. Verification duty `TASK-FR-ANA-008-03` (qualification); source `docs/backlog/backlog.csv` record 211, exact block `c69f45992351d7f1b5fc2d4a777c93488cedbb86a50a83710fde86d0a333d7fe`.

**Original preconditions**

1. a public dashboard

**Original actions**

1. its widgets are bound

**Exact source oracles — all required**

1. they reference only disclosure-approved artifacts
2. not unrestricted live private queries

Legacy same-requirement reuse candidates: `TC-ANA-008-01`, `TC-ANA-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-ANA-008-004 — Reject continued publication after a sensitivity change

Source persona: MEL Manager. Proposed fixture `FIX-FR-ANA-008-004` is not created. Verification duty `TASK-FR-ANA-008-03` (qualification); source `docs/backlog/backlog.csv` record 211, exact block `6417c278ba69aca505f75419dad9b519e8de197140a095e0c86f6205a5b416c9`.

**Original preconditions**

1. a published dashboard

**Original actions**

1. the sensitivity of one of its sources changes

**Exact source oracles — all required**

1. the affected publication is suspended until revalidated

Legacy same-requirement reuse candidates: `TC-ANA-008-01`, `TC-ANA-008-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
