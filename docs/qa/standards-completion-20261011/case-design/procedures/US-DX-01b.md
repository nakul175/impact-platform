## QA v1.3 — source-bound case design (proposed)

Story `US-DX-01b` · 2 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-DX-01b-001` / `TC-IMPRANA-US-DX-01b-001` | `REV_9fcc75604154b6dd0d5ac3e408edfb85f8dbc5c743e4b98002e5ca83585bb272` / `REV_5024705c870698136a9e73c39654ef8d095d58e69608e526e75eacbaf84ab61d` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-DX-01b-002` / `TC-IMPRANA-US-DX-01b-002` | `REV_de13aa940da241dc50b79f94d606a203b036daf70f548d583ccfb719d424833c` / `REV_36995745e0758b75c3a7e15a0ceaef5d63bf2e1bcccdeecaa87b70be14bd451d` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-DX-01b-001 — Conversation produces prioritised problems

Source persona: Executive Director. Proposed fixture `FIX-US-DX-01b-001` is not created. Verification duty `TASK-US-DX-01b-03` (qualification); source `docs/backlog/backlog.csv` record 34, exact block `9fcc75604154b6dd0d5ac3e408edfb85f8dbc5c743e4b98002e5ca83585bb272`.

**Original preconditions**

1. AI use case CHAT is enabled by policy

**Original actions**

1. the Executive Director completes the guided conversation

**Exact source oracles — all required**

1. it finishes in under 60 minutes
2. proposes problems in priority order, each with the evidence quoted from the conversation, for the Executive Director to accept or edit

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-DX-01b-002 — Reject AI output accepted without review

Source persona: Executive Director. Proposed fixture `FIX-US-DX-01b-002` is not created. Verification duty `TASK-US-DX-01b-03` (qualification); source `docs/backlog/backlog.csv` record 34, exact block `de13aa940da241dc50b79f94d606a203b036daf70f548d583ccfb719d424833c`.

**Original preconditions**

1. the agent proposes problems

**Original actions**

1. nobody has accepted or edited them

**Exact source oracles — all required**

1. they are not saved as the organisation's problems

Original proposed anchors (file/artifact candidates only): `qualification/test_ai_enablement.py` [code_source]. No assertion-level binding is established.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
