## QA v1.3 — source-bound case design (proposed)

Story `FR-OFF-007` · 4 original criteria · DESIGN_ONLY · execution **Not run**.
Original Gherkin remains authoritative. These proposed case/revision identities, modes and reuse candidates do not grant applicability, ownership, approval or an automated binding. Full local draft source: `docs/qa/standards-completion-20261011/case-design/`; this is not a remote-file export claim.

| Original criterion / proposed case | Proposed AC revision / case revision | Proposed method / binding |
| --- | --- | --- |
| `AC-FR-OFF-007-001` / `TC-IMPRANA-FR-OFF-007-001` | `REV_fe2245d3118e3ce930826e7eb0fe5ab3f629bf95815143b294b261bb6329dde1` / `REV_727298e154b854b00dc39d39e39b68c872f6cbce71fb0666933ab0bda5b568e4` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-007-002` / `TC-IMPRANA-FR-OFF-007-002` | `REV_27bed95d4c4130690fad981624cafd3100bec70d48975943fe88b38ecb6cfd84` / `REV_731cadfcb271e11c431993974bec8bdf39e3f47bedf362dab79b576f13fb2777` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-007-003` / `TC-IMPRANA-FR-OFF-007-003` | `REV_ea9bc904fdc945ce6b252b72ceba48ef08a6bab09daa835738bd5e40bac47936` / `REV_b561257a4fdce2f9ef678188dbcf6b00313e19ac1372449cef5c6e1015826fad` | browser → AUTO recommendation; UNRESOLVED; Not run |
| `AC-FR-OFF-007-004` / `TC-IMPRANA-FR-OFF-007-004` | `REV_398a281dac3e2f0da22bce608e09fd0c28989178c6ccbc0bca1ff5abd84b07c9` / `REV_61b6a0bd66997e47ad244e978d6099c7272c1023c76a6cfd198ca13dc92ac806` | browser → AUTO recommendation; UNRESOLVED; Not run |

Before execution: select an authorised exact scope/candidate/artifact/config/data/environment, agree fixture/input/role/capability, inspect reuse equivalence, bind every oracle and appoint actual independent reviewers where required. Applicability UNKNOWN; risk/owner/accepted mode unset. Missing automation remains an AUTO proposal rather than a MANUAL substitute.

### AC-FR-OFF-007-001 — Timestamped device status

Source persona: Programme Manager. Proposed fixture `FIX-FR-OFF-007-001` is not created. Verification duty `TASK-FR-OFF-007-03` (qualification); source `docs/backlog/backlog.csv` record 277, exact block `fe2245d3118e3ce930826e7eb0fe5ab3f629bf95815143b294b261bb6329dde1`.

**Original preconditions**

1. devices within the Programme Manager's scope

**Original actions**

1. the supervisor view is opened

**Exact source oracles — all required**

1. it shows last contact, last reported pending count, package version, expiry, known failures and unresolved conflicts
2. each value is timestamped

Legacy same-requirement reuse candidates: `TC-OFF-007-01`, `TC-OFF-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-007-002 — Disconnected device shows last-known state

Source persona: Programme Manager. Proposed fixture `FIX-FR-OFF-007-002` is not created. Verification duty `TASK-FR-OFF-007-03` (qualification); source `docs/backlog/backlog.csv` record 277, exact block `27bed95d4c4130690fad981624cafd3100bec70d48975943fe88b38ecb6cfd84`.

**Original preconditions**

1. a device reported two pending forms and then disconnected

**Original actions**

1. the Programme Manager views it

**Exact source oracles — all required**

1. the view shows two pending at last contact and current state unknown
2. no live count is shown

Legacy same-requirement reuse candidates: `TC-OFF-007-01`, `TC-OFF-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-007-003 — Request follow up or reassignment

Source persona: Programme Manager. Proposed fixture `FIX-FR-OFF-007-003` is not created. Verification duty `TASK-FR-OFF-007-03` (qualification); source `docs/backlog/backlog.csv` record 277, exact block `ea9bc904fdc945ce6b252b72ceba48ef08a6bab09daa835738bd5e40bac47936`.

**Original preconditions**

1. a device with unknown current progress

**Original actions**

1. the Programme Manager requests follow up or reassignment

**Exact source oracles — all required**

1. the request is recorded without claiming knowledge of unseen offline activity

Legacy same-requirement reuse candidates: `TC-OFF-007-01`, `TC-OFF-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.

### AC-FR-OFF-007-004 — Reject treating unknown progress as zero or wiped

Source persona: Programme Manager. Proposed fixture `FIX-FR-OFF-007-004` is not created. Verification duty `TASK-FR-OFF-007-03` (qualification); source `docs/backlog/backlog.csv` record 277, exact block `398a281dac3e2f0da22bce608e09fd0c28989178c6ccbc0bca1ff5abd84b07c9`.

**Original preconditions**

1. a disconnected device

**Original actions**

1. its status is shown

**Exact source oracles — all required**

1. it is not recorded as zero completed or guaranteed wiped
2. counts and locations outside the supervisor's scope are not shown

Legacy same-requirement reuse candidates: `TC-OFF-007-01`, `TC-OFF-007-02`. Their older procedures/statuses are retained; assertion equivalence and current qualification are unverified.

Current case gap: resolve exact fixture/input/observation channels, source applicability/risk/owner, automation or authorised manual procedure and actual current qualification evidence. Preserve failures/retries, source-required refusal audit and immutable history; a visible screen alone cannot prove an absence assertion.
