## QA v1.3 — source-bound case design (proposed)

Story `US-PL-03` · 3 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-US-PL-03-001` / `TC-IMPRANA-US-PL-03-001` | `REV_547e605473cda29401a067266e3f734db8cc5f0530c207167644ee811267b18b` / `REV_85f3f3acd09089b66550d342422a7d98ea43f9d9832f9c4192080ca41991aad8` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-PL-03-002` / `TC-IMPRANA-US-PL-03-002` | `REV_9e885a0b5428fcd3d2eb53d7df22af71bb86a6aeb2d00d5bd7fc882d047c8806` / `REV_8da1a76ab9d12e770d7f84e4d316e1fd6d5b26538ee562c2aaee4a3b55fb2098` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-US-PL-03-003` / `TC-IMPRANA-US-PL-03-003` | `REV_57462a0790e1565891e1ff0373ec489f660baf9d48c80dd829e6acf8ca554fc0` / `REV_d2259b0c8dbc0e0f05e5023cd368aa3f22b1d9fca507664a65dd4380f59cdba4` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-US-PL-03-001 — Invitations and notices arrive by real email

Source persona: Data Author. Proposed fixture `FIX-US-PL-03-001` is not created. Verification duty `TASK-US-PL-03-03` (qualification); source `docs/backlog/backlog.csv` record 125, exact block `547e605473cda29401a067266e3f734db8cc5f0530c207167644ee811267b18b`.

**Original preconditions**

1. a production email provider configured with SPF and DKIM

**Original actions**

1. the platform sends a Data Author an invitation or notice

**Exact source oracles — all required**

1. the email arrives in their inbox

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-PL-03-002 — Bounces handled and sending limits monitored

Source persona: Data Author. Proposed fixture `FIX-US-PL-03-002` is not created. Verification duty `TASK-US-PL-03-03` (qualification); source `docs/backlog/backlog.csv` record 125, exact block `9e885a0b5428fcd3d2eb53d7df22af71bb86a6aeb2d00d5bd7fc882d047c8806`.

**Original preconditions**

1. email sent through the production provider

**Original actions**

1. an email bounces

**Exact source oracles — all required**

1. the bounce is handled
2. sending against the provider's limits is monitored

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-US-PL-03-003 — Reject unauthenticated or unmonitored sending

Source persona: Data Author. Proposed fixture `FIX-US-PL-03-003` is not created. Verification duty `TASK-US-PL-03-03` (qualification); source `docs/backlog/backlog.csv` record 125, exact block `57462a0790e1565891e1ff0373ec489f660baf9d48c80dd829e6acf8ca554fc0`.

**Original preconditions**

1. the production environment

**Original actions**

1. email is sent without SPF and DKIM, bounces are not handled, or sending limits are not monitored

**Exact source oracles — all required**

1. the email setup is not accepted for production

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
