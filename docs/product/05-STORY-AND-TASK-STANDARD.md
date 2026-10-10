# Story and technical task standard

Owner: Nakul Jain · Prepared 10 October 2026 · Planning source: `8a1e405f0086033dfb25ad834689a08bfe9f1eea` · Status: proposed operating standard, to confirm at planning.

This standard makes a story traceable from the [product vision](01-VISION.md), [strategy](02-STRATEGY.md) and [release goals](04-RELEASE-GOALS.md) to the evidence needed for acceptance. It extends the [working agreement](../agile/WORKING-AGREEMENT.md); it does not replace the backlog, turn existing implementation into accepted work, or commit the next sprint. The [Sprint 1 review](../sprints/SPRINT-01-REVIEW.md) remains the evidence and acceptance record for the four built stories. The [next-sprint refinement](06-NEXT-SPRINT-REFINEMENT.md) contains the first proposed technical breakdown.

## 1. Trace every level

| Level | Required record | Parent and purpose |
| --- | --- | --- |
| Vision | Stable vision ID, intended user and long-term outcome | `VISION-IMPRANA-01`; the charter defines the product's direction |
| Strategic objective | Objective ID, outcome hypothesis, measure and evidence source | `STR-*`; references the vision, with unmeasured claims labelled hypotheses |
| Release goal | Goal ID, scope, entry/exit conditions and open decisions | `RG-*`; references the relevant objectives, with no assumed completion date |
| Epic | Canonical `EPIC-*` ID, capability boundary, release and objective links | Groups stories that contribute to an outcome; an epic's completion is not inferred from a task count |
| Story | Existing backlog ID, persona, behaviour, benefit and acceptance/rejection scenarios | Native issue parent is the epic; retain release-goal and objective IDs in the description |
| Technical task | Stable `TASK-<story ID>-<sequence>` ID, concrete deliverable, criteria and dependencies | Native issue parent is the story; inherit its higher-level links and name cross-story dependencies |

Linear native hierarchy is epic issue → story issue → technical subissue. Release goals map to the project's five release milestones. Vision and strategic objectives are linked in the project documents and issue descriptions; they do not need artificial delivery issues. The repository story ID stays the canonical identity even when Linear assigns a different display identifier. Split parents `US-DX-01` and `FR-AI-016` remain historical references; the active slices retain `split_from` links and are counted once.

A story card must retain the following fields, either directly or through explicit links:

```text
Canonical story ID / title:
Vision ID / strategic objective IDs / release-goal ID:
Epic ID / native parent issue / split-from ID (if applicable):
Source backlog row / source commit:
Persona / platform role / capability and scope:
As a …, I want …, so that …:
Outcome hypothesis / how we will measure it / baseline known or unknown:
Current implementation / requested slice / excluded follow-on work:
Functional rules / screens / API / persistence / events:
Positive and rejection Gherkin scenarios / rejection summary:
Applicable NFR IDs / story-specific measurable checks:
Security and privacy boundaries / release-review impacts:
Dependencies / unresolved decisions / owner and engineer:
Existing story points (if any) / sprint proposed or committed:
Workflow status / build status / acceptance status, separately:
Technical task IDs / exact evidence references:
Ready decision / Done decision / dated product-owner acceptance:
```

For each task, write what will be produced, where it connects to the implementation, how its result will be demonstrated, and what blocks it. Tasks may cover a contract decision, schema, governed service flow, screen, recovery path or a qualification obligation. Avoid one task per file and generic repetitions such as “implement”, “test” and “document” without a concrete result. Task completion can be reviewed while the parent story still needs integration or owner acceptance.

## 2. Write observable acceptance and rejection

Scenarios describe an actor, a state, an action and an observable outcome. Every story includes a positive case and at least one named `Scenario: Reject ...`. Rejections must also state the absence of harmful side effects: no write, no disclosure, no provider call or no second settlement as appropriate. Add stale-revision and retry behaviour for writes, current-authority checks for reads and replays, and relevant recovery or concurrency cases. Do not apply an independent-approval rule to an ordinary preference or draft lock unless the story actually introduces an approval decision.

