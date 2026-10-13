## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-016b` · 2 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-016b-001` / `TC-IMPRANA-FR-AI-016b-001` | `REV_da9c6b91f1c1eb94809619a581f41462094c64a815c7a5c840d32fd1da9f1c42` / `REV_4d0500175436a82d06000b6e0225d879334abfa5050ae7d9209a4153a89771e6` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-016b-002` / `TC-IMPRANA-FR-AI-016b-002` | `REV_3c50d52c049cdd23f7c17bf3028f182db7a714928b777f7bec6c60e549b6c714` / `REV_6c819e6305b2b91decd82a170de57face6d5375c5aaf3028cc1ef9519a654ce3` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-016b-001 — Long job times out with a labelled partial draft

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-016b-001` is not created. Verification duty `TASK-FR-AI-016b-03` (qualification); source `docs/backlog/backlog.csv` record 17, exact block `da9c6b91f1c1eb94809619a581f41462094c64a815c7a5c840d32fd1da9f1c42`.

**Original preconditions**

1. a report-draft job with a 20-minute limit

**Original actions**

1. it runs past 20 minutes

**Exact source oracles — all required**

1. it stops with outcome TIMED_OUT
2. any partial draft is kept and labelled "Incomplete draft"

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-016b-002 — Reject an incomplete draft shown as complete

Source persona: MEL Manager. Proposed fixture `FIX-FR-AI-016b-002` is not created. Verification duty `TASK-FR-AI-016b-03` (qualification); source `docs/backlog/backlog.csv` record 17, exact block `3c50d52c049cdd23f7c17bf3028f182db7a714928b777f7bec6c60e549b6c714`.

**Original preconditions**

1. a job that timed out or was cancelled

**Original actions**

1. its output is shown or exported

**Exact source oracles — all required**

1. it is labelled incomplete and cannot be published as a final draft

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
