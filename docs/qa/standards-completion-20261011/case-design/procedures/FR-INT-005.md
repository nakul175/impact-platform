## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-005` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-005-001` / `TC-IMPRANA-FR-INT-005-001` | `REV_ed1eaa43ed5c3c5a8cde3118d1d987cb57588bea6d24584f7a1b1029629f7b22` / `REV_5f19ca03e6382d16671181c19576efc75458eb1286e943518892980bcc38180e` | regression → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-005-002` / `TC-IMPRANA-FR-INT-005-002` | `REV_bcb39aa9ab3a301cbd4ae62d77797eb68bdc72dd338247da33dc04dd9b18d53e` / `REV_5f56dc2a5840917c3e2d70daee4830c2e798ef3103fcb9c201fe3dd9bf3253d5` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-005-003` / `TC-IMPRANA-FR-INT-005-003` | `REV_f89a8453b866d45b6f1bf34fb91c4a8290247b192f7472a6d340e543eee35f86` / `REV_847d759b5b2684c957d59b091de699780f50427e603598e47d5093eeef40d6f4` | regression → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-005-004` / `TC-IMPRANA-FR-INT-005-004` | `REV_f213ff11a7c0a48c2bf7906d861c3762aca325b8a35055b6015e45f0388f00da` / `REV_cabd3d1f0752c0455df5cbcee1a7d0beffdeebc87319bbd7f33dcfa23c314c9b` | unit → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-005-001 — Prior client works against a candidate release

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-005-001` is not created. Verification duty `TASK-FR-INT-005-03` (governance); source `docs/backlog/backlog.csv` record 249, exact block `ed1eaa43ed5c3c5a8cde3118d1d987cb57588bea6d24584f7a1b1029629f7b22`.

**Original preconditions**

1. a supported prior client

**Original actions**

1. it runs against a candidate release

**Exact source oracles — all required**

1. its saved queries, validation semantics and error codes still behave as documented

Legacy same-requirement reuse candidates: `TC-INT-005-01`, `TC-INT-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-005-002 — Deprecation notice provides overlap

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-005-002` is not created. Verification duty `TASK-FR-INT-005-03` (governance); source `docs/backlog/backlog.csv` record 249, exact block `bcb39aa9ab3a301cbd4ae62d77797eb68bdc72dd338247da33dc04dd9b18d53e`.

**Original preconditions**

1. a contract version is being deprecated

**Original actions**

1. the deprecation notice is issued

**Exact source oracles — all required**

1. it includes the effective date and a migration guide
2. at least twelve months of overlap is provided unless a documented security emergency requires an exception

Legacy same-requirement reuse candidates: `TC-INT-005-01`, `TC-INT-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-005-003 — Reject additive fields that change existing meaning

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-005-003` is not created. Verification duty `TASK-FR-INT-005-03` (governance); source `docs/backlog/backlog.csv` record 249, exact block `f89a8453b866d45b6f1bf34fb91c4a8290247b192f7472a6d340e543eee35f86`.

**Original preconditions**

1. an additive optional field is introduced

**Original actions**

1. existing clients use the API

**Exact source oracles — all required**

1. the meaning of existing fields is unchanged

Legacy same-requirement reuse candidates: `TC-INT-005-01`, `TC-INT-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-005-004 — Reject unclassified breaking changes

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-005-004` is not created. Verification duty `TASK-FR-INT-005-03` (governance); source `docs/backlog/backlog.csv` record 249, exact block `f213ff11a7c0a48c2bf7906d861c3762aca325b8a35055b6015e45f0388f00da`.

**Original preconditions**

1. a change that removes an enum value or changes units

**Original actions**

1. the change is classified

**Exact source oracles — all required**

1. it is treated as a breaking change even if the transport shape stays the same

Legacy same-requirement reuse candidates: `TC-INT-005-01`, `TC-INT-005-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
