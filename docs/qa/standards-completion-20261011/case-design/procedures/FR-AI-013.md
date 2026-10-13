## QA v1.3 — source-bound case design (proposed)

Story `FR-AI-013` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-AI-013-001` / `TC-IMPRANA-FR-AI-013-001` | `REV_9d7390d12e1fe0f4aa74240fabca1f39fcb9a6ab89e7e8dc6996382e09d44c66` / `REV_a518ccaa2c9c7744744220ad6f7ee77b1c5b2c41fefdb2d68627b2b8764edbec` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-013-002` / `TC-IMPRANA-FR-AI-013-002` | `REV_390bd914acebf3347408775c9a55f5f6fe0eb7d88b11995dcd49f157ea9a8d3a` / `REV_84db55217ed046939b17f9a5ccd5bd22a7a59f7c48f7d3b5c6573966e4741784` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-AI-013-003` / `TC-IMPRANA-FR-AI-013-003` | `REV_01dcb906c14f448dc4af9b1786a2928213d83af028dc2c5e14dabc24a9e18fc5` / `REV_58f891da54d8d99b90c415359f8007398aef07f51cc939ce6857f18bca2e1a0e` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-AI-013-001 — Answers record dependencies and audience

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-013-001` is not created. Verification duty `TASK-FR-AI-013-03` (qualification); source `docs/backlog/backlog.csv` record 12, exact block `9d7390d12e1fe0f4aa74240fabca1f39fcb9a6ab89e7e8dc6996382e09d44c66`.

**Original preconditions**

1. an AI answer or saved conversation

**Original actions**

1. it is saved

**Exact source oracles — all required**

1. its source dependencies and permitted audience are recorded

Legacy same-requirement reuse candidates: `TC-AI-013-01`, `TC-AI-013-02`, `TC-AT11`, `SEC-033`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-013-002 — Access is rechecked on reuse

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-013-002` is not created. Verification duty `TASK-FR-AI-013-03` (qualification); source `docs/backlog/backlog.csv` record 12, exact block `390bd914acebf3347408775c9a55f5f6fe0eb7d88b11995dcd49f157ea9a8d3a`.

**Original preconditions**

1. a saved conversation

**Original actions**

1. it is opened, shared, summarised or exported

**Exact source oracles — all required**

1. current access to its source dependencies is rechecked
2. inaccessible segments are withheld, or the artifact is withdrawn when redaction cannot be safe

Legacy same-requirement reuse candidates: `TC-AI-013-01`, `TC-AI-013-02`, `TC-AT11`, `SEC-033`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-AI-013-003 — Reject reintroduction of revoked text

Source persona: Organisation Administrator. Proposed fixture `FIX-FR-AI-013-003` is not created. Verification duty `TASK-FR-AI-013-03` (qualification); source `docs/backlog/backlog.csv` record 12, exact block `01dcb906c14f448dc4af9b1786a2928213d83af028dc2c5e14dabc24a9e18fc5`.

**Original preconditions**

1. a source grant revoked after a conversation

**Original actions**

1. the user requests a summary of the prior conversation, opens a cached answer or writes a new prompt

**Exact source oracles — all required**

1. the now restricted passages are not revealed
2. copying the chat does not create new source rights

Legacy same-requirement reuse candidates: `TC-AI-013-01`, `TC-AI-013-02`, `TC-AT11`, `SEC-033`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