```gherkin
Scenario: Save a complete ordered diagnosis
  Given an Executive Director acting as TENANT_ADMIN with the diagnosis capability
  And a diagnosis draft whose problems each have supporting evidence and a priority
  When they complete the diagnosis against its current revision
  Then a new complete revision records the ordered problem IDs and evidence references
  And the audit and operation receipt identify that revision

Scenario: Reject completion against a stale revision
  Given another editor has saved a newer diagnosis revision
  When the first editor completes against the older revision
  Then the command returns a documented 409 conflict
  And the newer revision and its order are unchanged

Scenario: Reject evidence outside current authority
  Given a referenced evidence revision is unavailable to the current actor
  When the actor tries to use it to complete the diagnosis
  Then the command fails without revealing the hidden evidence's title or content
  And no complete diagnosis revision is created
```

These are proposed scenarios, not passing-test claims. Refined scenarios add detail to the source criteria; they must not silently narrow or delete a backlog requirement. A decision that changes scope is recorded on the story, with the owner and date. Baseline values, credits, benefits and usage outcomes are not invented to make a scenario appear measured.

## 3. Define NFR and security obligations before building

Every story names the applicable platform NFR stories and its own measurable checks. For example, VF-DIN-002 governs concurrent changes and retries, VF-AUD-001 governs audit coverage/retention, VF-UX-001 governs WCAG 2.2 AA and manual keyboard/assistive-technology review, and VF-AVL-002 governs dependency degradation. An ordered form must work using the keyboard; a budget reservation must prevent overspend under simultaneous requests on native PostgreSQL; an immutable lock must survive process restart; an alert needs evidence of user-visible delivery. Use a source target where one exists. A new latency target, participant limit, budget-unit conversion or usability target is an open refinement decision until confirmed; never present an arbitrary estimate as an agreed requirement.

The [repository rules](../../AGENTS.md) and [engineering brief](../current/ENGINEERING-BRIEF.md) apply to every task. Story cards must identify the controls their changes touch:

- Tenant ID in all tenant keys and foreign keys, ENABLE and FORCE RLS with `tenant_fence`, transaction-local tenant context and narrow runtime-role grants.
- Tenant write lock before resolving write authority; current grants rechecked for commands, reads, replays, job execution and result disclosure.
- Closed write DTOs, rejection of unknown fields and duplicate JSON keys, bounded inputs, and server-owned actors, timestamps, policy pins and lease metadata.
- Immutable revisions and append-only audit/receipts; atomic head, projection, audit, outbox intent and receipt. External calls happen outside database transactions.
- Hidden and missing selectors both return `RESOURCE_UNAVAILABLE` 404; a client-selected ID is never proof of access. Read, export, approval, publication and sensitive access remain distinct.
- New capabilities are wired through generated contracts, fixture grants, the access profile and the web area's capability prefix. Existing tenant ceilings widen only through the reviewed upgrade path.
- A migration, contract, access-policy or AI-module change has a new impact-review entry in the applicable build's release review, with changed threats and named control tests recorded as needed.

Migration numbering and versions belong to implementation integration. This planning package assigns neither a final migration filename nor a build/API version. At the planning source the next available migration is 0044; recheck the actual migration ledger before assigning it. Applied migrations stay byte-identical, including 0041–0043 already present in the source checkout.

## 4. Keep workflow, implementation and acceptance separate

| Record | Meaning | Allowed interpretation |
| --- | --- | --- |
| Backlog / proposed task | Work described for refinement | No sprint commitment, assignee, elapsed-time estimate or implementation evidence implied |
| Ready | Owner and engineer have resolved the Ready checklist | Eligible for selection; still not selected |
| Sprint selected | Team confirms goal, scope and capacity at planning | The story belongs to a committed sprint |
| In progress | A task or story is being built | A design or partial screen is not acceptance evidence |
| In review | Built scope has evidence and awaits required review/acceptance | Sprint 1's four stories stay here until their remaining Done conditions are met |
| Done | All Done conditions, including product-owner acceptance, are recorded | Never inferred from a merged branch, green tests, task totals or an AI review |
| Split | Historical parent decomposed into active slices | Historical reference, not an extra active story or delivery item |

