## QA v1.3 — source-bound case design (proposed)

Story `FR-DQ-003` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-DQ-003-001` / `TC-IMPRANA-FR-DQ-003-001` | `REV_94dd44407236cb9e3753a3dbb2610c052bd0bab69b64617fe5e2cc589e38c29b` / `REV_2683becbff3d390786f1dca30efc037a9397f2e7e507b079ea62d657dfcbb7f1` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-003-002` / `TC-IMPRANA-FR-DQ-003-002` | `REV_185b572a328e95498fef07a4587f0f47f52ce417bc3c1b7bec29b9baf063ba84` / `REV_e6b3c2253605d5b933aa3e705c1d7d4e8f944c173823ee3f4609b1991961bcd7` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-003-003` / `TC-IMPRANA-FR-DQ-003-003` | `REV_6e8fe5bfc18a67d6a5d49f0d5d5b7cd4c8b3e2a20c7b6b223285b86bf2f327fe` / `REV_a65f3fcd105a1dc23725d0b0e52dc0b2dc57320717964539c586f5385c1cab38` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-003-004` / `TC-IMPRANA-FR-DQ-003-004` | `REV_091f96f71cd75300c10a0cc72c154a81ec4493917b194fb5c32e1c962d1f66d4` / `REV_f16ea398c4977bd8381f2421525c580bb0696b06e27b943377e25885a0a9e6bf` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-DQ-003-005` / `TC-IMPRANA-FR-DQ-003-005` | `REV_bbc9e43e7d6041ac0df471df293d5e0a6783030a41fa479af3f11a5ee3bc3540` / `REV_6667b766a263049a6c59a0e30f32c16f53c24716d6384e7ab4c8ca62094dda23` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-DQ-003-001 — Detect exact duplicates by declared business keys

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-003-001` is not created. Verification duty `TASK-FR-DQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 73, exact block `94dd44407236cb9e3753a3dbb2610c052bd0bab69b64617fe5e2cc589e38c29b`.

**Original preconditions**

1. business keys are declared for a record type

**Original actions**

1. two records share the same business key values

**Exact source oracles — all required**

1. they are flagged as exact duplicates

Legacy same-requirement reuse candidates: `TC-DQ-003-01`, `TC-DQ-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-003-002 — Same-name participants stay separate until reviewed evidence supports a merge

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-003-002` is not created. Verification duty `TASK-FR-DQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 73, exact block `185b572a328e95498fef07a4587f0f47f52ce417bc3c1b7bec29b9baf063ba84`.

**Original preconditions**

1. two participants both named Asha

**Original actions**

1. fuzzy matching proposes them as a candidate pair with permitted evidence and match rationale

**Exact source oracles — all required**

1. they remain separate until a Reviewer chooses distinct, merge or further investigation
2. a merge happens only when reviewed evidence supports identity equivalence
3. the merge maps both source identities to a canonical record, preserving provenance and source confidentiality

Legacy same-requirement reuse candidates: `TC-DQ-003-01`, `TC-DQ-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-003-003 — Unmerge restores relationships and counts

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-003-003` is not created. Verification duty `TASK-FR-DQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 73, exact block `6e8fe5bfc18a67d6a5d49f0d5d5b7cd4c8b3e2a20c7b6b223285b86bf2f327fe`.

**Original preconditions**

1. two records were merged into a canonical record

**Original actions**

1. a Data Steward performs an unmerge or corrective split

**Exact source oracles — all required**

1. the affected relationships are restored
2. affected counts are recalculated

Legacy same-requirement reuse candidates: `TC-DQ-003-01`, `TC-DQ-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-003-004 — Reject a merge based solely on a shared name

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-003-004` is not created. Verification duty `TASK-FR-DQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 73, exact block `091f96f71cd75300c10a0cc72c154a81ec4493917b194fb5c32e1c962d1f66d4`.

**Original preconditions**

1. two participants named Asha with no other supporting evidence

**Original actions**

1. a merge is attempted solely on the shared name

**Exact source oracles — all required**

1. the merge is refused

Legacy same-requirement reuse candidates: `TC-DQ-003-01`, `TC-DQ-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-DQ-003-005 — Reject silent reappearance of a rejected match

Source persona: Data Steward. Proposed fixture `FIX-FR-DQ-003-005` is not created. Verification duty `TASK-FR-DQ-003-03` (qualification); source `docs/backlog/backlog.csv` record 73, exact block `bbc9e43e7d6041ac0df471df293d5e0a6783030a41fa479af3f11a5ee3bc3540`.

**Original preconditions**

1. a Reviewer has rejected a candidate match

**Original actions**

1. duplicate detection runs again

**Exact source oracles — all required**

1. the rejected match does not silently reappear as confirmed

Legacy same-requirement reuse candidates: `TC-DQ-003-01`, `TC-DQ-003-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_import.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
