# Release 0.7.0 — reviewed exclusions and recalculation work centre

Build 0.7.0 · API 1.8.0 · additive migration 0010 · 26 September 2026.

This increment closes a bounded governance gap in the manual-measurement workflow. An approved collection-plan obligation can now be changed to an explicitly excepted obligation only through the existing independent change-review process. Any approval or governed correction that makes a provisional calculation stale creates a durable, personal recalculation task and a safe in-app notice. The assigned user can acknowledge the notice without closing the task and can execute an exact recalculation from the work centre.

This is a development release, not a complete enterprise product or production certification. External notification delivery, background workers, scheduled recalculation, cross-period fan-out, native PostgreSQL qualification and the remaining requirements in `COMPLETION-LEDGER.json` are still open.

## Delivered behaviour

### Governed eligibility exceptions

- Each collection obligation defaults to `REQUIRED` when eligibility is omitted, preserving compatibility with earlier approved plans.
- A proposed obligation may be marked `EXCEPTED` only with a non-empty reason and an effective UTC timestamp. Exception timestamps more than five minutes in the future are rejected.
- A plan must retain at least one required obligation. A proposal cannot erase the entire denominator by excepting every contributor.
- An exception to an approved plan is a `MeasurementChange`: it records the exact target and target revision, requires independent review, and creates a new approved plan revision. The earlier plan revision remains immutable.
- Coverage retains the historical expected count while reporting separate required and excepted counts. Excepted obligations remain visible with their reason and effective time, do not count as approved input, do not reduce the required-completion percentage, and do not block period close.
- An observation that matches an excepted obligation is excluded from calculation lineage with the explicit reason `APPROVED_OBLIGATION_EXCLUSION`; it is not silently discarded.

### Calculation invalidation and recovery

- Approval of an observation, approval of a collection plan, approval of an observation correction, and approval of a plan amendment inspect affected provisional result bindings inside the same database transaction.
- Each affected immutable result revision receives a durable invalidation record tied to the exact triggering revision, indicator, period and personal work item.
- Existing calculated-result reads are decorated with a current stale flag. A replacement calculation never overwrites the earlier result or its lineage.
- Invalidation fan-out is bounded to 500 affected result revisions and 500 bound periods per source event. A larger fan-out fails atomically with `LIMIT_EXCEEDED` instead of partially queuing work.
- The recalculation command loads current approved inputs, creates a new lineage manifest, job, result revision and binding, resolves all pending invalidations for that indicator-period, completes the task and emits a completion notice in one transaction.
- Exact command retry uses the existing actor-owned operation receipt. A changed body under the same operation identifier conflicts; a completed task cannot be run again under a new intent.
- Manual recalculation from the existing Results workflow also resolves any matching pending task, so users cannot be left with work that is already complete.

### Personal work and notices

- **My work** lists only tasks assigned to the current tenant principal and notices addressed to that principal. Detail reads enforce the same ownership rule and return the ordinary unavailable response to another user.
- A calculation task exposes its state, affected-result count, indicator, period, reason codes and replacement result identifier without copying source values into notification payloads.
- Notices carry an outbox event identity, a class and an opaque work-item reference. The safe in-app notice contains no source value, exclusion narrative or sensitive programme text.
- Acknowledgement is idempotent and per recipient. It records receipt but deliberately does not complete or dismiss the underlying action.
- Logical identifiers are deterministic for the same trigger/task/recipient class, preventing duplicate work items and notices on retry. Database uniqueness also protects exact invalidation retries.
- The UI supports acknowledgement and recalculation, reports command outcomes, disables unavailable actions and remains bounded at a 390-pixel viewport.

## Security and transaction rules

- The new invalidation and acknowledgement tables use forced row-level security against the transaction-local tenant context.
- The application role receives only `SELECT`/`INSERT` plus column-level update rights for invalidation resolution. It cannot rewrite immutable trigger, result, indicator, period or work-item identity.
- Work-item and notification list filters are implemented in SQL, not only in client rendering. Object detail responses repeat the current-principal check.
- Recalculation requires the existing `indicator.calculate` capability and a tenant-wide, non-purpose grant. A preferred collector is assigned only when currently eligible; otherwise the service selects a current eligible tenant principal or rejects creation with `RECALCULATION_OWNER_REQUIRED`.
- Notice acknowledgement requires `notifications.acknowledge`. Browser actions retain cookie, Origin and CSRF protection; API actions retain schema validation, optimistic revision checks, idempotency receipts, auditing and current-authority replay checks.
- Review independence is unchanged: the author of an eligibility change cannot approve it through another membership associated with the same natural person.

## Data and API changes

Migration `0010_work_and_recalculation.sql` adds:

- `impact.calculation_invalidation`, including immutable result/trigger references, pending/recalculated/cancelled state constraints, replacement-result references and a pending lookup index;
- `impact.notification_acknowledgement`, keyed by tenant and notification with the exact recipient and acknowledgement time;
- forced tenant RLS and bounded application-role grants for both tables.

API 1.8.0 adds six implemented domain operations:

| Method | Route | Capability |
|---|---|---|
| GET | `/v1/tenants/{tenant_id}/work-items` | `work-items.read` |
| GET | `/v1/tenants/{tenant_id}/work-items/{object_id}` | `work-items.read` |
| POST | `/v1/tenants/{tenant_id}/work-items/{object_id}/actions/recalculate` | `indicator.calculate` |
| GET | `/v1/tenants/{tenant_id}/notifications` | `notifications.read` |
| GET | `/v1/tenants/{tenant_id}/notifications/{object_id}` | `notifications.read` |
| POST | `/v1/tenants/{tenant_id}/notifications/{object_id}/actions/acknowledge` | `notifications.acknowledge` |

The collection-plan schemas accept eligibility evidence, and coverage responses can include `required_count` and `excepted_count`. The implemented domain surface now contains 106 operations. The broader design OpenAPI remains intentionally larger and is not an implementation claim.

## Qualification evidence

The final local gate passed:

- 220 application unit, contract, integration, security and smoke checks; one preserved offline-sync test remains explicitly deselected;
- 143 preserved reference assertions;
- 43 Chromium workflows: eight core, 12 access-administration, 17 measurement/change/work-centre, and six period/reporting workflows;
- Ruff lint/format, Prettier, TypeScript and Vite production build;
- migration application from a fresh database, forced-RLS cross-tenant denial, idempotent acknowledgement/recalculation, immutable old-result lineage and mobile UI checks.

The new primary evidence is `qualification/test_work_center.py`, the coverage unit vector in `qualification/test_measurement_unit.py`, `tools/browser/measurement-check.mjs`, `docs/evidence/work-center.png`, and the machine-readable test records under `docs/evidence`.

## Explicit limits

- Recalculation is user-triggered and synchronous. There is no leased background worker, scheduled retry, provider delivery or operational escalation.
- Notices are in-app records only. Email, SMS, push preferences, digests, provider attempts, bounces and mandatory security-notice routing are not implemented.
- Invalidation currently targets provisional result bindings for the same indicator-period. It does not regenerate annual/YTD aggregates, dashboards, unpublished reports, exports or distributed artifacts.
- Approved locked snapshots and published/frozen report packages never move automatically. Changing their data requires the separately reviewed restatement path.
- There is no bulk exclusion, prospective schedule regeneration, partner-lifecycle automation or attachment evidence.
- PGlite qualification does not establish native PostgreSQL concurrency, production throughput, backup/recovery, external identity or accessibility conformance.

These limits remain release gates in `NEXT-DELIVERY.md`; the conservative completion ledger marks only bounded tested behaviour as partial.