The backlog's `Built today` field is a historical implementation assessment. `Partial` does not prove the new slice exists, and `Absent` can be stale after building. Preserve the source value for traceability and record new engineering evidence separately. No new planning task is Done by inheritance from an existing implementation.

## 5. Definition of Ready

The owner and implementing engineer record a dated Ready decision only when all of these are resolved:

- The persona, benefit hypothesis and hierarchy links are agreed, and the behaviour is small enough to finish within one sprint.
- Positive, rejection and relevant boundary scenarios are reviewed without weakening the original requirement.
- API, data model, screen changes, permissions, evidence handling and proposed migration needs are concrete. The integrator will allocate the migration number at implementation time.
- Story-specific NFR checks and applicable platform NFR IDs are named, with exact evidence planned.
- Dependencies are available or deliberately selected in the same sprint with an executable order; unresolved owner decisions have been closed or explicitly removed from the slice.
- Technical tasks and their dependencies are reviewed, story points are confirmed and actual capacity is considered. Existing source points are planning inputs, not elapsed-time promises.

The four Sprint 2 candidates retain their original proposed tasks in [technical-tasks.json](technical-tasks.json). At Nakul's explicit request, [complete backlog refinement](10-COMPLETE-BACKLOG-REFINEMENT.md) now adds a separate task and scenario-test proposal for all 368 active stories. All 1,131 proposed tasks and 368 additive story sections are now native and read-back verified in the [continuation checkpoint](07-LINEAR-IMPORT-STATUS.md), covering 1,328 original scenario plans. Decisions remain explicit and source workflow states are unchanged. A complete written proposal does not establish Ready; the owner and engineer must resolve this checklist before selecting each slice.

## 6. Definition of Done and evidence record

Keep every condition in the [working agreement](../agile/WORKING-AGREEMENT.md): all scenarios pass in the required automated checks or a named manual check accepted by the owner; a person other than the author reviews the PR; lint, unit and relevant qualification checks are green; repository invariants hold; user text is plain and new screens meet accessibility checks; and the owner accepts the built scope at review. AI reviews supplement human review. Merge, deployment and paid execution still require their existing owner approvals.

Every evidence entry records the canonical story/task ID, scenario name, exact test node or browser/manual check, source commit, run ID or artifact path, environment, synthetic fixture, result and date. Record skips and unrun checks. For manual evidence, record the actor, steps, observed result and owner acceptance. Link the release note, PR and security-impact review where relevant. A future test name in a plan is labelled **proposed, not implemented or run**.

PGlite demonstrates application behaviour; it does not establish native PostgreSQL contention, forced RLS or login-role boundaries. Native evidence must use the provisioned non-owner roles and concurrent sessions where required. A queued outbox row proves intent; the delivered notification and consumer/delivery receipt prove in-app delivery. A provider request marker proves intent or an uncertain transmission, not a completed provider response or an agreed financial charge.

A story Done decision names the accepted revision and any residual limitations. If a bounded slice is accepted while a parent requirement still has unmet scope, retain that scope in active follow-on stories and do not mark the wider requirement accepted automatically.

## 7. Refinement and later technical tasks

The original 24-task next-sprint manifest remains an immutable planning baseline. Nakul's 10 October request authorises a full 368-story proposal now, saved separately in [backlog-refinement.json](refinement/backlog-refinement.json). Revisit each proposal with then-current code, owner decisions and capacity before implementation. Preserve stable IDs, original criteria and historical decisions; reconcile human changes rather than recreating or resetting imported Linear issues. Nakul approved and completed this native task/story expansion. Future updates reconcile the durable receipts and current human changes; the optional additional overview document has a separate pending upload approval.
