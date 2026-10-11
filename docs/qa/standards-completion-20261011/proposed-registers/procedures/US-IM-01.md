## QA v1.3 — source-bound case design (proposed)

Story `US-IM-01` · 2 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-IM-01-001` / `TC-IMPRANA-US-IM-01-001` | `REV_6a97f29f995e6589b470ae64309ee7ec612a34a09e86f3dbc591dceef73877d6` / `REV_cbd4a9fb0ef62bc57481ba9479c9f4622ba07b9e1aea44c93139e824b239af51` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-IM-01-002` / `TC-IMPRANA-US-IM-01-002` | `REV_3e67f079852986d1e7be9a2d2ae694efa6721a65b89ff63faa650d33409465b0` / `REV_2ecf46ef8681bb95a52c6686919bcd409c8a2d21452475db876d1a40ef2d2cf0` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-IM-01-001 — Compare current metrics with the locked baseline

Source persona: Executive Director. Proposed fixture `FIX-US-IM-01-001` is not created. Verification duty `TASK-US-IM-01-03` (qualification); source `docs/backlog/backlog.csv` record 43, exact block `6a97f29f995e6589b470ae64309ee7ec612a34a09e86f3dbc591dceef73877d6`.

**Original preconditions**

1. an opportunity with a locked baseline and a deployed solution

**Original actions**

1. the Executive Director opens the dashboard

**Exact source oracles — all required**

1. current usage and outcome metrics are shown against the locked baseline

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_pilot_outcomes.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-IM-01-002 — Reject comparison against anything but the locked baseline

Source persona: Executive Director. Proposed fixture `FIX-US-IM-01-002` is not created. Verification duty `TASK-US-IM-01-03` (qualification); source `docs/backlog/backlog.csv` record 43, exact block `3e67f079852986d1e7be9a2d2ae694efa6721a65b89ff63faa650d33409465b0`.

**Original preconditions**

1. a locked baseline

**Original actions**

1. the dashboard compares current metrics

**Exact source oracles — all required**

1. it does not compare them against any other baseline

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_pilot_outcomes.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
