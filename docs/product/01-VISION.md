# Imprana Commons vision

Owner: Nakul Jain · Prepared 10 October 2026 · Status: proposed product planning baseline; product scope approval pending.

Vision ID: `VISION-IMPRANA-01`.

## Purpose

**Imprana Commons is the operating system for impact organisations.** It should help an NGO or impact organisation move from a real problem to a working AI or technology solution, adopt it in everyday work, and measure whether it improves outcomes. Monitoring, evaluation and learning (MEL), impact reporting and AI enablement form one platform, sharing programme context, permissions, evidence and accountable decisions.

The existing Impact Platform supplies the development foundation. Its governed measurement workflow, saved adoption plans, guidance and AI controls provide bounded implementation evidence. Implementation and acceptance records are in [HANDOVER](../HANDOVER.md), [IMPLEMENTATION](../IMPLEMENTATION.md), the [completion ledger](../COMPLETION-LEDGER.md) and the retained [Sprint 1 review](../sprints/SPRINT-01-REVIEW.md); the [strategy](02-STRATEGY.md) clarifies the review's older pre-merge wording. This vision is target direction; it does not declare any story accepted or the product ready for production. Current use remains restricted to synthetic data.

## Who it serves

| User | Problem to solve | Intended benefit |
| --- | --- | --- |
| Executive Director and Operations Head | Too many possible interventions, uncertain costs and weak evidence of fit | Choose a bounded problem and an accountable investment decision |
| MEL Manager, Programme Manager and Analyst | Plans, delivery evidence and reporting are disconnected | Compare progress and outcomes with approved baselines and trace the sources |
| Data Author, Field Data Collector, Reviewer and Data Steward | Collection and correction create manual effort and unreliable records | Collect once, review independently and reuse approved evidence |
| Organisation Administrator and Privacy Officer | Access, disclosures and AI use can exceed authority | Control who can act, what can leave the organisation and which AI use is allowed |
| Staff adoption lead, Imprana Advisor and Solution Partner Manager | A shortlist does not become a usable workflow by itself | Record trial evidence, deployment responsibilities, training and follow-up |
| Funder Portfolio Manager | Needs evidence across a sponsored cohort while grantees retain control | Receive authorised progress and outcome reports with clear limitations |

These are business personas. Platform permissions follow the [persona to role map](../agile/PERSONA-ROLE-MAP.md); a persona label never grants access. A programme participant remains a data subject, not an assumed platform user.

## The connected journey

| Stage | Decision or evidence carried forward |
| --- | --- |
| Diagnose | Prioritised problem, supporting evidence, readiness and baseline |
| Map | Suitable AI, technology or process opportunities with explained priorities |
| Discover | Vetted options, fit reasons, sources and commercial disclosures |
| Assess | Trial scope, safe inputs, acceptance checks and recorded results |
| Value case | Costs, benefits, assumptions and an approved baseline for comparison |
| Deploy | Workflow changes, named owners, milestones and acceptance evidence |
| Adopt | Role-based training, internal champions and observed use |
| Improve | Equivalent before/after measures, realised outcomes and a decision to continue, change or stop |

Each stage should reuse the previous stage's evidence. An organisation must be able to conclude that a process change or a non-AI tool is the best answer. A catalogue listing, generated draft, self-recorded checklist or predicted ROI alone is insufficient evidence of successful delivery.

## Outcomes to learn about

The proposed outcomes are better problem selection, less avoidable work, safer adoption and more trustworthy impact reporting. Measure the current process before a trial, then compare equivalent tasks afterwards. Record total staff and review time, corrections, delivery acceptance, training evidence, actual use, support effort and incidents. Value cases must distinguish assumptions, forecasts and measured results; cost and benefit calculations must show their sources. Numeric improvement targets, pilot cohort size, languages, geography and commercial targets remain owner decisions.

## Trust that cannot be traded away

Tenant isolation and deny-by-default access apply across MEL and AI journeys. Approvals require a different natural person from every material author; aliases and extra logins do not create independence. Official arithmetic uses approved, versioned deterministic rules and approved source revisions. AI proposes and may be switched off without blocking collection, independent review, calculation, period close or reporting. Report approval, publication and wider disclosure remain separate decisions. Approved records and frozen reports preserve their history.

## From vision to delivery

The [strategy](02-STRATEGY.md) chooses priorities; the [roadmap](03-ROADMAP.md) sequences outcomes; [release goals](04-RELEASE-GOALS.md) define the evidence required for each bucket. The source [backlog](../backlog/backlog.csv) contains 368 active stories across 54 epic/areas, plus two retained split parents. Stories, acceptance and rejection criteria and technical tasks should trace back through that chain. Authorisation to prepare this structure and Linear integration is recorded separately from approval of product scope.


<!-- imprana:bundle-v4.2:documentation:20261011 -->

