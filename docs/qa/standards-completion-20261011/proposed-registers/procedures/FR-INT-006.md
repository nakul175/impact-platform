## QA v1.3 — source-bound case design (proposed)

Story `FR-INT-006` · 5 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-INT-006-001` / `TC-IMPRANA-FR-INT-006-001` | `REV_4b6b7a48651ef245f3b3725fe0dd1a5a3dd5b2d7ca429e866798c5feb7734f91` / `REV_128b4a792f454acea5410f177dedffd42d85baf6b2c58430df54ef06acf707e4` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-006-002` / `TC-IMPRANA-FR-INT-006-002` | `REV_7aabb9d9b2480153b184874eefa7332da3be829bf8aaf7036e46ffc46c13d3f3` / `REV_0ffecbccd2b19203aa86f3f0986eb89e7734b39cc12e2461844c6f45d3c7842b` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-006-003` / `TC-IMPRANA-FR-INT-006-003` | `REV_c31d3e22470a0f70467b7c5a49205ace440e6af5380dca87c30f1f08eac20c6e` / `REV_4becbfcf1ae482055c3b9e0f88bf8dd601d3db2c469e0a950da6ed988682dc92` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-006-004` / `TC-IMPRANA-FR-INT-006-004` | `REV_35af893405e534959b627033d842a49faecfd7ce1ca8976e87134e0fa22b6bf0` / `REV_d7a7826f0ad7375c69b1617ec2a6f4653b72ae2bdbca6b1b994ea59ed62d1502` | integration → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-INT-006-005` / `TC-IMPRANA-FR-INT-006-005` | `REV_b404c1a492d023951486538bc522f6800bd32b42a63d31f89552409e713b9c95` / `REV_61f9ca51b83c241fd26c8813ecfb2a65f1c67322b97ad01de1ebc31bea28ca34` | integration → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-INT-006-001 — Configure a webhook

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-006-001` is not created. Verification duty `TASK-FR-INT-006-03` (qualification); source `docs/backlog/backlog.csv` record 347, exact block `4b6b7a48651ef245f3b3725fe0dd1a5a3dd5b2d7ca429e866798c5feb7734f91`.

**Original preconditions**

1. the Integration Developer configures a webhook destination and event types

**Original actions**

1. the configuration is saved

**Exact source oracles — all required**

1. destination control and permitted event types are verified
2. delivery attempts are visible

Legacy same-requirement reuse candidates: `TC-INT-006-01`, `TC-INT-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-006-002 — Duplicate and out-of-order deliveries

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-006-002` is not created. Verification duty `TASK-FR-INT-006-03` (qualification); source `docs/backlog/backlog.csv` record 347, exact block `7aabb9d9b2480153b184874eefa7332da3be829bf8aaf7036e46ffc46c13d3f3`.

**Original preconditions**

1. events v2 then v1 are each delivered twice to a qualified consumer

**Original actions**

1. the consumer processes them

**Exact source oracles — all required**

1. it records one effect per event
2. the resource state is not downgraded

Legacy same-requirement reuse candidates: `TC-INT-006-01`, `TC-INT-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-006-003 — Reject invalid authentication

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-006-003` is not created. Verification duty `TASK-FR-INT-006-03` (qualification); source `docs/backlog/backlog.csv` record 347, exact block `c31d3e22470a0f70467b7c5a49205ace440e6af5380dca87c30f1f08eac20c6e`.

**Original preconditions**

1. a delivery with invalid authentication

**Original actions**

1. the qualified consumer receives it

**Exact source oracles — all required**

1. the delivery is rejected without downgrading resource state

Legacy same-requirement reuse candidates: `TC-INT-006-01`, `TC-INT-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-006-004 — Reject sensitive payloads and unchecked destinations

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-006-004` is not created. Verification duty `TASK-FR-INT-006-03` (qualification); source `docs/backlog/backlog.csv` record 347, exact block `35af893405e534959b627033d842a49faecfd7ce1ca8976e87134e0fa22b6bf0`.

**Original preconditions**

1. a webhook subscription

**Original actions**

1. an event is delivered

**Exact source oracles — all required**

1. no sensitive unrestricted payload is sent by default and details are fetched through current scope
2. destinations and redirects undergo the same outbound policy checks

Legacy same-requirement reuse candidates: `TC-INT-006-01`, `TC-INT-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-INT-006-005 — Reject retries after revocation

Source persona: Integration Developer. Proposed fixture `FIX-FR-INT-006-005` is not created. Verification duty `TASK-FR-INT-006-03` (qualification); source `docs/backlog/backlog.csv` record 347, exact block `b404c1a492d023951486538bc522f6800bd32b42a63d31f89552409e713b9c95`.

**Original preconditions**

1. a webhook with pending retries

**Original actions**

1. the webhook is revoked

**Exact source oracles — all required**

1. no further retries are sent

Legacy same-requirement reuse candidates: `TC-INT-006-01`, `TC-INT-006-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
