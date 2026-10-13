## QA v1.3 — source-bound case design (proposed)

Story `US-CM-02` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-CM-02-001` / `TC-IMPRANA-US-CM-02-001` | `REV_d1c585eb04fa060aec8331d926c43b56e353741a9240601f7400edce201df1e3` / `REV_4b499fa6d2ab05b94e135f1e5474ce6f3b7f2ea4fb919cb2aa505070f2afce36` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-02-002` / `TC-IMPRANA-US-CM-02-002` | `REV_323c643eec68166374bf16e27b595e1adb26ffa917fc27a81c5f613116de4499` / `REV_cae5bce7f8aa559e6f6991c3e7f09265ed9fadac06abd4d228fe2e18b5dafc2d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-CM-02-003` / `TC-IMPRANA-US-CM-02-003` | `REV_aa39252cda138ec56a1497dc58bcbd1cacad27022bd7d81993ac844c31b32cfe` / `REV_aa7463331b8d2458e2d4b03e13d54cfff36a527e666514ccd5dabf791cb5af51` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-CM-02-001 — Funder Portfolio Manager sponsors a named cohort

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-CM-02-001` is not created. Verification duty `TASK-US-CM-02-03` (qualification); source `docs/backlog/backlog.csv` record 204, exact block `d1c585eb04fa060aec8331d926c43b56e353741a9240601f7400edce201df1e3`.

**Original preconditions**

1. a Funder Portfolio Manager setting up sponsored access for a named cohort of grantees

**Original actions**

1. they enrol the grantee organisations and set the duration and budget

**Exact source oracles — all required**

1. the sponsorship is saved with the enrolled organisations, duration and budget

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-02-002 — Grantee gets access when it accepts

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-CM-02-002` is not created. Verification duty `TASK-US-CM-02-03` (qualification); source `docs/backlog/backlog.csv` record 204, exact block `323c643eec68166374bf16e27b595e1adb26ffa917fc27a81c5f613116de4499`.

**Original preconditions**

1. a grantee organisation enrolled in the sponsored cohort

**Original actions**

1. the grantee accepts the sponsorship

**Exact source oracles — all required**

1. the organisation gets access to the platform for the sponsored duration
2. the organisation is not charged for that access

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-CM-02-003 — Reject access before acceptance or without terms

Source persona: Funder Portfolio Manager. Proposed fixture `FIX-US-CM-02-003` is not created. Verification duty `TASK-US-CM-02-03` (qualification); source `docs/backlog/backlog.csv` record 204, exact block `aa39252cda138ec56a1497dc58bcbd1cacad27022bd7d81993ac844c31b32cfe`.

**Original preconditions**

1. a grantee organisation enrolled in the sponsored cohort that has not accepted

**Original actions**

1. anyone from that organisation tries to use the sponsored access

**Exact source oracles — all required**

1. access is not granted
2. a sponsorship with no duration or no budget cannot be saved

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
