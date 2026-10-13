## QA v1.3 — source-bound case design (proposed)

Story `FR-SEC-009` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-SEC-009-001` / `TC-IMPRANA-FR-SEC-009-001` | `REV_6b63abae3a04924ca678c6b6f969f0fa48f00edcc70b2e638696db9312043fcc` / `REV_68f911b5073f364b2d3825473d12f03454ad1489350bae22480d6188449b3e1e` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-009-002` / `TC-IMPRANA-FR-SEC-009-002` | `REV_1206b1a7224e22252bb3500f855ad8db2bb506a68c8245329c4eb9b116c76940` / `REV_692b84c50edf66ed937311eb4d78ae0aa864a84d5a5b607322002affc21f6fed` | manual → MANUAL recommendation; UNRESOLVED; Not run |
| `AC-FR-SEC-009-003` / `TC-IMPRANA-FR-SEC-009-003` | `REV_684de88c10ad18943b6f12a3b4b174bead7266383f348ae1f5f0e03c6e323034` / `REV_bf9a06d21c4244dcf8ca453ddcf8675e2b303c582f2291f67ab58581c3271fde` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-SEC-009-001 — Intake creates a restricted case

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-009-001` is not created. Verification duty `TASK-FR-SEC-009-03` (qualification); source `docs/backlog/backlog.csv` record 154, exact block `6b63abae3a04924ca678c6b6f969f0fa48f00edcc70b2e638696db9312043fcc`.

**Original preconditions**

1. a vulnerability report

**Original actions**

1. it is received

**Exact source oracles — all required**

1. a restricted case records reported scope, severity, affected versions, owner and timing targets
2. triage distinguishes confirmed exposure from suspected risk

Legacy same-requirement reuse candidates: `TC-SEC-009-01`, `TC-SEC-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-009-002 — Milestones are recorded against targets

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-009-002` is not created. Verification duty `TASK-FR-SEC-009-03` (qualification); source `docs/backlog/backlog.csv` record 154, exact block `1206b1a7224e22252bb3500f855ad8db2bb506a68c8245329c4eb9b116c76940`.

**Original preconditions**

1. a simulated credential exposure

**Original actions**

1. it is handled

**Exact source oracles — all required**

1. report, acknowledgement, containment, rotation, fix and retest times are recorded against the applicable targets
2. mitigation, fix, independent retest and closure are separate milestones

Legacy same-requirement reuse candidates: `TC-SEC-009-01`, `TC-SEC-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-SEC-009-003 — Reject silent downgrade and missed release block

Source persona: Platform Operator. Proposed fixture `FIX-FR-SEC-009-003` is not created. Verification duty `TASK-FR-SEC-009-03` (qualification); source `docs/backlog/backlog.csv` record 154, exact block `684de88c10ad18943b6f12a3b4b174bead7266383f348ae1f5f0e03c6e323034`.

**Original preconditions**

1. a critical or high finding affecting confidentiality, integrity or access

**Original actions**

1. an exception is requested or a release is attempted

**Exact source oracles — all required**

1. the BRD release block and timing targets still apply
2. the severity is not silently downgraded

Legacy same-requirement reuse candidates: `TC-SEC-009-01`, `TC-SEC-009-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