Application source 8a1e405f0086033dfb25ad834689a08bfe9f1eea; planning source eb194fdbb6fc8247db8429fc23120aa0fe659ed8; build 0.39.0, domain API 1.28.0, platform API 1.11.0, schema 43. These are source pins, not a fresh deployed-runtime assertion.

This edition applies the attached Product Management Agent Bundle v4.2 / standard 3.0-generic to Imprana Commons. It adds source-bound product reasoning and executable evidence plans. Original requirements, Gherkin, estimates, priorities, workflow states, release allocations, historical decisions and human edits remain authoritative. Recommendations below are not user research, a test execution, Ready/Done, an approved sprint, financial authority or production acceptance. The current request authorises documentation refinement and Linear publication.

Use the eight-tier chain: vision → strategy → roadmap → release goal → epic → user story → acceptance criterion and technical task. Criteria and tasks are sibling children of their story. Existing native epics can span releases; retain each story's real release and primary epic. A checker-only release anchor is explicitly a proposed adapter convention, never a native reparenting or scope change.

## Refined vision and outcome contract — 11 October 2026

**VISION-IMPRANA-01:** Enable a nonprofit team to choose an appropriate intervention, use it safely, and show what changed through trustworthy impact evidence. Imprana is one product: governed impact management and practical AI/technology adoption share organisation context, current authority, evidence and learning. Buying AI, running a model or exporting a report is not the desired benefit by itself.

The primary workflow serves the Adoption Lead/Operations Lead together with the MEL/Programme team. The Executive Director decides whether the change is useful and sustainable; collectors, reviewers and stewards provide or govern evidence. Advisors, partners and funders receive only the access their current agreement permits. These are planning personas; no new permission bundle follows from a persona name.

The source problem is fragmented diagnosis, tool selection, procurement, adoption support and evidence of value. This is a requirements-derived hypothesis. No interview sample, prevalence, willingness to pay, market size or realised savings is supplied by this refinement. Alternatives include keeping the present process, a reviewed spreadsheet/checklist, deterministic templates, improving the non-AI process and assisted advisory delivery.

**Recommended first learning population:** an isolated synthetic organisation and source personas exercising one complete problem-to-follow-up journey, with a separate governed MEL/reporting walkthrough. This qualifies the connected workflow; it cannot validate demand or real-world health/beneficiary outcomes. A real pilot needs a named organisation, purpose, permitted data, operational owner, cohort and baseline/follow-up protocol before enrolment. Geography, languages, commercial terms and recruitment remain actual decisions.

| Outcome hypothesis | Measurement definition | Baseline and comparison | Proposed decision rule |
| --- | --- | --- | --- |
| Less avoidable administrative work | M-01: median active staff minutes per completed comparable task, scoped by organisation, task type and period; record exclusions and incomplete tasks separately | Paired existing/manual process and proposed workflow at matched complexity; baseline not measured | Continue only after the authorised evaluator observes a useful reduction without worse quality or control failures; set the materiality target and sample before the comparison |
| Fewer corrections/rework | M-02: returned-for-correction submissions divided by all submitted items in the same task/population/window; distinguish legitimate review refusals from avoidable rework | Preserve submitted counts, reasons and revisions; no measured rate exists | Compare the same definition and reviewer policy; never improve the rate by suppressing refusals or removing failed items |
| Usable sustained adoption | M-03: assigned participants who complete the agreed task at the agreed follow-up, divided by all eligible assigned participants; report non-response/withdrawal and support burden | Training attendance is separate; no recruited population or follow-up observation exists | Continue/change/stop based on completed work and operating effort, rather than logins or course completion alone |
| Traceable governed decisions | M-04: applicable decisions with all required current source, scope, independent approvals and immutable receipt links, divided by all applicable decisions; publish missing-link counts | Synthetic positive and revoked/hidden/stale control cases first | Any disclosure, independence bypass, incorrect official result or lost approved history stops the affected commitment regardless of aggregate rate |
| Dependable fallback and reporting | M-05: named permitted workflow completion and exact official-result/report lineage oracle under AI-off and dependency-refusal conditions; a binary per-case correctness result, not a misleading ROI ratio | Compare permitted AI-off path and refused provider/source cases; exact arithmetic remains deterministic | The core task and honest service notice must remain usable within the source contract; no success claim from screen appearance alone |

Metric calculations here are product-learning proposals, not additions to official MEL calculation rules. Targets, decision owner, window, cohort, attribution limits and funding must be recorded before a result supports an investment or release commitment. Locked before/after observations describe change; they do not establish causation.

Trust boundaries are non-negotiable: deny by default, tenant isolation, current authority at disclosure/replay/jobs, natural-person independence and immutable approved history. AI stays advisory. No approved provider, data destination or spending authority is invented; the AI-off path remains a valid product choice.
