# Next-sprint refinement: four proposed candidates

Owner: Nakul Jain · Prepared 10 October 2026 · Source: `8a1e405f0086033dfb25ad834689a08bfe9f1eea` · Status: **proposed; Sprint 2 is not committed**.

The [Sprint 1 plan](../sprints/SPRINT-01.md) and [review](../sprints/SPRINT-01-REVIEW.md) nominate these four next candidates. This document refines their behaviour and proposes six technical tasks per story in [technical-tasks.json](technical-tasks.json). All 24 tasks enter **Backlog**. Existing story points are copied from the source for discussion, with no new time estimates, dates or capacity commitment. No candidate is declared Ready before its open decisions and the [Ready checklist](05-STORY-AND-TASK-STANDARD.md#5-definition-of-ready) are resolved.

## Hierarchy and proposed order

All four stories serve [VISION-IMPRANA-01](01-VISION.md) and [RG-R1](04-RELEASE-GOALS.md). [STR-02](02-STRATEGY.md) concerns choosing the right problem and intervention; STR-03 concerns adoption with measured value; STR-01 concerns a trusted operating foundation.

| Story | Native parent epic / strategic links | Split parent | Source points / workflow status | Prerequisite |
| --- | --- | --- | --- | --- |
| US-DX-01a Record and prioritise the organisation's problems | `EPIC-ADOPTION-DIAGNOSE` / STR-02 | US-DX-01 | 5 / Backlog | Agreed problem model and permissions |
| US-DX-03 Locked baseline metrics per priority problem | `EPIC-ADOPTION-DIAGNOSE` / STR-02, STR-03 | none | 8 / Backlog | US-DX-01a stable problem IDs and revision links |
| FR-AI-016a AI jobs with budget reservation and cancellation | `EPIC-AI-CAPABILITIES` / STR-01, STR-03 | FR-AI-016 | 8 / Backlog | FR-AI-001 policy controls built; remaining review/acceptance explicit |
| US-CM-05 Visible AI usage credits and limits | `EPIC-COMMERCIAL-AND-BILLING` / STR-01, STR-03 | none | 5 / Backlog | FR-AI-016a's authoritative ledger and settlement rules |

The two dependency chains are diagnosis → baseline and reservation/jobs → usage/alerts. Contract refinement may proceed in parallel, but a dependent feature cannot invent a different problem identity or credit basis. The source's four Sprint 1 stories remain **In review**. Sprint 1 code merged in [PR #94](https://github.com/nakul175/impact-platform/pull/94); product-owner acceptance remains unrecorded. The committed [Sprint 1 review](../sprints/SPRINT-01-REVIEW.md) contains older pre-merge wording; future changes retain the current [AGENTS](../../AGENTS.md) review, CI and owner gates. This proposal does not mark the stories Done or assume that a provider destination has been approved.

The CSV contains 370 historical rows: 368 active stories and two `Split` parents. The active catalogue can be organised now; technical work for later stories will be refined when their dependencies and current implementation are known. This package does not claim that all future stories have Ready task plans.

## Cross-cutting requirement links

| Applies to | Requirement IDs / concrete obligation |
| --- | --- |
| All four candidates | VF-DIN-002 (atomic writes, stale rejection and retry integrity), VF-AUD-001 (receipts/events, bounded metadata and retention), VF-UX-001 (WCAG 2.2 AA plus manual keyboard and assistive-technology review); FR-SEC-001/003 (material-impact review and tenant isolation), FR-PRV-001 (classify new fields with purpose, owner and retention) |
| FR-AI-016a and US-CM-05 | VF-AVL-002 (AI failure/exhaustion leaves independently healthy manual paths available), FR-SEC-002/006 (sealed recoverability, key/secret protection and no plaintext fallback) |
| Any new persistence | Apply the existing populated-upgrade/restart/restore checks to the new records; this is supporting evidence for VF-DR-003, not acceptance of its wider monthly/disaster-recovery scope |

A clean automated accessibility scan alone does not pass VF-UX-001. Record the complete new process, browser/assistive-technology environment and named manual checks as well as automated evidence. Each task's release-impact review lists its relevant controls and exact tests without declaring the wider security/NFR requirements accepted.

## US-DX-01a: save an agreed, ordered problem diagnosis

**Story:** As an Executive Director, I want to record our organisation's problems in a structured, plain-language form and put them in priority order, so that the rest of the adoption journey starts from agreed priorities.

**Current implementation:** `AIEnablementProfile` captures a goal and readiness answers; `AIAdoptionPlan` persists adoption drafts. Neither supplies a diagnosis/problem entity or a durable priority order. The backlog's historical `Partial` assessment therefore does not prove this new slice exists. The existing profile, catalogue and plan history must remain readable without being silently converted into completed diagnoses.

**Proposed slice:** a tenant-scoped diagnosis draft with stable problem IDs, description, affected area, bounded supporting-evidence notes and optional explicitly authorised evidence-revision references. Completing it captures one immutable revision with a complete ordered list of problem IDs. Drafts may be incomplete; completion identifies every incomplete problem and refuses the state change. Reordering creates a new revision. This is structured manual input; conversational proposals remain US-DX-01b.

**API/data/security proposal:** closed create/update/reorder/complete commands use operation IDs and expected revisions. Select a separate governed registry kind and current projection at design review; do not append fields to `AIAdoptionPlan` without a compatibility decision. Any new table has tenant-keyed primary/foreign keys, forced RLS and narrow `impact_app` grants. Bind external evidence to exact revisions, recheck current authority and never disclose a hidden title. Read and manage capabilities must be explicit in contracts, fixtures, the access profile and the web navigation. Executive Director maps to TENANT_ADMIN; OWNER custody does not authorise tenant data work. A diagnosis completion is not an independent approval or an official impact calculation.

**NFR checks:** fully usable by keyboard; saved order survives reload/restart; a stale save preserves the current revision; input remains on validation or permission failure; AI off produces no provider calls. List bounds and signed cursor bindings follow the existing platform rules. Apply the relevant security, data-integrity and accessibility NFR stories at refinement; no new latency or “minutes saved” target is assumed.

```gherkin
Scenario: Save and reopen prioritised problems
  Given an Executive Director with diagnosis manage permission
  When they record problems with a short description, affected area and supporting evidence
  And complete the diagnosis with the problems in priority order
  Then the complete revision retains stable problem IDs, that order and that evidence
  And reopening it shows the same data without an AI provider call

Scenario: Reject completion with evidence or priority missing
  Given a draft problem missing supporting evidence or a place in the priority order
  When the Executive Director completes the diagnosis
  Then completion is refused and each incomplete problem is named
  And the saved draft remains available

Scenario: Reject stale or duplicate-priority commands
  Given the diagnosis revision has changed or the submitted order repeats a problem ID
  When an update or completion is submitted
  Then the documented conflict or validation response is returned
  And no complete revision with that invalid order is created

Scenario: Reject an inaccessible evidence selector without leakage
  Given a referenced evidence revision is hidden or missing
  When it is added to a diagnosis
  Then the response is 404 RESOURCE_UNAVAILABLE in both cases
  And no title or content from that evidence is returned
```

**Open before Ready:** whether one or multiple diagnoses may be active per tenant; affected-area vocabulary and text/list bounds; which evidence types satisfy completion; completion/correction semantics; exact capability names and role/scope matrix. Confirm whether diagnosis completion must be explicitly superseded when priority order changes. The design task resolves these choices; the plan does not quietly treat them as owner decisions.

| Task IDs | Proposed deliverable |
| --- | --- |
| TASK-US-DX-01a-01 | Problem identity, completion/correction rules and closed API contract |
| TASK-US-DX-01a-02 | Tenant-fenced projection/revision design and additive schema changes |
| TASK-US-DX-01a-03 | Atomic create, edit, reorder and completion services with exact retry |
| TASK-US-DX-01a-04 | Current evidence authority and capability/profile wiring |
| TASK-US-DX-01a-05 | Accessible structured form with recovery of unsaved input |
| TASK-US-DX-01a-06 | Scenario evidence, native boundaries and compatibility review |

## US-DX-03: capture and preserve a baseline per priority problem

**Story:** As an Executive Director, I want to record baseline metrics for each priority problem, so that we can later prove what changed.

**Current implementation:** `ai_pilot_outcomes.py` compares self-reported drafting and review minutes, sample sizes and correction counts. Those comparisons are drafts and do not capture time, cost, quality and reach for each durable priority problem or lock an adoption baseline. Core programme targets/baselines have different official-result rules and must not be repurposed by assumption.

**Proposed slice:** a baseline draft references a specific diagnosis revision and stable problem ID, captures all four measures with their agreed units/bases and source notes, and locks one immutable metric revision with a server-set actor and date. Missing is distinct from a measured zero. A lock preserves observations; it does not prove a causal benefit, monetary saving or officially approved result. Any later material correction creates a separately identified successor with a reason if the owner selects that correction model; no command edits or unlocks the old locked metrics.

**API/data/security proposal:** closed baseline save and lock commands, expected baseline and problem revisions, tenant-scoped composite references and append-only lock evidence. Store exact decimal values as transport strings and use NUMERIC(38,12) for persisted quantities where applicable; bind units/currency, reporting window and denominator/sample basis rather than inferring them from the current profile. Exact DTOs depend on the metric decision. Actor/date/state are server owned. Reads and history check current authority; removed/restricted evidence stays hidden. TENANT_ADMIN is the persona's platform role. No new independent-approval workflow is inferred from “lock”.

**NFR checks:** preserve exact submitted observations and metric definitions across restart; no floating-point conversion; locked bytes and lock date remain unchanged after rejected edits; a stale or duplicate lock cannot create two lock records; keyboard review/confirmation works. No percentage improvement, ROI or assumed benefit is produced by this slice.

```gherkin
Scenario: Capture and lock all four measures
  Given a priority problem in a complete diagnosis revision
  When the Executive Director saves time, cost, quality and reach with their agreed units and source basis
  And locks the current baseline revision
  Then the locked record names the exact problem and metric revisions
  And a server-set lock date and actor are recorded
  And reopening the baseline shows the original observations

Scenario: Reject an incomplete lock
  Given a baseline missing any of time, cost, quality or reach
  When the Executive Director locks it
  Then locking is refused and the missing measure is named
  And no lock record is created

Scenario: Reject changing locked observations
  Given a locked baseline
  When anyone tries to edit its metrics or supply another lock date
  Then the command is refused
  And the locked observations and server-set date are unchanged

Scenario: Reject a lock after its source problem changes
  Given the baseline draft was made against an earlier problem revision
  When the diagnosis changes materially and the baseline lock is submitted
  Then the command returns the documented conflict
  And the actor must review the new source before locking
```

**Open before Ready:** define the four metrics and units, the meaning of quality/reach and any denominator, time/cost period and currency, required evidence, and correction/supersession policy. Decide whether a new diagnosis priority order alone is material to a baseline lock. Existing pilot sample data is not a default baseline. Confirm the read/manage/lock scope and keep the official MEL approval boundary explicit.

| Task IDs | Proposed deliverable |
| --- | --- |
| TASK-US-DX-03-01 | Metric definitions, source binding and closed save/lock contracts |
| TASK-US-DX-03-02 | Tenant-scoped baseline projection and insert-only lock register |
| TASK-US-DX-03-03 | Decimal validation and atomic immutable-lock transitions |
| TASK-US-DX-03-04 | Per-problem screen with completeness checks and lock confirmation |
| TASK-US-DX-03-05 | Authorised history and correction/supersession integration |
| TASK-US-DX-03-06 | Lock races, exact observations, native boundaries and acceptance evidence |

## FR-AI-016a: bounded jobs, reservation and cancellation

**Story:** As a MEL Manager, I want each AI request to run as a job that reserves budget, shows progress and can be cancelled, so that AI work stays within its limits and never blocks close or reporting.

**Current implementation:** `ai_enablement.py` handles advisory requests synchronously, records an insert-only request and sealed result, and limits the tenant to three attempts per 24 hours. `ai_policy.py` checks that `budget_units` is positive; it does not deduct or meter it. `application_executor.py` claims only IMPORT_COMMIT and runs as `impact_executor_login`, a member of `impact_app`. `worker.py` executes its own classes and its generic cancellation pass cancels pre-start jobs without settling an AI reservation; running jobs get `NOT_CANCELLED_STARTED`. None of these is an existing AI job/credit ledger.

**Proposed slice:** ADVISORY_DRAFT requests pass the server/use-case/current-policy gate, estimate a bounded maximum in the agreed budget unit, and atomically reserve that amount with a job and operation receipt. The response is 202 with a stable job ID. Job progress uses actual states/stages; it must not fabricate percentages. Exact retries return the same job under current authority, and changed payloads conflict. Queued cancellation releases unused reservation; a running cancellation prevents the next controllable model/tool call and separately accounts for provider work already accepted. The existing provider deadline remains a runtime bound; new timeout/partial-draft behaviour stays FR-AI-016b. EXTRACTION, REPORT_DRAFT, CHAT and tools remain disabled/reserved unless their own stories change the policy.

**Budget invariant proposal:** for a named tenant/use-case budget window, `consumed + outstanding reserved <= limit`. Available is `limit - consumed - outstanding reserved`; never double-subtract completed reservations. Before each controllable provider call, reserve a proven upper bound, including a bounded input and output allowance. If actual usage cannot be known after an ambiguous provider acceptance, account conservatively within that reservation and expose the uncertainty for reconciliation; do not release it as zero or automatically repeat a possibly accepted call. Exactly one terminal settlement per job transfers accounted consumption and releases the unused portion. A later reconciliation uses a new journal adjustment, with no second terminal settlement or rewrite. Policy edits do not silently replenish the window or erase past usage. A quota is not data permission and must never gate manual close or reporting.

**API/data/security proposal:** proposed tenant-keyed budget-window, job/reservation, provider-attempt and append-only journal/settlement records link to the exact policy version, requester and job. Use the existing job lease-generation model only after defining AI execution and cancellation ownership. The implementation must keep provider I/O outside database transactions, recheck current requester authority and in-force policy before every next controllable call, fence result/settlement on the lease owner/generation, seal stored input/output and log only bounded reason codes. A lost/stale executor must not create another paid call or settle again. Isolate AI cancellation from the generic worker pass, or make that pass delegate to the settlement-aware transition atomically. Do not widen the worker to tenant application data as a shortcut.

**NFR checks:** native simultaneous requests cannot overspend; cancel/complete/takeover races settle once; restart preserves pending job and accounting; unavailable ledger/policy fails closed before transmission; core approvals/calculation/close/reporting succeed with AI budget exhausted. MEL Manager maps to MEL_ADMIN. Existing `ai.advisory.request` is distinct from job visibility and cancellation; settle the own-job/tenant-admin scope matrix before building. Retain the existing daily attempt cap until an explicit contract decision changes it.

```gherkin
Scenario: Reserve a permitted job
  Given ADVISORY_DRAFT is enabled in the current policy and enough budget remains
  When a permitted MEL Manager submits the bounded request
  Then the response is 202 with one job ID
  And the maximum estimated units are reserved atomically with that job
  And progress and a Cancel action are available

Scenario: Cancel without hiding accepted provider work
  Given a job with a reservation and a provider attempt already accepted
  When the requester cancels it
  Then no new controllable provider call starts
  And accepted or uncertain provider work is accounted separately
  And one terminal settlement releases only the unused reservation

Scenario: Budget exhausted leaves manual work available
  Given the tenant's AI budget is exhausted
  When the MEL Manager approves data, calculates results, closes a period and generates a non-AI report
  Then those operations complete under their ordinary permissions
  And no AI provider call is needed

Scenario: Reject a reservation beyond the budget
  Given the available budget is smaller than the bounded estimate
  When a request is submitted
  Then the response is 429 with reason AI_BUDGET_EXHAUSTED
  And no job or reservation is created and no provider call occurs
  And the client retains the user's input

Scenario: Reject a stale executor settlement
  Given another executor holds a newer job lease generation
  When the old holder records a result or settlement
  Then its write is refused
  And no additional consumption, release or visible result is recorded
```

**Open before Ready:** budget-unit conversion and its maximum-call bound; budget window/reset and limit-change rules; how ambiguous acceptance is conservatively accounted/reconciled; executor topology/sealing-key access; job visibility/cancel scopes; synchronous-advisory compatibility (new route or an explicit changed contract). No provider/region is approved for live use. Synthetic provider qualification can proceed after the design decisions; turning AI on and paid calls remain separate owner decisions. If these rules do not fit one sprint, split this candidate before commitment.

| Task IDs | Proposed deliverable |
| --- | --- |
| TASK-FR-AI-016a-01 | Budget-unit/window contract, state machine and execution ownership |
| TASK-FR-AI-016a-02 | Tenant-fenced reservation, journal, attempt and terminal-settlement persistence |
| TASK-FR-AI-016a-03 | Current-policy request gate and concurrent atomic reservation/202 service |
| TASK-FR-AI-016a-04 | Lease-fenced executor, pre-call gate and ambiguous-provider recovery |
| TASK-FR-AI-016a-05 | Cancellation-aware terminal settlement and generic-worker integration |
| TASK-FR-AI-016a-06 | Honest progress/cancel UI plus concurrency, restart and AI-off evidence |

## US-CM-05: visible authoritative usage and delivered threshold alerts

**Story:** As an Operations Head, I want to see AI usage credits and limits, so that there are no surprise costs.

**Current implementation:** there is no `ai.usage.read` capability or metered usage screen. FINANCE can read AI enablement under the Sprint 1 access profile, but cannot manage it. `work.py` and `delivery.py` supply tenant-scoped in-app notification intents; the worker records delivered in-app notices using delivery and consumer receipts. FR-OPS-002 is a broader R2 entitlement story, not an available R1 entitlement system.

**Proposed slice:** expose the agreed limit, accounted consumption, outstanding reservation and available credits with the budget window, unit basis and as-of time. Break usage down by the requester, including accounted provider work after cancellation and uncertainty as its own state. Alerts at 80% and 100% name their usage basis and must be visible to the authorised Operations Head. The proposed warning basis is committed consumption plus outstanding reservation (budget exposure); display consumed usage separately and confirm this interpretation at refinement. A jump across both thresholds records both alerts. Releasing a reservation does not generate repeated alerts for the same threshold/window; the next budget window has its own keys. Zero limit and unavailable data never produce a fabricated percentage or balance.

**API/data/security proposal:** a closed usage response and bounded principal breakdown read from FR-AI-016a's authoritative journal, in one consistent read, with no new editable balance or billing ledger. Any cached projection is reconstructible and reconciled to the journal. Proposed `ai.usage.read` grants FINANCE read-only usage; confirm other roles and personal-data display. New profile registration and reviewed existing-tenant access upgrades are part of the task. Alerts need tenant/window/threshold/recipient uniqueness and atomic notification/outbox creation; the API never writes a delivery receipt as proof of receipt. Recheck current recipient membership/capability on delivery and do not leak a former user's private identity details.

**NFR checks:** exact balances under reserve/settle/release races; bounded user breakdown without false zeroes; keyboard/screen-reader-readable units and uncertainty; idempotent alert replay/restart. In-app delivery is the proposed required channel. Email delivery is not assumed or commissioned by this story. Export of usage is a distinct permission and outside this slice.

```gherkin
Scenario: See balance and per-user accounting
  Given a FINANCE Operations Head with ai.usage.read
  When they open the usage view
  Then limit, consumed, reserved and available units are shown for the named window
  And the view states its as-of time and unit basis
  And authorised per-user amounts reconcile to the tenant total

Scenario: Deliver both threshold alerts
  Given budget exposure below 80 percent of the finite limit
  When an atomic reservation or settlement makes it reach 100 percent
  Then an 80 percent notice and a 100 percent notice are recorded for the authorised recipient
  And both are visible in their in-app notifications with delivery evidence
  And retrying or restarting does not create duplicate threshold notices

Scenario: Reject threshold success without delivery evidence
  Given the 80 percent or 100 percent threshold has been crossed
  And only an outbox intent exists with no delivered in-app notice
  When acceptance is assessed
  Then that threshold's alert scenario is not passed

Scenario: Reject a hidden tenant's usage request
  Given a usage reader supplies another tenant's selector or has lost the capability
  When they request balance or per-user usage
  Then the resource is unavailable under the platform's hidden-resource rules
  And no balance, user identity or limit is disclosed
```

**Open before Ready:** credit terminology and exposure-versus-consumption threshold basis; alert recipients and required delivery channel; window-reset and policy-change behaviour; per-user identity/retention rules; zero-limit display; which roles beyond FINANCE read tenant usage. Resolve the dependency on FR-OPS-002 by building only the AI-specific slice and retaining the broader entitlement scope there. Do not require an unbuilt R2 system to appear complete for this R1 story.

| Task IDs | Proposed deliverable |
| --- | --- |
| TASK-US-CM-05-01 | Usage/threshold semantics, recipient rules and closed read contract |
| TASK-US-CM-05-02 | Consistent exact ledger queries and reconstructible aggregation |
| TASK-US-CM-05-03 | Read-only FINANCE capability, access-profile upgrade and hidden-resource enforcement |
| TASK-US-CM-05-04 | Durable threshold transitions and delivered in-app notice evidence |
| TASK-US-CM-05-05 | Accessible usage screen with window/basis/uncertainty labels |
| TASK-US-CM-05-06 | Reconciliation, threshold/restart/role tests and owner-review evidence |

## Evidence to build, not results already obtained

The task manifest names proposed test nodes and browser checks. They are a plan, with no implementation, run or pass implied. Reuse existing regression anchors where relevant: `qualification/test_ai_policy.py::test_core_workflows_complete_with_every_ai_use_case_off`, `qualification/test_ai_enablement.py::test_exact_replay_after_a_policy_change_returns_the_original_draft_only`, `qualification/test_import.py::test_large_commit_is_queued_fenced_and_reviewed`, `qualification/test_worker.py::test_queued_job_cancellation_is_honoured_and_a_running_job_is_not_cancelled`, and the existing `tools/browser/a11y-check.mjs`. Preserve the prior behaviour for existing classes while adding settlement-aware AI cancellation.

For each built task, record source commit, named scenario, exact test/check and synthetic fixture, environment, result and artifact. Use native provisioned roles for RLS and native concurrent sessions for reservation, lock, cancellation and settlement races. Include restart and populated-upgrade proof when new persistence is introduced, with a newly allocated additive migration and security-impact review. Do not publish a focused run as a full-suite result. Product-owner review validates the actual built scope and remaining limits; it is not replaced by this plan or by an AI reviewer.
